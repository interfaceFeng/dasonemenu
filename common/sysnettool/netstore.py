# -*- coding: utf-8 -*-

import yaml
import copy
import os
from functools import wraps
import nmclitool
from collections import defaultdict
import re


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


class DevExistError(NetStoreError):
    pass


class ParamentError(NetStoreError):
    pass


class BaseDev(object):
    property_dict = {'device': ''}

    def __init__(self, **property_dict):
        self.info = copy.deepcopy(self.property_dict)
        self.check_dict = {'ip4': self.check_ip4_list}
        self.init_info(**property_dict)

    @property
    def dev_propertys(self):
        return self.property_dict.keys()

    def init_info(self, **property_dict):
        try:
            self.info['device'] = property_dict.pop('device')
        except KeyError as e:
            raise NetStoreError, 'need to set device name'
        self.modify(**property_dict)

    def to_dict(self):
        return copy.deepcopy(self.info)

    def modify(self, **kwargs):
        for dev_property, value in kwargs.items():
            if not self.check_info(dev_property, value):
                raise ParamentError, '{value} not fit {dev_property}'.format(dev_property=dev_property,value=value)

            if dev_property == 'device':
                continue
            self.info[dev_property] = value

    def get(self, dev_property):
        if self.check_info(dev_property, None):
            return copy.deepcopy(self.info[dev_property])
        else:
            raise DevExistError, '{dev_property} not exist'.format(
                dev_property=dev_property)

    def check_ip4_list(self, ip4_list):
        if ip4_list is None:
            # if is None ,mean that check the name of property
            return True
        ip4_check_dict = {'address': self.check_ip4,
                          'netmask': self.check_ip4,
                          'gateway': self.check_ip4}

        for ip4 in ip4_list:
            if 'address' not in ip4 or 'netmask'not in ip4:
                return False

            for ip4_property, value in ip4.items():
                if not ip4_check_dict[ip4_property](value):
                    return False

        return True

    def check_ip4(self, ip4):
        return check_ip4(ip4)

    def check_info(self, dev_property, *args, **kwargs):
        # use the check_dict to check the value of dev_property
        if dev_property not in self.dev_propertys:
            return False
        return self.check_dict.get(dev_property, lambda *x, **y: True)(*args, **kwargs)


class Eth(BaseDev):
    property_dict = {'device': '',
                     'master': '',
                     'mac': '00:00:00:00:00:00',
                     'abstract': {'status': 'down'}}

    def __init__(self, **property_dict):
        super(Eth, self).__init__(**property_dict)


class MasterDev(BaseDev):
    def __init__(self, **property_dict):
        slave_info = property_dict.pop('slave', self.property_dict['slave'])
        super(MasterDev, self).__init__(**property_dict)

        check_dict = {'slave': self.check_slave}
        self.check_dict.update(check_dict)
        # self.add_slave(slave_info)
        self.mod_slave('add', slave_info)

    def modify(self, **kwargs):
        slave_info = kwargs.pop('slave', {})
        # if slave_info:
        #     self.modify_slave(slave_info)
        return super(MasterDev, self).modify(**kwargs)

    # def add_slave(self, slave_info):
    #     for slave_type, slave_list in slave_info.items():
    #         if not self.check_info('slave', slave_type):
    #             raise ParamentError, '{slave_type} not in slave_type'.format(slave_type=slave_type)
    #
    #         self.info['slave'][slave_type].update(slave_list)
    #
    # def del_slave(self, slave_info):
    #     for slave_type, slave_list in slave_info.items():
    #         if not self.check_info('slave', slave_type):
    #             raise ParamentError, '{slave_type} not in slave_type'.format(slave_type=slave_type)
    #
    #         self.info['slave'][slave_type].discard(slave_list)

    def mod_slave(self, mod_method, slave_info):
        for slave_type, slave_list in slave_info.items():
            if not self.check_info('slave', slave_type):
                raise ParamentError, '{slave_type} not in slave_type'.format(slave_type=slave_type)

            if mod_method == 'add':
                self.info['slave'][slave_type].update(slave_list)
            elif mod_method == 'del':
                if not isinstance(slave_list, list):
                    slave_list = [slave_list]
                for slave_name in slave_list:
                    self.info['slave'][slave_type].discard(slave_name)

    def check_slave(self, slave_type=None, slave_name=None):
        if slave_type is None:
            # if is None ,mean that check the name of property
            return True

        if slave_type not in self.info['slave']:
            return False

        return True

    # def modify_slave(self, init_slave_info):
    #     slave_info = copy.deepcopy(self.info['slave'])
    #     add_slave_info = init_slave_info.pop('add', {})
    #     del_slave_info = init_slave_info.pop('del', {})
    #
    #     for slave_type, slave_list in add_slave_info.items():
    #         slave_list = set(slave_info[slave_type]).add(slave_name)
    #         slave_info[slave_type] =
    #
    #     for slave_type, slave_name in del_slave_info.items():
    #         pass
    #
    #     self.info['slave'] = slave_info

    # def add_slave(self, slave_type, slave_list):
    #     if isinstance(slave_list, str):
    #         slave_list = [slave_list,]


class Bond(MasterDev):
    property_dict = {'device': '',
                     'mode': '1',
                     'slave': {'Eth': set()},
                     'master': '',
                     'ip4': [],
                     'ip6': []}

    def __init__(self, **property_dict):
        super(Bond, self).__init__(**property_dict)
        self.check_dict.update({'mode': self.check_mode})

    def check_mode(self, mode):
        if mode is None:
            # if is None ,mean that check the name of property
            return True

        if not bond_mode_convert(mode):
            return False

        return True



class Bridge(MasterDev):
    property_dict = {'device': '',
                     'slave': {'Eth': set(),
                                'Bridge': set()},
                     'ip4': [],
                     'ip6': []}

    def __init__(self, **property_dict):
        super(Bridge, self).__init__(**property_dict)


class Gateway(BaseDev):
    property_dict = {'device': '',
                     'ip4': '0.0.0.0',
                     'ip6': '::'}

    def __init__(self, **property_dict):
        super(Gateway, self).__init__(**property_dict)


class DevDict(BaseDev):
    # dev_propertys = {'Eth', 'Bond', 'Bridge', 'Gateway'}
    # master_devs = {'Bond', 'Bridge'}
    # slave_devs = {'Eth', 'Bond'}
    property_dict = {'Eth': {},
                     'Bond': {},
                     'Bridge': {},
                     'Gateway': {}}

    master_index = {'Eth': ['Bridge'],
                    'Bond': ['Bridge']}

    def __init__(self, **property_dict):
        super(DevDict, self).__init__(**property_dict)

    def init_info(self, **property_dict):
        self.modify(**property_dict)

    def to_dict(self):
        tmp_dict = copy.deepcopy(self.property_dict)
        for dev_type, dev_dict in self.info.items():
            for dev_name, dev in dev_dict.items():
                tmp_dict[dev_type][dev_name] = dev.to_dict()

        return tmp_dict

    def add_dev(self, dev_type, dev_name, *dev_tuple, **kwargs):
        # if dev_name in self.info[dev_type]:
        if self.dev_exist(dev_type, dev_name):
            raise DevExistError, '{dev_name} already exist in {dev_type}'.format(dev_name=dev_name,dev_type=dev_type)
        if not self.check_info(dev_type):
            raise DevExistError, '{dev_type} not exist'.format(dev_type=dev_type)

        if dev_tuple:
            if not isinstance(dev_tuple[0], BaseDev):
                raise ParamentError, 'dev_tuple type is not dev'

            dev = dev_tuple[0]
        else:
            dev = self.init_dev(dev_type, dev_name, **kwargs)

        self.info[dev_type][dev_name] = dev

        return copy.deepcopy(dev)

    def get_dev(self, dev_type, dev_name):
        if not self.dev_exist(dev_type, dev_name):
            raise DevExistError, '{dev_name} not exist in {dev_type}'.format(dev_name=dev_name,dev_type=dev_type)

        dev = self.info[dev_type][dev_name]
        return copy.deepcopy(dev)

    def mod_dev(self, dev_type, dev_name, **kwargs):
        dev = self.get_dev(dev_type, dev_name)
        dev.modify(**kwargs)
        self.info[dev_type][dev_name] = dev

        return copy.deepcopy(dev)

    def del_dev(self, dev_type, dev_name):
        try:
            dev = self.get_dev(dev_type, dev_name)
            self.info[dev_type].pop(dev_name)
            return dev
        except DevExistError:
            return None

    def init_dev(self, dev_type, dev_name, **info_dict):
        if not self.check_info(dev_type):
            raise DevExistError, '{dev_type} not exist'.format(dev_type=dev_type)

        info_dict['device'] = dev_name
        # TODO update to a more clever way
        return eval('{dev_type}(**{info_dict})'.format(dev_type=dev_type,info_dict=str(info_dict)))

    # def add_slave(self, master_type, master_name, slave_type, slave_name):
    #     # if not self.dev_exist(master_type, master_name):
    #     #     raise DevExistError, '{dev_name} not exist'.format(
    #     #         dev_name=master_name)
    #     # master_dev = self.get_dev(master_type, master_name)
    #     # slave_list = set(master_dev.get('slave'))
    #     # slave_list.add(slave_name)
    #     # self.mod_dev(master_type, master_name, slave=list(slave_list))
    #     master_dev = self.get_dev(master_type, master_name)
    #     slave_info = {slave_type: [slave_name]}
    #     master_dev.add_slave(slave_info)
    #     self.info[master_type][master_name] = master_dev
    #
    # def del_slave(self, master_type, master_name, slave_type, slave_name):
    #     master_dev = self.get_dev(master_type, master_name)
    #     slave_info = {slave_type: [slave_name]}
    #     master_dev.del_slave(slave_info)
    #     self.info[master_type][master_name] = master_dev

    def mod_slave(self, mod_method, master_type, master_name, slave_type, slave_name):
        master_dev = self.get_dev(master_type, master_name)
        slave_info = {slave_type: [slave_name]}
        master_dev.mod_slave(mod_method, slave_info)
        self.info[master_type][master_name] = master_dev

        return master_dev

    def dev_list(self, dev_type):
        return self.info[dev_type].keys()

    def init_from_dict(self, settings):
        for dev_type, devs in settings.items():
            for dev_name, dev_propertys in devs.items():
                self.add_dev(dev_type, dev_name, **dev_propertys)

    def dev_exist(self, dev_type, dev_name):
        if self.check_info(dev_type) and dev_name in self.info[dev_type].keys():
            return True
        else:
            return False


class BaseStore(object):
    setting_file = './netsetting.yaml'

    def __init__(self, setting_file=None):
        if setting_file:
            self.setting_file = setting_file

        basedir = os.path.dirname(self.setting_file)
        if not os.path.exists(basedir):
            os.mkdir(basedir, 644)

    def save(self, settings):
        with file(self.setting_file, 'w') as f:
            yaml.dump(settings, f, default_flow_style=False)

    def load(self):
        with file(self.setting_file, 'r')as f:
            return yaml.load(f)


class NetInfo(object):
    def __init__(self, setting_file=None):
        self.store = BaseStore(setting_file)
        # create the dev initialization dict
        self.dev_dict = None
        self.init_dev_dict()
        self.refresh_real_bond()
        self.refresh_real_eth()
        # self.refresh_slave_list()

    def init_dev_dict(self, settings=None):
        # use settings to create the dev set
        # tmp_set.info = {'Eth': {}}
        settings = self.load() if settings is None else settings
        try:
            self.dev_dict = DevDict()
            self.dev_dict.init_from_dict(settings)
        except Exception as e:
            return -1, 'there is some problem in settings'

    def load(self):
        # net_info = {'eths': {'eth1': {...},
        #                      'eth2': {...}}
        #             'bonds': {'bond1': {...},
        #                       'bond2': {...}}}
        try:
            return self.store.load()
        except Exception as e:
            return None

    def save(self):
        self.store.save(self.dev_dict.to_dict())

    def get_dev_info(self, dev_type):
        tmp_dev_info = {}
        preprocess_dict = {'Eth': self.refresh_real_eth}

        preprocess_dict.get(dev_type, lambda: True)()
        for dev_name in self.dev_dict.dev_list(dev_type):
            tmp_dev_info[dev_name] = self.dev_dict.get_dev(dev_type, dev_name).to_dict()

        return tmp_dev_info

    def add_bond(self, bond_name, bond_info):
        # add bond and mod slave
        bond_type = 'Bond'
        slave_type = 'Eth'
        # bond_info = self.init_info(bond_type, init_bond_info)
        slave_info = bond_info.pop('slave', {})
        # if self.dev_dict.dev_exist(bond_type, bond_name):
        #     return False, '{bond_name} alread exist'.format(bond_name=bond_name)

        try:
            # add bond
            bond_dev = self.dev_dict.add_dev(bond_type, bond_name, **bond_info)
            self.hw_add_dev(bond_type, bond_name, bond_dev.get('mode'))
            # if bond_info.get('ip4', None):
            self.hw_add_ip4(bond_name, bond_dev.get('ip4'))
            self.hw_up_dev(bond_name)

            # add slave
            for slave_name in slave_info.get(slave_type, []):
                self.add_slave(bond_type, bond_name, slave_type, slave_name)
                # self.mod_slave('add', bond_type, bond_name, slave_type, slave_name)
                # self.hw_make_slave(bond_type, bond_name, slave_type, slave_name)
                # self.hw_up_dev(slave_name)
                # self.dev_dict.mod_dev(slave_type, slave_name, master=bond_name)
                # self.dev_dict.add_slave(bond_type, bond_name, slave_type, slave_name)

        except Exception as e:
            # del bond
            status, message = self.del_bond(bond_name)

            if not status:
                return False, repr(e) + ' ' + message
            return False, repr(e)

        self.save()
        return True, ''

    def del_bond(self, bond_name):
        # delete bond and init the slave
        bond_type = 'Bond'
        slave_type = 'Eth'

        try:
            # delete bond
            bond_dev = self.dev_dict.del_dev(bond_type, bond_name)
            if not bond_dev:
                return False, '{bond_name} not exist'.format(
                    bond_name=bond_name)
            self.hw_del_dev(bond_type, bond_name)
            # if not self.dev_dict.dev_exist(bond_type, bond_name):
            #     return False, '{bond_name} not exist'.format(
            #         bond_name=bond_name)

            # init the slave
            for slave_name in bond_dev.get('slave')[slave_type]:
                self.dev_dict.mod_dev(slave_type, slave_name, master='')
                self.hw_del_dev(slave_type, slave_name)
                self.hw_add_dev(slave_type, slave_name)
                self.hw_up_dev(slave_name)

        except:
            return False, 'Error delete {bond_name}'.format(bond_name=bond_name)

        self.save()
        return True, ''

    def update_bond(self, bond_name, bond_info):
        # update bond and slave
        bond_type = 'Bond'
        slave_type = 'Eth'

        def update_ip4():
            # update ip4
            if bond_dev.get('master') != '':
                return False, 'Bond is slave, error set ip4'
            new_bond_info = self.dev_dict.mod_dev(bond_type, bond_name, ip4=bond_info['ip4'])
            self.hw_add_ip4(bond_name, new_bond_info.get('ip4'))

        def update_slave():
            # update slave
            add_slave_list = set(bond_info['slave'][slave_type]) - set(bond_dev.get('slave')[slave_type])
            del_slave_list = set(bond_dev.get('slave')[slave_type]) - set(bond_info['slave'][slave_type])
            for slave_name in add_slave_list:
                self.add_slave(bond_type, bond_name, slave_type, slave_name)

            for slave_name in del_slave_list:
                self.del_slave(bond_type, bond_name, slave_type, slave_name)

        def update_mode():
            # update mode
            self.dev_dict.mod_dev(bond_type, bond_name, mode=bond_info['mode'])
            self.hw_mod_bond_mode(bond_name, bond_info['mode'])

        try:
            bond_dev = self.dev_dict.get_dev(bond_type, bond_name)

            update_method_dict = {'ip4': update_ip4,
                                  'slave': update_slave,
                                  'mode': update_mode}

            for update_type in bond_info:
                update_method_dict.get(update_type, lambda: True)()

            self.hw_up_dev(bond_name)

        except Exception as e:
            return False, repr(e)

        self.save()
        return True, ''

    def refresh_real_eth(self):
        eth_type = 'Eth'
        store_eths = set(self.dev_dict.dev_list('Eth'))
        real_eths = set(self.hw_eth_list())

        remove_eths = store_eths - real_eths
        add_eths = real_eths - store_eths
        update_eths = real_eths & store_eths

        # delete the eth that not exist in hardware
        for eth_name in remove_eths:
            # nmclitool.nmcli_del_dev(eth_name)
            self.dev_dict.del_dev(eth_type, eth_name)
            self.hw_del_dev(eth_type, eth_name)

        # add the eth that not exist in store
        for eth_name in add_eths:
            eth_hw_info = self.hw_dev_info(eth_name)
            store_info = self.eth_convert_info(eth_hw_info)
            self.dev_dict.add_dev(eth_type, eth_name, **store_info)

            master_name = store_info['master']
            if master_name:
                try:
                    master_hw_info = self.hw_dev_info(master_name)
                    if master_hw_info['connection']['type'] == 'bond':
                        master_type = 'Bond'
                    elif master_hw_info['connection']['type'] == 'bridge':
                        master_type = 'Bridge'
                    self.dev_dict.mod_slave('add', master_type, master_name, eth_type, eth_name)


                except:
                    self.hw_del_dev(eth_type, eth_name)
                    self.hw_add_dev(eth_type, eth_name)
            # self.hw_del_dev('Eth', eth_name)
            # self.hw_add_dev('Eth', eth_name)


        # update the eth that exist in hardware and store
        for eth_name in update_eths:
            # update the info from nmcli
            eth_dev = self.dev_dict.get_dev(eth_type, eth_name)
            eth_hw_info = self.hw_dev_info(eth_name)
            # if eth_hw_info['GENERAL']['CON-PATH'] == '':
            #     self.hw_add_dev(eth_type, eth_name)
            store_info = self.eth_convert_info(eth_hw_info)

            eth_master = eth_dev.get('master')
            if eth_master != store_info['master']:
                if eth_master != '':
                    store_info['master'] = eth_master
                    self.hw_make_slave('Bond', eth_master, eth_type, eth_name)

            self.dev_dict.mod_dev(eth_type, eth_name, **store_info)

    def refresh_real_bond(self):
        bond_type = 'Bond'
        store_bonds = set(self.dev_dict.dev_list('Bond'))
        real_bonds = set(self.hw_bond_list())

        # remove_bonds = store_bonds - real_bonds
        add_bonds = store_bonds - real_bonds
        out_bonds = real_bonds - store_bonds
        update_bonds = real_bonds & store_bonds

        for bond_name in add_bonds:
            bond_dev = self.dev_dict.get_dev(bond_type, bond_name)
            self.hw_add_dev(bond_type, bond_name, bond_dev.get('mode'))
            self.hw_add_ip4(bond_name, bond_dev.get('ip4'))
            self.hw_up_dev(bond_name)

        for bond_name in out_bonds:
            bond_hw_info = self.hw_dev_info(bond_name)
            store_info = self.bond_convert_info(bond_hw_info)
            self.dev_dict.add_dev(bond_type, store_info['device'], **store_info)

        for bond_name in update_bonds:
            pass

    # TODO update refresh_real_br
    # def refresh_real_br(self):
    #     store_brs = set(self.dev_dict.dev_list('Bridge'))
    #     real_brs = set(nmclitool.br_list())
    #
    #     remove_brs = real_brs - store_brs
    #     add_brs = store_brs - real_brs
    #     update_brs = store_brs & real_brs
    #
    #     # delete the br that not exist in store
    #     for br_name in remove_brs:
    #         nmclitool.nmcli_del_dev(br_name)
    #
    #     # add the br that not exist in hardware
    #     for br_name in add_brs:
    #         br_dev = self.dev_dict.get_dev('Bridge', br_name)
    #         # nmclitool_info = self.br_store_to_nmclitool(br_dev)
    #         nmclitool_info = self.convert_nmcli_info(br_dev)
    #
    #         # nmclitool.nmcli_add_br(br_name)
    #         self.hw_add_dev('Bridge', br_name)
    #         nmclitool.nmcli_add_ip4(br_name, nmclitool_info['ip4'])
    #
    #         br_slave_list = br_dev.get('slave')
    #         for slave_name in br_slave_list:
    #             nmclitool.nmcli_up_dev(slave_name)
    #
    #     # update the br that exist both of hardware and store
    #     for br_name in update_brs:
    #         br_dev = self.dev_dict.get_dev()
    #         nmcli_info = nmclitool.nmcli_dev_info(br_name)
    #
    #         if self.compare_ip4_nmcli_store(nmcli_info, br_dev):
    #             pass

    def add_slave(self, master_type, master_name, slave_type, slave_name):
        slave_dev = self.dev_dict.get_dev(slave_type, slave_name)
        slave_master_store = slave_dev.get('master')
        self.dev_dict.mod_dev(slave_type, slave_name, master=master_name)
        self.dev_dict.mod_slave('add', master_type, master_name, slave_type, slave_name)

        # if slave_master_store == '' or slave_master_store != master_name:
        #     if slave_type == 'Eth' and slave_master_store != master_name:
        if slave_master_store != master_name:
            if slave_type == 'Eth':
                # Eth can't change from bridge-slave to bond-slave
                self.hw_del_dev(slave_type, slave_name)
                self.hw_add_dev(slave_type, slave_name)

            self.hw_make_slave(master_type, master_name, slave_type, slave_name)
            self.hw_up_dev(slave_name)


    def del_slave(self, master_type, master_name, slave_type, slave_name):
        slave_dev = self.dev_dict.get_dev(slave_type, slave_name)
        slave_master_store =slave_dev.get('master')

        if slave_master_store != master_name:
            raise NetStoreError, 'master of slave not match'
            # return False

        self.hw_del_dev(slave_type, slave_name)
        self.hw_add_dev(slave_type, slave_name)
        self.dev_dict.mod_dev(slave_type, slave_name, master='')
        self.dev_dict.mod_slave('del', master_type, master_name, slave_type, slave_name)

    # def init_info(self, dev_type, dev_info):
    #     tmp_dev_info = copy.deepcopy(dev_info)
    #     dev_dict = {'Eth': Eth,
    #                 'Bond': Bond,
    #                 'Bridge': Bridge}
    #
    #     init_dev_info = dev_dict[dev_type].property_dict
    #     for property_ in init_dev_info:
    #         if init_dev_info[property_] and not tmp_dev_info.get(property_, None):
    #             tmp_dev_info[property_] = init_dev_info[property_]
    #
    #     return tmp_dev_info

    @staticmethod
    def hw_eth_list():
        return nmclitool.eth_list()

    @staticmethod
    def hw_bond_list():
        return nmclitool.bond_list()

    @staticmethod
    def hw_del_dev(dev_type, dev_name):
        nmclitool.nmcli_del_dev(dev_name)

    @staticmethod
    def hw_add_dev(dev_type, *args, **kwargs):
        switch = {'Eth': nmclitool.nmcli_add_eth,
                  'Bond': nmclitool.nmcli_add_bond,
                  'Bridge': nmclitool.nmcli_add_br}

        switch[dev_type](*args, **kwargs)

    @staticmethod
    def hw_dev_info(dev_name):
        return nmclitool.nmcli_dev_info(dev_name)

    @staticmethod
    def hw_mod_bond_mode(bond_name, mode):
        return nmclitool.nmcli_mod_bond_mode(bond_name, mode)

    @staticmethod
    def hw_add_ip4(dev_name, init_ip4):
        hw_ip4 = []
        for ip4 in init_ip4:
            cidr_address = ip4_netmask_2_cidr(ip4)
            if not cidr_address:
                continue
            if 'gateway' in ip4 and not check_ip4(ip4['gateway']):
                continue

            ip4.pop('netmask')
            ip4['address'] = cidr_address
            hw_ip4.append(ip4)

        try:
            if hw_ip4:
                nmclitool.nmcli_add_ip4(dev_name, hw_ip4)
        except Exception as e:
            nmclitool.nmcli_flush_ip4(dev_name)
            raise e

    @staticmethod
    def hw_up_dev(dev_name):
        nmclitool.nmcli_up_dev(dev_name)

    def hw_make_slave(self, master_type, master_name, slave_type, slave_name):
        try:
            nmclitool.nmcli_make_slave(master_name, slave_name, master_type)
        except Exception as e:
            self.hw_del_dev(slave_type, slave_name)
            self.hw_add_dev(slave_type, slave_name)
            raise e

    @staticmethod
    def compare_ip4_nmcli_store(nmcli_info, br_dev):
        nmcli_ip4 = nmcli_info['IP4']
        dev_ip4 = br_dev.get('ip4')

        # TODO compare the ip between nmcli_info and br_dev

    @staticmethod
    def br_store_to_nmclitool(br_dev):
        nmclitool_info = {}
        nmclitool_info['ip4'] = []
        for ip4_info in br_dev.get('ip4'):
            tmp_ip4_dict = {}
            tmp_ip4_dict['address'] = ip4_info['address'] + '/' + str(netmask_2_cidr(ip4_info['netmask']))
            nmclitool_info['ip4'].append(tmp_ip4_dict)

        return nmclitool_info

    # @staticmethod
    # def bond_store_translate(bond_info):
    #     # rebuild the bond_info to the format of bond's propertys
    #     store_info = {}
    #     store_info['ip4'] = bond_info['ip4']['address'] + '/' + str(netmask_2_cidr(bond_info['ip4']['netmask']))
    #     store_info['slave_list'] = bond_info['devs']
    #     return store_info
    #

    @staticmethod
    def eth_convert_info(eth_hw_info):
        store_info = {'master': eth_hw_info.get('connection', {}).get('master',''),
                      'mac': eth_hw_info.get('GENERAL', {}).get('HWADDR', ''),
                      'abstract': {}}
        store_info['abstract']['status'] = eth_hw_info.get('WIRED-PROPERTIES', {}).get('CARRIER', '')

        return store_info

    @staticmethod
    def bond_convert_info(hw_info):
        device = ''
        ip4 = []
        # ip6 = []
        mode = ''
        master = ''

        master = hw_info['connection']['master']

        device = hw_info['GENERAL']['NAME']

        if 'IP4' in hw_info:
            for i, ip4_cidr in hw_info['IP4']['ADDRESS'].items():
                if not ip4_cidr:
                    continue
                ip4.append(ip4_cidr_2_netmask(ip4_cidr))
            gateway = hw_info['IP4']['GATEWAY']
            if gateway and check_ip4(gateway):
                ip4[0]['gateway'] = gateway

        mode_options = hw_info['bond']['options']
        for mode_option in mode_options.split(','):
            option, value = mode_option.split('=')
            if option == 'mode':
                tmp_mode = bond_mode_convert(value)
                if tmp_mode:
                    mode = tmp_mode
                    break

        store_info = {'device': device,
                      'ip4': ip4,
                      # 'ip6': '',
                      'mode': mode,
                      'master': master}

        return store_info

    def convert_nmcli_info(self, store_info):
        # translate BaseDev or store_info to nmcli_info
        if isinstance(store_info, BaseDev):
            store_info = store_info.to_dict()

        nmcli_switch = {
            'ip4': self.ip4_store_nmcli}
        nmcli_info_dict = {}

        for property_, value in store_info.items():
            property_method = nmcli_switch.get(property_, lambda x: x)
            nmcli_info_dict[property_] = property_method(value)

        return nmcli_info_dict


    @staticmethod
    def ip4_store_nmcli(store_ip4_list):
        # translate ip4 from store format to nmcli format
        if not isinstance(store_ip4_list, list) and isinstance(store_ip4_list, dict):
            # {'address': xx,,,} ==> [{'address': xx,,,},]
            store_ip4_list = [store_ip4_list,]
        if not isinstance(store_ip4_list, list):
            return None

        nmcli_ip4 = []
        for store_ip4 in store_ip4_list:
            tmp_ip4 = {'address': store_ip4['address'] + '/' + str(netmask_2_cidr(store_ip4['netmask']))}
            nmcli_ip4.append(tmp_ip4)

        return nmcli_ip4


    # @staticmethod
    # def bond_nmcli_translate(bond_info):
    #     # rebuild the bond_info to the format of nmclitool
    #     nmcli_info = {}
    #     nmcli_info['ip4'] = {}
    #     nmcli_info['ip4']['address'] = bond_info['ip4']['address'] + '/' + str(netmask_2_cidr(bond_info['ip4']['netmask']))
    #     nmcli_info['mode'] = bond_info['mode']
    #     return nmcli_info

    # @staticmethod
    # def bond_interface_translate(bond_dev):
    #     tmp_bond_info = {}
    #     tmp_bond_info['devs'] = bond_dev.get('slave')
    #     ip4, cidr = bond_dev.get('ip4').split('/')
    #     tmp_bond_info['ip4'] = {}
    #     tmp_bond_info['ip4']['address'] = ip4
    #     tmp_bond_info['ip4']['netmask'] = cidr_2_netmask(int(cidr))
    #     tmp_bond_info['master'] = bond_dev.get('master')
    #     return tmp_bond_info

    @staticmethod
    def eth_nmcli_to_store(nmcli_info):
        store_info = {}
        store_info['master'] = nmcli_info.get('connection', {}).get('master', '')
        store_info['mac'] = nmcli_info.get('GENERAL', {}).get('HWADDR', '')
        store_info['abstract'] = {}
        store_info['abstract']['status'] = nmcli_info.get('WIRED-PROPERTIES', {}).get('CARRIER', '')
        return store_info

    # @staticmethod
    # def eth_store_to_nmcli(eth_info):
    #     nmcli_info = {}
    #     nmcli_info['master'] = eth_info['master']
    #     nmcli_info['abstract'] = eth_info['abstract']
    #     nmcli_info['status'] = eth_info['status']
    #     return nmcli_info

    # @staticmethod
    # def eth_interface_translate(eth_dev):
    #     tmp_eth_info = {}
    #     tmp_eth_info['master'] = eth_dev.get('master')
    #     tmp_eth_info['abstract'] = eth_dev.get('abstract')
    #     tmp_eth_info['status'] = eth_dev.get('status')
    #     return tmp_eth_info

    # @staticmethod
    # def check_ip4(ip4):
    #     try:
    #         ip4, cidr = ip4.split('/')
    #         # return True if pass eth check_ip4 and check_cidr
    #         return check_ip4(ip4) and check_cidr(cidr)
    #     except Exception as e:
    #         return False

    # def refresh_slave_list(self):
    #     for master_type in self.dev_dict.master_devs:
    #         for master_name, master_dev in self.dev_dict.get(master_type).items():
    #             slave_list = []
    #             for slave_type in self.dev_dict.slave_devs:
    #                 for slave_name, slave_dev in self.dev_dict.get(slave_type).items():
    #                     if slave_dev.get('master') == master_name and master_name != '':
    #                         slave_list.append(slave_name)
    #             master_dev.set('slave', slave_list)
    #             self.dev_dict.add_dev(master_type, master_name, master_dev)

    # def clear_type(self, dev_type):
    #     for dev_name in self.dev_dict.get(dev_type):
    #         self.dev_dict.del_dev(dev_type, dev_name)

        # for eth_name in real_eth_list:
        #     if nmclitool.nmcli_check_dev(eth_name) is False:
        #         nmclitool.nmcli_del_dev(eth_name)
        #         nmclitool.nmcli_add_eth(eth_name)
        #         nmclitool.nmcli_up_dev(eth_name)
        #     eth_info = nmclitool.nmcli_dev_info(eth_name)
        #     # {'master', 'mac'}
        #     eth_master = dict_spider(eth_info, 'connection', 'master')
        #     eth_mac = dict_spider(eth_info, 'GENERAL', 'HWADDR')
        #     eth_status = dict_spider(eth_info, 'WIRED-PROPERTIES', 'CARRIER')
        #     self.add_dev('Eth', eth_name, master=eth_master, mac=eth_mac, status=eth_status)

    # def refresh_real_eth1(self): # 0.7
    #     self.clear_type('Eth')
    #     eth_list = nmclitool.eth_list() # 0.05
    #     for eth_name in eth_list: # 0.5
    #         if nmclitool.nmcli_check_dev(eth_name) is False:
    #             nmclitool.nmcli_del_dev(eth_name)
    #             nmclitool.nmcli_add_eth(eth_name)
    #             nmclitool.nmcli_up_dev(eth_name)
    #         eth_info = nmclitool.nmcli_dev_info(eth_name) # 0.4
    #         # {'master', 'mac'}
    #         eth_master = dict_spider(eth_info, 'connection', 'master')
    #         eth_master = ''
    #         eth_mac = ''
    #         eth_status = ''
    #         self.add_dev('Eth', eth_name, master=eth_master, mac=eth_mac, status=eth_status)

def ip4_netmask_2_cidr(init_ip):
    # convert and {'address': '1.1.1.1', 'netmask': '255.255.0.0'} into '1.1.1.1/16'
    if not isinstance(init_ip, dict) or 'netmask' not in init_ip or 'address' not in init_ip:
        return None

    address = init_ip['address']
    netmask = init_ip['netmask']
    if not check_ip4(address) or not check_ip4(netmask):
        return None

    return address + '/' + str(netmask_2_cidr(netmask))

def ip4_cidr_2_netmask(init_ip):
    # convert '1.1.1.1/16' into {'address': '1.1.1.1', 'netmask': '255.255.0.0'}
    if not isinstance(init_ip, str):
        return None

    address, cidr = init_ip.split('/')
    if not check_ip4(address) or not check_cidr(cidr):
        return None

    return {'address': address,
             'netmask': cidr_2_netmask(cidr)}

# def ip4_convert(init_ip):
#     # convert between '1.1.1.1/16' and {'address': '1.1.1.1', 'netmask': '255.255.0.0'}
#     if isinstance(init_ip, dict) and 'netmask' in init_ip and 'address' in init_ip:
#         address = init_ip['address']
#         netmask = init_ip['netmask']
#         if not check_ip4(address) or not check_ip4(netmask):
#             return None
#
#         return address + '/' + str(netmask_2_cidr(netmask))
#
#     elif isinstance(init_ip, str):
#         address, cidr = init_ip.split('/')
#         if not check_ip4(address) or not check_cidr(cidr):
#             return None
#
#         return {'address': address,
#                  'netmask': cidr_2_netmask(cidr)}
#
#     else:
#         return None


def check_ip4(ip4):
    try:
        ip = ip4.split('.')
        if len(ip) != 4:
            return False
        for ip_part in ip:
            if ip_part.isdigit() and 0 <= int(ip_part) <= 255:
                return True
            else:
                return False
    except:
        return False

def bond_mode_convert(bond_mode_info):
    convert_dict = {'balance-rr': '0',
                    'active-backup': '1',
                    'balance-xor': '2',
                    'broadcast': '3',
                    '802.3ad': '4',
                    'balance-tlb': '5',
                    'balance-alb': '6',
                    '0': '0',
                    '1': '1',
                    '2': '2',
                    '3': '3',
                    '4': '4',
                    '5': '5',
                    '6': '6'}

    return convert_dict.get(bond_mode_info, None)

def check_cidr(cidr):
    try:
        if 0 <= int(cidr) <= 24:
            return True
        else:
            return False
    except:
        return False


def netmask_2_cidr(netmask):
    return sum([bin(int(i)).count('1') for i in netmask.split('.')])


def cidr_2_netmask(cidr):
    cidr = int(cidr)
    return '.'.join([str((0xffffffff << (32 - cidr) >> i) & 0xff) for i in [24, 16, 8, 0]])

# def dict_spider(init_dict, *keys):
#     # if key not in init_dict, return ''
#     if keys[0] in init_dict.keys():
#         if len(keys) == 1:
#             return init_dict[keys[0]]
#         else:
#             return dict_spider(init_dict[keys[0]], *keys[1:])
#     else:
#         return ''


