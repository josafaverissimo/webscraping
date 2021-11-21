from .utils.webscraper import get_page
from .utils.database.orms.matches import Matches
from .utils.database.orms.events import Events
from datetime import datetime

def get_match_page_by_hltv_id(hltv_id):
    base_url = 'https://www.hltv.org/matches/'
    url = f'{base_url}{hltv_id}/match'

    match_page = get_page(url)

    if match_page is not None:
        return match_page.find('div', {'class': 'contentCol'})

    return None

def get_match_data(match_page, hltv_id):
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

            def toggle_side(side):
                return 'ct' if side == 't' else 't'

            for map in maps:
                if map.find('div', {'class': 'optional'}) is not None:
                    continue

                LEFT = 0
                SIDES_RESULTS = 1
                RIGHT = 2

                map_name = map.find('div', {'class': 'played'}).find('div', {'class': 'mapname'}).get_text().lower()
                results = [sibling for sibling in map.find('div', {'class': 'results'}).contents[0].next_siblings if sibling != '\n']

                left_result = {
                    'team': results[LEFT].find('div', {'class': 'results-teamname'}).get_text().lower(),
                    'ct_rounds_wins': None,
                    'tr_rounds_wins': None
                }
                right_result = {
                    'team': results[RIGHT].find('div', {'class': 'results-teamname'}).get_text().lower(),
                    'ct_rounds_wins': None,
                    'tr_rounds_wins': None
                }

                sides_results_not_serialized = results[SIDES_RESULTS].findAll('span')
                first_side_first_half = sides_results_not_serialized[1].attrs['class'][0]
                result_by_side = {
                    't': 'tr_rounds_wins',
                    'ct': 'ct_rounds_wins'
                }
                sides_result = "".join([character.get_text() for character in sides_results_not_serialized])
                not_overtime = sides_result.index(')')
                sides_result = sides_result[2:not_overtime].replace(' ', '')
                halfs = [half.split(':') for half in sides_result.split(';')]

                LEFT_TEAM = 0
                RIGHT_TEAM = 1

                side = first_side_first_half
                for half in halfs:
                    left_result[result_by_side[side]] = int(half[LEFT_TEAM])
                    side = toggle_side(side)
                    right_result[result_by_side[side]] = int(half[RIGHT_TEAM])

                if map_name not in maps_played_by_teams_results:
                    maps_played_by_teams_results[map_name] = {}

                maps_played_by_teams_results[map_name] = [left_result, right_result]

            return maps_played_by_teams_results

        return {
            'votation_by_team': get_maps_picked_and_banned_by_team(maps_voted),
            'maps_played': get_maps_played(maps_played)
        }

    match_data = get_result_and_event_and_match_timestamp(match_page)
    match_data['hltv_id'] = hltv_id
    match_data.update(get_maps_data_by_team(match_page))

    return match_data

def store_match(match):
    event_data = match['event']
    eventOrm = Events()
    eventOrm.set_columns(event_data)
    event = eventOrm.create()

    matchOrm = Matches()
    matchOrm.set_columns({
        'hltv_id': match['hltv_id'],
        'event_id': event['id'],
        'matched_at': match['matched_at']
    })
    match = matchOrm.create()

    print(match)


#TODO
#make a function that pass hltv_id to get_match_page and get_match_data

#HOW TODO
'''
    def get_match(hltv_id):
        match_data = get_match_data(get_match_page_by_hltv_id(hltv_id))
        match_data['hltv_id'] = hltv_id

        return match_data
'''

match_page = get_match_page_by_hltv_id(2352893)
store_match(get_match_data(match_page,2352893))
