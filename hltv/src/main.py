from sys import argv
from app.user_interface.teams_stats import TeamsStats
from app.user_interface.team import Team

def show_screen(screen):
    screen_by_module = {
        'teams_stats': TeamsStats().screen,
        'team': Team().screen,
        'match_page': None
    }

    if screen in screen_by_module:
        screen_by_module[screen]()
    else:
        print('screen inexistent')

screen = argv[1]

show_screen(screen)