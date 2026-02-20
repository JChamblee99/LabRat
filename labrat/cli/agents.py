from labrat.cli import common
from labrat.controllers.agents import Agents


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

    parser.set_defaults(controller=Agents())
    return parser

def handle_list_args(args):
    # Prepare table
    headers = ["Host", "ID", "Username", "Name", "Authenticated", "Is Admin", "Is Bot", "Password", "Private Token"]
    data = []

    for agent in args.controller.list(args.filter):
        data.append([
            agent.host,
            agent.id,
            agent.username,
            agent.gitlab.user.name if agent.is_authenticated else "-",
            agent.is_authenticated,
            agent.is_admin,
            agent.is_bot,
            agent.password,
            agent.private_token
        ])

    common.print_table(headers, data, "Host")

def handle_delete_args(args):
    # Delete configs for filtered sections
    for agent in args.controller.delete(args.filter):
        print(f"[-] Deleted {agent.label} from config")

def handle_add_key_args(args):
    # Prepare SSH key
    if args.key:
        key = args.key
    elif args.key_file:
        with open(args.key_file, "r") as f:
            key = f.read().strip()

    # Add SSH key to agents
    for agent, err in args.controller.add_ssh_key(args.filter, args.title, key):
        if err:
            print(f"[-] Failed to add SSH key to {agent.label}: {err}")
        else:
            print(f"[+] Added SSH key to {agent.label}")