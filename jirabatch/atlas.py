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
        """Initialize Atlas with a Jira connection.

        Connects to the Jira server specified in ``conf`` using basic authentication.
        ``api_token`` is used as the credential when available, falling back to ``password``.

        Args:
            conf: A configuration dictionary with the following keys:

                - ``url``: The base URL of the Jira server.
                - ``user``: The Jira username or email address.
                - ``api_token``: The Jira API token (preferred).
                                 Falls back to ``password`` if absent.
        """

        self.logger = init()
        self.jira = JIRA(
            server=conf["url"],
            basic_auth=(conf["user"], conf.get("api_token", conf.get("password"))),
        )

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

        # Get configured fields from issues file
        default_fields = issues.get("defaults", {})
        issues_fields = issues.get("issues", [])

        # Construct a list of Jira field dicts for each issue, merging with defaults and
        # extracting subtasks into a separate map to be processed after parent issues are created
        jira_fields_list = []
        subtask_map = {}
        for index, issue_fields in enumerate(issues_fields):
            combined_fields = {**default_fields, **issue_fields}
            subtasks = combined_fields.pop("subtasks", None)
            jira_fields_list.append(self._prepare_jira_fields(combined_fields))
            if subtasks:
                subtask_map[index] = subtasks

        # Placeholder for any pending subtasks to be created
        # after their parent issues are successfully created
        pending_subtasks = []

        for batch_start in range(0, len(jira_fields_list), batch_size):

            batch = jira_fields_list[batch_start : batch_start + batch_size]
            self.logger.info(f"Processing a batch of {len(batch)} issue(s)...")

            api_results_list = self._bulk_create_issues(field_list=batch)

            for batch_index, api_result in enumerate(api_results_list):
                absolute_index = batch_start + batch_index
                self.logger.debug(f"Result: {api_result}")
                if api_result["status"] != "Success":
                    self._log_issue_creation_failure(api_result)
                    continue

                created_issue = api_result["issue"]
                self.logger.info(
                    "Created issue %s: %s",
                    created_issue.key,
                    created_issue.fields.summary,
                )
                self.logger.debug(
                    "Issue %s fields: %s",
                    created_issue.key,
                    api_result["input_fields"],
                )

                pending_subtasks.extend(
                    self._prepare_pending_subtasks(
                        subtasks=subtask_map.get(absolute_index, []),
                        default_fields=default_fields,
                        issue_fields=issues_fields[absolute_index],
                        parent_issue_key=created_issue.key,
                    )
                )

        # Create any pending subtasks after all parent issues have been processed,
        # so that subtasks of successfully created parent issues can be created while
        # subtasks of failed parent issues are not attempted
        if pending_subtasks:
            self.logger.info(f"Creating {len(pending_subtasks)} subtask(s)...")
            for batch_start in range(0, len(pending_subtasks), batch_size):
                batch = pending_subtasks[batch_start : batch_start + batch_size]
                self.logger.info(f"Processing a batch of {len(batch)} subtask(s)...")
                api_results_list = self._bulk_create_issues(field_list=batch)
                for api_result in api_results_list:
                    self.logger.debug(f"Result: {api_result}")
                    if api_result["status"] == "Success":
                        created_issue = api_result["issue"]
                        self.logger.info(
                            "Created subtask %s: %s",
                            created_issue.key,
                            created_issue.fields.summary,
                        )
                    else:
                        errors_str = self._format_errors(api_result)
                        fields_str = "\n".join(
                            f"- {key}: {value}"
                            for key, value in api_result["input_fields"].items()
                        )
                        self.logger.error(
                            "Failed to create subtask:\nErrors:\n%s\nFields:\n%s",
                            errors_str,
                            fields_str,
                        )

    def _log_issue_creation_failure(self, api_result: dict) -> None:
        """Log issue creation failure details from a bulk API result."""

        errors_str = self._format_errors(api_result)
        fields_str = "\n".join(
            f"    {key}: {value}" for key, value in api_result["input_fields"].items()
        )
        self.logger.error(
            "Failed to create issue:\nErrors:\n%s\nFields:\n%s",
            errors_str,
            fields_str,
        )

    def _prepare_pending_subtasks(
        self,
        subtasks: list,
        default_fields: dict,
        issue_fields: dict,
        parent_issue_key: str,
    ) -> list[dict]:
        """Prepare Jira field dicts for subtasks of a successfully created issue."""

        if not subtasks:
            return []

        prepared_subtasks = []
        for subtask in subtasks:
            subtask_fields = {**default_fields, **subtask}

            # Subtasks often omit project in YAML examples; inherit from
            # the parent issue/defaults if none supplied in the subtask itself.
            if "project" not in subtask_fields:
                parent_project = issue_fields.get(
                    "project", default_fields.get("project")
                )
                if parent_project:
                    subtask_fields["project"] = parent_project

            subtask_fields["issuetype"] = subtask_fields.get("issuetype", "Subtask")
            subtask_fields["parent"] = parent_issue_key
            subtask_fields.pop("subtasks", None)
            prepared_subtasks.append(self._prepare_jira_fields(subtask_fields))

        return prepared_subtasks

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

        # Make API request to create issues in bulk, capturing
        # both field-level errors and general error messages
        api_request_payload = {
            "issueUpdates": [{"fields": fields} for fields in field_list]
        }
        url = self.jira._get_url("issue/bulk")  # pylint: disable=protected-access
        try:
            raw_api_response = (
                self.jira._session.post(  # pylint: disable=protected-access
                    url, data=json.dumps(api_request_payload)
                )
            )
            api_response = json_loads(raw_api_response)
        except JIRAError as je:
            if je.status_code == 400 and je.response is not None:
                api_response = json.loads(je.response.text)
            else:
                raise
        errors = {}
        for error in api_response.get("errors", []):
            element_errors = error.get("elementErrors", {})
            errors[error["failedElementNumber"]] = {
                "errors": element_errors.get("errors", {}),
                "errorMessages": element_errors.get("errorMessages", []),
            }

        # Build result list by pairing each input field with
        # - (Success result) its created issue
        # - (Error result) its error details
        api_results_list = []
        issues_queue = list(api_response.get("issues", []))
        for index, fields in enumerate(field_list):
            # Construct Error result
            if index in errors:
                api_results_list.append(
                    {
                        "status": "Error",
                        "error": errors[index]["errors"],
                        "error_messages": errors[index]["errorMessages"],
                        "issue": None,
                        "input_fields": fields,
                    }
                )
            # Construct Success result
            else:
                issue_raw = issues_queue.pop(0)
                issue = self.jira.issue(issue_raw["key"])
                api_results_list.append(
                    {
                        "status": "Success",
                        "issue": issue,
                        "error": None,
                        "error_messages": [],
                        "input_fields": fields,
                    }
                )
        return api_results_list

    @staticmethod
    def _format_errors(api_result: dict) -> str:
        """Format error details from a bulk create result into a readable string.

        Args:
            api_result: A result dict from ``_bulk_create_issues``.

        Returns:
            A formatted error string.
        """
        lines = []

        # Format error details from "error" field
        error = api_result.get("error", {})
        if error:
            for field, msg in error.items():
                lines.append(f"- {field}: {msg}")

        # Format error details from "error_messages" field
        for msg in api_result.get("error_messages", []):
            lines.append(f"- {msg}")

        # Add placeholder message when API result doesn't contain error-related field
        if not lines:
            lines.append("(no error details returned by Jira)")

        return "\n".join(lines)

    @staticmethod
    def _prepare_jira_fields(config_fields: dict) -> dict:
        """Build a Jira-compatible issue fields dictionary from an issue configuration.

        Args:
            config_fields: A dictionary describing a single issue with keys such as
                ``project``, ``summary``, ``issuetype``, and optional metadata.

        Returns:
            A dictionary of fields ready to be passed to the Jira API.
        """

        # Initialise Jira fields with required fields and common optional fields
        jira_fields = {
            "project": {"key": config_fields["project"]},
            "issuetype": {"name": config_fields["issuetype"]},
            "summary": config_fields["summary"],
            "description": config_fields.get("description"),
        }

        # Add optional fields with AS-IS value
        for field_name in ["labels", "environment", "timetracking"]:
            if field_name in config_fields:
                jira_fields[field_name] = config_fields[field_name]

        # Add optional fields with stringified formatting
        for field_name in ["duedate"]:
            if field_name in config_fields:
                jira_fields[field_name] = str(config_fields[field_name])

        # Add optional fields that require nested formatting with "accountId" key
        for field_name in ["reporter", "assignee"]:
            if field_name in config_fields:
                jira_fields[field_name] = {"accountId": config_fields[field_name]}

        # Add optional parent reference with nested formatting using "key".
        # `epic` is normalized to `parent` so downstream payload handling is consistent.
        if "parent" in config_fields:
            jira_fields["parent"] = {"key": config_fields["parent"]}
        elif "epic" in config_fields:
            jira_fields["parent"] = {"key": config_fields["epic"]}

        # Add optional fields that require nested formatting with "name" key and AS-IS value
        for field_name in ["security"]:
            if field_name in config_fields:
                jira_fields[field_name] = {"name": config_fields[field_name]}

        # Add optional fields that require nested formatting with "name" key and stringified value
        for field_name in ["priority"]:
            if field_name in config_fields:
                jira_fields[field_name] = {"name": str(config_fields[field_name])}

        # Add optional fields with a list of values that require nested formatting with "name" key
        for field_name in ["components", "versions", "fixVersions"]:
            if field_name in config_fields:
                jira_fields[field_name] = [
                    {"name": field_value} for field_value in config_fields[field_name]
                ]

        # Add any custom fields defined in the issue, which may have arbitrary formatting
        if "customFields" in config_fields:
            jira_fields.update(config_fields["customFields"])

        return jira_fields
