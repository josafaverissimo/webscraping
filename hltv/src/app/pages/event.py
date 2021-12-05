from .page import Page
from ..utils.database.orms.event import Event as EventORM


class Event(Page):
    def __init__(self, hltv_id=None):
        base_url = 'https://www.hltv.org/events'
        searchable_data = {
            'hltv_id': {
                'value': hltv_id,
                'get_partial_uri': self.__get_partial_uri_by_hltv_id,
                'set_value': int
            }
        }
        orm = EventORM()

        super().__init__(base_url, searchable_data, orm)

    def __get_partial_uri_by_hltv_id(self, hltv_id):
        return f"{hltv_id}/event"

    def get_event_name(self, page):
        wrapper = page.find('a', {'class': 'event-hub-top'})
        name = wrapper.find('h1', {'class': 'event-hub-title'}).get_text()

        return name.lower()

    def get_event_hltv_id(self, page):
        hltv_id = self.get_searchable_data('hltv_id')

        if hltv_id is None:
            wrapper = page.find('div', {'class': 'event-hub-bottom'})
            anchor = wrapper.find('a', {'class': 'event-hub-link'})
            hltv_id = anchor.attrs['href'].split('/')[2]

        return int(hltv_id)

    def set_page_data_by(self, searchable_data_name, searchable_data_value=None):
        page = self.get_page_by_searchable_data(
            searchable_data_name, searchable_data_value)
        page_data = {}

        if page is not None:
            page = page.find('div', {'class': 'event-page'})

            page_data['name'] = self.get_event_name(page)
            page_data['hltv_id'] = self.get_event_hltv_id(page)

            self._set_page_data(page_data)

    def store(self):
        page_data = self.get_page_data()
        event_orm = self._get_orm()

        if page_data is not None:
            event_orm.set_columns(page_data)

            return event_orm.create()

        return None
