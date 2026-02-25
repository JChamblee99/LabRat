from labrat.core.agent import Agent
from labrat.core.config import Config
from urllib.parse import urlparse

class Agents:
    def __init__(self):
        self.config = Config(preauth=True)

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
            if not agent.is_authenticated:
                continue
            
            try:
                agent.add_ssh_key(title, key)
                yield agent, None
            except Exception as e:
                yield agent, e