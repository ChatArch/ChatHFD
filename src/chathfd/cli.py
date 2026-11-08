"""CLI entrypoint for chathfd."""

from __future__ import annotations

import os
from pathlib import Path

import click
from chatstyle import add_tree_option

from chathfd import __version__


@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name="chathfd")
@add_tree_option(renderer_options={"root_name": "chathfd"})
@click.pass_context
def main(ctx: click.Context) -> None:
    """chathfd command line interface."""
    if ctx.invoked_subcommand is None:
        # Show help on bare invocation while registered commands stay discoverable.
        click.echo(ctx.get_help())


@main.command()
@click.argument("repo_id")
@click.option("--repo-type", type=click.Choice(["model", "dataset"]), default="model", show_default=True)
@click.option("--revision", default="main", show_default=True, help="Branch, tag or commit.")
@click.option("--endpoint", default=lambda: os.environ.get("HF_ENDPOINT") or "https://hf-mirror.com", show_default="HF_ENDPOINT or https://hf-mirror.com", help="Hugging Face-compatible HTTPS origin.")
@click.option("--local-dir", type=click.Path(path_type=Path, file_okay=False), help="Destination (default: ./models or ./datasets / repo ID).")
@click.option("--include", multiple=True, help="Glob pattern to include (repeatable).")
@click.option("--exclude", multiple=True, help="Glob pattern to exclude (repeatable).")
@click.option("--connections", type=click.IntRange(1, 10), default=4, show_default=True, help="Connections per file for aria2c.")
@click.option("--jobs", type=click.IntRange(1, 10), default=5, show_default=True, help="Concurrent files for aria2c.")
@click.option("--dry-run", is_flag=True, help="List files and sizes without downloading.")
@click.option("--allow-large", is_flag=True, help="Allow a selection above 10 GiB.")
def download(
    repo_id: str, repo_type: str, revision: str, endpoint: str, local_dir: Path | None,
    include: tuple[str, ...], exclude: tuple[str, ...], connections: int, jobs: int,
    dry_run: bool, allow_large: bool,
) -> None:
    """Download a public model or dataset with aria2c."""
    from chathfd.download import download_repo

    download_repo(repo_id, repo_type, revision, endpoint, local_dir, include, exclude, connections, jobs, dry_run, allow_large)


@main.command()
@click.option("--install", is_flag=True, help="Install missing aria2c after confirmation.")
def setup(install: bool) -> None:
    """Check the aria2c download engine and offer installation."""
    from chathfd.setup import setup_aria2

    setup_aria2(install)


if __name__ == "__main__":
    main()
