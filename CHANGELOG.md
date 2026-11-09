# Changelog

## 2026-11-09 - 0.1.6

- Add non-sensitive ChatEnv `CHATHFD_DOWNLOAD_ROOT`, using process env before the existing active provider profile and invocation cwd fallback. Real configuration remains manual.
- Change the implicit layout from models/datasets + repo ID to `<root>/<repo_id>`; default root is cwd. Explicit `--local-dir` stays an exact final directory and overrides invalid lower-priority roots.
- Share importable directory resolution across CLI/Python, validate before metadata, show the effective interactive default, and reject implicit repository symlink escapes/control characters.
- Replace the schema-only provider test with read-only effective-root validation. Update bilingual configuration/CLI/API guidance and isolated profile/precedence/safety tests; do not manage mounts or adopt unknown legacy files.

## 2026-11-09 - 0.1.5

- Added optional ChatStyle `-i/-I` input handling for downloads. A missing repository ID prompts only on a usable TTY, while `-I` fails fast without changing normal transfer semantics.
- Forced interaction can fill unspecified options. Metadata selection is shown before the user confirms transfer; refusal leaves the destination untouched. `--dry-run` remains the only preview-only flag.
- Reuse ChatStyle0.2.1 `CommandField.param_type` for choice, directory and concurrency validation instead of package-local numeric converters.

## 2026-11-09 - 0.1.4

### 文档

- 补齐中英文多栏导航首页、快速开始、完整 CLI 参数参考、配置与续传、能力地图、接口树、Python 示例和故障排查。
- 增加文档与真实 CLI/API 的一致性测试，明确模型配置小样例、公开仓库及验证边界。
- 文档预览与正式部署共享发布锁，正式部署保留已有 dev 预览；预览语言入口保持在预览路径内。

下载命令行为保持不变。

## 2026-11-08 - 0.1.3

### Added

- Added `chathfd download` for public Hugging Face models and datasets with HF-Mirror default, selection preflight, aria2 concurrency/resume, dry-run, and an explicit 10 GiB size gate.
- Added `chathfd setup` to detect aria2c, suggest installation commands, and offer a confirmed `--install` path.

### Changed

- Updated both CLI tree modes, bilingual docs and tests to reflect the real command surface. ModelScope is documented as a separate repository rather than an interchangeable mirror.

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
