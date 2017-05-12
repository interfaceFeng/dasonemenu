#!/bin/bash

sshd_config="/etc/ssh/sshd_config"

# ignore line with the head #
deny_head='^[^#].*enyUsers'
deny_re='^[^#]enyUsers.*sysadmin'
black_line=$(sudo cat $sshd_config | grep $deny_head)
black_items=$(sudo cat $sshd_config | grep $deny_re)

# close ssh login
if [ "$1" = "-c" ];then

    # the file has not set black items
    if [ -z "$black_line" ];then
        sudo sed -i '$a\DenyUsers sysadmin' $sshd_config
    # the file has set black items

    else

        # the black items do not contain sysadmin
        if [ -z "$black_items"];then
            sudo sed -i 's/'^[^#].*enyUsers'/& sysadmin/' $sshd_config
        # the black items contain sysadmin

        fi

    fi
# open ssh login
else
    # sysadmin is in black items
    if [ ! -z "black_items" ];then
        sudo sed -i 's/\(^[^#].*enyUsers.*\)sysadmin\(.*\)/\1\2/' $sshd_config
    # sysadmin is not in black items

    fi

fi

sudo systemctl restart sshd.service