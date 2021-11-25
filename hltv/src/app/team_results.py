from .utils.webscraper import get_page

def get_team_results(team_hltv_id):
    def get_results_urls(team_hltv_id, total_matches):
        MATCH_PER_PAGE = 100
        base_url = "https://www.hltv.org/results?"
        urls = []
        total_matches //= MATCH_PER_PAGE

        for offset in range(1, total_matches + 1):
            matches_ordered_by_offset_in_page = offset * MATCH_PER_PAGE
            urls.append(f"{base_url}offset={matches_ordered_by_offset_in_page}?team={team_hltv_id}")

        return urls

    def get_total_matches_from_result_page(result_page):
        pagination = result_page.find('span', {'class': 'pagination-data'}).get_text()
        total_matches = int(pagination.split('of')[1].lstrip())

        return total_matches

    def get_matches_hltv_id_from_result_page(result_page):
        pass

    base_url = "https://www.hltv.org/results?"
    url = f"{base_url}team={team_hltv_id}"
    result_page = get_page(url)
    matches_hltv_id = []

    if result_page is not None:
        total_matches = get_total_matches_from_result_page(result_page)
        urls = get_results_urls(team_hltv_id, total_matches)



get_team_results(7175)
