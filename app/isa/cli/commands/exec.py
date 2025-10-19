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
    new_parser = parser.add_parser('exec', help='Execute configuration file', description=f"Execute infrastructure module with target configuration file.")
    ## command options and description
    new_parser.add_argument("file", nargs='?', default="default", help="Which configuration file need execute. Default execute 'default.yml'")
    ## command process function
    new_parser.set_defaults(func=exec, helper=new_parser.print_help)

def exec(args):
    ## Create configuration file object
    c = infra.Config(args.file).load()
    ## Get execute order
    ## if configuration file has 'global' module and "flow" key, it mean flow use with it, otherwise flow equal module name sort.
    keys = []
    if "global" in c and "flow" in c["global"]:
        keys = c["global"]["flow"]
    else:
        keys = [m for m in c]
        keys.sort()
    ## Translate attribute module to dict object.
    attr_dict = {}
    for key in dir(attributes):
        attr = getattr(attributes, key)
        if not callable(key) and not key.startswith('__'):
            attr_dict[key] = attr
    ##
    for module in keys:
        try:
            module_name = module
            if isinstance(c[module], dict) and "module" in c[module]:
                module_name = c[module]["module"]
            m = infra.Module(module_name)
            c[module]['sys.attributes'] = attr_dict
            c[module]['sys.manager'] = infra.Manager()
            m.exec(c[module])
        except Exception as e:
            print(f"An error occurred: {e}")
