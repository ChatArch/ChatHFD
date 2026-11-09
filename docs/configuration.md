# 下载配置

<div class="grid cards" markdown>

-   :material-web: **端点**

    ---

    一个请求只使用一个 Hugging Face 兼容 HTTPS origin。

    [端点优先级](#endpoint)

-   :material-folder-outline: **输出与续传**

    ---

    一个目录对应固定仓库、commit 与文件集合。

    [目录身份](#resume)

-   :material-speedometer: **并发与筛选**

    ---

    分别控制单文件连接和同时下载的文件数。

    [传输参数](#selection)

</div>

## 端点优先级 {#endpoint}

| 来源 | 优先级 | 示例 |
| --- | --- | --- |
| 命令行 `--endpoint` | 最高 | `--endpoint https://huggingface.co` |
| 进程环境 `HF_ENDPOINT` | 其次 | `HF_ENDPOINT=https://hf-mirror.com` |
| 内置默认值 | 最后 | `https://hf-mirror.com` |

```bash
HF_ENDPOINT=https://hf-mirror.com chathfd download Qwen/Qwen3.8-Flash-Next --include config.json --dry-run
chathfd download Qwen/Qwen3.8-Flash-Next --endpoint https://huggingface.co --include config.json --dry-run
```

端点必须是 HTTPS origin，不能带用户名、密码、路径、查询参数或片段。当前 CLI 不持久化这些设置，也不会自动在镜像之间重试或回退。Python `download_repo()` 的 `endpoint` 是显式参数，不会代为读取 `HF_ENDPOINT`。

ModelScope 不是兼容的 `HF_ENDPOINT` 替换地址。它有独立的仓库 ID、发布状态与 SDK；当前 ChatHFD 没有 ModelScope 后端。也不要用旧的 Token 参数为当前下载器添加认证。

## 文件筛选与并发 {#selection}

```bash
chathfd download Qwen/Qwen3.8-Flash-Next \
  --include 'config.json' --include 'generation_config.json' \
  --exclude 'README*' --connections 4 --jobs 5 --dry-run
```

- `--include` 可重复，模式之间是“或”；未指定时选择所有文件。
- `--exclude` 可重复，对匹配的仓库相对路径排除；排除优先于包含。
- 用引号包住通配符，避免先被本地 shell 展开。
- `--connections` 为每个文件的连接/分片数，默认 4；`--jobs` 为并发文件数，默认 5。CLI 两者均限制在 1–10，不保证乘积一定变成实际连接数。
- `--revision` 接受分支、标签或 commit。下载 URL 固定为元数据返回的 commit，即使请求的是 `main`。

## 目录与续传身份 {#resume}

不传 `--local-dir` 时，模型写到 `./models/<org>/<repo>`，数据集写到 `./datasets/<org>/<repo>`；相对目录以命令启动位置为准。它不是 Hugging Face 标准缓存布局，也不会自动采用另一台机器的共享盘路径。

下载目录中生成：

```text
<destination>/
├── <selected repository files>
└── .chathfd/
    ├── selection.json    # endpoint/repo/type/commit/选中文件名与大小
    └── urls.txt          # aria2 输入清单
```

再次执行时要求端点、仓库、类型、commit 和选中文件集合一致。可恢复的部分文件依赖 aria2 的 `.aria2` 状态；同尺寸完整文件会跳过。更换文件集合、镜像或 commit 时，请选择新目录。未知旧文件、符号链接、目录逃逸、内部文件名冲突和没有续传状态的错误尺寸文件会被拒绝，不会自动删除或覆盖来“修复”。

`--dry-run` 只预检元数据、文件选择和路径，不创建记录，也不检查实际下载阶段的全部目录身份条件；预检成功不保证旧目录可直接复用。

## 大文件与校验 {#limits}

| 行为 | 实际契约 |
| --- | --- |
| 超过 10 GiB 的选择 | 预览可成功；实际传输须 `--allow-large` |
| 硬性网络配额 | 没有；大小来自服务端元数据 |
| 完成验收 | 文件存在、尺寸正确、没有残留 aria2 续传状态 |
| 加密哈希或模型可用性 | 当前不验证，不等于模型推理验收 |
| 下载器配置 | 禁用 aria2 默认配置和 netrc，避免隐式带出凭据 |

继续阅读[完整参数表](cli-tree.md#download)和[故障排查](troubleshooting.md)。
