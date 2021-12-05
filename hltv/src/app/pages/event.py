from .page import Page

class Event(Page):
    def __init__(self, hltv_id = None):
        base_url = 'https://www.hltv.org/events'
        
        searchable_data = {
            'hltv_id': {
                'value': hltv_id,
                'get': self.__get_by_hltv_id
                'set': int
            }
        }

        super().__init__(base_url, searchable_data)

    def __get_by_hltv_id(self, hltv_id = None):
        if hltv_id is not None:
            self._set_searchable_value('hltv_id', hltv_id)

        hltv_id = self.get_searchable_value('hltv_id')

        page = self.get_html()

        return page

