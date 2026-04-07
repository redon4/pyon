import curses

x = 0
def main(stdscr):
    curses.raw()
    stdscr.keypad(True)
    global x
    while True:
        x = stdscr.getch()
        stdscr.addstr(0, 0, f"{str(x):40s}" )

try:
    curses.wrapper(main)
except KeyboardInterrupt:
    print("Last Key:", x)