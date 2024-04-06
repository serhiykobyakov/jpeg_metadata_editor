""" modified TextCtrl class.
Provides spellcheck while type functionality"""

__version__ = '02.02.2023'
__author__ = 'Serhiy Kobyakov'
__license__ = "MIT"


import enchant
import wx
import wx.lib.newevent

DataReadyEvent, EVT_KEYW_DATA_READY = wx.lib.newevent.NewCommandEvent()



class MyTarget(wx.TextDropTarget):
    def __init__(self, obj):
        wx.TextDropTarget.__init__(self)
        self.object = obj

    def OnDropText(self, x, y, data):
        # print(f"OnDropText have text: -{data}-")
        # add a space before the dropped word to ensure it would not attached directly to the previous one
        self.object.AppendText(" ")
        return True


class KeywTextCtrl(wx.TextCtrl):
    """TextCtrl with spellcheck"""
    def __init__(self, parent, the_id, **kwargs):
        default_kwargs = {'wrap': False, 'allowComma': False, 'name': ''}
        kwargs = default_kwargs | kwargs
        self.allow_comma = kwargs['allowComma']
        self.need_spell_check_while_type = False
        wx.TextCtrl.__init__(self, parent=parent, id=the_id, style=wx.TE_MULTILINE, name=kwargs['name'])
        if kwargs['wrap']:
            self.SetWindowStyle(wx.TE_MULTILINE | wx.TE_WORDWRAP)

        self.SetDropTarget(MyTarget(self))
        self.Bind(wx.EVT_TEXT, self.__do_spellcheck_while_type)
        self.Bind(wx.EVT_CHAR, self.__filter_keys_while_type)

        self.the_dict = enchant.Dict("en_US")

    def __filter_keys_while_type(self, event):
        # filter out characters which are not allowed in the keywords
        # or not used in cursor positioning
        key_code = event.GetKeyCode()
        # print('KEY:', key_code)
        if key_code == 1 or key_code == 8 or key_code == 22 or key_code == 127 or key_code == 9:
            # select all, backspace, paste, delete, tab
            event.Skip()
        elif key_code == 3 or key_code == 22:
            # Ctrl+C, Ctrl+V
            event.Skip()
        elif key_code == 44 and self.allow_comma:
            # comma
            event.Skip()
        elif 312 <= key_code <= 317:
            # home and end; left, right, up and down arrows
            event.Skip()
        elif key_code == 13:
            # on Enter: format text line
            self.format_text()
            self.spell_check()
            # send event: the keywords are ready to check
            event = DataReadyEvent(self.GetId())
            self.GetEventHandler().ProcessEvent(event)
            # event.Skip() <- comment it to avoid GTK problems
        elif self.valid_char(key_code):
            self.need_spell_check_while_type = True
            event.Skip()
        else:
            # block out everything else
            pass

    @staticmethod
    def valid_char(key_code: int) -> bool:
        # function returns True if the key_code is a valid character code
        return chr(key_code) in " -abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'"

    def __do_spellcheck_while_type(self, event):
        """do spellcheck while type if necessary"""
        if len(self.GetLineText(0)) == self.GetInsertionPoint() and self.need_spell_check_while_type:
            last_word = self.GetLineText(0).split(' ')[-1]
            if len(last_word) > 1:
                the_end = len(self.GetLineText(0))
                the_start = len(self.GetLineText(0)) - len(last_word)
                if self.the_dict.check(last_word):
                    self.SetStyle(the_start, the_start + 1, self.GetDefaultStyle())
                    self.SetStyle(the_start, the_end, wx.TextAttr(wx.BLACK))
                else:
                    self.SetStyle(the_start, the_end, wx.TextAttr(wx.RED))
                # print("spellcheck:", last_word, self.the_dict.check(last_word))
            self.need_spell_check_while_type = False

    def format_text(self):
        """remove unnecessary spaces and then remove duplicates"""
        if len(self.GetLineText(0)) > 0:
            the_line = self.GetLineText(0).replace('  ', ' ').replace('  ', ' ').strip()
            keywords = list(dict.fromkeys(the_line.split(' ')))
            new_line = ' '.join(keywords)
            if len(the_line) != len(new_line):
                self.Clear()
                self.AppendText(new_line)

    def spell_check(self):
        """show misspelled words in red"""
        if len(self.GetLineText(0)) > 0:
            the_line = self.GetLineText(0)
            words = the_line.split(' ')
            for word in words:
                the_start = the_line.find(word)
                the_end = the_start + len(word)
                if self.the_dict.check(word):
                    self.SetStyle(the_start, the_start + 1, self.GetDefaultStyle())
                    self.SetStyle(the_start, the_end, wx.TextAttr(wx.BLACK))
                else:
                    self.SetStyle(the_start, the_end, wx.TextAttr(wx.RED))

    def append_words(self, the_line: str):
        """append new line with keywords into the text field"""
        if len(self.GetLineText(0)) > 0:
            self.AppendText(' ' + the_line.strip())
        else:
            self.AppendText(the_line.strip())

    def list_of_words(self) -> list:
        """return a list of words"""
        return self.GetLineText(0).split(" ")
