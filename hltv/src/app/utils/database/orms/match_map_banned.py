from .orm import Base

class MatchMapBanned(Base):
    def __init__(self, map_id = None, team_id = None, match_id = None):
        table_name = 'matches_maps_banned'
        columns = {
            'id': None,
            'map_id': map_id,
            'team_id': team_id,
            'match_id': match_id
        }

        get_columns = {}
        set_columns = {
            'map_id': int,
            'team_id': int,
            'match_id': int,
        }

        super().__init__(table_name, columns, get_columns, set_columns)
