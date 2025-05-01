#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '

export PATH=$PATH:/usr/bin

# Golang env
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
