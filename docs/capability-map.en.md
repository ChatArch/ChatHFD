# Capability Map

<div class="grid cards" markdown>

-   :material-download-outline: **Repository files**

    ---

    Public models and datasets, selection, revision and output.

    [Run examples](quickstart.md)

-   :material-shield-check-outline: **Preflight and resume**

    ---

    Explicit selection, commit pinning and destination identity; size-based completion checks.

    [Read constraints](configuration.md#resume)

-   :material-code-braces: **Reusable interfaces**

    ---

    CLI adapters call importable Python functions; aria2 transfers files.

    [Interface mapping](interface-tree.md)

</div>

## Implemented

| Capability | Interface | Boundary |
| --- | --- | --- |
| Models and datasets | `download`, `--repo-type` | Public repository files, not training or inference |
| Compatible mirrors | `--endpoint`, `HF_ENDPOINT` | HF-Mirror by default; no cross-platform fallback |
| Download root | `CHATHFD_DOWNLOAD_ROOT`, ChatEnv, `--local-dir` | Cwd default + repo ID; explicit local-dir is final; no automatic shared-path configuration |
| Concurrency and resume | `--connections`, `--jobs` | Local aria2 and matching destination identity |
| Selection and size preview | `--include`, `--exclude`, `--dry-run` | Metadata preflight, not a hard byte quota |
| Engine preparation | `setup [--install]` | Explicit, confirmed system package installation |
| Python calls | `download_repo`, `fetch_metadata`, `setup_aria2` | Still use Click output/errors; see API reference |

## Outside the current boundary

- Login, token management or forwarding for private/gated Hub repositories.
- Native ModelScope downloads, wget backend or automatic replacement of old `hfd` aliases.
- Standard Hugging Face cache migration or automatic legacy adoption, remote mounts, job queues or background daemons.
- Upstream cryptographic verification, inference validation or dataset training pipelines.

A successful config or README download is not a completed weight download. [Quickstart](quickstart.md#model) distinguishes small examples from full repositories.
