from datetime import timedelta
from .database.connection import Sql

days_by_period = {
    'year': timedelta(days = 365),
    'month': timedelta(days = 30)
}

def subtract_date_by_difference(date, diff):
    return (date.replace(day = 1) - diff).replace(day=date.day)

def get_team_url_page(team):
    def get_team(team):
        condition = 'id = %s' if isinstance(team, int) else 'name = %s'
        query = f'select * from teams where {condition}'

        sql = Sql()

        try:
            sql.open_connection()

            team_row = sql.execute(query, team).fetchone()

            return team_row
        finally:
            sql.close_connection()

    def get_url(team):
        base_url = 'https://www.hltv.org/team/'
        team = get_team(team)
        NAME = 1
        HLTV_ID = 2

        if team is not None:
            return f'{base_url}{team[HLTV_ID]}/{team[NAME]}'

    return get_url(team)

def has_none_value(dictonary):
    for value in dictonary.values():
        if value is None:
            return True

    return False

def is_all_values_none(dictonary):
    for value in dictonary.values():
        if value is not None:
            return False

    return True

def is_key_and_value_in_dictonary(dictonary, key_to_search, value_to_search):
    for key, value in dictonary.items():
        if key == key_to_search and value == value_to_search:
            return True

    return False