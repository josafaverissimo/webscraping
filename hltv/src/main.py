from sys import argv
from app.user_interface.match import Match
from app.user_interface.event import Event
from app.user_interface.map import Map
from app.user_interface.result import Result
from app.user_interface.team import Team


def show_screen(screen):
    screen_by_module = {
        'match': Match().screen,
        'event': Event().screen,
        'map': Map().screen,
        'result': Result().screen,
        'team': Team().screen
    }

    if screen in screen_by_module:
        screen_by_module[screen]()
    else:
        print('screen inexistent')


screen = argv[1]

show_screen(screen)
