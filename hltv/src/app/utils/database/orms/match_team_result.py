from .orm import Base
from .team import Team
from .match import Match

class MatchTeamResult(Base):
    def __init__(
        self,
        team_id = None,
        result = None,
        match_id = None,
        relationships = None
    ):
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

        relationships_by_table_name = Base.get_orms_by_relationships(relationships, {
            'teams': {'references_key': 'id', 'foreign_key': 'team_id', 'orm': Team},
            'matches': {'references_key': 'id', 'foreign_key': 'match_id', 'orm': Match}
        })

        super().__init__(table_name, columns, get_columns, set_columns, relationships_by_table_name)
