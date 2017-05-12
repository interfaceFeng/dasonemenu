# -*- coding: utf-8 -*-

import logging
import urwid
import common.utils as utils
import uuid
import time
from common.challenge.challenge import _Secret
from common.challenge.inclib.libotp import  OTP
import common.modulehelper as modulehelper

log = logging.getLogger('login dasone')

blank = urwid.Divider(" ")

class Login(urwid.WidgetWrap):
    def __init__(self, parent, language=modulehelper.LanguageType.CHINESE):
        self.parent = parent
        self.screen = None
        self.name = 'Login'
        self.visible = True
        self.language = language
        self.user = "sysadmin"

        ##draw header_content
        # logo
        self.logo = urwid.AttrWrap(urwid.BigText('DASONE', urwid.Thin6x6Font()), 'red')
        self.logo_padded = urwid.Padding(self.logo, 'center', None)
        self.logo_pd_fd = urwid.Filler(self.logo_padded, 'bottom', 'pack')
        self.logo = urwid.BoxAdapter(self.logo_pd_fd, 8)
        # user with fixed name
        self.name_field = urwid.AttrWrap(urwid.Text(["USER:".ljust(20),
                                                     ('editcp', "SYSADMIN")]), 'red')

        # every time login in has a challenge for forgetting password in case
        self.challenge_generate = self.get_challenge()
        self.challenge_field = urwid.AttrWrap(urwid.Text(["CHALLENGE:".ljust(20),
                                                          ('editcp', self.challenge_generate)]), 'red')

        #create header_content
        self.header_content = [self.logo, blank, blank, self.name_field, self.challenge_field]

        ## draw_fields with default info
        self.fields = ['SYS_PASSWORD']
        self.defaults = \
            {
                "SYS_PASSWORD": {"label": "PASSWORD",
                               "tooltip": "if you forget password, contact with us and login using a challenge code",
                               "value": ""}
            }

    def login(self, button):
        # self.parent.main()
        passwd = self.edits[0].original_widget.get_edit_text()
        ret_passwd = self.login_password(passwd)
        ret_challenge = self.login_challenge(passwd)

        if ret_challenge or ret_passwd:
            self.parent.is_login = True
            time.sleep(0.1)
            self.parent.footer.original_widget.set_text("Login success, loading info may takes 5-10 second")
            self.parent.refresh_screen()
            self.parent.main()
            log.info("login success")
        else:
            msg = "login fail, password and challenge code both do not match"
            self.edits[0].original_widget.set_edit_text("")
            self.parent.footer.original_widget.set_text("%s, try again"%msg)
            log.warning(msg)




    def login_password(self, passwd):
        cmd = "su %s"%self.user
        ret = utils.run_cmd(cmd, False, passwd)
        self.parent.footer.original_widget.set_text(str(ret))
        if ret[0] != 0:
            self.parent.is_login = False

            return False
        else:
            return True

    def login_challenge(self, challenge_code):
        otp = OTP(length=8, timeout=120)
        otp.CHALLENGE = dict(SHA1=self.challenge_generate, SHA256=self.challenge_generate, SHA512=self.challenge_generate)
        challenge_code_check = otp.generate_challenge(_Secret.get_seed(_Secret.memfrob('46454d4344'.decode('hex'))))['SHA1']

        if challenge_code == challenge_code_check:
            return True

        else:
            return False



    def get_challenge(self):
        seed = uuid.uuid5(uuid.NAMESPACE_OID, uuid.NAMESPACE_OID.get_hex()).get_hex()
        challenge_generate = OTP().generate_challenge(seed)["SHA1"]

        return challenge_generate

    def handle_extra_input(self, key):
        pass


    def refresh(self):
        pass

    def screenUI(self):
        screen = modulehelper.ModuleHelper.screenUI(self, self.header_content, self.fields,
                                                    self.defaults, button_visible=True,
                                                    button_label=["LOGIN"],
                                                    button_callback=[self.login])
        self.login_password_state = True

        return screen


