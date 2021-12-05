from .orm import Orm


class MatchTeamMapResult(Orm):
    def __init__(
        self,
        team_id=None,
        map_id=None,
        match_id=None,
        ct_rounds_wins=None,
        tr_rounds_wins=None
    ):
        table_name = 'matches_teams_maps_results'
        columns = {
            'id': None,
            'team_id': team_id,
            'map_id': map_id,
            'match_id': match_id,
            'ct_rounds_wins': ct_rounds_wins,
            'tr_rounds_wins': tr_rounds_wins
        }

        get_columns = {}
        set_columns = {
            'team_id': int,
            'map_id': int,
            'match_id': int,
            'ct_rounds_wins': int,
            'tr_rounds_wins': int
        }

        super().__init__(table_name, columns, get_columns, set_columns)
