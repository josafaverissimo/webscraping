import json
from datetime import date
from .utils.webscraper import get_page
from .utils.helpers import subtract_date_by_difference, days_by_period
from .utils.database.orms.team import Team
from .utils.database.orms.map import Map
from .utils.database.orms.team_stats import TeamStats

def get_teams_performance_by_map_and_period(map, period = None):
    def get_urls(map, period = None):
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
            'maps': f'de_{map}'
        }

        for url in urls:
            for query_param in query_params:
                urls[url] += f'&{query_param}={query_params[query_param]}'

        return urls

    def get_performance(map):
        urls = get_urls(map, period)
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
                            map: {
                                'times_played': times_played,
                                'rate_win_sides': {}
                            }
                        }
                    }

                performance[team]['maps_played'][map]['rate_win_sides'][side] = rate_win

        return performance

    return get_performance(map)

def store_teams_performance(teams_performance):
    teamOrm = Team()
    mapOrm = Map()
    team_statsOrm = TeamStats()
    teams_and_maps_stored = team_statsOrm.get_maps_by_teams_stats()

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
        
        for map in json.loads(maps_played):
            if map['name'] is None:
                continue

            teams_stored[team_name]['maps_played'][map['name']] = map['id']

            if map['name'] not in maps_stored:
                maps_stored[map['name']] = map['id']

    for team_name, team_performance in teams_performance.items():
        team_saved = None

        for map_name, team_performance_in_map in team_performance['maps_played'].items():
            if map_name in maps_stored:
                map_id = maps_stored[map_name]
            else:
                mapOrm.set_column('name', map_name)
                map_saved = mapOrm.create()

                if map_saved is not None:
                    maps_stored[map_name] = map_saved['id']

            if team_name in teams_stored:
                team_id = teams_stored[team_name]['id']
            else:
                team_data_to_save = {
                    'name': team_name,
                    'hltv_id': team_performance['hltv_id']
                }

                teamOrm.set_columns(team_data_to_save)
                team_saved = teamOrm.create()

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
                    team_statsOrm.set_columns(team_stats_to_save)
                    team_stats_saved = team_statsOrm.create()

                    if team_stats_saved is not None:
                        teams_stored[team_name]['maps_played'][map_name] = team_stats_saved['map_id']
