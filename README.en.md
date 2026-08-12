<div align="center">
    <a href="https://pypi.python.org/pypi/ChatHFD">
        <img src="https://img.shields.io/pypi/v/ChatHFD.svg" alt="PyPI version" />
    </a>
    <a href="https://github.com/ChatArch/ChatHFD/actions/workflows/ci.yml">
        <img src="https://github.com/ChatArch/ChatHFD/actions/workflows/ci.yml/badge.svg" alt="Tests" />
    </a>
    <a href="https://arch.gh.wzhecnu.cn/ChatHFD/">
        <img src="https://img.shields.io/badge/docs-mkdocs-blue.svg" alt="Documentation" />
    </a>
</div>

<div align="center">

[English](README.en.md) | [简体中文](README.md)
</div>

# ChatHFD

ChatHFD is the ChatArch Hugging Face Download (HFD) tooling package entrypoint. The package currently keeps a minimal root-only CLI so the tool remains installable, discoverable, and releasable; real download orchestration commands are not exposed yet.

## Quick Start

```bash
pip install ChatHFD
chathfd --help
chathfd --version
chathfd --tree
```

## Current CLI Tree

```text
chathfd  # ChatArch Hugging Face Download tooling entrypoint
├── --help  # show command help
├── --version  # show the installed package version
└── --tree  # show this CLI tree
```

## CLI Boundary

- The current CLI only exposes root options and has no business subcommands.
- `--tree` is generated from the real Click command registration and is used to align README, docs, and tests.
- When real HFD download, mirror, cache, or verification commands are added later, update the Click registration first and then sync docs from the real `chathfd --tree` output.

## Layout

- `src/`: package source code
- `tests/code-tests/`: code tests and migrated historical tests
- `tests/cli-tests/`: real CLI tests, doc-first
- `tests/mock-cli-tests/`: mock/fake CLI tests, doc-first
- `docs/`: long-lived project docs built by MkDocs

## Development Notes

See `DEVELOP.md` and `AGENTS.md` before expanding the scaffold.
