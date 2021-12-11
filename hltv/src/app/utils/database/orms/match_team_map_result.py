from .orm import Orm
from .map import Map
from .team import Team
from .match import Match


class MatchTeamMapResult(Orm):
    def __init__(
        self,
        team_id=None,
        map_id=None,
        match_id=None,
        ct_rounds_wins=None,
        tr_rounds_wins=None,
        relationships=None
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

        relationships_by_table_name = Orm.get_orms_by_relationships(relationships, {
            'maps': {'references_key': 'id', 'foreign_key': 'map_id', 'orm': Map},
            'teams': {'references_key': 'id', 'foreign_key': 'team_id', 'orm': Team},
            'matches': {'references_key': 'id', 'foreign_key': 'match_id', 'orm': Match},
        })

        super().__init__(table_name, columns, get_columns, set_columns, relationships_by_table_name)
