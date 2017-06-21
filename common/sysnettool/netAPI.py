# -*- coding: utf-8 -*-
'''
eth = {'device': '',
       'master': '',
       'mac': '00:00:00:00:00:00',
       'abstract': {'status': 'down/up'}}
bond = {'device': '',
        'mode': '1',
        'slave': set(),
        'master': '',
        'ip4': [{'address': '0.0.0.0',
                 'netmask': '255.255.255.255',
                 'gateway': '0.0.0.0',
                 'dns': ['223.5.5.5']}],
        'ip6': [{'address': '::',
                 'prefixlen': '128',
                 'gateway': '::',
                 'dns': ['::']}]}
bridge = {'device': '',
          'slave': [],
          'ip4': [{'address': '0.0.0.0',
                   'netmask': '255.255.255.255',
                   'gateway': '0.0.0.0',
                   'dns': ['223.5.5.5']}],
          'ip6': [{'address': '::',
                   'prefixlen': '128',
                   'gateway': '::',
                   'dns': ['::']}]}
gateway = {'ip4': '0.0.0.0',
           'ip6': '::'}
'''




def eths_info(eths=None):
    '''
    return the eth information.
    :param eth_name:
    'eth0_name' or ['eth0', 'eth1']
    :return: 
    {'eth1': {'mac': 'xx:xx:xx:xx:xx:xx',
              'abstract': {'status': 'on/off',
                           'xxx': 'xxx'}},
     'eth2': {'mac': 'xx:xx:xx:xx:xx:xx',
              'abstract': {'status': 'on/off',
                           'xxx': 'xxx'}}
     }
    if the 'eths' is not a string or a list, return (-1, 'eth name error'). 
    if the 'eths' not exist, return (-2, 'eth not exist').
    '''

def mod_eth(eths):
    '''
    change the eth status
    :param eths:
    {'eth1': {'abstract': {'status': 'on/off',
                           'xxx':'xxx'},
     'eth2': {'abstract': {'status': 'on/off',
                           'xxx':'xxx'}
     }
    :return: 
    (0, 'Success')
    (-1, 'eth parament error')
    (-2, 'the error reason')
    '''

def bonds_info(bonds=None):
    '''
    return eth bond information
    :param bonds:
    'bond0_name' or ['bond0', 'bond1']
    :return:
    {'bond0': {'mode': '0/1/2/.../6',
               'slave': [],
               'ip4': {'address': '10.10.10.10',
                       'netmask': '16'},
               'gateway4': '10.11.1.10',
               'dns4': 'xx:xx:xx:xx',
               'ip6': 'xxxx:xx:xxxx/xx',
               'gateway6': 'xxxx::xx:xxxx',
               'dns6': 'xx:xx:xx:xx',
               'master': ''}
     'bond1': {'mode': '0/1/2/.../6',
               'slave': [],
               'ip4': {'address': '10.10.10.10',
                       'netmask': '16'},
               'gateway4': '10.11.1.10',
               'dns4': 'xx:xx:xx:xx',
               'ip6': 'xxxx:xx:xxxx/xx',
               'gateway6': 'xxxx::xx:xxxx',
               'dns6': 'xx:xx:xx:xx',
               'master': ''}
     }
    if the 'bonds' is not a string or a list, return (-1, 'bond name error'). 
    if the 'bonds' not exist, return (-2, 'bond not exist').
    '''

def add_bond(bonds):
    '''
    add the bond
    :param bonds:
    {'bond1': {'mode': '0/1/2/.../6', # default '1'
               'slave': [], # default []
               'ip4': '10.10.10.12/24', # default ''
               'gateway4': '10.11.1.10', # default ''
               'dns4': 'xx:xx:xx:xx', # default ''
               'ip6': 'xxxx:xx:xxxx/xx', # default ''
               'gateway6': 'xxxx::xx:xxxx', # default ''
               'dns6': 'xx:xx:xx:xx', # default ''
               'master': '' # default ''
               }
    'bond2': {'mode': '0/1/2/.../6', # default '1'
              'slave': [], # default []
              'ip4': '10.10.10.12/24', # default ''
              'gateway4': '10.11.1.10', # default ''
              'dns4': 'xx:xx:xx:xx', # default ''
              'ip6': 'xxxx:xx:xxxx/xx', # default ''
              'gateway6': 'xxxx::xx:xxxx', # default ''
              'dns6': 'xx:xx:xx:xx', # default ''
              'master': '' # default ''
               }
     }
    :return:
    (0, 'Success')
    (-1, 'bonds parament error')
    (-2, 'the error reason')
    '''

def mod_bond(bonds):
    '''
    modify the bond
    :param bonds:
    {'bond1': {'mode': '0/1/2/.../6', # default '1'
               'slave': [], # default []
               'ip4': '10.10.10.12/24', # default ''
               'gateway4': '10.11.1.10', # default ''
               'dns4': 'xx:xx:xx:xx', # default ''
               'ip6': 'xxxx:xx:xxxx/xx', # default ''
               'gateway6': 'xxxx::xx:xxxx', # default ''
               'dns6': 'xx:xx:xx:xx', # default ''
               'master': '' # default ''
               }
    'bond2': {'mode': '0/1/2/.../6', # default '1'
              'slave': [], # default []
              'ip4': '10.10.10.12/24', # default ''
              'gateway4': '10.11.1.10', # default ''
              'dns4': 'xx:xx:xx:xx', # default ''
              'ip6': 'xxxx:xx:xxxx/xx', # default ''
              'gateway6': 'xxxx::xx:xxxx', # default ''
              'dns6': 'xx:xx:xx:xx', # default ''
              'master': '' # default ''
               }
     }
    :return:
    (0, 'Success')
    (-1, 'bonds parament error')
    (-2, 'bonds error reason')
    '''

def del_bond(bonds):
    '''
    del the bond
    :param bonds:
    'bond0_name' or ['bond0', 'bond1']
    :return:
    (0, 'Success')
    (-1, 'bonds not exist')
    (-2, 'the error reason')
    '''

def br_info(brs=None):
    '''
    return eth bridge information
    :param brs:
    'br0_name' or ['br0', 'br1']
    :return:
    {'br0': {'slave': [],
             'ip4': {'address': '10.10.10.10',
                     'netmask': '16'},
             'gateway4': '10.11.1.10',
             'dns4': 'xx:xx:xx:xx',
             'ip6': {'address': 'xxxx:xx:xxxx',
                     'netmask': 'xx'},
             'gateway6': 'xxxx::xx:xxxx',
             'dns6': 'xx:xx:xx:xx'}
     'br1': {'slave': [],
             'ip4': '10.10.10.12/24',
             'gateway4': '10.11.1.10',
             'dns4': 'xx:xx:xx:xx',
             'ip6': 'xxxx:xx:xxxx/xx',
             'gateway6': 'xxxx::xx:xxxx',
             'dns6': 'xx:xx:xx:xx'}
     }
    if the 'brs' is not a string or a list, return (-1, 'bridge name error'). 
    if the 'brs' not exist, return (-2, 'bridge not exist').
    '''

def add_br(brs):
    '''
    add the bridge
    :param brs:
    {'br0': {'slave': [],
             'ip4': {'address': '10.10.10.10',
                     'netmask': '16'},
             'gateway4': '10.11.1.10',
             'dns4': 'xx:xx:xx:xx',
             'ip6': {'address': 'xxxx:xx:xxxx',
                     'netmask': 'xx'},
             'gateway6': 'xxxx::xx:xxxx',
             'dns6': 'xx:xx:xx:xx'}
     'br1': {'slave': [],
             'ip4': {'address': '10.10.10.10',
                     'netmask': '16'},
             'gateway4': '10.11.1.10',
             'dns4': 'xx:xx:xx:xx',
             'ip6': {'address': 'xxxx:xx:xxxx',
                     'netmask': 'xx'},
             'gateway6': 'xxxx::xx:xxxx',
             'dns6': 'xx:xx:xx:xx'}
     }
    :return:
    (0, 'Success')
    (-1, 'brigdes parament error')
    (-2, 'the error reason')
    '''

def mod_bridge(brs):
    '''
    modify the bridge
    :param brs:
    {'br1': {'slave': [], # default []
             'ip4': '10.10.10.12/24', # default ''
             'gateway4': '10.11.1.10', # default ''
             'dns4': 'xx:xx:xx:xx', # default ''
             'ip6': 'xxxx:xx:xxxx/xx', # default ''
             'gateway6': 'xxxx::xx:xxxx', # default ''
             'dns6': 'xx:xx:xx:xx', # default ''
             }
    'br2': {'slave': [], # default []
            'ip4': '10.10.10.12/24', # default ''
            'gateway4': '10.11.1.10', # default ''
            'dns4': 'xx:xx:xx:xx', # default ''
            'ip6': 'xxxx:xx:xxxx/xx', # default ''
            'gateway6': 'xxxx::xx:xxxx', # default ''
            'dns6': 'xx:xx:xx:xx', # default ''
            }
     }
    :return:
    (0, 'Success')
    (-1, 'bridges parament error')
    (-2, 'bridges error reason')
    '''

def del_br(brs):
    '''
    del the bridge
    :param bonds:
    'bond0_name' or ['bond0', 'bond1']
    :return:
    (0, 'Success')
    (-1, 'bridges not exist')
    (-2, 'the error reason')
    '''




















