from .event import Event
from .team import Team
from .page import Page
from ..utils import helpers
from ..utils.database.orms.orm import Orm
from ..utils.database.orms.match import Match as MatchORM


class Match(Page):
    def __init__(self, hltv_id=None):
        base_url = 'https://www.hltv.org/matches'
        searchable_data = {
            'hltv_id': {
                'value': hltv_id,
                'get_partial_uri': self.__get_partial_uri_by_hltv_id,
                'set_value': int
            }
        }
        self.__event_page = Event()
        orm = MatchORM(relationships={
            "events": self.__event_page.get_orm()
        })

        super().__init__(base_url, searchable_data, orm)

    def __get_partial_uri_by_hltv_id(self, hltv_id):
        return f"{hltv_id}/match"

    def __set_match_event_from_page(self, page):
        wrapper = page.find('div', {'class': {'standard-box', 'teamsBox'}})
        event_wrapper = wrapper.find('div', {'class', 'timeAndEvent'})
        event_partial_link = event_wrapper.select_one('.event.text-ellipsis').find('a').attrs['href']
        event_hltv_id = event_partial_link.split('/')[2]
        self.__event_page.set_searchable_data('hltv_id', event_hltv_id)
        self.__event_page.load_page_data_by('hltv_id')

    def __get_map_metadata_index(self, metadata, maps_metadata):
        maps_by_metadata = {
            'votation': None,
            'played': None
        }

        maps_mentadata_len = len(maps_metadata)

        if maps_mentadata_len == 3:
            maps_by_metadata['votation'] = 1
            maps_by_metadata['played'] = 2
        elif maps_mentadata_len == 2:
            maps_by_metadata['votation'] = 0
            maps_by_metadata['played'] = 1
        else:
            maps_by_metadata['played'] = 0

        return maps_by_metadata[metadata]

    def __get_side_index_in_team_map_result(self, team_map_result):
        position = team_map_result.attrs['class'][0]
        side_index_by_position = {
            'results-left': 0,
            'results-right': 1
        }

        return side_index_by_position[position]

    def __get_team_sides_results_from_map_results(self, team, map_results):
        team_name = team.select_one('div.results-teamname').get_text().lower()
        halfs_results = []
        side = map_results.select_one('div.results-center-half-score > span:nth-child(2)').attrs['class'][0]
        side_position_index = self.__get_side_index_in_team_map_result(team)
        sides_results = {
            't': 0,
            'ct': 0
        }

        for half_result in map_results.select_one('div.results-center-half-score').get_text().split(";"):
            halfs_results.append(half_result.replace("(", "").replace(")", "").strip())

        for half_result in halfs_results:
            side_result = half_result.split(':')[side_position_index]
            sides_results[side] += int(side_result)

            side = helpers.toggle_value(side, ['t', 'ct'])

        return {
            'name': team_name,
            'tr_rounds_wins': sides_results['t'],
            'ct_rounds_wins': sides_results['ct']
        }

    def get_match_result_from_page(self, page):
        wrapper = page.find('div', {'class': {'standard-box', 'teamsBox'}})
        teams = wrapper.findAll('div', {'class': 'team'})
        result_by_team = {}

        for team in teams:
            won = team.find('div', {'class': 'won'})
            lost = team.find('div', {'class': 'lost'})
            result = None

            if won is None and lost is None:
                result = team.find('div', {'class': 'tie'}).get_text()
            else:
                result = won.get_text() if won is not None else lost.get_text()

            team_name = team.find(
                'div', {'class': 'teamName'}
            ).get_text().lower()

            result_by_team[team_name] = int(result)

        return result_by_team

    def get_match_timestamp_from_page(self, page):
        wrapper = page.find('div', {'class': {'standard-box', 'teamsBox'}})
        timestamp_wrapper = wrapper.find('div', {'class', 'timeAndEvent'})

        timestamp = int(timestamp_wrapper.find(
            'div', {'class': 'time'}
        ).attrs['data-unix']) / 1000

        return timestamp

    def get_event_id_from_event(self):
        event_data = self.__event_page.get_page_data()
        match_orm: Orm = self.get_orm()
        event_orm: Orm = match_orm.get_relationship_orm('events')

        event_stored = event_orm.load_by_column('hltv_id', event_data['hltv_id'])

        if event_stored is None:
            match_orm.set_foreign_key_by_relationship('events')

        return event_orm.get_column('id')

    def get_maps_votation_from_page(self, page):
        maps_data = page.select('.g-grid.maps > div:first-child > div')
        votation_index = self.__get_map_metadata_index('votation', maps_data)

        if votation_index is None:
            return None

        maps_votation = maps_data[votation_index].select('div div:not(:last-child)')
        maps_votation_by_option = {
            'picked': 'picks',
            'removed': 'bans'
        }
        maps_voted_by_team = {}

        for map_votation in maps_votation:
            votation = {
                'team': None,
                'map': None
            }
            votation_text = map_votation.get_text()
            vote = None

            for vote_option in maps_votation_by_option:
                if vote_option in votation_text:
                    vote = vote_option
                    votation_splited = votation_text.split(vote)
                    team_name = votation_splited[0][3:-1]
                    map_name = votation_splited[1][1:]
                    votation = {
                        'team': team_name,
                        'map': map_name
                    }
                    vote = maps_votation_by_option[vote_option]

                    if team_name not in maps_voted_by_team:
                        maps_voted_by_team[team_name] = {
                            'picks': [],
                            'bans': []
                        }

                    break

            maps_voted_by_team[votation['team']][vote].append(votation['map'])

        return maps_voted_by_team

    def get_maps_played_from_page(self, page):
        maps_data = page.select('.g-grid.maps > div:first-child > div')
        maps_played_index = self.__get_map_metadata_index('played', maps_data)
        maps_played = maps_data[maps_played_index].select('div.mapholder')
        invalid_maps_names = ['tba', 'default']
        maps_played_by_team = {}

        for map_played in maps_played:
            optional_map = map_played.select_one('div.optional')
            map_name = map_played.select_one('div > div.mapname').get_text().lower()
            map_results = map_played.select_one('div.results')

            if optional_map is not None or map_name in invalid_maps_names or map_results is None:
                continue

            team_left = map_results.select_one('.results-left')
            results = map_results.select_one('.results-center')
            team_right = map_results.select_one('.results-right')

            team_left_map_result = self.__get_team_sides_results_from_map_results(team_left, results)
            team_right_map_result = self.__get_team_sides_results_from_map_results(team_right, results)

    def get_page_data_from_page(self, page):
        page = page.find('div', {'class': 'contentCol'})
        page_data = {}

        if page is not None:
            self.__set_match_event_from_page(page)

            page_data['results'] = self.get_match_result_from_page(page)
            page_data['matched_at'] = self.get_match_timestamp_from_page(page)
            page_data['event_id'] = self.get_event_id_from_event()
            page_data['maps_votation'] = self.get_maps_votation_from_page(page)
            page_data['maps_played'] = self.get_maps_played_from_page(page)

            return page_data

        return None

    def search_match_by_hltv_id(self, hltv_id=None):
        def get_match_data(match_page):
            if match_page is None:
                return None

            def get_result_and_event_and_match_timestamp(match_page):
                result_and_event_html = match_page.find(
                    'div', {'class': {'standard-box', 'teamsBox'}})
                teams_html = result_and_event_html.findAll(
                    'div', {'class': 'team'})
                event_html = result_and_event_html.find(
                    'div', {'class': 'timeAndEvent'})

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
                        result = None

                        if won is None and lost is None:
                            result = int(
                                team.find('div', {'class': 'tie'}).get_text())
                        else:
                            result = int(won.get_text()) if won is not None else int(
                                lost.get_text())

                        team_name = team.find(
                            'div', {'class': 'teamName'}).get_text().lower()
                        teams_results[team_name] = result

                    return teams_results

                def get_event_and_match_timestamp(event):
                    HLTV_ID = 2

                    event_anchor = event.find(
                        'div', {'class': {'event', 'text-ellipsis'}}).find('a')
                    event_name = event_anchor.attrs['title'].lower()
                    hltv_id = int(
                        event_anchor.attrs['href'].split('/')[HLTV_ID])

                    timestamp = int(event.find(
                        'div', {'class': 'time'}).attrs['data-unix']) / 1000

                    return {'event': {'name': event_name, 'hltv_id': hltv_id}, 'match_timestamp': timestamp}

                match_result = get_match_result(teams_html)
                event_and_match_timestamp = get_event_and_match_timestamp(
                    event_html)
                event = event_and_match_timestamp['event']
                timestamp = event_and_match_timestamp['match_timestamp']

                data['result'] = match_result
                data['event'] = event
                data['matched_at'] = int(timestamp)

                return data

            def get_maps_data_by_team(match_page):
                def get_dictonary_maps_by_metadata(maps_voted_and_maps_played_len):
                    maps_by_metadata = {
                        'voted': None,
                        'played': None
                    }

                    if maps_voted_and_maps_played_len == 3:
                        maps_by_metadata['voted'] = 1
                        maps_by_metadata['played'] = 2
                    elif maps_voted_and_maps_played_len == 2:
                        maps_by_metadata['voted'] = 0
                        maps_by_metadata['played'] = 1
                    else:
                        maps_by_metadata['played'] = 0

                    return maps_by_metadata

                def get_maps_picked_and_banned_by_team(maps_voted):
                    if maps_voted is None:
                        return {}
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

                        maps_picked_and_banned[team][picks_and_bans_by_vote[vote]].append(
                            map)

                    return maps_picked_and_banned

                def get_maps_played(maps_played):
                    def is_map_valid(map_name):
                        invalids_map_names = ['tba', 'default']

                        return map_name not in invalids_map_names

                    maps = maps_played.findAll('div', {'class': 'mapholder'})
                    maps_played_by_teams_results = {}

                    def toggle_side(side):
                        return 'ct' if side == 't' else 't'

                    for map in maps:
                        if map.find('div', {'class': 'optional'}) is not None:
                            continue

                        map_name = map.find('div', {'class': 'played'}).find(
                            'div', {'class': 'mapname'}).get_text().lower()

                        if not is_map_valid(map_name):
                            continue

                        LEFT = 0
                        SIDES_RESULTS = 1
                        RIGHT = 2

                        map_results = map.find('div', {'class': 'results'})

                        if map_results is None:
                            continue

                        results = [
                            sibling for sibling in map_results.contents[0].next_siblings if sibling != '\n']

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

                        sides_results_not_serialized = results[SIDES_RESULTS].findAll(
                            'span')
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
                            left_result[result_by_side[side]] = int(
                                half[LEFT_TEAM])
                            side = toggle_side(side)
                            right_result[result_by_side[side]] = int(
                                half[RIGHT_TEAM])

                        if map_name not in maps_played_by_teams_results:
                            maps_played_by_teams_results[map_name] = {}

                        maps_played_by_teams_results[map_name] = [left_result, right_result]

                    return maps_played_by_teams_results

                maps_voted_and_maps_played = []
                votation_and_maps_played = match_page.find('div', {'class': {'g-grid', 'maps'}}).find(
                    'div', {'class': {'col-6', 'col-7-small'}}).contents[0].next_siblings
                for sibling in votation_and_maps_played:
                    if sibling != '\n':
                        maps_voted_and_maps_played.append(sibling)

                maps_voted_and_maps_played_len = len(
                    maps_voted_and_maps_played)
                maps_by_metadata = get_dictonary_maps_by_metadata(
                    maps_voted_and_maps_played_len)

                if helpers.is_all_values_none(maps_by_metadata):
                    return None

                MAPS_VOTED = maps_by_metadata['voted']
                MAPS_PLAYED = maps_by_metadata['played']

                maps_voted = None

                if MAPS_VOTED is not None:
                    maps_voted = maps_voted_and_maps_played[MAPS_VOTED].find('div', {'class': 'padding'})

                maps_played = maps_voted_and_maps_played[MAPS_PLAYED]

                votation_by_team = get_maps_picked_and_banned_by_team(maps_voted)
                maps_played = get_maps_played(maps_played)

                if not votation_by_team and not maps_played:
                    return None

                return {
                    'votation_by_team': votation_by_team,
                    'maps_played': maps_played
                }

            def rearrange_match_data(match_data):
                def get_teams_from_result(result):
                    return [team for team in result]

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
                    'results_by_team': {team: {} for team in get_teams_from_result(match_data['result'])},
                    'event': match_data['event']
                }

                votation = None
                if match_data['votation_by_team']:
                    votation = match_data['votation_by_team']

                for team in match['results_by_team']:
                    match['results_by_team'][team]['result'] = match_data['result'][team]
                    match['results_by_team'][team]['votation'] = None if votation is None else votation[team]
                    match['results_by_team'][team]['maps_played'] = get_maps_played_and_team_result(
                        match_data['maps_played'], team)

                return match

            match_data = get_result_and_event_and_match_timestamp(match_page)

            if match_data is None:
                return None

            maps_data_by_team = get_maps_data_by_team(match_page)

            if maps_data_by_team is None:
                return None

            match_data.update(maps_data_by_team)

            return rearrange_match_data(match_data)

        hltv_id = hltv_id if hltv_id is not None else self.get_hltv_id()
        match_page = get_match_page_by_hltv_id(hltv_id)
        match = get_match_data(match_page)

        if match is not None:
            match['hltv_id'] = hltv_id

        return match

    def load_match_by_hltv_id(self, hltv_id=None):
        match_data = self.search_match_by_hltv_id(hltv_id)
        self.load_by_match_data(match_data)

    def store(self):
        def store_event(event):
            event_orm = EventORM()
            event_orm.set_columns(event)

            event_stored = event_orm.get_by_column('hltv_id', event['hltv_id'])

            if event_stored is None:
                return event_orm.create()

            return event_stored

        def store_match(match, event):
            if event is None:
                return None

            match_orm = MatchORM()
            match_orm.set_columns({
                'hltv_id': match['hltv_id'],
                'event_id': event['id'],
                'matched_at': match['matched_at']
            })

            match_stored = match_orm.get_by_column('hltv_id', match['hltv_id'])

            if match_stored is None:
                return match_orm.create()

            return match_stored

        '''
        there's duplicated code in this function

        in store_team_votation, store_team_map_played_and_result, i need to check
        if map is already stored in database, but i have duplicated the same code...
        '''
        def store_results_by_team(results_by_team, match):
            def store_team_result(team_id, match_id, result):
                match_team_result_orm = MatchTeamResultORM()
                match_team_result_orm.set_columns({
                    'team_id': team_id,
                    'result': result,
                    'match_id': match_id
                })
                match_team_result_orm.create()

            def store_team_votation(team_id, match_id, votation):
                if votation is None:
                    return None

                def store_picks(map_id, team_id, match_id):
                    match_map_picked_orm = MatchMapPickedORM()
                    match_map_picked_orm.set_columns({
                        'map_id': map_data['id'],
                        'team_id': team_id,
                        'match_id': match_id
                    })

                    match_map_picked_orm.create()

                def store_bans(map_id, team_id, match_id):
                    match_map_banned_orm = MatchMapBannedORM()
                    match_map_banned_orm.set_columns({
                        'map_id': map_data['id'],
                        'team_id': team_id,
                        'match_id': match_id
                    })

                    match_map_banned_orm.create()

                map_orm = MapORM()
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
                            is_map_stored = helpers.is_key_and_value_in_dictonary(
                                map_stored, 'name', map_name)

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

                            store_vote_by_type[vote_type](
                                map_data['id'], team_id, match_id)

            def store_team_map_played_and_result(team_id, match_id, maps_played):
                match_team_map_result_orm = MatchTeamMapResultORM()
                map_orm = MapORM()
                maps_stored = list(map_orm.get_all())

                for map_played in maps_played:
                    map_name = map_played['name']
                    map_data = None
                    is_map_stored = False

                    for map_stored in maps_stored:
                        is_map_stored = helpers.is_key_and_value_in_dictonary(
                            map_stored, 'name', map_name)

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

            if match is None:
                return None

            team_orm = TeamORM()
            teams_stored = list(team_orm.get_all())

            for team_name in results_by_team:
                team_data = None
                is_team_stored = False

                for team_stored in teams_stored:
                    is_team_stored = helpers.is_key_and_value_in_dictonary(
                        team_stored, 'name', team_name)

                    if is_team_stored:
                        team_data = team_stored
                        break

                if not is_team_stored:
                    team = Team(team_name)
                    team_searched = team.search_team_by_name()

                    if team_searched is not None:
                        team_orm.set_columns({
                            'name': team_name,
                            'hltv_id': team_searched['hltv_id']
                        })
                        team_data = team_orm.create()

                if team_data is not None:
                    teams_stored.append(team_data)

                    store_team_result(
                        team_data['id'], match['id'], results_by_team[team_name]['result'])
                    store_team_votation(
                        team_data['id'], match['id'], results_by_team[team_name]['votation'])
                    store_team_map_played_and_result(
                        team_data['id'], match['id'], results_by_team[team_name]['maps_played'])

        match = self.get_match_data()
        if match is None:
            print("match is none")
            return None

        event_row = store_event(match['event'].get_event_data())
        match_row = store_match(match, event_row)
        store_results_by_team(match['results_by_team'], match_row)
