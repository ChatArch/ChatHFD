# ChatHFD 文档

ChatHFD 使用 HF-Mirror 和 aria2c 下载公开 Hugging Face 模型与数据集。先通过 `setup` 检查下载引擎，再通过 `download --dry-run` 预检文件和大小。

<div class="grid cards" markdown>

-   :material-console-line: **CLI 树**

    ---

    查看 `setup`、`download` 的真实参数和安全边界。

    [查看 CLI 树](cli-tree.md)

-   :material-package-variant: **下载模型与数据集**

    ---

    [README 示例](https://github.com/ChatArch/ChatHFD#下载示例) 展示 Qwen 模型的小型配置文件和 MathArena 数学数据集；默认源为 HF-Mirror，超过 10 GiB 需明确放行。

</div>

## 本地预览

```bash
pip install -e ".[docs]"
mkdocs serve
```
