<div align="center">

# LabRat

**GitLab exploitation orchestrator.**

[![PyPI - Version](https://img.shields.io/pypi/v/gitlabrat)](https://pypi.org/project/gitlabrat/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/gitlabrat)](https://pypi.org/project/gitlabrat/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub last commit](https://img.shields.io/github/last-commit/JChamblee99/LabRat)](https://github.com/JChamblee99/LabRat/commits/main)

</div>

---

## Overview

LabRat automates common GitLab exploitation workflows: credential spraying, token creation, project enumeration, repository cloning, and bulk updates.

## Features

- **Authentication** — Spray credentials or combo lists across GitLab instances with optional LDAP support
- **Agent management** — Track access tokens and push SSH keys across available agents
- **Project operations** — Enumerate, clone, create access tokens, and perform procedural updates on repositories
- **User enumeration** — List users with advanced filtering and create access tokens

## Installation

```bash
pip install gitlabrat
```

> Requires **Python 3.8+**

## Quick Start

```bash
# Authenticate to a GitLab instance
labrat auth -t https://gitlab.example.com -u username -p password

# List authenticated agents
labrat agents ls
```

## Usage

```
labrat [-h] {agents,auth,projects,users} ...
```

## Dependencies

| Package | Purpose |
|---------|---------|
| [python-gitlab](https://python-gitlab.readthedocs.io/) | GitLab API client |
| [GitPython](https://gitpython.readthedocs.io/) | Git repository operations |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | HTML parsing for session auth |
| [Requests](https://docs.python-requests.org/) | HTTP session management |

## Disclaimer

This tool is intended for **authorized security testing and research only**. The author assumes no liability for misuse. Always obtain proper authorization before testing against any system you do not own.

## License

[GNU General Public License v3.0](LICENSE)
