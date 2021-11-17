print('__file__={0:<35} | __name__={1:<25} | __package__={2:<25}'.format(__file__,__name__,str(__package__)))

from .. import teams_stats
from ..utils.helpers import subtract_date_by_difference, days_by_period
from datetime import date

def get_user_input():
    months = int(input("Type months diff: "))
    map = input("Type map: ")

    period = {
        'start': subtract_date_by_difference(date.today(), days_by_period['month'] * months).isoformat(),
        'end': date.today()
    }

    team_performance = teams_stats.get_teams_performance_by_map_and_period(map)
    teams_stats.store_teams_performance(team_performance)

def screen():
    get_user_input()
