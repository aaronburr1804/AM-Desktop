function fish_prompt
    set -l last_status $status
    set -l cog_color d4a640          # brass
    test $last_status -ne 0; and set cog_color f0483b   # red after a failed command

    set_color eadfc4
    echo -n (prompt_pwd)
    set_color normal
    echo -n ' '
    set_color $cog_color
    echo -n '⚙︎ '
    set_color normal
end