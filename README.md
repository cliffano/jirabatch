![Avatar](avatar.jpg)

[![Build Status](https://github.com/cliffano/jirabatch/workflows/CI/badge.svg)](https://github.com/cliffano/jirabatch/actions?query=workflow%3ACI)
[![Security Status](https://snyk.io/test/github/cliffano/jirabatch/badge.svg)](https://snyk.io/test/github/cliffano/jirabatch)
[![Dependencies Status](https://img.shields.io/librariesio/release/pypi/jirabatch)](https://libraries.io/github/cliffano/jirabatch)
[![Published Version](https://img.shields.io/pypi/v/jirabatch.svg)](https://pypi.python.org/pypi/jirabatch)

# JiraBatch

Jira Batch is a batch Jira issues creator.

Define the issues in 

## Installation

    pip3 install jirabatch

## Usage

Create a configuration file, e.g. `jirabatch.yaml`, and then create an issues file, e.g. `issues.yaml` .

Run jirabatch with specified config file and issues file:

    jirabatch --conf-file jirabatch.yaml --issues-file issues.yaml

Show help guide:

    jirabatch --help

## Configuration

These are the configuration properties that you can use with `jirabatch` CLI.
Some example configuration files are available on [examples](examples) folder.

Jira Batch configuration properties:

| Property | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `url` | String | Yes | The base URL of the Jira server | `https://someorg.atlassian.net` |
| `user` | String | Yes | The Jira username or email address | `someuser@example.com` |
| `api_token` | String | Yes* | The Jira API token used for authentication. Takes precedence over `password` | `sometoken12345` |
| `password` | String | Yes* | The Jira account password. Used as fallback when `api_token` is not set | `somepassword` |

Issues configuration properties:

| Property | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `defaults` | Object | No | Default field values merged into every entry in `issues[]` | `{ project: "ENG", issuetype: "Task" }` |
| `issues[]` | Array | Yes | List of Jira issues to create | `[{ summary: "Issue summary" }]` |
| `issues[].project` | String | Yes* | Jira project key | `ENG` |
| `issues[].issuetype` | String | Yes* | Jira issue type name | `Task` |
| `issues[].summary` | String | Yes* | Jira issue summary | `Rotate SSH key` |
| `issues[].description` | String | No | Jira issue description | `Rotate SSH key before expiry` |
| `issues[].reporter` | String | No | Reporter account ID | `5b10a2844c20165700ede21g` |
| `issues[].assignee` | String | No | Assignee account ID | `5b10ac8d82e05b22cc7d4ef5` |
| `issues[].priority` | String | No | Priority name | `High` |
| `issues[].labels[]` | Array[String] | No | Labels to assign | `["infra", "security"]` |
| `issues[].components[]` | Array[String] | No | Component names | `["Cloud", "Backend"]` |
| `issues[].versions[]` | Array[String] | No | Affects version names | `["2026.1"]` |
| `issues[].fixVersions[]` | Array[String] | No | Fix version names | `["2026.2"]` |
| `issues[].environment` | String | No | Environment field value | `Production AWS us-east-1` |
| `issues[].duedate` | String | No | Due date (sent as string) | `2026-04-01` |
| `issues[].timetracking` | Object | No | Jira timetracking object | `{ originalEstimate: "3d", remainingEstimate: "2d" }` |
| `issues[].security` | String | No | Security level name | `Internal` |
| `issues[].parent` | String | No | Parent issue key | `ENG-100` |
| `issues[].epic` | String | No | Epic issue key (normalized to parent) | `ENG-10` |
| `issues[].customFields` | Object | No | Map of Jira custom field IDs to values | `{ customfield_10100: "Platform Team" }` |
| `issues[].subtasks[]` | Array[Object] | No | Subtasks created after parent issue succeeds | `[{ summary: "Subtask 1" }]` |
| `issues[].subtasks[].summary` | String | Yes | Subtask summary | `Update cert in service A` |
| `issues[].subtasks[].issuetype` | String | No | Subtask issue type (defaults to `Subtask`) | `Sub-task` |

Colophon
--------

[Developer's Guide](https://cliffano.github.io/developers_guide.html#python)

Build reports:

* [Lint report](https://cliffano.github.io/jirabatch/lint/pylint/index.html)
* [Code complexity report](https://cliffano.github.io/jirabatch/complexity/wily/index.html)
* [Unit tests report](https://cliffano.github.io/jirabatch/test/pytest/index.html)
* [Test coverage report](https://cliffano.github.io/jirabatch/coverage/coverage/index.html)
* [Integration tests report](https://cliffano.github.io/jirabatch/test-integration/pytest/index.html)
* [API Documentation](https://cliffano.github.io/jirabatch/doc/sphinx/index.html)
