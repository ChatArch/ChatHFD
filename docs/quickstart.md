# 快速开始

先选一个小范围任务，确认下载器、镜像和目录可用，再考虑完整权重。以下命令使用当前真实 CLI；不需要 Hugging Face 账号或 API Key。

<div class="grid cards" markdown>

-   :material-package-variant: **准备环境**

    ---

    Python 3.10+、ChatHFD 与 aria2。

    [安装与检查](#install)

-   :material-file-document-outline: **模型小样例**

    ---

    只取 Qwen 配置文件，不拉取整套权重。

    [下载模型配置](#model)

-   :material-database-outline: **数学数据集**

    ---

    下载一个小型公开数据集仓库。

    [下载数据集](#dataset)

-   :material-download-multiple: **完整权重**

    ---

    先核对文件清单、磁盘和网络，再显式放行大体量选择。

    [查看大文件流程](#large)

</div>

## 1. 安装与检查 {#install}

在自己的 Python 虚拟环境中安装，不需要修改系统 Python：

```bash
python -m pip install ChatHFD==0.1.5
chathfd --version
chathfd --tree
chathfd setup
```

`setup` 找到 aria2c 时输出可执行文件路径。缺少时会显示安装建议；需要工具尝试安装时再执行：

```bash
chathfd setup --install
```

它会再次确认后才调用已识别的包管理器。Linux 使用 apt-get、dnf 或 pacman，Homebrew 可用时使用 brew；没有支持的管理器时给出错误，需要自行安装。非 root 的 Linux 尝试使用 `sudo -n`，不会在后台等候密码。不要把密码输入到日志或聊天中。

## 2. 只预检，不下载 {#preview}

```bash
chathfd download Qwen/Qwen3.8-Flash-Next \
  --include 'config.json' \
  --dry-run
```

输出包含仓库类型、请求版本、固定 commit、选中文件、字节数和目标路径。`--dry-run` 不创建下载目录，也不要求 aria2c 已安装。

### 人工输入与脚本

从0.1.5起可在终端运行 `chathfd download -i`，按提示输入仓库、类型、目录、过滤和并发等；交互下载会先列出文件与总量，确认后才传输。只想预检时显式传 `--dry-run`。缺少仓库 ID 时，若输入/输出都是 TTY 且 `CHATARCH_AUTO_PROMPT` 未关闭，也只会自动询问仓库 ID，后续沿用默认值。

```bash
# 人工逐项填写（真正传输前还需确认）
chathfd download -i
# CI/脚本：禁止提问，但 -I 本身不是 dry-run
chathfd download Qwen/Qwen3.8-Flash-Next --include config.json --dry-run -I
```

`-I` 缺仓库 ID 时直接失败；`-i` 没有 TTY 时也直接失败。若要屏蔽自动提问，设置 `CHATARCH_AUTO_PROMPT=0`。此交互功能从0.1.5起提供，范围/选择/路径转换由ChatStyle0.2.1统一校验。

## 3. 下载模型配置文件 {#model}

```bash
chathfd download Qwen/Qwen3.8-Flash-Next \
  --include 'config.json' \
  --local-dir ./models/qwen-config \
  --connections 4 \
  --jobs 5
```

目标是 `./models/qwen-config/config.json`。这只是模型配置，不含权重，不能单凭它运行模型推理。需要固定某个版本时加 `--revision`，例如模型页给出的 commit。

相同端点、仓库、commit 和文件选择可再次执行同一命令；完整文件会跳过，aria2 状态允许继续未完成传输。若改变了选中文件集合或分支已经更新，请使用新目录，详见[续传约束](configuration.md#resume)。

## 4. 下载数学数据集 {#dataset}

```bash
chathfd download MathArena/arxivmath-0926 \
  --repo-type dataset \
  --dry-run

chathfd download MathArena/arxivmath-0926 \
  --repo-type dataset \
  --local-dir ./datasets/arxivmath-0926 \
  --connections 4 \
  --jobs 3
```

这里下载数据集仓库文件，包含说明与 Parquet 分片；不是自动加载到训练器中。数据含义、许可和用途请以[数据集卡](https://huggingface.co/datasets/MathArena/arxivmath-0926)为准。

## 5. 完整权重与大文件 {#large}

```bash
# 只列出文件与大小
chathfd download Qwen/Qwen3.8-Flash-Next --dry-run
```

查看完整模型仓库时不要把小样例的下载量当成权重总量。先核对磁盘、带宽和模型许可；必要时用 `--include '*.safetensors'` 等模式缩小范围。若所选文件超过 10 GiB，实际传输需明确加 `--allow-large`；本页不自动启动大规模下载。

## 下一步

| 问题 | 文档 |
| --- | --- |
| 怎样切换镜像、并发或目录？ | [下载配置](configuration.md) |
| 每个参数的默认值是什么？ | [完整 CLI 树](cli-tree.md) |
| 怎样直接在 Python 中调用？ | [Python 接口](python-api.md) |
| 为什么拒绝已有文件或私有仓库？ | [故障排查](troubleshooting.md) |
