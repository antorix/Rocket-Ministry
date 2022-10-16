# EasyGui version 0.97
# Copyright (c) 2014, Stephen Raymond Ferg
# All rights reserved.

"""

.. moduleauthor:: easygui developers and Stephen Raymond Ferg
.. default-domain:: py
.. highlight:: python

"""

# Starting and global variables

window_size = ""# "500x500"
window_position = ""# "+500+250"

def saveWindowPosition(box):
    with open("winpos.ini", "w") as file:
        geom = box.geometry()
        window_position = '+' + geom.split('+', 1)[1]
        window_size = geom[0: geom.index("+")]
        file.write(window_size)
        file.write(window_position)

PROPORTIONAL_FONT_FAMILY = ("Calibri", "Arial", "MS", "Sans", "Serif")
MONOSPACE_FONT_FAMILY = "Liberation Mono"#, "DejaVu Sans Mono", "Cousine", "Lucida Console", "PT Mono",\
                         #"Fira Mono", "Ubuntu Mono", "Courier New")#getWinFonts()[0]

PROPORTIONAL_FONT_SIZE = 11
MONOSPACE_FONT_SIZE = 11
TEXT_ENTRY_FONT_SIZE = 11  # a little larger makes it easier to see

STANDARD_SELECTION_EVENTS = ["Return", "Button-1", "space"]

prop_font_line_length = 62
fixw_font_line_length = 80
num_lines_displayed = 50
default_hpad_in_chars = 40

inactive_background = "grey98"