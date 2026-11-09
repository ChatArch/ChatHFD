# CLI Tree and command reference

The complete tree comes from real `chathfd --tree` output, not a roadmap. Interaction flags are provided from0.1.5. Start with the brief view and then inspect each action.

## Brief command tree

```text
chathfd
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── download  # Download a public model or dataset with aria2c.
└── setup  # Check the aria2c download engine and offer installation.
```

## Complete command tree

```text
chathfd
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── download [REPO-ID] [--repo-type REPO-TYPE] [--revision REVISION] [--endpoint ENDPOINT] [--local-dir LOCAL-DIR] [--include INCLUDE] [--exclude EXCLUDE] [--connections CONNECTIONS] [--jobs JOBS] [--dry-run] [--allow-large] [--interactive]  # Download a public model or dataset with aria2c.
└── setup [--install]  # Check the aria2c download engine and offer installation.
```

## Root options

| Option | Purpose | Effects |
| --- | --- | --- |
| `--help` | Help for the current command | No download |
| `--version` | Installed package version | No download |
| `--tree` | Registered tree with parameter signatures | No download |
| `--tree-brief` | Same commands without signatures | No download |

## Download action {#download}

```text
chathfd download [REPO_ID] [OPTIONS] [-i|-I]
```

`REPO_ID` is `organization/repository`, or a supported legacy single-name Hub repository. Models and datasets share one action; preview is an option, not a subcommand. An omitted ID is prompted only on an interactive terminal; `-I` fails immediately when it is missing. The detailed tree renders Click's registered `[--interactive]` name; short `-i/-I` forms appear in command help.

| Option | Default | Meaning |
| --- | --- | --- |
| `--repo-type [model|dataset]` | `model` | Repository type |
| `--revision TEXT` | `main` | Branch, tag or commit |
| `--endpoint TEXT` | `HF_ENDPOINT` or HF-Mirror | Compatible HTTPS origin; explicit option wins |
| `--local-dir DIRECTORY` | Current-directory `models/` or `datasets/` + repo ID | Selected file output root |
| `--include TEXT` | All files | Repeatable include glob |
| `--exclude TEXT` | None | Repeatable exclude glob |
| `--connections INTEGER` | `4`, range 1–10 | Connections/splits per file |
| `--jobs INTEGER` | `5`, range 1–10 | Concurrent files |
| `--dry-run` | Off | Query and list files/sizes without creating download files |
| `--allow-large` | Off | Permit transfer of a selection over 10 GiB |
| `-i` / `--interactive` | Automatic | Force prompts for unspecified download options, then preview files and confirm before transfer |
| `-I` / `--no-interactive` | Automatic | Disable prompts; missing required values fail, complete values still download; not a dry run |
| `--help` | — | Show action help only |

Automatic prompting requires both input and output to be TTYs and `CHATARCH_AUTO_PROMPT` not set to `0/false/no/off`; `-i` fails without a TTY. Auto mode only requests a missing repository ID; `-i` also requests unspecified type, revision, endpoint, destination, filters, concurrency and preview/large-selection options, preserving explicit values. A declined confirmation creates no destination. An actual transfer writes files and `.chathfd` records and invokes aria2. See [Configuration](configuration.md) for preflight and completion conditions. Login, token forwarding, wget and native ModelScope are outside the implemented option surface.

```bash
chathfd download Qwen/Qwen3.8-Flash-Next --include config.json --dry-run
chathfd download MathArena/arxivmath-0926 --repo-type dataset --dry-run
```

## Engine preparation {#setup}

```text
chathfd setup [--install] [--help]
```

| Input | Behavior |
| --- | --- |
| No options | Check aria2c; print path when present or installation guidance otherwise |
| `--install` | If missing, show the proposed command and require confirmation before a package-manager call |
| `--help` | Show help without installation |

An existing aria2c is not reinstalled. This does not install external `hfd.sh`, launch a daemon or persist endpoint/output settings. Installation does not proceed without confirmation; manager errors fail nonzero.

## Output and exit behavior

- Successful preview or verified download exits 0 and prints selection information; completed transfer adds size-verification output.
- Invalid input, failed network/metadata or incomplete transfer fails nonzero. A start message is not a completion receipt.
- Setup can exit normally after detecting or suggesting installation. Exit 0 alone does not prove a missing engine was installed; require `aria2c ready` and the executable.
- No extra `model`, `dataset`, `login` or `mirror` subcommands exist. Legacy `hfd` flags are not current options.

[Quickstart](quickstart.md) · [Python API](python-api.md) · [Legacy comparison](troubleshooting.md)
