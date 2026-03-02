import copy

from labrat.core.agent import Agent
from labrat.core.config import Config
from labrat.core.utils import obj_filter

class Groups:
    def __init__(self):
        self.config = Config(authed_only=True)

    def list(self, filter=None, agent_filter=None, min_level=0):
        """List groups accessible by agents.

        Keyword arguments:
        - filter: Regex filter and field selection passed to `utils.obj_filter()` for group objects
        - agent_filter: Regex filter and field selection passed to `utils.obj_filter()` for agent objects
        - min_level: Minimum desired access level for agent to return a group
        """

        group_map = {}
        for section, agent in self.config.filter(agent_filter):
            groups = agent.gitlab.groups.list(all=True)
            for group in groups:
                access_level = self.get_group_access_level(agent, group)
                if access_level < min_level:
                    continue

                # Agent enrichment with shallow copy
                agent_copy = copy.copy(agent)
                agent_copy.access_level = access_level

                # Group enrichment
                group.host = agent.host

                # Add group and agent to map
                if group.web_url not in group_map:
                    group.agents = [agent_copy]
                    group.access_level = access_level
                    group_map[group.web_url] = group
                else:
                    group_map[group.web_url].agents.append(agent_copy)
                    group_map[group.web_url].access_level = max(group_map[group.web_url].access_level, access_level)

        return [group for group in group_map.values() if not filter or obj_filter(group, filter)]

    def create_token(self, name, access_level, scopes, expires_at, agent_filter=None, filter=None):
        """ Create Group Access Tokens.
        
        Keyword arguments:
        - name: Name of the access token.
        - access_level: Access level of the created PAT.
        - scopes: List of scopes for the created PAT. (e.g. `['read_repository', 'write_repository']`)
        - expires_at: ISO format expiration date for the created PAT.
        - agent_filter: Regex filter and field selection passed to `utils.obj_filter()` for agent objects.
        - filter: Regex filter and field selection passed to `utils.obj_filter()` for group objects.
        """

        for group in self.list(filter=filter, agent_filter=agent_filter, min_level=50):
            agent = group.agents[0]

            try:
                req = group.access_tokens.create({
                    'name': name,
                    'access_level': access_level,
                    'scopes': scopes,
                    'expires_at': expires_at
                })

                section = f"{req.user_id}_{group.id}@{agent.host}"
                group_agent = Agent(agent.url, username=name, private_token=req.token, section=section)
                self.config[section] = group_agent.to_dict()

                yield group, group_agent, None
            except Exception as e:
                yield group, None, e

    def get_group_access_level(self, agent, group):
        try:
            return group.members.get(agent.id).access_level
        except Exception as e:
            return 60 if agent.is_admin else 0