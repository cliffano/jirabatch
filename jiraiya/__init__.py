# pylint: disable=too-many-locals
"""
jiraiya
&#x3D;&#x3D;&#x3D;&#x3D;&#x3D;&#x3D;&#x3D;
... .
"""
import click
from cfgrw import CFGRW
from .atlas import Atlas
from .logger import init


def create_jira_issues(conf_file: str, issues_file: str, batch_size: int) -> None:
    """Create Jira issues."""

    logger = init()

    logger.info(f"Loading configuration file {conf_file}")
    conf_cfgrw = CFGRW(conf_file=conf_file)
    conf = conf_cfgrw.read(["url", "user", "api_token"])

    logger.info(f"Loading issues file {issues_file}")
    issues_cfgrw = CFGRW(conf_file=issues_file)
    issues = issues_cfgrw.read(["defaults", "issues"])

    atlas = Atlas(conf=conf)
    atlas.create_jira_issues(issues=issues, batch_size=batch_size)


@click.command()
@click.option(
    "--conf-file",
    default="jiraiya.yaml",
    show_default=True,
    type=str,
    help="Configuration file path",
)
@click.option(
    "--issues-file",
    default="issues.yaml",
    show_default=True,
    type=str,
    help="Issues file path",
)
@click.option(
    "--batch-size",
    default=50,
    show_default=True,
    type=int,
    help="Maximum number of issues to be created in a single batch",
)
@click.version_option(package_name="jiraiya", prog_name="jiraiya")
def cli(conf_file: str, issues_file: str, batch_size: int) -> None:
    """Create multiple Jira issues.
    Issue details are defined in the issues file,
    while the Jira settings are defined in the config file.
    """
    create_jira_issues(conf_file, issues_file, batch_size)
