from click.testing import CliRunner

from chathfd import __version__
from chathfd.cli import main


def test_help_mentions_tree_option():
    result = CliRunner().invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "--tree" in result.output


def test_version_option_reports_package_version():
    result = CliRunner().invoke(main, ["--version"])

    assert result.exit_code == 0
    assert f"chathfd, version {__version__}" in result.output


def test_tree_reports_registered_root_only_surface():
    result = CliRunner().invoke(main, ["--tree"])

    assert result.exit_code == 0
    assert result.output == (
        "chathfd  # ChatArch Hugging Face Download tooling entrypoint\n"
        "├── --help  # show command help\n"
        "├── --version  # show the installed package version\n"
        "└── --tree  # show this CLI tree\n"
    )
