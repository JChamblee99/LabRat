from labrat.cli import common
from labrat.controllers.users import Users

def build_parser(parsers):
    parser = parsers.add_parser("users", help="Manage GitLab users")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = common.add_filtered_parser(subparsers, "list", handle_list_args, aliases=["ls"], help="List GitLab users", filter_required=False)

    create_token_parser = common.add_filtered_parser(subparsers, "create_token", handle_create_token_args, help="Create an access token", filter_required=True)
    create_token_parser.add_argument("-n", "--token-name", required=False, help="Name for the access token", default="private token")
    create_token_parser.add_argument("-s", "--scopes", required=False, help="Comma-separated list of scopes for the access token", default="api,read_repository,write_repository")


    parser.set_defaults(controller=Users())
    return parser

def handle_list_args(args):
    headers = ["Host", "ID", "Username", "Name", "Is Agent", "Is Admin", "Is Bot"]
    data = []

    for user in args.controller.list(filter=args.filter):
        data.append([
            user.host,
            user.id,
            user.username,
            user.name,
            getattr(user, "is_agent", "-"),
            getattr(user, "is_admin", "-"),
            getattr(user, "bot", "-")
        ])

    common.print_table(headers, data, "Host")

def handle_create_token_args(args):
    for agent, err in args.controller.create_token(args.token_name, args.scopes.split(","), filter=args.filter):
        if err:
            print(f"[-] Failed to create access token: {err}")
        else:
            print(f"[+] Created access token for {agent.label}: {agent.private_token}")
