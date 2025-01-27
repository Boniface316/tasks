"""Documentation tasks of the project."""

# %% IMPORTS

from invoke import (
    Collection,
)
from invoke.context import (
    Context,
)
from invoke.tasks import (
    task,
)

from . import (
    cleans,
)

# %% CONFIGS

DOC_FORMAT = "google"
OUTPUT_DIR = "docs/"

# %% TASKS


@task
def serve(
    ctx: Context,
    package: str,
    format: str = DOC_FORMAT,
    port: int = 8088,
) -> None:
    """Serve the API docs with pdoc."""
    ctx.run(f"uv run pdoc --docformat={format} --port={port} src/{package}")


@task
def api(
    ctx: Context,
    package: str,
    format: str = DOC_FORMAT,
    output_dir: str = OUTPUT_DIR,
) -> None:
    """Generate the API docs with pdoc."""
    ctx.run(f"uv run pdoc --docformat={format} --output-directory={output_dir} src/{package}")


@task(
    pre=[cleans.docs],
    default=True,
    help={
        "package": "The package to generate the docs.",
        "format": "The format of the docs.",
        "output_dir": "The output directory of the docs.",
    },
)
def all(
    ctx: Context,
    package: str,
    format: str = DOC_FORMAT,
    output_dir: str = OUTPUT_DIR,
) -> None:
    """Run all docs tasks."""
    api(
        ctx,
        package,
        format,
        output_dir,
    )
    serve(
        ctx,
        package,
        format,
    )


# %% COLLECTION
namespace = Collection(
    "docs",
    all,
    api,
    serve,
)
