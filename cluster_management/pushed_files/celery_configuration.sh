#!/usr/bin/env bash

#AJK TODO @Eli I'm putting this directly into the launch script; let me know if there's a good reason not to
#sudo pip install celery
#sudo apt-get install rabbitmq-server

user=$(grep -Po '"user":(\d*?,|.*?[^\\]")' rabbitmq.json | cut -d":" -f2 | sed 's/"//g' )
password=$(grep -Po '"password":(\d*?,|.*?[^\\]")' rabbitmq.json | cut -d":" -f2 | sed 's/"//g' )

sudo rabbitmqctl $(user) $(password)
sudo rabbitmqctl set_user_tags $(user) administrator
sudo rabbitmqctl set_permissions -p / $(user) ".*" ".*" ".*"


