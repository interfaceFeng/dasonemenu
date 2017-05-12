#!/bin/bash

sshd_config="/etc/ssh/sshd_config"

# ignore line with the head #
deny_re='^[^#]enyUsers.*sysadmin'
black_items=$(sudo cat $sshd_config | grep $deny_re)

if [ -z "$black_items" ];then
    exit 1
else
    exit 0
fi