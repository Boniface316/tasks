import json
import subprocess
from typing import (
    Dict,
    List,
    Union,
)

import inquirer
from invoke import (
    Collection,
    run,
)
from invoke.tasks import (
    task,
)

from .base import (
    get_owner_repo,
)

# This file contains scripts related to setting up a repository.


labels_list = [
    {
        "color": "d73a4a",
        "description": "Something isn't working",
        "name": "bug",
    },
    {
        "color": "0075ca",
        "description": "Improvements or additions to documentation",
        "name": "docs",
    },
    {
        "color": "cfd3d7",
        "description": "Experiment to validate an hypothesis",
        "name": "exp",
    },
    {
        "color": "008672",
        "description": "Performance",
        "name": "perf",
    },
    {
        "color": "7057ff",
        "description": "Refactor the code",
        "name": "refact",
    },
    {
        "color": "8F7122",
        "description": "Anything outside of code and documentation",
        "name": "chore",
    },
    {
        "color": "E6F574",
        "description": "feature",
        "name": "feat",
    },
]


def get_existing_labels(
    owner: str,
    repo: str,
) -> List[
    Dict[
        str,
        Union[
            str,
            int,
        ],
    ]
]:
    """
    Get the existing labels in the repository.
    This function uses the GitHub CLI to get the existing labels in the repository.
    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
    Returns:
        List[Dict[str, Union[str, int]]]: The list of existing labels in the repository.
    """
    result = run(
        f"gh api repos/{owner}/{repo}/labels",
        hide=True,
    )
    existing_labels = result.stdout
    return json.loads(existing_labels)  # type: List[Dict[str, Union[str, int]]]


@task
def labels(
    ctx,
) -> None:
    """
    Set up the labels in the repository.
    This function uses the GitHub CLI to delete the existing labels in the repository and create new labels based on the `labels_list` defined in the script.
    Returns:
        None
    """

    
    (
        owner,
        repo,
    ) = get_owner_repo()

    
    existing_labels = get_existing_labels(
        owner,
        repo,
    )

    

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


def create_submodules():
    """
    Create the submodules in the repository.
    This function uses the GitHub CLI to create the submodules in the repository.
    Returns:
        None
    """

    (
        owner,
        repo,
    ) = get_owner_repo()
    path = inquirer.text("Enter the name of the submodule folder i.e notes")
    repo_name = f"{repo}_{path}"
    try:
        run(f"gh repo create {repo_name} --private --add-readme")
        run(f"git submodule add https://github.com/{owner}/{repo_name}.git {path}")
        run(f"git add .gitmodules {path}")
        run(f'git commit -m "Add {path} submodules"')
        run("git push")
        print(f"Successfully created and added {path} as submodule.")

    except subprocess.CalledProcessError as e:
        if "already exists in the index" in e.stderr.decode():
            print(f"Submodule {path} already exists, skipping creation.")
        else:
            raise


@task
def submodule(
    ctx: None,
) -> None:
    """
    Set up the repository to use submodules.
    """
    create_submodules()
    run("git config push.recurseSubmodules on-demand")


namespace = Collection(
    "setup",
    labels,
    submodule,
)
