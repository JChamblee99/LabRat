import argparse
from urllib.parse import urlparse

import gitlab

from labrat.cli import common
from labrat.core.agent import Agent
from labrat.core.config import Config

from labrat.controllers.users import Users


def build_parser(parsers):
    parser = parsers.add_parser("users", help="Manage GitLab users")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = common.add_filtered_parser(subparsers, "list", handle_list_args, aliases=["ls"], help="List GitLab users", filter_required=False)

    create_pat_parser = common.add_filtered_parser(subparsers, "create_pat", handle_create_pat_args, help="Create a personal access token", filter_required=True)

    parser.set_defaults(controller=Users())
    return parser

def handle_list_args(args):
    headers = ["Url", "ID", "Username", "Name", "Is Agent", "Is Admin", "Is Bot"]
    data = []

    for user in args.controller.list(filter=args.filter):
        data.append([
            user.url,
            user.id,
            user.username,
            user.name,
            getattr(user, "is_agent", "-"),
            getattr(user, "is_admin", "-"),
            getattr(user, "bot", "-")
        ])

    common.print_table(headers, data, "Url")

def handle_create_pat_args(args):
    for agent, err in args.controller.create_pat(filter=args.filter):
        if err:
            print(f"[-] Failed to create PAT: {err}")
        else:
            print(f"[+] Created PAT for {agent.label}: {agent.private_token}")
