from typing import (
    List,
)

import inquirer
from invoke import (
    run,
    task,
)

# This script contains the base functions that are used in other scripts.


# Define the types of commits
COMMIT_TYPES = [
    (
        "fix",
        "A bug fix.",
    ),
    (
        "feat",
        "A new feature.",
    ),
    (
        "WIP",
        "Work in progress.",
    ),
    (
        "exp",
        "A code to recreate experimentation or experimentation results",
    ),
    (
        "refactor",
        "A code changes that niether fixes a bur nor adds a feature.",
    ),
    (
        "perf",
        "A code change that improves performance.",
    ),
    (
        "docs",
        "Docs Documentation only changes.",
    ),
    (
        "test",
        "Test Adding missing or correcting existing tests.",
    ),
    (
        "build",
        "Changes that affect the build system or external dependencies (i.e pip, docker, .toml).",
    ),
    (
        "chor",
        "Chores like changing folder structure, renaming files, etc.",
    ),
    (
        "ci",
        " Changes to our CI configration files and scripts.",
    ),
    (
        "backup",
        "Backup.",
    ),
]


def parse_collaborators(
    owner: str,
    repo: str,
) -> List[str]:
    """
    Parse the collaborators of a repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The repository name.

    Returns:
        List[str]: A list containing the collaborators of the repository.
    """

    result = run(f"gh api repos/{owner}/{repo}/collaborators --jq '.[].login'")

    collaborators = result.stdout.strip().split("\n")

    return [collaborator for collaborator in collaborators]


def get_assignee(
    owner: str,
    repo: str,
) -> str:
    """
    Get the assignee for an issue.
    This function uses the `gh` command to retrieve the assignee for an issue.
    Args:
        owner (str): The owner of the repository.
        repo (str): The repository name.
    Returns:
        str: The assignee for the issue.
    """

    collaborators = parse_collaborators(
        owner,
        repo,
    )
    return inquirer.prompt(
        [
            inquirer.List(
                "assignee",
                message="Select an assignee",
                choices=[collaborator for collaborator in collaborators],
            )
        ]
    )["assignee"]


def get_owner_repo() -> tuple:
    """
    Get the owner and repository name.
    This function uses the `gh` command to retrieve the owner and repository name.
    Returns:
        tuple: A tuple containing the owner and repository name.
    """

    if owner is None:
        owner = run(
            "gh repo view --json owner --jq '.owner.login'",
            hide=True,
        ).stdout.strip()

    if repo is None:
        repo = run(
            "gh api repos/:owner/:repo -q .name",
            hide=True,
        ).stdout.strip()
    return (
        owner,
        repo,
    )


def get_label_selected():
    """
    Get the selected label.
    This function uses the `gh` command to retrieve the labels of a repository.
    Returns:
        str: The selected
    """

    result = run("gh label list").stdout.strip().split("\n")

    labels = [line.split("\t")[0] for line in result]

    return inquirer.prompt(
        [
            inquirer.List(
                "label",
                message="Select the label",
                choices=[label for label in labels],
            )
        ]
    )["label"]
