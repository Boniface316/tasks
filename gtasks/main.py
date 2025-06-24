from invoke import (
    Collection,
    Program,
)

from .branch import (
    namespace as branch_namespace,
)
from .checks import (
    namespace as checks_namespace,
)
from .cleans import (
    namespace as cleans_namespace,
)
from .containers import (
    namespace as containers_namespace,
)
from .docs import (
    namespace as docs_namespace,
)
from .formats import (
    namespace as formats_namespace,
)
from .git import (
    namespace as git_namespace,
)
from .installs import (
    namespace as installs_namespace,
)
from .issues import (
    namespace as issues_namespace,
)
from .projects import (
    namespace as projects_namespace,
)
from .setup_repo import (
    namespace as setup_namespace,
)

# Create a root collection and add both namespaces directly
ns = Collection()
ns.add_collection(setup_namespace, "setup")  # Add repo tasks directly to root
ns.add_collection(issues_namespace)  # Add issues tasks directly to root
ns.add_collection(git_namespace)  # Add repo tasks directly to root
ns.add_collection(branch_namespace)  # Add branch tasks directly to root
ns.add_collection(containers_namespace)  # Add containers tasks directly to root
ns.add_collection(cleans_namespace)  # Add cleans tasks directly to root
ns.add_collection(checks_namespace)  # Add checks tasks directly to root
ns.add_collection(docs_namespace)  # Add docs tasks directly to root
ns.add_collection(projects_namespace)  # Add projects tasks directly to root
ns.add_collection(formats_namespace)  # Add formats tasks directly to root
ns.add_collection(installs_namespace)  # Add installs tasks directly to root

# Create an Invoke program with the defined namespace
program = Program(namespace=ns)

if __name__ == "__main__":
    program.run()
