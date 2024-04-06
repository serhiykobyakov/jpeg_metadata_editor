#!/usr/bin/python3

__version__ = '01.01.2023'
__author__ = 'Serhiy Kobyakov'
__license__ = "MIT"


import wx
from keyw import KeywFrame


if __name__ == "__main__":
    app = wx.App()
    frame = KeywFrame(None)
    frame.Center()
    frame.Show()
    app.MainLoop()
