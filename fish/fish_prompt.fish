set -g __fish_git_prompt_showdirtystate 1        # * for unstaged, + for staged changes
set -g __fish_git_prompt_showuntrackedfiles 1    # % for untracked files
set -g __fish_git_prompt_showupstream auto       # ↑ ahead / ↓ behind the remote
set -g __fish_git_prompt_showstashstate 1        # $ if you have stashed changes
set -g __fish_git_prompt_color_branch d4a640            # brass
set -g __fish_git_prompt_color_dirtystate f0483b        # alarm red
set -g __fish_git_prompt_color_stagedstate 5cc96b       # cogitator green
set -g __fish_git_prompt_color_untrackedfiles e0a526    # amber
set -g __fish_git_prompt_color_upstream eadfc4          # bone
set -g __fish_git_prompt_char_upstream_ahead '↑'
set -g __fish_git_prompt_char_upstream_behind '↓'
set -g __fish_git_prompt_char_upstream_diverged '↕'
set -g __fish_git_prompt_char_upstream_equal ''      # hide it when in sync
set -g __fish_git_prompt_color_upstream_ahead 5cc96b
set -g __fish_git_prompt_color_upstream_behind e0a526

function fish_prompt
    set -l last_status $status
    set -l cog_color d4a640          # brass
    test $last_status -ne 0; and set cog_color f0483b   # red after a failed command

    set_color eadfc4
    echo -n (prompt_pwd)
    set_color normal
    echo -n (fish_vcs_prompt)
    echo -n ' '
    set_color $cog_color
    echo -n '⚙︎ '
    set_color normal
end