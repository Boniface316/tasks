"""Container tasks of the project."""

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

from . import (
    packages,
)
from .base import (
    get_owner_repo,
)

# %% CONFIGS

IMAGE_TAG = "latest"

# %% TASKS


@task(
    pre=[packages.build],
    help={"tag": "The tag of the image"},
)
def build(
    ctx: Context,
    tag: str = IMAGE_TAG,
) -> None:
    """Build the container image."""
    (
        _,
        project,
    ) = get_owner_repo()
    ctx.run(f"docker build --tag={project}:{tag} .")


@task(
    help={
        "tag": "The tag of the image",
        "port": "The port to expose",
        "gpus": "The number of GPUs to use",
        "source": "The source directory to mount",
        "dest": "The destination directory to mount",
    }
)
def run(
    ctx: Context,
    tag: str = IMAGE_TAG,
    port: str | None = None,
    gpus: str | None = None,
    source: str | None = None,
    dest: str | None = None,
    open_browser: str = False, 
) -> None:
    """Run the container image."""
    command = "docker run --rm -it "
    if port:
        command += f"-p {port}:{port} "
    if gpus:
        command += f"--gpus {gpus} "
    if source and dest:
        command += f"-v {source}:{dest} "
    (
        _,
        project,
    ) = get_owner_repo()
    command += f"{project}:{tag}"
    ctx.run(command)
    if open_browser:
        ctx.run(f'open -a "Google Chrome" http://localhost:{port}')


@task(
    help={
        "source": "The source directory to mount",
        "dest": "The destination directory to mount (default: /mlruns)",
        "port": "The port to expose (default: 5000)",
        "mlflow_version": "The version of MLflow docker image to use (default: v2.19.0)",
    }
)
def mlserver(
    ctx: Context,
    source: str = "mlruns",
    dest: str = "mlruns",
    port: int = 5000,
    mlflow_version: str = "v2.19.0",
) -> None:
    """Run the MLflow server."""
    source = os.getcwd() + "/" + source
    ctx.run(
        f"docker run -p {port}:{port} -e MLFLOW_HOST=0.0.0.0 -v {source}:/{dest} ghcr.io/mlflow/mlflow:{mlflow_version} mlflow server --backend-store-uri /{dest}"
    )
    ctx.run(f'open -a "Google Chrome" http://localhost:{port}')


@task(
    pre=[
        build,
        run,
    ],
    default=True,
)
def all(
    _: Context,
) -> None:
    """
    Build and run will be executed in sequence.

    Parameters:
        project: The name of the project
        tag: The tag of the image
        port: The port to expose
        gpus: The number of GPUs to use
        source: The source directory to mount
        dest: The destination directory to mount
    """


namespace = Collection(
    "containers",
    build,
    run,
    mlserver,
    all,
)
