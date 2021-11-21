from .orm import Base

class Events(Base):
    def __init__(
        self,
        name = None,
        hltv_id = None
    ):
        table_name = 'events'
        columns = {
            'id': None,
            'name': name,
            'hltv_id': hltv_id
        }
        get_columns = {}
        set_columns = {
            'name': str,
            'hltv_id': int
        }

        super().__init__(table_name, columns, get_columns, set_columns)
