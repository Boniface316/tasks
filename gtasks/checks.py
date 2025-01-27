"""Check tasks of the project."""

# %% IMPORTS
import os

from invoke import (
    Collection,
)
from invoke.context import (
    Context,
)
from invoke.tasks import (
    task,
)

# %% TASKS


def available_folders(
    _: Context,
    folders: list[str],
) -> str:
    """Check if the folders exist."""
    existing_folders = [f"{folder}/" for folder in folders if os.path.exists(folder)]
    return " ".join(existing_folders)


@task
def format(
    ctx: Context,
) -> None:
    """Check the formats with ruff."""
    folders = [
        "src",
        "tasks",
        "tests",
    ]
    folders = available_folders(
        ctx,
        folders,
    )
    ctx.run(f"uv run ruff format --check {folders}")


@task
def type(
    ctx: Context,
) -> None:
    """Check the types with mypy."""
    folders = [
        "src",
        "tasks",
        "tests",
    ]
    ctx.run(f"uv run mypy {folders}")


@task
def code(
    ctx: Context,
) -> None:
    """Check the codes with ruff."""
    folders = [
        "src",
        "tasks",
        "tests",
    ]
    ctx.run(f"uv run ruff check {folders}")


@task
def test(
    ctx: Context,
) -> None:
    """Check the tests with pytest."""
    if os.path.exists("tests/"):
        ctx.run("uv run pytest --numprocesses=auto tests/")
    else:
        print("No tests folder found.")


@task
def security(
    ctx: Context,
) -> None:
    """Check the security with bandit."""
    ctx.run("uv run bandit --recursive --configfile=pyproject.toml src/")


@task
def coverage(
    ctx: Context,
) -> None:
    """Check the coverage with coverage."""
    ctx.run("uv run pytest --numprocesses=auto --cov=src/ --cov-fail-under=80 tests/")


@task(
    pre=[
        format,
        type,
        code,
        security,
        coverage,
    ],
    default=True,
)
def all(
    _: Context,
) -> None:
    """Run all check tasks. This includes format, type, code, test, security, and coverage."""


namespace = Collection(
    "checks",
    format,
    type,
    code,
    test,
    security,
    coverage,
    all,
)
