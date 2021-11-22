from .orm import Base

class MatchTeamResult(Base):
    def __init__(self, team_id = None, result = None, match_id = None):
        table_name = 'matches_teams_results'
        columns = {
            'id': None,
            'team_id': team_id,
            'result': result,
            'match_id': match_id
        }

        get_columns = {}
        set_columns = {
            'team_id': int,
            'result': int,
            'match_id': int,
        }

        super().__init__(table_name, columns, get_columns, set_columns)
