# CLI Tree

`ChatHFD` is currently a root-only CLI. This page must stay synchronized from the real `chathfd --tree` output and must not invent future commands. ChatStyle's shared Click tree runtime fixes the public root name as `chathfd`.

```text
chathfd
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
└── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
```

`--tree` keeps command parameter signatures by default; `--tree-brief` removes signatures while retaining command nodes and descriptions. With no parameterized subcommands yet, both modes show the same root-only nodes.

## Current Status

| Entry | Status | Notes |
| --- | --- | --- |
| `chathfd --help` | Implemented | Shows root command help. |
| `chathfd --version` | Implemented | Shows the installed package version. |
| `chathfd --tree` | Implemented | Shows the current real CLI tree with command parameter signatures. |
| `chathfd --tree-brief` | Implemented | Shows the current real CLI tree without command parameter signatures. |
| HFD download subcommands | Not implemented | Add them only after real download orchestration exists. |

## Update Rule

When real commands are added, update the Click registration and tests first, then run `chathfd --tree` and `chathfd --tree-brief` to refresh README and this page.
