# Changelog

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
