import subprocess
import inquirer
from invoke.tasks import task
from invoke import Collection


def git_current_branch() -> str:
    result = subprocess.run(
        ["git", "symbolic-ref", "--short", "HEAD"], capture_output=True, text=True
    )
    branch = result.stdout.strip()
    return branch


@task
def new(ctx: None) -> None:
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
