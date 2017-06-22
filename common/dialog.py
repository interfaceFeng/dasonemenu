import common.urwidwidgetwrapper as widget
import urwid
import logging
import urwid.raw_display
import urwid.web_display

log = logging.getLogger("dialog")
blank = urwid.Divider()


class ModalDialog(urwid.WidgetWrap):
    signals = ['close']

    title = None

    def __init__(self, original_mod, title, body, previous_widget, escape_key='esc',
                 body_type=None, loop=None, mod_callback=None, confirm=True):
        self.escape_key = escape_key
        self.original_mod = original_mod
        self.previous_widget = previous_widget
        self.body_type = body_type
        self.edit_info = ' '
        self.keep_open = True
        self.loop = loop
        self.mod_callback = mod_callback

        if type(body) in [str, unicode]:
            body = urwid.Text(body)
        self.body = body
        self.title = title
        if confirm:
            bodybox = urwid.LineBox(urwid.Pile([urwid.AttrWrap(body, 'body'), blank, blank,
                                                widget.Button("OK", self.close, attr=None)]),title)
        else:
            bodybox = urwid.LineBox(urwid.Pile([urwid.AttrWrap(body, 'body'), blank]),title)
        pack = bodybox.pack((40, body.pack((40, ))[1] + 5))
        overlay = urwid.Overlay(urwid.Filler(bodybox), previous_widget,
                                'center', ('relative', 50), 'middle',
                                pack[1])
        overlay_attrmap = urwid.AttrMap(overlay, "dialog")
        super(ModalDialog, self).__init__(overlay_attrmap)

    def close(self, arg):
        # # if the dialog is editable, return edit msg to mod
        # if self.body_type == 'edit':
        #     self.mod_callback(self.body.get_edit_text())
        #
        # elif self.body_type == 'tworowlb':
        #     self.mod_callback(self.body.list_content_l,
        #                       self.body.list_content_r)
        # # if the dialog is to remind user to check modify
        # # return True
        # elif self.body_type == 'bool':
        #     self.mod_callback(True)


        urwid.emit_signal(self, "close")

        self.keep_open = False
        self.loop.widget = self.previous_widget
        self.mod_callback(None)

    def __repr__(self):
        return "<%s title='%s' at %s>" % (self.__class__.__name__, self.title,
                                          hex(id(self)))

    def keypress(self, size, key):
        super(ModalDialog, self).keypress(size, key)
        if key == self.escape_key:
            urwid.emit_signal(self, "close")
            self.keep_open = False
            self.loop.widget = self.previous_widget




def display_dialog(mod, body, title, escape_key="esc", body_type=None, mod_callback=None, confirm=True):
    filler = body
    dialog = ModalDialog(mod, title, filler,
                         mod.parent.mainloop.widget,
                         escape_key=escape_key,
                         body_type= body_type,
                         loop=mod.parent.mainloop,
                         mod_callback=mod_callback,
                         confirm=confirm
                         )
    mod.parent.mainloop.widget = dialog
    mod.parent.footer.original_widget.set_text('press %s to back'%escape_key)
    return dialog
