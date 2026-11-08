"""Setup is read-only unless installation is explicitly requested and confirmed."""

from click.testing import CliRunner

from chathfd.cli import main


def test_setup_reports_existing_engine(monkeypatch):
    from chathfd import setup

    monkeypatch.setattr(setup.shutil, "which", lambda name: "/usr/bin/aria2c" if name == "aria2c" else None)
    result = CliRunner().invoke(main, ["setup"])
    assert result.exit_code == 0
    assert "aria2c ready" in result.output


def test_missing_engine_offers_command_without_installing(monkeypatch):
    from chathfd import setup

    monkeypatch.setattr(setup.shutil, "which", lambda name: "/usr/bin/apt-get" if name == "apt-get" else None)
    monkeypatch.setattr(setup.os, "geteuid", lambda: 0)
    monkeypatch.setattr(setup.subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("must not install")))
    result = CliRunner().invoke(main, ["setup"])
    assert result.exit_code == 0
    assert "apt-get install -y aria2" in result.output
    assert "--install" in result.output


def test_install_declined_never_invokes_package_manager(monkeypatch):
    from chathfd import setup

    monkeypatch.setattr(setup.shutil, "which", lambda name: "/usr/bin/apt-get" if name == "apt-get" else None)
    monkeypatch.setattr(setup.os, "geteuid", lambda: 0)
    monkeypatch.setattr(setup.subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("must not install")))
    result = CliRunner().invoke(main, ["setup", "--install"], input="n\n")
    assert result.exit_code == 0
    assert "cancelled" in result.output


def test_install_confirmed_uses_argv_not_shell(monkeypatch):
    from chathfd import setup

    seen = []
    installed = []

    def which(name):
        if name == "aria2c":
            return "/usr/bin/aria2c" if installed else None
        return "/usr/bin/apt-get" if name == "apt-get" else None

    def run(command, check):
        seen.append((command, check))
        installed.append(True)

    monkeypatch.setattr(setup.shutil, "which", which)
    monkeypatch.setattr(setup.os, "geteuid", lambda: 0)
    monkeypatch.setattr(setup.subprocess, "run", run)
    result = CliRunner().invoke(main, ["setup", "--install"], input="y\n")
    assert result.exit_code == 0, result.output
    assert seen == [(["apt-get", "install", "-y", "aria2"], True)]
    assert "aria2c ready" in result.output


def test_install_noninteractive_without_confirmation_fails_closed(monkeypatch):
    from chathfd import setup

    monkeypatch.setattr(setup.shutil, "which", lambda name: "/usr/bin/apt-get" if name == "apt-get" else None)
    monkeypatch.setattr(setup.os, "geteuid", lambda: 0)
    monkeypatch.setattr(setup.subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("must not install")))
    result = CliRunner().invoke(main, ["setup", "--install"], input="")
    assert result.exit_code != 0
