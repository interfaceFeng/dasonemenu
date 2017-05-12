#!/usr/bin/python
# -*- coding: utf-8 -*-

# program entry
# 2017.3.29 create

import logging
import consts

logging.basicConfig(filename = consts.LOGFILE,
                    format = "%(name)s %(asctime)s %(levelname)s %(message)s",
                    level = logging.DEBUG)

import datetime
import common.utils as utils
import common.dialog as dialog
import subprocess
import modules as modules
from common.modulehelper import LanguageType



import os
import sys
import signal
import urwid
import time
import optparse

import urwid.raw_display
import urwid.web_display
import common.urwidwidgetwrapper as widget

log = logging.getLogger('dsMenu.loader')
blank = urwid.Divider(" ")

class DASONESetUp(object):
    def __init__(self):
        self.footer = None
        self.header = None
        self.screen = None
        self.globalsave = True
        self.defaultsettingsfile = "%s/settings.yaml" \
                                  % (os.path.dirname(__file__))
        self.settingsfile = "/etc/dsMenu/astute.yaml"
        self.children = []
        self.child = None
        self.choices = []
        self.menubox = None
        self.childpage = None
        self.childfill = None
        self.childbox = None
        self.cols = None
        self.listwalker = None
        self.listbox = None
        self.frame = None
        self.mainloop = None
        self.langtype = None
        self.is_login = False

        self.draw_login_screen()
        self.choices = []

    def exit_program(self, button):
        noout = open('/dev/null', 'w')
        subprocess.call(["sysctl", "-w", "kernel.printk=4 1 1 7"],
                        stdout=noout, stderr=noout)
        raise urwid.ExitMainLoop()

    def menu(self, title, choices):
        body = [urwid.Text(title), blank]
        for c in choices:
            button = urwid.Button(c)
            urwid.connect_signal(button, 'click', self.menuitem_chosen, c)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        return urwid.ListBox(urwid.SimpleListWalker(body))

    def menuitem_chosen(self, button, c):
        if self.is_login is False :
            if c != "Login":
                self.menuitems.set_focus(2)
                dialog.display_dialog(self.child, urwid.Text("Please login first"), "Illegal Operation")
                return False
        size = self.screen.get_cols_rows()
        self.screen.draw_screen(size, self.frame.render(size))
        for item in self.menuitems.body.contents:
            try:
                if isinstance(item.base_widget, urwid.Button):
                    if item.base_widget.get_label() == c:
                        item.set_attr_map({None: 'header'})

                    else:
                        item.set_attr_map({None: None})
            except AttributeError:
                log.exception("Unable to set menu item %s" % item)
        self.set_child_screen(name=c)

    def set_child_screen(self, name=None):
        if name is None:
            self.child = self.children[0]
        else:
            self.child = self.children[int(self.choices.index(name))]
        if not self.child.screen:
            self.child.screen = self.child.screenUI()
        self.draw_child_screen(self.child.screen)

    def draw_child_screen(self, child_screen, focus_on_child=False):
        self.childpage = child_screen
        self.childfill = urwid.Filler(self.childpage, 'top', 40)
        self.childbox = urwid.BoxAdapter(self.childfill, 40)
        self.cols = urwid.Columns(
            [
                ('fixed', 20, urwid.Pile([
                    urwid.AttrMap(self.menubox, 'bright'),
                    blank])),
                ('weight', 3, urwid.Pile([
                    blank,
                    self.childbox,
                    blank]))
            ], 1)
        if focus_on_child:
            self.cols.focus_position=1 # focus on childbox
        self.child.refresh()
        self.listwalker[:] = [self.cols]

    def refresh_screen(self):
        size = self.screen.get_cols_rows()
        self.screen.draw_screen(size, self.frame.render(size))


    def global_save(self):
        #Runs save function for every module
        for module, modulename in zip(self.children, self.choices):
            #Run invisible modules. They may not have screen methods
            module.apply(None)
        return True, None



    def main(self):
        # this program use frame as the topmost widget, header and footer
        # play roles of the top and bottom lines of the frame
        self.children = []

        # load the modules will be used,
        # every module is one child
        # you can extend the num of modules by modify modules.__init__.py file
        for clsobj in modules.__all__[1:]:
            modobj = clsobj(self, LanguageType.ENGLISH) # default language is chinese
            self.children.append(modobj)

        if len(self.children) == 0:
            log.debug('there is no available modules, dsMenu exit')
            sys.exit(1)

        # build list of choices
        self.choices = [m.name for m in self.children]

        # build list of visible choices
        self.visiblechoices = []
        for child, choice in zip(self.children, self.choices):
            if child.visible:
                self.visiblechoices.append(choice)

        # finish menu box
        self.menuitems = self.menu(self.language_field['menu_label'], self.visiblechoices)
        menufill = urwid.Filler(self.menuitems, 'top', 40)
        self.menubox = urwid.BoxAdapter(menufill, 40)

        # finish child box
        self.child = self.children[0] # use DaSone user modules default
        self.childpage = self.child.screenUI()
        self.child.screen = self.childpage
        self.childfill = urwid.Filler(self.childpage, 'top', 22)
        self.childbox = urwid.BoxAdapter(self.childfill, 22)
        # create col widget contain menubox and child box
        self.cols = urwid.Columns(
            [
                ('fixed', 20, urwid.Pile([
                    urwid.AttrMap(self.menubox, 'body'),
                    urwid.Divider(" ")])),
                ('weight', 3, urwid.Pile([
                    blank,
                    self.childbox,
                    blank]))
            ], 1)

        # top second widget -- Listbox
        self.listwalker = urwid.SimpleListWalker([self.cols])
        self.listbox = urwid.ListBox(self.listwalker)

        #topmost widget --Frame
        self.frame = urwid.Frame(urwid.AttrMap(self.listbox, 'body'),
                                 header=self.header, footer=self.footer)

        # begin mainloop
        self.mainloop.widget = self.frame

    def draw_login_screen(self):
        # field which need to choose language
        self.language_field = {
            'text_header' : None,
            'text_footer' : None,
            'menu_label' : None
        }

        #language choose
        self.language_field = LanguageType.choose_language("DASONEMENU",
                                                      LanguageType.ENGLISH,
                                                      language_field=self.language_field)

        login_obj = modules.__all__[0]
        login_mod = login_obj(self, LanguageType.ENGLISH)
        self.child = login_mod
        self.header = urwid.AttrMap(urwid.Text(self.language_field['text_header']), 'header')
        self.footer = urwid.AttrMap(widget.RefreshText(self.language_field['text_footer'], container=self), 'footer')
        page = self.child.screenUI()
        self.login_screen = urwid.AttrWrap(page, 'body')
        palette = \
            [
                ('body', 'black', 'light gray', 'standout'),
                ('reverse', 'light gray', 'black'),
                ('header', 'white', 'dark red', 'bold'),
                ('important', 'dark red', 'light gray',
                 ('standout', 'underline')),
                ('editfc', 'white', 'light blue', 'bold'),
                ('editbx', 'light gray', 'light blue'),
                ('editcp', 'black', 'light gray', 'standout'),
                ('bright', 'dark gray', 'light gray', ('bold', 'standout')),
                ('buttn', 'black', 'dark cyan'),
                ('buttnf', 'white', 'dark blue', 'bold'),
                ('light gray', 'white', 'light gray', 'bold'),
                ('red', 'dark red', 'light gray', 'bold'),
                ('black', 'black', 'black', 'bold'),
                ('padding', 'white', 'black', 'bold'),
                ('filler', 'white', 'black', 'bold'),
                ('text selected good', 'dark green', 'light gray', 'bold'),
                ('text selected bad', 'dark gray', 'light gray', 'bold'),
                ('text selected focus', 'dark cyan', 'light gray', 'bold'),
                ('dialog', 'dark red', 'light gray', 'bold'),
            ]

        # use appropriate Screen class
        if urwid.web_display.is_web_request():
            self.screen = urwid.web_display.Screen()
        else:
            self.screen = urwid.raw_display.Screen()

        # handle unexpected signal
        def handle_extra_input(key):
            if key == 'f12':
                raise urwid.ExitMainLoop()
            if key == 'shift tab':
                self.child.walker.tab_prev()
            if key == 'tab':
                self.child.walker.tab_next()
            else:
                self.child.handle_extra_input(key)

        self.frame = urwid.Frame(urwid.AttrMap(self.login_screen, 'body'),
                                 footer=self.footer)
        # begin mainloop
        self.mainloop = urwid.MainLoop(self.frame, palette, self.screen,
                                       unhandled_input=handle_extra_input)

        self.mainloop.run()



def main(*args, **kwargs):
    if urwid.VERSION < (1, 1, 0):
        print ("This program requires urwid 1.1.0 or greater.")

    parser = optparse.OptionParser()
    parser.add_option("-s", "--save-only", dest="save_only",
                      action="store_true",
                      help="Save default values and exit")

    parser.add_option("-d", "--debug", dest="debug",
                      action="store_true",
                      help="Open debug mod and output debug info to debug file")

    # parser.add_option("-i", "--iface", dest="iface", metavar="IFACE",
    #                   default="eth0", help="Set IFACE as primary.")
    #
    options, args = parser.parse_args()

    if options.save_only:
        pass

    if options.debug:
        logging.basicConfig(filename = consts.DEBUGFILE,
                            format = "%(name)s %(asctime)s %(levelname)s %(message)s",
                            level = logging.DEBUG)
    setup()










def setup(**kwargs):
    DASONESetUp(**kwargs)

if '__main__' == __name__ or urwid.web_display.is_web_request():
    setup()



