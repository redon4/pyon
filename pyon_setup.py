import os

alias_cmd = "alias pyon='python3 ~/pyon/pyon.py'"
shortcuts_cmd = "stty -ixon"
rc_file = os.path.expanduser("~/.bashrc")

with open(rc_file, "r") as f:
    content = f.read()

with open(rc_file, "a") as f:
    if alias_cmd not in content:
        f.write("\n" + alias_cmd + "\n")
    if shortcuts_cmd not in content:
        f.write("\n" + shortcuts_cmd + "\n")

print(f"Updated ~/.bashrc. Restart Terminal or Run: source {rc_file}")
