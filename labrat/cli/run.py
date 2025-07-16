import argparse
from urllib.parse import urlparse

from labrat.core.agent import Agent
from labrat.core.config import Config
from labrat.core.utils import print_table

def build_parser(subparser=None):
    parser = argparse.ArgumentParser("labrat run") if subparser is None else subparser
    parser.add_argument("-a", "--all", action="store_true", required=False, help="All agents")
    parser.add_argument("-f", "--filter", required=False, help="Filter agents by substring")
    parser.add_argument("command", help="Command to execute on the CI/CD job")
    parser.set_defaults(func=handle_args)
    return parser

def handle_args(args):
    if not args.all and not args.filter:
        build_parser().print_help()
        return
    
