# 接口树

## 从命令到文件

```text
chathfd.cli                         # 只负责 CLI 参数和调用
├── main                            # --help / --version / --tree / --tree-brief
├── download REPO_ID
│   └── chathfd.download.download_repo(...)
│       ├── fetch_metadata(...)     # Hub 模型/数据集元数据
│       ├── 文件选择、路径与身份检查
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
| `download_repo` | 仓库、端点、目录、筛选、并发与开关 | `None`；状态输出到控制台 | 非 dry-run 时写文件并运行 aria2 |
| `setup_aria2` | `install: bool` | `None`；检查/安装提示 | 默认不安装；显式模式仍需确认 |
| `ChathfdConfig` | ChatEnv provider 注册 | schema | 当前下载流程不使用其 API Key 认证 |

这些是当前导入面，不是 HTTP/MCP 服务，也没有独立的持久任务队列。`download_repo()` 的错误通过 `click.ClickException` 等异常报告，不返回结构化下载结果对象。

## 责任分工

- ChatStyle：真实 CLI 树、确认交互。
- ChatEnv：已有 schema/provider 注册；不是当前 Hugging Face 登录实现。
- ChatHFD：解析仓库元数据、选择文件、固定 commit、校验目标、构造 aria2 输入清单。
- aria2：网络传输、分片和续传；不因为它退出成功就省略最终大小检查。

[Python 调用示例](python-api.md) · [完整 CLI 参数](cli-tree.md)
