# LabRat

LabRat is a GitLab exploitation orchestrator designed for security researchers and penetration testers.

## Features

- **Authentication Management** - Authenticate to GitLab servers and manage access tokens
- **Project Management** - List, clone, and manipulate GitLab projects
- **User Management** - Enumerate and create access tokens for GitLab users
- **Agent Management** - Manage multiple GitLab agents and credentials

## Installation

Install LabRat from PyPI:

```bash
pip install gitlabrat
```

## Usage

```bash
labrat --help
```

### Commands

- `labrat auth` - Authenticate to GitLab server(s)
- `labrat agents` - Manage GitLab agents
- `labrat projects` - Manage GitLab projects
- `labrat users` - Manage GitLab users

## Requirements

- Python 3.8+
- python-gitlab
- GitPython
- beautifulsoup4
- requests

## License

GNU General Public License v3.0 (GPL-3.0)

## Author

John Chamblee
