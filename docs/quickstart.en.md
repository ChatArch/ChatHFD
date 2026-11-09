# Quickstart

Start with a small selection to check the engine, endpoint and destination before downloading complete weights. These examples use implemented commands and require no Hugging Face account or API key.

<div class="grid cards" markdown>

-   :material-package-variant: **Prepare**

    ---

    Python 3.10+, ChatHFD and aria2.

    [Install and check](#install)

-   :material-file-document-outline: **Small model example**

    ---

    Fetch only a Qwen config, not the full weights.

    [Download config](#model)

-   :material-database-outline: **Math dataset**

    ---

    Download a small public dataset repository.

    [Download dataset](#dataset)

-   :material-download-multiple: **Complete weights**

    ---

    Review files, disk and network before opting into a large selection.

    [Large-file workflow](#large)

</div>

## 1. Install and check {#install}

Use your own Python virtual environment instead of modifying system Python:

```bash
python -m pip install ChatHFD==0.1.4
chathfd --version
chathfd --tree
chathfd setup
```

When aria2c is available, `setup` prints its executable path. Otherwise it suggests an installation command. To let the tool attempt installation, run:

```bash
chathfd setup --install
```

A second confirmation is required before invoking the detected package manager. It uses apt-get, dnf or pacman on Linux, or brew when available. With no supported manager, install aria2 separately. Non-root Linux installation uses `sudo -n`; it does not wait for a password in the background. Keep passwords out of logs and chat.

## 2. Preview without transfer {#preview}

```bash
chathfd download Qwen/Qwen3.8-Flash-Next \
  --include 'config.json' \
  --dry-run
```

Output includes the repository type, requested revision, pinned commit, selected files, byte counts and destination. Dry-run does not create a download directory and does not require aria2c to be installed.

## 3. Download a model config {#model}

```bash
chathfd download Qwen/Qwen3.8-Flash-Next \
  --include 'config.json' \
  --local-dir ./models/qwen-config \
  --connections 4 \
  --jobs 5
```

The target is `./models/qwen-config/config.json`. This is configuration only, not weights; it cannot run inference by itself. Add `--revision` to request a model-page commit or another fixed version.

Rerun the same command for the same endpoint, repository, commit and file selection. Complete files are skipped; aria2 state permits continuation. If the selected set changes or a branch moves, choose a fresh directory. See [resume identity](configuration.md#resume).

## 4. Download a math dataset {#dataset}

```bash
chathfd download MathArena/arxivmath-0926 \
  --repo-type dataset \
  --dry-run

chathfd download MathArena/arxivmath-0926 \
  --repo-type dataset \
  --local-dir ./datasets/arxivmath-0926 \
  --connections 4 \
  --jobs 3
```

This fetches repository files, including the README and Parquet shard; it does not load them into a trainer. Check the [dataset card](https://huggingface.co/datasets/MathArena/arxivmath-0926) for content, license and intended use.

## 5. Complete weights and large selections {#large}

```bash
# List files and sizes only
chathfd download Qwen/Qwen3.8-Flash-Next --dry-run
```

A config-only example's transferred bytes do not represent a full model's weight size. Review disk space, bandwidth and license; narrow with patterns such as `--include '*.safetensors'` when appropriate. Actual selections above 10 GiB require an explicit `--allow-large`; this page does not automatically launch a large transfer.

## Continue

| Question | Guide |
| --- | --- |
| How do endpoint, concurrency and output settings work? | [Configuration](configuration.md) |
| What is the default for every option? | [Complete CLI Tree](cli-tree.md) |
| How can Python call the tool? | [Python API](python-api.md) |
| Why is a destination or private repository rejected? | [Troubleshooting](troubleshooting.md) |
