from utils.webscraper import get_page
from datetime import date, timedelta
from utils.database.connection import Sql
from utils.helpers import subtract_date_by_difference, days_by_period
import json

def get_teams_performance_by_map_and_period(map = None, period = None):
    def get_urls(map = None, period = None):
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
            'endDate': period['end']
        }

        if map != None:
            query_params['maps'] = f'de_{map}'

        for url in urls:
            for query_param in query_params:
                urls[url] += f'&{query_param}={query_params[query_param]}'

        return urls

    def get_performance(map):
        urls = get_urls(map, period)
        performance = {}
        columns_by_order = {'team': 0, 'times_played': 1, 'rate_win': 2, 'hltv_id': 2}
        
        for side in urls:
            url = urls[side]

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
                    .split('/')[columns_by_order['hltv_id']]
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
    sql = Sql()

    try:
        sql.open_connection()
    
        teams_stats = sql.execute(query = '''
            select t.id team_id, t.name team, group_concat(json_object("name", m.name, "id", m.id) separator ';') maps from teams t
            left join teams_stats ts on ts.team_id = t.id
            left join maps m on m.id = ts.map_id
            group by t.id;
        ''').fetchall()

        teams_stored = {}
        maps_stored = {}

        for (team_id, team, maps_played) in teams_stats:
            teams_stored[team] = {
                'id': team_id,
                'maps_played': {}
            }
            
            for map_json in maps_played.split(';'):
                map = json.loads(map_json)

                if map['name'] is None:
                    continue

                teams_stored[team]['maps_played'][map['name']] = map['id']

                if map['name'] not in maps_stored:
                    maps_stored[map['name']] = map['id']

        for team_name in teams_performance:
            team_performance = teams_performance[team_name]

            for map_name in team_performance['maps_played']:
                team_performance_in_map = team_performance['maps_played'][map_name]

                times_played = team_performance_in_map['times_played']

                rate_win_sides = {side: rate_win for (side, rate_win) in team_performance_in_map['rate_win_sides'].items()}

                if map_name in maps_stored:
                    map_id = maps_stored[map_name]
                else:
                    sql.execute(query = 'insert into maps (name) values (%s)', args = (map_name))
                    map_id = sql.last_insert_id()

                    maps_stored[map_name] = map_id

                if team_name in teams_stored:
                    team_id = teams_stored[team_name]['id']
                else:
                    sql.execute(query = 'insert into teams (name, hltv_id) values (%s, %s)', args = (team_name, team_performance['hltv_id']))
                    team_id = sql.last_insert_id()

                    teams_stored[team_name] = {
                        'id': team_id,
                        'maps_played': {}
                    }

                if map_name in teams_stored[team_name]['maps_played']:
                    print(f"{team_name} have alredy played the map {map_name}")
                else:
                    sql.execute(query = '''
                        insert into teams_stats (team_id, map_id, times_played, ct_rate_win, tr_rate_win, both_rate_win)
                        values (%s, %s, %s, %s, %s, %s)
                    ''', args = (team_id, map_id, times_played, rate_win_sides['ct'], rate_win_sides['tr'], rate_win_sides['both']))

                    teams_stored[team_name]['maps_played'][map_name] = map_id
    finally:
        sql.close_connection()

continue_getting_data = 'y'
FLAGS = ['n']
FLAG_MESSAGE = 'y/n'
while(continue_getting_data not in FLAGS):
    months = int(input('type mounths diff to subtract: '))
    map = str(input('type map: '))

    period = {
        'start': subtract_date_by_difference(date.today(), days_by_period['month'] * months),
        'end': date.today()
    }

    store_teams_performance(get_teams_performance_by_map_and_period(map, period))

    continue_getting_data = input(f"do you want get more data? [{FLAG_MESSAGE}]: ")
