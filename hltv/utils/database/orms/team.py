from .orm import Base

class Team(Base):
    def __init__(self, name = None, hltv_id = None, id = None, created_at = None):
        table_name = 'teams'
        columns = {
            'id': id,
            'name': name,
            'hltv_id': hltv_id,
            'created_at': created_at
        }

        get_columns = {}
        set_columns = {
            'name': str,
            'hltv_id': int
        }

        super().__init__(table_name, columns, get_columns, set_columns)        
