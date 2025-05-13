
import argparse
import re
from urllib.parse import urlparse
from labrat.core.agent import Agent
from labrat.core.config import Config


def build_parser(subparser=None):
    parser = argparse.ArgumentParser("labrat projects") if subparser is None else subparser
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="List GitLab projects")
    build_sub_parser(handle_list_args, list_parser)
    
    clone_parser = subparsers.add_parser("clone", help="Clone GitLab repositories")
    build_sub_parser(handle_clone_args, clone_parser)
    return parser

def build_sub_parser(handle=None, subparser=None, prog=None):
    parser = argparse.ArgumentParser(prog) if subparser is None else subparser
    parser.add_argument("-a", "--all", action="store_true", required=False, help="All projects")
    parser.add_argument("-f", "--filter", required=False, help="Filter for project names")
    parser.add_argument("-t", "--target", required=False, help="GitLab server URL or pattern")
    parser.add_argument("-u", "--username", required=False, help="Username or e-mail for authentication")
    parser.set_defaults(func=handle)
    return parser

def handle_list_args(args):
    # If no arguments are provided, show help
    if not args.all and not args.filter and not args.target and not args.username:
        build_sub_parser(handle_list_args).print_help()
        return

    # Dictionary to store repositories and their associated users
    repo_map = {}

    # Iterate through the configuration
    for section, agent in Config():
        # Filter by target if specified
        if args.target and args.target not in agent.url:
            continue

        # Filter by username if specified
        if args.username and args.username != agent.username:
            continue

        if agent.auth():
            # Fetch the list of projects for the agent
            projects = agent.gitlab.projects.list()
            for project in projects:
                # Filter by project name if specified
                if args.filter and args.filter not in project.path_with_namespace:
                    continue
                
                domain = urlparse(agent.url).netloc
                if domain not in repo_map:
                    repo_map[domain] = []  # Initialize the list if not already present
                if project.path_with_namespace not in repo_map[domain]:
                    repo_map[domain].append(project.path_with_namespace)
        else:
            print(f"[-] Authentication failed for {section}")

    # Sort targets
    repo_map = {k: sorted(v) for k, v in sorted(repo_map.items())}

    # Sort repositories
    for target, repos in repo_map.items():
        repo_map[target] = sorted(repos, key=lambda x: re.sub(r"[^a-zA-Z0-9]", "", x))
    
    # Display the results
    for target, repos in repo_map.items():
        print(f"{target}:")
        print("\t" + '\n\t'.join(repos))
        print()

def handle_clone_args(args):
    build_sub_parser(prog="labrat projects clone").print_help()
    #print("Cloning projects...")