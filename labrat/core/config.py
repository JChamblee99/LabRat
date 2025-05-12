import configparser
import threading

from labrat.core.agent import Agent

class Config:
    def __init__(self, config_file=".python-gitlab.cfg"):
        self.config_file = config_file
        self._config = configparser.ConfigParser()
        self._config.read(config_file)

    def __getitem__(self, section):
        try:
            return self._config[section]
        except KeyError:
            return {}

    def __setitem__(self, section, value):
        self._config[section] = value
        self._save()

    def _save(self):
        with open(self.config_file, "w") as file:
            self._config.write(file)

    def __iter__(self):
        for section in self.sections():
            if section not in ["DEFAULT", "global"]:  # Skip special sections
                data = self[section]
                agent = Agent.from_dict(data)  # Create an Agent instance from the section data
                yield section, agent

    def sections(self):
        return self._config.sections()