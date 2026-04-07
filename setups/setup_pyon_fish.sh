set path $(pwd)
echo "function pyon\n    python3 '$path'/pyon.py $argv\nend" >> ~/.config/fish/config.fish