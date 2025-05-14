import argparse
from urllib.parse import urlparse

from labrat.core.agent import Agent
from labrat.core.config import Config
from labrat.core.utils import print_table


def build_parser(subparser=None):
    parser = argparse.ArgumentParser("labrat agents") if subparser is None else subparser
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="List GitLab servers")
    build_sub_parser(handle_list_args, list_parser)
    
    delete_parser = subparsers.add_parser("delete", help="Delete GitLab server from config")
    build_sub_parser(handle_delete_args, delete_parser)
    return parser

def build_sub_parser(handle=None, subparser=None, prog=None):
    parser = argparse.ArgumentParser(prog) if subparser is None else subparser
    parser.add_argument("-a", "--all", action="store_true", required=False, help="All agents")
    parser.add_argument("-f", "--filter", required=False, help="Filter agents by substring")
    parser.set_defaults(func=handle)
    return parser

def handle_list_args(args):
    if not args.all and not args.filter:
        build_sub_parser(handle_delete_args, prog="labrat agents list").print_help()
        return
    config = Config()

    # Extract and sort sections by domain
    sorted_sections = sorted(
        config.sections(),  # Get all sections
        key=lambda section: urlparse(config[section].get("url", "")).netloc  # Extract domain
    )

    # Prepare table
    headers = ["Url", "Username", "Type", "Private Token"]
    data = []

    for section in sorted_sections:
        if section == "DEFAULT" or section == "global":
            continue
        
        domain = urlparse(config[section].get("url", "")).netloc
        data.append([
            config[section].get("url", ""),
            config[section].get("username", ""),
            "admin" if config[section].getboolean("is_admin", False) else "user",
            config[section].get("private_token", "")
        ])

    # Filter data if filter argument is provided
    if args.filter:
        data = [row for row in data if any(args.filter in str(item) for item in row)]

    print_table(headers, data)

def handle_delete_args(args):
    if not args.all and not args.filter:
        build_sub_parser(handle_delete_args, prog="labrat agents delete").print_help()
        return

    config = Config()

    # Delete configs for filtered sections
    for section in config.sections():
        if section == "DEFAULT" or section == "global":
            continue

        type = "admin" if config[section].getboolean("is_admin", False) else "user"
        if args.filter not in section and args.filter not in type and args.filter not in config[section].get("private_token", ""):
            continue
        config.remove_section(section)
        print(f"[-] Deleted {section} from config")

    return