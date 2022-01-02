from .page import Page
from bs4 import BeautifulSoup
from ..utils import requester
from ..utils.database.orms.orm import Orm
from ..utils.database.orms.map import Map as MapORM


class Map(Page):
    def __init__(self, map_name: str = None):
        base_url = 'https://www.hltv.org/stats/maps'
        searchable_data = {
            'map_name': {
                'value': map_name,
                'get_partial_uri': self.__get_partial_uri_by_map_name,
                'set_value': str
            }
        }
        orm: Orm = MapORM()

        super().__init__(base_url, searchable_data, orm)

        self.__maps_partial_uri_by_name = None
        self.__set_maps_partial_uri()

    def __get_maps_partial_uri_from_page(self, page: BeautifulSoup) -> dict:
        maps_anchors = page.select('nav.g-grid.maps-navigation > a')
        maps_data = {}

        for map_anchor in maps_anchors:
            map_partial_uri = map_anchor.attrs['href'].replace('/stats/maps/', '')
            map_name = map_anchor.select_one('div.maps-navigation-desc').get_text().lower()

            maps_data[map_name] = map_partial_uri

        return maps_data

    def __set_maps_partial_uri(self):
        page = requester.get_page(self.get_base_url())

        if page is not None:
            page = page.select_one('div.contentCol')
            maps_partial_uri_by_name = self.__get_maps_partial_uri_from_page(page)

            self.__maps_partial_uri_by_name = maps_partial_uri_by_name

    def __get_partial_uri_by_map_name(self, map_name):
        map_name = map_name.lower()

        return self.__maps_partial_uri_by_name[map_name]

    def __get_map_name_from_page(self, page):
        return page.select_one('h1.standard-headline.inline').get_text().split(' ')[-1].lower()

    def get_maps_partial_uri_by_map_name(self):
        return self.__maps_partial_uri_by_name

    def get_page_data_from_page(self, page):
        page = page.select_one('div.contentCol')
        page_data = {}

        if page is not None:
            page_data['name'] = self.__get_map_name_from_page(page)

            return page_data

    def store(self):
        orm = self.get_orm()
        page_data = self.get_page_data()

        if page_data is None:
            return None

        map_stored = orm.get_by_column('name', page_data['name'])

        if map_stored is not None:
            return map_stored

        orm.set_columns(page_data)
        return orm.create()

    def store_all(self):
        maps_names = self.get_maps_partial_uri_by_map_name().keys()

        for map_name in maps_names:
            self.set_searchable_data('map_name', map_name)
            self.load_page_data_by('map_name')
            self.store()
