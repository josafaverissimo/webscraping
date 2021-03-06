from bs4 import BeautifulSoup
from .page import Page
from ..utils.database.orms.orm import Orm
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
        orm: Orm = EventORM()

        super().__init__(base_url, searchable_data, orm)

    def __get_partial_uri_by_hltv_id(self, hltv_id) -> str:
        return f"{hltv_id}/event"

    def get_event_name(self, page: BeautifulSoup) -> str:
        wrapper = page.find('a', {'class': 'event-hub-top'})
        name = wrapper.find('h1', {'class': 'event-hub-title'}).get_text()

        return name.lower()

    def get_event_hltv_id(self, page: BeautifulSoup) -> int:
        hltv_id = self.get_searchable_data('hltv_id')

        if hltv_id is None:
            wrapper = page.select_one('div.event-hub-bottom')
            anchor = wrapper.select_one('a.event-hub_link')
            hltv_id = int(anchor.attrs['href'].split('/')[2])

        return hltv_id

    def get_page_data_from_page(self, page: BeautifulSoup) -> dict:
        page = page.find('div', {'class': 'event-page'})
        page_data = {}

        if page is not None:
            page_data['name'] = self.get_event_name(page)
            page_data['hltv_id'] = self.get_event_hltv_id(page)

        return page_data

    def store(self) -> dict:
        page_data = self.get_page_data()
        event_orm: Orm = self.get_orm()

        if page_data is not None:
            event_orm.set_columns(page_data)

            event_stored = event_orm.get_by_column('hltv_id', page_data['hltv_id'])

            if event_stored is not None:
                return event_stored

            return event_orm.create()

        return {}
