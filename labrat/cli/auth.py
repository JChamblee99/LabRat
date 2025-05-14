import argparse
from urllib.parse import urlparse
from labrat.core.agent import Agent
from labrat.core.config import Config
from labrat.core.utils import parse_host_range

def build_parser(subparser=None):
    parser = argparse.ArgumentParser("labrat auth") if subparser is None else subparser
    parser.add_argument("-t", "--target", required=False, help="GitLab server URL or pattern")
    parser.add_argument("-u", "--username", required=False, help="Username or e-mail for authentication")
    parser.add_argument("-p", "--password", required=False, help="Password for authentication")
    parser.add_argument("-C", "--combo-list", required=False, help="Path to the combo list file")
    parser.add_argument("-l", "--use-ldap", action="store_true", help="Use LDAP for authentication")
    parser.add_argument("-r", "--re-auth", action="store_true", help="Re-authenticate with stored credentials")

    parser.set_defaults(func=handle_args)
    return parser

def handle_args(args):
    if args.re_auth:
        reauth(args)
    elif args.target and (args.username and args.password or args.combo_list):
        auth(args)
    else:
        build_parser().print_help()
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

        if agent.auth():
            print(f"[+] Authenticated as {section} with {agent.private_token}")
            config[section] = agent.to_dict()
            continue
        elif agent.username and agent.password:
            print(f"[-] Authentication failed for {section}, re-authenticating...")
            agent.login()
            token = agent.create_pat()
            if token and agent.auth(private_token=token):
                print(f"[+] Re-authenticated as {section} with {agent.private_token}")
                config[section] = agent.to_dict()
                continue

        print(f"[-] Re-authentication failed for {section}")

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

                if agent.auth():
                    print(f"[*] Authenticated as {section} with {agent.private_token}")
                    config[section] = agent.to_dict()
                    continue
                else:
                    print(f"[-] Authentication failed for {section}, re-authenticating...")

            agent = Agent(target)
            agent.login(username, password, use_ldap=args.use_ldap)
            token = agent.create_pat()
            if token and agent.auth(private_token=token):
                print(f"[*] Authenticated as {section} ({'admin' if agent.is_admin else 'user'}) with {token}")
                config[section] = agent.to_dict()
                continue
            else:
                print(f"[-] Authentication failed for {section}")
