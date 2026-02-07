import curses
from curses import wrapper

def main(stdscr):
    #stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    #stdscr.nodelay(True)
    #stdscr.timeout(30)

    while True:
        key = stdscr.getch()
        if key == curses.KEY_UP :
            print('En avant')
        if key == curses.KEY_LEFT:
            print('à gauche')
        if key == curses.KEY_RIGHT:
            print('à droite')
        if key == curses.KEY_DOWN :
            print('STOP')
            break

    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

wrapper(main)