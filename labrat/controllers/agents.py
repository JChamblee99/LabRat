from labrat.core.config import Config

class Agents:
    def __init__(self):
        self.config = Config(preauth=True)

    def list(self, filter=None):
        for section, agent in self.config.filter(filter):
            yield section, agent
