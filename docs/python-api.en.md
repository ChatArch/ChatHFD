# Python API

<div class="grid cards" markdown>

-   :material-code-json: **Query metadata**

    ---

    Read commit and file metadata without a destination directory.

    [Metadata example](#metadata)

-   :material-download-outline: **Preview or transfer**

    ---

    Pass all inputs explicitly and reuse the CLI's download checks.

    [Download example](#download)

-   :material-tools: **Check the engine**

    ---

    Explicitly choose read-only checks or confirmed installation.

    [Dependency example](#setup)

</div>

## Query metadata {#metadata}

```python
from chathfd.download import DEFAULT_ENDPOINT, fetch_metadata

metadata = fetch_metadata(
    endpoint=DEFAULT_ENDPOINT,
    repo_id="Qwen/Qwen3.8-Flash-Next",
    repo_type="model",
    revision="main",
)
print(metadata["sha"])
print(len(metadata.get("siblings", [])))
```

This returns the Hub JSON object; optional fields can vary. It does not perform final selection, destination-identity validation or transfer verification.

## Preview and download {#download}

```python
from pathlib import Path
import click
from chathfd.download import DEFAULT_ENDPOINT, download_repo

try:
    download_repo(
        repo_id="Qwen/Qwen3.8-Flash-Next",
        repo_type="model",
        revision="main",
        endpoint=DEFAULT_ENDPOINT,
        local_dir=Path("models/qwen-config"),
        includes=("config.json",),
        excludes=(),
        connections=4,
        jobs=5,
        dry_run=True,
        allow_large=False,
    )
except click.ClickException as exc:
    print(f"Download incomplete: {exc.format_message()}")
```

The example is a metadata-only preview. Set `dry_run=False` to write files. For a dataset, use `repo_type="dataset"` and an explicit dataset ID and new output directory. Filters are tuples of strings, not one whitespace-separated string.

| Argument | Type or requirement |
| --- | --- |
| `repo_id`, `repo_type`, `revision` | Strings; type is `model` or `dataset` |
| `endpoint` | Explicit compatible HTTPS origin; not loaded from the environment |
| `local_dir` | `Path` or `None`; explicit value is the final directory, `None` uses process/ChatEnv/cwd root + repo ID |
| `includes`, `excludes` | `tuple[str, ...]` |
| `connections`, `jobs` | Integers; Python callers should retain the CLI's 1–10 range |
| `dry_run`, `allow_large` | Booleans |
| `confirm` | Optional keyword-only callback `(file_count: int, total_bytes: int) -> bool`; `None` does not prompt, refusal aborts before any file writes |

The function returns `None` and uses Click output. Metadata/transfer failures raise `click.ClickException`; a declined callback raises `click.Abort`. Filesystem failures can raise `OSError`. `confirm` lets the caller opt into a decision after preflight; the Python API does not force interaction. It is not a silent background API or a structured file-result service.

## Directory resolution {#directory}

Directory resolution is reusable without creating directories or network calls:

```python
from chathfd.config import resolve_download_root
from chathfd.download import resolve_download_directory

print(resolve_download_root())
print(resolve_download_directory("Example/repository"))
```

`resolve_download_directory(repo_id, local_dir=None)` appends the repo ID by default; an explicit `local_dir` overrides the exact final destination. The CLI and `download_repo()` share this logic and use the same provider namespace.

## Check the engine {#setup}

```python
from chathfd.setup import setup_aria2

setup_aria2(install=False)  # Read-only; does not change system packages
```

`install=True` still confirms. Unattended callers must not assume root authorization. See the [`setup` reference](cli-tree.md#setup).
