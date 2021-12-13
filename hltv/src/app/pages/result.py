from .match import Match
from .page import Page
from ..utils import requester


class Result(Page):
    def __init__(self, team_hltv_id: int = None):
        base_url = 'https://www.hltv.org/results'
        searchable_data = {
            'team_hltv_id': {
                'value': team_hltv_id,
                'get_partial_uri': self.__get_partial_uri_by_team_hltv_id,
                'set_value': int
            }
        }
        self.__match_page = Match()

        super().__init__(base_url, searchable_data)

    def __get_partial_uri_by_team_hltv_id(self, team_hltv_id):
        return f'?team={team_hltv_id}'

    def __get_total_matches_from_page(self, page):
        pagination = page.select_one('span.pagination-data').get_text()
        total_matches = int(pagination.split('of')[1].strip())

        return total_matches

    def __get_all_results_urls_from_page(self, page):
        MATCHES_PER_PAGE = 100
        team_hltv_id = self.get_searchable_data('team_hltv_id')

        total_matches = self.__get_total_matches_from_page(page)
        total_results_pages = total_matches // MATCHES_PER_PAGE

        base_url = self.get_base_url()
        urls = []

        for offset in range(1, total_results_pages + 1):
            page_offset = offset * MATCHES_PER_PAGE
            urls.append(f'{base_url}?offset={page_offset}&team={team_hltv_id}')

        return urls

    def __get_matches_hltv_ids_from_page(self, page):
        results_urls = self.__get_all_results_urls_from_page(page)
        pages = [page] + requester.get_pages_from_urls(results_urls, lambda page: page.select_one('div.results'))
        matches_hltv_ids = []

        for page in pages:
            results_sublist = page.select('div.results-sublist')

            for day_results in results_sublist:
                results = day_results.select('div.result-con')

                for result in results:
                    match_url = result.select_one('a.a-reset')
                    match_hltv_id = int(match_url.attrs['href'].split('/')[2])
                    matches_hltv_ids.append(match_hltv_id)

        return matches_hltv_ids

    def get_page_data_from_page(self, page):
        page = page.select_one('div.results')
        page_data = {}

        if page is not None:
            page_data['matches_hltv_ids'] = self.__get_matches_hltv_ids_from_page(page)

            return page_data

        return None

    def store(self):
        matches_hltv_ids = self.get_page_data('matches_hltv_ids')

        for match_hltv_id in matches_hltv_ids:
            self.__match_page.set_searchable_data('hltv_id', match_hltv_id)
            self.__match_page.load_page_data_by('hltv_id')
            self.__match_page.store()
