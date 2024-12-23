from invoke import Program
from gtasks import setup_repo

program = Program(namespace=setup_repo.namespace)

if __name__ == "__main__":
    program.run()
