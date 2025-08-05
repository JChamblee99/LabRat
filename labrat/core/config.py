import configparser
import os
import threading
from pathlib import Path

from labrat.core.agent import Agent

class Config:
    def __init__(self, config_file="~/.python-gitlab.cfg"):
        self.config_file = str(Path(config_file).expanduser())
        self._config = configparser.ConfigParser()
        self._config.read(self.config_file)

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

    def __iter__(self, keyword=None):
        for section in self.sections():
            if section not in ["DEFAULT", "global"]:  # Skip special sections
                
                data = self[section]

                # If keyword is provided, filter the agents for it
                if keyword:
                    fields = [
                        section,
                        data.get("url", ""),
                        data.get("username", ""),
                        "admin" if data.getboolean("is_admin", False) else "user",
                        data.get("private_token", "")
                    ]

                    if keyword.casefold() not in " ".join(fields).casefold():
                        continue

                agent = Agent.from_dict(data)  # Create an Agent instance from the section data
                yield section, agent

    def filter(self, keyword):
        return self.__iter__(keyword)

    def sections(self):
        return self._config.sections()
    
    def remove_section(self, section):
        if section in self._config:
            self._config.remove_section(section)
            self._save()
            return True
        else:
            return False