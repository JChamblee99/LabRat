import argparse
from urllib.parse import urlparse

from labrat.core.agent import Agent
from labrat.core.config import Config
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
    config = Config()
    
    # Iterate config sections and re-authenticate
    for section, agent in config:
        # Filter by target if specified
        if args.target and args.target not in agent.url:
            continue

        # Filter by username if specified
        if args.username and args.username != agent.username:
            continue

        try:
            agent.auth()
            config[section] = agent.to_dict()
            print(f"[+] Authenticated as {section} with {agent.private_token}")
            continue
        except Exception as e:
            pass

        try:
            agent.login()
            agent.auth(private_token=agent.create_pat())
            config[section] = agent.to_dict()
            print(f"[+] Authenticated as {section} with {agent.private_token}")
            continue
        except Exception as e:
            print(f"[-] Re-authentication failed for {section}: {e}")

def auth(args):
    config = Config()

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
    for username, password in users:
        for target in targets:
            domain = urlparse(target).hostname
            section = f"{username}@{domain}"

            c = config[section]
            if c:
                agent = Agent.from_dict(c)

                try:
                    agent.auth()
                    print(f"[*] Authenticated as {section} with {agent.private_token}")
                    config[section] = agent.to_dict()
                    continue
                except Exception as e:
                    pass

            try:
                agent = Agent(target)
                agent.login(username, password, use_ldap=args.use_ldap)
                agent.auth(private_token=agent.create_pat())
                config[section] = agent.to_dict()
                print(f"[*] Authenticated as {section} ({'admin' if agent.is_admin else 'user'}) with {agent.private_token}")
                continue
            except Exception as e:
                print(f"[-] Authentication failed for {section}: {e}")
