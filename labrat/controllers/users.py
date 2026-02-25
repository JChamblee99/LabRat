from labrat.core.agent import Agent
from labrat.core.config import Config
from labrat.core.utils import obj_filter
from urllib.parse import urlparse

class Users:
    def __init__(self):
        self.config = Config(authed_only=True)

    def list(self, filter=None):
        """List users and additional information.

        Keyword arguments:
        - filter: Regex filter and field selection passed to `utils.obj_filter()`
        """

        data = dict()
        for section, agent in self.config:
            users = agent.gitlab.users.list(all=True)
            for user in users:
                self._user_enrichment(agent, user)

                if user.section not in data.keys() or agent.is_admin:
                    data[user.section] = user

        data = [user for user in data.values() if not filter or obj_filter(user, filter)]

        return data

    def create_token(self, name, scopes, filter=None):
        """Create Personal Access Tokens for other users.

        Keyword arguments:
        - name: Name of the access token.
        - scopes: List of scopes for the access token.
        - filter: Regex filter and field selection passed to `utils.obj_filter()`
        """

        for section, agent in self.config:
            if not agent.is_admin:
                continue

            for user in agent.gitlab.users.list(all=True):
                self._user_enrichment(agent, user)
                if user.is_agent:
                    continue

                if filter and not obj_filter(user, filter):
                    continue

                try:
                    req = user.personal_access_tokens.create({
                        "name": name,
                        "scopes": scopes
                    })
                    agent_user = Agent(agent.url, username=user.username, private_token=req.token)
                    self.config[user.section] = agent_user.to_dict()
                    yield agent_user, None
                except Exception as e:
                    yield None, e

    def _user_enrichment(self, agent, user):
        user.url = agent.url
        user.host = agent.host
        user.section = f"{user.id}@{agent.host}"
        user.label = f"{user.username}@{agent.host}"
        user.is_agent = self.config.has_section(user.section)
        user.is_bot = getattr(user, "bot", None)