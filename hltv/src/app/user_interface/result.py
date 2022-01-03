from .interface import Boilerplate
from ..pages.result import Result as ResultPage


class Result(Boilerplate):
    def __init__(self):
        inputs = {
            'result': {
                'datatype': ResultPage,
                'validation': lambda team_hltv_id: team_hltv_id.isnumeric(),
                'message': 'Type team hltv id'
            }
        }

        super().__init__(inputs)

    def main(self, user_inputs):
        result: ResultPage = user_inputs['result']

        result.load_page_data_by('team_hltv_id')
        result.store()
