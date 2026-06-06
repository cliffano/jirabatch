# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,duplicate-code,too-many-locals
import unittest
from unittest.mock import patch
from click.testing import CliRunner
from jirabatch import cli


class TestCli(unittest.TestCase):

    def test_cli_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Usage: cli [OPTIONS]", result.output)
        self.assertIn("Show this message and exit.", result.output)

    def test_cli_with_invalid_arg(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--some-invalid-arg"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("No such option", result.output)
        self.assertIn("--some-invalid-arg", result.output)

    @patch("jirabatch.create_jira_issues")
    def test_cli_with_default_args(self, func_create_jira_issues):
        runner = CliRunner()
        result = runner.invoke(cli, [])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "")
        func_create_jira_issues.assert_called_once_with(
            "jirabatch.yaml", "issues.yaml", 50
        )

    @patch("jirabatch.create_jira_issues")
    def test_cli_with_explicit_args(self, func_create_jira_issues):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--conf-file",
                "some-jirabatch.yaml",
                "--issues-file",
                "some-issues.yaml",
                "--batch-size",
                "20",
            ],
        )

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "")
        func_create_jira_issues.assert_called_once_with(
            "some-jirabatch.yaml", "some-issues.yaml", 20
        )
