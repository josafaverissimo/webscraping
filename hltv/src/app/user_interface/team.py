from .. import team
from .interface import Boilerplate

class Team(Boilerplate):
    def __init__(self):
        inputs = {
            'team': {
                'datatype': str,
                'validation': None,
                'message': 'Type team name'
            }
        }

        super().__init__(inputs, self.main)

    def main(self):
        user_inputs = self.get_user_inputs()

        team = get_team.get_team_by_name(user_inputs['team'])
        get_team.store_team(team)
        
