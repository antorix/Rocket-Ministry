#!/usr/bin/python
# -*- coding: utf-8 -*-

import string
import global_state
from global_state import bindArrows
import tkinter as tk
import tkinter.font as tk_Font
from tkinter import ttk

def choicebox(msg="", title="", choices=[], preselect=0,
            positive=None, neutral=None, negative="Назад", callback=None, run=True):
    """
    Present the user with a list of choices.
    return the choice that he selects.

    :param str msg: the msg to be displayed
    :param str title: the window title
    :param list choices: a list or tuple of the choices to be displayed
    :return: List containing choice selected or None if cancelled
    """
    mb = ChoiceBox(msg, title, choices, preselect=preselect,
                   multiple_select=False,
                   positive=positive,
                   neutral=neutral,
                   negative=negative,
                   callback=callback)
    if run:
        reply = mb.run()
        return reply
    else:
        return mb

def multchoicebox(msg="Pick an item", title="", choices=[],
                  preselect=0, callback=None, positive=None, neutral=None, negative=None,
                  run=True):
    """ Same as choicebox, but the user can select many items.

    """
    mb = ChoiceBox(msg, title, choices, preselect=preselect,
                   multiple_select=True,
                   positive=positive,
                   neutral=neutral,
                   callback=callback)
    if run:
        reply = mb.run()
        return reply
    else:
        return mb


class ChoiceBox(object):

    def __init__(self, msg, title, choices, preselect, multiple_select, callback, positive, neutral, negative):

        self.callback = callback

        self.choices = self.to_list_of_str(choices)

        self.ui = GUItk(msg, title, self.choices, preselect, multiple_select,
                        self.callback_ui, neutral=neutral, positive=positive, negative=negative)

        self.positive = positive

        self.neutral = neutral

        self.neutral = negative

    def run(self):
        """ Start the ui """
        self.ui.run()
        self.ui = None
        return self.choices

    def stop(self):
        """ Stop the ui """
        self.ui.stop()

    def callback_ui(self, ui, command, choices):
        """ This method is executed when ok, cancel, or x is pressed in the ui.
        """
        if command == 'update':  # OK was pressed
            self.choices = choices
            if self.callback:
                # If a callback was set, call main process
                self.callback(self)
            else:
                self.stop()
        elif command == 'x':
            self.stop()
            self.choices = None
        elif command == 'cancel':
            self.stop()
            self.choices = None
        elif command == 'neutral':
            self.stop()
            self.choices = 'neutral'
        elif command == 'settings':
            self.stop()
            self.choices = 'settings'
        elif command == 'file':
            self.stop()
            self.choices = 'file'
        elif command == 'report':
            self.stop()
            self.choices = 'report'
        elif command == 'notebook':
            self.stop()
            self.choices = 'notebook'
        elif command == 'exit':
            self.stop()
            self.choices = 'exit'

    # methods to change properties --------------

    @property
    def msg(self):
        """Text in msg Area"""
        return self._msg

    @msg.setter
    def msg(self, msg):
        self.ui.set_msg(msg)

    @msg.deleter
    def msg(self):
        self._msg = ""
        self.ui.set_msg(self._msg)

    # Methods to validate what will be sent to ui ---------

    def to_list_of_str(self, choices):
        # -------------------------------------------------------------------
        # If choices is a tuple, we make it a list so we can sort it.
        # If choices is already a list, we make a new list, so that when
        # we sort the choices, we don't affect the list object that we
        # were given.
        # -------------------------------------------------------------------
        choices = list(choices)

        choices = [str(c) for c in choices]

        #while len(choices) < 2:
        #    choices.append("Add more choices")

        return choices

class GUItk(object):

    """ This object contains the tk root object.
        It draws the window, waits for events and communicates them
        to MultiBox, together with the entered values.

        The position in wich it is drawn comes from a global variable.

        It also accepts commands from Multibox to change its message.
    """

    def __init__(self, msg, title, choices, preselect, multiple_select, callback, positive, neutral, negative):

        self.callback = callback

        self.choices = choices

        self.positive = positive

        self.neutral = neutral

        self.negative = negative

        self.padx = self.pady = 3

        self.ipady = self.ipadx = 5

        self.width_in_chars = global_state.prop_font_line_length
        # Initialize self.selected_choices
        # This is the value that will be returned if the user clicks the close
        # icon
        # self.selected_choices = None

        self.multiple_select = multiple_select

        self.boxRoot = tk.Tk()

        self.boxFont = tk_Font.nametofont("TkTextFont") # getWinFonts()[0] шрифты

        self.config_root(title)

        #self.config_menu() # меню

        self.set_pos(global_state.window_position)  # GLOBAL POSITION

        from os import name
        if name == "nt":
            self.boxRoot.iconbitmap('icon.ico')

        self.create_msg_widget(msg)

        self.create_choicearea()

        self.create_ok_button()

        if self.positive!=None:
            self.create_positive_button()

        if self.neutral!=None:
            self.create_neutral_button()

        if self.negative!=None:
            self.create_cancel_button()

        self.create_special_buttons()

        self.preselect_choice(preselect)

        self.choiceboxWidget.focus_force()

    # Run and stop methods ---------------------------------------

    def run(self):
        self.boxRoot.mainloop()  # run it!
        self.boxRoot.destroy()   # Close the window

    def stop(self):
        # Get the current position before quitting
        self.get_pos()
        self.boxRoot.quit()

    def x_pressed(self):
        self.callback(self, command='x', choices=self.get_choices())

    def cancel_pressed(self, event):
        self.callback(self, command='cancel', choices=self.get_choices())

    def neutral_pressed(self, event):
        self.callback(self, command='neutral', choices="neutral")

    def ok_pressed(self, event):
        self.callback(self, command='update', choices=self.get_choices())

    def positive_pressed(self, event):
        self.callback(self, command='update', choices="positive")

    def menu_pressed(self, event, choice):
        self.callback(self, command=choice, choices=choice)

    def config_menu(self):

        def menuFile():
            self.callback(self, command="file", choices="file")
        def menuReport():
            self.callback(self, command="report", choices="report")
        def menuSettings():
            self.callback(self, command="settings", choices="settings")
        def menuNotebook():
            self.callback(self, command="notebook", choices="notebook")
        def menuExit():
            self.callback(self, command="exit", choices="exit")

        self.menu = tk.Menu(self.boxRoot)
        self.boxRoot.config(menu=self.menu)
        self.filemenu = tk.Menu(self.menu)
        #self.menu.add_cascade(label="Файл", menu=self.filemenu)
        self.menu.add_command(label="Файл", command=menuFile)
        self.menu.add_command(label="Настройки", command=menuSettings)
        self.menu.add_command(label="Отчет", command=menuReport)
        self.menu.add_command(label="Блокнот", command=menuNotebook)
        self.menu.add_command(label="Выход", command=menuExit)
        #self.filemenu.add_command(label="Экспорт", command=menuExport)
        #self.filemenu.add_separator()
        #self.filemenu.add_command(label="Exit", command=self.root.quit)

    # Methods to change content ---------------------------------------

    def set_msg(self, msg):
        self.messageArea.config(state=tk.NORMAL)
        self.messageArea.delete(1.0, tk.END)
        self.messageArea.insert(tk.END, msg)
        self.messageArea.config(state=tk.DISABLED)
        # Adjust msg height
        self.messageArea.update()
        numlines = self.get_num_lines(self.messageArea)
        self.set_msg_height(numlines)
        self.messageArea.update()
        # put the focus on the entryWidget

    def set_msg_height(self, numlines):
        self.messageArea.configure(height=numlines)

    def get_num_lines(self, widget):
        end_position = widget.index(tk.END)  # '4.0'
        end_line = end_position.split('.')[0]  # 4
        return int(end_line) + 1  # 5

    def set_pos(self, pos=None):
        if not pos:
            pos = global_state.window_position
        self.boxRoot.geometry(pos)

    def get_pos(self):
        # The geometry() method sets a size for the window and positions it on
        # the screen. The first two parameters are width and height of
        # the window. The last two parameters are x and y screen coordinates.
        # geometry("250x150+300+300")
        geom = self.boxRoot.geometry()  # "628x672+300+200"
        global_state.window_position = '+' + geom.split('+', 1)[1]

    def preselect_choice(self, preselect):
        if preselect != None:
            self.choiceboxWidget.select_set(preselect)
            self.choiceboxWidget.activate(preselect)

    def get_choices(self):
        choices_index = self.choiceboxWidget.curselection()
        if not choices_index:
            return None
        if self.multiple_select:
            selected_choices = [self.choiceboxWidget.get(index)
                                for index in choices_index]
        else:
            selected_choices = self.choiceboxWidget.get(choices_index)

        return selected_choices

    def return_choice(self, choice):
        return choice

    # Auxiliary methods -----------------------------------------------
    def calc_character_width(self):
        char_width = self.boxFont.measure('W')
        return char_width

    def config_root(self, title):

        #screen_width = self.boxRoot.winfo_screenwidth()
        #screen_height = self.boxRoot.winfo_screenheight()

        self.boxRoot.title(title)
        self.boxRoot.expand = tk.YES

        self.set_pos()

        self.boxRoot.protocol('WM_DELETE_WINDOW', self.x_pressed)
        self.boxRoot.bind('<Any-Key>', self.KeyboardListener)
        self.boxRoot.bind("<Escape>", self.cancel_pressed)

        self.buttonsFrame = tk.Frame(self.boxRoot)
        self.buttonsFrame.pack(side=tk.BOTTOM, expand=tk.YES, pady=self.pady)

    def create_msg_widget(self, msg):

        if msg is None:
            msg = ""

        self.msgFrame = tk.Frame(
            self.boxRoot,
            padx=self.padx * self.calc_character_width(),

        )
        self.messageArea = tk.Text(
            self.msgFrame,
            width=self.width_in_chars,
            state=tk.DISABLED,
            padx=(global_state.default_hpad_in_chars *
                  self.calc_character_width()),
            pady=(global_state.default_hpad_in_chars *
                  self.calc_character_width()),
            wrap=tk.WORD,

        )
        self.set_msg(msg)

        self.msgFrame.pack(side=tk.TOP, expand=1, fill='both')

        self.msgFrame.config(width=500) # ширина окна списка

        #self.messageArea.pack(side=tk.TOP, expand=1, fill='both')

    def create_choicearea(self):

        self.choiceboxFrame = ttk.Frame(master=self.boxRoot)
        self.choiceboxFrame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.YES,
                                 padx=self.padx, pady=self.pady, ipady=self.ipady, ipadx=self.ipadx)

        lines_to_show = min(len(self.choices), 20) # высота окна списка

        # --------  put the self.choiceboxWidget in the self.choiceboxFrame ---
        self.choiceboxWidget = tk.Listbox(self.choiceboxFrame,
                                          height=20,
                                          borderwidth="2m", relief="flat",
                                          bg="white")

        self.choiceboxWidget.configure(
            font=(global_state.MONOSPACE_FONT_FAMILY, global_state.MONOSPACE_FONT_SIZE)
        )

        if self.multiple_select:
            self.choiceboxWidget.configure(selectmode=tk.MULTIPLE)

        # self.choiceboxWidget.configure(font=(global_state.PROPORTIONAL_FONT_FAMILY,
        #                                     global_state.PROPORTIONAL_FONT_SIZE))

        # add a vertical scrollbar to the frame
        rightScrollbar = ttk.Scrollbar(self.choiceboxFrame, orient=tk.VERTICAL,
                                      command=self.choiceboxWidget.yview)
        self.choiceboxWidget.configure(yscrollcommand=rightScrollbar.set)

        # add a horizontal scrollbar to the frame
        bottomScrollbar = tk.Scrollbar(self.choiceboxFrame,
                                       orient=tk.HORIZONTAL,
                                       command=self.choiceboxWidget.xview)
        self.choiceboxWidget.configure(xscrollcommand=bottomScrollbar.set)

        # pack the Listbox and the scrollbars.
        # Note that although we must define
        # the textArea first, we must pack it last,
        # so that the bottomScrollbar will
        # be located properly.

        bottomScrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        rightScrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.choiceboxWidget.pack(
            side=tk.LEFT, padx=self.padx, pady=self.pady, expand=tk.YES, fill=tk.BOTH)

        # Insert choices widgets
        for choice in self.choices:
            self.choiceboxWidget.insert(tk.END, choice)

        # Bind the keyboard events
        self.choiceboxWidget.bind("<Return>", self.ok_pressed)
        self.choiceboxWidget.bind("<Double-Button-1>", self.ok_pressed)
        self.choiceboxWidget.bind("<space>", self.ok_pressed)
        self.choiceboxWidget.bind("<Insert>", self.positive_pressed)
        self.choiceboxWidget.bind("<*>", self.neutral_pressed)
        self.choiceboxWidget.bind("</>", self.positive_pressed)
        self.choiceboxWidget.bind("<BackSpace>", self.cancel_pressed)

    #def create_ok_button(self):
    def create_ok_button(self):
        # put the buttons in the self.buttonsFrame

        okButton = ttk.Button(self.boxRoot, takefocus=tk.YES, text="OK [Enter]")

        bindArrows(okButton)

        #okButton.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx='1m', pady='1m', ipady=1, ipadx=1)
        #okButton.pack(side=tk.TOP, expand=1, fill='both')

        okButton.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES,
                      padx=self.padx, pady=self.pady, ipady=self.ipady, ipadx=self.ipadx)

        # for the commandButton, bind activation events
        okButton.bind("<Return>", self.ok_pressed)
        okButton.bind("<Button-1>", self.ok_pressed)
        okButton.bind("<space>", self.ok_pressed)

    def create_positive_button(self):

        # put the buttons in the self.buttonsFrame
        from icons import icon
        if self.positive=="+": # если плюс, заменяем его на более красивый
            self.positive = "\u2795 Добавить [Insert]"
        elif self.positive==icon("down"):
            self.positive += " [/]"

        positiveButton = ttk.Button(self.buttonsFrame, takefocus=tk.YES, text=self.positive)

        bindArrows(positiveButton)
        #positiveButton.pack(expand=tk.YES, fill="x", side=tk.LEFT, padx='2m', pady='2m', ipady=5, ipadx=5)
        positiveButton.grid(column=0, row=0,
                            padx=self.padx, pady=self.pady, ipady=self.ipady, ipadx=self.ipadx)

        # for the commandButton, bind activation events
        positiveButton.bind("<Return>", self.positive_pressed)
        positiveButton.bind("<Button-1>", self.positive_pressed)
        positiveButton.bind("<space>", self.positive_pressed)


    def create_neutral_button(self): # experimental нейтральная кнопка списка

        # put the buttons in the self.buttonsFrame

        neutralButton = ttk.Button(self.buttonsFrame, takefocus=tk.YES, text=self.neutral + " [*]")

        bindArrows(neutralButton)

        neutralButton.grid(column=1, row=0, padx=self.padx, pady=self.pady, ipady=self.ipady, ipadx=self.ipadx)

        # for the commandButton, bind activation events
        neutralButton.bind("<Return>", self.neutral_pressed)
        neutralButton.bind("<Button-1>", self.neutral_pressed)
        neutralButton.bind("<space>", self.neutral_pressed)

    def create_cancel_button(self):
        cancelButton = ttk.Button(self.buttonsFrame, takefocus=tk.YES, text=self.negative + " [Escape]")
        bindArrows(cancelButton)
        cancelButton.grid(column=2, row=0, padx=self.padx, pady=self.pady, ipady=self.ipady, ipadx=self.ipadx)
        cancelButton.bind("<Return>", self.cancel_pressed)
        cancelButton.bind("<Button-1>", self.cancel_pressed)
        cancelButton.bind("<space>", self.cancel_pressed)
        cancelButton.bind("<Escape>", self.cancel_pressed)
        # for the commandButton, bind activation events to the activation event
        # handler

    def create_special_buttons(self):
        # add special buttons for multiple select features
        if not self.multiple_select:
            return

        selectAllButton = ttk.Button(self.buttonsFrame, text="Выбрать все")
        selectAllButton.grid(column=0, row=0, padx=self.padx, pady=self.pady, ipady=self.ipady, ipadx=self.ipadx)

        clearAllButton = ttk.Button(self.buttonsFrame, text="Снять все")
        clearAllButton.grid(column=1, row=0, padx=self.padx, pady=self.pady, ipady=self.ipady, ipadx=self.ipadx)

        selectAllButton.bind("<Button-1>", self.choiceboxSelectAll)
        bindArrows(selectAllButton)
        clearAllButton.bind("<Button-1>", self.choiceboxClearAll)
        bindArrows(clearAllButton)

    def KeyboardListener(self, event):
        key = event.keysym
        if len(key) <= 1:
            if key in string.printable:
                # Find the key in the liglobal_state.
                # before we clear the list, remember the selected member
                try:
                    start_n = int(self.choiceboxWidget.curselection()[0])
                except IndexError:
                    start_n = -1

                # clear the selection.
                self.choiceboxWidget.selection_clear(0, 'end')

                # start from previous selection +1
                for n in range(start_n + 1, len(self.choices)):
                    item = self.choices[n]
                    if item[0].lower() == key.lower():
                        self.choiceboxWidget.selection_set(first=n)
                        self.choiceboxWidget.see(n)
                        return
                else:
                    # has not found it so loop from top
                    for n, item in enumerate(self.choices):
                        if item[0].lower() == key.lower():
                            self.choiceboxWidget.selection_set(first=n)
                            self.choiceboxWidget.see(n)
                            return

                    # nothing matched -- we'll look for the next logical choice
                    for n, item in enumerate(self.choices):
                        if item[0].lower() > key.lower():
                            if n > 0:
                                self.choiceboxWidget.selection_set(
                                    first=(n - 1))
                            else:
                                self.choiceboxWidget.selection_set(first=0)
                            self.choiceboxWidget.see(n)
                            return

                    # still no match (nothing was greater than the key)
                    # we set the selection to the first item in the list
                    lastIndex = len(self.choices) - 1
                    self.choiceboxWidget.selection_set(first=lastIndex)
                    self.choiceboxWidget.see(lastIndex)
                    return

    def choiceboxClearAll(self, event):
        self.choiceboxWidget.selection_clear(0, len(self.choices) - 1)

    def choiceboxSelectAll(self, event):
        self.choiceboxWidget.selection_set(0, len(self.choices) - 1)
