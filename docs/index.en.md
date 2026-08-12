# ChatHFD Documentation

ChatHFD is the ChatArch Hugging Face Download (HFD) tooling package entrypoint. These docs record the implemented CLI and future extension boundary.

<div class="grid cards" markdown>

-   :material-console-line: **CLI Tree**

    ---

    Review the current real command entrypoint, root-only boundary, and update rule.

    [View CLI Tree](cli-tree.md)

-   :material-package-variant: **Package Boundary**

    ---

    The package currently stays as an installable, testable, releasable tooling shell; real download orchestration commands are not exposed yet.

</div>

## Local Preview

```bash
pip install -e ".[docs]"
mkdocs serve
```
