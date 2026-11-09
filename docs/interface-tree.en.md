# Interface Tree

## From command to files

```text
chathfd.cli                         # CLI inputs and dispatch
├── main                            # --help / --version / --tree / --tree-brief
├── download [REPO_ID] [-i|-I]      # ChatStyle input resolution; manual confirmation
│   └── chathfd.download.download_repo(...)
│       ├── resolve_download_directory(...) # final path; shared ChatEnv-root logic
│       ├── fetch_metadata(...)     # Hub model/dataset metadata
│       ├── selection, path and identity checks
│       ├── optional confirm callback  # after preflight, before writes
│       ├── .chathfd/selection.json + urls.txt
│       └── aria2c                  # concurrency, splits and resume
└── setup [--install]
    └── chathfd.setup.setup_aria2(...)
        ├── shutil.which           # aria2c and package-manager detection
        └── package manager        # explicit installation and confirmation only
```

## Call contracts

| API | Input | Output | Effects |
| --- | --- | --- | --- |
| `fetch_metadata` | endpoint, repo_id, repo_type, revision | Metadata `dict` | HTTP GET; no download files |
| `resolve_download_root` | Process env, active ChatEnv profile or `.` | Effective root `Path` | Read-only; no directory creation or network |
| `resolve_download_directory` | repo_id and optional final local_dir | Final directory `Path` | Shared read-only validation for CLI/Python |
| `download_repo` | repository, endpoint, directory, filters, concurrency, switches and optional `confirm` callback | `None`; console output | Writes files and runs aria2 unless dry-run or confirmation declined |
| `setup_aria2` | `install: bool` | `None`; check/install messages | No installation by default; explicit mode still confirms |
| `ChathfdConfig` | ChatEnv download-root field | Schema and read-only path validation hook | No target-directory writes; legacy API key is not authentication |

These are importable functions, not HTTP/MCP services or a persistent task queue. `download_repo()` reports failures through exceptions such as `click.ClickException`, not a structured result object.

## Ownership

- ChatStyle owns real CLI trees and reusable opt-in input/confirmation behavior.
- ChatEnv stores the active-profile download root; downloads only read it. It is not Hugging Face login.
- ChatHFD selects files, pins commits, validates destinations and builds aria2 input.
- aria2 transfers bytes with splits and resume; successful process exit does not replace final size checks.

[Python examples](python-api.md) · [All CLI options](cli-tree.md)
