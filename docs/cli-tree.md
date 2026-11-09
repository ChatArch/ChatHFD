# CLI 树与命令参考

完整树来自真实 `chathfd --tree`，不是规划中的命令。参数很多时，先看简明树，再进入对应动作。

## 简明命令树

```text
chathfd
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── download  # Download a public model or dataset with aria2c.
└── setup  # Check the aria2c download engine and offer installation.
```

## 完整命令树

```text
chathfd
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── download <REPO-ID> [--repo-type REPO-TYPE] [--revision REVISION] [--endpoint ENDPOINT] [--local-dir LOCAL-DIR] [--include INCLUDE] [--exclude EXCLUDE] [--connections CONNECTIONS] [--jobs JOBS] [--dry-run] [--allow-large]  # Download a public model or dataset with aria2c.
└── setup [--install]  # Check the aria2c download engine and offer installation.
```

## 根选项

| 选项 | 作用 | 副作用 |
| --- | --- | --- |
| `--help` | 当前命令帮助 | 无下载 |
| `--version` | 已安装包版本 | 无下载 |
| `--tree` | 真实注册树，包含参数签名 | 无下载 |
| `--tree-brief` | 相同命令节点，省略参数签名 | 无下载 |

## 下载动作 {#download}

```text
chathfd download REPO_ID [OPTIONS]
```

`REPO_ID` 为 `组织/仓库`，也接受 Hub 支持的单段旧仓库名。模型和数据集共用同一个动作；预览是选项，不是另一个子命令。

| 参数 | 默认值 | 含义 |
| --- | --- | --- |
| `--repo-type [model|dataset]` | `model` | 仓库类型 |
| `--revision TEXT` | `main` | 分支、标签或 commit |
| `--endpoint TEXT` | `HF_ENDPOINT` 或 HF-Mirror | 兼容 HTTPS origin；显式选项优先 |
| `--local-dir DIRECTORY` | 当前目录下 `models/` 或 `datasets/` + repo ID | 所选文件的输出根 |
| `--include TEXT` | 不限制 | 可重复的包含 glob |
| `--exclude TEXT` | 无 | 可重复的排除 glob |
| `--connections INTEGER` | `4`，范围 1–10 | 每个文件的连接/分片数 |
| `--jobs INTEGER` | `5`，范围 1–10 | 同时下载的文件数 |
| `--dry-run` | 关闭 | 查询并列出文件/大小，不创建下载文件 |
| `--allow-large` | 关闭 | 允许所选文件超过 10 GiB 后实际传输 |
| `--help` | — | 仅显示本动作帮助 |

实际传输创建目标文件与 `.chathfd` 记录，并调用 aria2。预检与传输完成条件见[下载配置](configuration.md)。公开仓库以外的登录、Token、wget 和 ModelScope 后端不在当前参数面内。

```bash
chathfd download Qwen/Qwen3.8-Flash-Next --include config.json --dry-run
chathfd download MathArena/arxivmath-0926 --repo-type dataset --dry-run
```

## 下载器准备 {#setup}

```text
chathfd setup [--install] [--help]
```

| 参数 | 行为 |
| --- | --- |
| 无选项 | 检查 aria2c；存在时打印路径，缺失时给出安装指引 |
| `--install` | 仅当缺失时提出明确安装命令；再次确认后才运行包管理器 |
| `--help` | 显示帮助，不安装 |

已有 aria2c 时不会重复安装。当前不安装外部 `hfd.sh`、不启动守护进程、不改镜像或下载目录配置。无人确认的安装不会继续；包管理器错误非零退出。

## 输出与退出状态

- 下载成功或预检完成：退出 0；输出选择信息，实际下载后输出按大小核验结果。
- 参数错误、网络/元数据错误或实际下载不完整：非零退出；不要只解析“开始下载”字样判断成功。
- `setup` 在检测/给出安装指引后可正常结束；退出 0 不等于缺失依赖已经安装，以 `aria2c ready` 和可执行文件为准。
- 当前无 `model`、`dataset`、`login`、`mirror` 等额外子命令；勿把旧 `hfd` 参数当作本工具参数。

[快速开始](quickstart.md) · [Python 接口](python-api.md) · [旧接口对照](troubleshooting.md)
