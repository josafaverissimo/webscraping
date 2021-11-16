from .orm import Base
from .team import Team
from .map import Map

class TeamStats(Base):
    def __init__(
        self,
        team_id = None,
        map_id = None,
        times_played = None,
        ct_rate_win = None,
        tr_rate_win = None,
        both_rate_win = None
    ):
        table_name = 'teams_stats'
        columns = {
            'id': None,
            'team_id': team_id,
            'map_id': map_id,
            'times_played': times_played,
            'ct_rate_win': ct_rate_win,
            'tr_rate_win': tr_rate_win,
            'both_rate_win': both_rate_win,
            'created_at': None
        }

        get_columns = {}
        set_columns = {
            'team_id': int,
            'map_id': int,
            'times_played': int,
            'ct_rate_win': float,
            'tr_rate_win': float,
            'both_rate_win': float
        }

        super().__init__(table_name, columns, get_columns, set_columns)

    def get_team(self):
        team = Team()
        team_id = self.get_column('team_id')

        if team_id is not None:
            return team.get_by_column('id', self.get_column('team_id'))

        return None

    def get_map(self):
        map = Map()
        map_id = self.get_column('map_id')

        if map_id is not None:
            return map.get_by_column('id', self.get_column('map_id'))

        return None