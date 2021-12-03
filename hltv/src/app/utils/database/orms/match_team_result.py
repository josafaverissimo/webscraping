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

        team_orm = None
        match_orm = None


        if relationships is not None:
            if 'teams' in relationships:
                team_orm = relationships['teams']
            else:
                team_orm = Team()

            if 'matches' in relationships:
                match_orm = relationships['matches']
            else:
                match_orm = Match()
        else:
            team_orm = Team()
            match_orm = Match()


        relationships_by_table_name = {
            'teams': {'references_key': 'id', 'foreign_key': 'team_id', 'orm': team_orm},
            'matches': {'references_key': 'id', 'foreign_key': 'match_id', 'orm': match_orm}
        }

        super().__init__(table_name, columns, get_columns, set_columns, relationships_by_table_name)
