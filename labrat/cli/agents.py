import argparse
from urllib.parse import urlparse

from labrat.core.agent import Agent
from labrat.core.config import Config
from labrat.core.utils import print_table


def build_parser(subparser=None):
    parser = argparse.ArgumentParser("labrat agents") if subparser is None else subparser
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", aliases=["ls"], help="List GitLab servers")
    build_sub_parser(handle_list_args, list_parser)
    
    delete_parser = subparsers.add_parser("delete", aliases=["rm"], help="Delete GitLab server from config")
    build_sub_parser(handle_delete_args, delete_parser)

    add_key_parser = subparsers.add_parser("add-key", help="Add SSH key to the user account")
    build_add_key_parser(add_key_parser)

    return parser

def build_sub_parser(handle=None, subparser=None, prog=None):
    parser = argparse.ArgumentParser(prog) if subparser is None else subparser
    parser.add_argument("-a", "--all", action="store_true", required=False, help="All agents")
    parser.add_argument("-f", "--filter", required=False, help="Filter agents by substring")
    parser.set_defaults(func=handle)
    return parser

def build_add_key_parser(subparser=None, prog=None):
    parser = argparse.ArgumentParser(prog) if subparser is None else subparser
    parser.add_argument("-f", "--filter", required=False, help="Filter agents by substring")
    parser.add_argument("-t", "--title", required=False, default="Default Key", help="Title for the SSH key")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-k", "--key", required=False, help="Public SSH key to add")
    group.add_argument("-K", "--key-file", required=False, help="Path to public SSH key file")
    
    parser.set_defaults(func=handle_add_key_args)
    return parser

def handle_list_args(args):
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

def handle_add_key_args(args):
    if args.key:
        key = args.key
    elif args.key_file:
        with open(args.key_file, "r") as f:
            key = f.read().strip()

    config = Config()
    
    for section, agent in config.filter(args.filter):
        if agent.auth():
            try:
                agent.add_ssh_key(args.title, key)
                print(f"[+] Added SSH key to {section}")
            except Exception as e:
                print(f"[-] Failed to add SSH key to {section}: {e}")
        else:
            print(f"[-] Authentication failed for {section}")