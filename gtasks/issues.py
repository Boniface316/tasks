import inquirer
from .base import get_owner_repo, get_label_selected, get_assignee
from .branch import delete_branch
from typing import List
from invoke.tasks import task
from invoke import Collection
from invoke import run

# This script is used to manage issues in a GitHub repository


def get_issues(assignee: str = "@me") -> List[str]:
    """
    Get the list of issues assigned to the user.

    By default, it gets the issues assigned to the user running the script. If the assignee is specified, it gets the issues assigned to that user.

    You can specify the assignee using the `--assignee` flag.

    Args:
        assignee (str, optional): The assignee of the issues. Defaults to "@me".

        Returns:
        List[str]: The list of issues assigned to the user
    """

    issues_list = run(f"gh issue list --assignee={assignee}")

    return issues_list.stdout.strip().split("\n")


def body_issue_docs() -> str:
    """
    Get the body of the issue for documentation issues.

    Returns:
        str: The body of the issue

    """
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
    """
    Get the body of the issue for feature requests.

    Returns:
        str: The body of the issue

    """

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
    """
    Get the body of the issue based on the label.

    Args:
        label (str): The label of the issue

    Returns:
        str: The body of the issue

    """
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
    """
    Get the body of the issue for bug reports.

    Returns:
        str: The body of the issue

    """

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


@task(
    help={
        "issue_id": "The ID of the issue to close",
    }
)
def close(ctx: None, issue_id: str = None) -> None:
    """
    Close an issue.

    This function uses the GitHub CLI to close an issue. If the issue ID is not provided, it prompts the user to enter one.

    Args:
        issue_id (str, optional): The ID of the issue to close.

    Returns:
        None
    """

    if issue_id is None:
        issues = get_issues()
        issues.append("Other")
        issue_id = inquirer.text("Enter the issue ID to close", choices=issues)

        if issue_id == "Other":
            issue_id = inquirer.text("Enter the issue ID to close")
            issue_id = issue_id.split(" ")[0]

    run(f"gh issue close {issue_id}")

    if inquirer.confirm("Do you want to delete the branch?", default=True):
        delete_branch()


@task(
    help={
        "assignee": "The assignee of the issues. Defaults to '@me'. Use 'all-open' to get all issues. Use 'none' to get unassigned issues. Use the username to get issues assigned to that user.",
    }
)
def list(context: None, assignee: str = "@me") -> None:
    """
    List the open issues assigned to the user.

    This function uses the GitHub CLI to list the open issues assigned to the user. By default, it lists the issues assigned to the user running the script. If the assignee is specified, it lists the issues assigned to that user.

    Other options for the assignee are:
    - `all-open`: Get all open issues
    - `none`: Get unassigned issues

    You can specify the assignee using the `--assignee` flag.

    Args:
        assignee (str, optional): The assignee of the issues. Defaults to "@me".

    Returns:
        None

    """
    lines = get_issues(assignee)

    print(f"Open Issues Assigned to {assignee}:")
    for line in lines:
        parts = line.split("\t")
        issue_id = parts[0]
        title = parts[2]
        print(f"{issue_id} - {title}")


@task
def new(context: None) -> None:
    """
    Create a new issue.

    This function uses the GitHub CLI to create a new issue. It prompts the user to enter the issue title, label, and assignee. It then constructs the body of the issue based on the label and creates a new issue.

    Returns:
        None

    """

    owner, repo = get_owner_repo()

    title = inquirer.text("Enter the issue title")
    label = get_label_selected()

    body = get_issue_body(label)

    command = f"gh issue create --title='{title}' --body='{body}' --repo='{owner}/{repo}' --label='{label}'"
    if inquirer.confirm("Assign this issue to someone? [True]", default=True):
        assignee = get_assignee(owner, repo)
        command += f" --assignee='{assignee}'"
    run(command)


namespace = Collection("issues", close, list, new)
