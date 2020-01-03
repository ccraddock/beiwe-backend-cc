# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific aliases and functions


# load the current environment variables for the ssh session
alias load='`cat /opt/python/current/env`'

alias code='cd /opt/python/current/env'

alias logs="alias | grep -i log"
alias log_commands="tail -f  /var/log/cfn-init-cmd.log"
alias loge="tail -f /var/log/httpd/error_log"

alias sudo="sudo "
alias n="nano "
alias sn="sudo nano "

alias pyc='find . -type f -name "*.pyc" -delete -print'
alias htop="htop -d 5"

alias u="cd .."
alias uu="cd ../.."
alias uuu="cd ../../.."

alias ls='ls --color=auto'
alias la='ls -A'
alias ll='ls -lh'
alias lh='ls -lhX --color=auto'

alias py="python"
alias ipy="ipython"
