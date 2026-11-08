"""Guided installation for the external aria2 download engine."""

from __future__ import annotations

import os
import shutil
import subprocess

import click
from chatstyle import ask_confirm


def _install_command() -> list[str] | None:
    if shutil.which("brew"):
        return ["brew", "install", "aria2"]
    for manager, args in (
        ("apt-get", ["install", "-y", "aria2"]),
        ("dnf", ["install", "-y", "aria2"]),
        ("pacman", ["-S", "--noconfirm", "aria2"]),
    ):
        if shutil.which(manager):
            command = [manager, *args]
            return command if os.geteuid() == 0 else ["sudo", "-n", *command]
    return None


def setup_aria2(install: bool) -> None:
    path = shutil.which("aria2c")
    if path:
        click.echo(f"aria2c ready: {path}")
        return
    click.echo("aria2c is not installed; ChatHFD requires it for concurrent downloads.")
    command = _install_command()
    if not command:
        raise click.ClickException("No supported package manager found; install aria2 via your OS package manager")
    manual = " ".join(part for part in command if part != "-n")
    if not install:
        click.echo(f"Suggested command: {manual}")
        click.echo("Run chathfd setup --install to attempt installation with confirmation.")
        return
    if not ask_confirm(f"Run {manual}? This changes system packages", default=False):
        click.echo("Installation cancelled")
        return
    try:
        subprocess.run(command, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise click.ClickException(f"Installation failed ({type(exc).__name__}); run {manual} interactively if authorization is needed") from exc
    if not shutil.which("aria2c"):
        raise click.ClickException("Installer completed but aria2c is not on PATH; check your shell environment")
    click.echo(f"aria2c ready: {shutil.which('aria2c')}")
