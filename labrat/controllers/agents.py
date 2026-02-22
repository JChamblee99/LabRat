from labrat.core.agent import Agent
from labrat.core.config import Config
from urllib.parse import urlparse

class Agents:
    def __init__(self):
        self.config = Config(preauth=True)

    def auth(self, targets, users, use_ldap=False):
        """Authenticate and create a PAT for each user on each target.
        
        Keyword arguments:
        - targets: List of target URLs to authenticate against.
        - users: List of (username, password) tuples for authentication.
        - use_ldap: Whether to use LDAP for authentication (default: False).
        """

        for username, password in users:
            for target in targets:
                domain = urlparse(target).hostname
                
                agent = Agent(target, use_ldap, username, password)
                try:
                    agent.login()
                    agent.auth(private_token=agent.create_pat())
                    self.config[agent.section] = agent.to_dict()
                    yield agent, None
                except Exception as e:
                    yield agent, e

    def reauth(self, targets=None, users=None):
        """Re-authenticate existing agents.

        Keyword arguments:
        - targets: List of target URLs to re-authenticate against.
        - users: List of usernames to re-authenticate.
        """

        for section, agent in self.config:
            # Filter by target if specified
            if targets and agent.url not in targets:
                continue

            # Filter by username if specified
            if users and agent.username not in users:
                continue

            try:
                if not agent.is_authenticated:
                    agent.login()
                    agent.auth(private_token=agent.create_pat())
                    self.config[section] = agent.to_dict()
                yield agent, None
            except Exception as e:
                yield agent, e

    def list(self, filter=None):
        """List Labrat agents in config.
        
        Keyword arguments:
        - filter: Regex filter and field selection passed to `utils.obj_filter()`
        """

        for section, agent in self.config.filter(filter):
            yield agent

    def delete(self, filter):
        """Delete Labrat agents from config.

        Keyword arguments:
        - filter: Regex filter and field selection passed to `utils.obj_filter()`
        """

        for section, agent in self.config.filter(filter):
            self.config.remove_section(section)
            yield agent

    def add_ssh_key(self, filter, title, key):
        """Add an SSH key to each agent matching the filter.

        Keyword arguments:
        - filter: Regex filter and field selection passed to `utils.obj_filter()`
        - title: Title of the SSH key.
        - key: The SSH key to add.
        """

        for section, agent in self.config.filter(filter):
            try:
                agent.add_ssh_key(title, key)
                yield agent, None
            except Exception as e:
                yield agent, e