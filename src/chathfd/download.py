"""Bounded, resumable public Hub downloads through aria2c."""

from __future__ import annotations

import fnmatch
import json
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import urlopen

import click

DEFAULT_ENDPOINT = "https://hf-mirror.com"
DEFAULT_MAX_BYTES = 10 * 1024**3
_ID_PART = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_REV_PART = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _parts(value: str, pattern: re.Pattern[str], label: str) -> list[str]:
    parts = value.split("/")
    if not all(part not in (".", "..") and pattern.fullmatch(part) for part in parts):
        raise click.ClickException(f"Invalid {label}: {value!r}")
    return parts


def _endpoint(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ("", "/"):
        raise click.ClickException("Endpoint must be an HTTPS origin without credentials, path or query")
    return value.rstrip("/")


def fetch_metadata(endpoint: str, repo_id: str, repo_type: str, revision: str) -> dict:
    prefix = "models" if repo_type == "model" else "datasets"
    segments = ["api", prefix, *_parts(repo_id, _ID_PART, "repository ID")]
    if revision != "main":
        segments += ["revision", *_parts(revision, _REV_PART, "revision")]
    url = endpoint + "/" + "/".join(quote(part, safe="") for part in segments) + "?blobs=true"
    try:
        with urlopen(url, timeout=30) as response:
            payload = response.read(4 * 1024 * 1024 + 1)
    except (HTTPError, URLError, TimeoutError) as exc:
        # Do not include the exception's URL or headers in output.
        raise click.ClickException(f"Failed to fetch {repo_type} metadata from {endpoint}: {type(exc).__name__}") from exc
    if len(payload) > 4 * 1024 * 1024:
        raise click.ClickException("Repository metadata exceeds 4 MiB; refusing incomplete preflight")
    try:
        data = json.loads(payload)
    except (ValueError, UnicodeDecodeError) as exc:
        raise click.ClickException("Invalid repository metadata response") from exc
    if not isinstance(data, dict):
        raise click.ClickException("Unexpected repository metadata response")
    return data


def _selected_files(metadata: dict, includes: tuple[str, ...], excludes: tuple[str, ...]) -> list[tuple[str, int]]:
    if metadata.get("gated") or metadata.get("private"):
        raise click.ClickException("Gated/private repositories are not supported; no token is forwarded")
    siblings = metadata.get("siblings")
    if not isinstance(siblings, list):
        raise click.ClickException("Repository metadata has no file list")
    files = []
    for entry in siblings:
        name = entry.get("rfilename") if isinstance(entry, dict) else None
        if not isinstance(name, str):
            raise click.ClickException("Repository metadata contains an invalid filename")
        path = PurePosixPath(name)
        if path.is_absolute() or "\\" in name or any(ord(char) < 32 or ord(char) == 127 for char in name) or any(part in ("", ".", "..") for part in name.split("/")):
            raise click.ClickException(f"Unsafe repository path: {name!r}")
        if includes and not any(fnmatch.fnmatchcase(name, p) for p in includes):
            continue
        if any(fnmatch.fnmatchcase(name, p) for p in excludes):
            continue
        if path.parts[0] == ".chathfd":
            raise click.ClickException("Repository file conflicts with the reserved .chathfd directory")
        size = entry.get("size")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise click.ClickException(f"Missing file size for {name!r}; cannot preflight")
        files.append((name, size))
    if not files:
        raise click.ClickException("No files match the include/exclude filters")
    names = {name for name, _ in files}
    for name in names:
        if name + ".aria2" in names or any(str(parent) in names for parent in PurePosixPath(name).parents if str(parent) != "."):
            raise click.ClickException(f"Repository file paths conflict with each other: {name!r}")
    return files


def _check_paths(root: Path, files: list[tuple[str, int]]) -> None:
    base = root.resolve()
    if any(ord(char) < 32 or ord(char) == 127 for char in str(base)):
        raise click.ClickException("Destination contains control characters unsafe for aria2c")
    for name, size in files:
        ancestor = root
        for part in name.split("/"):
            ancestor = ancestor / part
            if ancestor.is_symlink():
                raise click.ClickException(f"Destination contains a symlink: {name!r}")
        target = root.joinpath(*name.split("/"))
        if Path(str(target) + ".aria2").is_symlink():
            raise click.ClickException(f"Destination contains a symlinked aria2 state file: {name!r}")
        if not target.resolve().is_relative_to(base):
            raise click.ClickException(f"File path escapes destination: {name!r}")
        if target.exists() and target.is_file() and target.stat().st_size != size and not Path(str(target) + ".aria2").exists():
            raise click.ClickException(f"Existing file has wrong size: {name!r}; move it aside before retrying")
        if target.exists() and not target.is_file():
            raise click.ClickException(f"Destination is not a regular file: {name!r}")
    control = root / ".chathfd"
    if not control.resolve().is_relative_to(base) or control.is_symlink() or (control / "urls.txt").is_symlink() or (control / "selection.json").is_symlink():
        raise click.ClickException("Unsafe downloader control path")


def _check_selection(root: Path, files: list[tuple[str, int]], identity: dict) -> None:
    control = root / ".chathfd"
    receipt = control / "selection.json"
    if receipt.is_file():
        try:
            previous = json.loads(receipt.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            raise click.ClickException("Unreadable download selection; choose a fresh destination") from exc
        if previous != identity:
            raise click.ClickException("Destination belongs to another repository, endpoint, commit or file selection; choose a fresh destination")
    elif control.exists() or any(
        target.exists() or Path(str(target) + ".aria2").exists()
        for name, _ in files
        for target in (root.joinpath(*name.split("/")),)
    ):
        raise click.ClickException("Existing files have no matching download selection; choose a fresh destination")


def resolve_download_directory(repo_id: str, local_dir: Path | None = None) -> Path:
    """Return the exact explicit directory or configured-root/repository path."""
    from chathfd.config import resolve_download_root, _directory_path

    parts = _parts(repo_id, _ID_PART, "repository ID")
    if local_dir is not None:
        return _directory_path(local_dir, "--local-dir")
    base = resolve_download_root()
    destination = _directory_path(base.joinpath(*parts), "Download directory")
    if not destination.is_relative_to(base):
        raise click.ClickException("Repository destination escapes the configured download root")
    return destination


def download_repo(
    repo_id: str, repo_type: str, revision: str, endpoint: str, local_dir: Path | None,
    includes: tuple[str, ...], excludes: tuple[str, ...], connections: int, jobs: int,
    dry_run: bool, allow_large: bool, *, confirm: Callable[[int, int], bool] | None = None,
) -> None:
    repo_parts = _parts(repo_id, _ID_PART, "repository ID")
    _parts(revision, _REV_PART, "revision")
    endpoint = _endpoint(endpoint)
    root = resolve_download_directory(repo_id, local_dir)
    metadata = fetch_metadata(endpoint, repo_id, repo_type, revision)
    files = _selected_files(metadata, includes, excludes)
    commit = metadata.get("sha")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise click.ClickException("Repository metadata has no valid commit SHA; refusing unpinned download")
    _check_paths(root, files)
    total = sum(size for _, size in files)
    click.echo(f"{repo_type} {repo_id}@{revision} ({commit}): {len(files)} files, {total} bytes -> {root} (endpoint {endpoint})")
    for name, size in files:
        click.echo(f"  {name}: {size} bytes")
    if dry_run:
        if total > DEFAULT_MAX_BYTES and not allow_large:
            click.echo("Selection exceeds 10 GiB; a real download requires --allow-large or narrower --include")
        click.echo("Dry run: no files downloaded")
        return
    if total > DEFAULT_MAX_BYTES and not allow_large:
        raise click.ClickException("Selected files exceed 10 GiB; narrow --include or pass --allow-large explicitly")
    identity = {
        "version": 1, "endpoint": endpoint, "repo_id": repo_id,
        "repo_type": repo_type, "commit": commit,
        "files": sorted([name, size] for name, size in files),
    }
    _check_selection(root, files, identity)
    if confirm is not None and not confirm(len(files), total):
        raise click.Abort()
    if not shutil.which("aria2c"):
        raise click.ClickException("aria2c is required; run chathfd setup for instructions or chathfd setup --install")
    control = root / ".chathfd"
    control.mkdir(parents=True, exist_ok=True)
    (control / "selection.json").write_text(json.dumps(identity, sort_keys=True) + "\n", encoding="utf-8")
    urls = control / "urls.txt"
    prefix = ["datasets"] if repo_type == "dataset" else []
    url_prefix = endpoint + "/" + "/".join(quote(part, safe="") for part in [*prefix, *repo_parts, "resolve", commit])
    pending = []
    for name, size in files:
        target = root.joinpath(*name.split("/"))
        if target.is_file() and target.stat().st_size == size and not Path(str(target) + ".aria2").exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        url = url_prefix + "/" + "/".join(quote(part, safe="") for part in name.split("/"))
        pending.extend([url, f" dir={target.parent.resolve()}", f" out={target.name}"])
    urls.write_text("\n".join(pending) + ("\n" if pending else ""), encoding="utf-8")
    if pending:
        command = [
            "aria2c", "--no-conf=true", "--no-netrc=true", f"--input-file={urls}",
            "--continue=true", "--auto-file-renaming=false",
            f"--max-connection-per-server={connections}", f"--split={connections}",
            f"--max-concurrent-downloads={jobs}", "--file-allocation=none",
        ]
        try:
            subprocess.run(command, check=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            raise click.ClickException(f"aria2c failed ({type(exc).__name__}); re-run to resume") from exc
    for name, size in files:
        target = root.joinpath(*name.split("/"))
        if not target.is_file() or target.stat().st_size != size or Path(str(target) + ".aria2").exists():
            raise click.ClickException(f"Download incomplete or size mismatch: {name!r}")
    click.echo(f"Verified {len(files)} files by size (not cryptographic hashes)")
