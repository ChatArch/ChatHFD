"""CLI contract for public Hugging Face model and dataset downloads."""

import json
from pathlib import Path

from click.testing import CliRunner

from chathfd.cli import main


COMMIT = "a" * 40
MODEL = {"id": "Qwen/Qwen3.8-Flash-Next", "sha": COMMIT, "gated": False, "siblings": [
    {"rfilename": "config.json", "size": 5},
    {"rfilename": "model.safetensors", "size": 100_000_000_000},
]}
DATASET = {"id": "MathArena/arxivmath-0926", "sha": COMMIT, "gated": False, "siblings": [
    {"rfilename": "data/train.parquet", "size": 4},
]}


def test_model_dry_run_defaults_to_mirror_without_creating_files(monkeypatch, tmp_path):
    from chathfd import download

    monkeypatch.setattr(download, "fetch_metadata", lambda *args: MODEL)
    result = CliRunner().invoke(main, ["download", "Qwen/Qwen3.8-Flash-Next", "--include", "config.json", "--dry-run", "--local-dir", str(tmp_path / "model")])
    assert result.exit_code == 0, result.output
    assert "https://hf-mirror.com" in result.output
    assert "config.json" in result.output
    assert "5 bytes" in result.output
    assert not (tmp_path / "model").exists()


def test_dataset_uses_dataset_api_and_aria2_options(monkeypatch, tmp_path):
    from chathfd import download

    calls = []
    monkeypatch.setattr(download, "fetch_metadata", lambda *args: DATASET)
    monkeypatch.setattr(download.shutil, "which", lambda _: "/usr/bin/aria2c")

    def fake_run(command, check):
        calls.append(command)
        (tmp_path / "data" / "data" / "train.parquet").write_bytes(b"data")

    monkeypatch.setattr(download.subprocess, "run", fake_run)
    result = CliRunner().invoke(main, ["download", "MathArena/arxivmath-0926", "--repo-type", "dataset", "--local-dir", str(tmp_path / "data"), "--jobs", "2", "--connections", "3"])
    assert result.exit_code == 0, result.output
    assert len(calls) == 1
    assert "--max-concurrent-downloads=2" in calls[0]
    assert "--max-connection-per-server=3" in calls[0]
    assert "--no-conf=true" in calls[0]
    assert "--no-netrc=true" in calls[0]
    urls = (tmp_path / "data" / ".chathfd" / "urls.txt").read_text()
    assert f"https://hf-mirror.com/datasets/MathArena/arxivmath-0926/resolve/{COMMIT}/data/train.parquet" in urls


def test_large_download_requires_opt_in(monkeypatch, tmp_path):
    from chathfd import download

    monkeypatch.setattr(download, "fetch_metadata", lambda *args: MODEL)
    result = CliRunner().invoke(main, ["download", "Qwen/Qwen3.8-Flash-Next", "--local-dir", str(tmp_path / "model")])
    assert result.exit_code != 0
    assert "--allow-large" in result.output
    assert not (tmp_path / "model").exists()


def test_rejects_unsafe_metadata_path_and_symlink(monkeypatch, tmp_path):
    from chathfd import download

    monkeypatch.setattr(download, "fetch_metadata", lambda *args: {"sha": COMMIT, "siblings": [{"rfilename": "../escape", "size": 4}]})
    result = CliRunner().invoke(main, ["download", "team/repo", "--local-dir", str(tmp_path / "output")])
    assert result.exit_code != 0
    assert not (tmp_path / "output").exists()

    (tmp_path / "output" / "data").parent.mkdir(parents=True)
    (tmp_path / "output" / "data").symlink_to(tmp_path, target_is_directory=True)
    monkeypatch.setattr(download, "fetch_metadata", lambda *args: DATASET)
    result = CliRunner().invoke(main, ["download", "MathArena/arxivmath-0926", "--repo-type", "dataset", "--local-dir", str(tmp_path / "output"), "--dry-run"])
    assert result.exit_code != 0


def test_repo_id_and_empty_filter_fail(monkeypatch, tmp_path):
    from chathfd import download

    monkeypatch.setattr(download, "fetch_metadata", lambda *args: DATASET)
    assert CliRunner().invoke(main, ["download", "../repo", "--dry-run"]).exit_code != 0
    result = CliRunner().invoke(main, ["download", "team/repo", "--include", "missing", "--dry-run", "--local-dir", str(tmp_path / "repo")])
    assert result.exit_code != 0
    assert "No files" in result.output


def test_rejects_aria2_control_lines_from_metadata_or_destination(monkeypatch, tmp_path):
    from chathfd import download

    monkeypatch.setattr(download, "fetch_metadata", lambda *args: {"sha": COMMIT, "siblings": [{"rfilename": "file\n dir=/elsewhere", "size": 4}]})
    result = CliRunner().invoke(main, ["download", "team/repo", "--dry-run", "--local-dir", str(tmp_path / "model")])
    assert result.exit_code != 0
    assert not (tmp_path / "model").exists()
    monkeypatch.setattr(download, "fetch_metadata", lambda *args: DATASET)
    result = CliRunner().invoke(main, ["download", "team/repo", "--dry-run", "--local-dir", str(tmp_path / "bad\nout")])
    assert result.exit_code != 0
    assert not (tmp_path / "bad\nout").exists()


def test_rejects_reserved_control_file_and_missing_commit(monkeypatch, tmp_path):
    from chathfd import download

    monkeypatch.setattr(download, "fetch_metadata", lambda *args: {"sha": COMMIT, "siblings": [{"rfilename": ".chathfd/urls.txt", "size": 4}]})
    result = CliRunner().invoke(main, ["download", "team/repo", "--dry-run", "--local-dir", str(tmp_path / "repo")])
    assert result.exit_code != 0
    assert "reserved" in result.output
    monkeypatch.setattr(download, "fetch_metadata", lambda *args: {"siblings": [{"rfilename": "README.md", "size": 4}]})
    result = CliRunner().invoke(main, ["download", "team/repo", "--dry-run", "--local-dir", str(tmp_path / "repo")])
    assert result.exit_code != 0
    assert "commit SHA" in result.output
    assert not (tmp_path / "repo").exists()


def test_revision_identity_guards_same_size_files_and_resume(monkeypatch, tmp_path):
    from chathfd import download

    current = dict(DATASET)
    monkeypatch.setattr(download, "fetch_metadata", lambda *args: current)
    monkeypatch.setattr(download.shutil, "which", lambda _: "/usr/bin/aria2c")
    root = tmp_path / "dataset"
    existing = root / "data" / "train.parquet"
    existing.parent.mkdir(parents=True)
    existing.write_bytes(b"old!")
    args = ["download", "MathArena/arxivmath-0926", "--repo-type", "dataset", "--local-dir", str(root)]
    result = CliRunner().invoke(main, args)
    assert result.exit_code != 0
    assert "fresh destination" in result.output

    existing.unlink()
    calls = []

    def fake_run(command, check):
        calls.append(command)
        existing.write_bytes(b"data")

    monkeypatch.setattr(download.subprocess, "run", fake_run)
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 0, result.output
    assert len(calls) == 1
    assert CliRunner().invoke(main, args).exit_code == 0
    assert len(calls) == 1
    current = dict(DATASET, sha="b" * 40)
    result = CliRunner().invoke(main, args)
    assert result.exit_code != 0
    assert "another repository, endpoint, commit or file selection" in result.output
    assert len(calls) == 1
    assert existing.read_bytes() == b"data"


def test_expanding_selection_rejects_legacy_same_size_file(monkeypatch, tmp_path):
    from chathfd import download

    metadata = {"sha": COMMIT, "siblings": [
        {"rfilename": "config.json", "size": 4},
        {"rfilename": "old.txt", "size": 4},
    ]}
    monkeypatch.setattr(download, "fetch_metadata", lambda *args: metadata)
    monkeypatch.setattr(download.shutil, "which", lambda _: "/usr/bin/aria2c")
    root = tmp_path / "model"
    root.mkdir()
    (root / "old.txt").write_bytes(b"old!")
    calls = []

    def fake_run(command, check):
        calls.append(command)
        (root / "config.json").write_bytes(b"new!")

    monkeypatch.setattr(download.subprocess, "run", fake_run)
    base = ["download", "team/repo", "--local-dir", str(root)]
    first = CliRunner().invoke(main, [*base, "--include", "config.json"])
    assert first.exit_code == 0, first.output
    expanded = CliRunner().invoke(main, base)
    assert expanded.exit_code != 0
    assert "file selection" in expanded.output
    assert (root / "old.txt").read_bytes() == b"old!"
    assert len(calls) == 1


def test_dangling_selected_symlink_to_control_file_is_rejected(monkeypatch, tmp_path):
    from chathfd import download

    monkeypatch.setattr(download, "fetch_metadata", lambda *args: {"sha": COMMIT, "siblings": [
        {"rfilename": "config.json", "size": 4},
    ]})
    root = tmp_path / "model"
    root.mkdir()
    (root / "config.json").symlink_to(".chathfd/selection.json")
    result = CliRunner().invoke(main, ["download", "team/repo", "--local-dir", str(root)])
    assert result.exit_code != 0
    assert "symlink" in result.output
    assert not (root / ".chathfd").exists()


def test_dangling_sidecar_symlink_to_control_file_is_rejected(monkeypatch, tmp_path):
    from chathfd import download

    monkeypatch.setattr(download, "fetch_metadata", lambda *args: {"sha": COMMIT, "siblings": [
        {"rfilename": "config.json", "size": 4},
    ]})
    root = tmp_path / "model"
    root.mkdir()
    (root / "config.json.aria2").symlink_to(".chathfd/selection.json")
    result = CliRunner().invoke(main, ["download", "team/repo", "--local-dir", str(root)])
    assert result.exit_code != 0
    assert "symlinked aria2" in result.output
    assert not (root / ".chathfd").exists()


def test_sidecar_collisions_and_oversize_preview(monkeypatch, tmp_path):
    from chathfd import download

    monkeypatch.setattr(download, "fetch_metadata", lambda *args: {"sha": COMMIT, "siblings": [
        {"rfilename": "foo", "size": 4}, {"rfilename": "foo.aria2", "size": 4},
    ]})
    result = CliRunner().invoke(main, ["download", "team/repo", "--local-dir", str(tmp_path / "repo")])
    assert result.exit_code != 0
    assert "conflict" in result.output
    assert not (tmp_path / "repo").exists()
    monkeypatch.setattr(download, "fetch_metadata", lambda *args: MODEL)
    result = CliRunner().invoke(main, ["download", "Qwen/Qwen3.8-Flash-Next", "--dry-run", "--local-dir", str(tmp_path / "repo")])
    assert result.exit_code == 0, result.output
    assert "exceeds 10 GiB" in result.output
    assert not (tmp_path / "repo").exists()
