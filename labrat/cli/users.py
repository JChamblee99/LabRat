import argparse
from urllib.parse import urlparse

import gitlab

from labrat.cli import common
from labrat.core.agent import Agent
from labrat.core.config import Config


def build_parser(parsers):
    parser = parsers.add_parser("users", help="Manage GitLab users")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = common.add_filtered_parser(subparsers, "list", handle_list_args, aliases=["ls"], help="List GitLab users", filter_required=False)

    create_pat_parser = common.add_filtered_parser(subparsers, "create_pat", handle_create_pat_args, help="Create a personal access token", filter_required=True)

    return parser

def handle_list_args(args):
    config = Config()
    sections = config.sections()

    # Get a list of all users
    headers = ["Target", "Username", "Agent", "Type"]
    data = dict()

    for section, agent in config:
        try:
            agent.auth()
        except Exception as e:
            continue

        hostname = urlparse(agent.url).hostname
        users = agent.gitlab.users.list(all=True)

        for user in users:
            sect = f"{user.username}@{hostname}"

            # Determine account type
            if agent.is_admin:
                type = "admin" if user.is_admin else "bot" if user.bot else "user"
            elif sect == section:
                type = "bot" if agent.gitlab.user.bot else "user"
            else:
                type = "-"

            # Add user data to the list
            if sect not in data.keys() or agent.is_admin or sect == section:
                data[sect] = [
                    agent.url,
                    user.username,
                    sect in sections,
                    type
                ]

    # Transform data
    data = [item for item in data.values()]

    # Filter data if filter argument is provided
    if args.filter:
        data = [row for row in data if any(args.filter in str(item) for item in row)]

    common.print_table(headers, data)

def handle_create_pat_args(args):
    config = Config()
    sections = config.sections()

    for section, agent in config:
        try:
            agent.auth()
        except Exception as e:
            continue

        if agent.is_admin:
            users = agent.gitlab.users.list(all=True)
            for user in users:
                sect = f"{user.username}@{urlparse(agent.url).hostname}"
                if sect not in sections:
                    try:
                        token = agent.create_pat(user_id=user.id)
                        agent_user = Agent(agent.url, username=user.username, private_token=token)
                        config[sect] = agent_user.to_dict()
                        print(f"[+] Authenticated as {sect} ({'admin' if agent_user.is_admin else 'user'}) with {agent_user.private_token}")
                    except Exception as e:
                        print(f"[!] Failed to create PAT for {sect}: {e}")
