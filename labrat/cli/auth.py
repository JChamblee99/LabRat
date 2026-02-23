from labrat.controllers.agents import Agents
from labrat.core.utils import parse_host_range

def build_parser(parsers):
    parser = parsers.add_parser("auth", help="Authenticate to GitLab server(s)")

    parser.add_argument("-t", "--target", required=False, nargs="+", action="append", help="GitLab server URL or pattern")
    parser.add_argument("-T", "--target-file", required=False, help="Path to file containing GitLab server URLs or patterns")
    parser.add_argument("-u", "--username", required=False, help="Username or e-mail for authentication")
    parser.add_argument("-p", "--password", required=False, help="Password for authentication")
    parser.add_argument("-C", "--combo-list", required=False, help="Path to the combo list file")
    parser.add_argument("-l", "--use-ldap", action="store_true", help="Use LDAP for authentication")
    parser.add_argument("-r", "--re-auth", action="store_true", help="Re-authenticate with stored credentials")

    parser.set_defaults(func=handle_args, _parser=parser)
    parser.set_defaults(controller=Agents())
    return parser

def handle_args(args):
    has_targets = args.target or args.target_file
    has_credentials = (args.username and args.password) or args.combo_list
    can_auth = has_targets and has_credentials

    if args.re_auth or can_auth:
        auth(args)
    else:
        getattr(args, "_parser", None).print_help()
        return

def auth(args):
    # Build the list of users
    users = []
    if args.username:
        users = [(args.username, args.password)]
    elif args.combo_list:
        with open(args.combo_list, "r") as f:
            for line in f:
                username, password = line.strip().split(":")
                users.append((username, password))

    # Build the list of targets
    targets = []
    if args.target:
        target_args = [target for sublist in args.target for target in sublist]
        for target in target_args:
            targets.extend(parse_host_range(target))
    elif args.target_file:
        with open(args.target_file, "r") as f:
            for line in f:
                targets.extend(parse_host_range(line.strip()))

    # Iterate over each user and target
    for agent, err in args.controller.reauth(targets=targets, users=[user[0] for user in users]) if args.re_auth else args.controller.auth(targets, users, use_ldap=args.use_ldap):
        if err:
            print(f"[-] Authentication failed for {agent.label}: {err}")
        else:
            print(f"[+] Authenticated {agent.label}{' (admin)' if agent.is_admin else ''} with {agent.private_token}")