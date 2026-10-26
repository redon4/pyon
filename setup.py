#!/usr/bin/env python3

import os
import sys
from pathlib import Path

def print_header(current_header, header_max_len):
    filler = "=" * ((header_max_len - len(current_header)) // 2)

    print(filler + current_header + filler)


match sys.platform:
    case "linux":
        path1 =         Path.home() / ".local" / "opt" / "pyon" / "pyon.py"
        path2 =         Path.home() / ".local" / "bin" / "pyon"
        profile_path =  Path.home() / ".profile"
        path_set_code = 'export PATH="$HOME/.local/bin:$PATH"'

    case "win32":
        print("Sry windows is not supported yet")
        sys.exit(1)

        path1 = r""
        path2 = r""
        profile_path = r""

    # darwin is macos
    case "darwin":
        print("Sry macos is not supported yet")
        sys.exit(1)

        path1 = r""
        path2 = r""
        profile_path = r""

    case _:
        print("Invalid OS")
        sys.exit(1)

headers = ["FOLDERS", "SYMLINK", "PATH", "PATH CHANGE FILE"]
header_max_len = len(max(headers, key=len)) + 6


# FOLDERS #
print_header(headers[0], header_max_len)
try:
    path2.parent.mkdir(parents=True)
except FileExistsError:
    print(f"Folder {os.path.dirname(path2)} already exists\n")
else:
    print(f"Folder {os.path.dirname(path2)} was created\n")


# SYMLINK #
print_header(headers[1], header_max_len)
try:
    os.symlink(path1, path2)
    print("Link created successfully")

except FileExistsError:
    print("Symlink already exists")

except PermissionError:
    print("Permission denied: You might need admin rights")

except OSError as e:
    print("OS error occurred:", e)

print()

# PATH #
print_header(headers[2], header_max_len)

path = [Path(p) for p in os.environ.get("PATH", "").split(os.pathsep)]

if path2.parent in path:
    print(f"\"{path2.parent}\" is in path\n")

else:
    print(f"\"{path2.parent}\" is not in path\n")


    # PATH CHANGE FILE #
    print_header(headers[3], header_max_len)

    # Checks if any line in profile is the same as the path_set_code
    if any(path_set_code == line for line in profile_path.read_text().splitlines()):
        print(f"The correct line is in {profile_path}, but the PATH is wrong\nPlease run:\n\n{path_set_code}\n\nin every terminal or restart your PC\n")

    else:

        content = profile_path.read_text() if profile_path.exists() else ""
        print(f"The correct line \n({path_set_code})\nisn't in {profile_path}\n")

        profile_path.write_text(content + "\n" + path_set_code + "\n")
        print(f"{profile_path} was updated\n")
