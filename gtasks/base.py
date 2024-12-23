import json
import subprocess
from typing import List

import inquirer

# Define the types of commits
COMMIT_TYPES = [
    ("fix", "A bug fix."),
    ("feat", "A new feature."),
    ("WIP", "Work in progress."),
    ("exp", "A code to recreate experimentation or experimentation results"),
    ("refactor", "A code changes that niether fixes a bur nor adds a feature."),
    ("perf", "A code change that improves performance."),
    ("docs", "Docs Documentation only changes."),
    ("test", "Test Adding missing or correcting existing tests."),
    (
        "build",
        "Changes that affect the build system or external dependencies (i.e pip, docker, .toml).",
    ),
    ("chor", "Chores like changing folder structure, renaming files, etc."),
    ("ci", " Changes to our CI configration files and scripts."),
    ("backup", "Backup."),
]


def get_owner_repo() -> List[str]:
    command = [
        "gh",
        "repo",
        "view",
        "--json",
        "owner,name",
        "--jq",
        ".owner.login, .name",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout.strip().split("\n")


def parse_collaborators(owner: str, repo: str) -> List[str]:
    command = ["gh", "api", f"repos/{owner}/{repo}/collaborators", "--jq", ".[].login"]
    result = subprocess.run(command, capture_output=True, text=True)

    collaborators = result.stdout.strip().split("\n")

    return [collaborator for collaborator in collaborators]


def get_assignee(owner: str, repo: str) -> str:
    collaborators = parse_collaborators(owner, repo)
    return inquirer.prompt(
        [
            inquirer.List(
                "assignee",
                message="Select an assignee",
                choices=[collaborator for collaborator in collaborators],
            )
        ]
    )["assignee"]


def get_label_selected():
    owner, repo = get_owner_repo()
    result = subprocess.run(
        ["gh", "label", "list", "--repo", f"{owner}/{repo}", "--json", "name"],
        stdout=subprocess.PIPE,
        text=True,
    )

    labels_json = json.loads(result.stdout)

    labels_list = [label["name"] for label in labels_json]

    return inquirer.prompt(
        [
            inquirer.List(
                "label",
                message="Select the label",
                choices=[label for label in labels_list],
            )
        ]
    )["label"]
