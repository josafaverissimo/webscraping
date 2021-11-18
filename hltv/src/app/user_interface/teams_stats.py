from .. import teams_stats
from .interface import Boilerplate
from ..utils.helpers import subtract_date_by_difference, days_by_period
from datetime import date

class TeamsStats(Boilerplate):
    def __init__(self):
        inputs = {
            'months': {
                'datatype': int,
                'validation': self.valid_months,
                'message': 'Type months diff'
            },
            'map': {
                'datatype': str,
                'validation': None,
                'message': 'Type a map'
            }
        }

        super().__init__(inputs, self.main)

    def valid_months(self, months):
        if months.isnumeric():
            return int(months) > 0

        return False

    def main(self):
        user_inputs = self.get_user_inputs()

        period = {
            'start': subtract_date_by_difference(date.today(), days_by_period['month'] * user_inputs['months']).isoformat(),
            'end': date.today().isoformat()
        }

        teams_stats_performances = teams_stats.get_teams_performance_by_map_and_period(user_inputs['map'], period)
        teams_stats.store_teams_performance(teams_stats_performances)
        
