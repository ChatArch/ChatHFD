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
chathfd --tree-brief
```

## Current CLI Tree (`--tree`)

```text
chathfd
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
└── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
```

## CLI Boundary

- The current CLI only exposes root options and has no business subcommands.
- `--tree` and `--tree-brief` are generated from the real registration by ChatStyle's shared Click tree runtime, with `chathfd` fixed as the public root name.
- `--tree` keeps command parameter signatures by default; `--tree-brief` removes signatures while retaining command nodes and descriptions. With no parameterized subcommands yet, both modes show the same root-only nodes.
- When real HFD download, mirror, cache, or verification commands are added later, update the Click registration first and then sync docs from both real tree modes.

## Layout

- `src/`: package source code
- `tests/code-tests/`: code tests and migrated historical tests
- `tests/cli-tests/`: real CLI tests, doc-first
- `tests/mock-cli-tests/`: mock/fake CLI tests, doc-first
- `docs/`: long-lived project docs built by MkDocs

## Development Notes

See `DEVELOP.md` and `AGENTS.md` before expanding the scaffold.
