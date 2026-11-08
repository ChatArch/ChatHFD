# ChatHFD Documentation

ChatHFD downloads public Hugging Face models and datasets using HF-Mirror and aria2c. Check the engine with `setup`, then preview file selection and size with `download --dry-run`.

<div class="grid cards" markdown>

-   :material-console-line: **CLI Tree**

    ---

    Review the real `setup` and `download` commands, options, and safety boundaries.

    [View CLI Tree](cli-tree.md)

-   :material-package-variant: **Models and Datasets**

    ---

    [README examples](https://github.com/ChatArch/ChatHFD/blob/main/README.en.md#examples) show a small Qwen model config and a MathArena math dataset; the default source is HF-Mirror, and selections over 10 GiB require explicit opt-in.

</div>

## Local Preview

```bash
pip install -e ".[docs]"
mkdocs serve
```
