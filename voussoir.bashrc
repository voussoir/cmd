export PS1='$(dirs)> '
export PYTHONDONTWRITEBYTECODE=1

unset HISTFILE
unset HISTFILESIZE

export PYTHONPATH=~/pythonpath:${PYTHONPATH}
export PATH=~/cmd:~/git/cmd:${PATH}
export EDITOR=/usr/bin/vim

alias ..='cd ..'
alias ls='ls -a --color=auto --group-directories-first'
alias ll='ls -l -a --color=auto --group-directories-first'
alias dir='ls -l -a --color=auto --group-directories-first'
alias move=mv
alias copy=cp
alias md=mkdir
alias cls=clear
alias gfa='git fetch --all'

# This generates a warning in some non-interactive situations, like cron.
bind TAB:menu-complete > /dev/null 2>&1

# In the user's .bashrc file, include this line at the top:
# [[ -r ~/git/cmd/voussoir.bashrc ]] && . ~/git/cmd/voussoir.bashrc
# and put additional configuration below.
