# ChatHFD：模型与数据集下载

用一个命令下载公开 Hugging Face 仓库。默认 HF-Mirror，aria2 提供分片与多文件并发；先预检文件与体量，再开始传输。

<div class="grid cards" markdown>

-   :material-rocket-launch-outline: **第一次使用**

    ---

    安装、检查 aria2、下载一个模型配置文件和一个小型数学数据集。

    [进入快速开始](quickstart.md)

-   :material-file-tree-outline: **查完整命令**

    ---

    真实 CLI 树、全部参数、默认值、退出状态及安装确认行为。

    [打开 CLI 树](cli-tree.md)

-   :material-tune-variant: **选择镜像与目录**

    ---

    理清端点优先级、文件筛选、并发、固定版本和续传目录约束。

    [阅读下载配置](configuration.md)

-   :material-language-python: **从 Python 调用**

    ---

    复用元数据查询与下载函数，了解必填参数、输出和异常。

    [查看 Python 接口](python-api.md)

-   :material-vector-link: **了解能力边界**

    ---

    区分公开仓库、认证仓库、兼容镜像与 ModelScope 独立平台。

    [查看能力地图](capability-map.md)

-   :material-lifebuoy: **解决下载问题**

    ---

    依赖缺失、目录冲突、网络错误和旧 HFD 参数迁移。

    [打开故障排查](troubleshooting.md)

</div>

## 按任务选择入口

| 你要做什么 | 从哪里开始 | 是否写入文件 |
| --- | --- | --- |
| 看一个仓库有哪些文件、总共多大 | [`download --dry-run`](quickstart.md#preview) | 不创建下载文件 |
| 下载模型配置或权重 | [模型示例](quickstart.md#model) | 写入选中的文件 |
| 下载数学数据集 | [数据集示例](quickstart.md#dataset) | 写入数据集仓库文件 |
| 检查或安装 aria2 | [`setup`](cli-tree.md#setup) | 默认只检查；安装须确认 |
| 排查已有目录为什么被拒绝 | [目录与续传](configuration.md#resume) | 不自动删除旧文件 |
| 看命令如何映射到代码 | [接口树](interface-tree.md) | 只读说明 |

## 最小可运行流程

```bash
pip install ChatHFD==0.1.5
chathfd setup
chathfd download Qwen/Qwen3.8-Flash-Next --include config.json --dry-run
```

上面只查询配置文件元数据，不下载模型权重。继续操作见[快速开始](quickstart.md)。

!!! note "当前边界"
    仅支持公开仓库；不接收或转发账号 Token。完成后按文件大小校验，不做上游密码学哈希验证。10 GiB 是文件选择的元数据预检门槛，不是网络传输的硬限额。
