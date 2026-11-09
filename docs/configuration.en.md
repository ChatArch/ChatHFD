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

## ChatEnv download root {#download-root}

From0.1.6, non-sensitive `CHATHFD_DOWNLOAD_ROOT` defaults to `.` and is resolved against the invocation directory on every call. Models and datasets use `<root>/<organization>/<repository>`, without an extra models/datasets layer. Relative paths and `~` work; another machine's mount layout is never inferred.

| Source | Priority | Meaning |
| --- | --- | --- |
| `--local-dir` / Python `local_dir` | Highest | Exact final directory, no repo suffix; bypasses invalid lower-priority configuration |
| Process `CHATHFD_DOWNLOAD_ROOT` | Next | Root plus repo ID; an empty string explicitly selects cwd |
| Same key in active ChatEnv profile | Next | Same root rule |
| Default `.` | Last | `<cwd>/<organization>/<repository>`, not the install location |

Use ChatEnv in the same Python environment as ChatHFD so its provider is discoverable:

```bash
chatenv set CHATHFD_DOWNLOAD_ROOT=/data/hub -I
chatenv list -t chathfd
chatenv test -t chathfd -I
CHATHFD_DOWNLOAD_ROOT=./cache chathfd download Qwen/Qwen3.8-Flash-Next --include config.json --dry-run -I
```

This reuses the `chathfd` provider and `Chathfd` storage namespace. Downloads only read configuration; they never save a variable automatically. The provider test validates the effective root without network calls or creating directories. `-i` displays the effective final destination as the path default. For shared storage, use a directory accessible on the current host, not an NFS `server:/export` specification; the tool never remounts or guesses. Use the appropriate active profile, process root or exact directory when models/datasets need separate roots.

Version0.1.5 and earlier used `./models/<repo_id>` and `./datasets/<repo_id>`. Existing files are not migrated; explicit `--local-dir` semantics stay unchanged. Legacy scaffold `CHATHFD_API_KEY` is not downloader authentication and need not be filled.

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

Without `--local-dir`, the precedence above produces `<download-root>/<repo_id>`. The selected root itself may be a directory alias, but repository components cannot resolve outside it; an explicit final directory remains an intentional override. This is not the standard Hugging Face cache layout and does not infer another machine's shared paths.

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
