# Interface Tree

## From command to files

```text
chathfd.cli                         # CLI inputs and dispatch
├── main                            # --help / --version / --tree / --tree-brief
├── download REPO_ID
│   └── chathfd.download.download_repo(...)
│       ├── fetch_metadata(...)     # Hub model/dataset metadata
│       ├── selection, path and identity checks
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
| `download_repo` | repository, endpoint, directory, filters, concurrency and switches | `None`; console output | Writes files and runs aria2 unless dry-run |
| `setup_aria2` | `install: bool` | `None`; check/install messages | No installation by default; explicit mode still confirms |
| `ChathfdConfig` | ChatEnv provider registration | Schema | Its API key is not downloader authentication |

These are importable functions, not HTTP/MCP services or a persistent task queue. `download_repo()` reports failures through exceptions such as `click.ClickException`, not a structured result object.

## Ownership

- ChatStyle owns real CLI trees and confirmation interaction.
- ChatEnv provides the existing schema registration, not Hugging Face login here.
- ChatHFD selects files, pins commits, validates destinations and builds aria2 input.
- aria2 transfers bytes with splits and resume; successful process exit does not replace final size checks.

[Python examples](python-api.md) · [All CLI options](cli-tree.md)
