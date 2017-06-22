import logging
import urwid
import common.urwidwidgetwrapper as urwidwrapper
import six
import os
import sys

try:
    from collections import OrderedDict
except Exception:
    # python 2.6 or earlier use backport
    from ordereddict import OrderedDict
import yaml

log = logging.getLogger('common.modulehelper')

blank = urwid.Divider()

class LanguageType(object):
    CHINESE = 1 # default value
    ENGLISH = 2
    tail ={
        CHINESE: "_ch",
        ENGLISH: "_en"
    }
    @classmethod
    def choose_language(cls, part, language=CHINESE,
                        language_field=None):
        stringdir = "%s/strings"%sys.path[0]
        language_tail = cls.tail.get(language, "_ch")
        stringsfile = stringdir + '/' + 'strings' + language_tail + '.yaml'
        strings = cls._read_string_by_language(stringsfile,
                                              part, language_tail)
        log.debug(strings)
        for key in language_field:
            language_field[key] = strings[key]

        return language_field

    @classmethod
    def _read_string_by_language(cls, yamlfile, partname,
                                tail):
        try:
            infile = file(yamlfile, 'r')
            strings = yaml.load(infile)
            if strings is not None:
                strings = strings[partname]
                # if strings is not None:
                #     strings = strings[tail]
                #     return strings
                # else:
                #     log.warning("there is no strings in language %s"
                #             % tail)
                #     return OrderedDict()
                return strings
            else:
                log.warning("there is no part %s in strings file"
                    % partname)
                return OrderedDict()
        except Exception:
            if yamlfile is not None:
                import logging
                log.error("Unable to read YAML: %s" % yamlfile)
            log.debug("return empty orderedDict")
            return OrderedDict()


class WidgetType(object):
    TEXT_FIELD = 1  # default value. may be skipped
    LABEL = 2
    RADIO = 3
    CHECKBOX = 4
    LIST = 5
    BUTTON = 6
    LABEL_BUTTON = 7



class ModuleHelper(object):
    @classmethod
    def _get_header_content(cls, header_text):
        # this method can extend its function
        # when header_text is not only text-type
        # by add a filter
        def _convert(text):
            if isinstance(text, six.string_types):
                return urwid.Text(text)
            return text

        return [_convert(text) for text in header_text]

    @classmethod
    def _create_button_widget(cls, default_data):
        label = default_data.get('label', "")
        callback = default_data.get('callback', "")
        button = urwidwrapper.Button(label, callback)
        return button

    @classmethod
    def _create_label_widget(cls, label, default_date):
        return urwid.Text([('important', label.ljust(20)), default_date])

    @classmethod
    def _create_label_button_widget(cls, default_data):
        label = default_data.get('label', "")
        callback = default_data.get('callback', None)
        value = default_data.get('value', "")
        button = urwidwrapper.Button(value, callback,
                                     b_l="", ismiddle=False)
        label_button = urwidwrapper.TextWithButton(label, button)
        return label_button

    @classmethod
    def _create_widget(cls, key, default_data, toolbar):
        field_type = default_data.get('type', WidgetType.TEXT_FIELD)

        # you can expend widget's type here
        if field_type == WidgetType.LABEL:
            label = default_data.get('label', '')
            default = default_data.get('value', '')
            return cls._create_label_widget(label, default)



        if field_type == WidgetType.TEXT_FIELD:
            ispassword = "PASSWORD" in key.upper()
            label = default_data.get('label', '')
            default = default_data.get('value', '')
            tooltip = default_data.get('tooltip', '')
            return urwidwrapper.TextField(key, label, left_width=20,
                                          default_value=default,
                                          tooltip=tooltip, tool_bar=toolbar,
                                          ispassword=ispassword)
        elif field_type == WidgetType.BUTTON:
            return cls._create_button_widget(default_data)

        elif field_type == WidgetType.LABEL_BUTTON:
            return cls._create_label_button_widget(default_data)

    @classmethod
    def _setup_widgets(cls, toolbar, fields, defaults):
        return [cls._create_widget(key, defaults.get(key, {}), toolbar)
                for key in fields]

    @classmethod
    def _get_button_column(cls, modobj, button_label, button_callback):
        # get the button column at the bottom of the mod
        button_list = []
        for btn_l, callback in zip(button_label, button_callback):
            button = urwidwrapper.Button(btn_l, callback)
            button_list.append(button)

        button_list.append(('weight', 2, blank))

        return urwidwrapper.Columns(button_list)

    @classmethod
    def cancel(cls, modobj, button=None):
        for index, fieldname in enumerate(modobj.fields):
            if fieldname != "blank" and "label" not in fieldname:
                try:
                    modobj.edits[index].set_edit_text(modobj.defaults[fieldname][
                                                       'value'])
                except AttributeError:
                    log.warning("Field %s unable to reset text" % fieldname)
                    return False
        return True

    @classmethod
    def screenUI(cls, modobj, header_text=None, fields=None,
                 defaults=None, button_visible=True,
                 button_label=None, button_callback=None, iblank=True):
        log.debug("Preparing screen UI for %s", modobj.name)
        # preparing header_content
        log.debug("Preparing header_context for %s", modobj.name)
        header_content = cls._get_header_content(header_text)
        listbox_content = header_content
        # preparing editable fields with widgets
        log.debug("Preparing setup widgets for %s", modobj.name)
        edits = cls._setup_widgets(modobj.parent.footer, fields, defaults)
        # use listbox_content to store header_text and edits fields
        if iblank:
            listbox_content.append(blank)

        listbox_content.extend(edits)

        if iblank:
            listbox_content.append(blank)

        # Wrap buttons into Columns so it doesn't expand and look ugly
        log.debug("Preparing button for %s", modobj.name)
        button_column = None
        if button_visible:
            button_column = cls._get_button_column(modobj, button_label, button_callback)
            listbox_content.append(button_column)

        # add everything into a listbox and return it
        listwalker = urwidwrapper.TabbedListWalker(listbox_content)
        screen = urwid.ListBox(listwalker)

        # save information which may used in future

        modobj.edits = edits
        modobj.button_column = button_column
        modobj.walker = listwalker
        modobj.listbox_content = listbox_content

        return screen






