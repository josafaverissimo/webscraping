from ..utils.requester import get_page
from .match import Match

class Result:
    def __init__(self, team_hltv_id):
        self.__result_data = {
            'team_hltv_id': team_hltv_id,
            'matches_hltv_ids': []
        }

    def get_team_hltv_id(self):
        return self.__result_data['team_hltv_id']

    def set_team_hltv_id(self, hltv_id):
        self.__result_data['team_hltv_id'] = int(hltv_id)

    def get_matches_hltv_ids(self):
        return self.__result_data['matches_hltv_ids']

    def set_matches_hltv_ids(self, matches_hltv_ids):
        self.__result_data['matches_hltv_ids'] = matches_hltv_ids
    
    def get_team_matches_hltv_ids(self, team_hltv_id = None):
        def get_results_urls(team_hltv_id, total_matches):
            MATCH_PER_PAGE = 100
            base_url = "https://www.hltv.org/results?"
            urls = []
            total_matches //= MATCH_PER_PAGE

            for offset in range(1, total_matches + 1):
                matches_ordered_by_offset_in_page = offset * MATCH_PER_PAGE
                urls.append(f"{base_url}offset={matches_ordered_by_offset_in_page}&team={team_hltv_id}")

            return urls

        def get_total_matches_from_result_page(result_page):
            pagination = result_page.find('span', {'class': 'pagination-data'}).get_text()
            total_matches = int(pagination.split('of')[1].lstrip())

            return total_matches

        def get_matches_hltv_ids_from_result_page(result_page):
            results_sublist = result_page.find_all('div', {'class': 'results-sublist'})
            matches_hltv_ids = []

            for day_results in results_sublist:
                results = day_results.find_all('div', {'class': 'result-con'})

                for result in results:
                    match_link = result.find('a', {'class': 'a-reset'})
                    match_hltv_id = int(match_link.attrs['href'].split('/')[2])
                    matches_hltv_ids.append(match_hltv_id)

            return matches_hltv_ids

        team_hltv_id = team_hltv_id if team_hltv_id is not None else self.get_team_hltv_id()
        base_url = "https://www.hltv.org/results?"
        url = f"{base_url}team={team_hltv_id}"
        result_page = get_page(url)
        matches_hltv_ids = []

        if result_page is None:
            return None

        result_page = result_page.find('div', {'class': 'results'})
        total_matches = get_total_matches_from_result_page(result_page)
        urls = get_results_urls(team_hltv_id, total_matches)
        
        for match_hltv_id in get_matches_hltv_ids_from_result_page(result_page):
            matches_hltv_ids.append(match_hltv_id)

        for url in urls:
            result_page = get_page(url)

            if result_page is None:
                continue

            for match_hltv_id in get_matches_hltv_ids_from_result_page(result_page):
                matches_hltv_ids.append(match_hltv_id)

        return matches_hltv_ids

    def load_team_matches_hltv_ids(self, team_hltv_id = None):
        matches_hltv_ids = self.get_team_matches_hltv_ids(team_hltv_id)
        self.set_matches_hltv_ids(matches_hltv_ids)

    def store(self):
        matches_hltv_ids = self.get_matches_hltv_ids()
        for match_hltv_id in matches_hltv_ids:
            match = Match(match_hltv_id)
            match.load_match_by_hltv_id(match_hltv_id)
            match.store()
