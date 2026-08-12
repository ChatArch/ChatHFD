# CLI Tree

`ChatHFD` is currently a root-only CLI. This page must stay synchronized from the real `chathfd --tree` output and must not invent future commands.

```text
chathfd  # ChatArch Hugging Face Download tooling entrypoint
├── --help  # show command help
├── --version  # show the installed package version
└── --tree  # show this CLI tree
```

## Current Status

| Entry | Status | Notes |
| --- | --- | --- |
| `chathfd --help` | Implemented | Shows root command help. |
| `chathfd --version` | Implemented | Shows the installed package version. |
| `chathfd --tree` | Implemented | Shows the current real CLI tree. |
| HFD download subcommands | Not implemented | Add them only after real download orchestration exists. |

## Update Rule

When real commands are added, update the Click registration and tests first, then run `chathfd --tree` to refresh README and this page.
