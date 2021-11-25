from .utils.webscraper import get_page
from .utils.database.orms.event import Event
from .utils.database.orms.match import Match
from .utils.database.orms.match_map_picked import MatchMapPicked
from .utils.database.orms.match_map_banned import MatchMapBanned
from .utils.database.orms.match_team_result import MatchTeamResult
from .utils.database.orms.match_team_map_result import MatchTeamMapResult
from .utils.database.orms.team import Team
from .utils.database.orms.map import Map
from .utils.helpers import is_key_and_value_in_dictonary
from .team import get_team_by_name
from datetime import datetime
import re

def get_match(hltv_id):
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

                picks_and_bans_by_vote = {
                    'picked': 'picks',
                    'removed': 'bans'
                }

                for map in maps:
                    votation = map.get_text()
                    vote = None

                    for vote_option in picks_and_bans_by_vote:
                        if vote_option in votation:
                            votation = votation.split(vote_option)
                            team_name = votation[0][3:-1]
                            map_name = votation[1][1:]
                            votation = {
                                'team': team_name,
                                'map': map_name
                            }
                            vote = vote_option
                            break

                    team = votation['team'].lower()
                    map = votation['map'].lower()
                    
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

        def rearrange_match_data(match_data):
            def get_teams_from_votation(votation_by_team):
                return [team for team in votation_by_team]

            def get_maps_played_and_team_result(maps_played, team_name):
                maps_played_and_result = []

                for map_name in maps_played:
                    teams_results = maps_played[map_name]

                    for team_result in teams_results:
                        if team_result['team'] == team_name:
                            map_played = {
                                'name': map_name,
                                'ct_rounds_wins': team_result['ct_rounds_wins'],
                                'tr_rounds_wins': team_result['tr_rounds_wins']
                            }

                            maps_played_and_result.append(map_played)

                            break

                return maps_played_and_result


            match = {
                'matched_at': match_data['matched_at'],
                'teams': {team: {} for team in get_teams_from_votation(match_data['votation_by_team'])},
                'event': match_data['event']
            }

            for team in match['teams']:
                match['teams'][team]['result'] = match_data['result'][team]
                match['teams'][team]['votation'] = match_data['votation_by_team'][team]
                match['teams'][team]['maps_played'] = get_maps_played_and_team_result(match_data['maps_played'], team)

            return match

        match_data = get_result_and_event_and_match_timestamp(match_page)
        match_data.update(get_maps_data_by_team(match_page))

        return rearrange_match_data(match_data)

    match_page = get_match_page_by_hltv_id(hltv_id)
    match = get_match_data(match_page)
    match['hltv_id'] = hltv_id

    return match

def store_event(event):
    event_orm = Event()
    event_orm.set_columns(event)

    is_event_stored = event_orm.get_by_column('hltv_id', event['hltv_id']) != None

    if not is_event_stored:
        return event_orm.create()

    return None

def store_match(match, event):
    if event is not None:
        match_orm = Match()
        match_orm.set_columns({
            'hltv_id': match['hltv_id'],
            'event_id': event['id'],
            'matched_at': match['matched_at']
        })

        is_match_stored = match_orm.get_by_column('hltv_id', match['hltv_id']) != None

        if not is_match_stored:
            return match_orm.create()

        return None

'''
there's duplicated code in this function

in store_team_votation, store_team_map_played_and_result, i need to check
if map is already stored in database, but i have duplicated the same code...
'''
def store_teams_data(teams_data, match):
    def store_team_result(team_id, match_id, result):
        match_team_result_orm = MatchTeamResult()
        match_team_result_orm.set_columns({
            'team_id': team_id,
            'result': result,
            'match_id': match_id
        })
        match_team_result_orm.create()

    def store_team_votation(team_id, match_id, votation):
        def store_picks(map_id, team_id, match_id):
            match_map_picked_orm = MatchMapPicked()
            match_map_picked_orm.set_columns({
                'map_id': map_data['id'],
                'team_id': team_id,
                'match_id': match_id
            })

            match_map_picked_orm.create()

        def store_bans(map_id, team_id, match_id):
            match_map_banned_orm = MatchMapBanned()
            match_map_banned_orm.set_columns({
                'map_id': map_data['id'],
                'team_id': team_id,
                'match_id': match_id
            })

            match_map_banned_orm.create()

        map_orm = Map()
        maps_stored = list(map_orm.get_all())
        store_vote_by_type = {
            'picks': store_picks,
            'bans': store_bans
        }

        for vote_type in votation:
            maps_voted = votation[vote_type]
            for map_name in maps_voted:
                map_data = None
                is_map_stored = False

                for map_stored in maps_stored:
                    is_map_stored = is_key_and_value_in_dictonary(map_stored, 'name', map_name)

                    if is_map_stored:
                        map_data = map_stored
                        break

                if not is_map_stored:
                    map_orm.set_columns({
                        'name': map_name
                    })
                    map_data = map_orm.create()

                if map_data is not None:
                    maps_stored.append(map_data)

                    store_vote_by_type[vote_type](map_data['id'], team_id, match_id)

    def store_team_map_played_and_result(team_id, match_id, maps_played):
        match_team_map_result_orm = MatchTeamMapResult()
        map_orm = Map()
        maps_stored = list(map_orm.get_all())

        for map_played in maps_played:
            map_name = map_played['name']
            map_data = None
            is_map_stored = False

            for map_stored in maps_stored:
                is_map_stored = is_key_and_value_in_dictonary(map_stored, 'name', map_name)

                if is_map_stored:
                    map_data = map_stored
                    break
            if not is_map_stored:
                map_orm.set_columns({
                    'name': map_name
                })
                map_data = map_orm.create()

            if map_data is not None:
                maps_stored.append(map_data)

                match_team_map_result_orm.set_columns({
                    'team_id': team_id,
                    'map_id': map_data['id'],
                    'match_id': match_id,
                    'ct_rounds_wins': map_played['ct_rounds_wins'],
                    'tr_rounds_wins': map_played['tr_rounds_wins'],
                })

                match_team_map_result_orm.create()

    if match is not None:
        team_orm = Team()
        teams_stored = list(team_orm.get_all())

        for team_name in teams_data:
            team_data = None
            is_team_stored = False

            for team_stored in teams_stored:
                is_team_stored = is_key_and_value_in_dictonary(team_stored, 'name', team_name)

                if is_team_stored:
                    team_data = team_stored
                    break

            if not is_team_stored:
                team_searched = get_team_by_name(team_name)

                if team_searched is not None:
                    team_orm.set_columns({
                        'name': team_name,
                        'hltv_id': team_searched['hltv_id']
                    })
                    team_data = team_orm.create()

            if team_data is not None:
                teams_stored.append(team_data)

                store_team_result(team_data['id'], match['id'], teams_data[team_name]['result'])
                store_team_votation(team_data['id'], match['id'], teams_data[team_name]['votation'])
                store_team_map_played_and_result(team_data['id'], match['id'], teams_data[team_name]['maps_played'])

def store_match_data(match):
    event_row = store_event(match['event'])
    match_row = store_match(match, event_row)
    store_teams_data(match['teams'], match_row)

match = get_match(2352808)
store_match_data(match)
