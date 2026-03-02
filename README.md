<div align="center">

# Labrat

**Living rent-free in the walls of your GitLab.**

[![PyPI - Version](https://img.shields.io/pypi/v/gitlabrat)](https://pypi.org/project/gitlabrat/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/gitlabrat)](https://pypi.org/project/gitlabrat/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub last commit](https://img.shields.io/github/last-commit/JChamblee99/LabRat)](https://github.com/JChamblee99/LabRat/commits/main)

</div>

---

## Overview

Labrat automates workflows for gaining and maintaining access to GitLab instances and CI/CD pipelines.

## Installation

```bash
pip install gitlabrat
```

## Quick Start

```bash
# Authenticate to a GitLab instance
labrat auth -t https://gitlab.example.com -u username -p password

# List authenticated agents
labrat agents ls
```