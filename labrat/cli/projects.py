import datetime
import gitlab

from labrat.cli import common
from labrat.controllers.projects import Projects

def build_parser(parsers):
    parser = parsers.add_parser("projects", help="Manage GitLab projects")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = common.add_filtered_parser(subparsers, "list", handle_list_args, aliases=["ls"], help="List GitLab projects", filter_required=False)
    list_parser.add_argument("-m", "--min-access-level", required=False, type=int, help="Minimum access level to filter projects", default=0)
    list_parser.add_argument("-u", "--user", action="append", required=False, help="Filter agent performing action")

    clone_parser = common.add_filtered_parser(subparsers, "clone", handle_clone_args, help="Clone GitLab repositories")
    clone_parser.add_argument("-o", "--output", required=False, help="Output location for cloned repositories", default='./')
    clone_parser.add_argument("-u", "--user", action="append", required=False, help="Filter agent performing action")

    create_token_parser = common.add_filtered_parser(subparsers, "create_token", handle_create_token_args, help="Create an access token", filter_required=True)
    create_token_parser.add_argument("-l", "--access-level", required=False, type=int, help="Access level for the access token", default=50)
    create_token_parser.add_argument("-d", "--days", required=False, type=int, help="Number of days until the token expires", default=60)
    create_token_parser.add_argument("-n", "--token-name", required=False, help="Name for the access token", default="project_bot")
    create_token_parser.add_argument("-s", "--scopes", required=False, help="Comma-separated list of scopes for the access token", default="api,read_repository,write_repository")
    create_token_parser.add_argument("-u", "--user", action="append", required=False, help="Filter agent performing action")

    update_parser = common.add_filtered_parser(subparsers, "update", handle_update_args, help="Update GitLab repositories procedurally", filter_required=True)
    update_parser.add_argument("-F", "--file", required=True, help="Path to the remote file to update")

    mechanism_group = update_parser.add_mutually_exclusive_group(required=True)
    mechanism_group.add_argument("-c", "--content", required=False, help="Text content to replace the file with")
    mechanism_group.add_argument("-C", "--content-file", required=False, help="Path to replacement file")
    mechanism_group.add_argument("-p", "--pattern", required=False, help="String or regex pattern to find in the file")

    update_parser.add_argument("-r", "--replace", required=False, help="String or pattern to replace the found text")

    update_parser.add_argument("-m", "--commit-message", required=False, help="Commit message for the update", default="Update")
    update_parser.add_argument("-b", "--branch", required=False, help="Branch to update", default="main")
    update_parser.add_argument("-u", "--user", action="append", required=False, help="Filter agent performing action")

    parser.set_defaults(controller=Projects())
    return subparsers

def handle_list_args(args):
    headers = ["Host", "ID", "Path with Namespace", "Access Level", "Agents"]
    data = []

    for project in args.controller.list(args.filter, args.user):
        # color each username by that agent's access level (higher -> brighter)
        usernames = []
        for agent in project.agents:
            colored_username = common.color_access_level(agent.access_level, f"{agent.username} ({agent.access_level})")
            usernames.append(colored_username)
        
        # Add project information to data table
        data.append([
            project.host,
            project.id,
            project.path_with_namespace,
            f"{project.access_level} ({gitlab.const.AccessLevel(project.access_level).name.lower()})",
            ", ".join(usernames)
        ])

    common.print_table(headers, data)

def handle_clone_args(args):
    for project, err in args.controller.clone(args.output, args.user, args.filter):
        if err:
            print(f"[!] Failed to clone {project.web_url}: {err}")
        else:
            print(f"[+] Successfully cloned {project.web_url} to {project.to_path}")

def handle_create_token_args(args):
    expiration = (datetime.datetime.now() + datetime.timedelta(days=args.days)).strftime("%Y-%m-%d")
    for project, agent, err in args.controller.create_token(args.token_name, args.access_level, args.scopes.split(","), expiration, args.user, args.filter):
        if err:
            print(f"[!] Failed to create access token for {project.web_url}: {err}")
        else:
            print(f"[+] Successfully created access token for {project.web_url}: {agent.private_token}")

def handle_update_args(args):
    content = None
    if args.content:
        content = args.content
    elif args.content_file:
        with open(args.content_file, "r") as f:
            content = f.read()
    
    for project, commit, err in args.controller.update(file_path=args.file, content=content, pattern=args.pattern, replace=args.replace, branch=args.branch, commit_message=args.commit_message, agent_filter=args.user, filter=args.filter):
        if err:
            print(f"[!] Failed to update {project.web_url}: {err}")
        else:
            print(f"[+] Successfully updated {project.web_url}:")
            diff = commit.diff()
            if diff:
                print(common.color_diff(diff[0].get("diff")))