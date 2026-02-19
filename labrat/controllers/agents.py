from labrat.core.agent import Agent
from labrat.core.config import Config
from urllib.parse import urlparse

class Agents:
    def __init__(self):
        self.config = Config(preauth=True)

    def auth(self, targets, users, use_ldap=False):
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

    def reauth(self, target=None, username=None):
        for section, agent in self.config:
            # Filter by target if specified
            if target and target not in agent.url:
                continue

            # Filter by username if specified
            if username and username != agent.username:
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
        for section, agent in self.config.filter(filter):
            yield agent

    def delete(self, filter):
        for section, agent in self.config.filter(filter):
            self.config.remove_section(section)
            yield agent

    def add_ssh_key(self, filter, title, key):
        for section, agent in self.config.filter(filter):
            try:
                agent.add_ssh_key(title, key)
                yield agent, None
            except Exception as e:
                yield agent, e