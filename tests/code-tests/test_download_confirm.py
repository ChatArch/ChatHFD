"""The reusable Python downloader keeps confirmation opt-in and side-effect safe."""

import click
import pytest

from chathfd import download


REPO = "Example/small-model"
COMMIT = "a" * 40


def _download(tmp_path, *, dry_run, confirm):
    download.download_repo(
        repo_id=REPO,
        repo_type="model",
        revision="main",
        endpoint=download.DEFAULT_ENDPOINT,
        local_dir=tmp_path / "model",
        includes=("config.json",),
        excludes=(),
        connections=4,
        jobs=5,
        dry_run=dry_run,
        allow_large=False,
        confirm=confirm,
    )


def test_declined_callback_receives_preflight_and_prevents_writes(monkeypatch, tmp_path):
    metadata = {"sha": COMMIT, "gated": False, "siblings": [{"rfilename": "config.json", "size": 4}]}
    monkeypatch.setattr(download, "fetch_metadata", lambda *args: metadata)
    calls = []

    def refuse(count, total):
        calls.append((count, total))
        return False

    with pytest.raises(click.Abort):
        _download(tmp_path, dry_run=False, confirm=refuse)
    assert calls == [(1, 4)]
    assert not (tmp_path / "model").exists()


def test_dry_run_does_not_call_confirmation(monkeypatch, tmp_path):
    metadata = {"sha": COMMIT, "gated": False, "siblings": [{"rfilename": "config.json", "size": 4}]}
    monkeypatch.setattr(download, "fetch_metadata", lambda *args: metadata)

    def unexpected(*args):
        raise AssertionError("dry run must not request transfer confirmation")

    _download(tmp_path, dry_run=True, confirm=unexpected)
    assert not (tmp_path / "model").exists()
