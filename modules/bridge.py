# -*- coding: utf-8 -*-

import logging
import urwid
import common.dialog as dialog
import common.modulehelper as modulehelper
import common.networkhelper as networkhelper
import common.urwidwidgetwrapper as widget
import time
import copy

log = logging.getLogger('bridge setup')

blank = urwid.Divider(" ")

class Bridge(urwid.WidgetWrap):
    def __init__(self, parent, language=modulehelper.LanguageType.CHINESE):
        self.parent = parent
        self.screen = None
        self.original_screen = None
        self.name = 'BRIDGE'
        self.visible = True
        self.edit_open = False
        self.language = language

        self.bridge_info = self.bridge_info_load()
        self.bond_info = self.bond_info_load()

        ##draw header_content
        # radiobuton group under the button list but on the bridge abstract
        self.bridge_list = sorted(self.bridge_info.keys())
        if len(self.bridge_list) > 0:
            self.activebridge_name = self.bridge_list[0]
        else:
            self.activebridge_name = 'bridge'
        # eth info in active bridge
        self.active_bridge_bond_inuse = []
        self.active_bridge_bond_usable = []
        self.bridge_bond_inuse_tmp = []
        self.bridge_bond_usable_tmp = []
        self.active_bridge_bond_inuse, self.active_bridge_bond_usable = self.get_bridge_bond_info(self.activebridge_name)

        # create radiobutton group and set
        self.bridge_choices = widget.ChoicesGroup(self.bridge_list,
                                                  default_value=self.activebridge_name,
                                                  fn=self.radio_select_iface)
        self.bridge_info_abstract_listbox = self.get_abstract_listbox(self.active_bridge_bond_inuse)
        #create header_content
        self.header_content = [self.bridge_choices, urwid.Divider(" "),
                               self.bridge_info_abstract_listbox]

        ## draw_fields with default info
        self.fields = ['BRIDGE_NAME', 'IP_ADDRESS', 'NET_MASK']
        self.defaults = \
            {
                "BRIDGE_NAME" :{"label": "NAME",
                              "tooltip": "Change your bridge name here",
                              "value": self.activebridge_name},
                "IP_ADDRESS": {"label": "ADDRESS",
                               "tooltip": "Manual configure IP address (example 192.168.1.2)",
                               "value": self.bridge_info[self.activebridge_name]['ipv4']['address'] if len(self.bridge_list) > 0 else ""},
                "NET_MASK": {"label": "NETMASK",
                             "tooltip": "Manaual configure netmask (example 255.255.0.0)",
                             "value": self.bridge_info[self.activebridge_name]['ipv4']['netmask'] if len(self.bridge_list) > 0 else ""}
            }



    def bridge_info_load(self):
        # edit there to get bridge info
        bridge_info = networkhelper.get_bridge_info()
        if bridge_info is {}:
            body_msg = "load bridge info error, bridge info is error or bond info is empty"
            msg = 'bridge info is empty'
            self.parent.footer.original_widget.set_text(msg)
            log.warning(body_msg)
            return {}
        else:
            return bridge_info

    def bond_info_load(self):
        # edit there to get bond info
        bond_info = networkhelper.get_bond_info()
        if bond_info is {}:
            body_msg = "load bond info error, bond info is error or bond info is empty"
            msg = 'bond info is empty'
            self.parent.footer.original_widget.set_text(msg)
            log.warning(body_msg)
            return {}
        else:
            return bond_info



    # return TEXT widget contain bond info
    def get_abstract_listbox(self, active_bridge_bond_inuse):
        if len(active_bridge_bond_inuse) == 0:
            return blank
        text_bond = urwid.AttrWrap(urwid.Text(['. ', active_bridge_bond_inuse[0]]), 'text selected good')
        return text_bond


    def add_bridge(self, button):
        msg = "create new bridge"
        edit_field = widget.TextField(
            None, 'Bridge name', 13,
            tooltip='Manual add bridge, please add bridge name with digit and alpha',
            default_value="",
            tool_bar = self.parent.footer
        )
        dialog.display_dialog(self, edit_field, msg, body_type='edit',
                              mod_callback=self.dialog_callback_add_bridge)

    def dialog_callback_add_bridge(self, bridge_name):
        # check name
        format_msg = 'unusable bridge'
        if bridge_name == '':
            self.parent.footer.original_widget.set_text("%s: bridge name can not be empty"
                                                        % format_msg)
            return False
        for c in bridge_name:
            if c.isalpha() is False and c.isdigit() is False:
                self.parent.footer.original_widget.set_text("%s: bridge name can only contain digits and alpha"
                                                            % format_msg)
                return False
        if bridge_name in self.bridge_info.keys():
            self.parent.footer.original_widget.set_text("%s: bridge has existed"
                                                        % format_msg)
            return False

        # update bridge info
        bridge_info_tmp = copy.deepcopy(self.bridge_info)
        bridge_dic = {bridge_name:{
            'devs': [],
            'ipv4': {'address': "", 'netmask': ""}
        }}
        bridge_info_tmp = dict(bridge_info_tmp, **bridge_dic)
        response = networkhelper.update_bridge_info(bridge_info_tmp)
        time.sleep(0.5)

        if response[0] is True:
            # reload info
            self.refresh_details()
            log.info("create new bridge: %s" % bridge_name)
            self.parent.footer.original_widget.set_text("update success")
            self.parent.refresh_screen()
            return True
        else:
            msg = 'add fail：update info error'
            log.error("add %s error: %s" % (bridge_name, response[1]))
            self.parent.footer.original_widget.set_text(msg)
            return False
    def del_bridge_dialog(self, button):
        msg = "Delete bridge: %s ?"%self.activebridge_name
        dialog.display_dialog(self, urwid.Text(msg), "Confirm your operation",
                              body_type='bool', mod_callback=self.del_bridge)

    def del_bridge(self, confirm):
        bridge_name = self.activebridge_name
        # update bond info
        bridge_info_tmp = copy.deepcopy(self.bridge_info)
        del bridge_info_tmp[bridge_name]
        bond_info_tmp = copy.deepcopy(self.bond_info)
        for bond in self.active_bridge_bond_inuse:
            bond_info_tmp[bond]['master'] = ""
        response_bridge = networkhelper.update_bridge_info(bridge_info_tmp)
        response_bond = networkhelper.update_bond_info(bond_info_tmp)
        time.sleep(0.5)

        if response_bridge[0] is True and response_bond[0] is True:
            # reload info
            self.refresh_details()
            self.back_button.keypress((10, ), 'enter')
            self.defaults["IP_ADDRESS"]["value"] = self.bridge_info[self.activebridge_name]['ipv4']['address']
            self.defaults["NET_MASK"]["value"] = self.bridge_info[self.activebridge_name]['ipv4']['netmask']
            self.defaults["BOND_NAME"]["value"] = self.activebridge_name
            self.parent.footer.original_widget.set_text("update success")
            self.parent.refresh_screen()
            log.info("del bridge: %s success"%bridge_name)
            return True
        else:
            msg = 'update fail: error update bridge info'
            self.parent.footer.original_widget.set_text(msg)
            log.error("del bridge: %s fail: %s"%(bridge_name, response_bridge[1] + '; ' + response_bond[1]))
            return False


    def radio_select_iface(self, radiobutton, state, bridge_name):
        if state is True:
            self.activebridge_name = bridge_name
            self.active_bridge_bond_inuse, self.active_bridge_bond_usable = self.get_bridge_bond_info(bridge_name)
            self.bridge_bond_usable_tmp = []
            self.bridge_bond_inuse_tmp = []
            self.listbox_content[2] = self.get_abstract_listbox(self.active_bridge_bond_inuse)
            self.defaults["IP_ADDRESS"]["value"] = self.bridge_info[bridge_name]['ipv4']['address']
            self.defaults["NET_MASK"]["value"] = self.bridge_info[bridge_name]['ipv4']['netmask']
            self.defaults["BRIDGE_NAME"]["value"] = self.activebridge_name


    # get inuse and usable eth for one bond
    def get_bridge_bond_info(self, bridge_name):
        inuse = []
        usable = []

        for bond, bond_info in self.bond_info.items():
            if bond_info.get('master') == bridge_name:
                inuse.append(bond)

            elif bond_info.get('master') == "" :
                usable.append(bond)
        inuse = sorted(inuse)
        usable = sorted(usable)
        return inuse, usable


    # this two functions only use to remove or add bond in display
    # but not remove or add bond in fact
    def remove_bond(self, button):
        if len(self.bridge_bond_inuse_tmp) == 0 and len(self.bridge_bond_usable_tmp) == 0:
            self.bridge_bond_inuse_tmp = copy.deepcopy(self.active_bridge_bond_inuse)
            self.bridge_bond_usable_tmp = copy.deepcopy(self.active_bridge_bond_usable)

        button_label = button.get_label()
        self.bridge_bond_inuse_tmp.remove(button_label)
        self.bridge_bond_usable_tmp.append(button_label)
        self.bridge_bond_usable_tmp = sorted(self.bridge_bond_usable_tmp)
        # display new dialog
        eths_bond_dialog = widget.ColContainTwoListBox('Bond inuse', 'Bond usable',
                                                       self.bridge_bond_inuse_tmp,
                                                       self.bridge_bond_usable_tmp,
                                                       self.remove_bond, self.add_bond,
                                                       button.get_label())
        eths_bond_dialog_ltb = urwid.ListBox(urwid.SimpleListWalker([eths_bond_dialog]))
        eths_bond_dialog_lnb = urwid.LineBox(eths_bond_dialog_ltb, "Bridge Device")
        self.listbox_content[3] = urwid.BoxAdapter(eths_bond_dialog_lnb, self.bond_for_bridge_height + 7)
        self.parent.refresh_screen()

    def add_bond(self, button):
        if len(self.bridge_bond_inuse_tmp) == 0 and len(self.bridge_bond_usable_tmp) == 0:
            self.bridge_bond_inuse_tmp = copy.deepcopy(self.active_bridge_bond_inuse)
            self.bridge_bond_usable_tmp = copy.deepcopy(self.active_bridge_bond_usable)

        button_label = button.get_label()
        if len(self.bridge_bond_inuse_tmp) > 0:
            self.bridge_bond_usable_tmp.append(self.bridge_bond_inuse_tmp[0])
        self.bridge_bond_usable_tmp.remove(button_label)
        self.bridge_bond_inuse_tmp=[button_label]
        self.bridge_bond_usable_tmp = sorted(self.bridge_bond_usable_tmp)

        # display new dialog
        eths_bond_dialog = widget.ColContainTwoListBox('Bond inuse', 'Bond usable',
                                                       self.bridge_bond_inuse_tmp,
                                                       self.bridge_bond_usable_tmp,
                                                       self.remove_bond, self.add_bond,
                                                       button.get_label())
        eths_bond_dialog_ltb = urwid.ListBox(urwid.SimpleListWalker([eths_bond_dialog]))
        eths_bond_dialog_lnb = urwid.LineBox(eths_bond_dialog_ltb, "Bridge Device")
        self.listbox_content[3] = urwid.BoxAdapter(eths_bond_dialog_lnb, self.bond_for_bridge_height + 7)
        self.parent.refresh_screen()

    def apply(self, button):
        # the code here is used to check bond info and eth info
        if len(self.bridge_bond_inuse_tmp) == 0 and \
                        len(self.bridge_bond_usable_tmp) == 0:
            self.bridge_bond_inuse_tmp = copy.deepcopy(self.active_bridge_bond_inuse)
            self.bridge_bond_usable_tmp = copy.deepcopy(self.active_bridge_bond_usable)

        new_name = self.edits[0].original_widget.get_edit_text()
        ip_addr = self.edits[1].original_widget.get_edit_text()
        netmask = self.edits[2].original_widget.get_edit_text()

        # update IP info
        bridge_info_tmp = copy.deepcopy(self.bridge_info)
        del bridge_info_tmp[self.activebridge_name]
        bridge_dic = {new_name:{
            'devs': [],
            'ipv4': {'address': "", 'netmask': ""}
        }}
        bridge_info_tmp = dict(bridge_info_tmp, **bridge_dic)
        bridge_info_tmp[new_name]['ipv4']['address'] = ip_addr
        bridge_info_tmp[new_name]['ipv4']['netmask'] = netmask

        # update eths for bond info
        bond_info_tmp = copy.deepcopy(self.bond_info)
        inuse_list = []
        for inuse in self.bridge_bond_inuse_tmp:
            inuse_list.append(inuse)
            bond_info_tmp[inuse]['master'] = new_name
        bridge_info_tmp[new_name]['devs'] = inuse_list
        for usable in self.bridge_bond_usable_tmp:
            bond_info_tmp[usable]['master'] = ""

        response_bridge = networkhelper.update_bridge_info(bridge_info_tmp)
        response_bond = networkhelper.update_bond_info(bond_info_tmp)
        time.sleep(0.5)

        if response_bond[0] is True and response_bridge[0] is True:
            self.activebridge_name = new_name
            self.defaults["IP_ADDRESS"]["value"] = ip_addr
            self.defaults["NET_MASK"]["value"] = netmask
            self.defaults["BRIDGE_NAME"]["value"] = self.activebridge_name
            #self.back_button.keypress((10, ), 'enter')

            self.parent.footer.original_widget.set_text('update success')
            log.info('Apply change for %s success' % self.activebridge_name)
        else:
            self.parent.footer.original_widget.set_text('update fail')
            log.error('Apply change for %s fail: %s'%(self.activebridge_name,
                                                      response_bridge[1] + response_bond[1]))
        self.active_bridge_bond_inuse = []
        self.active_bridge_bond_usable = []

    def check_eth(self):
        focus = self.walker.get_focus()
        if focus[1] != 2:
            pass
        else:
            inner_pos = focus[0].original_widget.focus_position
            eth_name = focus[0].contents[inner_pos].get_label().split()[0]
            dialog.display_dialog(self, urwid.Text("%s is highlight"%eth_name), 'highlight', 'esc')

    def edit_bridge(self, button):
        if len(self.bridge_list) == 0:
            dialog.display_dialog(self, urwid.Text("No bridge could be edited"), "Error Operation")
            return
        # back button
        self.back_button = widget.Button('BACK', self.back_screen)
        back_button_line = urwid.GridFlow([self.back_button], 8, 0, 0, 'left')

        ## draw a new screen with two lineboxes which used to
        ## configure net info and eths for bond
        # linebox 1
        net_info_listbox = modulehelper.ModuleHelper.screenUI(self, [], self.fields,
                                                              self.defaults, button_visible=False)
        net_info_linebox = urwid.LineBox(net_info_listbox, "Network Address")
        # store edit fields for visiting conveniently
        self.edits_tmp = self.edits

        # linebox 2
        bond_for_bridge = widget.ColContainTwoListBox("Bond inuse", "Bond usable",
                                                      self.active_bridge_bond_inuse,
                                                      self.active_bridge_bond_usable,
                                                      self.remove_bond, self.add_bond)
        bond_for_bridge_listbox = modulehelper.ModuleHelper.screenUI(self, [bond_for_bridge],
                                                                   [], {}, button_visible=False,
                                                                     iblank=False)
        bond_for_bridge_linebox = urwid.LineBox(bond_for_bridge_listbox, "Bond Interface")

        # new screen
        self.bond_for_bridge_height = max([len(self.active_bridge_bond_inuse) , len(self.active_bridge_bond_usable)])
        screen_new_header = [back_button_line,
                             urwid.BoxAdapter(net_info_linebox, 7),
                             blank,
                             urwid.BoxAdapter(bond_for_bridge_linebox, self.bond_for_bridge_height + 7)]
        screen_new = modulehelper.ModuleHelper.screenUI(self, screen_new_header, [],
                                                        {}, button_label=["DEL", "APPLY"],
                                                        button_callback=[self.del_bridge_dialog, self.apply])
        self.edits = self.edits_tmp

        # redraw mod screen
        self.parent.draw_child_screen(screen_new)
        self.parent.cols.set_focus(1)
        self.edit_open = True

    def back_screen(self, button):
        self.screen = self.screenUI()
        self.refresh_details()
        self.parent.draw_child_screen(self.screen)
        self.parent.cols.set_focus(1)
        self.edit_open = False

    def refresh_details(self):
        # reload info
        self.bridge_info = self.bridge_info_load()
        self.bond_info = self.bond_info_load()
        self.bridge_list = sorted(self.bridge_info.keys())
        if self.activebridge_name not in self.bridge_list:
            self.activebridge_name = self.bridge_list[0]
        self.bridge_choices = widget.ChoicesGroup(self.bridge_list,
                                                  default_value=self.activebridge_name,
                                                  fn=self.radio_select_iface)
        # update radio button in header_content
        self.listbox_content[0] = self.bridge_choices
        self.listbox_content[0].set_focus(self.bridge_list.index(self.activebridge_name))
        # update details
        self.active_bridge_bond_inuse, self.active_bridge_bond_usable = self.get_bridge_bond_info(self.activebridge_name)
        self.listbox_content[2] = self.get_abstract_listbox(self.active_bridge_bond_inuse)
        self.parent.footer.original_widget.set_text("Update success")


    def handle_extra_input(self, key):
        if key == 'c':
            self.check_eth()
        if key == 'r':
            self.refresh_details()
        if key == 'esc' and self.edit_open:
            self.back_screen(None)
        else:
            pass

    def refresh(self):
        self.bridge_bond_inuse_tmp = []
        self.bridge_bond_usable_tmp = []

    def screenUI(self):
        screen = modulehelper.ModuleHelper.screenUI(self, self.header_content, [],
                                                    {}, button_visible=True,
                                                    button_label=['ADD', 'EDIT'],
                                                    button_callback=[self.add_bridge, self.edit_bridge])


        return screen


