from .interface import Boilerplate
from ..pages.team import Team as TeamPage


class Team(Boilerplate):
    def __init__(self):
        inputs = {
            'team': {
                'datatype': TeamPage,
                'validation': None,
                'message': 'Type team name'
            }
        }

        super().__init__(inputs)

    def main(self, user_inputs):
        team: TeamPage = user_inputs['team']

        team.load_page_data_by('team_name')
        team.store()
