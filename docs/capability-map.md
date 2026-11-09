# 能力地图

<div class="grid cards" markdown>

-   :material-download-outline: **仓库文件下载**

    ---

    公开模型、数据集、文件筛选、版本与目录。

    [运行示例](quickstart.md)

-   :material-shield-check-outline: **预检与续传**

    ---

    明确选择、commit 固定与目录身份；完成按大小检查。

    [阅读约束](configuration.md#resume)

-   :material-code-braces: **可复用接口**

    ---

    CLI 调用 importable Python 函数，aria2 执行传输。

    [接口映射](interface-tree.md)

</div>

## 已实现

| 能力 | 接口 | 边界 |
| --- | --- | --- |
| 模型与数据集 | `download`、`--repo-type` | 仅公开仓库文件，不启动训练或推理 |
| 兼容镜像 | `--endpoint`、`HF_ENDPOINT` | 默认 HF-Mirror，无自动跨平台回退 |
| 下载根目录 | `CHATHFD_DOWNLOAD_ROOT`、ChatEnv、`--local-dir` | 根默认当前目录，追加repo ID；显式local-dir是最终目录；不自动配置共享盘 |
| 并发与续传 | `--connections`、`--jobs` | 需本机 aria2，目录身份须匹配 |
| 文件和体量预检 | `--include`、`--exclude`、`--dry-run` | 元数据检查，不是网络硬限额 |
| 下载器准备 | `setup [--install]` | 安装是显式、需确认的系统包操作 |
| Python 调用 | `download_repo`、`fetch_metadata`、`setup_aria2` | 目前仍使用 Click 输出/异常，见接口页 |

## 不在当前能力内

- Hugging Face 私有或 gated 仓库登录、Token 管理及转发。
- ModelScope 原生下载、wget 后端、旧 `hfd` 别名自动替换。
- Hugging Face标准缓存迁移或旧目录自动接管、跨机器挂载、下载任务队列、后台守护进程。
- 上游加密哈希验收、模型推理验证或数据集训练流水线。

不要把单个配置文件或 README 的成功下载称为“模型权重已经下载完成”。查看[快速开始](quickstart.md#model)区分小样例和完整仓库。
