import click
from click.testing import CliRunner

from chathfd import __version__
from chathfd.cli import main


EXPECTED_ROOT_TREE = (
    "chathfd\n"
    "├── --help  # Show this message and exit.\n"
    "├── --version  # Show the version and exit.\n"
    "├── --tree  # Print the registered CLI tree and exit.\n"
    "└── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.\n"
)


def test_help_mentions_tree_options():
    result = CliRunner().invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "--tree" in result.output
    assert "--tree-brief" in result.output


def test_version_option_reports_package_version():
    result = CliRunner().invoke(main, ["--version"])

    assert result.exit_code == 0
    assert f"chathfd, version {__version__}" in result.output


def test_tree_reports_registered_root_only_surface():
    result = CliRunner().invoke(main, ["--tree"])

    assert result.exit_code == 0
    assert result.output == EXPECTED_ROOT_TREE


def test_tree_brief_reports_registered_root_only_surface():
    result = CliRunner().invoke(main, ["--tree-brief"])

    assert result.exit_code == 0
    assert result.output == EXPECTED_ROOT_TREE


def test_tree_modes_include_and_omit_command_parameter_signatures():
    @click.command("download")
    @click.argument("repo_id")
    @click.option("--revision", help="Repository revision.")
    def download(repo_id: str, revision: str | None) -> None:
        """Download a repository."""

    main.add_command(download)
    try:
        detailed = CliRunner().invoke(main, ["--tree"])
        brief = CliRunner().invoke(main, ["--tree-brief"])
    finally:
        main.commands.pop("download")

    assert detailed.exit_code == 0
    assert "download <REPO-ID> [--revision REVISION]  # Download a repository." in detailed.output
    assert brief.exit_code == 0
    assert "download  # Download a repository." in brief.output
    assert "<REPO-ID>" not in brief.output
    assert "[--revision REVISION]" not in brief.output
