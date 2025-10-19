# Import libraries
import os
import glob
from conf import attributes
from conf import infrastructures as infra

# Declare variable

# Declare function
def conf(parser):
    ## command description
    new_parser = parser.add_parser('list', help='List moduels or show module description.', description=f"List all module in '{attributes.APP_M_DIR}', or give module name to show single module description.")
    ## command options and description
    new_parser.add_argument('module', nargs='?', help='Infrastructure module name.')
    ## command process function
    new_parser.set_defaults(func=exec, helper=new_parser.print_help)

def exec(args):
    try:
        if args.module == None:
            print("Module list:")
            # For recursive search, use '**' and set recursive=True
            ## Search all python file in application directories
            files = glob.glob("*.py", root_dir=f"{attributes.APP_M_DIR}")
            for file in files:
                m = infra.Module(os.path.splitext(file)[0])
                m.short()
            ## Search all main.py in application sub-directories
            files = glob.glob("*/main.py", root_dir=f"{attributes.APP_M_DIR}")
            for file in files:
                m = infra.Module(os.path.dirname(file))
                m.short()
        else:
            m = infra.Module(args.module)
            m.desc()
    except Exception as e:
        print(f"An error occurred: {e}")
