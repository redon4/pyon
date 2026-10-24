#!/usr/bin/env python3

import os
import sys


match sys.platform:
    case "linux":
        path1 = r"~/.local/opt/pyon/pyon.py"
        path2 = r"~/.local/bin/pyon"
    case "win32":
        path1 = r""
        path2 = r""

    # darwin is macos
    case "darwin":
        path1 = r""
        path2 = r""

    case _:
        print("Invalid OS")
        sys.exit(1)

path1 = os.path.normpath(os.path.expanduser(path1))
path2 = os.path.normpath(os.path.expanduser(path2))

try:
    os.symlink(path1, path2)
    print("Link created successfully")

except FileExistsError:
    print("Symlink already exists.")

except PermissionError:
    print("Permission denied: You might need admin rights.")

except OSError as e:
    print("OS error occurred:", e)



path = os.environ.get("PATH", "").split(os.pathsep)


path = [os.path.normpath(p) for p in path]


if os.path.dirname(path2) in path:
    print("Is in path")
else:
    print("is not in path")