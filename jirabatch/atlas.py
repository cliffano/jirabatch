# pylint: disable=too-many-locals,too-few-public-methods,too-many-branches
"""This module contains the Atlas class."""

import json

from jira import JIRA
from jira.exceptions import JIRAError
from jira.utils import json_loads
from .logger import init


class Atlas:
    """This class represents an Atlassian Jira manager."""

    def __init__(self, conf: dict) -> None:
        """Initialize Atlas."""

        self.logger = init()
        self.jira = JIRA(
            server=conf["url"],
            basic_auth=(conf["user"], conf.get("api_token", conf.get("password"))),
        )

    def _bulk_create_issues(self, field_list: list[dict]) -> list[dict]:
        """Create issues via the Jira bulk API, capturing full error details.

        Unlike ``JIRA.create_issues``, this method also captures
        ``errorMessages`` from the API response, not just field-level
        ``errors``.

        Args:
            field_list: A list of Jira field dicts, one per issue.

        Returns:
            A list of result dicts with keys ``status``, ``issue``,
            ``error``, ``error_messages``, and ``input_fields``.
        """
        data = {"issueUpdates": [{"fields": fields} for fields in field_list]}

        url = self.jira._get_url("issue/bulk")  # pylint: disable=protected-access
        try:
            r = self.jira._session.post(  # pylint: disable=protected-access
                url, data=json.dumps(data)
            )
            raw = json_loads(r)
        except JIRAError as je:
            if je.status_code == 400 and je.response is not None:
                raw = json.loads(je.response.text)
            else:
                raise

        errors = {}
        for error in raw.get("errors", []):
            element_errors = error.get("elementErrors", {})
            errors[error["failedElementNumber"]] = {
                "errors": element_errors.get("errors", {}),
                "errorMessages": element_errors.get("errorMessages", []),
            }

        issue_list = []
        issues_queue = list(raw.get("issues", []))
        for index, fields in enumerate(field_list):
            if index in errors:
                issue_list.append(
                    {
                        "status": "Error",
                        "error": errors[index]["errors"],
                        "error_messages": errors[index]["errorMessages"],
                        "issue": None,
                        "input_fields": fields,
                    }
                )
            else:
                issue_raw = issues_queue.pop(0)
                issue = self.jira.issue(issue_raw["key"])
                issue_list.append(
                    {
                        "status": "Success",
                        "issue": issue,
                        "error": None,
                        "error_messages": [],
                        "input_fields": fields,
                    }
                )
        return issue_list

    def create_jira_issues(self, issues: dict, batch_size: int) -> None:
        """Create Jira issues in batches from a dictionary configuration.

        Iterates through the provided issues dictionary, builds the field
        definitions for each issue, and creates them in batches using the
        Jira bulk creation API. Each batch is limited to
        ``batch_size`` issues to respect the Jira REST API limit.

        Args:
            issues: A dictionary containing issue configurations. Expected
                structure::

                    {
                        "issues": [
                            {
                                "project": str,
                                "summary": str,
                                "issuetype": str,
                                ...
                            }
                        ]
                    }

            batch_size: Maximum number of issues to create per API call.
        """

        default_fields = issues.get("defaults", {})
        issues_fields = issues.get("issues", [])

        merged_fields = []
        subtask_map = {}
        for index, issue_fields in enumerate(issues_fields):
            combined = {**default_fields, **issue_fields}
            subtasks = combined.pop("subtasks", None)
            merged_fields.append(self._merge_jira_fields(combined))
            if subtasks:
                subtask_map[index] = subtasks

        pending_subtasks = []

        for batch_start in range(0, len(merged_fields), batch_size):

            batch = merged_fields[batch_start : batch_start + batch_size]
            self.logger.info(f"Processing a batch of {len(batch)} issue(s)...")

            results = self._bulk_create_issues(field_list=batch)

            for batch_index, result in enumerate(results):
                absolute_index = batch_start + batch_index
                self.logger.debug(f"Result: {result}")
                if result["status"] == "Success":
                    created_issue = result["issue"]
                    self.logger.info(
                        "Created issue %s: %s",
                        created_issue.key,
                        created_issue.fields.summary,
                    )
                    self.logger.debug(
                        "Issue %s fields: %s", created_issue.key, result["input_fields"]
                    )
                    if absolute_index in subtask_map:
                        for subtask in subtask_map[absolute_index]:
                            subtask_fields = {**default_fields, **subtask}
                            subtask_fields["issuetype"] = subtask_fields.get(
                                "issuetype", "Subtask"
                            )
                            subtask_fields["parent"] = created_issue.key
                            subtask_fields.pop("subtasks", None)
                            pending_subtasks.append(
                                self._merge_jira_fields(subtask_fields)
                            )
                else:
                    errors_str = self._format_errors(result)
                    fields_str = "\n".join(
                        f"    {key}: {value}"
                        for key, value in result["input_fields"].items()
                    )
                    self.logger.error(
                        "Failed to create issue:\nErrors:\n%s\nFields:\n%s",
                        errors_str,
                        fields_str,
                    )

        if pending_subtasks:
            self.logger.info(f"Creating {len(pending_subtasks)} subtask(s)...")
            for batch_start in range(0, len(pending_subtasks), batch_size):
                batch = pending_subtasks[batch_start : batch_start + batch_size]
                self.logger.info(f"Processing a batch of {len(batch)} subtask(s)...")
                results = self._bulk_create_issues(field_list=batch)
                for result in results:
                    self.logger.debug(f"Result: {result}")
                    if result["status"] == "Success":
                        created_issue = result["issue"]
                        self.logger.info(
                            "Created subtask %s: %s",
                            created_issue.key,
                            created_issue.fields.summary,
                        )
                    else:
                        errors_str = self._format_errors(result)
                        fields_str = "\n".join(
                            f"    {key}: {value}"
                            for key, value in result["input_fields"].items()
                        )
                        self.logger.error(
                            "Failed to create subtask:\nErrors:\n%s\nFields:\n%s",
                            errors_str,
                            fields_str,
                        )

    @staticmethod
    def _format_errors(result: dict) -> str:
        """Format error details from a bulk create result into a readable string.

        Args:
            result: A result dict from ``_bulk_create_issues``.

        Returns:
            A formatted error string.
        """
        lines = []
        error = result.get("error", {})
        if error:
            for field, msg in error.items():
                lines.append(f"    {field}: {msg}")
        for msg in result.get("error_messages", []):
            lines.append(f"    {msg}")
        if not lines:
            lines.append("    (no error details returned by Jira)")
        return "\n".join(lines)

    @staticmethod
    def _merge_jira_fields(issue: dict) -> dict:
        """Build a Jira-compatible issue fields dictionary from an issue definition.

        Args:
            issue: A dictionary describing a single issue with keys such as
                ``project``, ``summary``, ``issuetype``, and optional metadata.

        Returns:
            A dictionary of fields ready to be passed to the Jira API.
        """

        fields = {
            "project": {"key": issue["project"]},
            "issuetype": {"name": issue["issuetype"]},
            "summary": issue["summary"],
            "description": issue.get("description"),
        }

        if "reporter" in issue:
            fields["reporter"] = {"accountId": issue["reporter"]}

        if "assignee" in issue:
            fields["assignee"] = {"accountId": issue["assignee"]}

        if "priority" in issue:
            fields["priority"] = {"name": str(issue["priority"])}

        if "labels" in issue:
            fields["labels"] = issue["labels"]

        if "components" in issue:
            fields["components"] = [
                {"name": component} for component in issue["components"]
            ]

        if "versions" in issue:
            fields["versions"] = [{"name": version} for version in issue["versions"]]

        if "fixVersions" in issue:
            fields["fixVersions"] = [
                {"name": version} for version in issue["fixVersions"]
            ]

        if "environment" in issue:
            fields["environment"] = issue["environment"]

        if "dueDate" in issue:
            fields["duedate"] = str(issue["dueDate"])

        if "timetracking" in issue:
            fields["timetracking"] = issue["timetracking"]

        if "security" in issue:
            fields["security"] = {"name": issue["security"]}

        if "parent" in issue:
            fields["parent"] = {"key": issue["parent"]}

        if "epic" in issue:
            # parent is used when team managed, epic is used when company managed
            fields["parent"] = {"key": issue["epic"]}

        if "customFields" in issue:
            fields.update(issue["customFields"])

        return fields
