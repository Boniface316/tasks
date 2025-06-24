from invoke import run


def get_owner_repo() -> tuple:
    """
    Get the owner and repository name.
    This function uses the `gh` command to retrieve the owner and repository name.
    Returns:
        tuple: A tuple containing the owner and repository name.
    """
   
    owner = run(
            "gh repo view --json owner --jq '.owner.login'",
            hide=True,
        ).stdout.strip()

    repo = run(
            "gh api repos/:owner/:repo -q .name",
            hide=True,
        ).stdout.strip()

    return (
        owner,
        repo,
    )
