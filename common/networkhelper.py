import urwid
import sys
import os
import logging
from settings import Settings

log = logging.getLogger('networkhelper')

network_file = "%s/dasonemenu/common/network.yaml"%os.path.dirname(sys.path[0])

def get_bond_info():

    bond_info_dic = Settings.read(network_file)
    if bond_info_dic["BOND"] is None:
        return {}
    else:
        return bond_info_dic["BOND"]

def get_bridge_info():

    bridge_info_dic = Settings.read(network_file)
    if bridge_info_dic["BRIDGE"] is None:
        return {}
    else:
        return bridge_info_dic["BRIDGE"]


def get_eth_info():
    bond_info_dic = Settings.read(network_file)
    if bond_info_dic["ETH"] is None:
        return {}
    else:
        return bond_info_dic["ETH"]

def get_default_gateway():
    return "10.11.0.1"


def update_bond_info(bond_info):
    bond_info_dic = Settings.read(network_file)
    bond_info_dic["BOND"] = bond_info
    # bond_info_dic = {"BOND": bond_info_dic}
    Settings.write(bond_info_dic, defaultsfile=network_file, outfn=network_file)
    return True, ""

def update_bridge_info(bridge_info):
    bridge_info_dic = Settings.read(network_file)
    bridge_info_dic["BRIDGE"] = bridge_info
    Settings.write(bridge_info_dic, defaultsfile=network_file, outfn=network_file)
    return True, ""

def update_eth_info(eth_info):
    bond_info_dic = Settings.read(network_file)
    bond_info_dic["ETH"] = eth_info
    Settings.write(bond_info_dic, defaultsfile=network_file, outfn=network_file)
    return True, ""