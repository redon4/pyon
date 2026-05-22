#!/bin/sh

dir=$(pwd)

# Setup function folder
mkdir -p ~/.config/bash/functions

bash_config="$HOME/.bashrc"
loader_comment="# Bash func folder (dont delete this comment)"

if ! grep -q "$loader_comment" "$bash_config"; then
    printf "\n%s\nif [ -d ~/.config/bash/functions ]; then\n    for f in ~/.config/bash/functions/*.sh; do\n        [ -r \"\$f\" ] && source \"\$f\"\n    done\nfi\n" "$loader_comment" >> "$bash_config"
fi

if [[ "$dir" == *"/pyon"* ]]; then
    pyon_dir=$(echo "$dir" | grep -o '.*\/pyon')
else
    echo "No parent folder named \"pyon\""
    exit 1
fi

file_dir=$(find "$pyon_dir" -name pyon.py -print -quit 2>/dev/null)

printf "pyon() {\n    python3 \"%s\" \"\$@\"\n    stty -ixon\n}\n" "$file_dir" > ~/.config/bash/functions/pyon.sh

source ~/.config/bash/functions/pyon.sh

echo "Bash function folder updated and pyon function updated"
