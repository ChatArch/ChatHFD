# Troubleshooting and legacy interfaces

Choose the next action from the failure, rather than deleting evidence, adding tokens or blindly retrying.

| Symptom | Meaning | Next action |
| --- | --- | --- |
| Missing `aria2c` | Transfer engine unavailable | Run `chathfd setup`; use `setup --install` explicitly if needed |
| Installer fails or no manager | Manager, permission or host prerequisite missing | Install interactively as advised; no passwords in argv |
| Metadata HTTP/network failure | Endpoint, repository or network unavailable | Check repo card, type and existing network route; choose `--endpoint` explicitly |
| No matching files | Filters selected nothing | Check repository-relative paths and quote globs |
| Above 10 GiB | Large file selection | Preview first; use `--allow-large` only after resource review |
| Destination belongs to another selection | Endpoint/repo/type/commit/file set changed | Choose a new directory; do not remove the receipt to fake resume |
| Existing files without a receipt | Provenance is unknown | Preserve files and choose a fresh destination |
| Wrong size without `.aria2` | Existing file cannot safely resume | Deliberately move it aside and use a new directory |
| Interrupted transfer | aria2 has not completed | Rerun the same pinned commit and selection |
| Gated/private repository rejected | Authentication unsupported | Use official tooling and its authorization flow; no keys in this command |

## Migrating from old HFD

This is a comparison, not a claim that old aliases or flags still exist.

| Old input | Current input | Difference |
| --- | --- | --- |
| `hfd REPO_ID` | `chathfd download REPO_ID` | Separate root and action |
| `-d` / `--dataset` | `--repo-type dataset` | No current `-d` alias |
| `-x 4` | `--connections 4` | Per-file connections; `--jobs` controls concurrent files |
| `--tool wget` | No equivalent backend | aria2 only |
| `--hf_username` / `--hf_token` | No equivalent options | Public repositories only |
| Host-specific shared default | Explicit `--local-dir` | No shared-mount or global-cache management |
| Fetching external hfd.sh | No external hfd.sh needed | Package Python code coordinates aria2 |

Old aliases, backend paths and logs may contain host-specific configuration. Do not copy them into public docs or fill legacy examples with real tokens. Define a new backend/authentication contract before adding it; changing an endpoint does not implement a separate platform.

[All options](cli-tree.md) · [Resume identity](configuration.md#resume) · [Capability boundary](capability-map.md)
