from ..utils import requester
from ..utils.database.orms.orm import Orm


class Page:
    def __init__(self, base_url: str, searchable_data: str, orm: Orm = None, partial_uri=None):
        self.__base_url = base_url
        self.__page_data = None
        self.__searchable_data = searchable_data
        self.__url = None
        self.__current_url = None
        self.__html = None
        self.__orm = orm

        self.__set_searchable_data_values()

        if partial_uri is not None:
            self.__set_partial_uri(partial_uri)

    def __set_searchable_data_values(self):
        for name in self.__searchable_data:
            value = self.__searchable_data[name]['value']
            self.set_searchable_data(name, value)

    def __get_html(self):
        url = self.get_url()

        if self.__was_url_changed():
            html = requester.get_page(url)
            self.__set_html(html)
            self.__current_url = url

            return html

        return self.__html

    def __set_html(self, html):
        self.__html = html

    def __set_partial_uri(self, uri):
        if uri is not None:
            self.__url = self.get_base_url() + "/" + uri

    def __was_url_changed(self):
        url = self.get_url()

        return url != self.__current_url

    def get_orm(self):
        return self.__orm

    def load_page_data_by(self, searchable_data_name, searchable_data_value=None):
        page = self.get_page_by_searchable_data(searchable_data_name, searchable_data_value)

        if page is None:
            return None

        page_data = self.get_page_data_from_page(page)
        orm = self.get_orm()

        if orm is not None:
            orm.reset_columns_values()
            orm.set_columns(page_data)

        self._set_page_data(page_data)

        return page_data

    def _set_page_data(self, page_data):
        self.__page_data = page_data

    def set_searchable_data(self, name, value=None):
        if name in self.__searchable_data:
            searchable_data = self.__searchable_data[name]
            searchable_data_value = searchable_data['set_value'](value) if value is not None else None

            self.__searchable_data[name]['value'] = searchable_data_value

    def get_searchable_data(self, searchable_data_name):
        if searchable_data_name in self.__searchable_data:
            return self.__searchable_data[searchable_data_name]['value']

    def get_page_by_searchable_data(self, searchable_data_name, searchable_data_value=None):
        if searchable_data_name in self.__searchable_data:
            if searchable_data_value is not None:
                self.set_searchable_data(
                    searchable_data_name, searchable_data_value)

            searchable_data_value = self.get_searchable_data(
                searchable_data_name)

            if searchable_data_value is not None:
                partial_uri = self.__searchable_data[searchable_data_name]['get_partial_uri'](
                    searchable_data_value)

                self.__set_partial_uri(partial_uri)

                return self.__get_html()

        return None

    def get_url(self):
        return self.__url

    def get_base_url(self):
        return self.__base_url

    def get_page_data(self, index=None):
        return self.__page_data if index is None else self.__page_data[index]
