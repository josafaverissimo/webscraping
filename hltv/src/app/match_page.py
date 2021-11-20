from .utils.webscraper import get_page

def get_match_page_by_hltv_id(hltv_id):
    base_url = 'https://www.hltv.org/matches/'
    url = f'{base_url}{hltv_id}/match'

    match_page = get_page(url)

    if match_page is not None:
        return match_page.find('div', {'class': 'contentCol'})

    return None

def get_match_data(match_page):
    if match_page is None:
        return None

    def get_result_and_event_and_match_timestamp(match_page):
        result_and_event_html = match_page.find('div', {'class': {'standard-box', 'teamsBox'}})
        teams_html = result_and_event_html.findAll('div', {'class': 'team'})
        event_html = result_and_event_html.find('div', {'class': 'timeAndEvent'})

        data = {
            'result': {},
            'event': {},
            'matched_at': None
        }

        def get_match_result(teams):
            teams_results = {}

            for team in teams:
                won = team.find('div', {'class': 'won'})
                lost = team.find('div', {'class': 'lost'})
                team_name = team.find('div', {'class': 'teamName'}).get_text().lower()

                teams_results[team_name] = int(won.get_text()) if won is not None else int(lost.get_text())

            return teams_results

        def get_event_and_match_timestamp(event):
            HLTV_ID = 2

            event_anchor = event.find('div', {'class': {'event', 'text-ellipsis'}}).find('a')
            event_name = event_anchor.attrs['title']
            hltv_id = event_anchor.attrs['href'].split('/')[HLTV_ID]

            timestamp = event.find('div', {'class': 'time'}).attrs['data-unix']

            return {'event': {'name': event_name, 'hltv_id': hltv_id}, 'match_timestamp': timestamp}

        match_result = get_match_result(teams_html)
        event_and_match_timestamp = get_event_and_match_timestamp(event_html)
        event = event_and_match_timestamp['event']
        timestamp = event_and_match_timestamp['match_timestamp']

        data['result'] = match_result
        data['event'] = event
        data['matched_at'] = int(timestamp)

        return data

    print(get_result_and_event_and_match_timestamp(match_page))


match_page = get_match_page_by_hltv_id(2352893)
get_match_data(match_page)
