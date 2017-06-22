# -*- coding: utf-8 -*-

import logging
import urwid
import common.dialog as dialog
import common.modulehelper as modulehelper
import common.sysnettool.systool as networkhelper
import common.urwidwidgetwrapper as widget
import time
import copy
import datetime

log = logging.getLogger('bond setup')

blank = urwid.Divider(" ")

class Bond(urwid.WidgetWrap):
    mode_info_list = ['balance-rr', 'active-backup', 'balance-xor',
                      'broadcast', '802.3ad', 'balance-tlb',
                      'balance-alb']

    def __init__(self, parent, language=modulehelper.LanguageType.CHINESE):
        self.parent = parent
        self.screen = None
        self.original_screen = None
        self.name = 'BOND'
        self.visible = True
        self.edit_open = False
        self.language = language

        self.bond_info = self.bond_info_load()
        self.eth_info = self.eth_info_load()

        ##draw header_content
        # radiobuton group under the button list but on the bond abstract
        self.bond_list = sorted(self.bond_info.keys())
        if len(self.bond_list) > 0:
            self.activebond_name = self.bond_list[0]
        else:
            # only used to avoid index error
            self.activebond_name = 'bond'
        # eth info in active bond
        self.active_bond_eth_inuse = []
        self.active_bond_eth_usable = []
        self.bond_eth_inuse_tmp = []
        self.bond_eth_usable_tmp = []
        self.active_bond_eth_inuse, self.active_bond_eth_usable = self.get_bond_eth_info(self.activebond_name)

        # create radiobutton group and set
        self.bond_choices = widget.ChoicesGroup(self.bond_list,
                                                default_value=self.activebond_name,
                                                fn=self.radio_select_iface)
        self.eth_info_abstract_listbox = self._get_abstract_listbox(self.active_bond_eth_inuse)
        #create header_content
        self.header_content = [self.bond_choices, urwid.Divider(" "),
                               self.eth_info_abstract_listbox]

        ## draw_fields with default info
        self.fields = ['BOND_NAME', 'BOND_MODE', 'IP_ADDRESS', 'NET_MASK']
        self.defaults = \
            {
                "BOND_NAME" :{"label": "NAME",
                              "type": modulehelper.WidgetType.LABEL,
                              "tooltip": "Change your bond name here",
                              "value": ""},
                "IP_ADDRESS": {"label": "ADDRESS",
                              "tooltip": "Manual configure IP address (example 192.168.1.2)",
                              "value": ""},
                "NET_MASK": {"label": "NETMASK",
                             "tooltip": "Manaual configure netmask (example 255.255.0.0)",
                             "value": ""},
                "BOND_MODE": {"label": "MODE",
                              "type": modulehelper.WidgetType.LABEL_BUTTON,
                              "callback": self.modify_bond_mode,
                              "tooltip": "",
                              "value": ""}
            }
        self.update_bond_default()


    def bond_info_load(self):
        # edit there to get bond info
        bond_info = networkhelper.get_bond_info()
        log.debug(bond_info)
        if not bond_info:
            body_msg = "load bond info error, bond info is error or bond info is empty"
            msg = 'Bond info is empty'
            self.parent.footer.original_widget.set_text(msg)
            log.warning(body_msg)
            return {}
        else:
            return bond_info

    def eth_info_load(self):
        # edit there to get bond info
        eth_info = networkhelper.get_eth_info()
        if not eth_info:
            body_msg = "load eth info error, info is error or info is empty"
            msg = 'Eth devices info is empty'
            self.parent.footer.original_widget.set_text(msg)
            log.warning(body_msg)
            return {}
        else:
            return eth_info

    # return a flow widget which wrap a listbox widget containing
    # eth inuse abstract listbox
    def _get_abstract_listbox(self, active_bond_eth_inuse):
        list_content = []
        msg = "Press c to check devices or r to refresh info"
        for eth_inuse in active_bond_eth_inuse:
            abstract = self.eth_info[eth_inuse]['mac']
            link_up = self.eth_info[eth_inuse]['abstract']['status']
            status = True if link_up=="up" else False
            text_slt = widget.TextSelected(["%s   "%eth_inuse.ljust(9),
                                           "mac: %s   "%abstract.ljust(20),
                                           "Link: %s"%link_up],
                                           self.parent.footer,
                                           msg, status=status)
            list_content.append(text_slt)
        listbox = urwid.ListBox(widget.TabbedListWalker(list_content))
        wrapped_listbox = urwid.BoxAdapter(listbox, len(active_bond_eth_inuse))
        # bundle
        wrapped_listbox.contents = list_content
        if len(list_content) > 0 :
            return wrapped_listbox
        else:
            return blank

    def convert_mode_string_digit(self, alias):
        if str.isdigit(alias):
            return self.mode_info_list[int(alias)]
        else:
            return self.mode_info_list.index(alias)

    def modify_bond_mode(self, button):
        msg = "Choose bond mode"
        rgroup = []
        content_body = [blank]
        for radio_mode_index in range(0, len(self.mode_info_list)):
            if button.get_label().split(":")[0] == str(radio_mode_index):
                radio_mode_status = True
            else:
                log.debug(radio_mode_index)
                radio_mode_status = False
            radio_bond_piece = urwid.RadioButton(rgroup,
                                                   "%s: %s"%(
                                                       radio_mode_index,
                                                       self.convert_mode_string_digit(str(radio_mode_index))
                                                   ),
                                                   radio_mode_status,
                                                   self.modify_bond_mode_radiobutton_callback
                                                   )
            content_body.append(radio_bond_piece)
        radio_mode_listbox = urwid.ListBox(widget.TabbedListWalker(content_body))
        radio_mode_adapter = urwid.BoxAdapter(radio_mode_listbox, len(self.mode_info_list) + 1)
        self.radio_mode_dialog = dialog.display_dialog(self, radio_mode_adapter, msg, confirm=False)

    def modify_bond_mode_radiobutton_callback(self, radiobutton, args):
        if args:
            mode_value = radiobutton.get_label()
            self.radio_mode_dialog.close(None)
            self.edits[1].button.original_widget.set_label(mode_value)



    def add_bond(self, button):
        msg = "Create new bond"
        edit_field = widget.TextField(
            None, 'Bond name', 10,
            tooltip='Manual add bond, edit bond name with digit and alpha',
            default_value="",
            tool_bar = self.parent.footer
        )
        dialog.display_dialog(self, edit_field, msg, body_type='edit',
                              mod_callback=self.dialog_callback_add_bond)

    def dialog_callback_add_bond(self, bond_name):
        # check name
        format_msg = 'Unusable bond'
        if bond_name == '':
            self.parent.footer.original_widget.set_text("%s: bond name can not be empty"
                                                        % format_msg)
            return False
        for c in bond_name:
            if c.isalpha() is False and c.isdigit() is False:
                self.parent.footer.original_widget.set_text("%s: bond name can only contain digits and alpha"
                                                            % format_msg)
                return False
        if bond_name in self.bond_info.keys():
            self.parent.footer.original_widget.set_text("%s: bond has existed"
                                                        % format_msg)
            return False

        # update bond info
        bond_dic = {bond_name:{
        }}
        response = networkhelper.add_bond(bond_dic)
        time.sleep(0.5)

        if response[0] is True:
            # reload info
            self.refresh_details()
            if len(self.bond_list) == 1:
                self.update_bond_default()
            log.info("create new bond: %s"%bond_name)
            self.parent.footer.original_widget.set_text("update success")
            self.parent.refresh_screen()
            return True
        else:
            msg = 'add fail：update info error'
            log.error("add %s error: %s"%(bond_name, response[1]))
            self.parent.footer.original_widget.set_text(msg)
            return False
    def del_bond_dialog(self, button):
        msg = "Delete bond: %s ?"%self.activebond_name
        dialog.display_dialog(self, urwid.Text(msg), "Confirm your operation",
                              body_type='bool', mod_callback=self.del_bond)

    def del_bond(self, confirm):
        bond_name = self.activebond_name
        # update bond info
        response_bond = networkhelper.del_bond([bond_name])
        time.sleep(0.5)

        if response_bond[0] is True :
            # reload info
            self.refresh_details()
            self.back_button.keypress((10, ), 'enter')
            self.update_bond_default()
            self.parent.footer.original_widget.set_text("update success")
            self.parent.refresh_screen()
            log.info("del bond: %s success"%bond_name)
            return True
        else:
            msg = 'update fail: error update bond info'
            self.parent.footer.original_widget.set_text(msg)
            log.error("del bond: %s fail: %s"%(bond_name, response_bond[1]))
            return False


    def radio_select_iface(self, radiobutton, state, bond_name):
        if state is True:
            self.activebond_name = bond_name
            self.active_bond_eth_inuse, self.active_bond_eth_usable = self.get_bond_eth_info(bond_name)
            self.bond_eth_usable_tmp = []
            self.bond_eth_inuse_tmp = []
            self.listbox_content[2] = self._get_abstract_listbox(self.active_bond_eth_inuse)
            self.update_bond_default()


    # get inuse and usable eth for one bond
    def get_bond_eth_info(self, bond_name):
        inuse = []
        usable = []

        for eth in self.eth_info:
            if self.eth_info[eth]['master'] == bond_name:
                inuse.append(eth)

            elif self.eth_info[eth]['master'] == "":
                usable.append(eth)
        inuse = sorted(inuse)
        usable = sorted(usable)
        return inuse, usable


    # this two functions only use to remove or add eth in display
    # but not remove or add eth in fact
    def remove_eth(self, button):
        if len(self.bond_eth_inuse_tmp) == 0 and len(self.bond_eth_usable_tmp) == 0:
            self.bond_eth_inuse_tmp = copy.deepcopy(self.active_bond_eth_inuse)
            self.bond_eth_usable_tmp = copy.deepcopy(self.active_bond_eth_usable)

        button_label = button.get_label()
        self.bond_eth_inuse_tmp.remove(button_label)
        self.bond_eth_usable_tmp.append(button_label)
        self.bond_eth_usable_tmp = sorted(self.bond_eth_usable_tmp)
        # display new dialog
        eths_bond_dialog = widget.ColContainTwoListBox('Interface inuse', 'Interface usable',
                                                       self.bond_eth_inuse_tmp,
                                                       self.bond_eth_usable_tmp,
                                                       self.remove_eth, self.add_eth,
                                                       button.get_label())
        eths_bond_dialog_ltb = urwid.ListBox(urwid.SimpleListWalker([eths_bond_dialog, blank, blank]))
        eths_bond_dialog_lnb = urwid.LineBox(eths_bond_dialog_ltb, "Bond Interface")
        self.listbox_content[3] = urwid.BoxAdapter(eths_bond_dialog_lnb, self.eths_for_bond_height + 6)
        self.parent.refresh_screen()

    def add_eth(self, button):
        if len(self.bond_eth_inuse_tmp) == 0 and len(self.bond_eth_usable_tmp) == 0:
            self.bond_eth_inuse_tmp = copy.deepcopy(self.active_bond_eth_inuse)
            self.bond_eth_usable_tmp = copy.deepcopy(self.active_bond_eth_usable)

        button_label = button.get_label()
        self.bond_eth_inuse_tmp.append(button_label)
        self.bond_eth_usable_tmp.remove(button_label)
        self.bond_eth_inuse_tmp = sorted(self.bond_eth_inuse_tmp)

        # display new dialog
        eths_bond_dialog = widget.ColContainTwoListBox('Interface inuse', 'Interface usable',
                                                  self.bond_eth_inuse_tmp,
                                                  self.bond_eth_usable_tmp,
                                                  self.remove_eth, self.add_eth,
                                                       button.get_label())
        eths_bond_dialog_ltb = urwid.ListBox(urwid.SimpleListWalker([eths_bond_dialog, blank, blank]))
        eths_bond_dialog_lnb = urwid.LineBox(eths_bond_dialog_ltb, "Bond Interface")
        self.listbox_content[3] = urwid.BoxAdapter(eths_bond_dialog_lnb, self.eths_for_bond_height + 6)
        self.parent.refresh_screen()

    def apply(self, button):
        # the code here is used to check bond info and eth info
        self.parent.footer.original_widget.set_text("Apply change, it takes 5-10s")
        self.parent.refresh_screen()
        if len(self.bond_eth_inuse_tmp) == 0 and\
            len(self.bond_eth_usable_tmp) == 0:
            self.bond_eth_inuse_tmp = copy.deepcopy(self.active_bond_eth_inuse)
            self.bond_eth_usable_tmp = copy.deepcopy(self.active_bond_eth_usable)

        ip_addr = self.edits[2].original_widget.get_edit_text()
        netmask = self.edits[3].original_widget.get_edit_text()

        bond_mode = self.edits[1].button.original_widget.get_label().split(":")[0]
        bond_master = self.bond_info[self.activebond_name]['master']

        # update IP info
        set_tmp = set()
        bond_dic = {self.activebond_name:{
            'device': self.activebond_name,
            'master': bond_master,
            'mode': bond_mode,
            'slave': {'Eth': set_tmp},
            'ip4':[{'address': "", 'netmask': ""}]
        }}
        if ip_addr:
            bond_dic[self.activebond_name]['ip4'][0]['address'] = ip_addr
        if netmask:
            bond_dic[self.activebond_name]['ip4'][0]['netmask'] = netmask
        if not ip_addr and not netmask:
            del bond_dic[self.activebond_name]['ip4']
        # update eths for bond info
        inuse_set = set()
        for inuse in self.bond_eth_inuse_tmp:
            inuse_set.add(inuse)
        if len(inuse_set) > 0:
            bond_dic[self.activebond_name]['slave']['Eth'] = inuse_set
        else:
            del bond_dic[self.activebond_name]['slave']

        response_bond = networkhelper.update_bond_info(bond_dic)

        if response_bond[0] is True:
            self.defaults["IP_ADDRESS"]["value"] = ip_addr
            self.defaults["NET_MASK"]["value"] = netmask
            self.defaults["BOND_NAME"]["value"] = self.activebond_name
            #self.back_button.keypress((10, ), 'enter')

            self.parent.footer.original_widget.set_text('update success')
            log.info('Apply change for %s success'%self.activebond_name)
        else:
            self.parent.footer.original_widget.set_text('update fail')
            log.error('Apply change for %s fail: %s'%(self.activebond_name,
                                                      response_bond[1]))
        self.active_bond_eth_inuse = []
        self.active_bond_eth_usable = []

    def check_eth(self):
        focus = self.walker.get_focus()
        if focus[1] != 2:
            pass
        else:
            inner_pos = focus[0].original_widget.focus_position
            eth_name = focus[0].contents[inner_pos].get_label().split()[0]
            dialog.display_dialog(self, urwid.Text("%s is highlight"%eth_name), 'highlight', 'esc')

    def update_bond_default(self):
        self.defaults["BOND_NAME"]["value"] = self.activebond_name
        if len(self.bond_list) > 0:
            alias = self.bond_info[self.activebond_name]['mode']
            mode = self.convert_mode_string_digit(alias)
            self.defaults["BOND_MODE"]["value"] = "%s: %s"%(alias, mode)
        else:
            self.defaults["BOND_MODE"]["value"] = ""
        if len(self.bond_list) > 0 and self.bond_info[self.activebond_name]['ip4']:
            self.defaults["IP_ADDRESS"]["value"] = self.bond_info[self.activebond_name]['ip4'][0]['address']
            self.defaults["NET_MASK"]["value"] = self.bond_info[self.activebond_name]['ip4'][0]['netmask']
        else :
            self.defaults["IP_ADDRESS"]["value"] = ""
            self.defaults["NET_MASK"]["value"] = ""

    def edit_bond(self, button):
        if len(self.bond_list) == 0:
            dialog.display_dialog(self, urwid.Text("No bond could be edited"), "Error Operation")
            return
        # back button
        self.back_button = widget.Button('BACK', self.back_screen)
        back_button_line = urwid.GridFlow([self.back_button], 12, 0, 0, 'left')

        ## draw a new screen with two lineboxes which used to
        ## configure net info and eths for bond
        # linebox 1
        net_info_listbox = modulehelper.ModuleHelper.screenUI(self, [], self.fields,
                                                              self.defaults, button_visible=False)
        net_info_linebox = urwid.LineBox(net_info_listbox, "Network Address")
        # store edit fields for visiting conveniently
        self.edits_tmp = self.edits

        # linebox 2
        eths_for_bond = widget.ColContainTwoListBox("Interface inuse", "Interface usable",
                                                    self.active_bond_eth_inuse,
                                                    self.active_bond_eth_usable,
                                                    self.remove_eth, self.add_eth)
        eths_for_bond_listbox = modulehelper.ModuleHelper.screenUI(self, [eths_for_bond],
                                                                   [], {}, button_visible=False)
        eths_for_bond_linebox = urwid.LineBox(eths_for_bond_listbox, "Bond Interface")

        # new screen
        self.eths_for_bond_height = len(self.active_bond_eth_inuse) + len(self.active_bond_eth_usable)
        screen_new_header = [back_button_line,
                             urwid.BoxAdapter(net_info_linebox, 8),
                             blank,
                             urwid.BoxAdapter(eths_for_bond_linebox, self.eths_for_bond_height + 6)]
        screen_new = modulehelper.ModuleHelper.screenUI(self, screen_new_header, [],
                                                        {}, button_label=["DEL", "APPLY"],
                                                        button_callback=[self.del_bond_dialog, self.apply])
        self.edits = self.edits_tmp

        # redraw mod screen
        self.parent.draw_child_screen(screen_new)
        self.parent.cols.set_focus(1)
        self.edit_open = True

    def back_screen(self, button):
        self.parent.footer.original_widget.set_text("Refresh info, it takes 5-10s")
        self.parent.refresh_screen()
        self.screen = self.screenUI()
        self.refresh_details()
        self.parent.draw_child_screen(self.screen)
        self.parent.cols.set_focus(1)
        self.edit_open = False

    def refresh_details(self):
        # reload info
        self.bond_info = self.bond_info_load()
        self.eth_info = self.eth_info_load()
        self.bond_list = sorted(self.bond_info.keys())
        if self.activebond_name not in self.bond_list:
            if self.bond_list:
                self.activebond_name = self.bond_list[0]
            else:
                self.activebond_name = 'bond'
        self.bond_choices = widget.ChoicesGroup(self.bond_list,
                                                default_value=self.activebond_name,
                                                fn=self.radio_select_iface)
        # update radio button in header_content
        self.listbox_content[0] = self.bond_choices
        if self.bond_list:
            self.listbox_content[0].set_focus(self.bond_list.index(self.activebond_name))
            # update details
            self.active_bond_eth_inuse, self.active_bond_eth_usable = self.get_bond_eth_info(self.activebond_name)
            self.listbox_content[2] = self._get_abstract_listbox(self.active_bond_eth_inuse)
        else:
            self.listbox_content[2] = self._get_abstract_listbox([])
        self.parent.footer.original_widget.set_text("Update success")
        self.bond_eth_inuse_tmp = []
        self.bond_eth_usable_tmp = []

    def handle_extra_input(self, key):
        if key == 'c':
            self.check_eth()
        if key == 'r':
            self.parent.footer.original_widget.set_text("Refresh info, it takes 5-10s")
            self.parent.refresh_screen()
            self.refresh_details()
        if key == 'esc' and self.edit_open:
            self.back_screen(None)
        else:
            pass

    def refresh(self):
        self.bond_eth_usable_tmp = []
        self.bond_eth_inuse_tmp = []

    def screenUI(self):
       screen = modulehelper.ModuleHelper.screenUI(self, self.header_content, [],
                                                   {}, button_visible=True,
                                                  button_label=['ADD', 'EDIT'],
                                                  button_callback=[self.add_bond, self.edit_bond])

       return screen


