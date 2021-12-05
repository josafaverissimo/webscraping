from ..utils import requester

class Page:
    def __init__(self, base_url, searchable_data, uri = None):
        self.__base_url = base_url
        self.__page_data = None
        self.__searchable_data = searchable_data
        self.__url = None
        self.__current_url = None
        self.__html = None

        self._set_searchable_data()

        if uri is not None:
            self.set_uri(uri)

    def _set_searchable_data(self):
        for name in self.searchable_by:
            value = self.searchable_by[name]['value']
            self.__set_searchable_value(name, value)

    def _set_searchable_data(self, name, value = None):
        if name in self.searchable_by:
            gettable = self.searchable_by[name]        
            gettable_value = gettable['set'](value) if value is not None else None

            self.searchable_by[name]['value'] = gettable_value            

    def __was_url_changed(self):
        url = self.get_url()

        return url == self.__current_url

    def get_searchable_data(self, searchable_data_name):
        if searchable_data_name in self.__searchable_data:
            return self.__searchable_data[searchable_data_name]['value']

    def get_page_data_by_searchable_data(self, searchable_data_name, searchable_data_value = None):
        if searchable_value_name in self.__searchable_data:
            return self.__searchable_data[searchable_value_name]['get'](searchable_value)

    def get_url(self):
        return self.__url

    def set_uri(self, uri):
        self.__url = self.get_base_url() + "/" + uri        

    def get_html(self):
        url = self.get_url()

        if url is not None:
            if self.__was_url_changed():
                html = requester.get_page(url)
                self.__set_html(html)
                self.__current_url = url

                return html

        return None

    def __set_html(self, html):
        self.__html = html

    def get_base_url(self):
        return self.__base_url

    def get_page_data(self):
        return self.__page_data

    