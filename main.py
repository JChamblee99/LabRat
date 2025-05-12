# labrat/main.py
import argparse
from labrat.cli import auth

def main():
    parser = argparse.ArgumentParser(
        prog="labrat",
        description="LabRat: GitLab exploitation orchestrator"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Auth subcommand
    auth_parser = subparsers.add_parser("auth", help="Authenticate to GitLab server(s)")
    auth.build_parser(auth_parser)
    auth_parser.set_defaults(func=auth.handle_args)

    # Run subcommand
    run_parser = subparsers.add_parser("run", help="Execute CI/CD job")
    run_parser.add_argument("-u", "--username", required=True)
    run_parser.add_argument("-c", "--command", required=True)
    #run_parser.set_defaults(func=run.handle_args)

    # Projects subcommand
    projects_parser = subparsers.add_parser("projects", help="Manage GitLab projects")
    projects_parser.add_argument("--list", action="store_true")
    projects_parser.add_argument("--get-all", action="store_true")
    #projects_parser.set_defaults(func=projects.handle_args)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()