import argparse
import git
import re
import os
from urllib.parse import urlparse

from labrat.cli import common
from labrat.core.agent import Agent
from labrat.core.config import Config


def build_parser(parsers):
    parser = parsers.add_parser("projects", help="Manage GitLab projects")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = common.add_filtered_parser(subparsers, "list", handle_list_args, aliases=["ls"], help="List GitLab projects", filter_required=False)
    
    clone_parser = common.add_filtered_parser(subparsers, "clone", handle_clone_args, help="Clone GitLab repositories")
    clone_parser.add_argument("-o", "--output", required=False, help="Output location for cloned repositories", default='./')

    return subparsers

def handle_list_args(args):
    projects = get_projects(args)

    # Format map for table
    data = []
    for target, repos in projects.items():
        for path_with_namespace, agents in repos.items():
            usernames = [agent.username for agent in agents]
            data.append([
                target,
                path_with_namespace,
                ", ".join(usernames)
            ])

    common.print_table(["Target", "Project", "Usernames"], data)

def handle_clone_args(args):
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
        if agent.auth():
            # Fetch the list of projects for the agent
            projects = agent.gitlab.projects.list(all=True)
            for project in projects:
                # Filter by sbstring of fields
                if args.filter and args.filter.casefold() not in (f"{agent.url} {project.path_with_namespace} {agent.username}"):
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