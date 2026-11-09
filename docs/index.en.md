# ChatHFD: model and dataset downloads

Download public Hugging Face repositories with one command. HF-Mirror is the default endpoint; aria2 provides split and multi-file concurrency. Preview the selected files and size before transferring them.

<div class="grid cards" markdown>

-   :material-rocket-launch-outline: **Start here**

    ---

    Install the package, check aria2, and download a model config and a small math dataset.

    [Open Quickstart](quickstart.md)

-   :material-file-tree-outline: **Find a command**

    ---

    Real CLI trees, every option, defaults, exit behavior and installation confirmation.

    [Open CLI Tree](cli-tree.md)

-   :material-tune-variant: **Choose endpoint and output**

    ---

    Endpoint precedence, file filters, concurrency, pinned revisions and resume identity.

    [Read Configuration](configuration.md)

-   :material-language-python: **Call from Python**

    ---

    Reuse metadata and download functions with their exact arguments, output and errors.

    [View Python API](python-api.md)

-   :material-vector-link: **Understand the boundary**

    ---

    Public versus authenticated repositories, compatible mirrors and the separate ModelScope platform.

    [View Capability Map](capability-map.md)

-   :material-lifebuoy: **Resolve a failure**

    ---

    Missing dependencies, destination conflicts, network errors and legacy HFD flags.

    [Open Troubleshooting](troubleshooting.md)

</div>

## Choose by task

| Task | Starting point | File effects |
| --- | --- | --- |
| Inspect repository files and size | [`download --dry-run`](quickstart.md#preview) | No download files created |
| Download model config or weights | [Model example](quickstart.md#model) | Writes selected files |
| Download a math dataset | [Dataset example](quickstart.md#dataset) | Writes repository files |
| Check or install aria2 | [`setup`](cli-tree.md#setup) | Read-only unless installation is confirmed |
| Understand a rejected directory | [Output and resume](configuration.md#resume) | Existing files are not deleted |
| Map commands to implementation | [Interface Tree](interface-tree.md) | Reference only |

## Minimal working path

```bash
pip install ChatHFD==0.1.6
chathfd setup
chathfd download Qwen/Qwen3.8-Flash-Next --include config.json --dry-run
```

This only queries metadata for a config file, not model weights. Continue with [Quickstart](quickstart.md).

!!! note "Current boundary"
    Public repositories only; no account token input or forwarding. Completion checks file sizes, not upstream cryptographic hashes. The 10 GiB gate is metadata preflight on the file selection, not a hard network-byte quota.
