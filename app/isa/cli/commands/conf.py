# Import libraries
import os
import sys
import enum
import glob
from conf import attributes
from conf import infrastructures as infra

# Declare variable

# Declare function
def conf(parser):
    ## command description
    new_parser = parser.add_parser('conf', help='Setting configuration file', description=f"Configuration a module with JSON or YAML string.")
    ## command options and description
    new_parser.add_argument("config", nargs='?', default="default", help="Which configuration file need assigned to. Default assign to 'default.yml'")
    new_parser.add_argument("module", nargs='?', default="default", help="Which module is the configuration assigned to.")
    new_parser.add_argument("-m", "--methods", type=Methods, help=f"Method to perform on the process. {[m.value for m in Methods]}")
    new_parser.add_argument("-i", "--interactive", action='store_true', help="read JSON string from STDIN.")
    new_parser.add_argument("-f", "--file", help="read JSON string from target file.")
    ## command process function
    new_parser.set_defaults(func=exec, helper=new_parser.print_help)

def exec(args):
    ## Create configuration file object
    c = infra.Config(args.config)
    ## Process configuration file with method
    match args.methods:
        case Methods.LIST:
            ### Show all configuration file in conf folder
            files = glob.glob("*.yml", root_dir=f"{attributes.APP_C_DIR}")
            for file in files:
                print(os.path.splitext(file)[0])
        case Methods.GET:
            ### Read configuration file content.
            c.read(module=args.module)
        case Methods.POST:
            ### Update content into configuration file.
            ### The content source could come from stdin or file.
            if args.interactive:
                c.write(module=args.module, data=sys.stdin.read())
            elif args.file != None:
                c.write(module=args.module, path=args.file)
        case Methods.DELETE:
            ### Remove content in configuration file.
            c.delete(module=args.module)

# Declare class
class Methods(enum.Enum):
    LIST = "list"
    GET = "get"
    POST = "post"
    DELETE = "del"
