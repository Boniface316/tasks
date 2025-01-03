import subprocess
import inquirer
from invoke.tasks import task
from invoke import Collection

# This file contains scripts related to branch activities.


def git_current_branch() -> str:
    """
    Get the current branch name.
    This function uses the `git` command to retrieve the current branch name.
    Returns:
        str: The name of the current branch.
    """

    result = subprocess.run(
        ["git", "symbolic-ref", "--short", "HEAD"], capture_output=True, text=True
    )
    branch = result.stdout.strip()
    return branch


def delete_branch(ctx: None) -> None:
    """
    Delete the current branch.
    This function uses the `git` command to delete the current branch.
    Returns:
        None
    """

    branch = git_current_branch()
    subprocess.run(["git", "checkout", "main"])

    print("Deleting branch local branch")
    subprocess.run(["git", "branch", "-d", branch])
    print("Deleting branch remote branch")
    subprocess.run(["git", "push", "origin", "--delete", branch])


@task(
    help={
        "issue_id": "The ID of the issue to create a branch from. If not provided, use `gtasks issues.list` to get the issue ID."
    }
)
def new(ctx: None, issue_id: int = None) -> None:
    """
    Create a new branch based on a GitHub issue.
    This function interacts with the GitHub CLI to create a new branch based on the provided issue ID.
    If no issue ID is provided, it prompts the user to enter one. It then retrieves the labels of the issue,
    constructs a branch name, and creates a new branch based on the issue.
    Args:
        issue_id (int, optional): The ID of the GitHub issue. If not provided, the user will be prompted to enter it.
    Returns:
        None
    """

    if issue_id is None:
        issue_id = inquirer.text("Enter the issue ID")
        issue_id = issue_id.split(" ")[0]
    command = ["gh", "issue", "view", issue_id, "--json", "labels", "--jq", ".labels[].name"]
    label = subprocess.run(command, capture_output=True, text=True)
    label = label.stdout.strip()

    branch_name = inquirer.text("Enter the branch name [Make is similar to the issue title]")
    branch_name = f"{label}/{issue_id}-{branch_name}"

    command = [
        "gh",
        "issue",
        "develop",
        issue_id,
        "--name",
        branch_name,
        "--base",
        "main",
        "--checkout",
    ]
    subprocess.run(command)

    subprocess.run("git checkout -b " + branch_name, shell=True)


namespace = Collection("branch", new)
