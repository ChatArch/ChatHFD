"""ChatEnv-backed, invocation-time directory configuration for ChatHFD."""
from __future__ import annotations

import os
from pathlib import Path

import click
from chatenv import BaseEnvConfig, EnvField, EnvStore, get_paths


class ChathfdConfig(BaseEnvConfig):
    """ChatHFD configuration in its existing ChatEnv provider namespace."""

    _title = "ChatHFD Configuration"
    _aliases = ["chathfd"]
    _storage_dir = "Chathfd"

    CHATHFD_DOWNLOAD_ROOT = EnvField(
        "CHATHFD_DOWNLOAD_ROOT",
        default=".",
        desc="Download root; repository ID is appended. Default: invocation cwd.",
    )
    CHATHFD_API_KEY = EnvField(
        "CHATHFD_API_KEY",
        desc="Legacy scaffold field; not used for public repository downloads.",
        is_sensitive=True,
    )

    @classmethod
    def test(cls) -> None:
        """Validate the field already loaded by ChatEnv, including named profiles."""
        field = cls.CHATHFD_DOWNLOAD_ROOT
        root = _directory_path(field.value or field.default, field.env_key)
        print(f"Download root: {root}")
        print("Repository layout: <download-root>/<repo_id>; no directories created.")


def _directory_path(value: str | Path, label: str) -> Path:
    """Resolve a path without creating it; reject files and unsafe control text."""
    invalid = False
    path = None
    try:
        raw = os.fspath(value)
        if any(ord(char) < 32 or ord(char) == 127 for char in raw):
            invalid = True
        else:
            path = Path(raw or ".").expanduser().resolve()
            ancestor = path
            while not ancestor.exists() and ancestor.parent != ancestor:
                ancestor = ancestor.parent
            invalid = not ancestor.is_dir() or any(ord(char) < 32 or ord(char) == 127 for char in str(path))
    except (OSError, RuntimeError, ValueError, TypeError):
        invalid = True
    if invalid or path is None:
        raise click.ClickException(f"{label} must be a usable directory path without control characters")
    return path


def resolve_download_root() -> Path:
    """Read process env > active ChatEnv profile > cwd, with no storage writes."""
    field = ChathfdConfig.CHATHFD_DOWNLOAD_ROOT
    value = os.environ.get(field.env_key)
    if value is None:
        values = EnvStore(get_paths().envs_dir).load_active(ChathfdConfig)
        value = values.get(field.env_key, field.default)
    return _directory_path(value or field.default, field.env_key)


__all__ = ["ChathfdConfig", "resolve_download_root"]
