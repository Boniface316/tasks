from invoke import Program, Collection
from .setup_repo import namespace as setup_namespace
from .issues import namespace as issues_namespace
from .repo import namespace as repo_namespace
from .branch import namespace as branch_namespace

# Create a root collection and add both namespaces directly
ns = Collection()
ns.add_collection(setup_namespace)  # Add repo tasks directly to root
ns.add_collection(issues_namespace)  # Add issues tasks directly to root
ns.add_collection(repo_namespace)  # Add repo tasks directly to root
ns.add_collection(branch_namespace)  # Add branch tasks directly to root

# Create an Invoke program with the defined namespace
program = Program(namespace=ns)

if __name__ == "__main__":
    program.run()
