# Pyon
## Introduction
Pyon is a text Editor mainly made in python with the curses package that focuses on customization.
## Features
### Current:
- Python Syntax highlighting
- Python "self" highlighting
- Show trailing white-space 
- Keep cursor in the y center 
- Auto-Indent
- .json config and position saving
- Search function/shortcut
### Planned:
- Unicode support
## Installation/Setup
### Download
Get the files  from the `release` or `snapshot` branch
- `pyon.py`, the **main** editor
- either the **entire** `setups` folder or the file in `setups` that **matches** your **shell**.
### Setup
Execute the setup file that matches your shell.
Try:
```
source <file>
``` 
or 
```
. <file>
```

If none of both work, please look up how to run a script in your shell.

If there's no file for your shell there, look up how to create a permanent shortcut to `python3 <folder of download>/pyon.py` in your shell.
## Usage
You can use it just like nano or vim
To open a file type:
```
pyon <path-to-file>
```
## Shortcuts
- Ctrl + s = save
- Ctrl + q = quit
- Ctrl + o = toggles keeping the cursor in the y center
- Ctrl + l = toggles showing trailing whitespace
- Ctrl + h = removes trailing whitespace on the line (or all depending on config)
- Ctrl + n = toggles line numbers
### Search
- Ctrl + f = search
### Command line
Alt + "." = open command line
#### Commands
- w/write
- q/quit
- x/wq (write + quit)

