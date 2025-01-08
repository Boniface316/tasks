import inquirer
import yaml
import datetime
from typing import Any, Union
from invoke.tasks import task
from invoke import Collection
import os

from .base import get_assignee, COMMIT_TYPES, get_owner_repo
from .branch import git_current_branch
from invoke.context import Context

# This file contains scripts related to git activities.


def git_add(ctx: Context) -> None:
    """
    Interactively add changed files to the git staging area.
    This function checks the current git status for any changed files.
    If there are no changed files, it prints a message and exits.
    If there are changed files, it prompts the user to select which files
    to add to the staging area using an interactive checkbox menu.
    If no files are selected, it prints a message and exits.
    Otherwise, it adds the selected files to the git staging area and
    prints a confirmation message.
    """

    result = ctx.run("git status --porcelain", hide=True, warn=True)
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

    ctx.run("git add " + " ".join(files_to_add))

    print("Files added to the commit.")


def get_commit_type() -> Union[str, Any]:
    """
    Prompts the user to select the type of change they are committing from a list of commit types.
    Returns:
        str: The type of change selected by the user.
    """

    return inquirer.prompt(
        [
            inquirer.List(
                "type",
                message="Select the type of change you are committing",
                choices=[t[0] for t in COMMIT_TYPES],
            )
        ]
    )["type"]


def git_commit(ctx: Context, commit_type) -> None:
    """
    Create a git commit with a formatted commit message based on the provided commit type.
    Args:
        commit_type (str): The type of commit, e.g., "exp" for experiment notes or "WIP" for work in progress.
        The function prompts the user for additional information such as a short description, a longer description,
        and any breaking changes. It then formats these inputs into a commit message and executes the git commit command.
    """

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

    ctx.run(f'git commit -m "{commit_message}"')


def create_PR_body() -> str:
    """
    Prompts the user to input details for a pull request (PR) body and returns the formatted PR body as a string.
    The function interacts with the user to gather the following information:
    - Context: Why the PR is needed.
    - Solution: A concise description of the implemented solution.
    - Dependencies: Any added dependencies and their justification (optional).
    - Confirmation of self-review, inclusion of test cases, and documentation updates.
    Returns:
        str: The formatted PR body including the description and verification steps.
    """

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


def create_pr(ctx: Context, owner: str, repo: str) -> None:
    """
    Create a pull request on GitHub for the specified repository.
    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
    Returns:
        None
    """

    title = inquirer.text("Enter the PR title")
    body = create_PR_body()
    assignee = get_assignee(ctx, owner, repo)

    ctx.run(f'gh pr create --base=main --title="{title}" --body="{body}" --assignee="{assignee}"')


def add_commit_submodule(ctx: Context, path):
    if os.path.exists(f"{path}"):
        os.chdir(f"{path}")
        if os.path.exists(".git"):
            ctx.run("git add .")
            ctx.run(f'git commit -m "Add {path} results"')
            os.chdir("..")
            ctx.run(f"git add {path}")
            print(f"{path} is added to the submodule")
        else:
            print(f"{path} is pushed to the main repository")
    else:
        print(f"{path} does not exist")


def add_experiment_notes(ctx: Context):
    """
    Prompts the user for details about an experiment and saves the notes to a YAML file.
    The function collects the following information from the user:
    - Hypothesis
    - Results
    - Conclusion
    - Risks related to data (optional)
    - Risks related to the model (optional)
    - Risks related to the code (optional)
    The notes are saved in a YAML file named with the current date and time.
    The function also commits and pushes the changes to the git submodules.
    Returns:
        None
    """

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

    author = ctx.run("git config user.name", hide=True, warn=True).stdout.strip()

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

    add_commit_submodule(ctx, "notes")


@task
def gacp(ctx: Context) -> None:
    """
    Automates the process of adding, committing, and pushing changes to a Git repository,
    and optionally creates a pull request.
    Args:
        ctx (Context): Context parameter used to run commands.
    Steps:
        1. Retrieves the owner and repository name.
        2. Gets the current Git branch.
        3. Stages all changes for commit.
        4. Prompts the user for the type of commit.
        5. Commits the changes with the specified commit type.
        6. Pushes the changes to the remote repository and sets the upstream branch.
        7. If the commit type is not "WIP", "exp", or "backup", prompts the user to create a pull request.
    """

    owner, repo = get_owner_repo(ctx)
    current_branch = git_current_branch(ctx)

    git_add(ctx)

    commit_type = get_commit_type()

    git_commit(ctx, commit_type)

    ctx.run(f"git push --set-upstream origin {current_branch}")

    if commit_type not in ["WIP", "exp", "backup"]:
        if inquirer.confirm("Create a PR?", default=True):
            create_pr(ctx, owner, repo)


namespace = Collection("git", gacp)
