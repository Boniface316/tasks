import subprocess
import inquirer
import yaml
import datetime
from typing import Any, Union
from invoke.tasks import task
from invoke import Collection

from .base import get_owner_repo, get_assignee, COMMIT_TYPES
from .branch import git_current_branch


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


namespace = Collection("git", gacp)
