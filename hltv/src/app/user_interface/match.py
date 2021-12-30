from .interface import Boilerplate
from ..pages.match import Match
from ..utils import helpers


class Match(Boilerplate):
    def __init__(self):
        inputs = {
            'match': {
                'datatype': Match,
                'validation': lambda match_hltv_id: match_hltv_id.isnumeric(),
                'message': 'Type match hltv id'
            }
        }

        super().__init__(inputs)

    def main(self, user_inputs):
        match: Match = user_inputs['match_hltv_id']

        match.load_page_data_by('hltv_id')
        match.store()
