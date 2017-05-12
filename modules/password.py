# -*- coding: utf-8 -*-

import logging
import urwid
import common.utils as utils
import common.modulehelper as modulehelper
import datetime

log = logging.getLogger('password configure')

blank = urwid.Divider(" ")

class PasswordAndSSH(urwid.WidgetWrap):
    def __init__(self, parent, language=modulehelper.LanguageType.CHINESE):
        self.parent = parent
        self.screen = None
        self.name = 'CHPASWD'
        self.visible = True
        self.language = language
        begin_ssh = datetime.datetime.now()
        self.ssh_login = self.load_ssh()
        end_ssh = datetime.datetime.now()
        log.info("ssh load: %s"%(end_ssh-begin_ssh))

        ##draw header_content
        # user with fixed name
        self.name_field = urwid.AttrWrap(urwid.Text(["USER:".ljust(20),
                                                     ('editcp', "SYSADMIN")]), 'red')
        self.ssh_login_field = urwid.CheckBox("SSH LOGIN", state=self.ssh_login, on_state_change=self.ssh_login_change)
        self.header_bottom = urwid.Columns([
            ('weight', 4, self.name_field),
            ('weight', 1, self.ssh_login_field)
        ])

        #create header_content
        self.header_content = [self.header_bottom]

        ## draw_fields with default info
        self.fields = ['NEW_PASSWORD', 'CONFIRM_PASSWORD']
        self.defaults = \
            {
                "NEW_PASSWORD": {"label": "NEW PASSWORD",
                                 "tooltip": "Input your new password here",
                                 "value": ""},
                "CONFIRM_PASSWORD": {"label": "CONFIRM",
                                     "tooltip": "Confirm your new password",
                                     "value": ""}
            }

    def load_ssh(self):
        cmd = "./modules/sh/ssh_load.sh"
        ret = utils.run_cmd(cmd, True)
        if ret[0] == 1:
            return True
        elif ret[0] == 0:
            return False

    def ssh_login_change(self, checkbox, state):
        self.ssh_login = state
        msg = "open" if self.ssh_login else "close"
        self.parent.footer.original_widget.set_text("You will %s ssh login as user sysadmin,"
                                                    " click APPLY to make it effect"%msg)

    def apply(self, button):
        new_password = self.edits[0].original_widget.get_edit_text()
        confirm_password = self.edits[1].original_widget.get_edit_text()

        if new_password != confirm_password:
            self.parent.footer.original_widget.set_text("Password is not matched!")
            return False

        if new_password == "" and confirm_password == "":
            new_password = "\'\'"

        pass_prama = "-o" if self.ssh_login is True else "-c"
        msg = "open" if self.ssh_login else "close"

        cmd_password = "./modules/sh/passwd.sh %s"%new_password
        ret_password = utils.run_cmd(cmd_password, True)
        cmd_ssh = "./modules/sh/ssh_login.sh %s"%pass_prama
        ret_ssh = utils.run_cmd(cmd_ssh, True)

        if ret_password[0] == 0:
            if ret_ssh[0] == 0:
                self.parent.footer.original_widget.set_text("Update password success,"
                                                            " ssh login is %s now"%msg)
            else:
                self.parent.footer.original_widget.set_text("Update password success, %s ssh login fail"%msg)


        elif ret_password[0] == 222:
            # change ssh status but not modify password
            if ret_ssh[0] == 0:
                self.parent.footer.original_widget.set_text("ssh login is %s now"%msg)
            else:
                self.parent.footer.original_widget.set_text("%s ssh login fail"%str(ret_ssh))


        else:
            self.parent.footer.original_widget.set_text("Update password error: %s"%str(ret_password))

        self.edits[0].original_widget.set_edit_text("")
        self.edits[1].original_widget.set_edit_text("")





    def handle_extra_input(self, key):
        pass


    def refresh(self):
        pass

    def screenUI(self):
        screen = modulehelper.ModuleHelper.screenUI(self, self.header_content, self.fields,
                                                    self.defaults, button_visible=True,
                                                    button_label=["APPLY"],
                                                    button_callback=[self.apply])


        return screen


