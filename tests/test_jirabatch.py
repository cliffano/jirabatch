# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,duplicate-code,too-many-locals
from unittest.mock import patch, call
import unittest.mock
import unittest
from click.testing import CliRunner

from jirabatch import create_jira_issues
from jirabatch import cli


class TestJiraBatch(unittest.TestCase):
    """Test jirabatch module."""

    def test_cli_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Usage: cli [OPTIONS]", result.output)
        self.assertIn("--conf-file TEXT", result.output)
        self.assertIn("--issues-file TEXT", result.output)
        self.assertIn("--batch-size INTEGER", result.output)
        self.assertIn("Show this message and exit.", result.output)

    @patch("jirabatch.Atlas")
    @patch("jirabatch.CFGRW")
    @patch("jirabatch.init")
    def test_create_jira_issues(
        self, func_init, func_cfgrw, func_atlas
    ):  # pylint: disable=too-many-arguments
        mock_logger = unittest.mock.Mock()
        mock_conf_cfgrw = unittest.mock.Mock()
        mock_issues_cfgrw = unittest.mock.Mock()
        mock_atlas = unittest.mock.Mock()

        conf = {
            "url": "https://someuser.atlassian.net",
            "user": "someuser",
            "api_token": "someapitoken",
        }
        issues = {
            "defaults": {"project": "SOME", "issuetype": "Task"},
            "issues": [{"summary": "Some summary"}],
        }

        func_init.return_value = mock_logger
        func_cfgrw.side_effect = [mock_conf_cfgrw, mock_issues_cfgrw]
        mock_conf_cfgrw.read.return_value = conf
        mock_issues_cfgrw.read.return_value = issues
        func_atlas.return_value = mock_atlas

        create_jira_issues(
            conf_file="jirabatch.yaml", issues_file="issues.yaml", batch_size=25
        )

        mock_logger.info.assert_has_calls(
            [
                call("Loading configuration file jirabatch.yaml"),
                call("Loading issues file issues.yaml"),
            ]
        )
        func_cfgrw.assert_has_calls(
            [call(conf_file="jirabatch.yaml"), call(conf_file="issues.yaml")]
        )
        mock_conf_cfgrw.read.assert_called_once_with(["url", "user", "api_token"])
        mock_issues_cfgrw.read.assert_called_once_with(["defaults", "issues"])
        func_atlas.assert_called_once_with(conf=conf)
        mock_atlas.create_jira_issues.assert_called_once_with(
            issues=issues, batch_size=25
        )

    @patch("jirabatch.create_jira_issues")
    def test_cli(self, func_create_jira_issues):
        func_create_jira_issues.return_value = None

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--conf-file",
                "jirabatch.yaml",
                "--issues-file",
                "issues.yaml",
                "--batch-size",
                "25",
            ],
        )

        assert not result.exception
        assert result.exit_code == 0
        assert result.output == ""

        func_create_jira_issues.assert_called_once_with(
            "jirabatch.yaml", "issues.yaml", 25
        )
