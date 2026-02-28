import curses
import curses.ascii
import sys
import pickle
from collections import Counter
import argparse
import re
import os
import tokenize
from io import StringIO
import keyword



class save_file:
    def __init__(self):
        self.positions = Counter()
        self.settings = {
            "center_scroll":False,
            "show_spaces": False,
            "python_shell":False
        }

    @staticmethod
    def load(self):
        r=0
        try:
            with open("save_data.pkl" , "rb") as f:
                r = pickle.load(f)

        except FileNotFoundError:
            r = save_file()

        return r

    def save(self):
        with open("save_data.pkl" , "wb") as f:
            pickle.dump(self, f)


def prompt(stdscr, message):
    curses.echo()
    stdscr.addstr(curses.LINES-1, 0, message)
    stdscr.clrtoeol()
    name = stdscr.getstr().decode()
    curses.noecho()
    return name


class Perry:
    def __init__(self, stdscr):
        self.stdscr = stdscr

        # Argument Manager
        parser = argparse.ArgumentParser(prog="Pyon", description="A text editor")


        parser.add_argument("filename", help="The name of the file to load")
        parser.add_argument("-n", "--aldsj", help="A testing stuff")


        args = parser.parse_args()

        # Load Args/Filename
        self.current_file = args.filename

        # Load positions/settings
        self.saved_file = save_file.load(0)

        # curses settings
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        # curses colors
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, min(curses.COLORS, curses.COLOR_PAIRS - 1)):
            curses.init_pair(i + 1, i, -1)



        # text loading
        self.text = [""]  # Liste von Zeilen (Text-Buffer)
        if self.current_file:
            try:
                with open(self.current_file, "r") as f:
                    self.text = f.read().splitlines()
                if not self.text:
                    self.text = [""]
            except FileNotFoundError:
                self.text = [""]


        #Get pos
        self.y, self.x, self.scroll_start = self.saved_file.positions.get(self.current_file, (0, 0, 0))


        # Clamps
        self.y = max(0, min(self.y, len(self.text) - 1))
        self.x = max(0, min(self.x, len(self.text[self.y])))

        self.tabspace = "    "
        self.PRE_TEXT_WIDTH = 8
        self.AFTER_TEXT_WIDTH = 2
        self.textwidth = curses.COLS - self.PRE_TEXT_WIDTH - self.AFTER_TEXT_WIDTH
        self.buffer_height = curses.LINES - 1 - 1

        # scroll_start
        self.scroll_start = max(0, min(self.scroll_start, max(0, len(self.text) - self.buffer_height)))

#         # Clamp scroll_start into valid range
#        self.scroll_start = max(0, self.scroll_start)
#        self.scroll_start = min(self.scroll_start, max(0, len(text) - self.buffer_height))

        # Header stuff
        self.title = (self.current_file or "[No Name]").split("/")[-1]
        self.x_middle = curses.COLS // 2 - len(self.title) // 2

        # \|/ <- is for quitting the editor
        self.game = True


    def draw_screen(self):
        self.stdscr.erase()

        # Title im Header

        self.stdscr.addstr(0, self.x_middle, self.title)

        # Pyon im Header
        self.stdscr.addstr(0, 1, "Pyon")

        for i in range(self.buffer_height):
            start = self.textwidth * (self.x // self.textwidth)
            end = self.textwidth * (self.x // self.textwidth + 1)


            buffer_index = self.scroll_start + i
            if buffer_index >= len(self.text):
                break

            if i + 1 >= curses.LINES:  # <-- prevent drawing off-screen
                 break

            line = self.text[buffer_index]

            self.stdscr.addstr(i + 1, 0, f" |{buffer_index + 1:03d}|", curses.color_pair(101010))
            self.stdscr.addstr(i + 1, 6, "<|" if line[:start] and len(line) > start  else "  ", curses.color_pair(4))

            if self.saved_file.settings["python_shell"]:
                self.stdscr.addstr(i + 1, self.PRE_TEXT_WIDTH, line[start:end-self.x_middle])
                pass

            else:
                self.stdscr.addstr(i + 1, self.PRE_TEXT_WIDTH, line[start:end])


            self.stdscr.addstr(i + 1, curses.COLS - 2, "|>" if line[end:] else "  ", curses.color_pair(4))


        self.stdscr.refresh()

    def do_input(self):
        y = self.y
        x = self.x
        text = self.text
        char = self.stdscr.getch()

        match char:
            case _ if char == curses.ascii.ctrl(ord('q')):  # Ctrl+Q, Quit
                self.game = False

            case _ if char == curses.ascii.ctrl(ord('s')): # Ctrl+S, Save
                if not self.current_file:
                    self.current_file = prompt(stdscr, "Save as: ")

                with open(self.current_file, "w") as f:
                    f.write("\n".join(self.text))

            case _ if char == curses.ascii.ctrl(ord('p')): # Switches the setting for center scroll
                self.saved_file.settings["center_scroll"] = not self.saved_file.settings["center_scroll"]

            case _ if char == curses.ascii.ctrl(ord('l')):
                self.saved_file.settings["show_spaces"] = not self.saved_file.settings["show_spaces"]

            case curses.KEY_UP: # Up
                y = max(0, y - 1)
                x = min(x, len(text[y]))



            case curses.KEY_DOWN: # Down
                y = min(len(text) - 1, y + 1)
                x = min(x, len(text[y]))

            case curses.KEY_LEFT: # Left
                if x > 0:
                    x -= 1

            case curses.KEY_RIGHT: # Right
                if self.x < len(self.text[self.y]):
                    self.x += 1

            case 10 | 13:  # Enter
                rest = text[y][x:]
                text[y] = text[y][:x]
                text.insert(y + 1, rest)
                y += 1
                x = 0

            case curses.KEY_BACKSPACE | 127: # 127 ist oft Backspace in Terminals
                if x > 0:
                    text[y] = text[y][:x-1] + text[y][x:]
                    x -= 1
                elif y > 0: # Zeilen zusammenfügen
                    old_x = len(text[y-1])
                    text[y-1] += text[y]
                    text.pop(y)
                    y -= 1
                    x = old_x

            case 9: # Tab
                text[y] = text[y][:x] + tabspace + text[y][x:]
                x += len(tabspace)

            case curses.KEY_BTAB: # BTab
                for i in text[y][x-4:x]:
                    if i != " ":
                        break
                else:
                    if text[y][x-4:x] == tabspace:
                        text[y] = text[y][:x-4] + text[y][x:]
                        x -= len(tabspace)


            case curses.KEY_HOME:
                x = 0

            case curses.KEY_END:
                x = len(text[y])

            case _ if 32 <= char <= 126:  # Druckbare Zeichen
                text[y] = text[y][:x] + chr(char) + text[y][x:]
                x += 1
        # Cursor Pos changing
        if self.saved_file.settings["center_scroll"]:
            self.scroll_start = y - self.buffer_height // 2
            self.scroll_start = max(0, min(self.scroll_start, max(0, len(text) - self.buffer_height)))
        else:
            if y < self.scroll_start:
                self.scroll_start = y
            elif y >= (self.scroll_start + self.buffer_height):
                self.scroll_start = y - self.buffer_height + 1


        self.y = y
        self.x = x
        self.text = text






def main(stdscr):
    perry = Perry(stdscr)


    while perry.game:
        perry.draw_screen()
        # Berechne die relative Zeile auf dem Bildschirm:
        relative_y = perry.y - perry.scroll_start
        stdscr.move(relative_y + 1, perry.x % perry.textwidth + perry.PRE_TEXT_WIDTH)

        perry.do_input()

    perry.saved_file.positions[perry.current_file] = (perry.y, perry.x, perry.scroll_start)
    perry.saved_file.save()


#filename = sys.argv[-1] if len(sys.argv) > 1 else None

curses.wrapper(main)









"""
# Top of file, after imports
KEYWORD_COLOR = 1
STRING_COLOR  = 2
NUMBER_COLOR  = 3
COMMENT_COLOR = 4
SPACE_COLOR = 5

def get_python_highlight(line):
    highlights = []
    try:
        for tok in tokenize.generate_tokens(StringIO(line).readline):
            tok_type = tok.type
            start_col, end_col = tok.start[1], tok.end[1]

            if tok_type == tokenize.COMMENT:
                highlights.append((start_col, end_col, curses.color_pair(COMMENT_COLOR)))
            elif tok_type == tokenize.STRING:
                highlights.append((start_col, end_col, curses.color_pair(STRING_COLOR)))
            elif tok_type == tokenize.NUMBER:
                highlights.append((start_col, end_col, curses.color_pair(NUMBER_COLOR)))
            elif tok_type == tokenize.NAME:
                if tok.string in keyword.kwlist:
                    highlights.append((start_col, end_col, curses.color_pair(KEYWORD_COLOR)))
            # You can add more token types if needed
    except tokenize.TokenError:
        pass
    return highlights


# Example keyword mappings for multiple languages
language_keywords = {
    "python": ["def", "class", "import", "for", "while", "if", "else", "return"],
    "javascript": ["function", "var", "let", "const", "if", "else", "return"]
}

# Map file extension to language
file_language = {
    ".py": "python",
    ".js": "javascript"
}




# In your curses init loop, make sure these pairs exist:
    curses.init_pair(KEYWORD_COLOR, curses.COLOR_BLUE, -1)
    curses.init_pair(STRING_COLOR, curses.COLOR_GREEN, -1)
    curses.init_pair(NUMBER_COLOR, curses.COLOR_MAGENTA, -1)
    curses.init_pair(COMMENT_COLOR, curses.COLOR_CYAN, -1)
    curses.init_pair(SPACE_COLOR, curses.COLOR_BLACK, curses.COLOR_GREEN)




class Setup:
    def __init__(self):

        self.compose={} # [id, lines count, (y_start, x, text, color)]
        compose.append("Header":[1, (0, 1, "Pyon", None), (0, x_middle, title, None)])
        compose.append("":["fill", (1, 0, f" |{'line_number':03d}|", 101010), (1, 6, "<|" if line])

"""