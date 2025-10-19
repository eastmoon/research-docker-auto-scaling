# Import libraries
import pkgutil
import os
import importlib
import types
import argparse

# Declare variable

# Declare function
def list_package_scripts(package_path):
    """Lists all Python scripts within a given package path."""
    scripts = []
    for importer, modname, ispkg in pkgutil.walk_packages([package_path]):
        if not ispkg:  # Only consider modules, not subpackages
            scripts.append(modname)
    return scripts

def commands(parser, command_name="commands"):
    """Import all command defined within a given package name."""
    subparser = parser.add_subparsers(title=command_name)
    package_directory = f"{os.environ['PYTHON_CLI_DIR']}/{command_name}"
    if os.path.exists(package_directory):
        all_scripts = list_package_scripts(package_directory)
        for script in all_scripts:
            module = importlib.import_module(f".{script}", package=f"{command_name}")
            if hasattr(module, "conf") and isinstance(module.exec, types.FunctionType):
                module.conf(subparser)

def conf(parser):
    ## command description
    if 'PYTHON_CLI_NAME' in os.environ: parser.prog=os.environ['PYTHON_CLI_NAME']
    parser.description='This is a command line interface for algorithm service project.'
    ## command options and description
    ## command process function
    parser.set_defaults(help=parser.print_help)

# Setting command-line interface
if 'PYTHON_CLI_DIR' not in os.environ: os.environ['PYTHON_CLI_DIR']=os.getcwd()
cli = argparse.ArgumentParser()
conf(cli)
commands(cli)

# Script entrypoint
if __name__ == '__main__':
    # Retrieve argument with argparse
    args = cli.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    elif hasattr(args, "help"):
        args.help()
