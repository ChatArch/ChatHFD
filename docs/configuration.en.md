# Configuration

<div class="grid cards" markdown>

-   :material-web: **Endpoint**

    ---

    Use one Hugging Face-compatible HTTPS origin per invocation.

    [Endpoint precedence](#endpoint)

-   :material-folder-outline: **Output and resume**

    ---

    A destination belongs to one repository, commit and file selection.

    [Destination identity](#resume)

-   :material-speedometer: **Selection and concurrency**

    ---

    Control connections per file separately from concurrent files.

    [Transfer settings](#selection)

</div>

## Endpoint precedence {#endpoint}

| Source | Priority | Example |
| --- | --- | --- |
| CLI `--endpoint` | Highest | `--endpoint https://huggingface.co` |
| Process `HF_ENDPOINT` | Next | `HF_ENDPOINT=https://hf-mirror.com` |
| Built-in default | Last | `https://hf-mirror.com` |

```bash
HF_ENDPOINT=https://hf-mirror.com chathfd download Qwen/Qwen3.8-Flash-Next --include config.json --dry-run
chathfd download Qwen/Qwen3.8-Flash-Next --endpoint https://huggingface.co --include config.json --dry-run
```

The endpoint must be an HTTPS origin without userinfo, path, query or fragment. The CLI does not persist settings, automatically retry another mirror or silently fall back. Python `download_repo()` takes an explicit `endpoint`; it does not load `HF_ENDPOINT` for you.

ModelScope is not an interchangeable `HF_ENDPOINT`. It has separate repository IDs, availability and an SDK; ChatHFD has no ModelScope backend. Legacy token flags do not add authentication to the current downloader.

## File selection and concurrency {#selection}

```bash
chathfd download Qwen/Qwen3.8-Flash-Next \
  --include 'config.json' --include 'generation_config.json' \
  --exclude 'README*' --connections 4 --jobs 5 --dry-run
```

- Repeat `--include` for an OR across patterns; without it all files are selected.
- Repeated `--exclude` patterns remove matching repository-relative paths; exclusion wins.
- Quote globs to prevent local shell expansion.
- `--connections` controls per-file connections/splits (default 4); `--jobs` concurrent files (default 5). Both CLI ranges are 1–10; their product is not a promise of actual active connections.
- `--revision` accepts a branch, tag or commit. Resolve URLs use the commit returned by metadata, even when the request names `main`.

## Output and resume identity {#resume}

Without `--local-dir`, models use `./models/<org>/<repo>` and datasets `./datasets/<org>/<repo>`, relative to the invocation directory. This is not the standard Hugging Face cache layout and does not infer another machine's shared-storage paths.

```text
<destination>/
├── <selected repository files>
└── .chathfd/
    ├── selection.json    # endpoint/repo/type/commit/names and sizes
    └── urls.txt          # aria2 input list
```

A repeat invocation must match endpoint, repository, type, commit and selected file set. Partial transfers require aria2 `.aria2` state; complete same-size files are skipped. Use a fresh directory when changing file sets, endpoint or commit. Unknown existing files, symlinks, path escapes, internal-name collisions and wrong-size files without resume state are rejected, not silently deleted or overwritten.

Dry-run checks metadata, selection and paths only. It creates no receipt and does not perform every destination-identity check required for an actual transfer; a successful preview does not guarantee a pre-existing destination can be reused.

## Large selections and verification {#limits}

| Behavior | Contract |
| --- | --- |
| Selection above 10 GiB | Preview succeeds; transfer requires `--allow-large` |
| Hard network-byte quota | None; sizes come from server metadata |
| Completion | Files exist with expected size and no remaining aria2 state |
| Cryptographic hashes or inference | Not verified |
| Downloader configuration | Default aria2 config and netrc are disabled to avoid implicit credentials |

Continue with [all options](cli-tree.md#download) and [Troubleshooting](troubleshooting.md).
