# labrat/main.py
import argparse
from labrat.cli import agents, auth, projects

def main():
    parser = argparse.ArgumentParser(
        prog="labrat",
        description="LabRat: GitLab exploitation orchestrator"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Agents subcommand
    agents_parser = subparsers.add_parser("agents", help="Manage GitLab agents")
    agents.build_parser(agents_parser)

    # Auth subcommand
    auth_parser = subparsers.add_parser("auth", help="Authenticate to GitLab server(s)")
    auth.build_parser(auth_parser)

    # Projects subcommand
    projects_parser = subparsers.add_parser("projects", help="Manage GitLab projects")
    projects.build_parser(projects_parser)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()