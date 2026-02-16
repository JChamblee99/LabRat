from labrat.controllers.agents import Agents
from labrat.core.utils import parse_host_range

def build_parser(parsers):
    parser = parsers.add_parser("auth", help="Authenticate to GitLab server(s)")
    
    parser.add_argument("-t", "--target", required=False, help="GitLab server URL or pattern")
    parser.add_argument("-u", "--username", required=False, help="Username or e-mail for authentication")
    parser.add_argument("-p", "--password", required=False, help="Password for authentication")
    parser.add_argument("-C", "--combo-list", required=False, help="Path to the combo list file")
    parser.add_argument("-l", "--use-ldap", action="store_true", help="Use LDAP for authentication")
    parser.add_argument("-r", "--re-auth", action="store_true", help="Re-authenticate with stored credentials")

    parser.set_defaults(func=handle_args, _parser=parser)
    parser.set_defaults(controller=Agents())
    return parser

def handle_args(args):
    if args.re_auth:
        reauth(args)
    elif args.target and (args.username and args.password or args.combo_list):
        auth(args)
    else:
        getattr(args, "_parser", None).print_help()
        return

def reauth(args):
    for agent, err in args.controller.reauth(target=args.target, username=args.username):
        if err:
            print(f"[-] Re-authentication failed for {agent.label}: {err}")
        else:
            print(f"[+] Authenticated {agent.label} with {agent.private_token}")

def auth(args):
    # Build the list of users
    users = []
    if args.username and args.password:
        users = [(args.username, args.password)]
    elif args.combo_list:
        with open(args.combo_list, "r") as f:
            for line in f:
                username, password = line.strip().split(":")
                users.append((username, password))

    # Build the list of targets
    targets = parse_host_range(args.target)

    # Iterate over each user and target
    for agent, err in args.controller.auth(targets, users, use_ldap=args.use_ldap):
        if err:
            print(f"[-] Authentication failed for {agent.label}: {err}")
        else:
            print(f"[+] Authenticated {agent.label} {'(admin)' if agent.is_admin else ''} with {agent.private_token}")