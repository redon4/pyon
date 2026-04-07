## Introduction
Pyon is a text Editor made in python with the curses package that focuses on customization

## Features
### Current:
- Syntax highlighting
- Python "self" highlighting
- Show trailing white-space 
- Keep cursor in the y center 
- Auto-Indent
### Planned:
- Auto adding "()[]{}"
- Python-shell/terminal sidebar
- Unicode support
- Split-screen
- Portable Mode


## Installation
### Download
Download the newest release `pyon.py` and if you want the `setup_pyon.sh`.
Please put the downloaded files in a **"pyon"** folder in your **Home-Directory** (otherwise it wont work properly!).

### setup_pyon.sh
This shell script will create an alias so that `pyon` (in the terminal) starts pyon.
You can run it with `. setup_pyon.sh` or with `source setup_pyon.sh`.

## Usage
If you have used Nano or Vim before, you only need to read the **Without setup_pyon.sh**, just use it in the same way, but if you haven't:
to open a file simply type:
```
pyon path_to_file
```
If the file is in the current folder, only the filename will be enough, otherwise you need to type in either a relative (`../test.txt`) or an absolute (`/home/redon4/test.txt`) path.

### Without setup_pyon.sh 
If you don't want to use a shortcut, or aren't on a bash terminal, you need to type:
```
python3 ~/pyon/pyon.py path_to_file
```
