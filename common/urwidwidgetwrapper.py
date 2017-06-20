import urwid
import logging
import threading
from urwid.util import is_mouse_press

log = logging.getLogger('urwidwidgetwrapper')
blank = urwid.Divider(" ")

def TextField(keyword, label, left_width, default_value=None, tooltip=None,
              tool_bar=None, disabled=False, ispassword=False, attr="editbx", attr_focus="editfc"):
    """Returns an Urwid Edit object."""
    if ispassword:
        mask = "*"
    else:
        mask = None

    if not tooltip:
        edit_obj = urwid.Edit(('important', label.ljust(left_width)),
                              default_value, mask=mask)
    else:
        edit_obj = TextFieldWithTip(('important', label.ljust(left_width)),
                                    default_value, tooltip, tool_bar,
                                    mask=mask)
    wrapped_obj = urwid.AttrWrap(edit_obj, attr, attr_focus)

    return wrapped_obj

def Button(text, callback=None, attr='buttn'):
    """Returns a wrapped Button with attributes buttn and buttnf."""
    button = urwid.Button(text, callback)
    return urwid.AttrMap(button, attr, 'reversed')


def Columns(objects):
    """Returns a padded Urwid Columns object that is left aligned."""
    #   Objects is a list of widgets. Widgets may be optionally specified
    #   as a tuple with ('weight', weight, widget) or (width, widget).
    #   Tuples without a widget have a weight of 1."""
    return urwid.Padding(TabbedColumns(objects, 1),
                         left=0, right=0, min_width=61)
def BoxText(label):
    return urwid.ListBox(urwid.SimpleListWalker([urwid.Text(label)]))

def BoxButton(label, callback):
    button = urwid.Button(label, callback)
    return urwid.ListBox(urwid.SimpleListWalker([button]))

def ButtonGroup(choice_labels, callback_list, cell_width=13, user_data=None):
    """Returns list of button in a one-line Gridflow."""

    button_list = []
    for txt, cb in zip(choice_labels, callback_list):
        button = urwid.Button(txt, cb)
        button_wrap = urwid.AttrWrap(button, 'buttn', 'reversed')
        button_list.append(button_wrap)

    wrapped_button_list = TabbedGridFlow(button_list, cell_width, 3, 0, 'left')
    # Bundle choice_labels so it can be used later easily
    wrapped_button_list.label_list = choice_labels
    return wrapped_button_list


def ChoicesGroup(choices, default_value=None, fn=None):
    """Returns list of RadioButtons in a one-line GridFlow."""
    rb_group = []

    for txt in choices:
        is_default = True if txt == default_value else False
        urwid.AttrWrap(urwid.RadioButton(rb_group, txt,
                                         is_default, on_state_change=fn,
                                         user_data=txt),
                       'buttn', 'buttnf')
    wrapped_choices = TabbedGridFlow(rb_group, 13, 3, 0, 'left')
    #Bundle rb_group so it can be used later easily
    wrapped_choices.rb_group = rb_group
    return wrapped_choices

def TextWithButton(txt, button):
    """:returns a col widget which display as a text and button in a one-line Coloumn """
    text = urwid.Text(txt)
    text_with_button = urwid.Columns([('weight', 1, text),
                                      ('weight', 1, button)],
                                     dividechars=2)
    wrapped_text_with_button = urwid.AttrWrap(text_with_button, 'body')
    # Bundle button and text so it can be used later easily
    wrapped_text_with_button.button = button
    wrapped_text_with_button.text = text

    return wrapped_text_with_button

def ColContainTwoListBox(label_l, label_r,
                         text_list_l, text_list_r,
                         callback_l=None, callback_r=None,
                         focus_label=None):
    """:returns a flow widget which display as two linebox placed vertically
                the two listbox contain a Text and Button list each"""
    list_content_l = []
    list_content_r = []
    focus_row_col = None
    focus_col = None
    for index, txt_l in enumerate(text_list_l):
        button_l = urwid.AttrWrap(ButtonNoClick(txt_l, callback_l), None, 'reversed')
        if txt_l == focus_label:
            focus_row_col = index
            focus_col = 0
        list_content_l.append(button_l)

    for index, txt_r in enumerate(text_list_r):
        if txt_r == focus_label:
            focus_row_col = index
            focus_col = 2
        button_r = urwid.AttrWrap(ButtonNoClick(txt_r, callback_r), None, 'reversed')
        list_content_r.append(button_r)

    listbox_l = urwid.ListBox(TabbedListWalker(list_content_l))
    listbox_r = urwid.ListBox(TabbedListWalker(list_content_r))

    if focus_col == 0:
        listbox_l.set_focus(focus_row_col)
    elif focus_col == 2:
        listbox_r.set_focus(focus_row_col)

    linebox_l = urwid.LineBox(listbox_l, label_l)
    linebox_r = urwid.LineBox(listbox_r, label_r)


    list_mid = []
    height_max = len(text_list_l) + len(text_list_r) + 1
    for i in range(0, height_max/2):
        list_mid.append(urwid.Divider(" "))
    list_mid.append(urwid.Text(" ->"))
    listbox_mid = urwid.ListBox(urwid.SimpleListWalker(list_mid))

    if focus_col is None and len(text_list_l) > 0:
        focus_col = 0
    else:
        focus_col = 2
    col_two_listbox = urwid.Columns([('weight', 5, linebox_l), ('weight', 1, listbox_mid),
                                     ('weight', 5, linebox_r)], focus_column=focus_col)

    wrapped_col_two_listbox = urwid.AttrWrap(urwid.BoxAdapter(col_two_listbox, height_max + 1), 'body')

    # Bundle
    wrapped_col_two_listbox.list_content_l = list_content_l
    wrapped_col_two_listbox.list_content_r = list_content_r

    return wrapped_col_two_listbox

# this class init a button class which can be selected but
# will never callback
class TextSelected(urwid.Button):
    signals = ['click']
    def __init__(self, caption, toolbar, tip, callback=None, status=True):
        super(TextSelected, self).__init__("")
        self.caption = "".join(caption)
        if status:
            attr_text = 'text selected good'
        else:
            attr_text = 'text selected bad'
        self._w = urwid.AttrMap(urwid.SelectableIcon(
            ['. ', caption], 2), attr_text, 'text selected focus'
        )
        self.toolbar = toolbar
        self.tip = tip

    def get_label(self):
        return self.caption

    def render(self, size, focus=False):
        if focus:
            self.toolbar.original_widget.set_text(self.tip)
        canv = super(TextSelected, self).render(size, focus)
        return canv


# this a button class which ignore mouse click but callback when
# user press enter or space
class ButtonNoClick(urwid.Button):
    button_left = urwid.Text("-")
    button_right = urwid.Text("")

    signals = []

    def __init__(self, label, on_press=None, user_data=None):
        super(ButtonNoClick, self).__init__(label, on_press, user_data)

    def mouse_event(self, size, event, button, x, y, focus):
        pass

# button used to as a switch
class Switch(urwid.Button):
    button_left = urwid.Text("||")
    button_right = urwid.Text(" ")
    state = False

    def __init__(self, label, on_press=None, user_data = None,
                 mod = None):
        self._label = urwid.SelectableIcon("", 0)
        cols = urwid.Columns([
            ('fixed', 2, self.button_left),
            self._label,
            ('fixed', 2, self.button_right)],
            dividechars=1)
        super(urwid.Button, self).__init__(cols)

        # The old way of listening for a change was to pass the callback
        # in to the constructor.  Just convert it to the new way:
        if on_press:
            urwid.connect_signal(self, 'click', on_press, user_data)

        self.callback_func = on_press
        self.user_data = user_data
        self.mod = mod
        log.debug(str(self.mod.parent))
        log.debug(str(mod.name))
    def mouse_event(self, size, event, button, x, y, focus):
        if button != 1 or not is_mouse_press(event):
            return False
        self.state = not self.state
        tmp = self.button_left
        self.button_left =self.button_right
        self.button_right = tmp
        self.__init__(self.get_label(),
                      self.callback_func,
                      self.user_data,
                      self.mod)
        self.mod.parent.refresh_screen()
        log.debug(str(self.button_right))
        #self._emit('click')
        return True



# this class init a Text class which refresh text in a interval
# with a init msg
class RefreshText(urwid.Text):
    def __init__(self, init_msg=" ", refresh_interval=3.0, container=None):
        self.init_msg = init_msg
        self.timer = None
        self.refresh_status = False
        self.container = container
        self.refresh_interval = refresh_interval
        super(RefreshText, self).__init__(init_msg)

    def set_text(self, markup):
        if self.refresh_status is False:
            super(RefreshText, self).set_text(markup)
            self.timer = threading.Timer(self.refresh_interval, self.refresh)
            self.timer.start()
            self.refresh_status = True
        else:
            self.timer.cancel()
            super(RefreshText, self).set_text(markup)
            self.timer = threading.Timer(self.refresh_interval, self.refresh)
            self.timer.start()

    def refresh(self):
        super(RefreshText, self).set_text(self.init_msg)
        self.refresh_status = False
        # if self.container is not None:
        #     self.container.refresh_screen()


class TabbedGridFlow(urwid.GridFlow):

    def __init__(self, cells, cell_width, h_sep, v_sep, align):
        urwid.GridFlow.__init__(self, cells=cells, cell_width=cell_width,
                                h_sep=h_sep, v_sep=v_sep, align=align)

    def keypress(self, size, key):
        if key == 'tab' and self.focus_position < (len(self.contents) - 1) \
                and self.contents[self.focus_position + 1][0].selectable():
            self.tab_next(self.focus_position)
        elif key == 'shift tab' and self.focus_position > 0 \
                and self.contents[self.focus_position - 1][0].selectable():
            self.tab_prev(self.focus_position)
        else:
            return self.__super.keypress(size, key)

    def tab_next(self, pos):
        self.set_focus(pos + 1)
        maxlen = (len(self.contents) - 1)
        while pos < maxlen:
            if self.contents[pos][0].selectable():
                return
            else:
                pos += 1

        if pos >= maxlen:
            pos = 0
        self.set_focus(pos)

    def tab_prev(self, pos):
        self.set_focus(pos - 1)
        while pos > 0:
            if self.contents[pos][0].selectable():
                return
            else:
                pos -= 1
        if pos == 0:
            pos = (len(self.contents) - 1)

        self.set_focus(pos)

    def first_selectable(self):
        '''returns index of first selectable widget in contents.'''
        for pos, item in enumerate(self.contents):
            if item[0].selectable():
                return pos
        return (len(self.contents) - 1)

class TabbedColumns(urwid.Columns):

    def __init__(self, widget_list, dividechars=0, focus_column=None,
                 min_width=1, box_columns=None):
        urwid.Columns.__init__(self, widget_list,
                               dividechars=dividechars,
                               focus_column=focus_column,
                               min_width=min_width,
                               box_columns=box_columns)

    def keypress(self, size, key):
        if key == 'tab' and self.focus_position < (len(self.contents) - 1) \
                and self.widget_list[self.focus_position + 1].selectable():
            self.tab_next(self.focus_position)
        elif key == 'shift tab' and self.focus_position > 0 \
                and self.widget_list[self.focus_position - 1].selectable():
            self.tab_prev(self.focus_position)
        else:
            return self.__super.keypress(size, key)

    def tab_next(self, pos):
        self.set_focus(pos + 1)
        maxlen = (len(self.contents) - 1)
        while pos < maxlen:
            if self.widget_list[pos].selectable():
                return
            else:
                pos += 1

        if pos >= maxlen:
            pos = 0
        self.set_focus(pos)

    def tab_prev(self, pos):
        self.set_focus(pos - 1)
        while pos > 0:
            if self.widget_list[pos].selectable():
                return
            else:
                pos -= 1
        if pos == 0:
            pos = (len(self.widget_list) - 1)

        self.set_focus(pos)

    def first_selectable(self):
        '''returns index of first selectable widget in widget_list.'''
        for pos, item in enumerate(self.widget_list):
            if item.selectable():
                return pos
        return (len(self.widget_list) - 1)

class TextFieldWithTip(urwid.Edit):
    def __init__(self, label, default_value=None, tooltip=None,
                 toolbar=None, mask=None):
        super(TextFieldWithTip, self).__init__(caption=label, edit_text=default_value,
                                               mask=mask)

        self.tip = tooltip
        self.toolbar = toolbar



    def render(self, size, focus=False):
        if focus:
            self.toolbar.original_widget.set_text(self.tip)
        canv = super(TextFieldWithTip, self).render(size, focus)
        return canv

class TabbedListWalker(urwid.ListWalker):
    def __init__(self, lst):
        self.lst = lst
        self.focus = 0

    def _modified(self):
        return urwid.ListWalker._modified(self)

    def tab_next(self):
        item, pos = self.get_next(self.focus)
        while pos is not None:
            if item.selectable():
                break
            else:
                item, pos = self.get_next(pos)
        if pos is None:
            pos = 0
        self.focus = pos
        self._modified()
        try:
            #Reset focus to first selectable widget in item
            if hasattr(item, 'original_widget'):
                item.original_widget.set_focus(
                    item.original_widget.first_selectable())
            else:
                item.set_focus(item.first_selectable())
        except Exception:
            #Ignore failure. Case only applies to TabbedColumns and
            #TabbedGridFlow. Other items should fail silently.
            pass

    def tab_prev(self):
        item, pos = self.get_prev(self.focus)
        while pos is not None:
            if item.selectable():
                break
            else:
                item, pos = self.get_prev(pos)

        if pos is None:
            pos = (len(self.lst) - 1)

        self.focus = pos
        self._modified()
        try:
            if hasattr(item, 'original_widget'):
                item.original_widget.set_focus(
                    len(item.original_widget.contents) - 1)
            else:
                item.set_focus(len(item.contents) - 1)
        except Exception:
            #Ignore failure. Case only applies to TabbedColumns and
            #TabbedGridFlow. Other items should fail silently.
            pass

    def get_focus(self):
        if self.lst:
            return self.lst[self.focus], self.focus
        else:
            return None, None

    def set_focus(self, focus):
        self.focus = focus

    def get_next(self, pos):
        if (pos + 1) >= len(self.lst):
            return None, None
        return self.lst[pos + 1], pos + 1

    def get_prev(self, pos):
        if (pos - 1) < 0:
            return None, None
        return self.lst[pos - 1], pos - 1

