from sys import argv
from app.user_interface.match import Match


def show_screen(screen):
    screen_by_module = {
        'match': Match().screen
    }

    if screen in screen_by_module:
        screen_by_module[screen]()
    else:
        print('screen inexistent')


screen = argv[1]

show_screen(screen)
