from labrat.core.config import Config

class Agents:
    def __init__(self):
        self.config = Config(preauth=True)

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