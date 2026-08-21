# Changelog

## 2026-08-21 - 0.1.2

### Changed

- Migrated `--tree` and the new `--tree-brief` flag to ChatStyle's shared Click tree runtime with canonical root name `chathfd`.
- Kept command parameter signatures in the default tree and omitted them in the brief tree while retaining command nodes and descriptions.
- Updated runtime bounds to `chatstyle>=0.2.0,<0.3.0` and `chatenv>=0.2.10,<0.3.0`.
- Added detailed and brief tree smoke coverage to package tests and CI.

## 2026-08-12 - 0.1.1

### Added

- Added real root-only `chathfd --tree` generated from the Click command surface.
- Added CLI contract tests for `--help`, `--version`, and `--tree`.

### Changed

- Aligned documentation URLs to `https://arch.gh.wzhecnu.cn/ChatHFD/`.
- Enabled bilingual MkDocs navigation and Material icon rendering.
- Hardened Preview Docs and tag-only OIDC publish workflows.

## 2026-07-01 - 0.1.0

### Added

- Initial ChatHFD package scaffold with `chathfd` CLI.
- ChatEnv provider entry point for `chathfd` configuration discovery.
- CI and tag-driven Trusted Publisher workflow scaffold.
