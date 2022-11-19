#!/usr/bin/python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tk_FileDialog
import homepage
import os
import io2
import sys
import reports
import contacts
import house_op
import icons
import tkinter.font as tk_Font
from tkinter.scrolledtext import ScrolledText

class Desktop(ttk.Frame):
    """ Главный класс графического интерфейса на ПК """

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

    def __init__(self, msg="", title="", form="", choices=[], preselect=0, multiple_select=False,
                 positive=None, neutral=None, negative=None):

        print("Запускаем настольный GUI")
        ttk.Frame.__init__(self)
        self.boxRoot = self.master
        self.window_size = "550x620"  # размер и положение окна по умолчанию при первом запуске
        self.window_position = "+500+250"
        self.SimpleButtonSizeX = 8  # размеры кнопок в текстовом вводе
        self.SimpleButtonSizeY = 4
        self.TitleTextFont = None  # ("Arial", 7) # стиль текста, дублирующего title
        self.ToplevelShiftX = 7  # сдвиг позиции окна Toplevel от края
        self.ToplevelShiftY = 149
        self.GlobalPadX = 5
        self.GlobalPadY = 5
        self.LastPos = 0
        self.TitleColor = "grey20"  # цвет текста, дублирующего title
        self.inactive_background = "grey95"  # цвет фона для текстовых диалогов без редактирования
        self.PROPORTIONAL_FONT_FAMILY = ("Calibri", "Arial", "MS", "Sans", "Serif")
        try:
            self.MONOSPACE_FONT_FAMILY = (
                "Liberation Mono")  # , "DejaVu Sans Mono", "Cousine", "Lucida Console", "PT Mono", "Fira Mono", "Ubuntu Mono", "Courier New")
        except:
            self.MONOSPACE_FONT_FAMILY = self.PROPORTIONAL_FONT_FAMILY
        self.PROPORTIONAL_FONT_SIZE = self.TEXT_ENTRY_FONT_SIZE = 10
        self.MONOSPACE_FONT_SIZE = 11
        self.STANDARD_SELECTION_EVENTS = ["Return", "Button-1", "space"]
        try:
            with open("winpos.ini", "r") as file:
                line = file.read()
        except:
            with open("winpos.ini", "w") as file:
                file.write(self.window_size)
                file.write(self.window_position)
        else:
            self.window_position = '+' + line.split('+', 1)[1]
            self.window_size = line[0: line.index("+")]
        self.boxRoot.geometry(self.window_size + self.window_position)
        self.msg = msg
        self.title = title
        self.form = form
        self.choices = choices
        self.preselect = preselect
        self.multiple_select = multiple_select
        self.positive = positive
        self.neutral = neutral
        self.negative = negative
        self.textWidget = "" # для вывода текста из поля
        self.ipady = self.ipadx = 5
        self.systemMessage = ""
        self.initialize_images()
        try:
            self.boxRoot.wm_iconphoto(False, self.img[33]) # иконка - кросс-платформенный метод
        except:
            print("Не удалось отобразить иконку приложения")
        self.boxFont = tk_Font.nametofont("TkTextFont")
        self.boxRoot.title("Rocket Ministry")
        self.boxRoot.protocol('WM_DELETE_WINDOW', self.exit)
        self.boxRoot.bind("<Escape>", self.cancel_pressed)
        self.create_menu() # меню
        self.create_search_widget()
        self.create_footer()
        self.create_side_buttons()
        self.create_bottom_buttons()
        self.create_top_buttons()
        self.create_msg_widget()
        self.create_choicebox()
        self.bindHotKeys()
        self.refresh_timer()
        self.choiceboxWidget.focus_force()

    def update(self, msg="", title="", form="", choices=[], preselect=0, multiple_select=False,
               positive=None, neutral=None, negative=None):

        """ Обновление интерфейса - к этой функции обращаются все процедуры """

        self.msg = msg
        self.title = title
        self.form = form
        self.choices = choices
        self.preselect = preselect
        self.multiple_select = multiple_select
        self.positive = positive
        self.neutral = neutral
        self.negative = negative

        # Обновление верхних кнопок для множественного списка (если он активен)

        if self.multiple_select == True:
            self.positiveButton.grid_forget()
            self.neutralButton.grid_forget()
            self.selectAllButton.grid(row=0, column=0, sticky="we", padx=self.GlobalPadX, ipadx=0, ipady=self.GlobalPadY)
            self.clearAllButton.grid(row=0, column=1, sticky="we", padx=self.GlobalPadX, ipadx=0, ipady=self.GlobalPadY)
        else:
            if self.positive != None:
                self.positiveButton.grid(column=0, row=1, sticky="e")
            if self.neutral != None:
                self.neutralButton.grid(column=1, row=1, sticky="w")
            self.selectAllButton.grid_forget()
            self.clearAllButton.grid_forget()

        # Обновление дисплея уведомлений

        if self.systemMessage != "":
                self.display.config(state="normal")
                self.display.delete('1.0', tk.END)
                self.display.insert(tk.END, self.systemMessage)
                self.display.config(state="disabled")

        # Обновление "title" и поиска

        if len(self.title)>1 and self.title[1]==" " and self.form != "firstCallMenu" and "Этаж" not in self.title and self.form!="flatView":
            msg = self.title[1:]
        else:
            msg = self.title
        self.messageArea.config(text=msg)

        # Обновление центрального списка

        self.choiceboxWidget.delete(0, "end")
        for choice in self.choices:
            self.choiceboxWidget.insert(tk.END, choice)
        if self.multiple_select==True:
            self.choiceboxWidget.configure(selectmode=tk.MULTIPLE)
        else:
            self.choiceboxWidget.configure(selectmode=tk.BROWSE)
        self.preselect_choice()
        self.choiceboxWidget.focus_force()

        # Обновление нижних кнопок

        if self.positive != None:
            if self.positive == icons.icon("plus", simplified=False):  # если плюс, заменяем его на более красивый
                self.positive = "  Добавить [Ins]"
            elif self.positive == icons.icon("down"):
                self.positive += " [Ins]"
            self.positiveButton.config(text=self.getButton(self.positive, self.img)[0],
                                       image=self.getButton(self.positive, self.img)[1])
            self.positiveButton.grid(column=0, row=0, sticky="we", padx=self.GlobalPadX,
                                     ipadx=self.ipadx*5, ipady=self.ipady)
        else:
            self.positiveButton.grid_forget()

        if self.neutral != None:
            self.neutral += " [Ctrl+Ins]"

            self.neutralButton.config(text=self.getButton(self.neutral, self.img)[0],
                                      image=self.getButton(self.neutral, self.img)[1])

            self.neutralButton.grid(column=1, row=0, sticky="we", padx=self.GlobalPadX, ipadx=self.ipadx*5, ipady=self.ipady)
        else:
            self.neutralButton.grid_forget()

        if self.multiple_select:
            self.selectAllButton.grid(column=0, row=0, padx=self.GlobalPadX, pady=self.GlobalPadY,
                                      ipady=self.ipady, ipadx=self.ipadx)
            self.clearAllButton.grid(column=1, row=0, padx=self.GlobalPadX, pady=self.GlobalPadY,
                                     ipady=self.ipady, ipadx=self.ipadx)
        else:
            self.selectAllButton.grid_forget()
            self.clearAllButton.grid_forget()

        # Обновление боковых кнопок

        self.terButton.config(text="Участки (%d)" % len(io2.houses), image=self.img[21])

        self.conButton.config(text="Контакты (%d)" % contacts.getContactsAmount(date=1)[0])

        rep, gap = reports.getCurrentHours()
        self.repButton.config(text="Отчет (%s)" % rep)

        self.noteButton.config(text="Блокнот (%d)" % len(io2.resources[0]))

        # Обновление футера

        self.stats.config(text = " %d%%" % house_op.countTotalProgress()) # статистика

        datedFlats = contacts.getContactsAmount(date=1)[1] # встречи на сегодня
        if len(datedFlats)>0:
            self.meeting.pack(side=tk.LEFT, padx=10)
            self.meeting.config(image=self.img[35])
        else:
            self.meeting.config(image=None)
            self.meeting.pack_forget()

        if io2.settings[2][11] == 1: # напоминание сдать отчет
            self.remind.pack(side=tk.LEFT, padx=10)
            self.remind.config(image=self.img[36])
        else:
            self.remind.config(image=None)
            self.remind.pack_forget()

        if house_op.calcDueTers() > 0: # просроченные участки
            self.dueter.pack(side=tk.LEFT, padx=10)
            self.dueter.config(image=self.img[37])
        else:
            self.dueter.config(image=None)
            self.dueter.pack_forget()

        if gap >= 0:
            self.smile.config(text = " +" + reports.timeFloatToHHMM(gap), image=self.img[38])
            self.smile.pack(side=tk.LEFT, padx=10)
            self.CreateToolTip(self.smile, "Вы молодец, так держать!")
        else:
            self.smile.config(text = " -" + reports.timeFloatToHHMM(-gap), image=self.img[39])
            self.smile.pack(side=tk.LEFT, padx=10)
            self.CreateToolTip(self.smile, "Вы можете лучше")
        if io2.settings[0][3] == 0:
            self.smile.pack_forget()

    def pushTopLevel(self, msg="", title="", default="", mask="", form="", largeText=False, disabled=False,
                     doublesize=False, height=2, positive=None, neutral=None, negative=None, lib=False):
        """ Поднимаем Toplevel и получаем от него результат """
        self.topLevelResult = ""
        return self.toplevelbox(msg, title, default, mask, form, largeText, disabled, doublesize, height,
                             positive, neutral, negative, lib)

    def refresh_timer(self):
        """ Обновление таймера """
        if reports.updateTimer(io2.settings[2][6]) >= 0:
            self.time2 = reports.updateTimer(io2.settings[2][6])
        else:
            self.time2 = reports.updateTimer(io2.settings[2][6]) + 24
        if io2.settings[2][6] > 0:
            self.timerTime = " (%s)" % reports.timeFloatToHHMM(self.time2)
        else:
            self.timerTime = "  "
        self.timButton.config(text="Таймер%s" % self.timerTime, compound="top",
                              image=self.getButton("Таймер%s" % self.timerTime, self.img)[1])
        self.boxRoot.after(1000, self.refresh_timer)

    # Основные операции

    def exit(self):
        """ Полный выход из приложения """
        self.stop()
        with open("winpos.ini", "w") as file: # Запись положения окна в файл при выходе
            file.write(self.window_size)
            file.write(self.window_position)
        self.boxRoot.destroy()
        sys.exit(0)

    def run(self):
        """ Запуск и обновление главного окна с возвратом значений из него """
        self.boxRoot.mainloop()
        return self.choices

    def stop(self):
        """ Остановка процедур в окне и возврат управления логике """
        self.getWindowPosition()
        return self.choices

    def callback(self, command="", choices=[]):
        """ Обработка действий пользователя """
        if command == 'update':  # OK was pressed
            self.LastPos = self.choiceboxWidget.curselection()[0]
            self.choices = choices
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

    # Действия кнопок

    def cancel_pressed(self, event=None):
        self.callback(command='cancel', choices=self.get_choices())

    def neutral_pressed(self, event=None):
        if self.neutral != None:
            self.callback(command='neutral', choices="neutral")

    def ok_pressed(self, event=None):
        self.callback(command='update', choices=self.get_choices())

    def positive_pressed(self, event=None):
        if self.positive != None:
            self.callback(command='update', choices="positive")

    def menu_pressed(self, choice, event=None):
        self.callback(command=choice, choices=choice)

    def search_requested(self, choice, event=None):
        self.callback(command=choice, choices=choice)

    def go_home(self, event=None):
        self.callback(command="home", choices="home")

    def contacts_pressed(self, event=None):
        self.callback(command='contacts', choices="contacts")

    def ter_pressed(self, event=None):
        self.callback(command='ter', choices="ter")

    def report_pressed(self, event=None):
        self.callback(command='report', choices="report")

    def notebook_pressed(self, event=None):
        self.callback(command='notebook', choices="notebook")

    def stat_pressed(self, event=None):
        self.callback(command='statistics', choices="statistics")

    def timer_pressed(self, event=None):
        self.refresh_timer()
        self.callback(command='timer', choices="timer")

    def serviceyear_pressed(self, event=None):
        self.callback(command='serviceyear', choices="serviceyear")

    # Действия в списке

    def preselect_choice(self):
        """ Выбор пункта списка """
        if self.form!="porchViewGUIList" and self.form!="porchViewGUIOneFloor" and self.form!="firstCallMenu"\
                and self.form!="porchViewGUIOneFloor": # в этих формах работает встроенное запоминание позиции
            if self.LastPos <= len(self.choices)-1:
                self.choiceboxWidget.select_set(self.LastPos)
                self.choiceboxWidget.activate(self.LastPos)
            else:
                self.choiceboxWidget.select_set(len(self.choices)-1) # последняя позиция ниже текущего списка
                self.choiceboxWidget.activate(len(self.choices)-1)
        elif self.preselect != None:
            self.choiceboxWidget.select_set(self.preselect)
            self.choiceboxWidget.activate(self.preselect)

    def get_choices(self):
        """ Получение вариантов списка для передачи"""
        choices_index = self.choiceboxWidget.curselection()
        if not choices_index:
            return None
        if self.multiple_select:
            selected_choices = [self.choiceboxWidget.get(index)
                                for index in choices_index]
        else:
            selected_choices = self.choiceboxWidget.get(choices_index)
        return selected_choices

    def choiceboxClearAll(self, event=None):
        self.choiceboxWidget.selection_clear(0, len(self.choices) - 1)

    def choiceboxSelectAll(self, event=None):
        self.choiceboxWidget.selection_set(0, len(self.choices) - 1)

    def listContextMenu(self, e=None): # контекстное меню списка
        menu = tk.Menu(self.boxRoot, tearoff=0)
        menu.add_command(
            label=self.getButton("  OK", self.img)[0],
            image=self.getButton("  OK", self.img)[1],
            compound="left",
            command=self.ok_pressed
        )
        if self.positive != None:
            if "[" in self.positive:
                text = self.positive[0: self.positive.index("[")]
            else:
                text = self.positive
            menu.add_command(
                label=self.getButton(text, self.img)[0],
                image=self.getButton(text, self.img)[1],
                compound="left",
                command=self.positive_pressed
            )
        if self.neutral != None:
            if "[" in self.neutral:
                text = self.neutral[0: self.neutral.index("[")]
            else:
                text = self.neutral
            menu.add_command(
                label=self.getButton(text, self.img)[0],
                image=self.getButton(text, self.img)[1],
                compound="left",
                command=self.neutral_pressed
            )
        menu.add_separator()
        menu.add_command(label="Копировать", command=lambda: e.widget.event_generate("<<Copy>>"))
        menu.tk.call("tk_popup", menu, e.x_root, e.y_root)

    # Элементы окна

    def create_context_menu(self, e=None):
        """ Контекстное меню для всех окон, главного и второстепенных """
        menu = tk.Menu(self.boxRoot, tearoff=0)
        menu.add_command(label="Вырезать", command=lambda: e.widget.event_generate("<<Cut>>"))
        menu.add_command(label="Копировать", command=lambda: e.widget.event_generate("<<Copy>>"))
        menu.add_command(label="Вставить", command=lambda: e.widget.event_generate("<<Paste>>"))
        menu.add_command(label="Удалить", command=lambda: e.widget.event_generate("<<Clear>>"))
        menu.add_separator()
        menu.add_command(label="Выделить все", command=lambda: e.widget.event_generate("<<SelectAll>>"))
        menu.tk.call("tk_popup", menu, e.x_root, e.y_root)

    def create_menu(self):
        """ Главное меню """
        def fileImport(self):
            self.callback(command="import", choices="import")

        def fileRestore(self):
            self.callback(command="restore", choices="restore")

        def fileExport(self):
            self.callback(command="export", choices="export")

        def fileWipe(self):
            self.callback(command="wipe", choices="wipe")

        def fileExit(self):
            self.callback(command="exit", choices="exit")

        def menuStats():
            self.callback(command="statistics", choices="statistics")

        def menuAbout():
            self.callback(command="about", choices="about")

        self.menu = tk.Menu(self.boxRoot, tearoff=0)
        self.boxRoot.config(menu=self.menu)
        self.filemenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Файл", menu=self.filemenu)
        self.settingsMenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Настройки", menu=self.settingsMenu)
        self.menu.add_command(label="Статистика", command=menuStats)
        self.menu.add_command(label="О программе", command=menuAbout)

        # Файл

        self.filemenu.add_command(label="Импорт", compound="left", image=self.img[27], command=lambda s=self: fileImport(s))
        self.filemenu.add_command(label="Экспорт", compound="left", image=self.img[26], command=lambda s=self: fileExport(s))
        self.filemenu.add_command(label="Восстановление", compound="left", image=self.img[28],
                             command=lambda s=self: fileRestore(s))
        self.filemenu.add_command(label="Очистка", compound="left", image=self.img[29], command=lambda s=self: fileWipe(s))

        if io2.Simplified == 0:
            self.filemenu.add_separator()
            self.filemenu.add_command(label="Выход с экспортом", command=lambda s=self: fileExit(s))

        # Настройки

        options = homepage.preferences(getOptions=True)  # загрузка настроек из основного интерфейса
        self.settings = []
        for i in range(len(options)):
            if options[i][0] == "√":
                self.settings.append(tk.IntVar())
                self.settings[i].set(1)
                self.settingsMenu.add_checkbutton(
                    label=options[i][2:],
                    variable=self.settings[i],
                    compound="left",
                    command=lambda x=options[i], y=self: homepage.feedSetting(x, y)
                )
            elif options[i][0] == "×":
                self.settings.append(tk.IntVar())
                self.settings[i].set(0)
                self.settingsMenu.add_checkbutton(
                    label=options[i][2:],
                    variable=self.settings[i],
                    compound="left",
                    command=lambda x=options[i], y=self: homepage.feedSetting(x, y)
                )
            elif options[i][0] == "□":
                self.settings.append(tk.StringVar())
                self.settingsMenu.add_command(
                    label=options[i][2:],
                    compound="left",
                    command=lambda x=options[i], y=self: homepage.feedSetting(x, y)
                )

    def find(self, event=None):
        """ Поиск в интерфейсе """
        query=self.search.get().strip()
        self.search_requested(choice="[search]" + query)

    def create_search_widget(self):
        """ Поиск и монитор уведомлений """
        self.searchFrame = ttk.Frame(master=self.boxRoot)
        self.searchFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES,
                              padx=self.GlobalPadX)#, ipady=self.ipady, ipadx=self.ipadx)
        self.display = ScrolledText(self.searchFrame, width=40, font=("Arial", 8), fg="green", bg=self.inactive_background, height=2, state="disabled")
        self.display.pack(side=tk.LEFT, padx=1, pady=3)

        self.icon = ttk.Button(self.searchFrame, image=self.img[16], takefocus=0) # кнопка с лупой
        self.icon.pack(side=tk.RIGHT, padx=1, pady=1)
        self.icon.bind("<1>", self.find)

        self.style = ttk.Style() # поисковая строка
        self.search = tk.Entry(self.searchFrame, width=25, font=("", 9), fg="gray", relief="groove", takefocus=0)
        self.search.pack(side=tk.RIGHT, padx=1, pady=1)
        self.search.insert(0, "Поиск [F3]")
        self.search.bind("<Return>", self.find)
        def temp_text(e):
            if self.search.get()=="Поиск [F3]":
                self.search.delete(0, "end")
            self.search.config(fg = "black")
        self.search.bind("<FocusIn>", temp_text)

        self.search.bind("<3>", self.create_context_menu)

    def create_top_buttons(self):
        """ Верхние кнопки ok, назад и множественный выбор """
        self.topButtonFrame = tk.Frame(self.boxRoot)
        self.topButtonFrame.pack(side=tk.TOP, expand=1, fill="both")

        self.sideButtonIpadX = 0
        self.topButtonFrame.columnconfigure(0, weight=0)
        self.topButtonFrame.columnconfigure(1, weight=10)

        self.backButton = ttk.Button(self.topButtonFrame, takefocus=0, compound="left",  # кнопка назад
                                     text=self.getButton("  [Esc]", self.img)[0],
                                     image=self.getButton("  [Esc]", self.img)[1])
        self.backButton.bind("<Return>", self.cancel_pressed)
        self.backButton.bind("<Button-1>", self.cancel_pressed)
        self.backButton.bind("<space>", self.cancel_pressed)
        self.backButton.bind("<Escape>", self.cancel_pressed)
        self.backButton.grid(row=0, column=0, sticky="w", padx=self.GlobalPadX, ipadx=0, ipady=self.ipady)#pack(side=tk.RIGHT, padx=self.padx, ipadx=0, ipady=self.ipady)

        self.okButton = ttk.Button(self.topButtonFrame, takefocus=0, compound="left",  # кнопка OK в списке
                                   text=self.getButton("  OK [Enter]", self.img)[0],
                                   image=self.getButton("  OK [Enter]", self.img)[1])
        self.okButton.bind("<Return>", self.ok_pressed)
        self.okButton.bind("<Button-1>", self.ok_pressed)
        self.okButton.bind("<space>", self.ok_pressed)
        self.okButton.grid(row=0, column=1, sticky="we", padx=self.GlobalPadX, ipadx=self.ipadx * 5, ipady=self.ipady)  # pack(side=tk.RIGHT, fill="both", expand=tk.YES, padx=self.padx, ipadx=self.ipadx*5, ipady=self.ipady)

    def create_msg_widget(self):
        """ Текст, дублирующий title с Android """
        self.msgFrame = tk.Frame(self.boxRoot)
        self.msgFrame.pack(side=tk.TOP, expand=1, fill='both')
        #self.messageArea = tk.Label(self.msgFrame, fg="grey20")
        self.messageArea = tk.Label(self.msgFrame, font = self.TitleTextFont, fg=self.TitleColor)
        self.messageArea.pack(side=tk.TOP, expand=1, fill='y')

    def create_choicebox(self):
        """ Основной список """
        self.choiceboxFrame = ttk.Frame(master=self.boxRoot, relief="flat")
        self.choiceboxFrame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.YES)

        # --------  put the self.choiceboxWidget in the self.choiceboxFrame ---
        self.choiceboxWidget = tk.Listbox(self.choiceboxFrame,
                                          height=500,
                                          borderwidth="2m", relief="flat",
                                          bg="white"
        )

        self.choiceboxWidget.config( font = (self.MONOSPACE_FONT_FAMILY, self.MONOSPACE_FONT_SIZE) )

        # add a vertical scrollbar to the frame
        self.rightScrollbar = ttk.Scrollbar(self.choiceboxFrame, orient=tk.VERTICAL,
                                      command=self.choiceboxWidget.yview)
        self.choiceboxWidget.configure(yscrollcommand=self.rightScrollbar.set)

        # add a horizontal scrollbar to the frame
        self.bottomScrollbar = tk.Scrollbar(self.choiceboxFrame,
                                       orient=tk.HORIZONTAL,
                                       command=self.choiceboxWidget.xview)
        self.choiceboxWidget.configure(xscrollcommand=self.bottomScrollbar.set)

        self.bottomScrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.rightScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.choiceboxWidget.pack(side=tk.TOP, padx=self.GlobalPadX, pady=self.GlobalPadY, expand=tk.YES, fill=tk.BOTH)

        # Bind the keyboard events
        self.choiceboxWidget.bind("<Return>", self.ok_pressed)
        self.choiceboxWidget.bind("<Double-Button-1>", self.ok_pressed)
        self.choiceboxWidget.bind("<BackSpace>", self.cancel_pressed)
        self.choiceboxWidget.bind("<3>", self.listContextMenu)

        def focus_search(event):
            self.search.focus()
        self.boxRoot.bind("<F3>", focus_search)

    def create_side_buttons(self):
        """ Большие кнопки навигации """
        self.side_menu = ttk.Frame(self.boxRoot)
        self.side_menu.pack(side=tk.RIGHT)  # grid(column=0, row=1, columnspan=3, sticky="nsew", padx=self.padx, pady=self.pady*2, ipady=self.ipady, ipadx=self.ipadx)

        ipadxButton = 5
        ipadyButton = 1
        compound = "top"
        side = "top"
        expand = "yes"
        fill = "both"

        self.terButton = ttk.Button(self.side_menu, text="Участки", compound=compound, image=self.img[21])
        self.terButton.pack(side=side, padx=self.GlobalPadX, pady=self.GlobalPadY, ipadx=ipadxButton, ipady=ipadyButton,
                            expand=expand, fill=fill)
        # grid(row=0, column=0, padx=padx2, pady=pady2, ipadx=ipadxButton, ipady=ipadyButton, sticky="nesw")
        self.terButton.bind("<Return>", self.ter_pressed)
        self.terButton.bind("<Button-1>", self.ter_pressed)
        self.terButton.bind("<space>", self.ter_pressed)

        self.conButton = ttk.Button(self.side_menu, text="Контакты", compound=compound, image=self.img[20])
        self.conButton.pack(side=side, padx=self.GlobalPadX, pady=self.GlobalPadY, ipadx=ipadxButton, ipady=ipadyButton,
                            expand=expand, fill=fill)
        # grid(row=0, column=1, padx=padx2, pady=pady2, ipadx=ipadxButton + 12, ipady=ipadyButton, sticky="nesw")
        self.conButton.bind("<Return>", self.contacts_pressed)
        self.conButton.bind("<Button-1>", self.contacts_pressed)
        self.conButton.bind("<space>", self.contacts_pressed)

        self.side_menu.columnconfigure(0, weight=10)
        self.side_menu.columnconfigure(1, weight=0)
        self.side_menu.columnconfigure(0, weight=0)

        self.repButton = ttk.Button(self.side_menu, text="Отчет", compound=compound, image=self.img[22])
        self.repButton.pack(side=side, padx=self.GlobalPadX, pady=self.GlobalPadY, ipadx=ipadxButton, ipady=ipadyButton,
                            expand=expand, fill=fill)
        # grid(row=0, column=2, padx=padx2, pady=pady2, ipadx=ipadxButton, ipady=ipadyButton, sticky="nesw")
        self.repButton.bind("<Return>", self.report_pressed)
        self.repButton.bind("<Button-1>", self.report_pressed)
        self.repButton.bind("<space>", self.report_pressed)

        self.noteButton = ttk.Button(self.side_menu, text="Блокнот", compound=compound, image=self.img[34])
        self.noteButton.pack(side=side, padx=self.GlobalPadX, pady=self.GlobalPadY, ipadx=ipadxButton, ipady=ipadyButton,
                             expand=expand, fill=fill)
        # grid(row=0, column=1, padx=padx2, pady=pady2, ipadx=ipadxButton + 12, ipady=ipadyButton, sticky="nesw")
        self.noteButton.bind("<Return>", self.notebook_pressed)
        self.noteButton.bind("<Button-1>", self.notebook_pressed)
        self.noteButton.bind("<space>", self.notebook_pressed)

        self.servButton = ttk.Button(self.side_menu, text="Служебный год", compound=compound, image=self.img[24])
        self.servButton.pack(side=side, padx=self.GlobalPadX, pady=self.GlobalPadY, ipadx=ipadxButton, ipady=ipadyButton,
                            expand=expand, fill=fill)
        # grid(row=1, column=1, padx=padx2, pady=pady2, ipadx=ipadxButton, ipady=ipadyButton, sticky="nesw")
        self.servButton.bind("<Return>", self.serviceyear_pressed)
        self.servButton.bind("<Button-1>", self.serviceyear_pressed)
        self.servButton.bind("<space>", self.serviceyear_pressed)

        self.timButton = ttk.Button(self.side_menu, text="Таймер", compound=compound)
        self.timButton.pack(side=side, padx=self.GlobalPadX, pady=self.GlobalPadY, ipadx=ipadxButton, ipady=ipadyButton,
                            expand=expand, fill=fill)
        # grid(row=1, column=1, padx=padx2, pady=pady2, ipadx=ipadxButton, ipady=ipadyButton, sticky="nesw")
        self.timButton.bind("<Return>", self.timer_pressed)
        self.timButton.bind("<Button-1>", self.timer_pressed)
        self.timButton.bind("<space>", self.timer_pressed)

    def create_bottom_buttons(self):
        """ Кнопки управления списком """
        self.buttonsFrame = ttk.Frame(self.boxRoot)
        self.buttonsFrame.pack(side=tk.BOTTOM, fill="y", expand=1)

        self.positiveButton = ttk.Button(self.buttonsFrame, takefocus=tk.YES, compound="left",
                                        text=self.getButton(self.positive, self.img)[0],
                                        image=self.getButton(self.positive, self.img)[1])
        self.positiveButton.bind("<Return>", self.positive_pressed)
        self.positiveButton.bind("<Button-1>", self.positive_pressed)
        self.positiveButton.bind("<space>", self.positive_pressed)

        self.neutralButton = ttk.Button(self.buttonsFrame, takefocus=tk.YES, compound="left",
                                        text=self.getButton(self.neutral, self.img)[0],
                                        image=self.getButton(self.neutral, self.img)[1])

        self.neutralButton.bind("<Return>", self.neutral_pressed)
        self.neutralButton.bind("<Button-1>", self.neutral_pressed)
        self.neutralButton.bind("<space>", self.neutral_pressed)

        # Кнопки, которые появляются только на множественном списке (Checklist) вместо positive и neutral

        self.selectAllButton = ttk.Button(self.buttonsFrame, text="Выбрать все")
        self.clearAllButton = ttk.Button(self.buttonsFrame, text="Снять все")
        self.selectAllButton.bind("<Button-1>", self.choiceboxSelectAll)
        self.clearAllButton.bind("<Button-1>", self.choiceboxClearAll)

        #ttk.Label(self.buttonsFrame, font=("Arial", 2)).grid(row=99) # небольшой разрыв под нижними кнопками для красоты

    # Вспомогательные функции

    def getWindowPosition(self):
        """ Обновление координат окна """
        geom = self.boxRoot.geometry()
        self.window_position = '+' + geom.split('+', 1)[1]
        if os.name == "nt":
            x_size = int(geom[0: geom.index("x")])
            y_size = int(geom[geom.index("x") + 1: geom.index("+")])
            # коррекция высоты окна на 20 на Windows, потому что оно почему-то самопроизвольно уменьшается
            self.window_size = "%dx%d" % (x_size, y_size + 20)
        else:
            self.window_size = geom[0: geom.index("+")]
        self.boxRoot.quit()

    def getButton(self, text="", img=[]):
        """ Выдает по запросу обработанный текст и картинку """
        if text != None:
            text2 = text[2:]
        else:
            return None, None
        image = None
        if "Таймер" in text:
            if ":" in text:
                image = img[1]
            else:
                image = img[0]
        elif reports.monthName()[2] in text:
            image = img[28]
        elif "Добавить" in text:
            image = img[2]
        elif "Сорт." in text and icons.icon("phone2") in text:
            image = img[6]
        elif "Сорт." in text and icons.icon("numbers") in text:
            image = img[7]
        elif "Сорт." in text and icons.icon("pin") in text:
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
        elif icons.icon("export") in text:
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

    def bindHotKeys(self):
        """ Горячие клавиши """
        self.boxRoot.bind("<Insert>", self.positive_pressed)
        self.boxRoot.bind("<Control-Insert>", self.neutral_pressed)
        self.boxRoot.bind("<F1>", self.go_home)
        self.boxRoot.bind("<F2>", self.contacts_pressed)
        self.boxRoot.bind("<F4>", self.report_pressed)
        self.boxRoot.bind("<F5>", self.notebook_pressed)
        self.boxRoot.bind("<F6>", self.serviceyear_pressed)
        self.boxRoot.bind("<F7>", self.timer_pressed)

    def initialize_images(self):
        """ Загрузка картинок """
        ImgList = [
            "timer1.png"  # 0
            , "timer2.png"  # 1
            , "plus.png"  # 2
            , "sort.png"  # 3
            , "details.png"  # 4
            , "cancel.png"  # 5
            , "telephone.png"  # 6
            , "sort_numbers.png"  # 7
            , "pin.png"  # 8
            , "save.png"  # 9
            , "cancel.png"  # 10
            , "cancel.png"  # 11
            , "cancel.png"  # 12
            , "send.png"  # 13
            , "mark.png"  # 14
            , "calc.png"  # 15
            , "search.png"  # 16
            , "arrow_up.png"  # 17
            , "arrow_down.png"  # 18
            , "cancel.png"  # 19
            , "user.png"  # 20
            , "house.png"  # 21
            , "report.png"  # 22
            , "statistics.png"  # 23
            , "calendar.png"  # 24
            , "log.png"  # 25
            , "export.png"  # 26
            , "import.png"  # 27
            , "restore.png"  # 28
            , "clear.png"  # 29
            , "cancel.png"  # 30
            , "arrow_left.png"  # 31
            , "home.png"  # 32
            , "rocket64.png"  # 33
            , "notebook.png"  # 34
            , "calendar2.png"  # 35
            , "bell.png"  # 36
            , "error.png"  # 37
            , "happy.png"  # 38
            , "sad.png"     # 39
        ]
        self.img = []
        for image in ImgList:
            self.img.append(tk.PhotoImage(file=image))

    def create_footer(self):
        """ Подвал страницы """
        self.footerFrame = tk.Frame()
        self.footerFrame.pack(side=tk.BOTTOM, fill="both", expand=tk.YES)

        ttk.Separator(self.footerFrame, orient='horizontal').pack(fill='x')

        self.stats = tk.Label(self.footerFrame, compound="left", image = self.img[23], cursor="cross") # обработка участков
        self.stats.bind("<1>", self.stat_pressed)
        self.stats.pack(side=tk.LEFT)
        self.CreateToolTip(self.stats, "Средний уровень обработки ваших участков")

        def contacts_pressed_with_sort(event=None): # встречи на сегодня
            io2.settings[0][4]="в"
            self.contacts_pressed()
        self.meeting = tk.Label(self.footerFrame, compound="left", cursor="cross")
        self.meeting.bind("<1>", contacts_pressed_with_sort)
        self.CreateToolTip(self.meeting, "Встречи с контактами, запланированные на сегодня")

        def report_show(event=None): # напоминание сдать отчет
            report = reports.Report()
            report.showLastMonthReport()
        self.remind = tk.Label(self.footerFrame, compound="left", cursor="cross")
        self.remind.bind("<1>", report_show)
        self.CreateToolTip(self.remind, "Не забудьте сдать отчет!")

        def dueter_show(event=None):   # просроченный участок
            io2.settings[0][19] = "д"
            self.ter_pressed()
        self.dueter = tk.Label(self.footerFrame, compound="left", cursor="cross")
        self.dueter.bind("<1>", dueter_show)
        self.CreateToolTip(self.dueter, "У вас есть участки, которым больше полугода!")

        self.smile = tk.Label(self.footerFrame, compound="left", cursor="cross") # смайлик про запас или отставание
        self.smile.bind("<1>", self.report_pressed)

        ttk.Sizegrip(self.footerFrame).pack(side=tk.RIGHT) # грип

    def toplevelbox(self, msg="", title="", default="", mask=None, form="", largeText=False, disabled=False,
                 doublesize=False, height=5, positive=None, neutral=None, negative=None, lib=False):
        """ Создание всплывающего окна для ввода текста или показа информации """

        def __boxGetText(event=None):
            try:
                if disabled == True:
                    self.topLevelResult = "positive"
                elif largeText==False:
                    self.topLevelResult = entryWidget.get()
                else:
                    self.topLevelResult = textArea.get(0.0, 'end-1c')
            except:
                self.topLevelResult = None
            boxRoot.quit()

        def __boxCancel(event=None):
            self.topLevelResult = None
            boxRoot.quit()

        def __boxNeutral(event=None):
            self.topLevelResult = "neutral"
            boxRoot.quit()

        if title is None:
            title = ""
        if default is None:
            default = ""

        root = self.boxRoot
        boxRoot = tk.Toplevel()
        try:
            boxRoot.grab_set()
        except:
            pass
        boxRoot.withdraw()
        boxRoot.protocol('WM_DELETE_WINDOW', __boxCancel)
        boxRoot.title("Rocket Ministry")
        if form == "porchText" or doublesize == True:
            boxRoot.geometry("402x447" + self.geomShift(self.window_position))
        elif largeText==False:
            boxRoot.geometry("402x220" + self.geomShift(self.window_position))
        else:
            boxRoot.geometry("402x300" + self.geomShift(self.window_position))
        if lib == True:
            height = 1
            boxRoot.geometry("270x140" + self.geomShift(self.window_position))
        else:
            height = height
        boxRoot.bind("<Escape>", __boxCancel)
        mainFrame = tk.Frame(boxRoot)
        mainFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        bottomFrame = tk.Frame(boxRoot)
        bottomFrame.pack(side=tk.BOTTOM, fill=tk.BOTH)

        # Верхняя строка (дублирование title) - fillablebox
        msgFrame = tk.Frame(mainFrame)
        msgFrame.pack(side=tk.TOP, fill='y')
        if title.strip() == "":
            text = None
        elif title[1] == " ":
            text = title[2:]
        else:
            text = title
        if largeText==True and msg.strip() != "" and disabled == False:
            text = text + " | " + msg
        messageArea = tk.Label(msgFrame, text=text, fg=self.TitleColor)
        if text != None:
            messageArea.pack(side=tk.TOP, expand=1, fill='both', padx=self.GlobalPadX)


        # ------------- define the messageFrame ---------------------------------
        messageFrame = tk.Frame(master=mainFrame)
        messageFrame.pack(side=tk.TOP, fill=tk.BOTH)

        # ------------- define the entryFrame ---------------------------------
        entryFrame = ttk.Frame(master=mainFrame)
        entryFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # ------------- define the buttonsFrame ---------------------------------
        buttonsFrame = ttk.Frame(master=bottomFrame)
        buttonsFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # -------------------- the msg widget ----------------------------
        # messageWidget = tk.Message(messageFrame, width="4i", text=msg)

        if form == "porchText":
            height = 18
            font = (self.MONOSPACE_FONT_FAMILY, self.MONOSPACE_FONT_SIZE)
        else:
            font = (self.PROPORTIONAL_FONT_FAMILY, self.PROPORTIONAL_FONT_SIZE)

        if largeText==False and disabled==False:
            messageWidget = tk.Text(
                messageFrame,
                padx=self.GlobalPadX,
                pady=self.GlobalPadY,
                height=height,
                width=200,
                background=self.inactive_background,
                font=font,
                wrap=tk.WORD,
            )
            messageWidget.delete(1.0, tk.END)
            messageWidget.insert(tk.END, msg)
            messageWidget.config(state=tk.DISABLED)
            messageWidget.pack(side=tk.TOP, expand=1, fill=tk.BOTH, padx='3m', pady='3m')

        # --------- entryWidget ----------------------------------------------
        #if largeText == False and disabled == False:
            entryWidget = ttk.Entry(entryFrame, takefocus=1, width=500)  # ширина окна текста
            entryWidget.configure(
                font=(self.MONOSPACE_FONT_SIZE, self.TEXT_ENTRY_FONT_SIZE))
            if mask:
                entryWidget.configure(show=mask)

            entryWidget.pack(side=tk.LEFT, padx="5m")
            entryWidget.bind("<Return>", __boxGetText)
            entryWidget.bind("<Escape>", __boxCancel)
            entryWidget.bind("<Control-Insert>", __boxNeutral)
            entryWidget.insert(0, default)
            entryWidget.bind_class("TEntry", "<3>", self.create_context_menu)
            entryWidget.focus_force()  # put the focus on the entryWidget

        else:
            ### Создание большого поля вместо одной строки

            textFrame = tk.Frame(entryFrame, takefocus=0)
            textFrame.pack(side=tk.LEFT, padx=self.GlobalPadX)

            if doublesize==True:
                height = 21
            else:
                height = 12
            textArea = tk.Text(
                textFrame,
                padx=self.GlobalPadX,  # default_hpad_in_chars * calc_character_width(),
                pady=self.GlobalPadY,  # default_hpad_in_chars * calc_character_width(),
                height=height,  # TextBoxHeight,  # lines                     # высота текстового окна
                width=500,  # TextBoxWidth,   # chars of the current font # ширина текстового окна
                takefocus=1,
                font=(self.PROPORTIONAL_FONT_FAMILY, self.PROPORTIONAL_FONT_SIZE),
            )

            textArea.configure(wrap=tk.WORD)
            textArea.delete(1.0, tk.END)
            if disabled==False:
                textArea.insert(tk.END, default, "normal")
            else:
                textArea.insert(tk.END, msg, "normal")
                textArea.config(state=tk.DISABLED, bg=self.inactive_background)

            # some simple keybindings for scrolling
            boxRoot.bind("<Next>", textArea.yview_scroll(1, tk.PAGES))
            boxRoot.bind(
                "<Prior>", textArea.yview_scroll(-1, tk.PAGES))

            boxRoot.bind("<Right>", textArea.xview_scroll(1, tk.PAGES))
            boxRoot.bind("<Left>", textArea.xview_scroll(-1, tk.PAGES))

            boxRoot.bind("<Down>", textArea.yview_scroll(1, tk.UNITS))
            boxRoot.bind("<Up>", textArea.yview_scroll(-1, tk.UNITS))

            # add a vertical scrollbar to the frame
            rightScrollbar = tk.Scrollbar(
                textFrame, orient=tk.VERTICAL, command=textArea.yview)
            textArea.configure(yscrollcommand=rightScrollbar.set)

            # add a horizontal scrollbar to the frame
            bottomScrollbar = ttk.Scrollbar(
                textFrame, orient=tk.HORIZONTAL, command=textArea.xview)
            textArea.configure(xscrollcommand=bottomScrollbar.set)

            textArea.bind("<Control-s>", __boxGetText)
            textArea.bind("<Shift-Return>", __boxGetText)
            self.boxRoot.bind_class("Text", "<3>", self.create_context_menu)

            rightScrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            textArea.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
            textArea.focus_force()  # put the focus on the entryWidget

        # ------------------ ok button -------------------------------
        if positive != None and positive != "":
            if "Сохранить" in positive:
                text = positive + " [Shift-Enter]"
            elif len(positive)<=2:
                text = positive
            else:
                text = positive[2:]
            okButton = ttk.Button(buttonsFrame, takefocus=1, compound="left",
                                  text=text, command=__boxGetText)  # getButton("  OK", img)[0], image=getButton("  OK", img)[1])
            okButton.pack(expand=1, side=tk.LEFT, padx='3m', pady='3m',
                          ipadx=self.SimpleButtonSizeX, ipady=self.SimpleButtonSizeY)
            okButton.bind("<Return>", __boxGetText)

        # ------------------ neutral button -------------------------------
        if neutral != None and neutral != "" and not "Очист" in neutral:
            if len(neutral)>2:
                neutral = neutral[2:]
            nButton = ttk.Button(buttonsFrame, takefocus=1, compound="left", text=neutral, command=__boxNeutral)

            if neutral != None and neutral != "Очист.":
                nButton.pack(expand=1, side=tk.LEFT, padx='3m', pady='3m',
                             ipadx=self.SimpleButtonSizeX, ipady=self.SimpleButtonSizeY)
            nButton.bind("<Return>", __boxNeutral)

        # ------------------ cancel button -------------------------------
        if negative != None and negative != "":
            cancelButton = ttk.Button(buttonsFrame, takefocus=1, compound="left", text=negative, command=__boxCancel)
            cancelButton.pack(expand=1, side=tk.RIGHT, padx='3m', pady='3m',
                              ipadx=self.SimpleButtonSizeX, ipady=self.SimpleButtonSizeY)
            cancelButton.bind("<Return>", __boxCancel)

        boxRoot.deiconify()
        boxRoot.mainloop()  # run it!

        # -------- after the run has completed ----------------------------------

        root.deiconify()
        boxRoot.destroy()  # button_click didn't destroy boxRoot, so we do it now
        return self.topLevelResult

    def geomShift(self, pos):
        """ Сдвиг позиции окна Toplevel """
        pos = pos[1:]
        x = int(pos[0: pos.index("+")])
        y = int(pos[pos.index("+"):])
        return ("+%d+%d" % (x + self.ToplevelShiftX, y + self.ToplevelShiftY))

    def getfile(self, msg=None, title=None, default='*', filetypes=None, multiple=False):
        """ Диалог для загрузки файла на ПК """

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
                if self.name == "Все файлы":
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
                file_types = {".*": "Все", ".txt": ".jsn"}
                if e in file_types:
                    return '{} файлы'.format(file_types[e])
                if e.startswith("."):
                    return '{} файлы'.format(e[1:].upper())
                return '{} файлы'.format(e.upper())

        def getFileDialogTitle(msg, title):
            if msg and title:
                return "%s - %s" % (title, msg)
            if msg and not title:
                return str(msg)
            if title and not msg:
                return str(title)
            return None  # no message and no title

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
                    ALL_filetypes_was_specified = True
                if fto == initialFileTypeObject:
                    initialFileTypeObject.add(fto)  # add fto to initialFileTypeObject
                else:
                    filetypeObjects.append(fto)
            if ALL_filetypes_was_specified:
                pass
            elif allFileTypeObject == initialFileTypeObject:
                pass
            else:
                filetypeObjects.insert(0, allFileTypeObject)
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

        localRoot = tk.Tk()
        localRoot.withdraw()
        initialbase, initialfile, initialdir, filetypes = fileboxSetup( default, filetypes)
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
