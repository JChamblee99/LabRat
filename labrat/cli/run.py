import argparse
from urllib.parse import urlparse

from labrat.cli import common
from labrat.core.agent import Agent
from labrat.core.config import Config

def build_parser(parsers):
    parser = common.add_filtered_parser(parsers, "run", handle_args, help="Execute CI/CD job")
    parser.add_argument("command", help="Command to execute on the CI/CD job")

    return parser

def handle_args(args):
    getattr(args, "_parser", None).print_help()
    
