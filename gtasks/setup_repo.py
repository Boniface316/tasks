from invoke import task, Collection

import json
import subprocess
from typing import Dict, List, Union

from invoke.tasks import task

from .base import get_owner_repo


# This file contains scripts related to setting up a repository.


labels_list = [
    {"color": "d73a4a", "description": "Something isn't working", "name": "bug"},
    {
        "color": "0075ca",
        "description": "Improvements or additions to documentation",
        "name": "docs",
    },
    {"color": "cfd3d7", "description": "Experiment to validate an hypothesis", "name": "exp"},
    {"color": "008672", "description": "Performance", "name": "perf"},
    {"color": "7057ff", "description": "Refactor the code", "name": "refact"},
    {
        "color": "8F7122",
        "description": "Anything outside of code and documentation",
        "name": "chore",
    },
    {"color": "E6F574", "description": "feature", "name": "feat"},
]


def get_existing_labels(owner: str, repo: str) -> List[Dict[str, Union[str, int]]]:
    """
    Get the existing labels in the repository.
    This function uses the GitHub CLI to get the existing labels in the repository.
    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
    Returns:
        List[Dict[str, Union[str, int]]]: The list of existing labels in the repository.
    """
    existing_labels = subprocess.check_output(["gh", "api", f"repos/{owner}/{repo}/labels"]).decode(
        "utf-8"
    )
    return json.loads(existing_labels)  # type: List[Dict[str, Union[str, int]]]


@task
def labels(ctx: None) -> None:

    """
    Set up the labels in the repository.
    This function uses the GitHub CLI to delete the existing labels in the repository and create new labels based on the `labels_list` defined in the script.
    Returns:
        None
    """

    owner, repo = get_owner_repo()
    existing_labels = get_existing_labels(owner, repo)
    for label in existing_labels:
        subprocess.run(
            [
                "gh",
                "label",
                "delete",
                label["name"],
                "--repo",
                f"{owner}/{repo}",
                "--yes",  # Automatically confirm deletion
            ]
        )

    # Update with the provided labels
    for label in labels_list:
        subprocess.run(
            [
                "gh",
                "label",
                "create",
                label["name"],
                "--color",
                label["color"],
                "--description",
                label["description"],
                "--repo",
                f"{owner}/{repo}",
            ]
        )

@task
def submodule(ctx: None) -> None:
    subprocess.run(["git", "config", "push.recurseSubmodules", "on-demand"])


namespace = Collection("setup", labels, submodule)
