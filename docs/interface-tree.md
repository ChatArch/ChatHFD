# 接口树

## 从命令到文件

```text
chathfd.cli                         # 只负责 CLI 参数和调用
├── main                            # --help / --version / --tree / --tree-brief
├── download [REPO_ID] [-i|-I]      # ChatStyle 补参，人工预检后确认
│   └── chathfd.download.download_repo(...)
│       ├── resolve_download_directory(...) # 最终目录；复用ChatEnv下载根目录
│       ├── fetch_metadata(...)     # Hub 模型/数据集元数据
│       ├── 文件选择、路径与身份检查
│       ├── 可选 confirm 回调        # 预检后、任何写入前
│       ├── .chathfd/selection.json + urls.txt
│       └── aria2c                  # 并发、分片与续传
└── setup [--install]
    └── chathfd.setup.setup_aria2(...)
        ├── shutil.which           # 检查 aria2c 与包管理器
        └── 包管理器                # 只有明确安装并确认后执行
```

## 调用契约

| 接口 | 输入 | 输出 | 副作用 |
| --- | --- | --- | --- |
| `fetch_metadata` | endpoint、repo_id、repo_type、revision | 元数据 `dict` | HTTP GET；不写下载文件 |
| `resolve_download_root` | 进程变量、活动ChatEnv profile或`.` | 有效根目录`Path` | 只读；不创建目录或请求网络 |
| `resolve_download_directory` | repo_id、可选最终local_dir | 最终目录`Path` | 只读验证；CLI/Python共用 |
| `download_repo` | 仓库、端点、目录、筛选、并发、开关与可选 `confirm` 回调 | `None`；状态输出到控制台 | 仅非 dry-run 时：未设置回调或回调确认后，才写文件并运行 aria2 |
| `setup_aria2` | `install: bool` | `None`；检查/安装提示 | 默认不安装；显式模式仍需确认 |
| `ChathfdConfig` | ChatEnv下载根目录字段 | schema及只读路径验证hook | 不创建下载目录、不使用遗留API Key认证 |

这些是当前导入面，不是 HTTP/MCP 服务，也没有独立的持久任务队列。`download_repo()` 的错误通过 `click.ClickException` 等异常报告，不返回结构化下载结果对象。

## 责任分工

- ChatStyle：真实 CLI 树、可选的输入解析与确认交互。
- ChatEnv：保存活动profile中的下载根目录，下载读取但不自动保存；不是Hugging Face登录实现。
- ChatHFD：解析仓库元数据、选择文件、固定 commit、校验目标、构造 aria2 输入清单。
- aria2：网络传输、分片和续传；不因为它退出成功就省略最终大小检查。

[Python 调用示例](python-api.md) · [完整 CLI 参数](cli-tree.md)
