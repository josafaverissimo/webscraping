from .utils.webscraper import get_data_from_json_api
from .utils.database.orms.team import Team

def get_team_by_name(name):
    name = name.lower()

    def search(term):
        base_url = "https://www.hltv.org/search?term="
        url = base_url + term
        response = get_data_from_json_api(url)

        return response

    def get_team(name):
        teams = search(name)
        
        if teams is not None:
            teams = teams[0]['teams']
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

    teamOrm = Team()
    loaded = teamOrm.load_by_column('name', team['name'])

    if loaded is None:
        teamOrm.set_columns(team)
        teamOrm.create()
