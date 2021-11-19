from sys import argv
from app.user_interface.teams_stats import TeamsStats
from app.user_interface.get_team import GetTeam

def show_screen(screen):
    screen_by_module = {
        'team_stats': TeamsStats().screen,
        'get_team': GetTeam().screen
    }

    if screen in screen_by_module:
        screen_by_module[screen]()
    else:
        print('screen inexistent')

screen = argv[1]

show_screen(screen)