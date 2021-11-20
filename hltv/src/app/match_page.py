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

    match_data = {}

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
            event_name = event_anchor.attrs['title'].lower()
            hltv_id = int(event_anchor.attrs['href'].split('/')[HLTV_ID])

            timestamp = int(event.find('div', {'class': 'time'}).attrs['data-unix']) / 1000

            return {'event': {'name': event_name, 'hltv_id': hltv_id}, 'match_timestamp': timestamp}

        match_result = get_match_result(teams_html)
        event_and_match_timestamp = get_event_and_match_timestamp(event_html)
        event = event_and_match_timestamp['event']
        timestamp = event_and_match_timestamp['match_timestamp']

        data['result'] = match_result
        data['event'] = event
        data['matched_at'] = int(timestamp)

        return data

    def get_maps_data_by_team(match_page):
        MAPS_PICKED = 1
        MAPS_PLAYED = 2

        maps_picked_and_maps_played = []
        votation_and_maps_played = match_page.find('div', {'class': {'g-grid', 'maps'}}).find('div', {'class': {'col-6', 'col-7-small'}}).contents[0].next_siblings
        for sibling in votation_and_maps_played:
            if sibling != '\n':
                maps_picked_and_maps_played.append(sibling)

        maps_voted = maps_picked_and_maps_played[MAPS_PICKED].find('div', {'class': 'padding'})
        maps_played = maps_picked_and_maps_played[MAPS_PLAYED]

        def get_maps_picked_and_banned_by_team(maps_voted):
            LAST = -1
            maps = maps_voted.findAll('div')[:LAST]
            maps_picked_and_banned = {}

            TEAM = 1
            PICKED_OR_BANNED = 2
            MAP = 3

            picks_and_bans_by_vote = {
                'picked': 'picks',
                'removed': 'bans'
            }

            for map in maps:
                votation = map.get_text().split(' ')
                team = votation[TEAM].lower()
                vote = votation[PICKED_OR_BANNED]
                map = votation[MAP].lower()
                
                if team not in maps_picked_and_banned:
                    maps_picked_and_banned[team] = {
                        'picks': [],
                        'bans': []
                    }
                
                maps_picked_and_banned[team][picks_and_bans_by_vote[vote]].append(map)

            return maps_picked_and_banned

        def get_maps_played(maps_played):
            maps = maps_played.findAll('div', {'class': 'mapholder'})
            maps_played_by_teams_results = {}

            for map in maps:
                map_name = map.find('div', {'class': 'played'}).find('div', {'class': 'mapname'}).get_text().lower()
                results = map.find('div', {'class': {'results', 'played'}})
                left_result = {
                    'team': results.find('div', {'class': 'results-left'}).find('div', {'class': 'results-teamname'}).get_text().lower(),
                    'ct_rounds_wins' None,
                    'tr_rounds_wins': None
                }
                right_result = {
                    'team': results.find('div', {'class': 'results-right'}).find('div', {'class': 'results-teamname'}).get_text().lower(),
                    'ct_rounds_wins' None,
                    'tr_rounds_wins': None
                }

                #TODO
                '''
                    get ct rounds wins and tr rounds wins in <div class="results-half-score>"
                '''
                #HOW TODO
                '''
                    get all span tags text and split by " " to valid if there was overtime
                    if you splited string by " " and get a list lower than 2, so there was not overtime
                    get half's sum of left side and right side, to know if is ct or tr, save <span class="ct"> and determine its side, if 1 is tr else ct
                    go ahead!
                '''

                if map_name not in maps_played_by_teams_results:
                    maps_played_by_teams_results[map_name] = {}

                maps_played_by_teams_results[map_name] = [left_result, right_result]

        return get_maps_picked_and_banned_by_team(maps_voted)



    match_data = get_result_and_event_and_match_timestamp(match_page)



    get_maps_data_by_team(match_page)

    match_data = get_result_and_event_and_match_timestamp(match_page)
    match_data.update(get_maps_data_by_team(match_page))
    return match_data

match_page = get_match_page_by_hltv_id(2352893)
print(get_match_data(match_page))
