from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from datetime import date, timedelta
import pymysql

def getPage(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US'
    }

    html = None

    try:
        request = Request(url, headers=headers)
        response = urlopen(request).read()
        html = BeautifulSoup(response, 'html.parser')    
    except HTTPError as e:
        print(e)
    except URLError as e:
        print(e)
    finally:
        print(f"success to get: {url}")
        return html

def subtractDateByDifference(date, diff):
    return (date.replace(day=1) - diff).replace(day=date.day)

def getTeamsPerformanceByMapAndPeriod(map = None, period = None):
    def getURLS(map = None, period = None):
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
                'start': subtractDateByDifference(date.today(), YEAR).isoformat(),
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

    def getPerformance(map):
        urls = getURLS(map, period)
        performance = {}
        columns_by_order = {'team': 0, 'times_played': 1, 'rate_win': 2}
        
        for side in urls:
            url = urls[side]

            html = getPage(url)

            if(html == None):
                continue

            table = html.find('table', {'class': {'stats-table', 'player-ratings-table', 'ftu gtSmartphone-only'}})
            table_rows = table.find('tbody').findAll('tr')

            for row in table_rows:
                team_performance = row.findAll('td')
                team = team_performance[columns_by_order['team']].get_text()
                times_played = team_performance[columns_by_order['times_played']].get_text()
                rate_win = team_performance[columns_by_order['rate_win']].get_text()
                
                if team not in performance:
                    performance[team] = {
                        map: {
                            'times_played': times_played,
                            'rate_win_sides': {}
                        }
                    }

                performance[team][map]['rate_win_sides'][side] = rate_win

        return performance

    return getPerformance(map)

def storeTeamsPerformance(teams_performance):
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='', db='hltv')
    cur = conn.cursor()

    try:
        cur.execute('select id, name from teams')
        teams_stored = {team: id for (id, team) in cur.fetchall()}

        cur.execute('select id, name from maps')
        maps_stored = {map: id for (id, map) in cur.fetchall()}

        for team_name in teams_performance:
            team_performance = teams_performance[team_name]

            for map_name in team_performance:
                team_performance_in_map = team_performance[map_name]

                times_played = team_performance_in_map['times_played']
                rate_win_sides = {
                    'ct': team_performance_in_map['rate_win_sides']['ct'],
                    'tr': team_performance_in_map['rate_win_sides']['tr'],
                    'both': team_performance_in_map['rate_win_sides']['both']
                }

                if map_name in maps_stored:
                    map_id = maps_stored[map_name]
                else:
                    cur.execute('insert into maps (name) values (%s) ', (map_name))
                    cur.execute('select last_insert_id()')
                    map_id = cur.fetchone()[0]

                    maps_stored[map_name] = map_id

                if team_name in teams_stored:
                    team_id = teams_stored[team_name]
                else:
                    cur.execute('insert into teams (name) values (%s) ', (team_name))
                    cur.execute('select last_insert_id()')
                    team_id = cur.fetchone()[0]

                    teams_stored[team_name] = team_id

                cur.execute('''
                    insert into teams_stats (team_id, map_id, times_played, ct_rate_win, tr_rate_win, both_rate_win)
                    values (%s, %s, %s, %s, %s, %s)
                ''', (team_id, map_id, times_played, rate_win_sides['ct'], rate_win_sides['tr'], rate_win_sides['both']))

                cur.connection.commit()

                print(team_performance)

        print("success to save data")
    finally:
        cur.close()
        conn.close()

MONTH = timedelta(days=30)

continue_getting_data = 1
FLAGS = range(9)
FLAG_MESSAGE = '0 < FLAG > 9'
while(continue_getting_data in FLAGS):
    months = int(input('type mounths diff to subtract: '))
    map = str(input('type map: '))

    period = {
        'start': subtractDateByDifference(date.today(), MONTH * months),
        'end': date.today()
    }

    storeTeamsPerformance(getTeamsPerformanceByMapAndPeriod(map, period))

    continue_getting_data = int(input(f"do you want get more data? [{FLAG_MESSAGE}]: "))