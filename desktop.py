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
from tkinter.scrolledtext import ScrolledText
import string
import homepage
from icons import icon
from os import path
from reports import updateTimer, timeFloatToHHMM
import io2
import traceback
import dialogs
import reports
import re

# -------------------------------------------------------------------
# utility routines
# -------------------------------------------------------------------
# These routines are used by several other functions in the EasyGui module.

def initialize_images():
    images = []
    for image in dialogs.ImgList:
        images.append(tk.PhotoImage(file=image))
    return images

def bindHotKeys(self):
    self.boxRoot.bind("<Insert>", self.positive_pressed)
    self.boxRoot.bind("<Control-Insert>", self.neutral_pressed)
    self.boxRoot.bind("<BackSpace>", self.cancel_pressed)
    self.boxRoot.bind("<F1>", self.go_home)

def getButton(text="", img=[]):
    """ Выдает по запросу обработанный текст и картинку """
    if text!=None:
        text2 = text[2:]
    else:
        return None, None
    image = None
    if "Таймер" in text:
        if ":" in text:
            image = img[1]
        else:
            image = img[0]
    elif "Добавить" in text:
        image = img[2]
    elif "Сорт." in text and icon("phone2") in text:
        image = img[6]
    elif "Сорт." in text and icon("numbers") in text:
        image = img[7]
    elif "Сорт." in text and icon("pin") in text:
        image = img[8]
    elif "Сорт." in text:
        image = img[3]
    elif "Детали" in text:
        image = img[4]
    elif "Обновл." in text:
        image = img[10]
    elif "Обнов" in text:
        image = img[5]
    elif "OK [Enter]" in text:
        image = img[14]
    elif "OK" in text:
        image = img[14]
        text2 = text
    elif "Назад" in text:
        image = None
        text2 = text
    elif "Сохранить" in text:
        image = img[9]
    elif "Помощь" in text:
        image = img[11]
    elif "Отмена [Esc]" in text:
        image = img[12]
    elif "[Esc]" in text:
        image = img[31]
    elif icon("export") in text:
        image = img[13]
    elif "Аналитика" in text:
        image = img[15]
    elif "↑" in text:
        image = img[17]
    elif "↓" in text:
        image = img[18]
    elif "Журнал" in text:
        image = img[25]
    elif "Справка" in text:
        image = img[30]
    elif "F1" in text:
        image = img[32]
    else:
        text2 = text

    return text2, image

def getMenu(box, e):
    menu = tk.Menu(box, tearoff=0)
    menu.add_command(label="Вырезать", command=lambda: e.widget.event_generate("<<Cut>>"))
    menu.add_command(label="Копировать", command=lambda: e.widget.event_generate("<<Copy>>"))
    menu.add_command(label="Вставить", command=lambda: e.widget.event_generate("<<Paste>>"))
    menu.add_command(label="Удалить", command=lambda: e.widget.event_generate("<<Clear>>"))
    menu.add_separator()
    menu.add_command(label="Выделить все", command=lambda: e.widget.event_generate("<<SelectAll>>"))
    menu.tk.call("tk_popup", menu, e.x_root, e.y_root)

def config_menu(self):
    """ Главное меню """

    def fileImport(self):
        self.callback(self, command="import", choices="import")
    def fileRestore(self):
        self.callback(self, command="restore", choices="restore")
    def fileExport(self):
        self.callback(self, command="export", choices="export")
    def fileWipe(self):
        self.callback(self, command="wipe", choices="wipe")
    def fileExit(self):
        self.callback(self, command="exit", choices="exit")

    def menuFile():
        self.callback(self, command="file", choices="file")
    def menuReport():
        self.callback(self, command="report", choices="report")
    def menuSettings():
        self.callback(self, command="settings", choices="settings")
    def menuNotebook():
        self.callback(self, command="notebook", choices="notebook")
    def menuAbout():
        self.callback(self, command="about", choices="about")

    menu = tk.Menu(self.boxRoot, tearoff=0)
    self.boxRoot.config(menu=menu)
    filemenu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Файл", menu=filemenu)
    if 1:#io2.Simplified==1:
        menu.add_command(label="Настройки", command=menuSettings)
    else:
        settingsMenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Настройки", menu=settingsMenu)

        # Список настроек
        def setSetting(a=None):
            print(a)
        options = homepage.preferences(getOptions=True)
        for option in options:
            settingsMenu.add_command(label=option[2:], compound="left", command=lambda x=option: setSetting(x))

    menu.add_command(label="Отчет", command=menuReport)
    menu.add_command(label="Блокнот", command=menuNotebook)
    menu.add_command(label="О программе", command=menuAbout)

    # Файл
    filemenu.add_command(label="Импорт", compound="left", image=self.img[27], command=lambda s=self: fileImport(s))
    filemenu.add_command(label="Экспорт", compound="left", image=self.img[26], command=lambda s=self: fileExport(s))
    filemenu.add_command(label="Восстановление", compound="left", image=self.img[28], command=lambda s=self: fileRestore(s))
    filemenu.add_command(label="Очистка", compound="left", image=self.img[29], command=lambda s=self: fileWipe(s))

    if io2.Simplified == 0:
        filemenu.add_separator()
        filemenu.add_command(label="Выход с экспортом", command=lambda s=self: fileExit(s))

def create_footer(box, grid=False):
    footerFrame = tk.Frame(box)
    if grid==False:
        footerFrame.pack(side=tk.BOTTOM, fill="both", expand=tk.YES)
    else:
        footerFrame.grid(row=99, column=0, sticky="nesw")
    if io2.settings[2][6] > 0 and updateTimer(io2.settings[2][6]) >= 0:  # время в служении
        ministry_time = "В служении: " + timeFloatToHHMM(updateTimer(io2.settings[2][6]))
        timer2 = tk.Label(footerFrame, fg="royalblue", font=("Arial", 8), text=ministry_time)
        timer2.pack(side=tk.LEFT, padx=1)
    ttk.Sizegrip(footerFrame).pack(side=tk.RIGHT)

def exception_format():
    """
    Convert exception info into a string suitable for display.
    """
    return "".join(traceback.format_exception(
        sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
    ))

def parse_hotkey(text):
    """
    Extract a desired hotkey from the text.  The format to enclose
    the hotkey in square braces
    as in Button_[1] which would assign the keyboard key 1 to that button.
      The one will be included in the
    button text.  To hide they key, use double square braces as in:  Ex[[qq]]
    it  , which would assign
    the q key to the Exit button. Special keys such as <Enter> may also be
    used:  Move [<left>]  for a full
    list of special keys, see this reference: http://infohonmt.edu/tcc/help/
    pubs/tkinter/web/key-names.html
    :param text:
    :return: list containing cleaned text, hotkey, and hotkey position within
    cleaned text.
    """

    ret_val = [text, None, None]  # Default return values
    if text is None:
        return ret_val

    # Single character, remain visible
    res = re.search('(?<=\[).(?=\])', text)
    if res:
        start = res.start(0)
        end = res.end(0)
        caption = text[:start - 1] + text[start:end] + text[end + 1:]
        ret_val = [caption, text[start:end], start - 1]

    # Single character, hide it
    res = re.search('(?<=\[\[).(?=\]\])', text)
    if res:
        start = res.start(0)
        end = res.end(0)
        caption = text[:start - 2] + text[end + 2:]
        ret_val = [caption, text[start:end], None]

    # a Keysym.  Always hide it
    res = re.search('(?<=\[\<).+(?=\>\])', text)
    if res:
        start = res.start(0)
        end = res.end(0)
        caption = text[:start - 2] + text[end + 2:]
        ret_val = [caption, '<{}>'.format(text[start:end]), None]

    return ret_val



# -------------------------------------------------------------------
# choicebox
# -------------------------------------------------------------------


def choicebox(msg="", title="Окно", form="", choices=[], preselect=0,
            positive=None, neutral=None, negative="Назад", callback=None, run=True):
    """
    Present the user with a list of choices.
    return the choice that he selects.

    :param str msg: the msg to be displayed
    :param str title: the window title
    :param list choices: a list or tuple of the choices to be displayed
    :return: List containing choice selected or None if cancelled
    """
    mb = ChoiceBox(msg, title, form, choices, preselect=preselect,
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

def multchoicebox(msg="", title="Окно", form="", choices=[],
                  preselect=0, callback=None, positive=None, neutral=None, negative="Назад",
                  run=True):
    """ Same as choicebox, but the user can select many items. """

    mb = ChoiceBox(msg, title, form, choices, preselect=preselect,
                   multiple_select=True,
                   positive=positive,
                   neutral=neutral,
                   negative=negative,
                   callback=callback)
    if run:
        reply = mb.run()
        return reply
    else:
        return mb

class ChoiceBox(object):

    def __init__(self, msg, title, form, choices, preselect, multiple_select, callback, positive, neutral, negative):

        self.ui = GUItk3(msg, title, form, choices, preselect, multiple_select, self.callback_ui,
                         positive, neutral, negative)

        self.callback = callback

        self.choices = choices

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
        else:
            self.stop()
            self.choices = command

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

class GUItk3(object):

    """ This object contains the tk root object.
        It draws the window, waits for events and communicates them
        to MultiBox, together with the entered values.

        The position in wich it is drawn comes from a global variable.

        It also accepts commands from Multibox to change its message.
    """

    def __init__(self, msg="", title="Участки", form="terView", choices=[], preselect=0, multiple_select=1, callback=1, positive=None, neutral=None, negative="Назад"):

        self.callback = callback

        self.choices = choices

        self.positive = positive

        self.neutral = neutral

        self.negative = negative

        self.form = form

        self.msg = msg

        self.title = title

        self.padx = self.pady = 3

        self.ipady = self.ipadx = 5

        #self.width_in_chars = prop_font_line_length
        # Initialize self.selected_choices
        # This is the value that will be returned if the user clicks the close
        # icon
        # self.selected_choices = None

        self.multiple_select = multiple_select

        self.boxRoot = tk.Tk()
        #from os import name
        #if name == "nt":
        #    self.boxRoot.iconbitmap('icon.ico') # иконка плохо работает - окно скачет
        #self.boxRoot.iconify
        #photo = tk.PhotoImage(file='icon.png')
        #self.boxRoot.wm_iconphoto(False, photo)
        #self.boxRoot.call('wm', 'iconphoto', self.boxRoot._w, photo)
        #self.boxFont = tk_Font.nametofont("TkTextFont") # getWinFonts()[0] шрифты

        self.config_root(title)
        config_menu(self) # меню
        self.set_pos(dialogs.window_position)  # GLOBAL POSITION
        self.create_search_widget()
        create_footer(self.boxRoot)
        self.create_buttons_frame()
        self.create_ok_button()
        self.create_msg_widget()
        self.create_choicearea()
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

    def cancel_pressed(self, event=None):
        if self.form != "terView":
            self.get_pos()
            try:
                dialogs.saveWindowPosition(self.boxRoot)
            except:
                pass
            self.callback(self, command='cancel', choices=self.get_choices())

    def neutral_pressed(self, event=None):
        if self.neutral != None:
            self.callback(self, command='neutral', choices="neutral")

    def ok_pressed(self, event=None):
        self.callback(self, command='update', choices=self.get_choices())

    def positive_pressed(self, event=None):
        if self.positive != None:
            self.callback(self, command='update', choices="positive")

    def menu_pressed(self, choice, event=None):
        self.callback(self, command=choice, choices=choice)

    def search_requested(self, choice, event=None):
        self.callback(self, command=choice, choices=choice)

    def go_home(self, event=None):
        self.callback(self, command="home", choices="home")

    def contacts_pressed(self, event=None):
        self.callback(self, command='contacts', choices="contacts")

    def report_pressed(self, event=None):
        self.callback(self, command='report', choices="report")

    def stat_pressed(self, event=None):
        self.callback(self, command='statistics', choices="statistics")

    def timer_pressed(self, event=None):
        self.callback(self, command='timer', choices="timer")

    def serviceyear_pressed(self, event=None):
        self.callback(self, command='serviceyear', choices="serviceyear")


    # меню

    # Methods to change content ---------------------------------------

    def get_num_lines(self, widget):
        end_position = widget.index(tk.END)  # '4.0'
        end_line = end_position.split('.')[0]  # 4
        return int(end_line) + 1  # 5

    def set_pos(self, pos=None):
        pos = dialogs.window_size + dialogs.window_position
        self.boxRoot.geometry(pos)

    def get_pos(self):
        # The geometry() method sets a size for the window and positions it on
        # the screen. The first two parameters are width and height of
        # the window. The last two parameters are x and y screen coordinates.
        # geometry("250x150+300+300")
        geom = self.boxRoot.geometry()
        #x_size = int(geom[ 0: geom.index("x") ])
        #y_size = int(geom[ geom.index("x")+1 : geom.index("+") ])
        #y_size2= y_size+20 # коррекция высоты окна на 20, потому что оно почему-то самопроизвольно уменьшается
        #dialogs.window_size = "%dx%d" % (x_size, y_size2)
        dialogs.window_size = geom[ 0 : geom.index("+") ]
        dialogs.window_position = '+' + geom.split('+', 1)[1]

    def preselect_choice(self, preselect):
        if preselect != None:
            self.choiceboxWidget.select_set(preselect)
            #self.choiceboxWidget.selection_set(preselect)
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

        self.boxRoot.title("Rocket Ministry")
        self.boxRoot.expand = tk.YES

        self.set_pos()

        self.img = initialize_images() # картинки

        #self.boxRoot.protocol('WM_DELETE_WINDOW', self.x_pressed)
        def exit():
            self.get_pos()
            try:
                dialogs.saveWindowPosition(self.boxRoot)
            except:
                pass
            self.stop()
            self.boxRoot.destroy()
            sys.exit(0)
        self.boxRoot.protocol('WM_DELETE_WINDOW', exit)
        self.boxRoot.bind('<Any-Key>', self.KeyboardListener)
        self.boxRoot.bind("<Escape>", self.cancel_pressed)

    def find(self, event):
        query=self.search.get().strip()
        self.search_requested(choice="[search]" + query)

    def create_search_widget(self): # поиск

        self.searchFrame = ttk.Frame(master=self.boxRoot)
        self.searchFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES,
                              padx=self.padx)#, ipady=self.ipady, ipadx=self.ipadx)

        #self.display = tk.Entry(self.searchFrame, width=50, font=("arial", 8), fg="green", state="readonly")
        self.display = ScrolledText(self.searchFrame, width=30, font=("Arial", 8), fg="green", bg=dialogs.inactive_background, height=2, state="disabled")
        self.display.pack(side=tk.LEFT, padx=1, pady=3)

        if io2.LastSystemMessage[0] != "":
            if io2.LastSystemMessage[1] < 1:
                self.display.config(state="normal")
                self.display.insert(tk.INSERT, io2.LastSystemMessage[0])
                self.display.config(state="disabled")
                io2.LastSystemMessage[1] += 1
            else:
                io2.LastSystemMessage[1] = 0
                io2.LastSystemMessage[0] = ""

        self.icon = ttk.Button(self.searchFrame, image=self.img[16], takefocus=0) # кнопка с лупой
        self.icon.pack(side=tk.RIGHT, padx=1, pady=1)
        self.icon.bind("<1>", self.find)

        self.style = ttk.Style() # поисковая строка
        self.style.configure("TEntry", foreground="grey60", background="green")
        self.search = ttk.Entry(self.searchFrame, width=20, style="TEntry", takefocus=0)
        self.search.pack(side=tk.RIGHT, padx=1, pady=1)
        self.search.insert(0, "Поиск [F3]")
        self.search.bind("<Return>", self.find)
        #self.search.bind_class("Entry", "<3>", self.contextMenu)
        #self.search.bind_class("Text", "<3>", self.contextMenu)
        def temp_text(e):
            self.search.delete(0, "end")
        self.search.bind("<FocusIn>", temp_text)

        def contextMenu(e=None):
            """ Контекстное меню. Создается из внешней функции getMenu, универсальной для всех виджетов """
            getMenu(box=boxRoot, e=e)
        self.search.bind("<3>", contextMenu)

    def create_buttons_frame(self):
        self.buttonsFrame = ttk.Frame(self.boxRoot)
        self.buttonsFrame.pack(side=tk.BOTTOM, fill="y", expand=tk.YES)

        if self.form == "terView":
            #else: # отдельная конфигурация под стартовую страницу с большими кнопками
            self.startmenu = ttk.Frame(self.buttonsFrame)
            self.startmenu.grid(column=0, row=0, columnspan=3, sticky="nsew",
                                padx=self.padx, ipady=self.ipady, ipadx=self.ipadx)#pack(side=tk.BOTTOM, padx=self.padx, pady=self.pady, expand=tk.YES, fill=tk.BOTH)

            ipadxButton = ipadyButton = 5
            padx2 = pady2 = 3

            self.terButton = ttk.Button(self.startmenu, text="Новый участок", compound="top", image=self.img[21])
            self.terButton.grid(row=0, column=0, padx=padx2, pady=pady2, ipadx=ipadxButton, ipady=ipadyButton, sticky="nesw")#pack(side=side, padx=self.padx, pady=self.pady, ipady=ipadyButton, expand=expand, fill=fill)
            self.terButton.bind("<Return>", self.positive_pressed)
            self.terButton.bind("<Button-1>", self.positive_pressed)
            self.terButton.bind("<space>", self.positive_pressed)

            from contacts import getContactsAmount
            con = getContactsAmount(date=1)[0]
            self.conButton = ttk.Button(self.startmenu, text="Контакты (%d)" % con, compound="top", image=self.img[20])
            self.conButton.grid(row=0, column=1, padx=padx2, pady=pady2, ipadx=ipadxButton+12, ipady=ipadyButton, sticky="nesw")#pack(side=side, padx=self.padx, pady=self.pady, ipady=ipadyButton, expand=expand, fill=fill)
            self.conButton.bind("<Return>", self.contacts_pressed)
            self.conButton.bind("<Button-1>", self.contacts_pressed)
            self.conButton.bind("<space>", self.contacts_pressed)

            self.startmenu.columnconfigure(0, weight=1)
            self.startmenu.columnconfigure(1, weight=1)
            self.startmenu.columnconfigure(2, weight=1)

            rep, gap = reports.getCurrentHours()
            if gap >= 0:
                gap_str = "↑"
            else:
                gap_str = "↓"
            if io2.settings[0][3]==0:
                gap_str = ""
            self.repButton = ttk.Button(self.startmenu, text="Отчет (%s%s)" % (rep, gap_str), compound="top", image=self.img[22])
            self.repButton.grid(row=0, column=2, padx=padx2, pady=pady2, ipadx=ipadxButton, ipady=ipadyButton, sticky="nesw")  # pack(side=side, padx=self.padx, pady=self.pady, ipady=ipadyButton, expand=expand, fill=fill)
            self.repButton.bind("<Return>", self.report_pressed)
            self.repButton.bind("<Button-1>", self.report_pressed)
            self.repButton.bind("<space>", self.report_pressed)

            from house_op import countTotalProgress
            self.staButton = ttk.Button(self.startmenu, text="Статистика (%s%%)" % countTotalProgress(), compound="top", image=self.img[23])
            self.staButton.grid(row=1, column=0, padx=padx2, pady=pady2, ipadx=ipadxButton, ipady=ipadyButton, sticky="nesw")#pack(side=side, padx=self.padx, pady=self.pady, ipady=ipadyButton, expand=expand, fill=fill)
            self.staButton.bind("<Return>", self.stat_pressed)
            self.staButton.bind("<Button-1>", self.stat_pressed)
            self.staButton.bind("<space>", self.stat_pressed)

            if reports.updateTimer(io2.settings[2][6]) >= 0:  # проверка, включен ли таймер
                time2 = reports.updateTimer(io2.settings[2][6])
            else:
                time2 = reports.updateTimer(io2.settings[2][6]) + 24
            if io2.settings[2][6] > 0:
                timerTime = reports.timeFloatToHHMM(time2)
            else:
                timerTime = ""
            self.timButton = ttk.Button(self.startmenu, text="Таймер %s" % timerTime, compound="top", image=getButton("Таймер %s" % timerTime, self.img)[1])
            self.timButton.grid(row=1, column=1, padx=padx2, pady=pady2, ipadx=ipadxButton, ipady=ipadyButton, sticky="nesw")#pack(side=side, padx=self.padx, pady=self.pady, ipady=ipadyButton, expand=expand, fill=fill)
            self.timButton.bind("<Return>", self.timer_pressed)
            self.timButton.bind("<Button-1>", self.timer_pressed)
            self.timButton.bind("<space>", self.timer_pressed)

            self.serButton = ttk.Button(self.startmenu, text="Служебный год", compound="top", image=self.img[24])
            self.serButton.grid(row=1, column=2, padx=padx2, pady=pady2, ipadx=ipadxButton, ipady=ipadyButton, sticky="nesw")#pack(side=side, padx=self.padx, pady=self.pady, ipady=ipadyButton, expand=expand, fill=fill)
            self.serButton.bind("<Return>", self.serviceyear_pressed)
            self.serButton.bind("<Button-1>", self.serviceyear_pressed)
            self.serButton.bind("<space>", self.serviceyear_pressed)

        # put the buttons in the self.buttonsFrame

        if self.positive == icon("plus", simplified=False):  # если плюс, заменяем его на более красивый
            self.positive = "  Добавить [Ins]"
        elif self.positive == icon("down"):
            self.positive += " [Ins]"
        if self.positive!=None and self.form != "terView":
            positiveButton = ttk.Button(self.buttonsFrame, takefocus=tk.YES, compound="left",
                                        text=getButton(self.positive, self.img)[0], image=getButton(self.positive, self.img)[1])
            positiveButton.grid(column=0, row=1, sticky="we",
                                padx=self.padx, ipady=self.ipady, ipadx=self.ipadx)
            # for the commandButton, bind activation events
            positiveButton.bind("<Return>", self.positive_pressed)
            positiveButton.bind("<Button-1>", self.positive_pressed)
            positiveButton.bind("<space>", self.positive_pressed)

        # put the buttons in the self.buttonsFrame

        if self.neutral != None and self.form != "terView":
            self.neutral += " [Ctrl+Ins]"
            neutralButton = ttk.Button(self.buttonsFrame, takefocus=tk.YES, compound="left",
                                       text=getButton(self.neutral, self.img)[0], image = getButton(self.neutral, self.img)[1])
            neutralButton.grid(column=1, row=1, sticky="we",
                               padx=self.padx, ipady=self.ipady, ipadx=self.ipadx)
            # for the commandButton, bind activation events
            neutralButton.bind("<Return>", self.neutral_pressed)
            neutralButton.bind("<Button-1>", self.neutral_pressed)
            neutralButton.bind("<space>", self.neutral_pressed)

        # add special buttons for multiple select features
        if not self.multiple_select:
            return

        selectAllButton = ttk.Button(self.buttonsFrame, text="Выбрать все")
        selectAllButton.grid(column=0, row=1, padx=self.padx, pady=self.pady, ipady=self.ipady, ipadx=self.ipadx)

        clearAllButton = ttk.Button(self.buttonsFrame, text="Снять все")
        clearAllButton.grid(column=1, row=1, padx=self.padx, pady=self.pady, ipady=self.ipady, ipadx=self.ipadx)

        selectAllButton.bind("<Button-1>", self.choiceboxSelectAll)

        clearAllButton.bind("<Button-1>", self.choiceboxClearAll)

    def create_msg_widget(self):

        self.msgFrame = tk.Frame(self.boxRoot) # дублирование title
        self.msgFrame.pack(side=tk.TOP, expand=1, fill='both')
        if len(self.title)>1 and self.title[1]==" " and self.form != "firstCallMenu" and "Этаж" not in self.title and self.form!="flatView":
            msg = self.title[1:]
        else:
            msg = self.title
        self.messageArea = tk.Label(self.msgFrame, text=msg, fg="grey20")
        self.messageArea.pack(side=tk.TOP, expand=1, fill='both')

    def create_ok_button(self):

        okButtonFrame = tk.Frame(self.boxRoot)
        okButtonFrame.pack(side=tk.TOP, fill="both", expand=tk.YES)

        okButton = ttk.Button(okButtonFrame, takefocus=0, compound="left",  # кнопка OK в списке
                              text=getButton("  OK [Enter]", self.img)[0],
                              image=getButton("  OK [Enter]", self.img)[1])
        okButton.bind("<Return>", self.ok_pressed)
        okButton.bind("<Button-1>", self.ok_pressed)
        okButton.bind("<space>", self.ok_pressed)

        sideButtonIpadX = 0

        if self.form == "terView":
            okButton.pack(side=tk.LEFT, fill="x", expand=tk.YES, padx=self.padx, ipady=self.ipady)

            if self.neutral != None:
                neutralButton = ttk.Button(okButtonFrame, takefocus=0, compound="left",  # кнопка сортировка участков
                                    text=getButton(self.neutral, self.img)[0],
                                    image=getButton(self.neutral, self.img)[1])
                neutralButton.bind("<Return>", self.neutral_pressed)
                neutralButton.bind("<Button-1>", self.neutral_pressed)
                neutralButton.bind("<space>", self.neutral_pressed)
                neutralButton.pack(side=tk.LEFT, padx=self.padx, pady=0, ipadx=sideButtonIpadX, ipady=self.ipady)

        else:
            if self.negative != None:
                backButton = ttk.Button(okButtonFrame, takefocus=0, compound="left",  # кнопка назад
                                        text=getButton("  [Esc]", self.img)[0],
                                        image=getButton("  [Esc]", self.img)[1])
                backButton.bind("<Return>", self.cancel_pressed)
                backButton.bind("<Button-1>", self.cancel_pressed)
                backButton.bind("<space>", self.cancel_pressed)
                backButton.bind("<Escape>", self.cancel_pressed)
                backButton.pack(side=tk.LEFT, padx=self.padx, pady=0, ipadx=sideButtonIpadX, ipady=self.ipady)

                okButton.pack(side=tk.LEFT, fill="x", expand=tk.YES, padx=self.padx, ipady=self.ipady)

                homeButton = ttk.Button(okButtonFrame, takefocus=0, compound="left",   # кнопка возврата на главную
                                        text=getButton("  [F1]", self.img)[0],
                                        image=getButton("  [F1]", self.img)[1])
                homeButton.bind("<Return>", self.go_home)
                homeButton.bind("<Button-1>", self.go_home)
                homeButton.bind("<space>", self.go_home)
                homeButton.pack(side=tk.LEFT, padx=self.padx, pady=0, ipadx=sideButtonIpadX, ipady=self.ipady)

    def create_choicearea(self):

        self.choiceboxFrame = ttk.Frame(master=self.boxRoot)
        self.choiceboxFrame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.YES, padx=1, ipady=self.ipady, ipadx=self.ipadx)

        # --------  put the self.choiceboxWidget in the self.choiceboxFrame ---
        self.choiceboxWidget = tk.Listbox(self.choiceboxFrame,
                                          height=500,
                                          borderwidth="2m", relief="flat",
                                          bg="white"
        )

        if 1:#self.form == "porchViewGUIList" or self.form == "porchViewGUIOneFloor" or self.form == "porchText":
            self.choiceboxWidget.config( font = (dialogs.MONOSPACE_FONT_FAMILY, dialogs.MONOSPACE_FONT_SIZE) )
        else:
            self.choiceboxWidget.config(font=(dialogs.PROPORTIONAL_FONT_FAMILY, dialogs.PROPORTIONAL_FONT_SIZE))

        for choice in self.choices:
            self.choiceboxWidget.insert(tk.END, choice)

        if self.multiple_select:
            self.choiceboxWidget.configure(selectmode=tk.MULTIPLE)

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
        self.choiceboxWidget.pack(side=tk.TOP, padx=self.padx, pady=self.pady, expand=tk.YES, fill=tk.BOTH)

        # Bind the keyboard events
        self.choiceboxWidget.bind("<Return>", self.ok_pressed)
        self.choiceboxWidget.bind("<Double-Button-1>", self.ok_pressed)
        self.choiceboxWidget.bind("<3>", self.listContextMenu)

        bindHotKeys(self)

        def focus_search(event):
            self.search.focus()
        self.boxRoot.bind("<F3>", focus_search)

    def listContextMenu(self, e=None): # контекстное меню списка ***
        menu = tk.Menu(self.boxRoot, tearoff=0)
        menu.add_command(
            label=getButton("  OK", self.img)[0],
            image=getButton("  OK", self.img)[1],
            compound="left",
            command=self.ok_pressed
        )
        if self.positive != None:
            if "[" in self.positive:
                text = self.positive[0: self.positive.index("[")]
            else:
                text = self.positive
            menu.add_command(
                label=getButton(text, self.img)[0],
                image=getButton(text, self.img)[1],
                compound="left",
                command=self.positive_pressed
            )
        if self.neutral != None:
            if "[" in self.neutral:
                text = self.neutral[0: self.neutral.index("[")]
            else:
                text = self.neutral
            menu.add_command(
                label=getButton(text, self.img)[0],
                image=getButton(text, self.img)[1],
                compound="left",
                command=self.neutral_pressed
            )
        menu.add_separator()
        menu.add_command(label="Копировать", command=lambda: e.widget.event_generate("<<Copy>>"))
        menu.tk.call("tk_popup", menu, e.x_root, e.y_root)

    def KeyboardListener(self, event):
        key = event.keysym
        if len(key) <= 1:
            if key in string.printable:
                # Find the key in the li
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


# -------------------------------------------------------------------
# getFileDialogTitle
# -------------------------------------------------------------------


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


# -------------------------------------------------------------------
# textbox
# -------------------------------------------------------------------


def textbox(msg="", title=" ", text="",
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

    tb = TextBox(msg=msg, title=title, text=text, disabled=disabled,
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

    def __init__(self, msg, title, text, codebox, callback, disabled, positive, neutral, negative):
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
        self.ui = GUItk(msg, title, text, codebox, self.callback_ui, disabled, positive=positive, neutral=neutral, negative=negative)
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

    def __init__(self, msg, title, text, codebox, callback, disabled, positive, neutral, negative):

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

        self.padx = 5

        self.pady = 6

        self.ipady = 5

        self.ipadx = 5

        self.disabled = disabled

        self.boxRoot = tk.Tk()

        self.img = initialize_images()

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

        # default_font.configure(size=PROPORTIONAL_FONT_SIZE)

        if title[1] == " ":
            self.configure_root(title[2:])
        else:
            self.configure_root(title)

        #bindHotKeys(self)

        self.create_msg_widget(msg)

        create_footer(self.boxRoot)

        self.create_buttons_frame()

        self.create_text_area(wrap_text)

        #from os import name
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

    def get_num_lines(self, widget):
        end_position = widget.index(tk.END)  # '4.0'
        end_line = end_position.split('.')[0]  # 4
        return int(end_line) + 1  # 5

    def set_text(self, text):
        self.textArea.delete(1.0, tk.END)
        self.textArea.insert(tk.END, text, "normal")
        if self.disabled == True:
            self.textArea.config(state=tk.DISABLED, background=dialogs.inactive_background)
        self.textArea.focus_force()

    def set_pos(self, pos):
        self.boxRoot.geometry(pos)

    def get_pos(self):
        # The geometry() method sets a size for the window and positions it on
        # the screen. The first two parameters are width and height of
        # the window. The last two parameters are x and y screen coordinates.
        # geometry("250x150+300+300")
        geom = self.boxRoot.geometry()  # "628x672+300+200"
        dialogs.window_position = '+' + geom.split('+', 1)[1]
        dialogs.window_size = geom[0: geom.index("+")]

    def get_text(self):
        return self.textArea.get(0.0, 'end-1c')

    # Methods executing when a key is pressed -------------------------------
    def x_pressed(self):
        self.callback(self, command='x', text=self.get_text())

    def ok_button_pressed(self, event=None):
        self.callback(self, command='update', text=self.get_text())

    """def positive_pressed(self, event=None):
        self.ok_button_pressed()"""

    def cancel_pressed(self, event):
        self.get_pos()
        dialogs.saveWindowPosition(self.boxRoot)
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

        self.set_pos(dialogs.window_size + dialogs.window_position)

        # Quit when x button pressed
        #self.boxRoot.protocol('WM_DELETE_WINDOW', self.x_pressed)
        def exit():
            dialogs.saveWindowPosition(self.boxRoot)
            self.stop()
            self.boxRoot.destroy()
            sys.exit(0)
        self.boxRoot.protocol('WM_DELETE_WINDOW', exit)
        self.boxRoot.bind("<Escape>", self.cancel_pressed)
        #from os import name
        #if name == "nt":
        #    self.boxRoot.iconbitmap('icon.ico')

        self.boxRoot.bind_class("Text", "<3>", self.contextMenu)

    def create_msg_widget(self, msg):

        self.msgFrame = tk.Frame(self.boxRoot) # дублирование title
        self.msgFrame.pack(side=tk.TOP, expand=1, fill='both')
        if self.title[1] == " ":
            text = self.title[1:]
        else:
            text = self.title
        self.messageArea = tk.Label(self.msgFrame, text=text, fg="grey30")
        self.messageArea.pack(side=tk.TOP, expand=1, fill='both', padx=3)

    def create_text_area(self, wrap_text):
        """
        Put a textArea in the top frame
        Put and configure scrollbars
        """

        self.textFrame = tk.Frame(
            self.boxRoot,
            padx=self.padx,
            pady=self.pady#self.pady
        )

        self.textFrame.pack(side=tk.BOTTOM)
        # self.textFrame.grid(row=1, column=0, sticky=tk.EW)

        self.textArea = tk.Text(
            self.textFrame,
            padx=self.padx,#default_hpad_in_chars * self.calc_character_width(),
            pady=self.pady,#default_hpad_in_chars * self.calc_character_width(),
            height=500,#TextBoxHeight,  # lines                     # высота текстового окна
            width=500,#TextBoxWidth,   # chars of the current font # ширина текстового окна
            takefocus=1,
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

        if not wrap_text:
            bottomScrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        rightScrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.textArea.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

    def create_buttons_frame(self):

        self.buttonsFrame = tk.Frame(self.boxRoot, takefocus=1)
        self.buttonsFrame.pack(side=tk.BOTTOM, expand=tk.YES, fill="both")

    def create_ok_button(self):
        # put the buttons in the buttonsFrame

        if self.disabled==False:
            text, image = getButton("  " + self.positive + " [Shift-Enter]", self.img)
        else:
            text = self.positive
            image = None
        self.okButton = ttk.Button(
            self.buttonsFrame, takefocus=tk.YES, compound="left", text=text, image=image)
        self.okButton.pack(
            expand=tk.YES, side=tk.LEFT, padx=self.padx,
            ipady=self.ipady, ipadx=self.ipadx)

        # for the commandButton, bind activation events to the activation event
        # handler
        self.okButton.bind("<Return>", self.ok_button_pressed)
        self.okButton.bind("<Button-1>", self.ok_button_pressed)
        self.okButton.focus_force()

    def create_cancel_button(self):
        # put the buttons in the buttonsFrame
        self.cancelButton = ttk.Button(
            self.buttonsFrame, takefocus=tk.YES, compound="left",
            text=getButton("  " + self.negative + " [Esc]", self.img)[0],
            image=getButton(self.negative + " [Esc]", self.img)[1]
        )
        self.cancelButton.pack(
            expand=tk.YES, side=tk.RIGHT, padx=self.padx,
            ipady=self.ipady, ipadx=self.ipadx)

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

    def contextMenu(self, e=None):
        """ Контекстное меню. Создается из внешней функции getMenu, универсальной для всех виджетов """
        getMenu(box=self.boxRoot, e=e)

# -------------------------------------------------------------------
# enterbox
# -------------------------------------------------------------------

def enterbox(msg="", title=" ", default="",
             strip=True, image=None, root=None, mono=False, height=5, neutral=None):
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
        msg, title, default=default, mask=None, root=root, mono=mono, height=height, neutral=neutral)
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
    return __fillablebox(msg, title, default, mask="*", root=root, mono=mono, height=height, neutral=None, lib=lib)


# -------------------------------------------------------------------
# buttonbox
# -------------------------------------------------------------------

def buttonbox(msg="",
              title=" ",
              choices=[],
              image=None,
              images=None,
              default_choice=None,
              cancel_choice=None,
              callback=None,
              run=True,
              mono=False,
              height=5,
              positive=None,
              neutral=None,
              negative=None):
    """
    Display a msg, a title, an image, and a set of buttons.
    The buttons are defined by the members of the choices

    :param str msg: the msg to be displayed
    :param str title: the window title
    :param list choices: a list or tuple of the choices to be displayed
    :param str image: (Only here for backward compatibility)
    :param str images: Filename of image or iterable or iteratable of iterable to display
    :param str default_choice: The choice you want highlighted when the gui appears
    :return: the text of the button that the user selected
    """

    if image and images:
        raise ValueError("Specify 'images' parameter only for buttonbox.")
    if image:
        images = image
    bb = ButtonBox(
        msg=msg,
        title=title,
        choices=[positive, neutral, negative],
        images=images,
        default_choice=positive,
        cancel_choice=negative,
        callback=callback,
        #mono=mono,
        height=height,
        positive=positive,
        neutral=neutral,
        negative=negative)
    if not run:
        return bb
    else:
        reply = bb.run()
        return reply


class ButtonBox(object):
    """ Display various types of button boxes

    This object separates user from ui, defines which methods can
    the user invoke and which properties can he change.

    It also calls the ui in defined ways, so if other gui
    library can be used (wx, qt) without breaking anything for the user.
    """

    def __init__(self, msg, title, choices, images, default_choice, cancel_choice, callback, height,
                 positive, neutral, negative):
        """ Create box object

        Parameters
        ----------
        msg : string
            text displayed in the message area (instructions...)
        title : str
            the window title
        choices : iterable of strings
            build a button for each string in choices
        images : iterable of filenames, or an iterable of iterables of filenames
            displays each image
        default_choice : string
            one of the strings in choices to be the default selection
        cancel_choice : string
            if X or <esc> is pressed, it appears as if this button was pressed.
        callback: function
            if set, this function will be called when any button is pressed.

        Returns
        -------
        object
            The box object
        """

        self.callback = callback

        if positive ==None:
            positive=""

        self.positive = positive

        if neutral==None:
            neutral=""

        self.neutral = neutral

        if negative==None:
            negative=""

        self.negative = negative

        self.height = height,

        self.ui = GUItk2(msg, title, choices, images, default_choice, cancel_choice, self.height, self.callback_ui,
                        self.positive, self.neutral, self.negative)

    def run(self):
        """ Start the ui """
        self.ui.run()
        ret_val = self._text
        self.ui = None
        return ret_val

    def stop(self):
        """ Stop the ui """
        self.ui.stop()

    def callback_ui(self, ui, command):
        """ This method is executed when buttons or x is pressed in the ui.
        """
        if command == 'update':  # Any button was pressed
            if self.positive in ui.choice: # адаптация вывода кнопок под вывод SL4A
                self._text = "positive"
            elif self.neutral in ui.choice:
                self._text = "neutral"
            elif self.negative in ui.choice:
                self._text = "negative"
            else:
                self._text = ui.choice
            self._choice_rc = ui.choice_rc
            if self.callback:
                # If a callback was set, call main process
                self.callback(self)
            else:
                self.stop()
        elif command == 'x':
            self.stop()
            self._text = None
        elif command == 'cancel':
            self.stop()
            self._text = None

    # methods to change properties --------------
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

    @property
    def choice(self):
        """ Name of button selected """
        return self._text

    @property
    def choice_rc(self):
        """ The row/column of the selected button (as a tuple) """
        return self._choice_rc

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


class GUItk2(object):
    """ This is the object that contains the tk root object"""

    def __init__(self, msg, title, choices, images, default_choice, cancel_choice,
                 height, callback, positive, neutral, negative):
        """ Create ui object

        Parameters
        ----------
        msg : string
            text displayed in the message area (instructions...)
        title : str
            the window title
        choices : iterable of strings
            build a button for each string in choices
        images : iterable of filenames, or an iterable of iterables of filenames
            displays each image
        default_choice : string
            one of the strings in choices to be the default selection
        cancel_choice : string
            if X or <esc> is pressed, it appears as if this button was pressed.
        callback: function
            if set, this function will be called when any button is pressed.


        Returns
        -------
        object
            The ui object
        """
        self._title = title
        self._msg = msg
        self._choices = choices
        self._default_choice = default_choice
        self._cancel_choice = cancel_choice
        self.positive = positive
        self.neutral = neutral
        self.negative = negative
        self.callback = callback
        self._choice_text = None
        self._choice_rc = None
        self._images = list()

        self.boxRoot = tk.Tk()
        self.boxFont = tk_Font.Font(
             family=dialogs.MONOSPACE_FONT_FAMILY,
             size=dialogs.MONOSPACE_FONT_SIZE)

        #self.boxFont = tk_Font.nametofont("TkFixedFont")
        self.width_in_chars = dialogs.fixw_font_line_length

        self.configure_root("Rocket Ministry")

        self.create_msg_widget(msg)

        self.create_images_frame()

        create_footer(self.boxRoot, grid=True)

        #self.create_images(images)

        self.create_buttons_frame()

        self.create_buttons(choices, default_choice)

        self.messageArea.focus_force()

    @property
    def choice(self):
        return self._choice_text

    @property
    def choice_rc(self):
        return self._choice_rc

    # Run and stop methods ---------------------------------------

    def run(self):
        self.boxRoot.mainloop()
        self.boxRoot.destroy()

    def stop(self):
        # Get the current position before quitting
        self.get_pos()
        self.boxRoot.quit()

    # Methods to change content ---------------------------------------

    def set_pos(self, pos):
        self.boxRoot.geometry(pos)

    def get_pos(self):
        # The geometry() method sets a size for the window and positions it on
        # the screen. The first two parameters are width and height of
        # the window. The last two parameters are x and y screen coordinates.
        # geometry("250x150+300+300")
        geom = self.boxRoot.geometry()  # "628x672+300+200"
        dialogs.window_position = '+' + geom.split('+', 1)[1]
        dialogs.window_size = geom[0: geom.index("+")]

    # Methods executing when a key is pressed -------------------------------
    def x_pressed(self):
        self._choice_text = self._cancel_choice
        self.callback(self, command='x')

    def cancel_pressed(self, event):
        self.get_pos()
        dialogs.saveWindowPosition(self.boxRoot)
        self._choice_text = self._cancel_choice
        self.callback(self, command='cancel')

    def button_pressed(self, button_text, button_rc):
        self._choice_text = button_text
        self._choice_rc = button_rc
        self.callback(self, command='update')

    def positive_pressed(self):
        self.callback(self, command='update')

    def hotkey_pressed(self, event=None):
        """
        Handle an event that is generated by a person interacting with a button.  It may be a button press
        or a key press.

        TODO: Enhancement: Allow hotkey to be specified in filename of image as a shortcut too!!!
        """

        # Determine window location and save to global
        # TODO: Not sure where this goes, but move it out of here!
        m = re.match("(\d+)x(\d+)([-+]\d+)([-+]\d+)", self.boxRoot.geometry())
        if not m:
            raise ValueError(
                "failed to parse geometry string: {}".format(self.boxRoot.geometry()))
        width, height, xoffset, yoffset = [int(s) for s in m.groups()]
        dialogs.window_position = '{0:+g}{1:+g}'.format(xoffset, yoffset)

        # Hotkeys
        if self._buttons:
            for button_name, button in self._buttons.items():
                hotkey_pressed = event.keysym
                if event.keysym != event.char:  # A special character
                    hotkey_pressed = '<{}>'.format(event.keysym)
                if button['hotkey'] == hotkey_pressed:
                    self._choice_text = button_name
                    self.callback(self, command='update')
                    return
        print("Event not understood")

    # Auxiliary methods -----------------------------------------------
    def calc_character_width(self):
        char_width = self.boxFont.measure('W')
        return char_width

    # Initial configuration methods ---------------------------------------
    # These ones are just called once, at setting.

    def configure_root(self, title):
        self.boxRoot.title(title)

        self.set_pos(dialogs.window_size + dialogs.window_position)

        # Resize setup
        self.boxRoot.columnconfigure(0, weight=10)
        self.boxRoot.minsize(20, 50)
        # Quit when x button pressed
        #self.boxRoot.protocol('WM_DELETE_WINDOW', self.x_pressed)
        def exit():
            dialogs.saveWindowPosition(self.boxRoot)
            self.stop()
            self.boxRoot.destroy()
            sys.exit(0)
        self.boxRoot.protocol('WM_DELETE_WINDOW', exit)
        self.boxRoot.bind("<Escape>", self.cancel_pressed)
        #from os import name
        #if name == "nt":
        #    self.boxRoot.iconbitmap('icon.ico')

        self.img = initialize_images()

    def create_msg_widget(self, msg):

        if len(self._title) > 1 and self._title[1]==" ":
            text = self._title[1:]
        else:
            text = self._title

        self.msgArea = tk.Label(self.boxRoot, text=text, fg="grey30")
        self.msgArea.grid(row=0)#pack(expand=1, fill='both', padx=3)

        self.messageArea = tk.Text(
            self.boxRoot,
            width=self.width_in_chars,
            padx=10,
            pady=10,
            wrap=tk.WORD,
            font=(dialogs.PROPORTIONAL_FONT_FAMILY, dialogs.PROPORTIONAL_FONT_SIZE),
        )
        self.messageArea.insert(tk.END, msg)
        self.messageArea.config(state=tk.DISABLED, bg=dialogs.inactive_background)
        self.messageArea.config(width=200, padx=20, background=dialogs.inactive_background)  # ширина окна текста
        self.messageArea.grid(row=1)
        self.boxRoot.rowconfigure(0, weight=0)
        self.boxRoot.rowconfigure(1, weight=10)
        self.boxRoot.rowconfigure(2, weight=0)
        self.boxRoot.bind_class("Text", "<3>", self.contextMenu)








    def contextMenu(self, e=None):
        """ Контекстное меню. Создается из внешней функции getMenu, универсальной для всех виджетов """
        getMenu(box=self.boxRoot, e=e)

    def create_images_frame(self):
        self.imagesFrame = tk.Frame(self.boxRoot)
        row = 1
        #self.imagesFrame.grid(row=row)
        self.boxRoot.rowconfigure(row, weight=10, minsize='10m')

    def create_buttons_frame(self):
        self.buttonsFrame = ttk.Frame(self.boxRoot)
        self.buttonsFrame.grid(row=2, column=0, padx=2, pady=10)

        # add a vertical scrollbar to the frame
        self.rightScrollbar = ttk.Scrollbar(
            self.imagesFrame, orient=tk.VERTICAL, command=self.messageArea.yview)
        self.messageArea.configure(yscrollcommand=self.rightScrollbar.set)
        self.rightScrollbar.grid()#(column=0, row=0)

    def create_buttons(self, choices, default_choice):
        #unique_choices = uniquify_list_of_strings(choices)
        # Create buttons dictionary and Tkinter widgets
        buttons = dict()
        i_hack = 0
        for row, (button_text, unique_button_text) in enumerate(zip(choices, choices)):

            #button_text = getButton(button_text, button_text)[0]
            #button_image = getButton(button_text, button_text)[1]

            this_button = dict()
            #if button_text != None and "Обновл." in button_text:
            #    button_text = "  Обновление"
            this_button['original_text'] = button_text
            this_button['clean_text'], this_button['hotkey'], hotkey_position = parse_hotkey(button_text)
            if this_button['clean_text'] != "Назад":
                text = getButton(this_button['clean_text'], self.img)[0]
            else:
                text = "Назад"
            this_button['widget'] = ttk.Button(
                    self.buttonsFrame,
                    takefocus=1,
                    compound="left",
                    text = text,
                    image = getButton(this_button['clean_text'], self.img)[1],
                    underline=hotkey_position)
            fn = lambda text=button_text, row=row, column=0: self.button_pressed(text, (row, column))
            this_button['widget'].configure(command=fn)
            if button_text != None:
                this_button['widget'].grid(row=0, column=i_hack, padx='2m', pady='1.5m', ipadx='1m', ipady='1m')
            self.buttonsFrame.columnconfigure(i_hack, weight=10)
            i_hack += 1
            buttons[unique_button_text] = this_button

        self._buttons = buttons
        if default_choice in buttons:
            buttons[default_choice]['widget'].focus_force()

        #else:
        #    buttons[self.positive].focus_force()
        # Bind hotkeys
        for hk in [button['hotkey'] for button in buttons.values() if button['hotkey']]:
            self.boxRoot.bind_all(hk, lambda e: self.hotkey_pressed(e), add=True)
            #self.boxRoot.bind_all("Return", lambda e: self.hotkey_pressed(e), add=True)
            #self.boxRoot.bind_all("<Return>", self.positive_pressed)



# -----------------------------------------------------------------------
# msgbox
# -----------------------------------------------------------------------


def msgbox(msg="", title=" ",
           ok_button=None, positive=None, neutral=None, negative=None, image=None, root=None):
    """
    Display a message box

    :param str msg: the msg to be displayed
    :param str title: the window title
    :param str ok_button: text to show in the button
    :param str image: Filename of image to display
    :param tk_widget root: Top-level Tk widget
    :return: the text of the ok_button
    """
#    if not isinstance(ok_button, str):
#        raise AssertionError(
#            "The 'ok_button' argument to msgbox must be a string.")

    return buttonbox(msg=msg,
                     title=title,
                     choices=[positive, neutral, negative],
                     image=image,
                     default_choice=positive,
                     cancel_choice=negative,
                     positive=positive,
                     neutral=neutral,
                     negative=negative)

def convert_to_type(input_value, new_type, input_value_name=None):
    """
    Attempts to convert input_value to type new_type and throws error if it can't.

    If input_value is None, None is returned
    If new_type is None, input_value is returned unchanged
    :param input_value: Value to be converted
    :param new_type: Type to convert to
    :param input_value_name: If not None, used in error message if input_value cannot be converted
    :return: input_value converted to new_type, or None
    """
    if input_value is None or new_type is None:
        return input_value

    exception_string = (
        'value {0}:{1} must be of type {2}.')
    ret_value = new_type(input_value)
#        except ValueError:
#            raise ValueError(
#                exception_string.format('default', default, type(default)))
    return ret_value


# -------------------------------------------------------------------
# fillablebox
# -------------------------------------------------------------------

boxRoot = None
entryWidget = None
__enterboxText = ''
__enterboxDefaultText = ''
cancelButton = None
nButton = None
okButton = None

def __fillablebox(msg, title="", default="", mask=None, root=None, mono=False, height=5, neutral=None, lib=False):
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

    if root:
        root.withdraw()
        boxRoot = tk.Toplevel(master=root)
        boxRoot.withdraw()
    else:
        boxRoot = tk.Tk()
        boxRoot.withdraw()

    #boxRoot.protocol('WM_DELETE_WINDOW', __enterboxQuit)
    def exit():
        geom = boxRoot.geometry()
        if lib == False:
            dialogs.window_position = '+' + geom.split('+', 1)[1]
            dialogs.window_size = geom[0: geom.index("+")]
            dialogs.saveWindowPosition(boxRoot)
        boxRoot.destroy()
        sys.exit(0)
    boxRoot.protocol('WM_DELETE_WINDOW', exit)

    boxRoot.title("Rocket Ministry")

    #from os import name
    #if name == "nt":
    #    boxRoot.iconbitmap('icon.ico')

    if lib==True:
        height = 1
        boxRoot.geometry("250x120+500+350")
    else:
        height=height
        pos = dialogs.window_size + dialogs.window_position
        boxRoot.geometry(pos)

    boxRoot.bind("<Escape>", __enterboxCancel)

    mainFrame = tk.Frame(boxRoot)
    mainFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    bottomFrame = tk.Frame(boxRoot)
    bottomFrame.pack(side=tk.BOTTOM, fill=tk.BOTH)

    create_footer(bottomFrame)

    # Верхняя строка (дублирование title)
    msgFrame = tk.Frame(mainFrame)
    msgFrame.pack(side=tk.TOP, fill='both')
    if title.strip()=="":
        text = None
    elif title[1]==" ":
        text = title[1:]
    else:
        text = title
    messageArea = tk.Label(msgFrame, text=text, fg="grey30")
    if text!=None:
        messageArea.pack(side=tk.TOP, expand=1, fill='both', padx=3)

    # ------------- define the messageFrame ---------------------------------
    messageFrame = tk.Frame(master=mainFrame)
    messageFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # ------------- define the entryFrame ---------------------------------
    entryFrame = ttk.Frame(master=mainFrame)
    entryFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # ------------- define the buttonsFrame ---------------------------------
    buttonsFrame = ttk.Frame(master=mainFrame)
    buttonsFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # -------------------- the msg widget ----------------------------
    #messageWidget = tk.Message(messageFrame, width="4i", text=msg)

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
    entryWidget = ttk.Entry(entryFrame, width=500) # ширина окна текста

    entryWidget.configure(
        font=(dialogs.MONOSPACE_FONT_SIZE, dialogs.TEXT_ENTRY_FONT_SIZE))
    if mask:
        entryWidget.configure(show=mask)

    def contextMenu(e=None):
        """ Контекстное меню. Создается из внешней функции getMenu, универсальной для всех виджетов """
        getMenu(box=boxRoot, e=e)

    entryWidget.pack(side=tk.LEFT, padx="5m")
    entryWidget.bind("<Return>", __enterboxGetText)
    entryWidget.bind("<Escape>", __enterboxCancel)
    entryWidget.bind("<Control-Insert>", __enterboxNeutral)
    # put text into the entryWidget
    entryWidget.insert(0, __enterboxDefaultText)
    entryWidget.bind_class("TEntry", "<3>", contextMenu)

    img = initialize_images()

    # ------------------ ok button -------------------------------
    okButton = ttk.Button(buttonsFrame, takefocus=1, compound="left", text="OK")#getButton("  OK", img)[0], image=getButton("  OK", img)[1])

    okButton.pack(expand=1, side=tk.LEFT, padx='3m', pady='3m', ipadx='2m', ipady='1m')

    # for the commandButton, bind activation events to the activation event
    # handler
    commandButton = okButton
    handler = __enterboxGetText
    for selectionEvent in dialogs.STANDARD_SELECTION_EVENTS:
        commandButton.bind("<{}>".format(selectionEvent), handler)

    # ------------------ neutral button -------------------------------
    if neutral!=None:
        nButton = ttk.Button(buttonsFrame, takefocus=1, compound="left",
                             text=getButton(neutral, img)[0], image=getButton(neutral, img)[1])

        if neutral!=None and neutral!="Очист.":
            #nButton.grid(column=1, row=0, padx='3m', pady='3m', ipadx='2m', ipady='1m')
            nButton.pack(expand=1, side=tk.LEFT, padx='3m', pady='3m', ipadx='2m', ipady='1m')

        # for the commandButton, bind activation events to the activation event
        # handler
        commandButton = nButton
        handler = __enterboxNeutral
        for selectionEvent in dialogs.STANDARD_SELECTION_EVENTS:
            commandButton.bind("<{}>".format(selectionEvent), handler)

    # ------------------ cancel button -------------------------------
    cancelButton = ttk.Button(buttonsFrame, takefocus=1, compound="left", text="Отмена")#getButton("  Отмена", img)[0], image=getButton("  Отмена", img)[1])

    #cancelButton.grid(column=2, row=0, padx='3m', pady='3m', ipadx='2m', ipady='1m')
    cancelButton.pack(expand=1, side=tk.RIGHT, padx='3m', pady='3m', ipadx='2m', ipady='1m')

    # for the commandButton, bind activation events to the activation event
    # handler
    commandButton = cancelButton
    handler = __enterboxCancel
    for selectionEvent in dialogs.STANDARD_SELECTION_EVENTS:
        commandButton.bind("<{}>".format(selectionEvent), handler)

    #create_footer(boxRoot)

    # ------------------- time for action! -----------------
    entryWidget.focus_force()  # put the focus on the entryWidget
    boxRoot.deiconify()
    boxRoot.mainloop()  # run it!

    # -------- after the run has completed ----------------------------------
    if root:
        root.deiconify()
    boxRoot.destroy()  # button_click didn't destroy boxRoot, so we do it now
    return __enterboxText

def __enterboxQuit():
    geom = boxRoot.geometry()
    dialogs.window_position = '+' + geom.split('+', 1)[1]
    dialogs.window_size = geom[0: geom.index("+")]
    return __enterboxCancel(None)


def __enterboxCancel(event):
    global __enterboxText
    geom = boxRoot.geometry()
    dialogs.window_position = '+' + geom.split('+', 1)[1]
    dialogs.window_size = geom[0: geom.index("+")]

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


# -------------------------------------------------------------------
# fileopenbox
# -------------------------------------------------------------------


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
        f = [path.normpath(x) for x in localRoot.tk.splitlist(ret_val)]
    else:
        f = path.normpath(ret_val)

    localRoot.destroy()

    if not f:
        return None
    return f


# -------------------------------------------------------------------
# fileboxsetup
# -------------------------------------------------------------------


def fileboxSetup(default, filetypes):
    if not default:
        default = path.join(".", "*")
    initialdir, initialfile = path.split(default)
    if not initialdir:
        initialdir = "."
    if not initialfile:
        initialfile = "*"
    initialbase, initialext = path.splitext(initialfile)
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


# -------------------------------------------------------------------
# class FileTypeObject for use with fileopenbox
# -------------------------------------------------------------------


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
        self.ext = path.splitext(filemask)[1]
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

def topText(value):
    form = tk.Toplevel()
    return
    def _saveSetting(event=None):

        value = entry.get().strip()
        form.destroy()

    bgColor = "gray94"
    width = 180
    padx = pady = 5
    form = tk.Toplevel(bg=bgColor, bd=1, relief='solid', borderwidth=1)
    width = 200
    height = 100
    return

    #form.geometry(dialogs.window_size + dialogs.window_position)
    form.wm_overrideredirect(True)
    form.grab_set()
    entry = tk.Entry(form, relief="flat")
    entry.pack(side="bottom", padx=5, pady=5, fill="x")
    entry.focus_force()
    tk.Message(form, bg=bgColor, width=width, text="123").pack(side="top", padx=padx, pady=pady)
    entry.insert(0, "456")
    
    entry.bind("<Return>", _saveSetting)
    entry.bind("<FocusOut>", _saveSetting)
    entry.bind("<Escape>", lambda x: form.destroy())
