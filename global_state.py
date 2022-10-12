# EasyGui version 0.97
# Copyright (c) 2014, Stephen Raymond Ferg
# All rights reserved.

"""

.. moduleauthor:: easygui developers and Stephen Raymond Ferg
.. default-domain:: py
.. highlight:: python

Version |release|
"""

# Starting and global variables

window_position = "+500+250"

def getWinFonts():
    """Try to get a nice font on Windows as default, return first font or Courier if none found"""
    fonts=[]
    try:
        fonts.append("Liberation Mono")
        fonts.append("DejaVu Sans Mono")
        fonts.append("Cousine")
        fonts.append("Lucida Console")
        fonts.append("PT Mono")
        fonts.append("Fira Mono")
        fonts.append("Ubuntu Mono")
    except:
        pass
    fonts.append("Courier New")
    return fonts

PROPORTIONAL_FONT_FAMILY = ("Calibri", "Arial", "MS", "Sans", "Serif")
MONOSPACE_FONT_FAMILY = getWinFonts()[0]

PROPORTIONAL_FONT_SIZE = 11
# a little smaller, because it is more legible at a smaller size
MONOSPACE_FONT_SIZE = 11
TEXT_ENTRY_FONT_SIZE = 11  # a little larger makes it easier to see

STANDARD_SELECTION_EVENTS = ["Return", "Button-1", "space"]

prop_font_line_length = 62
fixw_font_line_length = 80
num_lines_displayed = 50
default_hpad_in_chars = 40

#boxRoot = None

def bindArrows(widget):
    pass
    #№widget.bind("<Down>", tabRight)
    #widget.bind("<Up>", tabLeft)

    #widget.bind("<Right>", tabRight)
    #widget.bind("<Left>", tabLeft)

def tabRight(event):
    if event!=None:
        boxRoot.event_generate("<Tab>")


def tabLeft(event):
    if event != None:
        boxRoot.event_generate("<Shift-Tab>")