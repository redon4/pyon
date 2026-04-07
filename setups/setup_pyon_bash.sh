path=$(pwd)

echo "alias pyon='python3 "$path"/pyon.py'" >> ~/.bashrc
echo "stty -ixon" >> ~/.bashrc

echo "~/.bashrc was updated!"