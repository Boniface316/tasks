# GTasks

GTasks is a Python package that provides a set of Invoke tasks for managing GitHub repositories. It includes tasks for managing issues, branches, commits, and repository setup.

## Installation

To install the package, run:

### Option 1: Install via pipx or uvx

```sh
pipx install git+https://github.com/Boniface316/tasks.git
```

or

```sh
uvx pip install gtasks git+https://github.com/Boniface316/tasks.git
```

### Option 2: Clone and install

```sh
git clone https://github.com/yourusername/gtasks.git
cd gtasks
pip install .
```

## Usage

To view the list of subcommands run `gtasks --list` and it will provide a list of subcommands and short summary of them in the following manner:

```sh
❯ gtasks --list
Subcommands:

    branch.new     Create a new branch based on a GitHub issue.
    git.gacp       Automates the process of adding, committing, and pushing changes to a Git repository.
    issues.close   Close an issue.
    issues.list    List the open issues assigned to the user.
    issues.new     Create a new issue.
    setup.labels   Set up the labels in the repository.
```

If you want to get more details on a particular subcommand, use --help. i.e:

```sh
❯ gtasks --help branch.new
Usage: gtasks [--core-opts] branch.new [--options] [other tasks here ...]

Docstring:
    Create a new branch based on a GitHub issue.
    This function interacts with the GitHub CLI to create a new branch based on the provided issue ID.
    If no issue ID is provided, it prompts the user to enter one. It then retrieves the labels of the issue,
    constructs a branch name, and creates a new branch based on the issue.
    Args:
            issue_id (int, optional): The ID of the GitHub issue. If not provided, the user will be prompted to enter it.
    Returns:
            None

Options:
    -i STRING, --issue-id=STRING   The ID of the issue to create a branch from. If not provided, use `gtasks issues.list` to get the issue ID.

```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.