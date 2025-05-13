# labrat/main.py
import argparse
from labrat.cli import auth, projects

def main():
    parser = argparse.ArgumentParser(
        prog="labrat",
        description="LabRat: GitLab exploitation orchestrator"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Auth subcommand
    auth_parser = subparsers.add_parser("auth", help="Authenticate to GitLab server(s)")
    auth.build_parser(auth_parser)

    # Run subcommand
    run_parser = subparsers.add_parser("run", help="Execute CI/CD job")
    run_parser.add_argument("-u", "--username", required=True)
    run_parser.add_argument("-c", "--command", required=True)
    #run_parser.set_defaults(func=run.handle_args)

    # Projects subcommand
    projects_parser = subparsers.add_parser("projects", help="Manage GitLab projects")
    projects.build_parser(projects_parser)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()