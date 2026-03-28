read -p "Which shell are you using(lowercase): " shell
echo $shell


case "$shell" in
    "bash")
        path=$(pwd)
        echo "alias pyon='python3 "$path"/pyon.py'" >> ~/.bashrc
        ;;
    "fish")
        set path $(pwd)
        echo "function pyon\n    python3 '$path'/pyon.py $argv\nend" >> ~/.config/fish/config.fish
        ;;
    *)
        # Default-Fall (entspricht 'else' oder '_')
        ;;
esac





#echo "alias pyon='python3 "$path"/pyon.py'" >> ~/.bashrc
#echo "stty -ixon" >> ~/.bashrc
echo "~/.bashrc was updated!"