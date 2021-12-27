from .event import Event
from .team import Team
from .page import Page
from ..utils import helpers
from ..utils.database.orms.orm import Orm
from ..utils.database.orms.map import Map as MapORM
from ..utils.database.orms.match_map_banned import MatchMapBanned as MatchMapBannedORM
from ..utils.database.orms.match_map_picked import MatchMapPicked as MatchMapPickedORM
from ..utils.database.orms.match import Match as MatchORM
from ..utils.database.orms.match_team_result import MatchTeamResult as MatchTeamResultORM
from ..utils.database.orms.match_team_map_result import MatchTeamMapResult as MatchTeamMapResultORM


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
        self.__team_page = Team()

        orm = MatchORM(relationships={
            "events": self.__event_page.get_orm()
        })

        self.__map_orm = MapORM()

        self.__match_map_picked_orm = MatchMapPickedORM(relationships={
            'teams': self.__team_page.get_orm(),
            'maps': self.__map_orm,
            'matches': orm
        })

        self.__match_map_banned_orm = MatchMapBannedORM(relationships={
            'teams': self.__team_page.get_orm(),
            'maps': self.__map_orm,
            'matches': orm
        })

        self.__match_team_result_orm = MatchTeamResultORM(relationships={
            'teams': self.__team_page.get_orm(),
            'matches': orm
        })

        self.__match_team_map_result_orm = MatchTeamMapResultORM(relationships={
            'maps': self.__map_orm,
            'teams': self.__team_page.get_orm(),
            'matches': orm
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

    def __set_team_page_data_from_team_name(self, team_name):
        self.__team_page.set_searchable_data('team_name', team_name)
        self.__team_page.load_page_data_by('team_name')

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

    def __get_map_result_halfs(self, half_score):
        halfs = "".join([half_result.get_text() for half_result in half_score]).strip()
        no_overtime_index = halfs.index(')')

        return halfs[1:no_overtime_index]

    def __get_map_played_result(self, team, map_results):
        team_name = team.select_one('div.results-teamname').get_text().lower()
        map_results = map_results.select_one('div.results-center-half-score')
        side = map_results.contents[1].attrs['class'][0]
        side_position_index = self.__get_side_index_in_team_map_result(team)

        halfs_results = self.__get_map_result_halfs(map_results).split(";")
        maps_played_by_team = []

        for half_result in halfs_results:
            sides_results = {
                't': 0,
                'ct': 0
            }
            half_result = half_result.strip()
            side_result = half_result.split(':')[side_position_index]
            sides_results[side] = int(side_result)

            side = helpers.toggle_value(side, ['t', 'ct'])
            maps_played_by_team.append({
                'team_name': team_name,
                'tr_rounds_wins': sides_results['t'],
                'ct_rounds_wins': sides_results['ct']
            })

        return maps_played_by_team

    def __valid_dictonary_keys(self, valid_keys, dictonary_to_valid):
        if len(dictonary_to_valid) > 2 or len(valid_keys) > 2:
            return None

        is_keys_valid = False

        for key in dictonary_to_valid:
            if key in valid_keys:
                is_keys_valid = True
                continue

            is_keys_valid = False
            break

        if is_keys_valid:
            return dictonary_to_valid

        keys_not_valid = [key for key in dictonary_to_valid if key not in valid_keys]

        if len(keys_not_valid) > 2:
            return None

        valid_key = [key for key in dictonary_to_valid if key in valid_keys][0]
        missing_key = [key for key in valid_keys if key != valid_key][0]
        key_not_valid = keys_not_valid[0]

        a = {
            valid_key: dictonary_to_valid[valid_key],
            missing_key: dictonary_to_valid[key_not_valid]
        }

        return {
            valid_key: dictonary_to_valid[valid_key],
            missing_key: dictonary_to_valid[key_not_valid]
        }

    def __rearrange_page_data(self, unrearrange_data):
        teams = [team for team in unrearrange_data['results']]

        unrearrange_data['maps_votation'] = self.__valid_dictonary_keys(teams, unrearrange_data['maps_votation'])

        page_data = {
            'matched_at': unrearrange_data['matched_at'],
            'event_id': unrearrange_data['event_id'],
            'match_data_by_team': {team: {} for team in teams}
        }

        has_votation = unrearrange_data['maps_votation']
        has_maps_results = unrearrange_data['maps_results_by_team']

        for team in teams:
            votation = unrearrange_data['maps_votation'][team] if has_votation else None
            maps_results = unrearrange_data['maps_results_by_team'][team] if has_maps_results else None
            page_data['match_data_by_team'][team]['votation'] = votation
            page_data['match_data_by_team'][team]['maps_results'] = maps_results
            page_data['match_data_by_team'][team]['result'] = unrearrange_data['results'][team]

        return page_data

    def __store_match_data(self):
        page_data = self.get_page_data()
        match_orm: Orm = self.get_orm()

        event_orm: Orm = match_orm.get_relationship_orm('events')
        event_orm.load_by_column('hltv_id')

        match_orm.set_columns({
            'matched_at': page_data['matched_at'],
            'hltv_id': page_data['hltv_id']
        })
        match_orm.set_foreign_key_by_relationship('events')

        match_stored = match_orm.load_by_column('hltv_id')

        if match_stored is None:
            return match_orm.create()

        return match_stored

    def __store_match_team_result(self, result):
        self.__match_team_result_orm.set_columns({
            'result': result
        })
        self.__match_team_result_orm.set_all_foreign_key()

        match_team_result_stored = self.__match_team_result_orm.get_by_columns({
            'team_id': None,
            'match_id': None
        })

        if match_team_result_stored is None:
            return self.__match_team_result_orm.create()

        return match_team_result_stored

    def __store_match_votation(self, votation):
        orms_by_vote = {
            'picks': self.__match_map_picked_orm,
            'bans': self.__match_map_banned_orm
        }

        if votation is not None:
            for vote in votation:
                orm: Orm = orms_by_vote[vote]
                maps = votation[vote]

                for map_name in maps:
                    map_stored = self.__map_orm.load_by_column('name', map_name)

                    if map_stored is None:
                        self.__map_orm.reset_columns_values()
                        self.__map_orm.set_columns({
                            'name': map_name
                        })

                    orm.set_all_foreign_key()

                    row_stored = orm.get_by_columns({
                        'map_id': None,
                        'team_id': None,
                        'match_id': None
                    })

                    if row_stored is None:
                        orm.create()

    def __store_match_team_maps_results(self, maps_results):
        if maps_results is not None:
            for map_name in maps_results:
                map_result = maps_results[map_name]

                map_stored = self.__map_orm.load_by_column('name', map_name)

                if map_stored is None:
                    self.__map_orm.reset_columns_values()
                    self.__map_orm.set_columns({
                        'name': map_name
                    })

                self.__match_team_map_result_orm.set_columns(map_result)
                self.__match_team_map_result_orm.set_all_foreign_key()

                match_team_map_result_stored = self.__match_team_map_result_orm.get_by_columns({
                    'team_id': None,
                    'map_id': None,
                    'match_id': None
                })

                if match_team_map_result_stored is None:
                    self.__match_team_map_result_orm.create()

    def __store_teams_match_data(self):
        page_data = self.get_page_data()
        match_data_by_team = page_data['match_data_by_team']

        for team_name in match_data_by_team:
            self.__set_team_page_data_from_team_name(team_name)

            team_match_data = page_data['match_data_by_team'][team_name]
            result = team_match_data['result']
            votation = team_match_data['votation']
            maps_results = team_match_data['maps_results']

            team_orm = self.__team_page.get_orm()
            team_orm.load_by_column('hltv_id')

            self.__store_match_team_result(result)
            self.__store_match_votation(votation)
            self.__store_match_team_maps_results(maps_results)

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
                    team_name = votation_splited[0][3:-1].lower()
                    map_name = votation_splited[1][1:].lower()
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

    def get_maps_results_from_page(self, page):
        maps_data = page.select('.g-grid.maps > div:first-child > div')
        maps_played_index = self.__get_map_metadata_index('played', maps_data)
        maps_played = maps_data[maps_played_index].select('div.mapholder')
        invalid_maps_names = ['tba', 'default']
        maps_played_results_by_team = {}

        for map_played in maps_played:
            optional_map = map_played.select_one('div.optional')
            map_name = map_played.select_one('div > div.mapname').get_text().lower()
            map_results = map_played.select_one('div.results')
            teams_map_results = []

            if optional_map is not None or map_name in invalid_maps_names or map_results is None:
                continue

            team_left = map_results.select_one('.results-left')
            results = map_results.select_one('.results-center')
            team_right = map_results.select_one('.results-right')

            teams_map_results.append(self.__get_map_played_result(team_left, results))
            teams_map_results.append(self.__get_map_played_result(team_right, results))

            for team_map_result in teams_map_results:
                for half in team_map_result:
                    team_name = half['team_name']

                    if team_name not in maps_played_results_by_team:
                        maps_played_results_by_team[team_name] = {
                            map_name: {
                                'tr_rounds_wins': 0,
                                'ct_rounds_wins': 0
                            }
                        }

                    if map_name not in maps_played_results_by_team[team_name]:
                        maps_played_results_by_team[team_name][map_name] = {
                            'tr_rounds_wins': 0,
                            'ct_rounds_wins': 0
                        }

                    maps_played_results_by_team[team_name][map_name]['tr_rounds_wins'] += half['tr_rounds_wins']
                    maps_played_results_by_team[team_name][map_name]['ct_rounds_wins'] += half['ct_rounds_wins']

        return maps_played_results_by_team

    def get_page_data_from_page(self, page):
        page = page.find('div', {'class': 'contentCol'})
        page_data = {}

        if page is not None:
            self.__set_match_event_from_page(page)

            page_data['results'] = self.get_match_result_from_page(page)
            page_data['matched_at'] = self.get_match_timestamp_from_page(page)
            page_data['event_id'] = None
            page_data['maps_votation'] = self.get_maps_votation_from_page(page)
            page_data['maps_results_by_team'] = self.get_maps_results_from_page(page)
            page_data = self.__rearrange_page_data(page_data)
            page_data['hltv_id'] = self.get_searchable_data('hltv_id')

            return page_data

        return None

    def store(self):
        self.__store_match_data()
        self.__store_teams_match_data()
