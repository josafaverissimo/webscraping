from .orm import Orm
from .map import Map
from .team import Team
from .match import Match


class MatchMapBanned(Orm):
    def __init__(
        self,
        map_id=None,
        team_id=None,
        match_id=None,
        relationships=None
    ):
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

        relationships_by_table_name = Orm.get_orms_by_relationships(relationships, {
            'maps': {'references_key': 'id', 'foreign_key': 'map_id', 'orm': Map},
            'teams': {'references_key': 'id', 'foreign_key': 'team_id', 'orm': Team},
            'matches': {'references_key': 'id', 'foreign_key': 'match_id', 'orm': Match}
        })

        super().__init__(table_name, columns, get_columns, set_columns, relationships_by_table_name)
