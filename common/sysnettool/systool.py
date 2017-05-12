#!/usr/bin/python
# -*- coding: utf-8 -*-

import common.sysnettool.nmclitool as nmclitool
import functools
import common.sysnettool.netstore as netstore
import logging

log = logging.getLogger("systool")
net = netstore.NetInfo()


def exception(log_file='./test.log'):
    def mylog(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except nmclitool.NetworkError as e:
                with open(log_file, "a") as f:
                    f.write(e.str())
        return wrapper
    return mylog


def get_bond_info():
    # if not specify, return all bond
    # else return the bond in bond_List
    # returt {'bond0': {'devs': ['eth0', ...],
    #                   'ipv4': {'ip':'xx', 'netmask':'xx'}}
    #        'bond1': ...}
    return net.get_bond_info()


def get_default_gateway():
    # if no specify, return default gateway
    # else return the gateway of gateway
    return net.get_default_gateway()

def get_eth_info():
    # if no specify, return all eth info
    # else the info of eth in eth_list
    # return {'eth0': {'master': 'bond1',
    #                  'abstract': '...',
    #                  'status': 'up/down'}
    #        'eth1': ...}
    return net.get_eth_info()

def update_bond_info(bonds_info):
    # update the bond info
    # bond_info =  {'bond0': {'devs': ['eth0', ...],
    #                         'ipv4': {'ip':'xx', 'netmask':'xx'}}
    #               'bond1': ...}
    # return (True/False, Log)
    return net.update_bond_info(bonds_info)

def update_eth_info(eths_info):
    # update the eth info
    # eths_info = {'eth0': {'master': 'bond1',
    #                       'abstract': '...',
    #                       'status': 'up/down'}
    #              'eth1': ...}
    # return (True/False, Log)
    return net.update_eth_info(eths_info)



# def del_dev(dev):
#     nmciltool.nmcli_down_dev(dev)
#     nmciltool.nmcli_del_dev(dev)
#
# def add_bond(bond_name, mode):
#     del_dev(bond_name)
#     nmciltool.nmcli_create_bond(bond_name, mode)
#     nmciltool.nmcli_down_dev(bond_name)
#
# def del_bond(bond_name):
#     nmciltool.nmcli_del_dev(bond_name)
#
# def add_bond_dev(bond_name, dev):
#     del_dev(dev)
#     nmciltool.nmcli_add_bond_dev(bond_name, dev)
#
# def del_bond_dev(dev):
#     del_dev(dev)
#
# def set_bond_ip(bond_name, ipv4):
#     nmciltool.nmcli_down_dev(bond_name)
#     nmciltool.nmcli_add_ip(bond_name, ipv4)
#     nmciltool.nmcli_up_dev(bond_name)
#
# def add_bridge(br_name):
#     nmciltool.nmcli_del_dev(br_name)
#     nmciltool.nmcli_add_br(br_name)
#     nmciltool.nmcli_down_dev(br_name)
#
# def del_bridge(br_name):
#     nmciltool.nmcli_del_dev(br_name)
#
# def add_brideg_dev(br_name, dev):
#     nmciltool.nmcli_add_br_dev(br_name, dev)
#
# def del_bridge_dev(dev):
#     nmciltool.nmcli_del_dev(dev)
#
# def set_bridge_ip(br_name, ipv4):
#     nmciltool.nmcli_add_ip(br_name, ipv4)
#     nmciltool.nmcli_up_dev(br_name)
#
# def get_bond_info():
#     bond = 'bond2'
#     info_dict = nmciltool.nmcli_bond_info(bond)
#     info_map = {'devs': 'devs',
#                 'ipv4': 'ipv4.addresses'}


