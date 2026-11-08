<div align="center">
    <a href="https://pypi.python.org/pypi/ChatHFD"><img src="https://img.shields.io/pypi/v/ChatHFD.svg" alt="PyPI version" /></a>
    <a href="https://github.com/ChatArch/ChatHFD/actions/workflows/ci.yml"><img src="https://github.com/ChatArch/ChatHFD/actions/workflows/ci.yml/badge.svg" alt="Tests" /></a>
</div>

<div align="center">[English](README.en.md) | [简体中文](README.md)</div>

# ChatHFD

ChatHFD is ChatArch's tool for downloading Hugging Face models and datasets. Requires Python 3.10+ and `aria2c`. Public repositories only; no CLI token handling.

## Examples

```bash
pip install ChatHFD==0.1.3
chathfd --tree
chathfd setup  # Check aria2c; if missing, show installation guidance
# To install explicitly: chathfd setup --install (requires confirmation)
# Inspect a small file in a recent open Qwen model (the full repo is ~360 GB)
chathfd download Qwen/Qwen3.8-Flash-Next --include config.json --dry-run
chathfd download Qwen/Qwen3.8-Flash-Next --include config.json --local-dir ./models/qwen-sample
# Recent math dataset (~246 KB including its single Parquet shard)
chathfd download MathArena/arxivmath-0926 --repo-type dataset --dry-run
chathfd download MathArena/arxivmath-0926 --repo-type dataset --local-dir ./datasets/arxivmath-0926
```

The default endpoint is `https://hf-mirror.com`. Override with `HF_ENDPOINT` or `--endpoint` for another Hugging Face-compatible HTTPS origin, such as `https://huggingface.co`. Repeat `--include` / `--exclude` to select repository paths, pin `--revision`, set `--jobs` (5 concurrent files by default) and `--connections` (4 connections per file by default). aria2 provides resume support. Completion checks file sizes, not cryptographic hashes. A pre-existing wrong-size file without aria2 state is rejected, not deleted.

Selections over 10 GiB require an explicit `--allow-large` after reviewing `--dry-run` and free space. Download URLs are pinned to the metadata response's commit SHA; the destination records the repository, commit, and selected file set. Rerunning the same set can resume, but a moved branch, changed selected set or unknown pre-existing files require a fresh destination. The 10 GiB gate is metadata preflight, not a hard limit on bytes sent by a server. Dry-run previews even oversized selections without creating destination files. The default destination is `./models/<org>/<repo>` or `./datasets/<org>/<repo>`.

ModelScope is a separate repository/SDK, not a drop-in replacement for `HF_ENDPOINT`. If the content is independently published there, use its CLI, e.g. `modelscope download --model Qwen/Qwen2.5-0.5B-Instruct --local_dir ./model`. Do not assume the same HF repo ID exists on ModelScope; this command does not silently fall back to it.

References: [HF-Mirror](https://hf-mirror.com/) · [ModelScope CLI](https://www.modelscope.cn/docs/sdk/cli) · [Qwen model](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) · [MathArena dataset](https://huggingface.co/datasets/MathArena/arxivmath-0926).

## Current CLI tree (`--tree`)

```text
chathfd
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── download <REPO-ID> [--repo-type REPO-TYPE] [--revision REVISION] [--endpoint ENDPOINT] [--local-dir LOCAL-DIR] [--include INCLUDE] [--exclude EXCLUDE] [--connections CONNECTIONS] [--jobs JOBS] [--dry-run] [--allow-large]  # Download a public model or dataset with aria2c.
└── setup [--install]  # Check the aria2c download engine and offer installation.
```

`--tree-brief` omits parameter signatures. See `DEVELOP.md` and `AGENTS.md` before extending the package; `src/` contains source, `tests/cli-tests/` the real CLI tests, and `docs/` long-lived documentation.
