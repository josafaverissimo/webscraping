from ..utils.webscraper import get_data_from_json_api
from ..utils.database.orms.team import Team as TeamORM
from urllib.parse import quote
from ..utils import helpers

class Team:
    def __init__(self, name = None):
        self.__team_data = {
            'name': name.lower() if name is not None else None,
            'hltv_id': None
        }
        self.__team_orm = TeamORM()

    def get_orm(self):
        team_orm = self.__team_orm
        team_orm.reset_columns_values()

        return team_orm

    def get_name(self):
        return self.__team_data['name']

    def set_name(self, name):
        self.__team_data['name'] = name.lower()

    def get_hltv_id(self):
        return self.__team_data['hltv_id']

    def set_hltv_id(self, hltv_id):
        self.__team_data['hltv_id'] = int(hltv_id)

    def get_team_data(self):
        return self.__team_data

    def load_by_team_data(self, team_data):
        if team_data is None:
            return None

        self.set_name(team_data['name'])
        self.set_hltv_id(team_data['hltv_id'])

    def search_team_by_name(self, name = None):
        def search(term):
            base_url = "https://www.hltv.org/search?term="
            url = base_url + quote(term)
            response = get_data_from_json_api(url)

            return response

        def get_team(name):
            teams = search(name)
            
            if teams is not None:
                teams = teams[0]['teams']
                for team in teams:
                    team_name = team['name'].lower()

                    if team_name == name:
                        return {
                            'name': team_name,
                            'hltv_id': team['id']
                        }

            return None

        name = name if name is not None else self.get_name()
        team_data = get_team(name)

        return team_data

    def load_team_by_name(self, name = None):
        team_data = self.search_team_by_name(name)
        self.load_by_team_data(team_data)

    def store(self):
        team_data = self.get_team_data()
        if helpers.has_none_value(team_data):
            return None

        team_orm = self.get_orm()
        loaded = team_orm.get_by_column('name', team_data['name'])

        if loaded is None:
            team_orm.set_columns(team_data)
            return team_orm.create()
        
        return loaded
