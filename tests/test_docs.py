"""Keep bilingual docs, examples and publication mechanics tied to real APIs."""
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import re
import shlex
import subprocess

import click
from click.testing import CliRunner
import pytest

from chathfd import __version__
from chathfd.cli import main

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index", "quickstart", "cli-tree", "configuration", "capability-map", "interface-tree", "python-api", "troubleshooting")


@pytest.mark.parametrize("page", PAGES)
def test_bilingual_sources_and_navigation_exist(page):
    for suffix in (".md", ".en.md"):
        text = (ROOT / "docs" / (page + suffix)).read_text(encoding="utf-8")
        assert text.startswith("# ")
    assert page + ".md" in (ROOT / "mkdocs.yml").read_text(encoding="utf-8")


@pytest.mark.parametrize("suffix", (".md", ".en.md"))
def test_tree_page_contains_both_actual_runtime_trees(suffix):
    text = (ROOT / "docs" / ("cli-tree" + suffix)).read_text(encoding="utf-8")
    for option in ("--tree", "--tree-brief"):
        actual = CliRunner().invoke(main, [option])
        assert actual.exit_code == 0
        assert actual.output.strip() in text
    for command in main.commands.values():
        for param in command.params:
            if isinstance(param, click.Argument):
                assert param.name.upper() in text
            elif isinstance(param, click.Option):
                for option in param.opts:
                    assert option in text


def test_install_examples_pin_the_source_version():
    for name in ("README.md", "README.en.md", "docs/index.md", "docs/index.en.md", "docs/quickstart.md", "docs/quickstart.en.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert f"ChatHFD=={__version__}" in text


@pytest.mark.parametrize("suffix", (".md", ".en.md"))
def test_hub_and_quickstart_have_real_cards_and_task_links(suffix):
    for name in ("index", "quickstart"):
        text = (ROOT / "docs" / (name + suffix)).read_text(encoding="utf-8")
        assert '<div class="grid cards" markdown>' in text
        assert ":material-" in text
    assert "quickstart.md" in (ROOT / "docs" / ("index" + suffix)).read_text()


@pytest.mark.parametrize("page", PAGES)
@pytest.mark.parametrize("suffix", (".md", ".en.md"))
def test_documented_cli_examples_parse_without_invocation(page, suffix, monkeypatch):
    monkeypatch.setenv("CHATARCH_AUTO_PROMPT", "0")
    text = (ROOT / "docs" / (page + suffix)).read_text(encoding="utf-8")
    for block in re.findall(r"```bash\n(.*?)```", text, re.S):
        for line in block.replace("\\\n", " ").splitlines():
            tokens = shlex.split(line, comments=True)
            if "chathfd" not in tokens:
                continue
            args = tokens[tokens.index("chathfd") + 1:]
            try:
                if args and args[0] in main.commands:
                    command = main.commands[args[0]]
                    with command.make_context("chathfd " + args[0], args[1:]):
                        pass
                else:
                    with main.make_context("chathfd", args):
                        pass
            except click.exceptions.Exit as exc:
                assert exc.exit_code == 0


@pytest.mark.parametrize("suffix", (".md", ".en.md"))
def test_python_examples_execute_with_offline_metadata(suffix, monkeypatch, tmp_path):
    import chathfd.download as downloader
    import chathfd.setup as setup

    monkeypatch.chdir(tmp_path)
    metadata = {"sha": "a" * 40, "gated": False, "siblings": [{"rfilename": "config.json", "size": 10}]}
    monkeypatch.setattr(downloader, "fetch_metadata", lambda *args, **kwargs: metadata)
    monkeypatch.setattr(setup.shutil, "which", lambda name: "/usr/bin/aria2c" if name == "aria2c" else None)
    text = (ROOT / "docs" / ("python-api" + suffix)).read_text(encoding="utf-8")
    for block in re.findall(r"```python\n(.*?)```", text, re.S):
        ast.parse(block)
        exec(compile(block, "documented-python-example", "exec"), {})
    assert not (tmp_path / "models").exists()


def _preview_module():
    spec = importlib.util.spec_from_file_location("preview_preserve", ROOT / "scripts" / "preserve_docs_preview.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_production_copies_only_preview_not_stale_root(monkeypatch, tmp_path):
    module = _preview_module()
    payloads = {"dev/index.html": b"preview", "dev/assets/app.js": b"asset", "versions.json": b"[]", "stale.html": b"stale"}

    def fake_run(args, check, capture_output):
        if args[1] == "ls-tree":
            body = b"".join(b"100644 blob deadbeef\t" + name.encode() + b"\0" for name in payloads)
        else:
            body = payloads[args[2].split(":", 1)[1]]
        return subprocess.CompletedProcess(args, 0, stdout=body)

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    assert module.preserve_preview(tmp_path) == 3
    assert (tmp_path / "dev/index.html").read_bytes() == b"preview"
    assert not (tmp_path / "stale.html").exists()


@pytest.mark.parametrize("mode,path", [("120000", "dev/link"), ("100644", "dev/../../escape")])
def test_preview_copy_rejects_nonregular_and_escaping_paths(mode, path, monkeypatch, tmp_path):
    module = _preview_module()
    monkeypatch.setattr(module.subprocess, "run", lambda args, **kwargs: subprocess.CompletedProcess(args, 0, stdout=f"{mode} blob abc\t{path}\0".encode()))
    with pytest.raises(ValueError):
        module.preserve_preview(tmp_path / "site")
    assert not (tmp_path / "escape").exists()


def test_preview_and_production_share_lock_and_keep_preview_language_prefix():
    preview = (ROOT / ".github/workflows/preview.yaml").read_text()
    deploy = (ROOT / ".github/workflows/deploy.yaml").read_text()
    for text in (preview, deploy):
        assert "group: docs-pages-${{ github.repository }}" in text
        assert "cancel-in-progress: false" in text
    assert "CHATARCH_DOCS_ZH_PREFIX: /ChatHFD/dev/" in preview
    assert "CHATARCH_DOCS_EN_PREFIX: /ChatHFD/dev/en/" in preview
    assert "preserve_docs_preview.py" in deploy
    assert "ghp-import --no-jekyll --push --force site" in deploy
