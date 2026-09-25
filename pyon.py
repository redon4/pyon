#!/usr/bin/env python3

import curses # for perry
import curses.ascii # for the curses.ascii.ctrl
import sys # for shell and other stuff
import json # for settings saving
from collections import Counter # for the pos saving
import argparse # for the file arguments
from io import StringIO # for the shell
import keyword # for the python syntax keywords
import code # for the shell
import re # for the syntax highlighting
import time # for the saving popup
import os # for the save file
import subprocess # for the command running



# Color indexes
colors = {
    "KEYWORD":[
        1, curses.COLOR_BLUE, -1
    ],
    "STRING":[
        2, curses.COLOR_GREEN, -1
    ],
    "NUMBER":[
        3, curses.COLOR_MAGENTA, -1
    ],
    "COMMENT":[
        4, curses.COLOR_RED, -1
    ],
    "SPACE":[
        5, curses.COLOR_WHITE, curses.COLOR_GREEN
    ],
    "FUNCTION":[
        6, curses.COLOR_CYAN, -1
    ],
    "OVERFLOW":[
        7, curses.COLOR_CYAN, -1
    ],
    "SELF":[
        8, curses.COLOR_MAGENTA, -1
    ],
    "LINENUMBER":[
        9, curses.COLOR_MAGENTA, -1
    ],
    "SEARCH":[
        10, -1, curses.COLOR_GREEN
    ]
}




class CaptureConsole(code.InteractiveConsole):
    def runsource(self, source, filename="<input>", symbol="single"):
        buffer = StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer
        try:
            super().runsource(source, filename, symbol)
        finally:
            sys.stdout = old_stdout
        return buffer.getvalue()



class save_file:
    def __init__(self):
        self.settings = { # default settings
            "center_scroll":False,
            "show_spaces":True,
            "line_numbers":True,

            "linenumber_filling":" ",
            "linenumber_outline":" ",
            "always_show_staring_line":True,

            "auto_indent":True,

            "python_shell":False,
            "shell_size":3,

            "show_whitespace":True,
            "remove_every_line_whitespaces":True,
            "syntax_color":None
        }

        self.positions = {}

        self.filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "save_data.json"))

    @classmethod
    def load(clc):
        standard = clc()
        try:
            with open(standard.filepath , "r") as f:
                data = json.load(f)

                standard.__dict__.update(data)

        except FileNotFoundError:
            #r = standard
            #inp = prompt(stdscr, f"\"{self.filepath}\", type another to change: ")
            #if inp:
            #    r.filepath = os.path.expanduser(inp)
            pass

        except JSONDecodeError:
            raise Exception("Invalid save_data.json")

        return standard

    def save(self):
        d = self.__dict__.copy()
        d.pop("filepath", None)

        try:
            with open(self.filepath , "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2, ensure_ascii=False)

        except AttributeError:
            raise Exception("No filename found")


def prompt(stdscr, message):
    curses.echo()
    stdscr.addstr(stdscr.getmaxyx()[0]-1, 0, message)
    stdscr.clrtoeol()
    name = stdscr.getstr().decode()
    curses.noecho()
    return name


class Perry:
    def __init__(self, stdscr):
        self.stdscr = stdscr

        # Argument Manager
        parser = argparse.ArgumentParser(prog="Pyon", description="A text editor")


        parser.add_argument("filename", nargs="?", help="The name of the file to load")
        parser.add_argument("-n", "--aldsj", help="A testing stuff")


        args = parser.parse_args()

        # Load Args/Filename
        self.current_file = args.filename
        if self.current_file:
            if "." in self.current_file:
                self.file_ending = self.current_file.rsplit(".", 1)[-1] if self.current_file else "txt"
            else:
                self.file_ending = "txt"
        else:
            self.file_ending = "txt"
        # Load positions/settings
        self.saved_file = save_file.load()

        # curses settings
        curses.noecho()
        curses.cbreak()
        curses.raw()
        stdscr.keypad(True)

        # curses colors
        curses.start_color()
        curses.use_default_colors()

        #for i in range(0, min(curses.COLORS, curses.COLOR_PAIRS - 1)):
        #    curses.init_pair(i + 1, i, -1)

        # Color setup
        for name, content in colors.items():
            curses.init_pair(content[0], content[1], content[2])

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


        commands = {
            "toggle show_whitespace": lambda: not self.saved_file.settings["show_whitespace"]
        }

        # for command in commands:
        #     if inp == command[:len(inp)]:
        #        autocomplete.append(command)

        self.footer_message = ""
        self.footer_until = 0

        self.height, self.width = self.stdscr.getmaxyx()

        # search things
        self.search = False
        self.search_word = ""
        self.search_no_move = False

    def resize(self):
        curses.update_lines_cols()
        self.height, self.width = self.stdscr.getmaxyx()

        self.update_layout()

        self.buffer_height = self.height - 2
        self.x_middle = self.width // 2 - len(self.title) // 2

        self.scroll_start = max(0, min(self.scroll_start, max(0, len(self.text) - self.buffer_height)))

    def update_layout(self):
        if self.saved_file.settings["line_numbers"]:
            self.PRE_TEXT_WIDTH = 5 + self.line_number_len
        else:
            self.PRE_TEXT_WIDTH = 2
        self.AFTER_TEXT_WIDTH = 2

        shell_width = self.width // self.shell_size if self.saved_file.settings["python_shell"] else 0

        self.textwidth = self.width - self.PRE_TEXT_WIDTH - self.AFTER_TEXT_WIDTH - shell_width

    def update_title(self):
        self.title = (self.current_file or "[No Name]").rsplit("/", 1)[-1]

    @property
    def line_number_len(self):
        return len(str(len(self.text)))

    def text_setup(self):
        # Get pos from save file
        self.y, self.x, self.scroll_start = self.saved_file.positions.get(self.current_file, (0, 0, 0))

        # Position Vars
        self.tabspace = "    "
        self.PRE_TEXT_WIDTH = 5 + self.line_number_len if self.saved_file.settings["line_numbers"] else 2
        self.AFTER_TEXT_WIDTH = 2

        self.buffer_height = self.height - 1 - 1  # header and footer


        # Clamps for the loaded stuff
        self.y = max(0, min(self.y, len(self.text) - 1))
        self.x = max(0, min(self.x, len(self.text[self.y])))

        self.scroll_start = max(0, min(self.scroll_start, max(0, len(self.text) - self.buffer_height)))

        # Shell size (1 / x) * screen
        self.shell_size = self.saved_file.settings["shell_size"]

        #Header
        self.update_title()
        #Init resizing
        self.resize()

        # \|/ is for quitting the editor
        self.game = True

        # Syntax highliting
            # Keywords
        self.keywords = {
            "py":keyword.kwlist,
            "js":["func"],
        }

            # Patterns for re


        self.patterns = []
        if self.file_ending != "txt":
            self.patterns.append((
                re.compile(r"\b\d+\b"),
                curses.color_pair(1)
            ))  # Numbers

            if self.file_ending in self.keywords.keys():
                self.patterns.append((
                    re.compile(r"\b(%s)\b" % "|".join(map(re.escape, self.keywords[self.file_ending]))),
                    curses.color_pair(1)
                ))  # Keywords

            if self.file_ending == "py":
                self.patterns.append((
                    re.compile(r"\bself\b"),
                    curses.color_pair(8)
                )) # Self in python

            self.patterns.append((
                re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''),
                curses.color_pair(2)
            ))  # Strings

            if self.file_ending == "py":
                self.patterns.append((
                    re.compile(r'#.*'),
                    curses.color_pair(4)
                ))  # Comments
        if self.saved_file.settings["show_spaces"]:
            self.patterns.append((
                re.compile(r"[ \t]+$"),
                curses.color_pair(5)
            ))  # Trailing whitespace
        self.patterns.append([
            re.compile(r"%s" % (self.get_search_word())),
            curses.color_pair(10)
        ])



#        self.patterns = []
#        if self.file_ending != "txt":
#            self.patterns.append((re.compile(r"\b\d+\b"), curses.color_pair(3))) # Numbers
#            self.patterns.append((re.compile(r"\b(%s)\b" % "|".join(map(re.escape, self.keywords[self.file_ending]))), curses.color_pair(1))) # checks for keywords of current language, join produces an or ("|") arragment and escappe reformats potential special characters
#
#            self.patterns.append((re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''), curses.color_pair(2))) # Strings
#            self.patterns.append((re.compile(r'#.*'), curses.color_pair(4))), # Comments
#            self.patterns.append((re.compile(r"[ \t]+$"), curses.color_pair(5))) # Trailing Whitespace


    def draw_text_color(self, y, x_draw_start, text, text_start, text_end):
        string_spans = [] # contains all strings
        self.stdscr.addstr(y, x_draw_start, text[text_start:text_end]) # for all not colored stuff


        for i, element in enumerate(self.patterns):
            if curses.color_pair(10) in element:
                if self.search:
                    self.patterns[i][0] = re.compile(r"%s" % (self.search_word))
                else:
                    self.patterns[i][0] = re.compile(r"")
                break

        for pattern, color in self.patterns:
            for match in pattern.finditer(text):
                start, end = match.span()

                if start >= text_end or end <= text_start: # if word isnt on screen
                    continue

                if color == curses.color_pair(2): # if word is string
                    string_spans.append((start, end))

                if color == curses.color_pair(4): # if word is comment
                     if any(s <= start < e for s, e in string_spans):
                        continue


                start = max(start, text_start)
                end = min(end, text_end)


                self.stdscr.addstr(y, x_draw_start + (start - text_start), text[start:end], color)



    def draw_body(self):
        shell_start_x = self.width - (self.width // self.shell_size)
        if self.saved_file.settings["python_shell"]:
            overflow_position = shell_start_x -2

        else:
            overflow_position = self.width -2

        #if self.saved_file.settings["line_numbers"]:
        #    line_number_len = self.line_number_len
        #    self.PRE_TEXT_WIDTH = 5 + line_number_len
        #else:
        #    self.PRE_TEXT_WIDTH = 2

        #self.textwidth = self.calc_textwidth()
        #if self.x > self.textwidth:
        #    self.PRE_TEXT_WIDTH -= 2
        #    self.textwidth += 2

        start = self.textwidth * (self.x // self.textwidth)
        end = self.textwidth * (self.x // self.textwidth + 1)

        for i in range(self.buffer_height):
            buffer_index = self.scroll_start + i

            if buffer_index >= len(self.text):
                break

            if i + 1 >= self.height:  # <-- prevent drawing off-screen
                 break

            line = self.text[buffer_index]

            if self.saved_file.settings["line_numbers"]:
                self.stdscr.addstr(i + 1, 0, f" {self.saved_file.settings['linenumber_outline']}{str(buffer_index + 1):{str(self.saved_file.settings['linenumber_filling'])[0]}>{self.line_number_len}s}{self.saved_file.settings['linenumber_outline']} ", curses.color_pair(colors["LINENUMBER"][0]))


            if line[:start] and len(line) > start:
                self.stdscr.addstr(i + 1, self.PRE_TEXT_WIDTH - 2, "<|", curses.color_pair(colors["OVERFLOW"][0]))
            elif self.saved_file.settings["line_numbers"] or self.saved_file.settings["always_show_staring_line"]:
                self.stdscr.addstr(i + 1, self.PRE_TEXT_WIDTH - 2, " |", curses.color_pair(colors["LINENUMBER"][0]))
            #else:
            #    self.stdscr.addstr(i + 1, self.PRE_TEXT_WIDTH - 2, " |", curses.color_pair(colors["LINENUMBER"][0]))

            self.draw_text_color(i + 1, self.PRE_TEXT_WIDTH, line, start, end)

            if self.saved_file.settings["python_shell"]:
                self.stdscr.addstr(i + 1, shell_start_x, "|")
                coming_soon_text = "Coming soon! (or later)"[:self.width // self.shell_size - 2]
                coming_soon_placement = shell_start_x + ((self.width // self.shell_size) // 2 - len(coming_soon_text) // 2)
                self.stdscr.addstr(i + 1, coming_soon_placement, coming_soon_text)
                # sometime later the shell will be here

            self.stdscr.addstr(i + 1, overflow_position, "|>" if line[end:] else "  ", curses.color_pair(7))



    def set_footer(self, message, duration=3):
        self.footer_message = message
        self.footer_until = time.time() + duration

    def draw_footer(self):
        if time.time() < self.footer_until:
            y = self.height - 1

            msg = self.footer_message[:self.width-1]
            x = max(0, self.width - len(self.footer_message))
            try:
                self.stdscr.addstr(y, x, msg)#[:self.width])
            except curses.error:
                pass


    def draw_screen(self,
        search=False, search_i=0, search_cnt=0, search_word=""
    ):
        self.stdscr.erase()

        # Title im Header
        self.stdscr.addstr(0, self.x_middle, self.title)

        # Pyon im Header
        self.stdscr.addstr(0, 1, "Pyon")

        # Main Body
        self.draw_body()

        # Footer
        self.draw_footer()

        if search:
            msg = f"{search_word} |{search_i + 1:{len(str(search_cnt))}d}/{search_cnt}| \"q\" to quit"
            try:
                self.stdscr.addstr(0, self.width // 4 - len(msg), msg)
            except:
                pass


        self.stdscr.refresh()

    def update_scroll(self):
        if self.saved_file.settings["center_scroll"]:
            self.scroll_start = self.y - self.buffer_height // 2
            self.scroll_start = max(0, min(self.scroll_start, max(0, len(self.text) - self.buffer_height)))
        else:
            if self.y < self.scroll_start:
                self.scroll_start = self.y
            elif self.y >= (self.scroll_start + self.buffer_height):
                self.scroll_start = self.y - self.buffer_height + 1

    def update_cursor(self):
        relative_y = self.y - self.scroll_start
        self.stdscr.move(relative_y + 1, self.x % self.textwidth + self.PRE_TEXT_WIDTH)

    def write_file(self):
        if not self.current_file:
            self.current_file = prompt(self.stdscr, "Save as: ")
            self.update_title()
        self.set_footer("Saved!", 0.01)

        with open(self.current_file, "w") as f:
            f.write("\n".join(self.text))


    def do_input(self):
        start_y = self.y
        start_x = self.x
        start_scroll_start = self.scroll_start


        char = self.stdscr.getch()

        match char:
            case _ if char == curses.ascii.ctrl(ord('q')):  # Ctrl+Q, Quit
                self.game = False

            case _ if char == curses.ascii.ctrl(ord('s')): # Ctrl+S, Save
               self.write_file()

            case _ if char == curses.ascii.ctrl(ord('o')): # Switches the setting for center scroll
                self.saved_file.settings["center_scroll"] = not self.saved_file.settings["center_scroll"]

            case _ if char == curses.ascii.ctrl(ord('l')):
                self.saved_file.settings["show_spaces"] = not self.saved_file.settings["show_spaces"]

            case _ if char == curses.ascii.ctrl(ord('p')):
                self.saved_file.settings["python_shell"] = not self.saved_file.settings["python_shell"]
                self.update_layout()

            case _ if char == curses.ascii.ctrl(ord('h')):
                if self.saved_file.settings["remove_every_line_whitespaces"]:
                    self.text = [line.rstrip() for line in self.text]
                else:
                    self.text[y] = self.text[y].rstrip()
                self.x = min(x ,len(self.text[y]))

            case _ if char == curses.ascii.ctrl(ord("n")):
                self.saved_file.settings["line_numbers"] = not self.saved_file.settings["line_numbers"]
                self.update_layout()

            case _ if char == curses.ascii.ctrl(ord("f")):
                self.do_search()

            case 27: # alt +
                self.stdscr.nodelay(True)
                next_ch = self.stdscr.getch()
                self.stdscr.nodelay(False)

                if next_ch in (127, 8, curses.KEY_BACKSPACE):
                    left_part = self.text[self.y][:self.x]
                    right_part = self.text[self.y][self.x:]
                    del_len = len(self.text[self.y])
                    # delete spaces and tabs
                    if left_part.endswith((" ", "\t")):
                        self.text[self.y] = left_part.rstrip(" \t") + right_part
                    # delte word
                    elif re.search(r"\w$", left_part):
                        self.text[self.y] = re.sub(r"\w+$", "", left_part) + right_part
                    # delete special characters
                    else:
                        self.text[self.y] = re.sub(r"[^\w\s]+$", "", left_part) + right_part

                    del_len -= len(self.text[self.y])
                    self.x -= del_len

                elif next_ch ==  ord("."):
                        command = prompt(self.stdscr, ":")
                        self.do_command(command)

                elif next_ch == ord("k"): # up
                    self.y = max(0, self.y - 1)
                    self.x = min(self.x, len(self.text[self.y]))



                elif next_ch == ord("j"): # down
                    self.y = min(len(self.text) - 1, self.y + 1)
                    self.x = min(self.x, len(self.text[self.y]))

                elif next_ch == ord("h"): # Left
                    if self.x > 0:
                        self.x -= 1

                elif next_ch == ord("l"): # Right
                    if self.x < len(self.text[self.y]):
                        self.x += 1
                elif next_ch == -1:
                    self.set_footer("Alt + Escape", 0.01)
                else:
                    self.set_footer(f"Alt + {chr(next_ch)}", 0.01)


            case curses.KEY_UP: # Up
                self.y = max(0, self.y - 1)
                self.x = min(self.x, len(self.text[self.y]))



            case curses.KEY_DOWN: # Down
                self.y = min(len(self.text) - 1, self.y + 1)
                self.x = min(self.x, len(self.text[self.y]))

            case curses.KEY_LEFT: # Left
                if self.x > 0:
                    self.x -= 1

            case curses.KEY_RIGHT: # Right
                if self.x < len(self.text[self.y]):
                    self.x += 1

            case 10 | 13 | curses.KEY_ENTER:  # Enter
                line = self.text[self.y]
                if self.saved_file.settings["auto_indent"]:
                    indent = line[:len(line) - len(line.lstrip(" \t"))]

                    if self.file_ending== "py":
                        comment = "#"
                    else:
                        comment = "//"

                    for end_symbol in (":", "(", "[", "{", ","): # add an indent if it should be there
                        if line[:self.x].split(comment, 1)[0].rstrip().endswith(end_symbol):
                            indent += self.tabspace
                else:
                    indent = ""



                rest = line[self.x:].lstrip(" \t")

                self.text[self.y] = line[:self.x]

                self.text.insert(self.y + 1, indent + rest)


                self.y += 1

                self.x = min(self.x, len(indent))

                self.update_layout()


            case curses.KEY_BACKSPACE | 127: # Backspace
                if self.x > 0:
                    self.text[self.y] = self.text[self.y][:self.x-1] + self.text[self.y][self.x:]
                    self.x -= 1
                elif self.y > 0: # Zeilen zusammenfügen
                    old_x = len(self.text[self.y-1])
                    self.text[self.y-1] += self.text[self.y].lstrip()
                    self.text.pop(self.y)
                    self.y -= 1
                    self.x = old_x
                self.update_layout()

            case curses.KEY_DC: # Delete
                if self.x < len(self.text[self.y]): # if x not at end of line
                    self.text[self.y] = self.text[self.y][:self.x] + self.text[self.y][self.x+1:]

                elif self.x == len(self.text[self.y]) and self.y < len(self.text) - 1: # if x at end of line and y isnt the last line
                    self.text[self.y] += self.text[self.y + 1].lstrip()
                    self.text.pop(self.y + 1)
                self.update_layout()

            case 9: # Tab
                self.text[self.y] = self.text[self.y][:self.x] + self.tabspace + self.text[self.y][self.x:]
                self.x += len(self.tabspace)

            case curses.KEY_BTAB: # BackTab
                for i in self.text[self.y][self.x-4:self.x]:
                    if i != " ":
                        break
                else:
                    if self.text[self.y][self.x-4:self.x] == self.tabspace:
                        self.text[self.y] = self.text[self.y][:self.x-4] + self.text[self.y][self.x:]
                        self.x -= len(self.tabspace)


            case 544: # ctrl + Home
                self.y = 0
                self.x = 0

            case 539: # ctrl + End
                self.y = len(self.text) - 1
                self.x = len(self.text[-1])
            case curses.KEY_HOME: # Home
                self.x = 0

            case curses.KEY_END: # End
                self.x = len(self.text[self.y])

            case curses.KEY_PPAGE: # Page up
                self.y = max(0, self.y - self.buffer_height + 1) #
                self.scroll_start = max(0, self.scroll_start - self.buffer_height + 1)
                self.x = min(self.x, len(self.text[self.y]))


            case curses.KEY_NPAGE: # Page down
                self.y = min(len(self.text) - 1, self.y + self.buffer_height - 1)
                self.scroll_start = min(len(self.text) - self.buffer_height, self.scroll_start + self.buffer_height - 1)
                self.x = min(self.x, len(self.text[self.y]))

            case curses.KEY_RESIZE:
                self.resize()



            case _ if 32 <= char <= 126:  # Normal Letters
                self.text[self.y] = self.text[self.y][:self.x] + chr(char) + self.text[self.y][self.x:]
                self.x += 1

        if self.search_no_move and not self.search:
            self.y = start_y
            self.x = start_x
            self.scroll_start = start_scroll_start
            self.search_no_move = False

    def get_search_word(self):
        return self.search_word

    def do_search(self, command=[]):
        self.search = True
        self.search_no_move = False
        if command:
            if any(text in ("nm", "no-move", "nomove", "no_move") for text in command):
                self.search_no_move = True

        self.search_word = prompt(self.stdscr, "Search for: ")
        if not self.search_word:
            return
        name = self.search_word
        cnt=0
        for line in self.text:
            cnt += line.count(name)
        g=True
        first=True
        while g:
            if first and not (any(text in ("fs", "from-start", "fromstart", "from_start") for text in command)):
                start=[self.y, self.x]
                first = False
            else:
                start=[0,0]
            for i in range(cnt):

                for line_index in range(start[0], len(self.text)):
                    line = self.text[line_index]

                    if line_index == start[0]:
                        part = line[start[1]:]
                    else:
                        part = line
                    index = part.find(name)

                    if index != -1:
                        self.x = index + (start[1] if line_index == start[0] else 0)

                        start = [line_index, index + 1 + (start[1] if line_index == start[0] else 0)]

                        self.y = line_index

                        self.update_scroll()

                        self.scroll_start = self.y - self.buffer_height // 2

                        self.draw_screen(search=True, search_i=i, search_cnt=cnt, search_word=name)
                        self.update_cursor()
                        break
                enter=False
                while not enter:
                    inp = self.stdscr.getkey()
                    if inp == "\n":
                        enter = True
                    elif inp == "KEY_DC" or inp == "q":
                        self.search = False
                        return


    def do_command(self, command):
        command = command.split(" ")
        match command[0]:
            case "settings" | "s":
                if len(command) < 2:
                    return
                match command[1]:
                    case "toggle" | "t":
                        if len(command) > 2:
                            self.saved_file.settings[command[-1]] = not self.saved_file.settings[command[-1]]
                    case "set" | "s":
                        value = command[-1]
                        if value.isdigit():
                            value = int(value)
                        elif value == "True":
                            value = True
                        elif value == "False":
                            value = False

                        self.saved_file.settings[command[-2]] = value
            case "q" | "quit":
                self.game = False
            case "w" | "write" | "save":
                self.write_file()
            case "wq" | "x":
                self.write_file()
                self.game = False
            case "rn" | "rename":
#                dir = os.path.abspath(os.path.dirname(__file__))
#                old_path = os.path.join(dir, self.current_file)

                new_name = prompt(self.stdscr, "New name: ")
                new_name = os.path.join(os.path.dirname(self.current_file), new_name)
#                new_path = os.path.join(dir, new_name)
#                subprocess.call(f"mv {self.current_file} {new_name}", shell=True)
                os.rename(self.current_file, new_name)
                self.current_file = new_name
                self.update_title()
            case "search" | "srch":
                self.do_search(command)




class PythonShell:
    def __init__(self, console):
        self.console = console



    def refresh_shell(self):
        pass


def main(stdscr):
    perry = Perry(stdscr)
    perry.text_setup()


    #console = CaptureConsole()
    #pyshell = PythonShell(console)

    while perry.game:
        perry.draw_screen()

        perry.update_cursor()

        perry.do_input()
        perry.update_scroll()

    if perry.current_file:
        perry.saved_file.positions[perry.current_file] = (perry.y, perry.x, perry.scroll_start)
    perry.saved_file.save()


curses.wrapper(main)
