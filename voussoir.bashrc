export PS1='$(dirs)> '
export PYTHONDONTWRITEBYTECODE=1

unset HISTFILE
unset HISTFILESIZE

alias ..='cd ..'
alias ls='ls -a --color=auto --group-directories-first'
alias ll='ls -l -a --color=auto --group-directories-first'
alias dir='ls -l -a --color=auto --group-directories-first'
alias move=mv
alias copy=cp
alias md=mkdir

bind TAB:menu-complete
