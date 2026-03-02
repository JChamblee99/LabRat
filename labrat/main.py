# labrat/main.py
import argparse
from labrat.cli import agents, auth, projects, groups, users

def main():
    parser = argparse.ArgumentParser(
        prog="labrat",
        description="LabRat: GitLab exploitation orchestrator"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in [agents, auth, projects, groups, users]:
        command.build_parser(subparsers)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
