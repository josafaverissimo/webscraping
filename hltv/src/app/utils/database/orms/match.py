from .orm import Orm
from .event import Event
from datetime import datetime

class Match(Orm):
    def __init__(
        self,
        hltv_id = None,
        event_id = None,
        matched_at = None,
        relationships = None
    ):
        table_name = 'matches'
        columns = {
            'id': None,
            'hltv_id': hltv_id,
            'event_id': event_id,
            'matched_at': matched_at
        }
        get_columns = {}
        set_columns = {
            'hltv_id': int,
            'event_id': int,
            'matched_at': self.set_matched_at
        }

        relationships_by_table_name = Orm.get_orms_by_relationships(relationships, {
            'events': {'references_key': 'id', 'foreign_key': 'event_id', 'orm': Event}
        })

        super().__init__(table_name, columns, get_columns, set_columns, relationships_by_table_name)

    def set_matched_at(self, timestamp):
        timestamp = int(timestamp)

        return datetime.fromtimestamp(timestamp).isoformat()