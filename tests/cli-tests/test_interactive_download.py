"""The download leaf uses ChatStyle's shared interactive contract."""

from click.testing import CliRunner
import chatstyle.core.interactive as interactive_core

from chathfd.cli import main


REPO = "Example/small-model"
COMMIT = "a" * 40
METADATA = {"sha": COMMIT, "gated": False, "siblings": [{"rfilename": "config.json", "size": 4}]}


def fake_metadata(monkeypatch):
    from chathfd import download

    calls = []

    def fetch(*args):
        calls.append(args)
        return METADATA

    monkeypatch.setattr(download, "fetch_metadata", fetch)
    return calls


def test_no_interactive_missing_repo_fails_fast_without_network(monkeypatch):
    calls = fake_metadata(monkeypatch)
    result = CliRunner().invoke(main, ["download", "-I"])
    assert result.exit_code != 0
    assert "Missing required value: repo_id" in result.output
    assert calls == []


def test_forced_interaction_without_tty_fails_before_network(monkeypatch):
    calls = fake_metadata(monkeypatch)
    monkeypatch.setattr(interactive_core, "is_interactive_available", lambda: False)
    result = CliRunner().invoke(main, ["download", REPO, "-i"])
    assert result.exit_code != 0
    assert "no TTY" in result.output
    assert calls == []


def test_auto_prompt_can_be_disabled_for_tty(monkeypatch):
    calls = fake_metadata(monkeypatch)
    monkeypatch.setattr(interactive_core, "is_interactive_available", lambda: True)
    result = CliRunner().invoke(main, ["download"], input=f"{REPO}\n", env={"CHATARCH_AUTO_PROMPT": "0"})
    assert result.exit_code != 0
    assert "Missing required value: repo_id" in result.output
    assert "Repository ID" not in result.output
    assert calls == []


def test_automatic_repo_prompt_previews_then_cancel_is_no_write(monkeypatch, tmp_path):
    calls = fake_metadata(monkeypatch)
    monkeypatch.setattr(interactive_core, "is_interactive_available", lambda: True)
    root = tmp_path / "model"
    result = CliRunner().invoke(main, ["download", "--include", "config.json", "--local-dir", str(root)], input=f"{REPO}\nn\n")
    assert result.exit_code != 0
    assert "Repository ID" in result.output
    assert "4 bytes" in result.output
    assert not root.exists()
    assert len(calls) == 1


def test_forced_interaction_prompts_missing_options_and_keeps_explicit_values(monkeypatch, tmp_path):
    from chatstyle.input import resolve as resolver

    calls = fake_metadata(monkeypatch)
    monkeypatch.setattr(interactive_core, "is_interactive_available", lambda: True)
    prompted = []

    def text(message, default="", password=False):
        prompted.append((message, default))
        return default

    def select(message, choices):
        prompted.append((message, choices))
        return choices[0]

    def path(message, default=""):
        prompted.append((message, default))
        return default

    monkeypatch.setattr(resolver.prompt_runtime, "ask_text", text)
    monkeypatch.setattr(resolver.prompt_runtime, "ask_select", select)
    monkeypatch.setattr(resolver.prompt_runtime, "ask_path", path)
    monkeypatch.setattr(resolver.prompt_runtime, "ask_confirm", lambda message, default=False: default)
    root = tmp_path / "dataset"
    result = CliRunner().invoke(main, ["download", REPO, "--repo-type", "dataset", "--local-dir", str(root), "--include", "config.json", "--dry-run", "-i"])
    assert result.exit_code == 0, result.output
    assert "Dry run" in result.output
    assert calls[0][2] == "dataset"
    assert root.exists() is False
    assert prompted
    assert not any(item[0] == "Repository ID" for item in prompted)
    assert not any(item[0] == "Repository type" for item in prompted)
    assert not any(item[0] == "Destination directory" for item in prompted)


def test_no_interactive_complete_args_actually_download(monkeypatch, tmp_path):
    from chathfd import download

    fake_metadata(monkeypatch)
    monkeypatch.setattr(download.shutil, "which", lambda _: "/usr/bin/aria2c")
    calls = []
    root = tmp_path / "model"

    def run(args, check):
        calls.append(args)
        (root / "config.json").write_bytes(b"data")

    monkeypatch.setattr(download.subprocess, "run", run)
    result = CliRunner().invoke(main, ["download", REPO, "--include", "config.json", "--local-dir", str(root), "-I"])
    assert result.exit_code == 0, result.output
    assert len(calls) == 1
    assert (root / "config.json").read_bytes() == b"data"


def test_dry_run_remains_distinct_from_no_interactive(monkeypatch, tmp_path):
    fake_metadata(monkeypatch)
    root = tmp_path / "model"
    result = CliRunner().invoke(main, ["download", REPO, "--include", "config.json", "--local-dir", str(root), "--dry-run", "-I"])
    assert result.exit_code == 0, result.output
    assert not root.exists()


def test_complete_args_on_tty_do_not_auto_prompt(monkeypatch, tmp_path):
    fake_metadata(monkeypatch)
    monkeypatch.setattr(interactive_core, "is_interactive_available", lambda: True)
    root = tmp_path / "model"
    result = CliRunner().invoke(main, ["download", REPO, "--include", "config.json", "--local-dir", str(root), "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "Repository type" not in result.output
    assert "Continue" not in result.output
    assert not root.exists()


def test_explicit_force_still_prompts_when_auto_prompt_disabled(monkeypatch, tmp_path):
    from chatstyle.input import resolve as resolver

    fake_metadata(monkeypatch)
    monkeypatch.setattr(interactive_core, "is_interactive_available", lambda: True)
    prompted = []

    def text(message, default="", password=False):
        prompted.append(message)
        return default

    monkeypatch.setattr(resolver.prompt_runtime, "ask_text", text)
    monkeypatch.setattr(resolver.prompt_runtime, "ask_select", lambda *args: "model")
    monkeypatch.setattr(resolver.prompt_runtime, "ask_path", lambda *args, **kwargs: "")
    monkeypatch.setattr(resolver.prompt_runtime, "ask_confirm", lambda *args, **kwargs: False)
    root = tmp_path / "model"
    result = CliRunner().invoke(
        main, ["download", REPO, "--include", "config.json", "--local-dir", str(root), "--dry-run", "-i"],
        env={"CHATARCH_AUTO_PROMPT": "0"},
    )
    assert result.exit_code == 0, result.output
    assert "Revision" in prompted
    assert not root.exists()


def test_oversized_selection_rejected_before_confirmation(monkeypatch, tmp_path):
    from chathfd import download

    metadata = {"sha": COMMIT, "gated": False, "siblings": [{"rfilename": "weights.safetensors", "size": 11 * 1024**3}]}
    monkeypatch.setattr(download, "fetch_metadata", lambda *args: metadata)
    monkeypatch.setattr(interactive_core, "is_interactive_available", lambda: True)
    root = tmp_path / "model"
    result = CliRunner().invoke(main, ["download", "--local-dir", str(root)], input=f"{REPO}\n")
    assert result.exit_code != 0
    assert "exceed 10 GiB" in result.output
    assert "Continue" not in result.output
    assert not root.exists()


def test_prompted_destination_uses_same_click_directory_validation(monkeypatch, tmp_path):
    from chatstyle.input import resolve as resolver

    calls = fake_metadata(monkeypatch)
    monkeypatch.setattr(interactive_core, "is_interactive_available", lambda: True)
    file = tmp_path / "not-a-directory"
    file.write_text("existing")
    monkeypatch.setattr(resolver.prompt_runtime, "ask_path", lambda *args, **kwargs: str(file))
    monkeypatch.setattr(resolver.prompt_runtime, "ask_text", lambda message, default="", **kwargs: default)
    monkeypatch.setattr(resolver.prompt_runtime, "ask_confirm", lambda *args, **kwargs: False)
    result = CliRunner().invoke(main, ["download", REPO, "-i", "--repo-type", "model", "--revision", "main", "--endpoint", "https://hf-mirror.com", "--connections", "4", "--jobs", "5", "--include", "config.json", "--dry-run"])
    assert result.exit_code != 0
    assert "Destination" in result.output
    assert calls == []
    assert file.read_text() == "existing"


def test_invalid_interactive_connection_fails_without_network(monkeypatch):
    from chatstyle.input import resolve as resolver

    calls = fake_metadata(monkeypatch)
    monkeypatch.setattr(interactive_core, "is_interactive_available", lambda: True)
    monkeypatch.setattr(resolver.prompt_runtime, "ask_select", lambda *args: "model")
    monkeypatch.setattr(resolver.prompt_runtime, "ask_path", lambda *args, **kwargs: "")
    monkeypatch.setattr(resolver.prompt_runtime, "ask_text", lambda message, default="", password=False: "not-a-number" if message == "Connections per file" else default)
    monkeypatch.setattr(resolver.prompt_runtime, "ask_confirm", lambda *args, **kwargs: False)
    result = CliRunner().invoke(main, ["download", REPO, "-i", "--include", "config.json"])
    assert result.exit_code != 0
    assert "Connections" in result.output
    assert calls == []
