from .interface import Boilerplate
from ..pages.event import Event as EventPage


class Event(Boilerplate):
    def __init__(self):
        inputs = {
            'event': {
                'datatype': EventPage,
                'validation': lambda event_hltv_id: event_hltv_id.isnumeric(),
                'message': 'Type event hltv id'
            }
        }

        super().__init__(inputs)

    def main(self, user_inputs):
        event: EventPage = user_inputs['event']

        event.load_page_data_by('hltv_id')
        event.store()
