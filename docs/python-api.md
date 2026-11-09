# Python 接口

<div class="grid cards" markdown>

-   :material-code-json: **查询元数据**

    ---

    获取仓库 commit 与文件列表，不创建下载目录。

    [查询示例](#metadata)

-   :material-download-outline: **执行或预览下载**

    ---

    显式传入所有参数，复用与 CLI 相同的检查。

    [下载示例](#download)

-   :material-tools: **检查下载器**

    ---

    在调用端明确选择只检查或询问安装。

    [依赖示例](#setup)

</div>

## 查询元数据 {#metadata}

```python
from chathfd.download import DEFAULT_ENDPOINT, fetch_metadata

metadata = fetch_metadata(
    endpoint=DEFAULT_ENDPOINT,
    repo_id="Qwen/Qwen3.8-Flash-Next",
    repo_type="model",
    revision="main",
)
print(metadata["sha"])
print(len(metadata.get("siblings", [])))
```

返回 Hub JSON 对象；服务器响应未保证所有条目都有相同可选字段。该函数只查询，不做最终文件选择、目录身份或传输验收。

## 预览与下载 {#download}

```python
from pathlib import Path
import click
from chathfd.download import DEFAULT_ENDPOINT, download_repo

try:
    download_repo(
        repo_id="Qwen/Qwen3.8-Flash-Next",
        repo_type="model",
        revision="main",
        endpoint=DEFAULT_ENDPOINT,
        local_dir=Path("models/qwen-config"),
        includes=("config.json",),
        excludes=(),
        connections=4,
        jobs=5,
        dry_run=True,
        allow_large=False,
    )
except click.ClickException as exc:
    print(f"下载未完成：{exc.format_message()}")
```

示例是元数据预览。实际写入需把 `dry_run` 改成 `False`；数据集调用改为 `repo_type="dataset"`，并显式提供数据集 ID 与新目录。`includes`/`excludes` 是字符串元组，不是用空格分隔的一个长字符串。

| 参数 | 类型或要求 |
| --- | --- |
| `repo_id`、`repo_type`、`revision` | 字符串；类型用 `model` 或 `dataset` |
| `endpoint` | Hugging Face 兼容 HTTPS origin；显式传入，不自动读环境变量 |
| `local_dir` | `Path` 或 `None`；显式值是最终目录，`None`使用进程变量/ChatEnv/当前目录根 + repo ID |
| `includes`、`excludes` | `tuple[str, ...]` |
| `connections`、`jobs` | 整数；Python 调用方应使用与 CLI 相同的 1–10 范围 |
| `dry_run`、`allow_large` | 布尔值 |
| `confirm` | 可选仅关键字回调 `(文件数: int, 总字节数: int) -> bool`；默认 `None` 不提问，拒绝时在任何文件写入前中止 |

函数返回 `None`，状态通过 Click 输出。元数据/下载失败会抛出 `click.ClickException`，回调拒绝则抛出 `click.Abort`；本地文件系统失败还可能抛出 `OSError`。`confirm` 用于调用端选择是否在预检后确认，不会因为 Python API 被调用就强制交互。它不是静默后台下载 API，暂不返回文件清单结果对象。

## 目录解析 {#directory}

目录解析可直接复用，不创建目录或请求网络：

```python
from chathfd.config import resolve_download_root
from chathfd.download import resolve_download_directory

print(resolve_download_root())
print(resolve_download_directory("Example/repository"))
```

`resolve_download_directory(repo_id, local_dir=None)`默认追加repo ID；显式`local_dir`优先并作为最终目录。CLI和`download_repo()`共享此逻辑，不读取其他命名空间的配置。

## 检查下载器 {#setup}

```python
from chathfd.setup import setup_aria2

setup_aria2(install=False)  # 只检查并提示，不修改系统包
```

`install=True` 仍会确认；不要在无人值守进程中假设它能自动获得 root 权限。完整行为见 [`setup`](cli-tree.md#setup)。
