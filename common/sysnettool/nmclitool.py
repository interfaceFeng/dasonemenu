# -*- coding: utf-8 -*-

import subprocess
import shlex
import functools
import logs
from pipes import quote
import os
import re
from collections import defaultdict

NMCLICMD = 'sudo /usr/bin/nmcli'
BONDDIR = '/proc/net/bonding/'
LSPCI = '/usr/sbin/lspci'
FIND = 'sudo /usr/bin/find'
BRCTL = '/usr/sbin/brctl'


class NetworkError(Exception):
    pass


def run_cmd(cmd, whitelists=None):
    try:
        # args check
        cmd = shlex.split(cmd)
        args = [quote(cmd_word) for cmd_word in cmd]

        # whitelits check
        if whitelists is not None:
            if args[0] not in whitelists:
                raise Exception, 'not in white lists'

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        returncode = p.wait()
        return returncode, stdout, stderr
    except Exception as e:
        return -1, '', e.message


def net_cmd_run(cmd, ignore_error=False):
    status, stdout, stderr = run_cmd(cmd)
    if status != 0 and ignore_error is not True:
        raise NetworkError, stderr
    else:
        return status, stdout, stderr

# def net_cmd_decorator(ignore_error=False):
#     '''run the cmd and raise the error of runing cmd'''
#     def decorator(func):
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             cmd = func(*args, **kwargs)
#             returncode, stdout, stderr = run_cmd(cmd)
#             if returncode != 0 and ignore_error is not True:
#                 raise NetworkError, stderr
#             else:
#                 return returncode, stdout, stderr
#         return wrapper
#     return decorator

def nmcli_add_eth(eth_name, nmcli=NMCLICMD):
    cmd = '{nmcli} connection add type ethernet con-name {con_name} ifname {ifname} ' \
          'ipv4.method disabled ipv6.method ignore'.format(
        nmcli=nmcli,
        con_name=eth_name,
        ifname=eth_name)
    return net_cmd_run(cmd)

def nmcli_add_bond(bond_name, mode='1', nmcli=NMCLICMD):
    cmd = '{nmcli} connection add type bond con-name {con_name} ifname {ifname} mode {mode} ' \
          'ipv4.method disabled ipv6.method ignore connection.autoconnect-slaves 1'.format(
        nmcli=nmcli,
        con_name=bond_name,
        ifname=bond_name,
        mode=mode)
    return net_cmd_run(cmd)

def nmcli_mod_bond_mode(bond_name, mode='1', nmcli=NMCLICMD):
    cmd = '{nmcli} connection mod {bond_name} mode {mode}'.format(
        nmcli=nmcli,
        bond_name=bond_name,
        mode=mode)
    return net_cmd_run(cmd)

# def nmcli_add_bond_dev(bond_name, ifname, nmcli=NMCLICMD):
#     cmd = '{nmcli} connection add type bond-slave con-name {con_name} ifname {ifname} master {bond_name} '.format(
#         nmcli=nmcli,
#         con_name=if_name,
#         ifname=ifname,
#         bond_name=bond_name)
#     return net_cmd_run(cmd)


def nmcli_status_dev(dev_name, status, nmcli=NMCLICMD):
    cmd = '{nmcli} connection {status} {ifname} '.format(
        nmcli=nmcli,
        status=status,
        ifname=dev_name)
    return net_cmd_run(cmd)


def nmcli_up_dev(if_name):
    return nmcli_status_dev(if_name, 'up')


def nmcli_down_dev(if_name):
    return nmcli_status_dev(if_name, 'down')


def nmcli_del_dev(dev_name, nmcli=NMCLICMD):
    cmd = '{nmcli} connection del {ifname} '.format(
        nmcli=nmcli,
        ifname=dev_name)
    return net_cmd_run(cmd, ignore_error=True)


def nmcli_add_br(br_name, nmcli=NMCLICMD):
    cmd = '{nmcli} connection add type bridge con-name {con_name} ifname {ifname} ' \
          'ipv4.method disabled ipv6.method ignore'.format(
        nmcli=nmcli,
        con_name=br_name,
        ifname=br_name)
    return net_cmd_run(cmd)


# def nmcli_add_br_dev(br_name, dev, nmcli=NMCLICMD):
#     cmd = '{nmcli} connection add type bridge-slave con-name {con_name} ifname {if_name} master {br_name} '.format(
#         nmcli=nmcli,
#         con_name=dev,
#         if_name=dev,
#         br_name=br_name)
#     return net_cmd_run(cmd)

def nmcli_add_ip4(dev_name, ip_infos, nmcli=NMCLICMD):
    ip_list = []
    route_conf = ''
    # support the ip_infos is not list
    if isinstance(ip_infos, dict):
        ip_infos = [ip_infos,]

    for ip_info in ip_infos:
        for property_, value in ip_info.items():
            if property_ == 'address':
                ip_list.append('ipv4.{property_} {value} '.format(
                    property_=property_,
                    value=value))
            elif property_ == 'gateway':
                route_conf = 'ipv4.{property_} {value} '.format(
                    property_=property_,
                    value=value)
    ip_conf = '+'.join(ip_list)

    cmd = '{nmcli} connection modify {con_name} ipv4.method manual ipv6.method ignore {ip_conf} {route_conf}'.format(
        nmcli=nmcli,
        con_name=dev_name,
        ip_conf=ip_conf,
        route_conf=route_conf)
    return net_cmd_run(cmd)


def nmcli_flush_ip4(dev_name, nmcli=NMCLICMD):
    cmd = cmd = '{nmcli} connection modify {con_name} ipv4.method disabled ipv6.method ignore'.format(
        nmcli=nmcli,
        con_name=dev_name)
    return net_cmd_run(cmd)


def nmcli_reload(nmcli=NMCLICMD):
    cmd = '{nmcli} connection reload '.format(
        nmcli=nmcli)
    return net_cmd_run(cmd)


def nmcli_make_slave(master_name, slave_name, slave_type, nmcli=NMCLICMD):
    cmd = '{nmcli} connection modify {slave_name} master {master_name} slave-type {slave_type}'.format(
        nmcli=nmcli,
        slave_name=slave_name,
        master_name=master_name,
        slave_type=slave_type)
    return net_cmd_run(cmd)


def bond_list(bond_info_dir=BONDDIR):
    return os.listdir(bond_info_dir)


def nmcli_show_dev(dev_name, nmcli=NMCLICMD, show_type='connection'):
    cmd = '{nmcli} {show_type} show {dev_name} '.format(
        nmcli=nmcli,
        show_type=show_type,
        dev_name=dev_name)
    return net_cmd_run(cmd)


def rebuild_info_dict(dev_info):
    tmp_info_dict = {}
    # split the xx.yy to xx[yy]
    for info in dev_info.split('\n'):
        if info == '':
            continue

        info_list = info.split(':',1)
        key = info_list[0].strip()
        value = info_list[1].strip()
        value = (value, '')[value == '--']

        # split 'GENERAL.DEVICE' to ['GENERAL', 'DEVICE']
        # split 'IP4.ADDRESS[1]' to ['IP4', 'ADDRESS', '1', '']
        key_list = re.split(r'[.\[\]]', key)

        if len(key_list) == 2 :
            tmp_info_dict.setdefault(key_list[0], {})
            tmp_info_dict[key_list[0]][key_list[1]] = value
        elif len(key_list) == 4:
            # handle the situation
            # change 'IP4.ADDRESS[1]' to {'IP4':{'ADDRESS':{'1': ...}}}
            # tmp_dict = tmp_info_dict.setdefault(key_list[0], {})
            # tmp_dict.setdefault(key_list[1], {})
            tmp_info_dict.setdefault(key_list[0], {key_list[1]:{}})
            tmp_info_dict[key_list[0]].setdefault(key_list[1], {})
            tmp_info_dict[key_list[0]][key_list[1]][key_list[2]] = value
        elif len(key_list) == 1:
            tmp_info_dict[key_list[0]] = value

    return tmp_info_dict


def nmcli_dev_info(dev_name):
    _, dev_stdout, _ = nmcli_show_dev(dev_name, show_type='device')
    con_stdout = ''
    try:
        # add connection info
        _, con_stdout, _ = nmcli_show_dev(dev_name)
    except:
        pass

    stdout = con_stdout + dev_stdout
    dev_info = stdout.strip()

    return rebuild_info_dict(dev_info)

def nmcli_bond_info(bond):
    info_dict = nmcli_dev_info(bond)

def nmcli_check_dev(dev_name, nmcli=NMCLICMD):
    cmd = '{nmcli} con show {con_name}'.format(
        nmcli=nmcli,
        con_name=dev_name)
    try:
        net_cmd_run(cmd)
        return True
    except:
        return False

def dev_id_list(dev_type, lspci_cmd=LSPCI):
    cmd = '{lspci_cmd}'.format(
        lspci_cmd=lspci_cmd)
    _, lspci_info, _ = net_cmd_run(cmd)

    # get dev id list
    dev_info_list = lspci_info.split('\n')
    id_re = re.compile('^([0-9a-f]{2}\:[0-9a-f]{2}\.[0-9a-f])\s*%s' % dev_type)
    id_list = []

    for dev_info in dev_info_list:
        re_match = id_re.match(dev_info)
        if re_match:
            id_list.append(re_match.group(1))

    return id_list

def eth_name(id_list, find_cmd=FIND):
    cmd = '{find_cmd} /sys/devices -name {dev_id}'
    name_list = []

    for dev_id in id_list:
        eth_id = '0000:' + dev_id
        _, eth_path, _ = net_cmd_run(cmd.format(
            find_cmd=find_cmd,
            dev_id=eth_id))
        eth_path = eth_path.split('\n', 1)[0] + '/net'
        if not os.path.exists(eth_path):
            continue
        name_list.extend(os.listdir(eth_path))

    return name_list


def eth_list():
    id_list = dev_id_list('Ethernet')
    name_list = eth_name(id_list)
    return name_list

def br_list(brctl_cmd=BRCTL):
    cmd = '{brctl_cmd} show'.format(
        brctl_cmd=brctl_cmd)
    _, br_list_str, _ = net_cmd_run(cmd)

    br_list = br_list_str.strip().split('\n')
    br_list = br_list[1:]
    tmp_br_name_list = []
    for br_info in br_list:
        tmp_br_name = br_info.split('\t', 2)[0]
        tmp_br_name_list.append(tmp_br_name)

    return tmp_br_name_list


    # for dev_info in dev_info_list:
    #     re_match = dev_re.match(dev_info)
    #     if re_match:
    #         dev_id_list.append(re_match.group(1))


    # dev_basedir = '/sys/devices/pci0000:00/0000:{dev_id}/net/'
    # for dev_id in dev_id_list:
    #     dev_dir = dev_basedir.format(dev_id=dev_id)
    #     print(os.listdir(dev_dir))







