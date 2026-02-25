from labrat.core.agent import Agent
from labrat.core.config import Config
from urllib.parse import urlparse

class Auth:
    def __init__(self):
        self.config = Config()

    def auth(self, targets, users, use_ldap=False):
        """Authenticate and create a PAT for each user on each target.
        
        Keyword arguments:
        - targets: List of target URLs to authenticate against.
        - users: List of (username, password) tuples for authentication.
        - use_ldap: Whether to use LDAP for authentication (default: False).
        """

        for username, password in users:
            for target in targets:
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