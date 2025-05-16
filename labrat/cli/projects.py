
import argparse
import git
import re
import os
from urllib.parse import urlparse
from labrat.core.agent import Agent
from labrat.core.config import Config
from labrat.core.utils import print_table


def build_parser(subparser=None):
    parser = argparse.ArgumentParser("labrat projects") if subparser is None else subparser
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", aliases=["ls"], help="List GitLab projects")
    build_list_parser(list_parser)
    
    clone_parser = subparsers.add_parser("clone", help="Clone GitLab repositories")
    build_clone_parser(clone_parser)
    return parser

def build_list_parser(subparser=None, prog=None):
    parser = argparse.ArgumentParser(prog) if subparser is None else subparser
    parser.add_argument("-a", "--all", action="store_true", required=False, help="All projects")
    parser.add_argument("-f", "--filter", required=False, help="Filter for project names")
    parser.add_argument("-t", "--target", required=False, help="GitLab server URL or pattern")
    parser.add_argument("-u", "--username", required=False, help="Username or e-mail for authentication")
    parser.set_defaults(func=handle_list_args)
    return parser

def build_clone_parser(subparser=None, prog=None):
    parser = argparse.ArgumentParser(prog) if subparser is None else subparser
    parser.add_argument("-a", "--all", action="store_true", required=False, help="All projects")
    parser.add_argument("-f", "--filter", required=False, help="Filter for project names")
    parser.add_argument("-t", "--target", required=False, help="GitLab server URL or pattern")
    parser.add_argument("-u", "--username", required=False, help="Username or e-mail for authentication")
    parser.add_argument("-o", "--output", required=False, help="Output location for cloned repositories", default='./')
    parser.set_defaults(func=handle_clone_args)
    return parser

def handle_list_args(args):
    # If no arguments are provided, show help
    if not args.all and not args.filter and not args.target and not args.username:
        build_list_parser(prog="labrat projects list").print_help()
        return
    
    projects = get_projects(args)

    # Format map for table
    data = []
    for target, repos in projects.items():
        for repo, users in repos.items():
            usernames = [user.username for user in users]
            data.append([
                target,
                repo,
                ", ".join(usernames)
            ])

    print_table(["Target", "Repository", "Users"], data)

def handle_clone_args(args):
    # If no arguments are provided, show help
    if not args.all and not args.filter and not args.target and not args.username:
        build_clone_parser(prog="labrat projects clone").print_help()
        return
    
    projects = get_projects(args)

    for target, repos in projects.items():
        for path_with_namespace, agents in repos.items():
            agent = agents[0]
            url = urlparse(agent.url)

            clone_url = f"{url.scheme}://{agent.username}:{agent.private_token}@{url.netloc}/{path_with_namespace}.git"
            to_path = f"{args.output}{'/' if args.output[-1] != '/' else ''}{url.hostname}/{path_with_namespace}"

            if os.path.isdir(to_path):
                print(f"[-] Directory {to_path} already exists, skipping...")
                continue

            try:
                git.Repo.clone_from(clone_url, to_path)
            except git.exc.GitCommandError as e:
                print(f"[!] Failed to clone {path_with_namespace} from {target}: {e}")
                continue

            print(f"[+] Cloned {target}/{path_with_namespace} to {to_path}")



def get_projects(args):
    # Dictionary to store map of targets to repositories to a list of users
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
            projects = agent.gitlab.projects.list(all=True)
            for project in projects:
                # Filter by project name if specified
                if args.filter and args.filter not in project.path_with_namespace:
                    continue
                
                domain = urlparse(agent.url).netloc
                if domain not in repo_map:
                    repo_map[domain] = {}
                if project.path_with_namespace not in repo_map[domain]:
                    repo_map[domain][project.path_with_namespace] = []
                repo_map[domain][project.path_with_namespace].append(agent)
        else:
            print(f"[-] Authentication failed for {section}")

    # Sort targets
    repo_map = dict(sorted(repo_map.items(), key=lambda x: re.sub(r"[^a-zA-Z0-9]", "", x[0])))

    # Sort repositories
    for target, repos in repo_map.items():
        repo_map[target] = dict(sorted(repos.items(), key=lambda x: re.sub(r"[^a-zA-Z0-9]", "", x[0])))

    return repo_map