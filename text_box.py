"""

.. moduleauthor:: easygui developers and Stephen Raymond Ferg
.. default-domain:: py
.. highlight:: python

Version |release|
"""


import sys

import global_state
#import os

import tkinter as tk  # python 3
import tkinter.font as tk_Font
from tkinter import ttk
from fillable_box import __fillablebox

def textbox(msg="", title=" ", text="",
            codebox=False, callback=None, run=True, positive=None, neutral=None, negative=None):
    """ Display a message and a text to edit

    Parameters
    ----------
    msg : string
        text displayed in the message area (instructions...)
    title : str
        the window title
    text: str, list or tuple
        text displayed in textAreas (editable)
    codebox: bool
        if True, don't wrap and width is set to 80 chars
    callback: function
        if set, this function will be called when OK is pressed
    run: bool
        if True, a box object will be created and returned, but not run

    Returns
    -------
    None
        If cancel is pressed
    str
        If OK is pressed returns the contents of textArea

    """

    tb = TextBox(msg=msg, title=title, text=text,
                 codebox=codebox, callback=callback, positive=positive, neutral=neutral, negative=negative)
    if not run:
        return tb
    else:
        reply = tb.run()
        return reply


class TextBox(object):

    """ Display a message and a text to edit

    This object separates user from ui, defines which methods can
    the user invoke and which properties can he change.

    It also calls the ui in defined ways, so if other gui
    library can be used (wx, qt) without breaking anything for the user.
    """

    def __init__(self, msg, title, text, codebox, callback, positive, neutral, negative):
        """ Create box object

        Parameters
        ----------
        msg : string
            text displayed in the message area (instructions...)
        title : str
            the window title
        text: str, list or tuple
            text displayed in textAres (editable)
        codebox: bool
            if True, don't wrap and width is set to 80 chars
        callback: function
            if set, this function will be called when OK is pressed

        Returns
        -------
        object
            The box object
        """
        self.positive = positive
        self.neutral = neutral
        self.negative = negative
        self.callback = callback
        self.ui = GUItk(msg, title, text, codebox, self.callback_ui, positive=positive, neutral=neutral, negative=negative)
        self.text = text

        #self.padx = self.pady = 5

        #self.ipady = self.ipadx = 5


    def run(self):
        """ Start the ui """
        self.ui.run()
        self.ui = None
        return self._text

    def stop(self):
        """ Stop the ui """
        self.ui.stop()

    def callback_ui(self, ui, command, text):
        """ This method is executed when ok, cancel, or x is pressed in the ui.
        """
        if command == 'update':  # OK was pressed
            self._text = text
            if self.callback:
                # If a callback was set, call main process
                self.callback(self)
            else:
                self.stop()
        elif command == 'x':
            self.stop()
            self._text = None
        elif command == 'neutral':
            self.stop()
            self._text = 'neutral'
        elif command == 'cancel':
            self.stop()
            self._text = None

    # methods to change properties --------------
    @property
    def text(self):
        """Text in text Area"""
        return self._text

    @text.setter
    def text(self, text):
        self._text = self.to_string(text)
        self.ui.set_text(self._text)

    @text.deleter
    def text(self):
        self._text = ""
        self.ui.set_text(self._text)

    @property
    def msg(self):
        """Text in msg Area"""
        return self._msg

    @msg.setter
    def msg(self, msg):
        self._msg = self.to_string(msg)
        self.ui.set_msg(self._msg)

    @msg.deleter
    def msg(self):
        self._msg = ""
        self.ui.set_msg(self._msg)

    # Methods to validate what will be sent to ui ---------

    def to_string(self, something):
        try:
            basestring  # python 2
        except NameError:
            basestring = str  # Python 3

        if isinstance(something, basestring):
            return something
        try:
            text = "".join(something)  # convert a list or a tuple to a string
        except:
            textbox(
                "Exception when trying to convert {} to text in self.textArea"
                .format(type(something)))
            sys.exit(16)
        return text


class GUItk(object):

    """ This is the object that contains the tk root object"""

    def __init__(self, msg, title, text, codebox, callback, positive, neutral, negative):

        """ Create ui object

        Parameters
        ----------
        msg : string
            text displayed in the message area (instructions...)
        title : str
            the window title
        text: str, list or tuple
            text displayed in textAres (editable)
        codebox: bool
            if True, dont wrap and width is set to 80 chars
        callback: function
            if set, this function will be called when OK is pressed

        Returns
        -------
        object
            The ui object
        """

        self.callback = callback

        self.positive = positive

        self.neutral = neutral

        self.negative = negative

        self.padx = 5

        self.pady = 7

        self.ipady = 5

        self.ipadx = 5

        self.boxRoot = tk.Tk()
        self.boxFont = tk_Font.Font(
             family=global_state.PROPORTIONAL_FONT_FAMILY,
             size=15)

        wrap_text = codebox
        if wrap_text:
            self.boxFont = tk_Font.nametofont("TkTextFont")
            self.width_in_chars = global_state.prop_font_line_length
        else:
            self.boxFont = tk_Font.nametofont("TkFixedFont")
            self.width_in_chars = global_state.fixw_font_line_length

        # default_font.configure(size=global_state.PROPORTIONAL_FONT_SIZE)

        self.configure_root(title)

        #self.create_msg_widget(msg)

        self.create_buttons_frame()

        self.create_text_area(wrap_text)

        from os import name
        #if name == "nt":
        #    self.boxRoot.iconbitmap('icon.ico')

        if self.positive != None:
            self.create_ok_button()

        if self.neutral!=None and self.neutral!="Очист.":
            self.create_neutral_button()

        if self.negative != None:
            self.create_cancel_button()

    # Run and stop methods ---------------------------------------

    def run(self):
        self.boxRoot.mainloop()
        self.boxRoot.destroy()

    def stop(self):
        # Get the current position before quitting
        self.get_pos()
        self.boxRoot.quit()

    # Methods to change content ---------------------------------------

    def set_msg(self, msg):
        self.messageArea.config(state=tk.NORMAL)
        self.messageArea.delete(1.0, tk.END)
        self.messageArea.insert(tk.END, msg)
        self.messageArea.config(state=tk.DISABLED)
        # Adjust msg height
        #self.messageArea.update()
        numlines = self.get_num_lines(self.messageArea)
        self.set_msg_height(numlines)
        self.messageArea.update()

    def set_msg_height(self, numlines):
        self.messageArea.configure(height=numlines)

    def get_num_lines(self, widget):
        end_position = widget.index(tk.END)  # '4.0'
        end_line = end_position.split('.')[0]  # 4
        return int(end_line) + 1  # 5

    def set_text(self, text):
        self.textArea.delete(1.0, tk.END)
        self.textArea.insert(tk.END, text, "normal")
        if self.positive==None:
            self.textArea.config(state=tk.DISABLED, background=global_state.inactive_background)
        self.textArea.focus_force()


    def set_pos(self, pos):
        self.boxRoot.geometry(pos)

    def get_pos(self):
        # The geometry() method sets a size for the window and positions it on
        # the screen. The first two parameters are width and height of
        # the window. The last two parameters are x and y screen coordinates.
        # geometry("250x150+300+300")
        geom = self.boxRoot.geometry()  # "628x672+300+200"
        global_state.window_position = '+' + geom.split('+', 1)[1]
        global_state.window_size = geom[0: geom.index("+")]

    def get_text(self):
        return self.textArea.get(0.0, 'end-1c')

    # Methods executing when a key is pressed -------------------------------
    def x_pressed(self):
        self.callback(self, command='x', text=self.get_text())

    def ok_button_pressed(self, event):
        self.callback(self, command='update', text=self.get_text())

    def cancel_pressed(self, event):
        self.get_pos()
        global_state.saveWindowPosition(self.boxRoot)
        self.callback(self, command='cancel', text=self.get_text())

    def neutral_button_pressed(self, event):
        self.callback(self, command='neutral', text="neutral")

    # Auxiliary methods -----------------------------------------------
    def calc_character_width(self):
        char_width = self.boxFont.measure('W')
        return char_width

    # Initial configuration methods ---------------------------------------
    # These ones are just called once, at setting.

    def configure_root(self, title):

        self.boxRoot.title(title)

        self.set_pos(global_state.window_size + global_state.window_position)

        # Quit when x button pressed
        #self.boxRoot.protocol('WM_DELETE_WINDOW', self.x_pressed)
        def exit():
            global_state.saveWindowPosition(self.boxRoot)
            import sys
            sys.exit(0)
        self.boxRoot.protocol('WM_DELETE_WINDOW', exit)
        self.boxRoot.bind("<Escape>", self.cancel_pressed)
        #from os import name
        #if name == "nt":
        #    self.boxRoot.iconbitmap('icon.ico')

    def create_msg_widget(self, msg):

        if msg is None:
            msg = ""

        self.msgFrame = tk.Frame(
            self.boxRoot,
            padx=self.padx * self.calc_character_width(),
        )
        self.messageArea = tk.Text(
            self.msgFrame,
            width=10,#self.width_in_chars,
            state=tk.DISABLED,
            padx=self.padx,#(global_state.default_hpad_in_chars) *
            #self.calc_character_width(),
            pady=self.padxy,#global_state.default_hpad_in_chars *
            #self.calc_character_width(),
            wrap=tk.WORD
        )
        #self.set_msg(msg)

        #self.msgFrame.pack(side=tk.TOP, expand=1, fill='both')

        #self.messageArea.pack(side=tk.TOP, expand=1, fill='both')

    def create_text_area(self, wrap_text):
        """
        Put a textArea in the top frame
        Put and configure scrollbars
        """

        self.textFrame = tk.Frame(
            self.boxRoot,
            padx=self.padx+2,
            pady=0#self.pady
        )

        self.textFrame.pack(side=tk.BOTTOM)
        # self.textFrame.grid(row=1, column=0, sticky=tk.EW)

        self.textArea = tk.Text(
            self.textFrame,
            padx=self.padx,#global_state.default_hpad_in_chars * self.calc_character_width(),
            pady=self.pady,#global_state.default_hpad_in_chars * self.calc_character_width(),
            height=500,#global_state.TextBoxHeight,  # lines                     # высота текстового окна
            width=500,#global_state.TextBoxWidth,   # chars of the current font # ширина текстового окна
            takefocus=1
        )

        self.textArea.configure(wrap=tk.WORD)
        self.textArea.configure(
            font=(global_state.MONOSPACE_FONT_FAMILY, global_state.MONOSPACE_FONT_SIZE)
        )

        # some simple keybindings for scrolling
        self.boxRoot.bind("<Next>", self.textArea.yview_scroll(1, tk.PAGES))
        self.boxRoot.bind(
            "<Prior>", self.textArea.yview_scroll(-1, tk.PAGES))

        self.boxRoot.bind("<Right>", self.textArea.xview_scroll(1, tk.PAGES))
        self.boxRoot.bind("<Left>", self.textArea.xview_scroll(-1, tk.PAGES))

        self.boxRoot.bind("<Down>", self.textArea.yview_scroll(1, tk.UNITS))
        self.boxRoot.bind("<Up>", self.textArea.yview_scroll(-1, tk.UNITS))

        # add a vertical scrollbar to the frame
        rightScrollbar = tk.Scrollbar(
            self.textFrame, orient=tk.VERTICAL, command=self.textArea.yview)
        self.textArea.configure(yscrollcommand=rightScrollbar.set)

        # add a horizontal scrollbar to the frame
        bottomScrollbar = ttk.Scrollbar(
            self.textFrame, orient=tk.HORIZONTAL, command=self.textArea.xview)
        self.textArea.configure(xscrollcommand=bottomScrollbar.set)

        # pack the textArea and the scrollbars.  Note that although
        # we must define the textArea first, we must pack it last,
        # so that the bottomScrollbar will be located properly.

        # Note that we need a bottom scrollbar only for code.
        # Text will be displayed with wordwrap, so we don't need to have
        # a horizontal scroll for it.

        if not wrap_text:
            bottomScrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        rightScrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.textArea.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

    def create_buttons_frame(self):

        self.buttonsFrame = tk.Frame(self.boxRoot, takefocus=1)
        self.buttonsFrame.pack(side=tk.TOP, expand=tk.YES, fill="both")

    def create_ok_button(self):
        # put the buttons in the buttonsFrame
        self.okButton = ttk.Button(
            self.buttonsFrame, takefocus=tk.YES, text=self.positive)
        self.okButton.pack(
            expand=tk.YES, fill="both", side=tk.LEFT, padx=self.padx,
            pady=self.pady, ipady=self.ipady, ipadx=self.ipadx)

        # for the commandButton, bind activation events to the activation event
        # handler
        self.okButton.bind("<Return>", self.ok_button_pressed)
        self.okButton.bind("<Button-1>", self.ok_button_pressed)
        self.okButton.focus_force()

    def create_cancel_button(self):
        # put the buttons in the buttonsFrame
        self.cancelButton = ttk.Button(
            self.buttonsFrame, takefocus=tk.YES, text=self.negative + " [Escape]")
        self.cancelButton.pack(
            expand=tk.YES, fill="both", side=tk.RIGHT, padx=self.padx,
            pady=self.pady, ipady=self.ipady, ipadx=self.ipadx)

        # for the commandButton, bind activation events to the activation event
        # handler
        self.cancelButton.bind("<Return>", self.cancel_pressed)
        self.cancelButton.bind("<Button-1>", self.cancel_pressed)
        self.cancelButton.bind("<Escape>", self.cancel_pressed)

    def create_neutral_button(self):
        # put the buttons in the buttonsFrame
        self.neutralButton = ttk.Button(
            self.buttonsFrame, takefocus=1, text=self.neutral)
        self.neutralButton.pack(
            expand=tk.NO, side=tk.RIGHT, padx=self.padx, pady=self.pady, ipady=self.ipady,
            ipadx=self.ipadx)

        # for the commandButton, bind activation events to the activation event
        # handler
        self.neutralButton.bind("<Return>", self.neutral_button_pressed)
        self.neutralButton.bind("<Button-1>", self.neutral_button_pressed)

# -------------------------------------------------------------------
# enterbox
# -------------------------------------------------------------------
def enterbox(msg="", title=" ", default="",
             strip=True, image=None, root=None, neutral=None):
    """
    Show a box in which a user can enter some text.

    You may optionally specify some default text, which will appear in the
    enterbox when it is displayed.

    Example::

        reply = enterbox(....)
        if reply:
            ...
        else:
            ...

    :param str msg: the msg to be displayed.
    :param str title: the window title
    :param str default: value returned if user does not change it
    :param bool strip: If True, the return value will have
      its whitespace stripped before being returned
    :return: the text that the user entered, or None if he cancels
      the operation.
    """
    result = __fillablebox(
        msg, title, default=default, mask=None, image=image, root=root, neutral=neutral)
    if result and strip:
        result = result.strip()
    return result


def passwordbox(msg="Введите пароль", title=" ", default="",
                image=None, root=None):
    """
    Show a box in which a user can enter a password.
    The text is masked with asterisks, so the password is not displayed.

    :param str msg: the msg to be displayed.
    :param str title: the window title
    :param str default: value returned if user does not change it
    :return: the text that the user entered, or None if he cancels
      the operation.
    """
    return __fillablebox(msg, title, default, mask="*",
                         image=image, root=root, neutral=None)



