import configparser
from pathlib import Path

from labrat.core.agent import Agent
from labrat.core.utils import obj_filter

class Config:
    def __init__(self, config_file="~/.python-gitlab.cfg", preauth=False, authed_only=False):
        self.config_file = str(Path(config_file).expanduser())
        self._config = configparser.ConfigParser()
        self._config.read(self.config_file)
        self.preauth = preauth
        self.authed_only = authed_only

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

    def __iter__(self, filter=None):
        for section in self.sections():
            if section not in ["DEFAULT", "global"]:  # Skip special sections
                
                data = self[section]
                agent = Agent.from_dict(data)  # Create an Agent instance from the section data

                if self.preauth or self.authed_only:
                    try:
                        agent.auth()
                    except Exception as e:
                        pass

                if filter and not obj_filter(agent, filter):
                    continue

                if agent.is_authenticated or not self.authed_only:
                    yield section, agent

    def filter(self, filter):
        return self.__iter__(filter)

    def sections(self):
        return self._config.sections()
        
    def has_section(self, section):
        return self._config.has_section(section)
    
    def remove_section(self, section):
        if section in self._config:
            self._config.remove_section(section)
            self._save()
            return True
        else:
            return False