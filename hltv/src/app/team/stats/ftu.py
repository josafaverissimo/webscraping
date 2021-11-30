from ...utils.webscraper import get_page
from ...utils.helpers import subtract_date_by_difference, days_by_period
from ...utils.database.orms.team import Team as TeamORM
from ...utils.database.orms.map import Map as MapORM
from ...utils.database.orms.team_stats import TeamStats as TeamStatsORM
from datetime import date

class FTU:
    def __init__(self, map_name = None, period = None):
        self.__map_name = map_name
        self.__period = period
        self.__ftu_data = None

    def get_map_name(self):
        return self.__map_name

    def set_map_name(self, map_name):
        self.__map_name = map_name

    def get_period(self):
        return self.__period
    
    def set_period(self, period):
        self.__period = period
    
    def get_ftu_data(self):
        return self.__ftu_data

    def search_ftu_data_by_map_name_and_period(self, map_name = None, period = None):
        def get_urls(map_name, period = None):
            sides = {
                'tr': 'TERRORIST',
                'ct': 'COUNTER_TERRORIST'
            }

            baseURL = 'https://www.hltv.org/stats/teams/ftu?'
            urls = {
                'both': baseURL,
                'tr': f'{baseURL}side={sides["tr"]}',
                'ct': f'{baseURL}side={sides["ct"]}',
            }

            if period == None:
                today = date.today()

                period = {
                    'start': subtract_date_by_difference(date.today(), days_by_period['year']).isoformat(),
                    'end': today.isoformat()
                }

            query_params = {
                'startDate': period['start'],
                'endDate': period['end'],
                'maps': f'de_{map_name}'
            }

            for url in urls:
                for query_param in query_params:
                    urls[url] += f'&{query_param}={query_params[query_param]}'

            return urls

        def get_performance(map_name, period):
            urls = get_urls(map_name, period)
            performance = {}
            columns_by_order = {'team': 0, 'times_played': 1, 'rate_win': 2}
            HLTV_ID = 2
            
            for side, url in urls.items():
                html = get_page(url)

                if(html == None):
                    continue

                table = html.find('table', {'class': {'stats-table', 'player-ratings-table', 'ftu gtSmartphone-only'}})
                table_rows = table.find('tbody').findAll('tr')

                for row in table_rows:
                    team_performance = row.findAll('td')
                    
                    hltv_id = int(
                        team_performance[columns_by_order['team']]
                        .find(lambda tag: 'href' in tag.attrs).attrs['href'][1::]
                        .split('/')[HLTV_ID]
                    )

                    team = team_performance[columns_by_order['team']].get_text().lower()
                    times_played = int(team_performance[columns_by_order['times_played']].get_text())
                    rate_win = float(team_performance[columns_by_order['rate_win']].get_text().replace('%', ''))
                    
                    if team not in performance:
                        performance[team] = {
                            'hltv_id': hltv_id,
                            'maps_played': {
                                map_name: {
                                    'times_played': times_played,
                                    'rate_win_sides': {}
                                }
                            }
                        }

                    performance[team]['maps_played'][map_name]['rate_win_sides'][side] = rate_win

            return performance

        map_name = self.get_map_name() if map_name is None else map_name
        period = self.get_period() if period is None else period

        return get_performance(map_name, period)

    def load_ftu_data_by_map_name_and_period(self, map_name = None, period = None):
        self.__ftu_data = self.search_ftu_data_by_map_name_and_period(map_name, period)

    def store(self):
        ftu_data = self.get_ftu_data()
        team_orm = TeamORM()
        map_orm = MapORM()
        team_stats_orm = TeamStatsORM()
        teams_and_maps_stored = team_stats_orm.get_maps_by_teams_stats()

        teams_stored = {}
        maps_stored = {}

        for team_and_map_stored in teams_and_maps_stored:
            team_id = team_and_map_stored['team_id']
            team_name = team_and_map_stored['team_name']
            maps_played = team_and_map_stored['maps']

            teams_stored[team_name] = {
                'id': team_id,
                'maps_played': {}
            }
            
            for map_data in json.loads(maps_played):
                if map_data['name'] is None:
                    continue

                teams_stored[team_name]['maps_played'][map_data['name']] = map_data['id']

                if map_data['name'] not in maps_stored:
                    maps_stored[map_data['name']] = map_data['id']

        for team_name, team_performance in ftu_data.items():
            team_saved = None

            for map_name, team_performance_in_map in team_performance['maps_played'].items():
                if map_name in maps_stored:
                    map_id = maps_stored[map_name]
                else:
                    map_orm.set_column('name', map_name)
                    map_saved = map_orm.create()

                    if map_saved is not None:
                        maps_stored[map_name] = map_saved['id']

                if team_name in teams_stored:
                    team_id = teams_stored[team_name]['id']
                else:
                    team_data_to_save = {
                        'name': team_name,
                        'hltv_id': team_performance['hltv_id']
                    }

                    team_orm.set_columns(team_data_to_save)
                    team_saved = team_orm.create()

                    if team_saved is not None:
                        teams_stored[team_name] = {
                            'id': team_saved['id'],
                            'maps_played': {}
                        }

                if map_name in teams_stored[team_name]['maps_played']:
                    print(f"{team_name} have alredy played the map {map_name}")
                else:
                    if team_saved is not None and map_saved is not None:                    
                        rate_win_sides = {side: rate_win for (side, rate_win) in team_performance_in_map['rate_win_sides'].items()}

                        team_stats_to_save = {
                            'team_id': team_saved['id'],
                            'map_id': map_saved['id'],
                            'times_played': team_performance_in_map['times_played'],
                            'ct_rate_win': rate_win_sides['ct'],
                            'tr_rate_win': rate_win_sides['tr'],
                            'both_rate_win': rate_win_sides['both'],
                        }
                        team_stats_orm.set_columns(team_stats_to_save)
                        team_stats_saved = team_stats_orm.create()

                        if team_stats_saved is not None:
                            teams_stored[team_name]['maps_played'][map_name] = team_stats_saved['map_id']
