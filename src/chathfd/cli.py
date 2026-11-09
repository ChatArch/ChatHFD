"""CLI entrypoint for chathfd."""

from __future__ import annotations

import os
from pathlib import Path

import click
from chatstyle import CommandField, CommandSchema, add_interactive_option, add_tree_option, ask_confirm, resolve_command_inputs

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


def _patterns(value: str | tuple[str, ...]) -> tuple[str, ...]:
    if isinstance(value, tuple):
        return value
    return tuple(part.strip() for part in value.split(",") if part.strip())


@main.command()
@click.argument("repo_id", required=False)
@click.option("--repo-type", type=click.Choice(["model", "dataset"]), default=None, show_default="model")
@click.option("--revision", default=None, show_default="main", help="Branch, tag or commit.")
@click.option("--endpoint", default=None, show_default="HF_ENDPOINT or https://hf-mirror.com", help="Hugging Face-compatible HTTPS origin.")
@click.option("--local-dir", type=click.Path(path_type=Path, file_okay=False), help="Exact final directory. Default: CHATHFD_DOWNLOAD_ROOT / repo ID; root from process env, ChatEnv profile or cwd.")
@click.option("--include", multiple=True, help="Glob pattern to include (repeatable).")
@click.option("--exclude", multiple=True, help="Glob pattern to exclude (repeatable).")
@click.option("--connections", type=click.IntRange(1, 10), default=None, show_default="4", help="Connections per file for aria2c.")
@click.option("--jobs", type=click.IntRange(1, 10), default=None, show_default="5", help="Concurrent files for aria2c.")
@click.option("--dry-run", is_flag=True, default=None, help="List files and sizes without downloading.")
@click.option("--allow-large", is_flag=True, default=None, help="Allow a selection above 10 GiB.")
@add_interactive_option
def download(
    repo_id: str | None, repo_type: str | None, revision: str | None, endpoint: str | None, local_dir: Path | None,
    include: tuple[str, ...], exclude: tuple[str, ...], connections: int | None, jobs: int | None,
    dry_run: bool | None, allow_large: bool | None, interactive: bool | None,
) -> None:
    """Download a public model or dataset with aria2c."""
    from chathfd.download import DEFAULT_ENDPOINT, _endpoint, download_repo, resolve_download_directory

    missing_repo = repo_id is None
    repo_id = resolve_command_inputs(
        schema=CommandSchema("download", (CommandField("repo_id", "Repository ID (owner/name)", required=True),)),
        provided={"repo_id": repo_id}, interactive=interactive,
        usage="Usage: chathfd download [REPO_ID] [OPTIONS] [-i|-I]",
    )["repo_id"]

    schema = CommandSchema("download", fields=(
        CommandField("repo_id", "Repository ID (owner/name)", required=True),
        CommandField("repo_type", "Repository type", kind="select", choices=("model", "dataset"), default="model", prompt_if_missing=interactive is True,
                     param_type=click.Choice(("model", "dataset"))),
        CommandField("revision", "Revision", default="main", prompt_if_missing=interactive is True),
        CommandField("endpoint", "HTTPS Hub endpoint", default_factory=lambda: _endpoint(os.environ.get("HF_ENDPOINT") or DEFAULT_ENDPOINT), prompt_if_missing=interactive is True),
        CommandField("local_dir", "Destination directory", kind="path", default_factory=lambda: resolve_download_directory(repo_id), prompt_if_missing=interactive is True,
                     param_type=click.Path(path_type=Path, file_okay=False)),
        CommandField("include", "Include globs (comma separated; empty for all)", normalizer=_patterns, prompt_if_missing=interactive is True),
        CommandField("exclude", "Exclude globs (comma separated; empty for none)", normalizer=_patterns, prompt_if_missing=interactive is True),
        CommandField("connections", "Connections per file", default=4, param_type=click.IntRange(1, 10), prompt_if_missing=interactive is True),
        CommandField("jobs", "Concurrent files", default=5, param_type=click.IntRange(1, 10), prompt_if_missing=interactive is True),
        CommandField("dry_run", "Preview only (no download)", kind="confirm", default=False, prompt_if_missing=interactive is True),
        CommandField("allow_large", "Permit selection above 10 GiB", kind="confirm", default=False, prompt_if_missing=interactive is True),
    ))
    values = resolve_command_inputs(
        schema=schema,
        provided={"repo_id": repo_id, "repo_type": repo_type, "revision": revision, "endpoint": endpoint,
                  "local_dir": local_dir, "include": include, "exclude": exclude,
                  "connections": connections, "jobs": jobs, "dry_run": dry_run, "allow_large": allow_large},
        interactive=interactive,
        usage="Usage: chathfd download [REPO_ID] [OPTIONS] [-i|-I]",
    )
    destination = Path(values["local_dir"]) if values["local_dir"] else None
    manual = interactive is True or (missing_repo and interactive is not False)
    confirm = (lambda files, total: ask_confirm(f"Download {files} files ({total} bytes)?", default=False)) if manual else None
    download_repo(
        values["repo_id"], values["repo_type"], values["revision"], values["endpoint"], destination,
        tuple(values["include"] or ()), tuple(values["exclude"] or ()), values["connections"], values["jobs"],
        values["dry_run"], values["allow_large"], confirm=confirm,
    )


@main.command()
@click.option("--install", is_flag=True, help="Install missing aria2c after confirmation.")
def setup(install: bool) -> None:
    """Check the aria2c download engine and offer installation."""
    from chathfd.setup import setup_aria2

    setup_aria2(install)


if __name__ == "__main__":
    main()
