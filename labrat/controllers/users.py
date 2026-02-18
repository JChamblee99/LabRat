from labrat.core.agent import Agent
from labrat.core.config import Config
from labrat.core.utils import obj_filter
from urllib.parse import urlparse

class Users:
    def __init__(self):
        self.config = Config(authed_only=True)

    def list(self, filter=None):
        for section, agent in self.config:
            users = agent.gitlab.users.list(all=True)
            for user in users:
                label = f"{user.id}@{agent.host}"
                user.label = label
                user.is_agent = (self.config.has_section(label))
                if filter is None or obj_filter(user, filter):
                    yield agent, user

    def create_pat(self, filter=None):
        for section, agent in self.config:
            if agent.is_admin:
                for user in agent.gitlab.users.list(all=True):
                    label = f"{user.id}@{agent.host}"
                    if not self.config.has_section(label):
                        if filter and not obj_filter(user, filter):
                            continue

                        try:
                            token = agent.create_pat(user_id=user.id)
                            agent_user = Agent(agent.url, username=user.username, private_token=token)
                            self.config[label] = agent_user.to_dict()
                            yield agent_user, None
                        except Exception as e:
                            yield None, e