# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,duplicate-code,too-many-locals
import unittest
from jira.exceptions import JIRAError
from requests.exceptions import ConnectionError as RequestsConnectionError
from jirabatch import create_jira_issues


class TestConstructor(unittest.TestCase):

    def test_constructor_with_inexisting_conf_file(self):
        with self.assertRaises(FileNotFoundError):
            create_jira_issues(
                "examples/inexisting-jirabatch.yaml", "examples/issues.yaml", 50
            )

    def test_constructor_with_inexisting_issues_file(self):
        with self.assertRaises(FileNotFoundError):
            create_jira_issues(
                "examples/jirabatch.yaml", "examples/inexisting-issues.yaml", 50
            )

    def test_constructor_with_unreachable_jira(self):
        with self.assertRaises((RequestsConnectionError, JIRAError)):
            create_jira_issues("examples/jirabatch.yaml", "examples/issues.yaml", 50)
