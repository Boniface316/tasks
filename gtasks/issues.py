import inquirer
from .base import get_owner_repo, get_label_selected, get_assignee
from .branch import git_current_branch
from typing import List
import subprocess
from invoke.tasks import task
from invoke import Collection


def get_issues(assignee: str = "@me") -> List[str]:
    owner, repo = get_owner_repo()
    assignee = "--assignee=" + assignee
    command = ["gh", "issue", "list", assignee, f"--repo={owner}/{repo}"]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout.strip().split("\n")


def body_issue_docs() -> str:
    description = inquirer.text("Enter the issue description")
    location = inquirer.text("Enter the location of the documentation [Optional]", default="")
    issue_type = inquirer.prompt(
        [
            inquirer.List(
                "type",
                message="Select the type of documentation",
                choices=["Missing", "Outdated", "Typo", "Inaccurate"],
            )
        ]
    )["type"]
    details = inquirer.text("Enter the details of the issue [Optional]", default="")
    suggestion = inquirer.text("Enter the suggestion to fix the issue [Optional]", default="")
    additional = inquirer.text("Enter any additional information [Optional]", default="")

    body = "## Description\n\n"
    body += f"{description}\n\n"
    body += "## Location\n\n"
    body += f"{location}\n\n"
    body += "## Issue Type\n\n"
    body += f"{issue_type}\n\n"
    body += "## Details\n\n"
    body += f"{details}\n\n"
    body += "## Suggestion\n\n"
    body += f"{suggestion}\n\n"
    body += "## Additional Information\n\n"
    body += f"{additional}\n\n"
    return body


def body_issue_feat() -> str:
    description = inquirer.text("Descbribe the feature you want to add")
    solution = inquirer.text("Describe the solution you have in mind")
    alternatives = inquirer.text(
        "Describe any alternative solutions you have in mind if the feature is not feasible [Optional]",
        default="",
    )
    additional = inquirer.text("Enter any additional information [Optional]", default="")

    body = "## Description\n\n"
    body += f"{description}\n\n"
    body += "## Solution\n\n"
    body += f"{solution}\n\n"
    body += "## Alternatives\n\n"
    body += f"{alternatives}\n\n"
    body += "## Additional Information\n\n"
    body += f"{additional}\n\n"
    return body


def get_issue_body(label: str) -> str:
    if label == "bug":
        body = body_issue_bug()
    elif label == "docs":
        body = body_issue_docs()
    elif label == "feat":
        body = body_issue_feat()
    else:
        body = inquirer.text("Describe the issue")
    return body


def body_issue_bug() -> str:
    description = inquirer.text("Enter the issue description")
    steps = inquirer.text("Enter the steps to reproduce the problem")
    expected = inquirer.text("Enter the expected behavior")
    actual = inquirer.text("Enter the actual behavior")
    additional = inquirer.text("Enter any additional information [Optional]", default="")

    body = "## Description\n\n"
    body += f"{description}\n\n"
    body += "## Steps to Reproduce the Problem\n\n"
    body += f"{steps}\n\n"
    body += "## Expected Behavior\n\n"
    body += f"{expected}\n\n"
    body += "## Actual Behavior\n\n"
    body += f"{actual}\n\n"
    body += "## Additional Information\n\n"
    body += f"{additional}\n\n"
    return body


@task
def close(issue_id: str) -> None:
    # issue_id = inquirer.text("Enter the issue ID to close")
    # issue_id = issue_id.split(" ")[0]

    # subprocess.run(["gh", "issue", "close", issue_id])

    if inquirer.confirm("Do you want to delete the branch?", default=True):
        branch = git_current_branch()
        subprocess.run(["git", "checkout", "main"])

        print("Deleting branch local branch")
        subprocess.run(["git", "branch", "-d", branch])
        print("Deleting branch remote branch")
        subprocess.run(["git", "push", "origin", "--delete", branch])


@task
def list(context: None, assignee: str = "@me") -> None:
    lines = get_issues(assignee)

    print(f"Open Issues Assigned to {assignee}:")
    for line in lines:
        parts = line.split("\t")
        issue_id = parts[0]
        title = parts[2]
        print(f"{issue_id} - {title}")


@task
def new(context: None) -> None:
    owner, repo = get_owner_repo()

    title = inquirer.text("Enter the issue title")
    label = get_label_selected()

    body = get_issue_body(label)

    command = [
        "gh",
        "issue",
        "create",
        f"--title={title}",
        f"--body={body}",
        f"--repo={owner}/{repo}",
        f"--label={label}",
    ]
    if inquirer.confirm("Assign this issue to someone? [True]", default=True):
        assignee = get_assignee(owner, repo)
        command.append(f"--assignee={assignee}")
    subprocess.run(command)


namespace = Collection("issues", close, list, new)
