from .orm import Orm


class Team(Orm):
    def __init__(self, name=None, hltv_id=None, world_ranking=None):
        table_name = 'teams'
        columns = {
            'id': None,
            'name': name,
            'hltv_id': hltv_id,
            'world_ranking': world_ranking,
            'created_at': None
        }

        get_columns = {}
        set_columns = {
            'name': str,
            'hltv_id': int,
            'world_ranking': int
        }

        super().__init__(table_name, columns, get_columns, set_columns)
