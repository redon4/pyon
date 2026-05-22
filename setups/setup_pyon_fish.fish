set dir (pwd)

if string match -q "*/pyon*" $dir
    set pyon_dir (string match -r '.*/pyon' $dir)
else
    echo "No parent folder named \"pyon\""
    exit 1
end

set file_dir (find $pyon_dir -name pyon.py -print -quit)
printf "function pyon\n    python3 $file_dir \$argv\nend" > ~/.config/fish/functions/pyon.fish

source ~/.config/fish/functions/pyon.fish

echo "fish function was added!"
