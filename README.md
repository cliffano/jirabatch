![Avatar](avatar.jpg)

[![Build Status](https://github.com/cliffano/jira-batch/workflows/CI/badge.svg)](https://github.com/cliffano/jira-batch/actions?query=workflow%3ACI)
[![Security Status](https://snyk.io/test/github/cliffano/jira-batch/badge.svg)](https://snyk.io/test/github/cliffano/jira-batch)
[![Dependencies Status](https://img.shields.io/librariesio/release/pypi/jirabatch)](https://libraries.io/github/cliffano/jira-batch)
[![Published Version](https://img.shields.io/pypi/v/jirabatch.svg)](https://pypi.python.org/pypi/jirabatch)

# JiraBatch

JiraBatch is a batch Jira issues creator.

Define the issues in 

## Installation

    pip3 install jirabatch

## Usage

Create a configuration file, e.g. `jirabatch.yaml`, and then create an issues file, e.g. `issues.yaml` .

Run jirabatch with specified config file and issues file:

    jirabatch --conf-file jiraiya.yaml --issues-file issues.yaml

Show help guide:

    jirabatch --help

## Configuration

These are the configuration properties that you can use with `jirabatch` CLI.
Some example configuration files are available on [examples](examples) folder.

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `text` | String | The message text | Hello World |

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
