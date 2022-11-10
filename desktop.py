#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
EasyGUI
.. moduleauthor:: easygui developers and Stephen Raymond Ferg
.. default-domain:: py
.. highlight:: python
Modified for Rocket Ministry (https://github.com/antorix/rocket-ministry)
"""

import sys
import tkinter as tk
import tkinter.font as tk_Font
from tkinter import ttk
import tkinter.filedialog as tk_FileDialog
import homepage
import os
import dialogs
import _thread

def getFileDialogTitle(msg, title):
    """
    Create nicely-formatted string based on arguments msg and title
    :param msg: the msg to be displayed
    :param title: the window title
    :return: None
    """
    if msg and title:
        return "%s - %s" % (title, msg)
    if msg and not title:
        return str(msg)
    if title and not msg:
        return str(title)
    return None  # no message and no title

def textbox(msg="", title=" ", text="", doublesize=False,
            codebox=False, callback=None, run=True, disabled=False, positive=None, neutral=None, negative=None):
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

    tb = TextBox(msg=msg, title=title, text=text, disabled=disabled, doublesize=doublesize,
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

    def __init__(self, msg, title, text, codebox, callback, disabled, doublesize, positive, neutral, negative):
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
        self.doublesize = doublesize
        self.ui = GUItk(msg, title, text, codebox, self.callback_ui, disabled, doublesize, positive=positive, neutral=neutral, negative=negative)
        self.text = text

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

        if isinstance(something, str):
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

    def __init__(self, msg, title, text, codebox, callback, disabled, doublesize, positive, neutral, negative):

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
        self.title = title
        self.msg = msg
        self.padx = dialogs.GlobalPadX
        self.pady = dialogs.GlobalPadY
        self.ipadx = dialogs.SimpleButtonSizeX  # 10
        self.ipady = dialogs.SimpleButtonSizeY  # 5
        self.disabled = disabled
        self.doublesize = doublesize
        self.boxRoot = tk.Toplevel(master=dialogs.MainGUI.root())
        try:
            self.boxRoot.grab_set()
        except:
            pass
        self.boxFont = tk_Font.Font(
             family=dialogs.PROPORTIONAL_FONT_FAMILY,
             size=15)
        wrap_text = codebox
        if wrap_text:
            self.boxFont = tk_Font.nametofont("TkTextFont")
            self.width_in_chars = dialogs.prop_font_line_length
        else:
            self.boxFont = tk_Font.nametofont("TkFixedFont")
            self.width_in_chars = dialogs.fixw_font_line_length

        if title[1] == " ":
            self.configure_root(title[2:])
        else:
            self.configure_root(title)

        self.create_msg_widget(msg)

        self.create_buttons_frame()

        self.create_text_area(wrap_text)

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
        #self.get_pos()
        self.boxRoot.quit()

    # Methods to change content ---------------------------------------

    def get_num_lines(self, widget):
        end_position = widget.index(tk.END)  # '4.0'
        end_line = end_position.split('.')[0]  # 4
        return int(end_line) + 1  # 5

    def set_text(self, text):
        self.textArea.delete(1.0, tk.END)
        self.textArea.insert(tk.END, text, "normal")
        if self.disabled == True:
            self.textArea.config(state=tk.DISABLED, background=dialogs.inactive_background, takefocus=0)
        self.textArea.focus_force()

    def set_pos(self, pos):
        self.boxRoot.geometry(pos)

    def get_text(self):
        if self.positive!=None and "Сохран" in self.positive:
            return self.textArea.get(0.0, 'end-1c')
        else:
            return "positive"

    # Methods executing when a key is pressed -------------------------------
    def x_pressed(self):
        self.callback(self, command='x', text=self.get_text())

    def ok_button_pressed(self, event=None):
        self.callback(self, command='update', text=self.get_text())

    def cancel_pressed(self, event=None):
        #self.get_pos()
        #dialogs.saveWindowPosition(self.boxRoot)
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

        self.boxRoot.title("  Rocket Ministry")

        self.set_pos(dialogs.miniwindow2 + dialogs.window_position)

        if self.doublesize==False:
            self.set_pos(dialogs.miniwindow2 + geomShift(dialogs.window_position))
        else:
            self.set_pos(dialogs.miniwindow3 + geomShift(dialogs.window_position))

        # Quit when x button pressed
        self.boxRoot.protocol('WM_DELETE_WINDOW', self.x_pressed)
        self.boxRoot.bind("<Escape>", self.cancel_pressed)
        #self.boxRoot.wm_iconphoto(False, self.img[33]) # иконка
        self.boxRoot.bind_class("Text", "<3>", self.contextMenu)

    def create_msg_widget(self, msg):

        self.msgFrame = tk.Frame(self.boxRoot, takefocus=0) # дублирование title - textbox
        self.msgFrame.pack(side=tk.TOP, expand=1, fill='both')
        if self.title[1] == " ":
            text = self.title[1:]
        else:
            text = self.title
        if self.msg.strip() != "" and self.disabled == False:
            text = text + " | " + self.msg
        self.messageArea = tk.Label(self.msgFrame, text=text, fg=dialogs.TitleColor, takefocus=0)
        self.messageArea.pack(side=tk.TOP, expand=1, padx=self.padx, pady=self.pady, fill='both')

    def create_text_area(self, wrap_text):
        """
        Put a textArea in the top frame
        Put and configure scrollbars
        """

        self.textFrame = tk.Frame(self.boxRoot, takefocus=0)
        self.textFrame.pack(side=tk.BOTTOM, padx=self.padx, pady=self.pady)

        self.textArea = tk.Text(
            self.textFrame,
            padx=dialogs.GlobalPadX,#default_hpad_in_chars * self.calc_character_width(),
            pady=dialogs.GlobalPadY,#default_hpad_in_chars * self.calc_character_width(),
            height=500,#TextBoxHeight,  # lines                     # высота текстового окна
            width=500,#TextBoxWidth,   # chars of the current font # ширина текстового окна
            takefocus=0,
            font = (dialogs.PROPORTIONAL_FONT_FAMILY, dialogs.PROPORTIONAL_FONT_SIZE)
        )

        self.textArea.configure(wrap=tk.WORD)

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

        self.textArea.bind("<Control-s>", self.ok_button_pressed)
        self.textArea.bind("<Shift-Return>", self.ok_button_pressed)

        # pack the textArea and the scrollbars.  Note that although
        # we must define the textArea first, we must pack it last,
        # so that the bottomScrollbar will be located properly.

        # Note that we need a bottom scrollbar only for code.
        # Text will be displayed with wordwrap, so we don't need to have
        # a horizontal scroll for it.

        #if not wrap_text:
        #    bottomScrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        rightScrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.textArea.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

    def create_buttons_frame(self):
        self.buttonsFrame = tk.Frame(self.boxRoot, takefocus=0)
        self.buttonsFrame.pack(side=tk.BOTTOM, expand=tk.YES, fill="both", padx=self.padx, pady=self.pady)
        self.buttonsFrame.columnconfigure(0, weight=10)
        self.buttonsFrame.columnconfigure(1, weight=10)
        self.buttonsFrame.columnconfigure(2, weight=10)

    def create_ok_button(self):
        # put the buttons in the buttonsFrame

        if self.disabled==False:
            text = self.positive + " [Shift-Enter]"
        elif self.positive != "OK" and self.positive != "Да":
            text = self.positive[2:]
        else:
            text = self.positive
        self.okButton = ttk.Button(
            self.buttonsFrame, takefocus=tk.YES, compound="left", text=text)#image)
        self.okButton.grid(row=0, column=0, sticky="w", padx=self.padx, pady=self.pady, ipadx=self.ipadx, ipady=self.ipady)#(expand=tk.YES, side=tk.LEFT, padx=self.padx, ipady=self.ipady, ipadx=self.ipadx)

        # for the commandButton, bind activation events to the activation event
        # handler
        self.okButton.bind("<Return>", self.ok_button_pressed)
        self.okButton.bind("<Button-1>", self.ok_button_pressed)
        self.okButton.focus_force()

    def create_neutral_button(self):
        # put the buttons in the buttonsFrame
        self.neutralButton = ttk.Button(self.buttonsFrame, takefocus=1, text=self.neutral[2:])
        if self.positive!=None:
            column=1
            sticky="n"
        else:
            column=0
            sticky="w"
        self.neutralButton.grid(row=0, column=column, sticky=sticky, padx=self.padx, pady=self.pady, ipadx=self.ipadx, ipady=self.ipady)#pack(expand=tk.NO, side=tk.LEFT, padx=self.padx, pady=self.pady, ipady=self.ipady,ipadx=self.ipadx)

        # for the commandButton, bind activation events to the activation event
        # handler
        self.neutralButton.bind("<Return>", self.neutral_button_pressed)
        self.neutralButton.bind("<Button-1>", self.neutral_button_pressed)

    def create_cancel_button(self):
        # put the buttons in the buttonsFrame
        #if self.negative=="Отмена":
        #    self.negative += " [Esc]"
        self.cancelButton = ttk.Button(self.buttonsFrame, takefocus=tk.YES, compound="left", text=self.negative)
        self.cancelButton.grid(row=0, column=2, sticky="e", padx=self.padx, pady=self.pady, ipadx=self.ipadx, ipady=self.ipady)#pack(expand=tk.YES, side=tk.LEFT, padx=self.padx,ipady=self.ipady, ipadx=self.ipadx)

        # for the commandButton, bind activation events to the activation event
        # handler
        self.cancelButton.bind("<Return>", self.cancel_pressed)
        self.cancelButton.bind("<Button-1>", self.cancel_pressed)
        self.cancelButton.bind("<Escape>", self.cancel_pressed)

    def contextMenu(self, e=None):
        """ Контекстное меню. Создается из внешней функции getMenu, универсальной для всех виджетов """
        dialogs.getMenu(box=self.boxRoot, e=e)

def dialogCheck():
    return homepage.cycle()

def enterbox(msg="", title=" ", default="", form="",
             strip=True, mono=False, height=5, neutral=None):
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
        msg, title, default=default, mask=None, mono=mono, form=form, height=height, neutral=neutral)
    if result and strip:
        result = result.strip()
    return result

def libbox(msg="", title="Rocket Ministry", default="", mono=False, height=5, root=None, lib=True):
    """

    :param str msg: the msg to be displayed.
    :param str title: the window title
    :param str default: value returned if user does not change it
    :return: the text that the user entered, or None if he cancels
      the operation.
    """
    return __fillablebox(msg, title, default, mask="*", mono=mono, height=height, neutral=None, lib=lib)

boxRoot = None
entryWidget = None
__enterboxText = ''
__enterboxDefaultText = ''
cancelButton = None
nButton = None
okButton = None

def __fillablebox(msg, title="", default="", mask=None, form="", mono=False, height=5, neutral=None, lib=False):
    """
    Show a box in which a user can enter some text.
    You may optionally specify some default text, which will appear in the
    enterbox when it is displayed.
    Returns the text that the user entered, or None if he cancels the operation.
    """
    global boxRoot, __enterboxText, __enterboxDefaultText
    global cancelButton, nButton, entryWidget, okButton

    if title is None:
        title = ""
    if default is None:
        default = ""
    __enterboxDefaultText = default
    __enterboxText = __enterboxDefaultText

    #root.withdraw()
    root = dialogs.MainGUI.root()
    boxRoot = tk.Toplevel(master = root)
    try:
        boxRoot.grab_set()
    except:
        pass
    boxRoot.withdraw()

    boxRoot.protocol('WM_DELETE_WINDOW', __enterboxCancel)
    boxRoot.title("Rocket Ministry")

    if lib==True:
        height = 1
        boxRoot.geometry("270x140" + geomShift(dialogs.window_position))
    else:
        height=height
        if form!="porchText":
            pos = dialogs.miniwindow1 + geomShift(dialogs.window_position)
        else:
            pos = dialogs.miniwindow3 + geomShift(dialogs.window_position)
        boxRoot.geometry(pos)

    boxRoot.bind("<Escape>", __enterboxCancel)

    mainFrame = tk.Frame(boxRoot)
    mainFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    bottomFrame = tk.Frame(boxRoot)
    bottomFrame.pack(side=tk.BOTTOM, fill=tk.BOTH)

    # Верхняя строка (дублирование title) - fillablebox
    msgFrame = tk.Frame(mainFrame)
    msgFrame.pack(side=tk.TOP, fill='both')
    if title.strip()=="":
        text = None
    elif title[1]==" ":
        text = title[1:]
    else:
        text = title
    messageArea = tk.Label(msgFrame, text=text, fg=dialogs.TitleColor)
    if text!=None:
        messageArea.pack(side=tk.TOP, expand=1, fill='both', padx=3)

    # ------------- define the messageFrame ---------------------------------
    messageFrame = tk.Frame(master=mainFrame)
    messageFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # ------------- define the entryFrame ---------------------------------
    entryFrame = ttk.Frame(master=mainFrame)
    entryFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # ------------- define the buttonsFrame ---------------------------------
    buttonsFrame = ttk.Frame(master=bottomFrame)
    buttonsFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # -------------------- the msg widget ----------------------------
    #messageWidget = tk.Message(messageFrame, width="4i", text=msg)

    if form=="porchText":
        height=18

    messageWidget = tk.Text(
            messageFrame,
            padx=5,
            pady=5,
            height=height,
            width=200,
            background=dialogs.inactive_background,
            font=(dialogs.PROPORTIONAL_FONT_FAMILY, dialogs.PROPORTIONAL_FONT_SIZE),
            wrap=tk.WORD,
        )
    messageWidget.delete(1.0, tk.END)
    messageWidget.insert(tk.END, msg)
    messageWidget.config(state=tk.DISABLED)
    messageWidget.pack(side=tk.TOP, expand=1, fill=tk.BOTH, padx='3m', pady='3m')

    if mono==True:
        messageWidget.config(font = (dialogs.MONOSPACE_FONT_FAMILY, dialogs.MONOSPACE_FONT_SIZE))

    # --------- entryWidget ----------------------------------------------
    entryWidget = ttk.Entry(entryFrame, takefocus=1, width=500) # ширина окна текста

    entryWidget.configure(
        font=(dialogs.MONOSPACE_FONT_SIZE, dialogs.TEXT_ENTRY_FONT_SIZE))
    if mask:
        entryWidget.configure(show=mask)

    def contextMenu(e=None):
        """ Контекстное меню. Создается из внешней функции getMenu, универсальной для всех виджетов """
        dialogs.getMenu(box=boxRoot, e=e)

    entryWidget.pack(side=tk.LEFT, padx="5m")
    entryWidget.bind("<Return>", __enterboxGetText)
    entryWidget.bind("<Escape>", __enterboxCancel)
    entryWidget.bind("<Control-Insert>", __enterboxNeutral)
    # put text into the entryWidget
    entryWidget.insert(0, __enterboxDefaultText)
    entryWidget.bind_class("TEntry", "<3>", contextMenu)

    # ------------------ ok button -------------------------------
    okButton = ttk.Button(buttonsFrame, takefocus=1, compound="left", text="OK")#getButton("  OK", img)[0], image=getButton("  OK", img)[1])

    okButton.pack(expand=1, side=tk.LEFT, padx='3m', pady='3m',
                  ipadx=dialogs.SimpleButtonSizeX, ipady=dialogs.SimpleButtonSizeY)

    # for the commandButton, bind activation events to the activation event
    # handler
    commandButton = okButton
    handler = __enterboxGetText
    for selectionEvent in dialogs.STANDARD_SELECTION_EVENTS:
        commandButton.bind("<{}>".format(selectionEvent), handler)

    # ------------------ neutral button -------------------------------
    if neutral!=None:
        if "Детали" in neutral:
            neutral = neutral[2:]
        nButton = ttk.Button(buttonsFrame, takefocus=1, compound="left", text=neutral)

        if neutral!=None and neutral!="Очист.":
            nButton.pack(expand=1, side=tk.LEFT, padx='3m', pady='3m',
                         ipadx=dialogs.SimpleButtonSizeX, ipady=dialogs.SimpleButtonSizeY)

        # for the commandButton, bind activation events to the activation event
        # handler
        commandButton = nButton
        handler = __enterboxNeutral
        for selectionEvent in dialogs.STANDARD_SELECTION_EVENTS:
            commandButton.bind("<{}>".format(selectionEvent), handler)

    # ------------------ cancel button -------------------------------
    cancelButton = ttk.Button(buttonsFrame, takefocus=1, compound="left", text="Отмена")

    cancelButton.pack(expand=1, side=tk.RIGHT, padx='3m', pady='3m',
                      ipadx=dialogs.SimpleButtonSizeX, ipady=dialogs.SimpleButtonSizeY)

    # for the commandButton, bind activation events to the activation event
    # handler
    commandButton = cancelButton
    handler = __enterboxCancel
    for selectionEvent in dialogs.STANDARD_SELECTION_EVENTS:
        commandButton.bind("<{}>".format(selectionEvent), handler)

    #create_footer(boxRoot)

    # ------------------- time for action! -----------------

    boxRoot.deiconify()
    entryWidget.focus_force()  # put the focus on the entryWidget
    boxRoot.mainloop()  # run it!

    # -------- after the run has completed ----------------------------------

    root.deiconify()
    boxRoot.destroy()  # button_click didn't destroy boxRoot, so we do it now
    return __enterboxText

def __enterboxQuit():
    return __enterboxCancel(None)

def __enterboxCancel(event=None):
    global __enterboxText

    __enterboxText = None
    boxRoot.quit()

def __enterboxGetText(event):
    global __enterboxText

    __enterboxText = entryWidget.get()
    boxRoot.quit()

def __enterboxNeutral(event):
    global __enterboxText

    __enterboxText = "neutral"
    boxRoot.quit()

def __enterboxRestore(event):
    global entryWidget

    entryWidget.delete(0, len(entryWidget.get()))
    entryWidget.insert(0, __enterboxDefaultText)

def fileopenbox(msg=None, title=None, default='*', filetypes=None, multiple=False):
    """ A dialog to get a file name. """

    localRoot = tk.Tk()
    localRoot.withdraw()

    initialbase, initialfile, initialdir, filetypes = fileboxSetup(
        default, filetypes)

    # ------------------------------------------------------------
    # if initialfile contains no wildcards; we don't want an
    # initial file. It won't be used anyway.
    # Also: if initialbase is simply "*", we don't want an
    # initialfile; it is not doing any useful work.
    # ------------------------------------------------------------
    if (initialfile.find("*") < 0) and (initialfile.find("?") < 0):
        initialfile = None
    elif initialbase == "*":
        initialfile = None

    func = tk_FileDialog.askopenfilenames if multiple else tk_FileDialog.askopenfilename
    ret_val = func(parent=localRoot,
                   title=getFileDialogTitle(msg, title),
                   initialdir=initialdir, initialfile=initialfile,
                   filetypes=filetypes
                   )

    if multiple:
        f = [os.path.normpath(x) for x in localRoot.tk.splitlist(ret_val)]
    else:
        f = os.path.normpath(ret_val)

    localRoot.destroy()

    if not f:
        return None
    return f

def fileboxSetup(default, filetypes):
    if not default:
        default = os.path.join(".", "*")
    initialdir, initialfile = os.path.split(default)
    if not initialdir:
        initialdir = "."
    if not initialfile:
        initialfile = "*"
    initialbase, initialext = os.path.splitext(initialfile)
    initialFileTypeObject = FileTypeObject(initialfile)

    allFileTypeObject = FileTypeObject("*")
    ALL_filetypes_was_specified = False

    if not filetypes:
        filetypes = list()
    filetypeObjects = list()

    for filemask in filetypes:
        fto = FileTypeObject(filemask)

        if fto.isAll():
            ALL_filetypes_was_specified = True  # remember this

        if fto == initialFileTypeObject:
            initialFileTypeObject.add(fto)  # add fto to initialFileTypeObject
        else:
            filetypeObjects.append(fto)

    # ------------------------------------------------------------------
    # make sure that the list of filetypes includes the ALL FILES type.
    # ------------------------------------------------------------------
    if ALL_filetypes_was_specified:
        pass
    elif allFileTypeObject == initialFileTypeObject:
        pass
    else:
        filetypeObjects.insert(0, allFileTypeObject)
    # ------------------------------------------------------------------
    # Make sure that the list includes the initialFileTypeObject
    # in the position in the list that will make it the default.
    # This changed between Python version 2.5 and 2.6
    # ------------------------------------------------------------------
    if len(filetypeObjects) == 0:
        filetypeObjects.append(initialFileTypeObject)

    if initialFileTypeObject in (filetypeObjects[0], filetypeObjects[-1]):
        pass
    else:
        filetypeObjects.insert(0, initialFileTypeObject)

    filetypes = [fto.toTuple() for fto in filetypeObjects]

    return initialbase, initialfile, initialdir, filetypes

    # Hotkeys
    if buttons:
        for button_name, button in buttons.items():
            hotkey_pressed = event.keysym
            if event.keysym != event.char:  # A special character
                hotkey_pressed = '<{}>'.format(event.keysym)
            if button['hotkey'] == hotkey_pressed:
                __replyButtonText = button_name
                boxRoot.quit()
                return

    print("Event not understood")

class FileTypeObject:

    def __init__(self, filemask):
        if len(filemask) == 0:
            raise AssertionError('Filetype argument is empty.')

        self.masks = list()

        if isinstance(filemask, str):  # a str or unicode
            self.initializeFromString(filemask)

        elif isinstance(filemask, list):
            if len(filemask) < 2:
                raise AssertionError('Invalid filemask.\n'
                                     + 'List contains less than 2 members: "{}"'.format(filemask))
            else:
                self.name = filemask[-1]
                self.masks = list(filemask[:-1])
        else:
            raise AssertionError('Invalid filemask: "{}"'.format(filemask))

    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False

    def add(self, other):
        for mask in other.masks:
            if mask in self.masks:
                pass
            else:
                self.masks.append(mask)

    def toTuple(self):
        return self.name, tuple(self.masks)

    def isAll(self):
        if self.name == "All files":
            return True
        return False

    def initializeFromString(self, filemask):
        # remove everything except the extension from the filemask
        self.ext = os.path.splitext(filemask)[1]
        if self.ext == "":
            self.ext = ".*"
        if self.ext == ".":
            self.ext = ".*"
        self.name = self.getName()
        self.masks = ["*" + self.ext]

    def getName(self):
        e = self.ext
        file_types = {".*": "All", ".txt": "Text",
                      ".py": "Python", ".pyc": "Python", ".xls": "Excel"}
        if e in file_types:
            return '{} files'.format(file_types[e])
        if e.startswith("."):
            return '{} files'.format(e[1:].upper())
        return '{} files'.format(e.upper())

class CreateToolTip(object):
    """Show tooptips at widgets"""

    def __init__(self, widget, text='widget info', waittime=200):
        self.waittime = waittime  # miliseconds
        self.wraplength = 180  # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event):
        self.schedule(event)

    def leave(self, event):
        self.unschedule()
        self.hidetip()

    def schedule(self, event):
        self.unschedule()
        self.id = self.widget.after(self.waittime, lambda: self.showtip(event))

    def unschedule(self):
        id = self.id
        self.id = None
        if id: self.widget.after_cancel(id)

    def showtip(self, event):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        self.label = tk.Label(self.tw, text=self.text, justify='left',
                              background="#ffffff", relief='solid', borderwidth=1,
                              wraplength=self.wraplength)
        self.label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw: tw.destroy()

    def rewrite(self, text):
        self.text = text

class Splash(tk.Toplevel):
    """Show splash screen"""

    def __init__(self, permission=False, master=None):
        self.permission = permission
        if self.permission == False: return
        self.master = tk.Toplevel()
        self.master["cursor"] = "watch"
        w = 450
        h = 300
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2) - 50
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.master.wm_overrideredirect(True)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(2, weight=1)
        self.imgSplash = tk.PhotoImage(file="images/splash.gif")
        tk.Label(self.master, bd=0, image=self.imgSplash).place(x=0, y=0)
        ttk.Label(self.master, text="Halieus", font="Arial 12 bold italic").grid(column=0, row=0, padx=5, pady=5,
                                                                                 sticky="nw")
        with open("Halieus.pyw", "r", encoding="utf-8") as file: content = [line.rstrip() for line in file]
        ttk.Label(self.master, text="v%s" % content[0][10:], font="Arial 8 italic").grid(column=0, columnspan=2, row=0,
                                                                                         padx=5, pady=7, sticky="ne")
        self.splashText = tk.Label(self.master, fg="white", bg="Teal", font="Arial 8")
        self.splashText.grid(column=1, row=4, sticky="se")
        self.master.update()

    def update(self, text):
        if self.permission == False: return
        self.splashText["text"] = text
        self.master.update()

    def end(self):
        if self.permission == False: return
        self.master.destroy()

class Progress():
    """Show progress bar"""

    def __init__(self, root, text="Подождите…"):
        bgColor = "gray95"
        self.form = tk.Toplevel(bg=bgColor, bd=1, relief='solid', borderwidth=1)
        width = 200
        height = 50
        h = root.master.winfo_height()
        w = root.master.winfo_width()
        x = root.master.winfo_x() + (w / 2) - (width / 2)
        y = root.master.winfo_y() + (h / 2) - (height / 2)
        self.form.geometry('%dx%d+%d+%d' % (width, height, x, y))
        self.form.wm_overrideredirect(True)
        tk.Label(self.form, bg=bgColor, text=text).pack()
        self.bar = ttk.Progressbar(self.form)
        self.bar.pack(padx=5, pady=5, fill="both")

        _thread.start_new_thread(self.run, ("Thread-Progress", 1,))

    def run(self, threadName, delay):
        self.bar.start()
        self.form["cursor"] = "watch"
        self.form.update()
        #self.form.focus_force()
        try:
            self.form.grab_set()
        except:
            pass

    def end(self):
        self.form.destroy()

def geomShift(pos=dialogs.window_position):#, shiftx=None, shifty=None, reverse=False):
    """ Сдвиг позиции окна Toplevel """
    pos = pos[1:]
    x = int(pos[ 0 : pos.index("+") ])
    y = int(pos[ pos.index("+") : ])
    return("+%d+%d" % (x+dialogs.ToplevelShiftX, y+dialogs.ToplevelShiftY))