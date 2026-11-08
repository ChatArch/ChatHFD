# CLI 树

此页基于真实 `chathfd --tree` 输出。ChatStyle 将公开根名固定为 `chathfd`；`--tree-brief` 只省略子命令参数签名。

```text
chathfd
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── download <REPO-ID> [--repo-type REPO-TYPE] [--revision REVISION] [--endpoint ENDPOINT] [--local-dir LOCAL-DIR] [--include INCLUDE] [--exclude EXCLUDE] [--connections CONNECTIONS] [--jobs JOBS] [--dry-run] [--allow-large]  # Download a public model or dataset with aria2c.
└── setup [--install]  # Check the aria2c download engine and offer installation.
```

`chathfd --tree-brief` 的子命令行：

```text
├── download  # Download a public model or dataset with aria2c.
└── setup  # Check the aria2c download engine and offer installation.
```

## 下载边界

`setup` 检查本机 `aria2c`，缺失时给出安装指引；`setup --install` 需再次确认才会尝试安装。`download` 支持公开 Hugging Face 模型和 `--repo-type dataset` 数据集；默认 `https://hf-mirror.com`，可用 `HF_ENDPOINT` / `--endpoint` 覆盖。`--include` / `--exclude` 限定文件，`--dry-run` 预检大小，超过 10 GiB 需要 `--allow-large`。`--jobs` 和 `--connections` 分别设置并发文件数和每文件连接数。只按大小校验，不支持 gated/private 仓库 Token。完整示例与 ModelScope 区别见[仓库 README](https://github.com/ChatArch/ChatHFD#下载示例)。

更新 CLI 时先更新 Click 注册面及测试，再运行真实 `chathfd --tree` 和 `chathfd --tree-brief` 回填本页及 README。
