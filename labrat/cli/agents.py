import argparse
from urllib.parse import urlparse

from labrat.cli import common
from labrat.core.agent import Agent
from labrat.core.config import Config


def build_parser(parsers):
    parser = parsers.add_parser("agents", help="Manage GitLab agents")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = common.add_filtered_parser(subparsers, "list", handle_list_args, aliases=["ls"], help="List GitLab servers", filter_required=False)
    
    delete_parser = common.add_filtered_parser(subparsers, "delete", handle_delete_args, aliases=["rm"], help="Delete GitLab server from config")

    add_key_parser = common.add_filtered_parser(subparsers, "add-key", handle_add_key_args, help="Add SSH key to the user account", filter_required=False)
    key_group = add_key_parser.add_mutually_exclusive_group(required=True)
    key_group.add_argument("-k", "--key", required=False, help="Public SSH key to add")
    key_group.add_argument("-K", "--key-file", required=False, help="Path to public SSH key file")

    add_key_parser.add_argument("-t", "--title", required=False, help="Title for the SSH key", default="SSH Key")

    return parser

def handle_list_args(args):
    config = Config()

    # Extract and sort sections by domain
    sorted_sections = sorted(
        config.sections(),  # Get all sections
        key=lambda section: urlparse(config[section].get("url", "")).netloc  # Extract domain
    )

    # Prepare table
    headers = ["Url", "Username", "Type", "Password", "Private Token"]
    data = []

    for section in sorted_sections:
        if section == "DEFAULT" or section == "global":
            continue
        
        domain = urlparse(config[section].get("url", "")).netloc
        data.append([
            config[section].get("url", ""),
            config[section].get("username", ""),
            "admin" if config[section].getboolean("is_admin", False) else "user",
            config[section].get("password", ""),
            config[section].get("private_token", "")
        ])

    # Filter data if filter argument is provided
    if args.filter:
        data = [row for row in data if any(args.filter in str(item) for item in row)]

    common.print_table(headers, data)

def handle_delete_args(args):
    config = Config()

    # Delete configs for filtered sections
    for section, _ in config.filter(args.filter):
        config.remove_section(section)
        print(f"[-] Deleted {section} from config")

def handle_add_key_args(args):
    if args.key:
        key = args.key
    elif args.key_file:
        with open(args.key_file, "r") as f:
            key = f.read().strip()

    config = Config()
    
    for section, agent in config.filter(args.filter):
        try:
            agent.auth()
            agent.add_ssh_key(args.title, key)
            print(f"[+] Added SSH key to {section}")
        except Exception as e:
            print(f"[-] Failed to add SSH key to {section}: {e}")