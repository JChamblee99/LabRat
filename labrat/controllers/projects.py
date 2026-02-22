import copy
import os
import git
import re

from labrat.core.agent import Agent
from labrat.core.config import Config
from labrat.core.utils import obj_filter
from urllib.parse import urlparse

class Projects:
    def __init__(self):
        self.config = Config(authed_only=True)

    def list(self, filter=None, agent_filter=None, min_level=0):
        """List projects accessible by agents.

        Keyword arguments:
        - filter: Regex filter and field selection passed to `utils.obj_filter()` for project objects
        - agent_filter: Regex filter and field selection passed to `utils.obj_filter()` for agent objects
        - min_level: Minimum desired access level for agent to return a project
        """

        repo_map = {}
        for section, agent in self.config.filter(agent_filter):
            projects = agent.gitlab.projects.list(all=True)
            for project in projects:
                access_level = self.get_project_access_level(agent, project)
                if access_level < min_level:
                    continue

                # Agent enrichment with shallow copy
                agent_copy = copy.copy(agent)
                agent_copy.access_level = access_level

                # Project enrichment
                project.host = agent.host

                # Add project and agent to map
                if project.web_url not in repo_map:
                    project.agents = [agent_copy]
                    project.access_level = access_level
                    repo_map[project.web_url] = project
                else:
                    repo_map[project.web_url].agents.append(agent_copy)
                    repo_map[project.web_url].access_level = max(repo_map[project.web_url].access_level, access_level)

        return [proj for proj in repo_map.values() if not filter or obj_filter(proj, filter)]

    def clone(self, output, agent_filter=None, filter=None):
        """Clone projects accessible by agents.

        Keyword arguments:
        - output: Output directory for cloned projects. A nested structure of `<hostname>/<namespace>/<project>` will be created inside.
        - agent_filter: Regex filter and field selection passed to `utils.obj_filter()` for agent objects.
        - filter: Regex filter and field selection passed to `utils.obj_filter()` for project objects.
        """

        projects = self.list(filter=filter, agent_filter=agent_filter, min_level=15)
        for project in projects:
            agent = project.agents[0]

            url = urlparse(agent.url)
            clone_url = f"{url.scheme}://{agent.username}:{agent.private_token}@{url.netloc}/{project.path_with_namespace}.git"
            to_path = f"{output}{'/' if output[-1] != '/' else ''}{url.hostname}/{project.path_with_namespace}"
            project.clone_url = clone_url
            project.to_path = to_path

            if os.path.isdir(to_path):
                yield project, f"destination path '{to_path}' already exists"
                continue

            try:
                git.Repo.clone_from(clone_url, to_path)
                yield project, None
            except Exception as e:
                yield project, e

    def create_access_token(self, name, access_level, scopes, expires_at, agent_filter=None, filter=None):
        """ Create Project Access Tokens.
        
        Keyword arguments:
        - name: Name of the access token.
        - access_level: Access level of the created PAT.
        - scopes: List of scopes for the created PAT. (e.g. `['read_repository', 'write_repository']`)
        - expires_at: ISO format expiration date for the created PAT.
        - agent_filter: Regex filter and field selection passed to `utils.obj_filter()` for agent objects.
        - filter: Regex filter and field selection passed to `utils.obj_filter()` for project objects.
        """

        for project in self.list(filter=filter, agent_filter=agent_filter, min_level=40):
            agent = project.agents[0]

            try:
                req = project.access_tokens.create({
                    'name': name,
                    'access_level': access_level,
                    'scopes': scopes,
                    'expires_at': expires_at
                })

                section = f"{req.user_id}_{project.id}@{agent.host}"
                project_agent = Agent(agent.url, username=name, private_token=req.token, section=section)
                self.config[section] = project_agent.to_dict()

                yield project, project_agent, None
            except Exception as e:
                yield project, None, e

    def update(self, file_path, content=None, pattern=None, replace=None, branch=None, commit_message=None, agent_filter=None, filter=None):
        """Update file contents.

        Keyword arguments:
        - file_path: Path to the file in project to update.
        - content: New content for the file.
        - pattern: Regex pattern to match for replacement.
        - replace: Replacement string for the regex pattern.
        - branch: Branch to commit the changes to.
        - commit_message: Commit message for the update.
        - agent_filter: Regex filter and field selection passed to `utils.obj_filter()` for agent objects.
        - filter: Regex filter and field selection passed to `utils.obj_filter()` for project objects.
        """

        for project in self.list(filter=filter, agent_filter=agent_filter, min_level=30):
            agent = project.agents[0]
            try:
                file = project.files.get(file_path=file_path, ref="main")
                file_content = file.decode().decode("utf-8")

                if content:
                    new_content = content
                elif pattern and replace is not None:
                    new_content = re.sub(pattern, replace, file_content)
                else:
                    yield project, None, "No update method specified"
                    continue

                if new_content == file_content:
                    yield project, None, "Content is the same, skipping update"
                    continue

                commit = project.commits.create({
                    "branch": branch,
                    "commit_message": commit_message,
                    "actions": [
                        {
                            "action": "update",
                            "file_path": file_path,
                            "content": new_content
                        }
                    ]
                })
                yield project, commit, None
            except Exception as e:
                yield project, None, e

    def get_project_access_level(self, agent, project):
        if project.permissions['project_access']:
            access_level = int(project.permissions['project_access']['access_level'])
        elif project.permissions['group_access']:
            access_level = int(project.permissions['group_access']['access_level'])
        else:
            access_level = 50 if agent.is_admin else 15
        return access_level