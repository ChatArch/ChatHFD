"""Carry the published dev preview into a freshly built production site."""
from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import subprocess


def preserve_preview(site_dir: Path, ref: str = "origin/gh-pages") -> int:
    """Copy only regular dev/ files and versions.json; never stale production."""
    result = subprocess.run(["git", "ls-tree", "-r", "-z", ref], check=True, capture_output=True)
    root = site_dir.resolve()
    copied = 0
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, _object = metadata.decode("ascii").split()
        name = raw_path.decode("utf-8")
        if not (name.startswith("dev/") or name == "versions.json"):
            continue
        path = PurePosixPath(name)
        if mode not in ("100644", "100755") or kind != "blob":
            raise ValueError("Preview contains a non-regular file")
        if path.is_absolute() or any(part in ("", ".", "..") for part in name.split("/")):
            raise ValueError("Unsafe preview path")
        target = root.joinpath(*path.parts)
        ancestor = root
        for part in path.parts:
            ancestor = ancestor / part
            if ancestor.is_symlink():
                raise ValueError("Preview destination contains a symlink")
        if not target.resolve().is_relative_to(root):
            raise ValueError("Preview escapes publication root")
        payload = subprocess.run(["git", "show", f"{ref}:{name}"], check=True, capture_output=True).stdout
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        copied += 1
    return copied


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, default=Path("site"))
    args = parser.parse_args()
    print(f"Preserved {preserve_preview(args.site_dir)} preview files")
