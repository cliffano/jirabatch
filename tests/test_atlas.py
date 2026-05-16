# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,protected-access
import json
import unittest
from unittest.mock import MagicMock, patch

from jirabatch.atlas import Atlas


class TestPrepareJiraFields(unittest.TestCase):
    """Tests for Atlas._prepare_jira_fields static method."""

    def test_required_fields_only(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "Minimal task",
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields == {
            "project": {"key": "ENG"},
            "issuetype": {"name": "Task"},
            "summary": "Minimal task",
            "description": None,
        }

    def test_description(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "A task",
            "description": "Some details",
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["description"] == "Some details"

    def test_reporter(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "A task",
            "reporter": "tech-lead-account-id",
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["reporter"] == {"accountId": "tech-lead-account-id"}

    def test_assignee(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "A task",
            "assignee": "cliffano-account-id",
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["assignee"] == {"accountId": "cliffano-account-id"}

    def test_priority(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "A task",
            "priority": "High",
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["priority"] == {"name": "High"}

    def test_labels(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "A task",
            "labels": ["infra", "aws"],
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["labels"] == ["infra", "aws"]

    def test_components(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "A task",
            "components": ["Cloud", "Backend"],
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["components"] == [{"name": "Cloud"}, {"name": "Backend"}]

    def test_versions(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "A task",
            "versions": ["2025.4"],
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["versions"] == [{"name": "2025.4"}]

    def test_fix_versions(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "A task",
            "fixVersions": ["2026.1", "2026.2"],
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["fixVersions"] == [{"name": "2026.1"}, {"name": "2026.2"}]

    def test_environment(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "A task",
            "environment": "Production AWS us-east-1",
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["environment"] == "Production AWS us-east-1"

    def test_due_date(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "A task",
            "duedate": "2026-04-01",
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["duedate"] == "2026-04-01"

    def test_timetracking(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "A task",
            "timetracking": {
                "originalEstimate": "3d",
                "remainingEstimate": "3d",
            },
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["timetracking"] == {
            "originalEstimate": "3d",
            "remainingEstimate": "3d",
        }

    def test_security(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "A task",
            "security": "Confidential",
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["security"] == {"name": "Confidential"}

    def test_parent(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Sub-task",
            "summary": "A sub-task",
            "parent": "ENG-100",
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["parent"] == {"key": "ENG-100"}

    def test_epic(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Story",
            "summary": "A story under an epic",
            "epic": "ENG-10",
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["parent"] == {"key": "ENG-10"}

    def test_custom_fields_team_and_sprint(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "A task",
            "customFields": {
                "customfield_10100": "Platform Team",
                "customfield_10200": "Sprint 42",
            },
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["customfield_10100"] == "Platform Team"
        assert jira_fields["customfield_10200"] == "Sprint 42"

    def test_custom_fields_do_not_overwrite_standard_fields(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "A task",
            "priority": "High",
            "customFields": {
                "customfield_10100": "Security Team",
            },
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["priority"] == {"name": "High"}
        assert jira_fields["customfield_10100"] == "Security Team"

    def test_all_fields_together(self):
        config_fields = {
            "project": "ENG",
            "issuetype": "Task",
            "summary": "Full task",
            "description": "All fields set",
            "reporter": "tech-lead-account-id",
            "assignee": "cliffano-account-id",
            "priority": "High",
            "labels": ["infra"],
            "components": ["Cloud"],
            "versions": ["2025.4"],
            "fixVersions": ["2026.1"],
            "environment": "Production",
            "duedate": "2026-04-01",
            "timetracking": {"originalEstimate": "5d"},
            "security": "Internal",
            "parent": "ENG-50",
            "customFields": {
                "customfield_10100": "Platform Team",
                "customfield_10200": "Sprint 42",
            },
        }
        jira_fields = Atlas._prepare_jira_fields(config_fields)
        assert jira_fields["project"] == {"key": "ENG"}
        assert jira_fields["issuetype"] == {"name": "Task"}
        assert jira_fields["summary"] == "Full task"
        assert jira_fields["description"] == "All fields set"
        assert jira_fields["reporter"] == {"accountId": "tech-lead-account-id"}
        assert jira_fields["assignee"] == {"accountId": "cliffano-account-id"}
        assert jira_fields["priority"] == {"name": "High"}
        assert jira_fields["labels"] == ["infra"]
        assert jira_fields["components"] == [{"name": "Cloud"}]
        assert jira_fields["versions"] == [{"name": "2025.4"}]
        assert jira_fields["fixVersions"] == [{"name": "2026.1"}]
        assert jira_fields["environment"] == "Production"
        assert jira_fields["duedate"] == "2026-04-01"
        assert jira_fields["timetracking"] == {"originalEstimate": "5d"}
        assert jira_fields["security"] == {"name": "Internal"}
        assert jira_fields["parent"] == {"key": "ENG-50"}
        assert jira_fields["customfield_10100"] == "Platform Team"
        assert jira_fields["customfield_10200"] == "Sprint 42"


class TestCreateJiraIssues(unittest.TestCase):
    """Tests for Atlas.create_jira_issues method."""

    @patch("jirabatch.atlas.JIRA")
    @patch("jirabatch.atlas.init")
    def test_single_issue_success(self, mock_init, mock_jira_cls):
        mock_logger = MagicMock()
        mock_init.return_value = mock_logger

        mock_created = MagicMock()
        mock_created.key = "ENG-1"
        mock_created.fields.summary = "A task"

        mock_jira = MagicMock()
        mock_jira_cls.return_value = mock_jira
        mock_jira.issue.return_value = mock_created
        mock_jira._session.post.return_value = MagicMock()
        mock_jira._get_url.return_value = (
            "https://jira.example.com/rest/api/2/issue/bulk"
        )

        with patch("jirabatch.atlas.json_loads") as mock_json_loads:
            mock_json_loads.return_value = {"issues": [{"key": "ENG-1"}], "errors": []}

            conf = {"url": "https://jira.example.com", "user": "u", "api_token": "t"}
            atlas = Atlas(conf)

            issues = {
                "issues": [{"project": "ENG", "issuetype": "Task", "summary": "A task"}]
            }
            atlas.create_jira_issues(issues, batch_size=50)

        mock_logger.info.assert_any_call("Created issue %s: %s", "ENG-1", "A task")

    @patch("jirabatch.atlas.JIRA")
    @patch("jirabatch.atlas.init")
    def test_issue_failure_logs_error(self, mock_init, mock_jira_cls):
        mock_logger = MagicMock()
        mock_init.return_value = mock_logger

        mock_jira = MagicMock()
        mock_jira_cls.return_value = mock_jira
        mock_jira._session.post.return_value = MagicMock()
        mock_jira._get_url.return_value = (
            "https://jira.example.com/rest/api/2/issue/bulk"
        )

        with patch("jirabatch.atlas.json_loads") as mock_json_loads:
            mock_json_loads.return_value = {
                "issues": [],
                "errors": [
                    {
                        "failedElementNumber": 0,
                        "elementErrors": {
                            "errors": {"summary": "Field 'summary' is required"},
                            "errorMessages": [],
                        },
                    }
                ],
            }

            conf = {"url": "https://jira.example.com", "user": "u", "api_token": "t"}
            atlas = Atlas(conf)

            issues = {
                "issues": [
                    {"project": "ENG", "issuetype": "Task", "summary": "Bad issue"}
                ]
            }
            atlas.create_jira_issues(issues, batch_size=50)

        mock_logger.error.assert_called_once()

    @patch("jirabatch.atlas.JIRA")
    @patch("jirabatch.atlas.init")
    def test_batching_over_default_batch_size(self, mock_init, mock_jira_cls):
        mock_logger = MagicMock()
        mock_init.return_value = mock_logger

        mock_jira = MagicMock()
        mock_jira_cls.return_value = mock_jira
        mock_jira._get_url.return_value = (
            "https://jira.example.com/rest/api/2/issue/bulk"
        )

        def make_raw_issue(i):
            return {"key": f"ENG-{i}"}

        def make_mock_issue(i):
            mock_issue = MagicMock()
            mock_issue.key = f"ENG-{i}"
            mock_issue.fields.summary = f"Task {i}"
            return mock_issue

        # 75 issues with batch_size=50 should produce 2 batches: 50 + 25
        num_issues = 75
        mock_jira._session.post.return_value = MagicMock()
        mock_jira.issue.side_effect = [make_mock_issue(i) for i in range(num_issues)]

        with patch("jirabatch.atlas.json_loads") as mock_json_loads:
            mock_json_loads.side_effect = [
                {"issues": [make_raw_issue(i) for i in range(50)], "errors": []},
                {"issues": [make_raw_issue(i) for i in range(50, 75)], "errors": []},
            ]

            conf = {"url": "https://jira.example.com", "user": "u", "api_token": "t"}
            atlas = Atlas(conf)

            issues = {
                "issues": [
                    {"project": "ENG", "issuetype": "Task", "summary": f"Task {i}"}
                    for i in range(num_issues)
                ]
            }
            atlas.create_jira_issues(issues, batch_size=50)

        assert mock_jira._session.post.call_count == 2

    @patch("jirabatch.atlas.JIRA")
    @patch("jirabatch.atlas.init")
    def test_batching_with_custom_batch_size(self, mock_init, mock_jira_cls):
        mock_logger = MagicMock()
        mock_init.return_value = mock_logger

        mock_jira = MagicMock()
        mock_jira_cls.return_value = mock_jira
        mock_jira._get_url.return_value = (
            "https://jira.example.com/rest/api/2/issue/bulk"
        )

        def make_raw_issue(i):
            return {"key": f"ENG-{i}"}

        def make_mock_issue(i):
            mock_issue = MagicMock()
            mock_issue.key = f"ENG-{i}"
            mock_issue.fields.summary = f"Task {i}"
            return mock_issue

        # 5 issues with batch_size=2 should produce 3 batches: 2 + 2 + 1
        num_issues = 5
        mock_jira._session.post.return_value = MagicMock()
        mock_jira.issue.side_effect = [make_mock_issue(i) for i in range(num_issues)]

        with patch("jirabatch.atlas.json_loads") as mock_json_loads:
            mock_json_loads.side_effect = [
                {"issues": [make_raw_issue(i) for i in range(2)], "errors": []},
                {"issues": [make_raw_issue(i) for i in range(2, 4)], "errors": []},
                {"issues": [make_raw_issue(i) for i in range(4, 5)], "errors": []},
            ]

            conf = {"url": "https://jira.example.com", "user": "u", "api_token": "t"}
            atlas = Atlas(conf)

            issues = {
                "issues": [
                    {"project": "ENG", "issuetype": "Task", "summary": f"Task {i}"}
                    for i in range(num_issues)
                ]
            }
            atlas.create_jira_issues(issues, batch_size=2)

        assert mock_jira._session.post.call_count == 3

    @patch("jirabatch.atlas.JIRA")
    @patch("jirabatch.atlas.init")
    def test_mixed_success_and_failure(self, mock_init, mock_jira_cls):
        mock_logger = MagicMock()
        mock_init.return_value = mock_logger

        mock_created = MagicMock()
        mock_created.key = "ENG-1"
        mock_created.fields.summary = "Good task"

        mock_jira = MagicMock()
        mock_jira_cls.return_value = mock_jira
        mock_jira._get_url.return_value = (
            "https://jira.example.com/rest/api/2/issue/bulk"
        )
        mock_jira._session.post.return_value = MagicMock()
        mock_jira.issue.return_value = mock_created

        with patch("jirabatch.atlas.json_loads") as mock_json_loads:
            mock_json_loads.return_value = {
                "issues": [{"key": "ENG-1"}],
                "errors": [
                    {
                        "failedElementNumber": 1,
                        "elementErrors": {
                            "errors": {"summary": "Permission denied"},
                            "errorMessages": [],
                        },
                    }
                ],
            }

            conf = {"url": "https://jira.example.com", "user": "u", "api_token": "t"}
            atlas = Atlas(conf)

            issues = {
                "issues": [
                    {"project": "ENG", "issuetype": "Task", "summary": "Good task"},
                    {"project": "ENG", "issuetype": "Task", "summary": "Bad task"},
                ]
            }
            atlas.create_jira_issues(issues, batch_size=50)

        mock_logger.info.assert_any_call("Created issue %s: %s", "ENG-1", "Good task")
        mock_logger.error.assert_called_once()

    @patch("jirabatch.atlas.JIRA")
    @patch("jirabatch.atlas.init")
    def test_custom_fields_passed_through(self, mock_init, mock_jira_cls):
        mock_logger = MagicMock()
        mock_init.return_value = mock_logger

        mock_created = MagicMock()
        mock_created.key = "ENG-1"
        mock_created.fields.summary = "A task"

        mock_jira = MagicMock()
        mock_jira_cls.return_value = mock_jira
        mock_jira._get_url.return_value = (
            "https://jira.example.com/rest/api/2/issue/bulk"
        )
        mock_jira._session.post.return_value = MagicMock()
        mock_jira.issue.return_value = mock_created

        captured_payloads = []

        def capture_post(_url, data):
            captured_payloads.append(json.loads(data))
            return MagicMock()

        mock_jira._session.post.side_effect = capture_post

        with patch("jirabatch.atlas.json_loads") as mock_json_loads:
            mock_json_loads.return_value = {"issues": [{"key": "ENG-1"}], "errors": []}

            conf = {"url": "https://jira.example.com", "user": "u", "api_token": "t"}
            atlas = Atlas(conf)

            issues = {
                "issues": [
                    {
                        "project": "ENG",
                        "issuetype": "Task",
                        "summary": "A task",
                        "customFields": {
                            "customfield_10100": "Platform Team",
                            "customfield_10200": "Sprint 42",
                        },
                    }
                ]
            }
            atlas.create_jira_issues(issues, batch_size=50)

        sent_fields = captured_payloads[0]["issueUpdates"][0]["fields"]
        assert sent_fields["customfield_10100"] == "Platform Team"
        assert sent_fields["customfield_10200"] == "Sprint 42"
