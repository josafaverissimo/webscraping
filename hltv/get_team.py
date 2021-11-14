from utils.webscraper import get_data_from_json_api
from utils.database.connection import Sql

def get_team_by_name(name):
    name = name.lower()

    def search(term):
        base_url = "https://www.hltv.org/search?term="
        url = base_url + term
        response = get_data_from_json_api(url)

        return response

    def get_team(name):
        teams = search(name)[0]['teams']

        for team in teams:
            team_name = team['name'].lower()

            if team_name == name:
                return {
                    'name': team_name,
                    'hltv_id': team['id']
                }

        return None

    return get_team(name)

def store_team(team):
    if team is None:
        return None

    sql = Sql()

    try:
        sql.open_connection()

        team_id = sql.execute('select id from teams where name = %s', team['name']).fetchone()[0]

        if team_id is None:
            sql.execute('''
                insert into teams (name, hltv_id)
                values (%s, %s)
            ''', (team['name'], team['hltv_id']))
        else:
            sql.execute('''
                update teams set hltv_id = %s
                where id = %s
            ''', (team['hltv_id'], team_id))

    finally:
        sql.close_connection()

store_team(get_team_by_name('gambit'))
