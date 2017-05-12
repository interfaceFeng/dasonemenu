# -*- coding: utf-8 -*-

import yaml
import copy
from functools import wraps
import nmclitool
import traceback
import logging
import datetime

log = logging.getLogger("netstore")
log.debug(1)


def singleton(cls):
    instances = {}
    @wraps(cls)
    def get_instance(*wargs, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*wargs, **kwargs)
        return instances
    return get_instance


class NetStoreError(Exception):
    pass


class BaseDev(object):
    dev_propertys = set()

    def __init__(self, name=''):
        self.info = {}
        self.name = name
        for dev_property in self.dev_propertys:
            self.info[dev_property] = ''

    def set(self, dev_property, value):
        if self.check(dev_property, value):
            self.info[dev_property] = value
        else:
            return False

    def get(self, dev_property):
        if self.check(dev_property, ''):
            return copy.deepcopy(self.info[dev_property])

    def check(self, dev_property, value):
        if dev_property in self.dev_propertys:
            return True
        else:
            return False
            # raise NetStoreError, 'the {dev_property} is not in propertys'.format(dev_property=dev_property)


class DevDict(BaseDev):
    dev_propertys = {'Eth', 'Bond', 'Bridge', 'Gateway'}
    master_devs = {'Bond', 'Bridge'}
    slave_devs = {'Eth', 'Bond'}

    def __init__(self, name=''):
        super(DevDict, self).__init__(name)
        for dev_property in self.dev_propertys:
            self.info[dev_property] = {}

    def add_dev(self, dev_type, dev):
        if self.check(dev_type, dev):
            self.info[dev_type][dev.name] = dev

    def get_dev(self, dev_type, dev_name):
        if self.check_dev_exist(dev_type, dev_name):
            dev = self.get(dev_type)[dev_name]
            return copy.deepcopy(dev)

    def del_dev(self, dev_type, dev_name):
        dev = self.get_dev(dev_type, dev_name)
        del self.info[dev_type][dev_name]
        return dev

    def init_dev(self, dev_type, dev_name):
        if self.check(dev_type, dev_name):
            # TODO update to a more clever way
            return eval('{dev_type}(\'{dev_name}\')'.format(
                dev_type=dev_type,
                dev_name=dev_name))

    def check_dev_exist(self, dev_type, dev_name):
        if self.check(dev_type, '') and  dev_name in self.get(dev_type):
            return True
            # raise NetStoreError, 'the {dev_name} isn\'t exist'.format(dev_name=dev_name)
        else:
            return True
    
    def check(self, dev_property, value):
        return super(DevDict, self).check(dev_property, value)


class Eth(BaseDev):
    dev_propertys = {'master', 'mac', 'abstract', 'status'}

    def __init__(self, name=''):
        super(Eth, self).__init__(name)

    def check(self, dev_property, value):
        return super(Eth, self).check(dev_property, value)


class Bond(BaseDev):
    dev_propertys = {'mode', 'slave', 'ip4', 'gateway4', 'ip6', 'gateway6', 'dns', 'master'}

    def __init__(self, name=''):
        super(Bond, self).__init__(name)

    def check(self, dev_property, value):
        return super(Bond, self).check(dev_property, value)


class Bridge(BaseDev):
    dev_propertys = {'ip4', 'slave', 'gateway4', 'ip6', 'gateway6', 'dns'}

    def __init__(self, name=''):
        super(Bridge, self).__init__(name)

    def check(self, dev_property, value):
        return super(Bridge, self).check(dev_property, value)


class Gateway(BaseDev):
    dev_propertys = {'ip4', 'ip6'}

    def __init__(self, name=''):
        super(Gateway, self).__init__(name)

    def check(self, dev_property, value):
        return super(Gateway, self).check(dev_property, value)


class BaseStore(object):
    setting_file = './strings//netsetting.yaml'
    def __init__(self, setting_file=None):
        if setting_file is not None:
            self.setting_file = setting_file

    def save_file(self, settings):
        with file(self.setting_file, 'w') as f:
            yaml.dump(settings, f, default_flow_style=False)

    def load_file(self):
        with file(self.setting_file, 'r')as f:
            return yaml.load(f)


class NetInfo(BaseStore):
    setting_file = './strings/netsetting.yaml'
    def __init__(self, setting_file=None):
        self.number = 0
        super(NetInfo, self).__init__(setting_file=setting_file)
        # create the dev initialization dict
        self.dev_dict = None
        # self.init_dev_dict()
        self.load()

    def init_dev_dict(self, settings=None):
        # base on the settings, create the dev set
        # tmp_set.info = {'Eth': {}}
        dev_dict = DevDict()
        if settings is None:
            pass
        else:
            try:
                for dev_type, devs in settings.items():
                    tmp_dev_dict = {}
                    for dev_name, dev_propertys in devs.items():
                        tmp_dev = dev_dict.init_dev(dev_type, dev_name)
                        for dev_property, value in dev_propertys.items():
                            tmp_dev.set(dev_property, value)
                        tmp_dev_dict[dev_name] = tmp_dev
                    dev_dict.set(dev_type, tmp_dev_dict)
            except Exception as e:
                raise NetStoreError, 'there is some problem in settings'
        self.dev_dict = dev_dict
        self.refresh_real_eth()
        self.refresh_slave_list()
        self.write()

    def load(self):
        # net_info = {'eths': {'eth1': {...},
        #                      'eth2': {...}}
        #             'bonds': {'bond1': {...},
        #                       'bond2': {...}}}
        try:
            settings = self.load_file()
            self.init_dev_dict(settings)
        except IOError as e:
            # need to handle Exception
            self.init_dev_dict()
            # raise NetStoreError, 'read file error, {message}'.format(message=str(e))
        except Exception as e:
            self.init_dev_dict()
            raise e

    def write(self):
        # dev_dict transform into settings
        tmp_settings = {}
        for dev_type in self.dev_dict.dev_propertys:
            tmp_settings[dev_type] = {}
            for dev_name, dev in self.dev_dict.get(dev_type).items():
                tmp_settings[dev_type][dev_name] = {}
                for dev_property in dev.dev_propertys:
                    tmp_settings[dev_type][dev_name][dev_property] = dev.get(dev_property)
        self.save_file(tmp_settings)

    def get_dev(self, dev_type, dev_name, **kwargs):
        return copy.deepcopy(self.dev_dict.get_dev(dev_type, dev_name))

    def add_dev(self, dev_type, dev_name, **kwargs):
        dev = self.dev_dict.init_dev(dev_type, dev_name)
        for dev_propertys, value in kwargs.items():
            dev.set(dev_propertys, value)
        self.dev_dict.add_dev(dev_type, dev)

    def mod_dev(self, dev_type, dev_name, **kwargs):
        dev = self.dev_dict.get_dev(dev_type, dev_name)
        for dev_propertys, value in kwargs.items():
            dev.set(dev_propertys, value)
        self.dev_dict.add_dev(dev_type, dev)

    def update_bond_info(self, bond_infos):
        try:
            for bond_name, bond_info in bond_infos.items():

                # translate bond info
                store_info = self.bond_store_translate(bond_info)
                nmcli_info = self.bond_nmcli_translate(bond_info)

                # create bond
                nmclitool.nmcli_del_dev(bond_name)
                nmclitool.nmcli_add_bond(bond_name, nmcli_info['mode'])
                nmclitool.nmcli_add_ip4(bond_name, nmcli_info['ipv4'])
                # nmclitool.nmcli_up_dev(bond_name)
                self.add_dev('Bond', bond_name, ip4=store_info['ip4'], mode=store_info['mode'])

                # modify eth
                for slave_name in store_info['slave_list']:
                    nmclitool.nmcli_del_dev(slave_name)
                    nmclitool.nmcli_add_eth(slave_name)
                    nmclitool.nmcli_make_slave(bond_name, slave_name, 'bond')
                    # nmclitool.nmcli_up_dev(slave_name)
                    self.mod_dev('Eth', slave_name, master=bond_name)
                # self.refresh_slave_list()
            self.write()
            return True, ''
        except Exception as e:
            traceback.print_exc(file=file("./123456", 'w'))
            return False, e.message

    def get_bond_info(self):
        self.refresh_real_eth()
        self.refresh_slave_list()
        bond_info = {}
        master_type = 'Bond'
        for bond_name, bond_dev in self.dev_dict.get(master_type).items():
            bond_info[bond_name] = self.bond_interface_translate(bond_dev)
        return bond_info

    def get_default_gateway(self):
        return self.dev_dict.get('Gateway')['gateway'].get('ip4')

    def get_eth_info(self):
        self.refresh_real_eth()
        eth_info = {}
        for eth_name, eth_dev in self.dev_dict.get('Eth').items():
            eth_info[eth_name] = self.eth_interface_translate(eth_dev)
        return eth_info

    def update_eth_info(self, eth_infos):
        try:
            for eth_name, eth_info in eth_infos.items():
                eth_dev = self.dev_dict.get_dev('Eth', eth_name)
                if eth_dev:
                    store_info = self.eth_store_translate(eth_info)
                    nmcli_info = self.eth_nmcli_translate(eth_info)

                    nmclitool.nmcli_del_dev(eth_name)
                    nmclitool.nmcli_add_eth(eth_name)
                    if nmcli_info['master'] in self.dev_dict.get('Bond'):
                        nmclitool.nmcli_make_slave(nmcli_info['master'], eth_name, 'bond')
                    else:
                        raise NetStoreError, '{master} not exist'.format(master=nmcli_info['master'])
                    nmclitool.nmcli_status_dev(eth_name, nmcli_info['status'])
                    # TODO need to handle the 'abstract'
                    self.mod_dev('Eth', eth_name, master=store_info['master'], status=store_info['status'])
                else:
                    raise NetStoreError, '{eth_name} not exist'.format(eth_name=eth_name)
            return True, ''
        except Exception as e:
            return False, e.message

    @staticmethod
    def bond_store_translate(bond_info):
        # rebuild the bond_info to the format of bond's propertys
        store_info = {}
        store_info['ip4'] = bond_info['ipv4']['address'] + '/' + str(netmask_2_cidr(bond_info['ipv4']['netmask']))
        store_info['slave_list'] = bond_info['devs']
        store_info['mode'] = bond_info['mode']
        return store_info

    @staticmethod
    def bond_nmcli_translate(bond_info):
        # rebuild the bond_info to the format of nmclitool
        nmcli_info = {}
        nmcli_info['ipv4'] = {}
        nmcli_info['ipv4']['address'] = bond_info['ipv4']['address'] + '/' + str(netmask_2_cidr(bond_info['ipv4']['netmask']))
        nmcli_info['mode'] = bond_info['mode']
        return nmcli_info

    @staticmethod
    def bond_interface_translate(bond_dev):
        tmp_bond_info = {}
        tmp_bond_info['devs'] = bond_dev.get('slave')
        ip4, cidr = bond_dev.get('ip4').split('/')
        tmp_bond_info['ipv4'] = {}
        tmp_bond_info['ipv4']['address'] = ip4

        tmp_bond_info['ipv4']['netmask'] = cidr_2_netmask(int(cidr))
        tmp_bond_info['master'] = bond_dev.get('master')
        tmp_bond_info['mode'] = bond_dev.get('mode')
        return tmp_bond_info

    @staticmethod
    def eth_store_translate(eth_info):
        store_info = {}
        store_info['master'] = eth_info['master']
        store_info['abstract'] = eth_info['abstract']
        store_info['status'] = eth_info['status']
        return store_info

    @staticmethod
    def eth_nmcli_translate(eth_info):
        nmcli_info = {}
        nmcli_info['master'] = eth_info['master']
        nmcli_info['abstract'] = eth_info['abstract']
        nmcli_info['status'] = eth_info['status']
        return nmcli_info

    @staticmethod
    def eth_interface_translate(eth_dev):
        tmp_eth_info = {}
        tmp_eth_info['master'] = eth_dev.get('master')
        tmp_eth_info['abstract'] = eth_dev.get('abstract')
        tmp_eth_info['status'] = eth_dev.get('status')
        return tmp_eth_info



    def del_dev(self, dev_type, dev_name):
        nmclitool.nmcli_del_dev(dev_name)
        self.dev_dict.del_dev(dev_type, dev_name)

    def refresh_slave_list(self):
        for master_type in self.dev_dict.master_devs:
            for master_name, master_dev in self.dev_dict.get(master_type).items():
                slave_list = []
                for slave_type in self.dev_dict.slave_devs:
                    for slave_name, slave_dev in self.dev_dict.get(slave_type).items():
                        if slave_dev.get('master') == master_name and master_name != '':
                            slave_list.append(slave_name)
                master_dev.set('slave', slave_list)
                self.dev_dict.add_dev(master_type, master_dev)

    def clear_type(self, dev_type):
        for dev_name in self.dev_dict.get(dev_type):
            self.dev_dict.del_dev(dev_type, dev_name)

    def refresh_real_eth(self):
        self.clear_type('Eth')
        eth_list = nmclitool.eth_list()
        for eth_name in eth_list:
            if nmclitool.nmcli_check_dev(eth_name) is False:
                nmclitool.nmcli_del_dev(eth_name)
                nmclitool.nmcli_add_eth(eth_name)
                nmclitool.nmcli_up_dev(eth_name)
            eth_info = nmclitool.nmcli_dev_info(eth_name)
            # {'master', 'mac'}
            eth_master = dict_spider(eth_info, 'connection', 'master')
            eth_mac = dict_spider(eth_info, 'GENERAL', 'HWADDR')
            eth_status = dict_spider(eth_info, 'WIRED-PROPERTIES', 'CARRIER')
            self.add_dev('Eth', eth_name, master=eth_master, mac=eth_mac, status=eth_status)


def dict_spider(init_dict, *keys):
    # if key not in init_dict, return ''
    if keys[0] in init_dict.keys():
        if len(keys) == 1:
            return init_dict[keys[0]]
        else:
            return dict_spider(init_dict[keys[0]], *keys[1:])
    else:
        return ''


def netmask_2_cidr(netmask):
    return sum([bin(int(i)).count('1') for i in netmask.split('.')])

def cidr_2_netmask(cidr):
    return '.'.join([str((0xffffffff << (32 - cidr) >> i) & 0xff) for i in [24, 16, 8, 0]])



