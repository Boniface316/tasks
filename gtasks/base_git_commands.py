import datetime
import json
import subprocess
from typing import Any, List, Union

import inquirer
import yaml
from invoke.tasks import task
from invoke import Collection

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


def git_current_branch() -> str:
    result = subprocess.run(
        ["git", "symbolic-ref", "--short", "HEAD"], capture_output=True, text=True
    )
    branch = result.stdout.strip()
    return branch


def git_add() -> None:
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    changed_files = [line[3:] for line in result.stdout.splitlines() if line]
    if not changed_files:
        print("No files to add.")
        return

    files_to_add = inquirer.prompt(
        [
            inquirer.Checkbox(
                "files",
                message="Select the files to add to the commit",
                choices=changed_files,
            )
        ]
    )["files"]

    if not files_to_add:
        print("No files selected.")
        return

    subprocess.run(["git", "add"] + files_to_add)

    print("Files added to the commit.")


def get_commit_type() -> Union[str, Any]:
    return inquirer.prompt(
        [
            inquirer.List(
                "type",
                message="Select the type of change you are committing",
                choices=[t[0] for t in COMMIT_TYPES],
            )
        ]
    )["type"]


def git_commit(commit_type) -> None:
    if commit_type == "exp":
        add_experiment_notes()
    elif commit_type == "WIP":
        if inquirer.confirm("Do you want to add experiment notes? [True]", default=True):
            add_experiment_notes()

    description = inquirer.text("Enter a short description of the change [code]")

    body = inquirer.text("Enter a longer description of the change [code] (optional)", default="")

    breaking_changes = inquirer.text("Are there any breaking changes? (optional)", default="")

    # Format the commit message
    commit_message = f"{commit_type}: {description}\n\n{body}"
    if breaking_changes:
        commit_message += f"\n\nBREAKING CHANGE: {breaking_changes}"

    subprocess.run(["git", "commit", "-m", commit_message])


def create_PR_body() -> str:
    print("Enter the PR body")
    print(
        "Include description of feature this PR introduces or a bug that it fixes. Include the following information:"
    )
    context = inquirer.text("Context: Why is it needed? ")
    solution = inquirer.text("Consise description of the implemented solution ")
    dependencies = inquirer.text(
        "If any dependencies are added, list them and justify why they are needed [optional] ",
        default="",
    )

    confirm_revision = inquirer.confirm("I have self-reviewed my code.", default=True)
    confirm_tests = inquirer.confirm(
        "I have included test cases validating introduced feature/fix.", default=True
    )
    confirm_docs = inquirer.confirm("I have updated the documentation.", default=True)

    body = "## Description\n"

    body += f"Context: {context}\n\nSolution: {solution}\n\nDependencies: {dependencies}\n\n"

    body += "## Please Verify that you have completed the following steps\n"
    if not confirm_revision:
        body += "- [ ] I have self-reviewed my code.\n"
    else:
        body += "- [x] I have self-reviewed my code.\n"
    if not confirm_tests:
        body += "- [ ] I have included test cases validating introduced feature/fix.\n"
    else:
        body += "- [x] I have included test cases validating introduced feature/fix.\n"
    if not confirm_docs:
        body += "- [ ] I have updated the documentation.\n"
    else:
        body += "- [x] I have updated the documentation.\n"

    return body


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


def create_pr(owner: str, repo: str) -> None:
    title = inquirer.text("Enter the PR title")
    body = create_PR_body()
    assignee = get_assignee(owner, repo)

    subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--base=main",
            f"--title={title}",
            f"--body={body}",
            f"--assignee={assignee}",
        ]
    )


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


def add_experiment_notes():
    date_time = datetime.datetime.now()
    date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    exp_hypothesis = inquirer.text("What was the hypothesis?")
    exp_results = inquirer.text("What were the results?")
    exp_conclusion = inquirer.text("What is the conclusion?")
    exp_data_risk = inquirer.text("What are the risks related to data? (optional)", default="")
    exp_model_risk = inquirer.text(
        "What are the risks related to the model? (optional)",
        default="",
    )
    exp_code_risk = inquirer.text("What are the risks related to the code? (optional)", default="")

    author = subprocess.run(
        ["git", "config", "user.name"], capture_output=True, text=True
    ).stdout.strip()

    experiment_notes = {
        "author": author,
        "date": date_time,
        "hypothesis": exp_hypothesis,
        "results": exp_results,
        "conclusion": exp_conclusion,
        "data_risk": exp_data_risk,
        "model_risk": exp_model_risk,
        "code_risk": exp_code_risk,
    }

    # Save the experiment notes to a YAML file
    with open(f"notes/{date_time}.yaml", "w") as file:
        yaml.dump(experiment_notes, file)

    subprocess.run(["git", "submodule", "foreach", "git", "add", "."])
    subprocess.run(["git", "submodule", "foreach", "git", "commit", "-m", "Update submodule"])
    subprocess.run(["git", "submodule", "foreach", "git", "push"])


@task
def close(issue_id: str) -> None:
    issue_id = inquirer.text("Enter the issue ID to close")
    issue_id = issue_id.split(" ")[0]

    subprocess.run(["gh", "issue", "close", issue_id])


@task
def issues(context: None, assignee: str = "@me") -> None:
    lines = get_issues(assignee)

    print("Open Issues Assigned to You:")
    for line in lines:
        parts = line.split("\t")
        issue_id = parts[0]
        title = parts[2]
        print(f"{issue_id} - {title}")


@task
def newissue(context: None) -> None:
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


@task
def gacp(ctx: None) -> None:
    owner, repo = get_owner_repo()
    current_branch = git_current_branch()

    git_add()

    commit_type = get_commit_type()

    git_commit(commit_type)

    subprocess.run(["git", "push", "--set-upstream", "origin", current_branch])

    if commit_type not in ["WIP", "exp", "backup"]:
        if inquirer.confirm("Create a PR?", default=True):
            create_pr(owner, repo)


@task
def newbranch(ctx: None) -> None:
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


namespace = Collection(close, issues, newissue, gacp, newbranch)
