# Import libraries
import os
import glob
import shutil
import subprocess
from conf import attributes
from conf import infrastructures as infra

# Declare variable

# Declare function
def conf(parser):
    ## command description
    new_parser = parser.add_parser('infra', help='Manage the Docker Compose.', description=f"Manage the Docker Compose to which the current container belongs.")
    subparsers = new_parser.add_subparsers(title="commands")
    ## command options and description
    ## command process function
    new_parser.set_defaults(func=exec, helper=new_parser.print_help)
    ## Subcommand : ps
    ps_parser = subparsers.add_parser("ps", help="List containers information")
    ps_parser.set_defaults(func=exec_ps, helper=ps_parser.print_help)
    ## Subcommand : stats
    stats_parser = subparsers.add_parser("stats", help="Display container(s) resource usage statistics")
    stats_parser.set_defaults(func=exec_stats, helper=stats_parser.print_help)
    ## Subcommand : start
    start_parser = subparsers.add_parser("start", help="Start services, but not include isa service.")
    start_parser.set_defaults(func=exec_start, helper=start_parser.print_help)
    ## Subcommand : stop
    stop_parser = subparsers.add_parser("stop", help="Stop services, but not include isa service.")
    stop_parser.set_defaults(func=exec_stop, helper=stop_parser.print_help)
    ## Subcommand : restart
    restart_parser = subparsers.add_parser("restart", help="Restart target services.")
    restart_parser.add_argument('service', help='Target service name.')
    restart_parser.set_defaults(func=exec_restart, helper=restart_parser.print_help)

def exec(args):
    try:
        infra.Manager.env_check()
    except Exception as e:
        print(f"An error occurred: {e}")

def exec_ps(args):
    try:
        m = infra.Manager()
        m.ps()
    except Exception as e:
        print(f"An error occurred: {e}")

def exec_stats(args):
    try:
        m = infra.Manager()
        m.stats()
    except Exception as e:
        print(f"An error occurred: {e}")

def exec_start(args):
    try:
        m = infra.Manager()
        m.start()
    except Exception as e:
        print(f"An error occurred: {e}")

def exec_stop(args):
    try:
        m = infra.Manager()
        m.stop()
    except Exception as e:
        print(f"An error occurred: {e}")

def exec_restart(args):
    try:
        m = infra.Manager()
        m.restart(args.service)
    except Exception as e:
        print(f"An error occurred: {e}")
