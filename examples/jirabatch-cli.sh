#!/usr/bin/bash
set -o nounset

cd ../
. ./.venv/bin/activate
cd examples/

printf "\n\n========================================\n"
printf "Show help guide:\n"
jirabatch --help

printf "\n\n========================================\n"
printf "Show version info: jirabatch --version\n"
jirabatch --version

printf "\n\n========================================\n"
printf "Run command with default config file and default issues file:\n"
jirabatch

printf "\n\n========================================\n"
printf "Run command with specified config files creating a simple Jira epic:\n"
jirabatch --conf-file jirabatch.yaml --issues-file epic-simple.yaml

printf "\n\n========================================\n"
printf "Run command with specified config files creating a simple Jira story:\n"
jirabatch --conf-file jirabatch.yaml --issues-file story-simple.yaml

printf "\n\n========================================\n"
printf "Run command with specified config files creating a simple Jira task:\n"
jirabatch --conf-file jirabatch.yaml --issues-file task-simple.yaml

printf "\n\n========================================\n"
printf "Run command with specified config files creating a simple Jira epic and a story as part of the epic:\n"
jirabatch --conf-file jirabatch.yaml --issues-file epic-with-story.yaml

printf "\n\n========================================\n"
printf "Run command with specified config files creating a simple Jira story and a subtask as part of the story:\n"
jirabatch --conf-file jirabatch.yaml --issues-file story-with-subtask.yaml

printf "\n\n========================================\n"
printf "Run command with specified config files creating a simple Jira task and a subtask as part of the first task:\n"
jirabatch --conf-file jirabatch.yaml --issues-file task-with-subtask.yaml

printf "\n\n========================================\n"
printf "Run command with specified config files creating a comprehensive Jira epic:\n"
jirabatch --conf-file jirabatch.yaml --issues-file epic-comprehensive.yaml

printf "\n\n========================================\n"
printf "Run command with specified config files creating a comprehensive Jira story:\n"
jirabatch --conf-file jirabatch.yaml --issues-file story-comprehensive.yaml

printf "\n\n========================================\n"
printf "Run command with specified config files creating a comprehensive Jira task:\n"
jirabatch --conf-file jirabatch.yaml --issues-file task-comprehensive.yaml

printf "\n\n========================================\n"
printf "Run command with specified config files creating Jira epic, stories, and subtasks with default values:\n"
jirabatch --conf-file jirabatch.yaml --issues-file defaults-epic-story-subtask.yaml
