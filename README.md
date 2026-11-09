<div align="center">
    <a href="https://pypi.python.org/pypi/ChatHFD"><img src="https://img.shields.io/pypi/v/ChatHFD.svg" alt="PyPI version" /></a>
    <a href="https://github.com/ChatArch/ChatHFD/actions/workflows/ci.yml"><img src="https://github.com/ChatArch/ChatHFD/actions/workflows/ci.yml/badge.svg" alt="Tests" /></a>
</div>

<div align="center">[英文版](README.en.md) | [简体中文](README.md)</div>

# ChatHFD

ChatHFD 是 ChatArch 的 Hugging Face 模型与数据集下载工具。要求 Python 3.10+ 和 `aria2c`；只支持公开仓库，不在命令行传递 Token。

从0.1.5起，`download`按需接入ChatStyle共享输入解析与类型校验，支持`-i/-I`；`-I`禁止提问但不是dry-run。

## 文档导航

| 你要做什么 | 文档入口 |
| --- | --- |
| 第一次安装与下载 | [快速开始](https://arch.gh.wzhecnu.cn/ChatHFD/quickstart/) |
| 查看全部命令、参数与默认值 | [完整 CLI 树](https://arch.gh.wzhecnu.cn/ChatHFD/cli-tree/) |
| 配置镜像、目录和续传 | [下载配置](https://arch.gh.wzhecnu.cn/ChatHFD/configuration/) |
| 从 Python 调用 | [Python 接口](https://arch.gh.wzhecnu.cn/ChatHFD/python-api/)与[接口树](https://arch.gh.wzhecnu.cn/ChatHFD/interface-tree/) |
| 查看当前支持范围 | [能力地图](https://arch.gh.wzhecnu.cn/ChatHFD/capability-map/) |
| 解决失败或对照旧参数 | [故障排查](https://arch.gh.wzhecnu.cn/ChatHFD/troubleshooting/) |

## 下载示例

```bash
pip install ChatHFD==0.1.6
chathfd --tree
chathfd setup  # 检查 aria2c；未安装时提示命令
# 如确需安装：chathfd setup --install（还需确认）
# 先预检 Qwen 模型中的小文件，不直接全量下载权重
chathfd download Qwen/Qwen3.8-Flash-Next --include config.json --dry-run
chathfd download Qwen/Qwen3.8-Flash-Next --include config.json --local-dir ./models/qwen-sample
# 数学数据集：约 246 KB，包含 README、元数据和一个 Parquet 分片
chathfd download MathArena/arxivmath-0926 --repo-type dataset --dry-run
chathfd download MathArena/arxivmath-0926 --repo-type dataset --local-dir ./datasets/arxivmath-0926
```

默认端点为 `https://hf-mirror.com`；`HF_ENDPOINT` 环境变量或 `--endpoint` 可覆盖为其它 Hugging Face 兼容 HTTPS 端点（如 `https://huggingface.co`）。使用 `--include` / `--exclude`（可重复）筛选仓库路径，`--revision` 固定版本，`--jobs`（默认 5）控制并发文件数，`--connections`（默认 4）控制每文件连接数。下载通过 aria2 续传，完成后只核对文件大小，不做加密哈希校验。若已有文件大小不匹配且无 aria2 续传状态，命令会报错而不会删除它。

默认最多选择 10 GiB 文件；如确需更大的全量权重，先看 `--dry-run` 的大小与磁盘空间，再明确使用 `--allow-large`。元数据响应的 commit SHA 会固定到下载 URL，目标目录也记录仓库、commit 和选中文件集合；再次运行同一集合可续传，分支更新、选中文件集合改变或目标目录已有未知文件时应另选目录。10 GiB 是元数据预检，不是服务器返回字节数的硬上限。`--dry-run` 不创建目标文件，即使超过 10 GiB 仍可预览。从0.1.6起默认根目录是当前目录，最终路径为`./<org>/<repo>`（不再加models/datasets层）。可用`CHATHFD_DOWNLOAD_ROOT`进程变量或ChatEnv活动profile配置根目录；`--local-dir`始终指定最终目录并优先覆盖。

ModelScope 是独立仓库平台，不是 HF-Mirror 的 `HF_ENDPOINT` 替代地址；仅当该模型/数据集也在 ModelScope 发布时，另用其 SDK，例如 `modelscope download --model Qwen/Qwen2.5-0.5B-Instruct --local_dir ./model`。不能假定 HF 仓库 ID 在 ModelScope 同步存在，也不能把其 SDK 当作本命令的自动回退。

参考：[HF-Mirror 下载说明](https://hf-mirror.com/) · [ModelScope CLI](https://www.modelscope.cn/docs/sdk/cli) · [Qwen 模型](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) · [MathArena 数据集](https://huggingface.co/datasets/MathArena/arxivmath-0926)。

## 当前 CLI 树（`--tree`）

```text
chathfd
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── download [REPO-ID] [--repo-type REPO-TYPE] [--revision REVISION] [--endpoint ENDPOINT] [--local-dir LOCAL-DIR] [--include INCLUDE] [--exclude EXCLUDE] [--connections CONNECTIONS] [--jobs JOBS] [--dry-run] [--allow-large] [--interactive]  # Download a public model or dataset with aria2c.
└── setup [--install]  # Check the aria2c download engine and offer installation.
```

`--tree-brief` 省略子命令参数签名。`src/` 是源码；`tests/cli-tests/` 是真实 CLI 测试；`tests/mock-cli-tests/` 是模拟测试；`docs/` 是长期文档。扩展前请阅读 `DEVELOP.md` 和 `AGENTS.md`。
