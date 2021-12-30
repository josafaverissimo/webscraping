from .interface import Boilerplate
from ..pages.match import Match as MatchPage
from ..utils import helpers


class Match(Boilerplate):
    def __init__(self):
        inputs = {
            'match': {
                'datatype': MatchPage,
                'validation': lambda match_hltv_id: match_hltv_id.isnumeric(),
                'message': 'Type match hltv id'
            }
        }

        super().__init__(inputs)

    def main(self, user_inputs):
        match: MatchPage = user_inputs['match']

        match.load_page_data_by('hltv_id')
        match.store()
