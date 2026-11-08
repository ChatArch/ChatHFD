# CLI Tree

This page mirrors the real `chathfd --tree` output. ChatStyle fixes the public root name to `chathfd`; `--tree-brief` only omits command parameter signatures.

```text
chathfd
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── download <REPO-ID> [--repo-type REPO-TYPE] [--revision REVISION] [--endpoint ENDPOINT] [--local-dir LOCAL-DIR] [--include INCLUDE] [--exclude EXCLUDE] [--connections CONNECTIONS] [--jobs JOBS] [--dry-run] [--allow-large]  # Download a public model or dataset with aria2c.
└── setup [--install]  # Check the aria2c download engine and offer installation.
```

The command line in `chathfd --tree-brief` is:

```text
├── download  # Download a public model or dataset with aria2c.
└── setup  # Check the aria2c download engine and offer installation.
```

## Download boundary

`setup` checks for `aria2c` and suggests a package-manager command if missing; `setup --install` requires explicit confirmation before attempting installation. `download` supports public Hugging Face models and datasets (`--repo-type dataset`). The default endpoint is `https://hf-mirror.com`; `HF_ENDPOINT` or `--endpoint` overrides it. Select files with `--include` / `--exclude`, preview with `--dry-run`, and opt in to selections over 10 GiB with `--allow-large`. `--jobs` controls concurrent files and `--connections` connections per file. Verification is by size only; gated/private tokens are not supported. See the [repository README](https://github.com/ChatArch/ChatHFD/blob/main/README.en.md#examples) for examples and the ModelScope distinction.

When updating the CLI, change Click registration and tests first, then rerun `chathfd --tree` and `chathfd --tree-brief` to refresh this page and the README.
