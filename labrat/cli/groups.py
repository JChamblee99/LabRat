import datetime

import gitlab

from labrat.cli import common
from labrat.controllers.groups import Groups

def build_parser(parsers):
    parser = parsers.add_parser("groups", help="Manage GitLab groups")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = common.add_filtered_parser(subparsers, "list", handle_list_args, aliases=["ls"], help="List GitLab groups", filter_required=False)
    list_parser.add_argument("-m", "--min-access-level", required=False, type=int, help="Minimum access level to filter groups", default=0)
    list_parser.add_argument("-u", "--user", action="append", required=False, help="Filter agent performing action")

    create_token_parser = common.add_filtered_parser(subparsers, "create_token", handle_create_token_args, help="Create an access token", filter_required=True)
    create_token_parser.add_argument("-l", "--access-level", required=False, type=int, help="Access level for the access token", default=50)
    create_token_parser.add_argument("-d", "--days", required=False, type=int, help="Number of days until the token expires", default=60)
    create_token_parser.add_argument("-n", "--token-name", required=False, help="Name for the access token", default="project_bot")
    create_token_parser.add_argument("-s", "--scopes", required=False, help="Comma-separated list of scopes for the access token", default="api,read_repository,write_repository")
    create_token_parser.add_argument("-u", "--user", action="append", required=False, help="Filter agent performing action")


    parser.set_defaults(controller=Groups())
    return subparsers

def handle_list_args(args):
    headers = ["Host", "ID", "Name", "Access Level", "Agents"]
    data = []

    for group in args.controller.list(args.filter, args.user):
        # color each username by that agent's access level (higher -> brighter)
        usernames = []
        for agent in group.agents:
            colored_username = common.color_access_level(agent.access_level, f"{agent.username} ({agent.access_level})")
            usernames.append(colored_username)
        
        # Add group information to data table
        data.append([
            group.host,
            group.id,
            group.name,
            f"{group.access_level} ({gitlab.const.AccessLevel(group.access_level).name.lower()})",
            ", ".join(usernames)
        ])

    common.print_table(headers, data)

def handle_create_token_args(args):
    expiration = (datetime.datetime.now() + datetime.timedelta(days=args.days)).strftime("%Y-%m-%d")
    for group, agent, err in args.controller.create_token(args.token_name, args.access_level, args.scopes.split(","), expiration, args.user, args.filter):
        if err:
            print(f"[!] Failed to create access token for {group.web_url}: {err}")
        else:
            print(f"[+] Successfully created access token for {group.web_url}: {agent.private_token}")