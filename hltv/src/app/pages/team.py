from .page import Page
from ..utils import requester
from ..utils.database.orms.team import Team as TeamORM
from ..utils import helpers
from urllib import parse


class Team(Page):
    def __init__(self, team_name=None):
        self.__team_data_response = None
        self.__api_base_url = "https://www.hltv.org/search"
        self.__team_data = None

        base_url = 'https://www.hltv.org/team'
        searchable_data = {
            'team_name': {
                'value': team_name,
                'get_partial_uri': self.__get_partial_uri_by_team_name,
                'set_value': self.__set_team_name
            }
        }
        orm = TeamORM()

        super().__init__(base_url, searchable_data, orm)

    def __set_team_name(self, team_name):
        return str(team_name).lower()

    def __get_partial_uri_by_team_name(self, team_name):
        team_data = self.__load_team_data_by_name(team_name)

        if team_data is None:
            return None

        hltv_id = team_data['hltv_id']
        return f"{hltv_id}/team"

    def __get_team_data_by_name(self):
        team_name = self.get_searchable_data('team_name')

        response = self.__team_data_response

        if response is not None:
            teams = response[0]['teams']

            for team in teams:
                if team_name == team['name'].lower():
                    team_data = {
                        'name': team_name,
                        'hltv_id': team['id']
                    }

                    return team_data

        return None

    def __set_team_data_response_by_name(self):
        team_name = self.get_searchable_data('team_name')

        if team_name is None:
            return None

        team_name = parse.quote(team_name)

        url = f"{self.__api_base_url}?term={team_name}"

        self.__team_data_response = requester.get_data_from_json_api(url)

    def __load_team_data_by_name(self, team_name=None):
        if team_name is not None:
            self.set_searchable_data('team_name', team_name)

        self.__set_team_data_response_by_name()

        self.__team_data = self.__get_team_data_by_name()

        return self.__team_data

    def get_world_ranking(self, page):
        wrapper = page.find('div', {'class': 'profile-team-stat'})
        world_ranking = int(wrapper.find('a').get_text().replace('#', ''))

        return world_ranking

    def get_page_data_from_page(self, page):
        page = page.find('div', {'class': 'contentCol'})
        page_data = {}

        if page is not None:
            page_data['name'] = self.__team_data['name']
            page_data['hltv_id'] = self.__team_data['hltv_id']
            page_data['world_ranking'] = self.get_world_ranking(page)

            return page_data

        return None

    def store(self):
        page_data = self.get_page_data()
        team_orm = self._get_orm()

        if page_data is not None:
            team_orm.set_columns(page_data)
            return team_orm.create()
