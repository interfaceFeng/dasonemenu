#!/bin/bash
if [ "$1" ];then
    echo sysadmin:$1 | chpasswd
    exit 0
else
    exit 222
fi


