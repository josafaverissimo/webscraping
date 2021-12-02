from .orm import Base
from .match import Match

class Event(Base):
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
        relationships_by_table_name = {
            'matches': {'references_key': 'id', 'foreign_key': 'event_id', 'orm': Match()}
        }

        super().__init__(table_name, columns, get_columns, set_columns, relationships_by_table_name)

    
