import argparse
import git
import re
import os
from urllib.parse import urlparse

import gitlab

from labrat.cli import common
from labrat.core.utils import ansi_for_level
from labrat.core.agent import Agent
from labrat.core.config import Config


def build_parser(parsers):
    parser = parsers.add_parser("projects", help="Manage GitLab projects")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = common.add_filtered_parser(subparsers, "list", handle_list_args, aliases=["ls"], help="List GitLab projects", filter_required=False)
    list_parser.add_argument("-m", "--min-access-level", required=False, type=int, help="Minimum access level to filter projects", default=0)

    clone_parser = common.add_filtered_parser(subparsers, "clone", handle_clone_args, help="Clone GitLab repositories")
    clone_parser.add_argument("-o", "--output", required=False, help="Output location for cloned repositories", default='./')

    update_parser = common.add_filtered_parser(subparsers, "update", handle_update_args, help="Update GitLab repositories procedurally")
    update_parser.add_argument("-F", "--file", required=True, help="Path to the remote file to update")

    mechanism_group = update_parser.add_mutually_exclusive_group(required=True)
    mechanism_group.add_argument("-c", "--content", required=False, help="Text content to replace the file with")
    mechanism_group.add_argument("-C", "--content-file", required=False, help="Path to replacement file")
    mechanism_group.add_argument("-p", "--pattern", required=False, help="String or regex pattern to find in the file")

    update_parser.add_argument("-r", "--replace", required=False, help="String or pattern to replace the found text")

    update_parser.add_argument("-m", "--commit-message", required=False, help="Commit message for the update", default="Update")
    update_parser.add_argument("-b", "--branch", required=False, help="Branch to update", default="main")

    return subparsers

def handle_list_args(args):
    projects = get_projects(args)

    # Format map for table
    data = []
    for target, repos in projects.items():
        for path_with_namespace, agents in repos.items():
            access_levels = [get_project_access_level(agent, agent.gitlab.projects.get(path_with_namespace)) for agent in agents]
            max_access_level = max(access_levels) if access_levels else 0

            # color each username by that agent's access level (higher -> brighter)
            usernames = []
            for lvl, agent in zip(access_levels, agents):
                color = ansi_for_level(lvl)
                usernames.append(f"{color}{agent.username}\x1b[0m")

            data.append([
                target,
                path_with_namespace,
                gitlab.const.AccessLevel(max_access_level).name.lower(),
                ", ".join(usernames)
            ])

    common.print_table(["Target", "Project", "Access Level", "Usernames"], data)

def handle_clone_args(args):
    projects = get_projects(args, required_access_level=15)

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

def handle_update_args(args):
    projects = get_projects(args, required_access_level=30)

    for target, repos in projects.items():
        for path_with_namespace, agents in repos.items():
            agent = agents[0]

            try:
                project = agent.gitlab.projects.get(path_with_namespace)
                file = project.files.get(file_path=args.file, ref="main")
                content = file.decode().decode("utf-8")

                if args.content:
                    new_content = args.content
                elif args.content_file:
                    with open(args.content_file, "r") as f:
                        new_content = f.read()
                elif args.pattern:
                    if args.replace == None:
                        print(f"[!] Failed to update: No replacement value provided with -r/--replace")
                        return
                    
                    new_content = re.sub(args.pattern, args.replace, content, flags=re.MULTILINE)

                if new_content == content:
                    print(f"[-] No changes for {target}/{path_with_namespace}, skipping...")
                    continue

                commit = project.commits.create({
                    "branch": args.branch,
                    "commit_message": args.commit_message,
                    "actions": [
                        {
                            "action": "update",
                            "file_path": args.file,
                            "content": new_content
                        }
                    ]
                })

                
                print(f"[+] Updated {commit.web_url}")

                diff = commit.diff()
                if diff: print(diff[0].get("diff"))

            except gitlab.exceptions.GitlabGetError as e:
                continue
            except Exception as e:
                print(f"[!] Failed to update {target}/{path_with_namespace}: {e}")

def get_projects(args, required_access_level=0):
    # Dictionary to store map of targets to repositories to a list of users
    repo_map = {}

    # Iterate through the configuration
    for section, agent in Config():
        if not agent.auth():
            print(f"[-] Authentication failed for {section}")
            continue
        
        # Fetch the list of projects for the agent
        projects = agent.gitlab.projects.list(all=True)
        for project in projects:
            # Filter by sbstring of fields
            if args.filter and args.filter.casefold() not in (f"{agent.url} {project.path_with_namespace} {agent.username}"):
                continue

            access_level = get_project_access_level(agent, project)
            if "min_access_level" in args and access_level < args.min_access_level or access_level < required_access_level:
                continue

            domain = urlparse(agent.url).netloc
            if domain not in repo_map:
                repo_map[domain] = {}
            if project.path_with_namespace not in repo_map[domain]:
                repo_map[domain][project.path_with_namespace] = []
            repo_map[domain][project.path_with_namespace].append(agent)
            

    # Sort targets
    repo_map = dict(sorted(repo_map.items(), key=lambda x: re.sub(r"[^a-zA-Z0-9]", "", x[0])))

    # Sort repositories
    for target, repos in repo_map.items():
        repo_map[target] = dict(sorted(repos.items(), key=lambda x: re.sub(r"[^a-zA-Z0-9]", "", x[0])))

    return repo_map

def get_project_access_level(agent, project):
    if project.permissions['project_access']:
        access_level = int(project.permissions['project_access']['access_level'])
    elif project.permissions['group_access']:
        access_level = int(project.permissions['group_access']['access_level'])
    else:
        access_level = 50 if agent.is_admin else 15
    return access_level