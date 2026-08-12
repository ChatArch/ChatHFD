from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_publish_workflow_is_tag_only_oidc_and_main_guarded():
    workflow = (ROOT / ".github" / "workflows" / "publish.yml").read_text(encoding="utf-8")

    assert 'tags:' in workflow
    assert 'workflow_dispatch' not in workflow
    assert 'id-token: write' in workflow
    assert 'pypa/gh-action-pypi-publish@release/v1' in workflow
    assert 'git fetch --no-tags origin main:refs/remotes/origin/main' in workflow
    assert 'git merge-base --is-ancestor "${GITHUB_SHA}" refs/remotes/origin/main' in workflow
    legacy_secret_markers = ["PYPI" + "_API_TOKEN", "TWINE" + "_PASSWORD", "secrets" + ".PYPI"]
    assert all(marker not in workflow for marker in legacy_secret_markers)


def test_preview_workflow_uses_site_url_from_mkdocs():
    workflow = (ROOT / ".github" / "workflows" / "preview.yaml").read_text(encoding="utf-8")

    assert 'CHATARCH_PREVIEW_URL' in workflow
    assert 'site_url=$(python' in workflow
    assert 'mkdocs.yml' in workflow
    assert 'github.io' not in workflow


def test_mkdocs_material_renderer_and_public_domain():
    config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert 'site_url: https://arch.gh.wzhecnu.cn/ChatHFD/' in config
    assert 'mkdocs-static-i18n' not in config  # dependency belongs to pyproject; plugin name is i18n
    assert 'pymdownx.emoji' in config
    assert 'material.extensions.emoji.twemoji' in config
    assert 'material.extensions.emoji.to_svg' in config
    assert 'cli-tree.md' in config
