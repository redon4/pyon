import curses

x = 0
def main(stdscr):
    curses.raw()
    stdscr.keypad(True)
    global x
    while True: # getkey, get_wch, getch
        x = stdscr.getkey()
        stdscr.addstr(0, 0, f"{str(x):40s}" )

try:
    curses.wrapper(main)
except KeyboardInterrupt:
    print("Last Key:", x)