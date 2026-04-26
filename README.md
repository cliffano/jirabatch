# jiraiya
<img align="right" src="https://raw.github.com/cliffano/jiraiya/main/avatar.jpg" alt="Avatar"/>

[![Build Status](https://github.com/cliffano/jiraiya/workflows/CI/badge.svg)](https://github.com/cliffano/jiraiya/actions?query=workflow%3ACI)
[![Security Status](https://snyk.io/test/github/cliffano/jiraiya/badge.svg)](https://snyk.io/test/github/cliffano/jiraiya)
[![Dependencies Status](https://img.shields.io/librariesio/release/pypi/jiraiya)](https://libraries.io/github/cliffano/jiraiya)
[![Published Version](https://img.shields.io/pypi/v/jiraiya.svg)](https://pypi.python.org/pypi/jiraiya)
<br/>

Jiraiya
-------

Jiraiya is a batch Jira issues creator via YAML definition.

Installation
------------

    pip3 install jiraiya

Usage
-----

Create a configuration file, e.g. `jiraiya.yaml`:

    ---
    text: Hello World

Run jiraiya with specified config file:

    jiraiya --conf-file jiraiya.yaml

Run jiraiya with specified config file and custom flags:

    jiraiya --conf-file jiraiya.yaml --reverse --transformation upper

Show help guide:

    jiraiya --help

Configuration
-------------

These are the configuration properties that you can use with `jiraiya` CLI.
Some example configuration files are available on [examples](examples) folder.

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `text` | String | The message text | Hello World |

Colophon
--------

[Developer's Guide](https://cliffano.github.io/developers_guide.html#python)

Build reports:

* [Lint report](https://cliffano.github.io/jiraiya/lint/pylint/index.html)
* [Code complexity report](https://cliffano.github.io/jiraiya/complexity/wily/index.html)
* [Unit tests report](https://cliffano.github.io/jiraiya/test/pytest/index.html)
* [Test coverage report](https://cliffano.github.io/jiraiya/coverage/coverage/index.html)
* [Integration tests report](https://cliffano.github.io/jiraiya/test-integration/pytest/index.html)
* [API Documentation](https://cliffano.github.io/jiraiya/doc/sphinx/index.html)
>>>>>>> c735851 (Initial skeleton commit.)
