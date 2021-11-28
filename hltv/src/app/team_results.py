from .utils.webscraper import get_page
from .match_page import get_match
from .match_page import store_match_data

def get_team_matches_hltv_ids(team_hltv_id):
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

    base_url = "https://www.hltv.org/results?"
    url = f"{base_url}team={team_hltv_id}"
    result_page = get_page(url)
    matches_hltv_ids = []

    if result_page is not None:
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

def store_matches(matches_hltv_ids):
    for match_hltv_id in matches_hltv_ids:
        match_data = get_match(match_hltv_id)
        store_match_data(match_data)

matches_hltv_ids = get_team_matches_hltv_ids(9215)
store_matches(matches_hltv_ids)
