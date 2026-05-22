set parent_path (path dirname (pwd))
printf "function pyon\n    python3 $parent_path/pyon.py \$argv\nend" > ~/.config/fish/functions/pyon.fish

