"""CLI entrypoint for chathfd."""

from __future__ import annotations

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
        # Root-only package for now: keep normal Click help behavior when no command is supplied.
        click.echo(ctx.get_help())


if __name__ == "__main__":
    main()
