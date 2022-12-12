#!/usr/bin/python
# -*- coding: utf-8 -*-

import utils
import house
import report
import time
import datetime
import webbrowser
import iconfonts
from iconfonts import icon
import plyer
from datetime import datetime

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.base import EventLoop
from kivy.uix.popup import Popup
#from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown
from kivy.core.clipboard import Clipboard
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.config import Config
#from kivy.lang import Builder
#from kivy.uix.bubble import Bubble, BubbleButton
from kivy import platform
from kivy.clock import Clock

if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.INTERNET, Permission.CALL_PHONE])#, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

else:
    try:
        import docx2txt
    except:
        from subprocess import check_call
        from sys import executable
        check_call([executable, '-m', 'pip', 'install', 'docx2txt'])
        import docx2txt

#Builder.load_file('rm.kv')

class DataTransfer(object):
    def __init__(self):
        self.message = ""
        self.title = ""
        self.form = ""
        self.options = []
        self.selected = 0
        self.positive = None
        self.neutral = None
        self.negative = None

    def update(self, message="", title="", form="", options=[], selected=0,
                 positive=None, neutral=None, negative=None):
        self.message = message
        self.title = title
        self.form = form
        self.options = options
        self.preselect = selected
        self.positive = positive
        self.neutral = neutral
        self.negative = negative

    def show(self):
        print(self.title)
        print(self.message)
        print(self.options)

class SearchBar(TextInput):
    def __init__(self):
        super(SearchBar, self).__init__()
        self.multiline=False
        self.size_hint=(1, None)
        self.pos_hint={"center_y": .5}
        self.height=MyApp.standardTextHeight*1.1
        self.hint_text="Введите запрос"
        self.input_type = "text"

class TopButton(Button):
    def __init__(self, text=""):
        super(TopButton, self).__init__()
        self.text = text
        self.font_size = MyApp.fontXXL
        self.markup=True
        self.size_hint = (1, None)
        self.pos_hint = {"center_y": .5}
        self.color = MyApp.topButtonColor
        self.background_color = MyApp.globalBGColor #globalBGColor
        self.background_normal = ""
        self.background_down = MyApp.buttonPressedBG

class TableButton(Button):
    def __init__(self, text="", size_hint_x=1, color=None, background_color=None):
        super(TableButton, self).__init__()
        self.text = text.strip()
        self.markup = True
        self.size_hint_y = 1#MyApp.marginSizeHintY
        self.size_hint_x = size_hint_x
        self.pos_hint = {"center_y": .5}
        if color == None:
            self.color = MyApp.tableColor
        else:
            self.color = color
        if background_color == None:
            self.background_color = MyApp.tableBGColor
        else:
            self.background_color = background_color
        self.background_normal = ""
        self.background_disabled_normal = ""
        self.background_down = MyApp.buttonPressedBG

class SmallUpButton(Button):
    def __init__(self):
        super(SmallUpButton, self).__init__()
        self.text = icon("icon-plus-circled-1")
        self.markup = True
        self.size_hint = (None, 1)
        self.font_size = MyApp.fontL
        self.pos_hint = {"center_y": .5}
        if utils.settings[0][5] == "dark":
            color = "black"
        elif utils.settings[0][5] == "teal":
            color = MyApp.themeDefault[1]
        else:
            color = MyApp.mainMenuButtonColor
        self.color = color
        self.background_color = MyApp.topButtonColor
        self.background_normal = ""
        self.background_down = MyApp.buttonPressedBG
        self.size = (MyApp.standardTextHeight, MyApp.standardTextHeight)

class SmallDownButton(Button):
    def __init__(self):
        super(SmallDownButton, self).__init__()
        self.text = icon("icon-minus-circled-1")
        self.markup = True
        self.size_hint = (None, 1)
        self.font_size = MyApp.fontL
        self.pos_hint = {"center_y": .5}
        if utils.settings[0][5] == "dark":
            color = "black"
        elif utils.settings[0][5] == "teal":
            color = MyApp.themeDefault[1]
        else:
            color = MyApp.mainMenuButtonColor
        self.color = color
        self.background_color = MyApp.topButtonColor
        self.background_normal = ""
        self.background_down = MyApp.buttonPressedBG
        self.size = (MyApp.standardTextHeight, MyApp.standardTextHeight)

class Counter(AnchorLayout):
    def __init__(self, type="int", text="", size_hint=(1, 1), width=0, height=0, disabled=False):
        super(Counter, self).__init__()
        self.anchor_x = "center"
        self.anchor_y = "center"
        self.size_hint = (1, 1)

        box = BoxLayout(orientation="horizontal", size_hint=size_hint)

        self.input = TextInput(text=text,  # поле ввода
                            disabled=disabled, multiline=False, width = width, height=height,
                            size_hint=(1, 1), pos_hint={"center_y": .5}, input_type="number")
        self.input.bind(focus=MyApp.onKeyboardFocusNum)
        box.add_widget(self.input)

        box2 = BoxLayout(orientation="vertical", size_hint=(1, 1), spacing=MyApp.spacing)

        aUp = AnchorLayout(anchor_x="left", anchor_y="top")
        btnUp = SmallUpButton()  # кнопка вверх
        def __countUp(instance=None):
            try:
                if type != "time":
                    self.input.text = str(int(self.input.text) + 1)
                else:
                    hours = self.input.text[: self.input.text.index(":")]
                    minutes = self.input.text[self.input.text.index(":") + 1:]
                    self.input.text = "%d:%s" % (int(hours) + 1, minutes)
            except:
                pass
        btnUp.bind(on_press=__countUp)
        #btnUp.bind(on_press=MyApp.changeColor1)
        #btnUp.bind(on_release=MyApp.changeColor2)
        aUp.add_widget(btnUp)

        aDown = AnchorLayout(anchor_x="left", anchor_y="bottom")
        btnDown = SmallDownButton() # кнопка вниз
        def __countDown(instance=None):
            try:
                if type != "time":
                    self.input.text = str(int(self.input.text) - 1)
                else:
                    hours = self.input.text[: self.input.text.index(":")]
                    minutes = self.input.text[self.input.text.index(":") + 1:]
                    self.input.text = "%d:%s" % (int(hours) - 1, minutes)
            except:
                pass
        btnDown.bind(on_press=__countDown)
        #btnDown.bind(on_press=MyApp.changeColor1)
        #btnDown.bind(on_release=MyApp.changeColor2)
        aDown.add_widget(btnDown)
        box2.add_widget(aUp)
        box2.add_widget(aDown)
        box.add_widget(box2)
        self.add_widget(box)

    def get(self):
        if not ":" in self.input.text and utils.ifInt(self.input.text) == True:
            return self.input.text
        elif ":" in self.input.text:
            return self.input.text
        else:
            return "0"

    def flash(self):
        self.input.background_color = MyApp.reportFlashColor
        def __removeFlash(instance):
            self.input.background_color = "white"
            unflash.cancel()
        unflash = Clock.schedule_interval(__removeFlash, 0.5)

class Timer(Button):
    def __init__(self):
        super(Timer, self).__init__()
        self.pos_hint = {"center_y": .5}
        self.font_size = MyApp.fontXXL*2
        self.markup = True
        self.halign = "left"
        self.background_color = MyApp.globalBGColor
        self.background_normal = ""
        self.background_down = MyApp.buttonPressedBG
        self.size_hint = (None, None)
        self.width = MyApp.standardTextHeight*1.7

    def on(self):
        """ Включение таймера """
        self.text = icon("icon-stop-circle")
        self.color = "crimson"

    def off(self):
        """ Выключение таймера """
        self.text = icon("icon-play-circled-1")
        self.color = "limegreen"

class MainMenuButton(Button):
    def __init__(self, text):
        super(MainMenuButton, self).__init__()
        self.markup = True
        terNormal  = icon("icon-building") + "\nУчастки"
        terPressed = icon("icon-building-filled") + "\nУчастки"
        conNormal  = icon ("icon-address-book-o") + "\nКонтакты"
        conPressed = icon ("icon-address-book-1") + "\nКонтакты"
        repNormal  = icon("icon-doc-text") + "\nОтчет"
        repPressed = icon("icon-doc-text-inv") + "\nОтчет"
        self.background_down = MyApp.buttonPressedBG
        self.pos_hint = {"center_y": .5}
        if text == "Участки":
            self.text = terNormal
        elif text == "Контакты":
            self.text = conNormal
        else:
            self.text = repNormal
        self.valign = self.halign = "center"
        self.size_hint = (1, 1)
        self.markup = True
        if MyApp.platform == "mobile":
            self.font_size = MyApp.fontL*.8
        else:
            self.font_size = MyApp.fontL * 1.1
        self.background_color = MyApp.tableBGColor
        self.background_normal = ""
        self.color = MyApp.mainMenuButtonColor
        def __change1(instance):
            if self.text == terNormal:
                self.text = terPressed
            elif self.text == conNormal:
                self.text = conPressed
            elif self.text == repNormal:
                self.text = repPressed
            #self.background_color = MyApp.tableColor
            #self.background_normal = ""
            #self.color = MyApp.titleColor
        #self.bind(on_press=__change1)
        def __change2(instance):
            if self.text == terPressed:
                self.text = terNormal
            elif self.text == conPressed:
                self.text = conNormal
            elif self.text == repPressed:
                self.text = repNormal
            #self.background_color = MyApp.globalBGColor
            #self.color = MyApp.tableColor
        #self.bind(on_release=__change2)

    def activate(self):
        return
        self.color = MyApp.titleColor

    def deactivate(self):
        return
        self.color = MyApp.topButtonColor

class RM(App):
    """ Главный класс приложения """

    def build(self):

        try:
            utils.load()
            self.setParameters()
            self.setTheme()
            self.createInterface()
            self.terPressed()
            Clock.schedule_interval(self.updateTimer, 1)
            self.onStartup()
        except:
            print("Произошла ошибка при запуске программы.")
            self.stop()
        else:
            utils.save(backup=True)
            return self.globalAnchor

    # Подготовка переменных

    def setParameters(self):
        if platform != "win" and platform != "linux":
            self.platform = "mobile"
        else:
            self.platform = "desktop"
        self.rep = report.Report()
        iconfonts.register('default_font', 'fontello.ttf', 'fontello.fontd')
        self.feed = DataTransfer()
        self.contactsEntryPoint = self.searchEntryPoint = self.popupEntryPoint = 0
        self.porch = house.House().Porch()
        #self.porch.type = "virtual"
        self.searchOpened = False
        self.lastForm = "ter"
        self.devmode = 0
        self.displayed = self.feed
        self.button = {
            "save":     str(icon("icon-floppy") + " Сохранить"),
            "cancel":   "Отмена", # str(icon("icon-left-big")
            "exit":     "Выход", # str(icon("icon-left-big") +
            "ok":       str(icon("icon-ok-1") + " OK"),
            "yes":      "Да",
            "no":       "Нет"
        }

        #Window.softinput_mode = 'pan'
        #Window.softinput_mode = 'below_target'
        #Config.set('kivy', 'keyboard_mode', 'system')
        Window.fullscreen = False
        #Config.set('kivy', 'keyboard_mode', '')
        self.wsizeInit = Window.size
        self.spacing = Window.size[1]/600
        self.padding = Window.size[1]/600
        self.standardTextHeight = self.standardBarWidth = Window.size[1] * .04 #90
        self.standardTextWidth = self.standardTextHeight*1.3
        self.marginSizeHintY = 0.08
        #self.standardBarWidth = 60
        self.fontXXL = Window.size[1] / 30
        self.fontXL = Window.size[1] / 35
        self.fontL = Window.size[1] / 40
        self.fontM = Window.size[1] / 45
        self.fontS = Window.size[1] / 50
        self.fontXS = Window.size[1] / 55
        self.fontXXS = Window.size[1] / 60
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

        if self.platform == "desktop":
            # Window.size = (800, 801)
            Config.set('graphics', 'left', '200')
            Config.set('graphics', 'top', '20')
            Config.set('graphics', 'window_icon', 'icon.png')
            Config.write()
            self.title = 'Rocket Ministry'
            self.icon = "icon.png"
            k=1.3
            y = Window.size[1] * k
            x = y / 2
            Window.size = (x, y)
            Window.icon = "icon.png"
            self.storage = "no"
        else:
            plyer.orientation.set_portrait()

    # Создание интерфейса

    def createInterface(self):
        """ Создание основных элементов """

        self.globalAnchor = AnchorLayout(anchor_x="center", anchor_y="top", size_hint=(1, 1))
        self.interface = BoxLayout(orientation="vertical", size_hint=(1, 1))#, spacing=self.spacing, padding=self.padding)
        self.boxHeader = BoxLayout(orientation="horizontal", size_hint=(1, self.marginSizeHintY),
                                   spacing=self.spacing, padding=self.padding)
        # Таймер

        self.timerBox = BoxLayout(orientation="horizontal", size_hint=(0.33, 1), spacing=self.spacing*2,
                                  padding=(self.padding, 0))
        self.timer = Timer()
        self.timer.bind(on_press=self.timerPressed)
        self.timerBox.add_widget(self.timer)
        self.timerText = Label(halign="left", valign="center", font_size=self.fontXL,
                               color=self.topButtonColor, width=self.standardTextWidth,
                               markup=True, size_hint=(None, None), pos_hint={"center_y": .5})
        self.timerBox.add_widget(self.timerText)
        self.boxHeader.add_widget(self.timerBox)

        # Заголовок таблицы

        self.headBox = BoxLayout(size_hint_x=1, size_hint_min_y=0.08)
        self.listTitle = Label(text="Заголовок страницы", color=self.titleColor, halign="center",
                               valign="center", text_size=(Window.size[0] * .33, self.standardTextHeight * 3))
        self.listTitle.bind(on_press=self.detailsPressed)
        self.headBox.add_widget(self.listTitle)
        self.boxHeader.add_widget(self.headBox)

        # Поиск и настройки

        self.setBox = BoxLayout(orientation="horizontal", size_hint=(.33, 1), padding=self.padding*2,
                                spacing=self.spacing*4)
        self.search = TopButton(text=icon("icon-search-1"))
        self.search.bind(on_press=self.searchPressed)
        aS = AnchorLayout(anchor_x="left", anchor_y="center", size_hint=(1, 1))
        aS.add_widget(self.search)
        self.setBox.add_widget(aS)

        self.settings = TopButton(text="  " + icon("icon-dots") + "  ")

        self.settings.bind(on_press=self.settingsPressed)
        self.setBox.add_widget(self.settings)
        self.boxHeader.add_widget(self.setBox)
        self.interface.add_widget(self.boxHeader)

        self.boxCenter = BoxLayout(orientation="horizontal", size_hint=(1, 1), padding=self.padding,
                                   spacing=self.spacing)
        mainBox = BoxLayout(orientation="horizontal", size_hint=(1, 1), spacing=self.spacing)
        self.boxCenter.add_widget(mainBox)
        self.listarea = BoxLayout(orientation="vertical", spacing=self.spacing)
        mainBox.add_widget(self.listarea)

        #  Верхние кнопки таблицы

        self.titleBox = BoxLayout(orientation="horizontal", size_hint_y=self.marginSizeHintY)
        self.listarea.add_widget(self.titleBox)
        self.backButton = TableButton(text=icon("icon-left-big"))
        self.backButton.bind(on_press=self.backPressed)
        self.titleBox.add_widget(self.backButton)

        self.dropSortMenu = DropDown()
        self.sortButton = TableButton(text=icon("icon-sort-alt-up"))
        self.titleBox.add_widget(self.sortButton)
        self.sortButton.bind(on_press=self.sortPressed)

        self.detailsButton = TableButton(text=icon("icon-edit-1"))
        self.detailsButton.bind(on_press=self.detailsPressed)
        self.titleBox.add_widget(self.detailsButton)

        self.note = TableButton(text=icon("icon-edit-1"))
        self.titleBox.add_widget(self.note)
        self.note.bind(on_press=self.notePressed)

        # Главный список

        self.mainList = BoxLayout(orientation="vertical", size_hint=(1, 1))
        self.listarea.add_widget(self.mainList)

        # Нижние кнопки таблицы

        self.bottomButtons = BoxLayout(orientation="horizontal", size_hint_y=self.marginSizeHintY)
        self.listarea.add_widget(self.bottomButtons)

        self.positive = TableButton(background_color=self.globalBGColor)
        if utils.settings[0][5] == "teal":
            self.positive.color = self.themeDefault[1]
        self.positive.bind(on_press=self.positivePressed)
        self.bottomButtons.add_widget(self.positive)

        self.neutral = TableButton(size_hint_x=0.25, background_color=self.globalBGColor)
        if utils.settings[0][5] == "teal":
            self.neutral.color = self.themeDefault[1]
        self.neutral.bind(on_press=self.neutralPressed)
        self.bottomButtons.add_widget(self.neutral)

        self.negative = TableButton(background_color=self.globalBGColor)
        if utils.settings[0][5] == "teal":
            self.negative.color = self.themeDefault[1]
        self.negative.bind(on_press=self.backPressed)
        self.bottomButtons.add_widget(self.negative)
        self.interface.add_widget(self.boxCenter)

        # Подвал и кнопки меню

        self.boxFooter = BoxLayout(orientation="horizontal", size_hint=(1, self.marginSizeHintY))#, padding=(0, self.padding*2))
        self.buttonTer = MainMenuButton(text="Участки")  # text="Участки")#
        self.buttonTer.bind(on_press=self.terPressed)
        b1 = AnchorLayout(anchor_x="center")
        b1.add_widget(self.buttonTer)
        self.boxFooter.add_widget(b1)
        self.buttonCon = MainMenuButton(text="Контакты")  # (text="Контакты")
        self.buttonCon.bind(on_press=self.conPressed)
        b2 = AnchorLayout(anchor_x="center")
        b2.add_widget(self.buttonCon)
        self.boxFooter.add_widget(b2)
        self.buttonRep = MainMenuButton(text="Отчет")  # Button(text="Отчет")
        self.buttonRep.bind(on_press=self.repPressed)
        b3 = AnchorLayout(anchor_x="center")
        b3.add_widget(self.buttonRep)
        self.boxFooter.add_widget(b3)

        self.interface.add_widget(self.boxFooter)
        self.globalAnchor.add_widget(self.interface)

    def setTheme(self):

        self.themeDefault = [0.92, 0.92, 0.92, .9], [0, .15, .35, .8] # цвет фона и кнопок
        self.themePurple = [0.92, 0.92, 0.92, .9], [.36, .24, .53, .9]
        self.themeTeal = [0.2, 0.64, 0.81, .9], "white"
        self.themeDark = [.22, .22, .22, .9], "white"

        if utils.settings[0][5] == "dark":
            self.globalBGColor = self.globalBGColor0 = "black"#self.themeDark # фон программы
            Window.clearcolor = self.globalBGColor
            self.mainMenuButtonColor =  self.themeDark[1]
            self.mainMenuButtonColor2= "FFFFFF"
            self.topButtonColor = "lightgray" # поиск, настройки и кнопки счетчиков
            self.tableBGColor = self.themeDark[0] # цвет фона кнопок таблицы
            self.standardTextColor = "white" # основной текст всех шрифтов             
            self.titleColor = [.3, .82, 1] # неон - цвет нажатой кнопки и заголовка
            self.popupBackgroundColor = [.16, .16, .16] # фон всплывающего окна 
            self.tableColor = self.themeDark[1] # цвет текста на плашках таблицы и кнопках главного меню
            self.standardScrollColor = "white" # текст пунктов списка
            self.scrollButtonBackgroundColor = [.14, .14, .14] # фон пунктов списка
            self.createNewPorchButton = [.2, .2, .2] # пункт списка создания нового подъезда
            self.buttonPressedBG = "button_background_gray.png"

        else:
            self.globalBGColor = (1, 1, 1, 1)
            self.globalBGColor0 = (1, 1, 1, 0)
            Window.clearcolor = self.globalBGColor
            self.topButtonColor = [.75,.75,.75]
            self.standardTextColor = [.1, .1, .1]
            self.titleColor = [.09, .61, .85]  # неон
            self.tableBGColor = self.themeDefault[0]
            self.popupBackgroundColor = [.16, .16, .16]
            self.standardScrollColor = "white"
            self.scrollButtonBackgroundColor = [.56,.56,.56]
            self.createNewPorchButton = "dimgray"
            self.phoneNeutralButton = "lightgreen"
            self.reportFlashColor = "lightgreen"

            if utils.settings[0][5] == "purple": # под Library
                self.titleColor = [.7, .3, .8, .8]
                self.tableColor = self.mainMenuButtonColor = self.themePurple[1]
                self.mainMenuButtonColor2 = "5C3D87"
                self.buttonPressedBG = "button_background_gray.png"

            elif utils.settings[0][5] == "green":
                self.titleColor = [0, .6, .6, .9]
                self.tableColor = self.mainMenuButtonColor = [0, .4, .4]
                self.mainMenuButtonColor2 = "000A0A"
                self.buttonPressedBG = "button_background_gray.png"

            elif utils.settings[0][5] == "teal": # тема 2.0.1 бирюзовая
                self.tableColor = self.mainMenuButtonColor = self.themeTeal[1]
                self.tableBGColor = self.themeTeal[0]
                self.mainMenuButtonColor2 = "FFFFFF"
                self.buttonPressedBG = "button_background_teal.png"

            else: # основная тема
                self.tableColor = self.mainMenuButtonColor = self.themeDefault[1]
                self.mainMenuButtonColor2 = "2F4E77"
                self.buttonPressedBG = "button_background_gray.png"

    # Основные действия с центральным списком

    def update(self):
        """Заполнение главного списка элементами"""

        try:
            self.standardTextHeight = Window.size[1] * .05  # 90
            self.mainList.clear_widgets()
            self.detailsButton.disabled = True
            self.sortButton.disabled = True
            self.neutral.text = ""

            self.positive.text = self.displayed.positive
            self.negative.text = self.displayed.negative

            if not "rep" in self.displayed.form and self.displayed.form != "set":
                self.note.text = icon("icon-sticky-note-o") + " Заметка"

            # Обычный список (этажей нет)

            if self.displayed.form != "porchView" or \
                    (self.displayed.form == "porchView" and self.porch.floors() == False):#or self.porch.rows==1:
                bar_width = self.standardBarWidth
                height1 = self.standardTextHeight*1.2
                height2 = height1 * 1.5
                height = height1
                self.scrollWidget = GridLayout(cols=1, spacing=self.spacing, size_hint_y=None)
                self.scrollWidget.bind(minimum_height=self.scrollWidget.setter('height'))
                self.scroll = ScrollView(size=(Window.width, Window.height), bar_width=bar_width,
                                         scroll_type=['bars', 'content'])
                self.btn = []

                if self.displayed.form == "porchView":
                    self.indexes = []
                    for f in range(len(self.porch.flats)):
                        if not "." in self.porch.flats[f].number:
                            self.indexes.append(f) # создаем отдельный список с индексами квартир

                for i in range(len(self.displayed.options)):
                    label = self.displayed.options[i]
                    if (self.displayed.form == "porchView" or self.displayed.form == "con") and "{" in label:
                        status = label[label.index("{") + 1: label.index("}")]  # определение статуса по цифре
                        label = label[3:] # удаление статуса из строки
                        background_color = self.getColorForStatus(status)
                    elif "Создать подъезд" in label:
                        background_color = self.createNewPorchButton
                    else:
                        background_color = self.scrollButtonBackgroundColor

                    addRecord = False
                    valign = "center"
                    if self.displayed.form == "porchView":
                        if len(self.indexes) > 0 and len(self.porch.flats[self.indexes[i]].records) > 0:
                            addRecord = True
                    elif self.displayed.form == "flatView":
                        height = height2
                        valign = "top"

                    # Добавление пункта списка

                    if "Ничего не найдено" in label or "Здесь будут" in label or self.displayed.form == "repLog":
                        # отдельный механизм добавления записей журнала отчета + ничего не найдено в поиске
                        self.scrollWidget.add_widget(Label(text=label.strip(), color=self.standardTextColor, halign="left",
                                                           valign="top", size_hint_y=None, height=height2,
                                                            text_size=(Window.size[0] - 50, height2)))

                    else: # стандартное добавление

                        box = BoxLayout(orientation="vertical", size_hint=(1, None))

                        self.btn.append( Button(text=label.strip(), size_hint_y=1, height=height, halign="center",
                                                valign=valign, text_size = (Window.size[0], height),
                                                background_normal="", color=self.standardScrollColor,
                                                background_color=background_color, markup=True)
                        )
                        last = len(self.btn)-1
                        box.add_widget(self.btn[last])
                        if addRecord == True: # если есть запись посещения на виде подъезда, добавляем ее снизу
                            box.add_widget( Label(
                                text= "[i]" + self.porch.flats[self.indexes[i]].records[0].title + "[/i]", markup=True,
                                color=self.standardTextColor, halign="left", valign="top", size_hint_y=None, height=height2,
                                text_size = (Window.size[0]-50, height2)
                                )
                            )
                            box.height = height + height2
                        else:
                            box.height = height
                        self.btn[last].bind(on_press=self.clickOnList)

                        self.scrollWidget.add_widget(box)

                self.scrollWidget.add_widget(Button(size_hint_y=None, # пустая кнопка для решения бага последней записи
                                                    height=height, halign="center", valign="center",
                                                    text_size = (Window.size[0]-15, height-10), background_normal="",
                                                    background_color=self.globalBGColor))

                self.scroll.add_widget(self.scrollWidget)
                self.mainList.add_widget(self.scroll)
                self.positive.text = self.displayed.positive
                self.negative.text = self.displayed.negative

            # Вид подъезда с этажами

            else:
                if len(self.porch.flats) > 100:
                    spacing = self.spacing
                elif len(self.porch.flats) > 50:
                    spacing = self.spacing * 1.2
                else:
                    spacing = self.spacing * 1.5
                self.floorview = GridLayout(cols=self.porch.columns+1, rows=self.porch.rows, spacing=spacing,
                                            padding=spacing*2)
                for label in self.displayed.options:
                    if "│" in label: # показ цифры этажа
                        self.floorview.add_widget(Label(text=label[: label.index("│")], halign="right",
                                color=self.standardTextColor, width=self.standardTextHeight*1.5,
                                                        font_size=self.fontXS*.8))
                    elif "." in label:
                        self.floorview.add_widget(Widget())
                    else:
                        status = label[label.index("{")+1 : label.index("}")] # определение цвета по статусу
                        b = Button(text=label[label.index("}")+1 : ], background_color=self.getColorForStatus(status),
                                   background_normal="0", color=self.standardScrollColor,
                                   size_hint_x=10, size_hint_y=0)
                        self.floorview.add_widget(b)
                        b.bind(on_press=self.clickOnList)
                self.mainList.add_widget(self.floorview)
            self.listTitle.text = self.displayed.title

        except: # в случае ошибки пытаемся восстановить последнюю резервную копию
            result = utils.backupRestore(restoreWorking=True, silent=True)
            if result == True:
                self.popup(title="Ошибка базы данных",
                       message="Файл базы данных поврежден! Восстанавливаю резервную копию. Если эта ошибка будет повторяться, обратитесь в поддержку.")
                self.rep = report.Report()
                utils.save()
                self.terPressed()

    def clickOnList(self, instance):
        """Действия, которые совершаются на указанных экранах по нажатию на кнопку главного списка"""

        if "Создайте" in instance.text or "Здесь будут" in instance.text:
            self.positivePressed()
        elif "Создать подъезд" in instance.text:
            text = instance.text[19:]
            if "[/i]" in text:
                text = text[ : text.index("[")]
            self.house.addPorch(text.strip())
            utils.save()
            self.houseView()

        for i in range(len(self.displayed.options)):

            if self.displayed.form == "porchView" or self.displayed.form == "con":
                self.contactsEntryPoint = 0
                self.searchEntryPoint = 0
                self.displayed.options[i] = self.displayed.options[i][3:] # удаление {}, чтобы определение нажатия работало

            if self.displayed.options[i].strip() == instance.text.strip():
                self.choice = i

                if self.displayed.form == "ter":
                    self.house = utils.houses[i] # начиная отсюда знаем дом и его индекс
                    self.selectedHouse = self.choice
                    self.houseView() # вход в дом

                elif self.displayed.form == "houseView":
                    self.porch = self.house.porches[self.choice] # начиная отсюда знаем подъезд и его индекс
                    self.selectedPorch = self.choice
                    self.porchView() # вход в подъезд

                elif self.displayed.form == "porchView":
                    self.flat = self.findFlatByNumber(instance.text)

                    if self.porch.floors() == False: # определяем индекс нажатой конкретной кнопки скролла, чтобы затем промотать до нее вид
                        for i in range(len(self.btn)):
                            if self.btn[i].text == instance.text:
                                self.clickedBtnIndex = i
                                break

                    for y in range(len(self.porch.flats)):
                        if self.porch.flats[y].number == self.flat.number:
                            self.selectedFlat = y # отсюда знаем квартиру, ее индекс и фактический номер
                            break
                    self.flatView(call=False) # вход в квартиру

                elif self.displayed.form == "flatView": # режим редактирования записей
                    self.selectedRecord = self.choice # отсюда знаем запись и ее индекс
                    self.record = self.flat.records[self.selectedRecord]
                    self.recordView() # вход в запись посещения

                elif self.displayed.form == "con": # контакты
                    contactText = self.displayed.options[self.choice]

                    for w in range(len(self.displayed.options)):
                        if contactText == self.displayed.options[w]:
                            self.selectedCon = w # знаем индекс контакта в списке контактов
                            break

                    h = self.allcontacts[self.selectedCon][7][0]  # получаем дом, подъезд и квартиру выбранного контакта
                    p = self.allcontacts[self.selectedCon][7][1]
                    f = self.allcontacts[self.selectedCon][7][2]
                    if self.allcontacts[self.selectedCon][8] != "virtual":
                        self.house = utils.houses[h]
                    else:
                        self.house = utils.resources[1][h] # заменяем дом на ресурсы для отдельных контактов
                    self.selectedHouse = h
                    self.porch = self.house.porches[p]
                    self.selectedPorch = p
                    self.flat = self.porch.flats[f]
                    self.selectedFlat = f
                    self.contactsEntryPoint = 1
                    self.searchEntryPoint = 0
                    self.flatView()

                elif self.displayed.form == "search": # поиск
                    contactText = self.displayed.options[self.choice]

                    for w in range(len(self.displayed.options)):
                        if contactText == self.displayed.options[w]:
                            self.selectedCon = w  # знаем индекс контакта в поисковой выдаче
                            break

                    h = self.searchResults[self.selectedCon][0][0]  # получаем номера дома, подъезда и квартиры
                    p = self.searchResults[self.selectedCon][0][1]
                    f = self.searchResults[self.selectedCon][0][2]
                    if self.searchResults[self.selectedCon][1] != "virtual":  # regular contacts
                        self.house = utils.houses[h]
                    else:
                        self.house = utils.resources[1][h]
                    self.selectedHouse = h
                    self.porch = self.house.porches[p]
                    self.selectedPorch = p
                    self.flat = self.porch.flats[f]
                    self.selectedFlat = f
                    self.searchEntryPoint = 1
                    self.contactsEntryPoint = 0
                    self.flatView()

                break

    def detailsPressed(self, instance=None):
        """ Нажата кнопка настроек рядом с заголовком (редактирование данного объекта) """

        if self.displayed.form == "houseView" or self.displayed.form == "noteForHouse" or \
            self.displayed.form == "createNewPorch":  # детали участка
            self.displayed.form = "houseDetails"
            if self.house.type == "private":
                title = "Название участка:"
            else:
                title = "Адрес:"
            self.createMultipleInputBox(
                options=[title, "Дата взятия:"],
                defaults=[self.house.title, self.house.date],
                multilines=[False, False]
            )

        elif self.displayed.form == "porchView" or self.displayed.form == "noteForPorch" or \
            self.displayed.form == "createNewFlat": # детали подъезда
            self.displayed.form = "porchDetails"
            options = ["Номер (название) %sа:" % self.porch.type[:7]]
            defaults = [self.porch.title]
            self.createMultipleInputBox(
                options=options,
                defaults=defaults,
                multilines=[False]
            )

        elif self.displayed.form == "flatView" or self.displayed.form == "noteForFlat" or\
            self.displayed.form == "createNewRecord" or self.displayed.form == "recordView": # детали квартиры

            self.displayed.form = "flatDetails"

            options = ["Имя и (или) описание человека:", "Телефон:"]
            defaults = [self.flat.getName(), self.flat.phone]
            multilines = [False, False]
            if self.house.type == "virtual":
                options.append("Адрес:")
                defaults.append(self.house.title)
                multilines.append(self.house.title)
            elif self.house.type != "condo":
                options.append("Номер %s:" % self.house.getPorchType()[1])
                defaults.append(self.flat.number)
                multilines.append(False)
            self.createMultipleInputBox(
                title=self.flatTitle,
                options=options,
                defaults=defaults,
                multilines=multilines
            )

    def backPressed(self, instance=None):
        """Нажата кнопка «назад»"""
        if self.displayed.form == "houseView" or self.displayed.form == "createNewHouse":
            self.terPressed()
        elif self.displayed.form == "porchView" or self.displayed.form == "createNewPorch" or\
            self.displayed.form == "noteForHouse" or self.displayed.form == "editHouse" or\
                self.displayed.form == "houseDetails":
                self.houseView()
        elif self.displayed.form == "flatView" or self.displayed.form == "createNewFlat" or\
            self.displayed.form == "noteForPorch" or self.displayed.form == "editPorch" or\
            self.displayed.form == "porchDetails" or self.displayed.form == "createNewCon":
            if self.contactsEntryPoint == 1:
                self.conPressed()
            elif self.searchEntryPoint == 1:
                self.find()
            else:
                self.porchView()
        elif self.displayed.form == "createNewRecord" or self.displayed.form == "noteForFlat" or\
            self.displayed.form == "editFlat" or self.displayed.form == "recordView" or\
            self.displayed.form == "flatDetails":
                if self.popupEntryPoint == 0:
                    self.flatView()
                else:
                    self.popupEntryPoint = 0
                    self.porchView()
        elif self.displayed.form == "repLog":
            self.repPressed()
        elif self.displayed.form == "ter" or "rep" in self.displayed.form or self.displayed.form == "con" or\
            self.displayed.form == "set" or self.displayed.form == "noteGlobal":
            self.loadForm(self.lastForm) # для возврата из этих форм на запомненную предыдущую страницу
        else:
            self.terPressed()

    def sortPressed(self, instance=None):
        self.dropSortMenu.clear_widgets()
        if self.displayed.form == "ter":  # меню сортировки участков
            sortTypes = [
                "Название",
                "Дата",
                "Интерес.",
                "Обраб.",
                "Обраб. обр."
            ]
            for i in range(len(sortTypes)):
                btn = Button(text=sortTypes[i], size_hint_y=None, height=self.standardTextHeight,
                             background_color=self.tableBGColor, background_normal="",
                             color=self.tableColor)
                def __resortHouses(instance=None):
                    if instance.text == sortTypes[0]:
                        utils.settings[0][19] = "н"
                    elif instance.text == sortTypes[1]:
                        utils.settings[0][19] = "д"
                    elif instance.text == sortTypes[2]:
                        utils.settings[0][19] = "и"
                    elif instance.text == sortTypes[3]:
                        utils.settings[0][19] = "п"
                    elif instance.text == sortTypes[4]:
                        utils.settings[0][19] = "о"
                    utils.save()
                    self.terPressed()
                btn.bind(on_release=__resortHouses)
                self.dropSortMenu.add_widget(btn)
            self.dropSortMenu.bind(on_select=lambda instance, x: setattr(self.sortButton, 'text', x))
            self.sortButton.bind(on_release=self.dropSortMenu.open)

        elif self.displayed.form == "porchView":  # меню сортировки квартир в подъезде
            self.dropSortMenu.clear_widgets()
            sortTypes = ["Номер", "Номер обр.", "Статус", "Заметка", "Телефон"]
            for i in range(len(sortTypes)):
                btn = Button(text=sortTypes[i], size_hint_y=None, height=self.standardTextHeight,
                             background_color=self.tableBGColor, background_normal="",
                             color=self.tableColor)
                def __resortFlats(instance=None):
                    if instance.text == sortTypes[0]:
                        self.porch.flatsLayout = "н"
                    elif instance.text == sortTypes[1]:
                        self.porch.flatsLayout = "о"
                    elif instance.text == sortTypes[2]:
                        self.porch.flatsLayout = "с"
                    elif instance.text == sortTypes[3]:
                        self.porch.flatsLayout = "з"
                    elif instance.text == sortTypes[4]:
                        self.porch.flatsLayout = "т"
                    utils.save()
                    self.porchView()
                btn.bind(on_release=__resortFlats)
                self.dropSortMenu.add_widget(btn)
            self.dropSortMenu.bind(on_select=lambda instance, x: setattr(self.sortButton, 'text', x))
            self.sortButton.bind(on_release=self.dropSortMenu.open)

        elif self.displayed.form == "con":  # меню сортировки контактов
            sortTypes = [
                "Имя",
                "Статус",
                "Адрес",
                "Телефон"
            ]
            for i in range(len(sortTypes)):
                btn = Button(text=sortTypes[i], size_hint_y=None, height=self.standardTextHeight,
                             background_color=self.tableBGColor, background_normal="",
                             color=self.tableColor)
                def __resortCons(instance=None):
                    if instance.text == sortTypes[0]:
                        utils.settings[0][4] = "и"
                    elif instance.text == sortTypes[1]:
                        utils.settings[0][4] = "с"
                    elif instance.text == sortTypes[2]:
                        utils.settings[0][4] = "а"
                    elif instance.text == sortTypes[3]:
                        utils.settings[0][4] = "т"
                    utils.save()
                    self.conPressed()
                btn.bind(on_release=__resortCons)
                self.dropSortMenu.add_widget(btn)
            self.dropSortMenu.bind(on_select=lambda instance, x: setattr(self.sortButton, 'text', x))
            self.sortButton.bind(on_release=self.dropSortMenu.open)

    # Таймер

    def updateTimer(self, dt=None):
        """ Обновление таймера """
        endTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
            time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
        updated = (endTime - utils.settings[2][6]) / 3600
        if updated >= 0:
            self.time2 = updated
        else:
            self.time2 = updated + 24
        if utils.settings[2][6] > 0:
            self.timerTime = "%s" % utils.timeFloatToHHMM(self.time2)
        else:
            self.timerTime = ""

        if ":" in self.timerTime:
            self.timer.on()
        else:
            self.timer.off()
        self.timerText.text = " [b]" + self.timerTime + "[/b]"

    def timerPressed(self, instance=None):
        self.updateTimer()
        result = self.rep.toggleTimer()
        if result == 1:
            self.rep.modify(")") # кредит выключен, записываем время служения сразу
        elif result == 2: # кредит включен, сначала спрашиваем, что записать
            self.popupForm = "timerType"
            self.popup(title="Таймер", message="Подсчитанное время: %s. Куда записать?" % self.timerTime,
                        options=["Служение", "Кредит"])

    def notePressed(self, instance=None):
        self.lastForm = self.displayed.form
        if self.displayed.form == "ter" or self.displayed.form == "con":
            self.detailsButton.disabled = True
        self.sortButton.disabled = True

        if self.displayed.form == "ter" or self.displayed.form == "con" or self.displayed.form == "createNewHouse" or \
             self.displayed.form == "createNewCon" or self.displayed.form == "search":
            self.lastForm = self.displayed.form
            self.displayed.form = "noteGlobal"
            self.createInputBox(
                title="Глобальная заметка",
                message="Любая произвольная информация для себя:",
                default=utils.resources[0][0],
                multiline=True
            )

        elif self.displayed.form == "set":
            webbrowser.open("https://github.com/antorix/Rocket-Ministry/wiki")

        elif self.displayed.form == "houseView" or self.displayed.form == "houseDetails" or \
                self.displayed.form == "createNewPorch":
            self.displayed.form = "noteForHouse"
            self.createInputBox(
                title="Заметка участка",
                message="Любая информация об участке:",
                default=self.house.note,
                multiline=True
            )

        elif self.displayed.form == "porchView" or self.displayed.form == "porchDetails"  or \
                self.displayed.form == "createNewFlat":
            self.displayed.form = "noteForPorch"
            self.createInputBox(
                title="Заметка подъезда",
                message="Любая информация о %sе:" % self.porch.type[:7],
                default=self.porch.note,
                multiline=True
            )

        elif self.displayed.form == "flatView" or self.displayed.form == "flatDetails" or \
                self.displayed.form == "createNewRecord" or self.displayed.form == "recordView":
            self.displayed.form = "noteForFlat"
            if "подъезд" in self.porch.type:
                title = "Заметка кв. " + self.flat.number
            else:
                title = "Заметка контакта " + self.flat.getName()
            self.createInputBox(
                title=title,
                message="Любая информация о человеке/квартире:",
                default=self.flat.note,
                multiline=True
            )

        elif "rep" in self.displayed.form: # журнал отчета
            options=[]
            for line in utils.resources[2]:
                options.append(line)
            self.feed.update(
                title="Журнал отчета",
                options=options,
                form="repLog",
                positive=self.button["save"],
                negative=self.button["cancel"]
            )
            self.displayed = self.feed
            self.update()

    # Действия главных кнопок positive, neutral, negative

    def positivePressed(self, instance=None, value=None):
        """ Что выполняет левая кнопка в зависимости от экрана """

        # Отчет

        if self.displayed.form == "rep":
            success = 1
            try:
                temp = int(self.placements.get())
            except:
                success = 0
            else:
                self.rep.placements = temp

            try:
                temp = int(self.video.get())
            except:
                success = 0
            else:
                self.rep.videos = temp

            try:
                temp = utils.timeHHMMToFloat(self.hours.get())
                if temp == None: # если конвертация не удалась, создаем ошибку
                    5/0
            except:
                success = 0
            else:
                self.rep.hours = temp

            try:
                if utils.settings[0][2]==1:
                    temp = utils.timeHHMMToFloat(self.credit.get())
                    if temp == None:
                        5/0
                else:
                    temp = 0
            except:
                success = 0
            else:
                self.rep.credit = temp

            try:
                temp = int(self.returns.get())
            except:
                success = 0
            else:
                self.rep.returns = temp

            try:
                temp = int(self.studies.get())
            except:
                success = 0
            else:
                self.rep.studies = temp

            if success == 1:
                if utils.settings[0][2] == 1:
                    credit = "кред.: %s, " % utils.timeFloatToHHMM(utils.settings[2][1])
                else:
                    credit = ""
                self.rep.saveReport(
                    message="Сохранены ручные значения: публ.: %d, видео: %d, часы: %s, %sповт.: %d, из.: %d" % (
                        self.rep.placements,
                        self.rep.videos,
                        utils.timeFloatToHHMM(self.rep.hours),
                        credit,
                        self.rep.returns,
                        self.rep.studies
                    )
                )
                self.backPressed()
            else:
                self.popup("Ошибка в каком-то из полей, проверьте данные!")

        elif self.displayed.form == "repLog":
            self.repPressed()

        # Настройки

        elif self.displayed.form == "set":
            try:
                utils.settings[0][3] = int(self.multipleBoxEntries[0].text.strip()) # норма часов
            except:
                pass
            utils.settings[0][13] = self.multipleBoxEntries[1].active # нет дома
            utils.settings[0][15] = self.multipleBoxEntries[2].active # переносить минуты
            utils.settings[0][10] = self.multipleBoxEntries[3].active # автоотказ
            utils.settings[0][2] = self.multipleBoxEntries[4].active  # кредит
            utils.settings[0][20] = self.multipleBoxEntries[5].active # показывать телефон
            utils.save()
            self.backPressed()

        elif self.displayed.form == "con":
            self.detailsButton.disabled = True
            self.displayed.form = "createNewCon"
            self.createInputBox(
                title="Создание контакта",
                message="Имя и (или) описание человека:",
                multiline=False
            )

        elif self.displayed.form == "flatView":
            self.detailsButton.disabled = True
            if len(self.flat.records) > 0:# or self.house.type == "virtual":
                self.displayed.form = "createNewRecord" # в этом случае позитивная кнопка - создание посещения
                self.detailsButton.disable = True
                self.createInputBox(
                    title=self.flatTitle + " — новое посещение",
                    message="О чем говорили?",
                    multiline=True,
                    addCheckBoxes=True
                )
            else: # в этом случае - сохранение первого посещения и выход в подъезд
                newName = self.multipleBoxEntries[0].text.strip()
                if len(self.flat.records) == 0:
                    if self.house.type != "virtual" or newName != "":
                        self.flat.updateName(newName)
                    if self.multipleBoxEntries[1].text.strip() != "":
                        self.flat.addRecord(self.multipleBoxEntries[1].text.strip())
                if int(self.addPlacement.get()) > 0:
                    self.rep.modify("б" + self.addPlacement.get())
                if int(self.addVideo.get()) > 0:
                    self.rep.modify("в" + self.addVideo.get())
                #if self.flat.status == "?":
                #    self.flat.status = "1"
                if self.contactsEntryPoint == 1:
                    self.conPressed()
                elif self.searchEntryPoint == 1:
                    self.find()
                else:
                    self.porchView()
                utils.save()

        # Форма создания квартир в подъезде

        elif self.displayed.form == "porchView":
            #self.detailsButton.disabled = True
            self.sortButton.disabled = True
            self.neutral.disabled = True
            self.displayed.form = "createNewFlat"
            if self.house.type == "condo":
                self.mainList.clear_widgets()
                self.listTitle.text = "Квартиры подъезда %s" % self.porch.title
                self.positive.text = self.button["save"]
                self.negative.text = self.button["cancel"]
                a = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(.9, .5))
                grid = GridLayout(rows=4, cols=2, size_hint=(1, 1))
                align="center"
                if len(self.porch.flats)==0: # определяем номер первой и последней квартир
                    firstflat = "1"
                    lastflat = "20"
                else:
                    firstflat, lastflat = self.porch.getFirstAndLastNumbers()
                if self.porch.type[7:] != "": # определяем кол-во этажей
                    floors = self.porch.type[7:]
                else:
                    floors = "5"
                size_hint = (None, .3)
                text_size = (Window.size[0]*.3, self.standardTextHeight*2)

                grid.add_widget(Label(text="Квартир:", halign=align, valign=align, color=self.standardTextColor,
                                      text_size=text_size))
                b1 = BoxLayout(orientation="horizontal")
                b1.add_widget(Label(text="c", color=self.standardTextColor))
                a1 = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, 1))
                self.flatRangeStart = TextInput(text=firstflat, multiline=False, size_hint=size_hint,
                                                height=self.standardTextHeight, width=self.standardTextWidth,
                                                input_type="number")
                a1.add_widget(self.flatRangeStart)
                self.flatRangeStart.bind(focus=self.onKeyboardFocusNum)
                b1.add_widget(a1)
                b1.add_widget(Label(text="по", color=self.standardTextColor))
                a2 = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, 1))
                self.flatRangeEnd = TextInput(text=lastflat, multiline=False, size_hint=size_hint,
                                              height=self.standardTextHeight, width=self.standardTextWidth,
                                              input_type="number")
                a2.add_widget(self.flatRangeEnd)
                self.flatRangeEnd.bind(focus=self.onKeyboardFocusNum)

                b1.add_widget(a2)
                grid.add_widget(b1)
                grid.add_widget(Label(text="Этажей:", halign=align, valign=align, color=self.standardTextColor,
                                      text_size=text_size))
                self.floors = Counter(text=floors, size_hint=(.7, .5))
                grid.add_widget(self.floors)
                grid.add_widget(Label(text="Номер 1-го\nэтажа:", halign=align, valign=align, color=self.standardTextColor,
                                      text_size=text_size))
                self.floor1 = Counter(text=str(self.porch.floor1), size_hint=(.7, .5))
                grid.add_widget(self.floor1)
                #grid.add_widget(Widget())
                a.add_widget(grid)
                self.mainList.add_widget(a)
            else:
                self.createInputBox(
                    title="Новые дома",
                    message="Введите номер дома (или другого объекта):",
                    checkbox="Массовое добавление",
                    active=False,
                    hint="1 / 1а / красный дом"
                )

        elif self.displayed.form == "search":
            self.backPressed()

        elif self.displayed.form == "houseView":
            self.displayed.form = "createNewPorch"
            if self.house.type == "condo":
                message = "Введите заголовок подъезда:"
                hint = "Номер или описание"
            else:
                message = "Для удобства участок можно разделить на части, или сегменты. Введите название нового сегмента:"
                hint = "1 / южная часть / администрация"
            self.createInputBox(
                title="Новый %s" % self.house.getPorchType()[0],
                message=message,
                hint=hint
            )

        elif self.displayed.form == "ter":
            self.detailsButton.disabled = True
            self.displayed.form = "createNewHouse"
            self.createInputBox(
                title="Новый участок",
                checkbox="Многоквартирный дом",
                active=True,
                message="Введите адрес участка:",
                hint="Пушкина, 30"
            )

        elif self.displayed.form == "createNewCon": # создание контакта
            self.displayed.form = "con"
            newContact = self.inputBoxEntry.text.strip()
            if self.inputBoxEntry.text.strip != "":
                utils.addHouse(utils.resources[1], "", "virtual")  # создается новый виртуальный дом
                utils.resources[1][len(utils.resources[1]) - 1].addPorch(input="virtual", type="virtual")
                utils.resources[1][len(utils.resources[1]) - 1].porches[0].addFlat("+" + newContact, virtual=True)
                utils.resources[1][len(utils.resources[1]) - 1].porches[0].flats[0].status = "1"
                utils.log("Создан контакт %s" % utils.resources[1][len(utils.resources[1]) - 1].porches[0].flats[0].getName())
                utils.save()
                self.conPressed()

        elif self.displayed.form == "createNewRecord": # создание записи посещения
            self.displayed.form = "flatView"
            record = self.inputBoxEntry.text.strip()
            if record != "":
                self.flat.addRecord(record)
            if int(self.addPlacement.get()) > 0:
                self.rep.modify("б" + self.addPlacement.get())
            if int(self.addVideo.get()) > 0:
                self.rep.modify("в" + self.addVideo.get())
            if self.addReturn.active == True:
                self.rep.modify("п")
            #if self.flat.status == "" or self.flat.status == "?":
            #    self.flat.status = "1"
            utils.save()
            self.flatView()

        elif self.displayed.form == "createNewFlat": # создание квартиры
            self.displayed.form = "porchView"
            if self.house.type == "condo": # создание квартир в подъезде
                try:
                    start = int(self.flatRangeStart.text.strip())
                    finish = int(self.flatRangeEnd.text.strip())
                    floors = int(self.floors.get())
                    f1 = int(self.floor1.get())
                    if start > finish or floors < 1:
                        5 / 0
                except:
                    self.popup(title="Что-то не сработало!",
                               message = "Все поля должны быть заполнены и иметь числовые значения. Кол-во этажей должно быть больше 0. Последняя квартира диапазона должна иметь номер не меньше первой квартиры.\n\nУ вас обязательно получится!"
                    )
                    self.porchView()
                    self.positivePressed()
                else:
                    self.porch.deleteHiddenFlats()
                    numbers = []
                    for flat in self.porch.flats:  # удаляем квартиры до и после заданного диапазона
                        if int(flat.number) < int(start):
                            numbers.append(flat.number)
                    for number in numbers:
                        for i in range(len(self.porch.flats)):
                            if self.porch.flats[i].number == number:
                                del self.porch.flats[i]
                                break
                    del numbers[:]
                    for flat in self.porch.flats:
                        if int(flat.number) > int(finish):
                            numbers.append(flat.number)
                    for number in numbers:
                        for i in range(len(self.porch.flats)):
                            if self.porch.flats[i].number == number:
                                del self.porch.flats[i]
                                break
                    self.porch.addFlats("+%d-%d[%d" % (start, finish, floors))
                    self.porch.flatsLayout = str(floors)
                    self.porch.floor1 = f1
                    utils.save()
                    self.porchView()

            else: # создание контактов в сегменте универсального участка
                addFlat = self.inputBoxEntry.text.strip()
                if self.checkbox.active == True:
                    addFlat2 = self.inputBoxEntry2.text.strip()
                if self.checkbox.active == False:
                    self.porch.addFlat("+" + addFlat)
                    utils.save()
                    self.porchView()
                else:
                    try:
                        self.porch.addFlats("+%d-%d" % (int(addFlat), int(addFlat2)))
                    except:
                        pass
                    else:
                        utils.save()
                        self.porchView()

        elif self.displayed.form == "createNewPorch":  # создание подъезда
            self.displayed.form = "houseView"
            newPorch = self.inputBoxEntry.text
            if newPorch == None:
                self.houseView()
                self.update()
            elif newPorch == "":
                self.inputBoxText.text = "Не сработало, попробуйте еще раз."
            else:
                for porch in self.house.porches:
                    if newPorch.strip() == porch.title:
                        self.inputBoxText.text = "Уже есть %s с таким названием, выберите другое!" % self.house.getPorchType()[0]
                        break
                else:
                    self.house.addPorch(newPorch, self.house.getPorchType()[0])
                    utils.save()
                    self.houseView()

        elif self.displayed.form == "createNewHouse": # создание участка
            self.displayed.form = "ter"
            newTer = self.inputBoxEntry.text
            condo = self.checkbox.active
            if newTer == "":
                self.inputBoxText.text = "Не сработало, попробуйте еще раз."
            else:
                for house in utils.houses:
                    if newTer.upper().strip() == house.title.upper().strip():
                        self.inputBoxText.text = "Уже есть участок с таким названием, выберите другое!"
                        break
                else:
                    utils.addHouse(utils.houses, newTer, condo)
                    utils.log("Создан участок «%s»" % newTer.upper())
                    utils.save()
                    self.terPressed()

        elif self.displayed.form == "noteForHouse": # заметка участка
            self.displayed.form = "houseView"
            self.house.note = self.inputBoxEntry.text.strip()
            utils.save()
            self.houseView()

        elif self.displayed.form == "noteForPorch": # заметка подъезда
            self.displayed.form = "porchView"
            self.porch.note = self.inputBoxEntry.text.strip()
            utils.save()
            self.porchView()

        elif self.displayed.form == "noteForFlat": # заметка квартиры
            self.displayed.form = "flatView"
            self.flat.editNote(self.inputBoxEntry.text.strip())
            utils.save()
            self.flatView()

        elif self.displayed.form == "noteGlobal":  # глобальная заметка
            self.displayed.form = "ter"
            utils.resources[0][0] = self.inputBoxEntry.text.strip()
            utils.save()
            self.terPressed()

        elif self.displayed.form == "recordView":  # редактирование записи посещения
            self.displayed.form = "flatView"
            newRec = self.inputBoxEntry.text.strip()
            if newRec != "":
                self.flat.editRecord(self.selectedRecord, newRec)
            else:
                self.flat.deleteRecord(self.selectedRecord)
            utils.save()
            self.flatView()

        elif self.displayed.form == "houseDetails":  # детали участка
            self.displayed.form = "houseView"
            newTitle = self.multipleBoxEntries[0].text.upper().strip()  # попытка изменить адрес - сначала проверяем, что нет дублей
            if newTitle == "":
                newTitle = self.house.title
            allow = True
            for i in range(len(utils.houses)):
                if utils.houses[i].title == newTitle and i != self.selectedHouse:
                    allow = False
                    break
            if allow == True:
                self.house.title = newTitle
                utils.save()
                self.houseView()
            else:
                self.detailsPressed()
                self.multipleBoxEntries[0].text = newTitle
                self.multipleBoxLabels[0].text = "Уже есть участок с таким названием!"
                return

            newDate = self.multipleBoxEntries[1].text.strip()
            if utils.checkDate(newDate)==True:
                self.house.date = newDate
                utils.save()
                self.houseView()
            else:
                self.detailsPressed()
                self.multipleBoxEntries[1].text = newDate
                self.multipleBoxLabels[1].text = "Дата должна быть в формате ГГГГ-ММ-ДД!"
                return

        elif self.displayed.form == "porchDetails":  # детали подъезда
            self.displayed.form = "porchView"
            newTitle = self.multipleBoxEntries[0].text.strip() # попытка изменить название подъезда - сначала проверяем, что нет дублей
            if newTitle == "":
                newTitle = self.porch.title
            allow = True
            for i in range(len(self.house.porches)):
                if self.house.porches[i].title == newTitle and i != self.selectedPorch:
                    allow = False
                    break
            if allow == True and newTitle:
                self.porch.title = newTitle
                utils.save()
                self.porchView()
            else:
                self.detailsPressed()
                self.multipleBoxEntries[0].text = newTitle
                self.multipleBoxLabels[0].text = "Уже есть %s с таким названием!" % self.porch.type[:7]

        elif self.displayed.form == "flatDetails":  # детали квартиры
            success = True
            self.displayed.form = "flatView"
            newName = self.multipleBoxEntries[0].text.strip()
            if newName != "" or self.house.type != "virtual":
                self.flat.updateName(newName)
            self.flat.editPhone(self.multipleBoxEntries[1].text.strip())
            if self.house.type == "virtual":
                self.house.title = self.multipleBoxEntries[2].text.strip()
            elif self.house.type != "condo": # попытка изменить номер дома - сначала проверяем, что нет дублей
                newNumber = self.multipleBoxEntries[2].text.strip()
                allow = True
                for i in range(len(self.porch.flats)):
                    if self.porch.flats[i].number == newNumber and i != self.selectedFlat:
                        allow = False
                        break
                if allow == True:
                    self.flat.updateTitle(newNumber)
                else:
                    success = False
                    self.detailsPressed()
                    self.multipleBoxEntries[2].text = newNumber
                    self.multipleBoxLabels[2].text = "Уже есть дом с таким названием!"
            if success == True:
                utils.save()
                self.flatView()

    def neutralPressed(self, instance=None, value=None):
        if self.displayed.form == "porchView":
            if self.porch.floors() == True:
                self.porch.flatsLayout = "н"
            else:
                self.porch.flatsLayout = self.porch.type[7:] # определение этажей по цифре в типе подъезда
                if self.porch.flatsLayout == "":
                    self.popup("Для этого подъезда еще не задавались этажи. Задайте их в разделе «Квартиры».")
            utils.save()
            self.porchView()
        elif icon("icon-phone-squared") in instance.text:
            if self.platform == "mobile":
                plyer.call.makecall(tel=self.flat.phone)
            else:
                Clipboard.copy(self.flat.phone)
                self.popup("Номер телефона %s скопирован в буфер обмена." % self.flat.phone)

    # Действия других кнопок

    def terPressed(self, instance=None):
        try:
            self.lastForm = self.displayed.form
        except:
            pass
        else:
            self.displayed.form = "ter"

        self.sortButton.disabled = False
        self.detailsButton.disabled = False
        self.neutral.disabled = True
        self.contactsEntryPoint = 0
        self.searchEntryPoint = 0
        self.note.text = icon("icon-sticky-note-o") + " Заметка"
        if utils.settings[0][19] == "д":  # first sort - by date
            utils.houses.sort(key=lambda x: x.date, reverse=False)
        elif utils.settings[0][19] == "н":  # alphabetic by title
            utils.houses.sort(key=lambda x: x.title, reverse=False)
        elif utils.settings[0][19] == "и":  # by number of interested persons
            for i in range(len(utils.houses)):
                utils.houses[i].interest = utils.houses[i].getHouseStats()[1]
            utils.houses.sort(key=lambda x: x.interest, reverse=True)
        elif utils.settings[0][19] == "п":  # by progress
            for i in range(len(utils.houses)):
                utils.houses[i].progress = utils.houses[i].getProgress()[0]
            utils.houses.sort(key=lambda x: x.progress, reverse=False)
        elif utils.settings[0][19] == "о":  # by progress reversed
            for i in range(len(utils.houses)):
                utils.houses[i].progress = utils.houses[i].getProgress()[0]
            utils.houses.sort(key=lambda x: x.progress, reverse=True)
        housesList = []

        for house in utils.houses:  # check houses statistics
            if house.getHouseStats()[1] > 0:
                interested = " [color=46CB18][b]%d[/b][/color] " % house.getHouseStats()[1]
            else:
                interested = " "
            d1 = datetime.strptime(house.date, "%Y-%m-%d")
            d2 = datetime.strptime(time.strftime("%Y-%m-%d", time.localtime()), "%Y-%m-%d")
            days_between = abs((d2 - d1).days)

            if days_between > 122:
                houseDue = "[color=FEDF00]" + icon("icon-attention")+" [/color]"
            else:
                houseDue = ""

            housesList.append("%s%s (%s) [i]%d%%[/i]%s" %
                              (houseDue,
                               house.title,
                               utils.shortenDate(house.date),
                               int(house.getProgress()[0] * 100),
                               interested
                               )
                              )

        if len(housesList) == 0:
            housesList.append("Создайте свой первый участок")

        self.feed.update(  # display list of houses and options
            title="Участки (%d)" % len(utils.houses),
            # houses sorting type, timer icon
            message="Список участков:",
            options=housesList,
            form="ter",
            positive=icon("icon-plus-circled-1") + " Новый участок",
            negative=self.button["cancel"]
        )
        self.displayed = self.feed
        self.update()
        if utils.resources[0][0].strip() != "":
            self.note.text = icon("icon-sticky-note") + " Заметка"
        else:
            self.note.text = icon("icon-sticky-note-o") + " Заметка"

        self.sortButton.disabled = False

    def conPressed(self, instance=None):

        self.lastForm = self.displayed.form
        self.displayed.form = "con"
        self.contactsEntryPoint = 1
        self.searchEntryPoint = 0
        self.detailsButton.disabled = True
        self.neutral.disabled = True
        self.allcontacts = self.getContacts()
        options = []

        # Sort
        if utils.settings[0][4] == "и":
            self.allcontacts.sort(key=lambda x: x[0])  # by name
        elif utils.settings[0][4] == "с":
            self.allcontacts.sort(key=lambda x: x[16])  # by status
        elif utils.settings[0][4] == "а":
            self.allcontacts.sort(key=lambda x: x[2])  # by address
        elif utils.settings[0][4] == "т":
            self.allcontacts.sort(key=lambda x: x[9], reverse=True)  # by phone number

        for i in range(len(self.allcontacts)):
            if self.allcontacts[i][15] != "condo" and self.allcontacts[i][15] != "virtual":
                porch = self.allcontacts[i][12] + ", "
                gap = ", "
            else:
                porch = gap = ""
            if self.allcontacts[i][5] != "":
                appointment = "%s " % self.allcontacts[i][5][0:5]  # appointment
            else:
                appointment = ""
            if self.allcontacts[i][9] != "":
                phone = "%s%s " % ("т.", self.allcontacts[i][9])  # phone
            else:
                phone = ""
            if "подъезд" in self.allcontacts[i][8]:
                hyphen = "-"
            else:
                hyphen = ""
            if self.allcontacts[i][2] != "":
                address = "(%s%s%s%s%s) " % (self.allcontacts[i][2], gap, porch, hyphen, self.allcontacts[i][3])
            else:
                address = ""
            if self.allcontacts[i][11] != "":
                note = "• " + self.allcontacts[i][11]
            else:
                note = ""

            options.append(
                "%s%s %s%s%s%s" % (
                    self.allcontacts[i][1],
                    self.allcontacts[i][0],
                    address,
                    appointment,
                    phone,
                    note,
                )
            )

        if len(options) == 0:
            options.append("Здесь будут отображаться жильцы со всех участков и отдельные контакты, созданные вами.")

        self.feed.update(
            form="con",
            title="Контакты (%d)" % len(self.allcontacts),
            message="Список контактов:",
            options=options,
            positive=icon("icon-plus-circled-1") + " Новый контакт",
            negative=self.button["cancel"]
        )
        self.displayed = self.feed
        self.update()

        if utils.resources[0][0].strip() != "":
            self.note.text = icon("icon-sticky-note") + " Заметка"
        else:
            self.note.text = icon("icon-sticky-note-o") + " Заметка"

        self.sortButton.disabled = False

    def repPressed(self, instance=None):

        self.detailsButton.disabled = True
        self.neutral.disabled = True
        self.sortButton.disabled = True

        self.note.text = icon("icon-history") + " Журнал"
        self.lastForm = self.displayed.form
        self.listTitle.text = "Отчет"
        self.detailsButton.disabled = True
        self.displayed.form = "rep"
        self.positive.text = self.button["save"]
        self.negative.text = self.button["cancel"]

        self.reportPanel = TabbedPanel(background_color=self.globalBGColor0)
        tab1 = TabbedPanelHeader(text=utils.monthName()[0])#, background_color=self.tableBGColor, background_normal="", color=self.tableColor)
        tab2 = TabbedPanelHeader(text=utils.monthName()[2])#, background_color=self.tableBGColor, background_normal="", color=self.tableColor)

        self.listTitle.text = "Отчет %s" % self.rep.getCurrentHours()[2]

        text_size = (Window.size[0]/3, None)

        self.mainList.clear_widgets()
        a = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, 1))
        report = GridLayout(cols=2, rows=7, size_hint=(.9, .9), spacing=self.spacing, padding=self.padding,
                            pos_hint={"center_x": .7})
        size_hint = (1, 1)

        report.add_widget(Label(text="Публикации", halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.placements = Counter(text = str(self.rep.placements), size_hint=size_hint)
        report.add_widget(self.placements)

        #report.add_widget(Widget())

        report.add_widget(Label(text="Видео", halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.video = Counter(text=str(self.rep.videos), size_hint=size_hint)
        report.add_widget(self.video)

        #report.add_widget(Widget())

        report.add_widget(Label(text="Часы", halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.hours = Counter(type="time", text=utils.timeFloatToHHMM(self.rep.hours), size_hint=size_hint)
        report.add_widget(self.hours)

        #report.add_widget(Widget())

        if utils.settings[0][2]==1:
            report.add_widget(Label(text="Кредит (итого с часами %s)" % self.rep.getCurrentHours()[0], markup=True,
                                    halign="center", valign="center", text_size = text_size, color=self.standardTextColor))
            self.credit = Counter(type="time", text=utils.timeFloatToHHMM(self.rep.credit), size_hint=size_hint)
            report.add_widget(self.credit)

            #report.add_widget(Widget())

        report.add_widget(Label(text="Повторные посещения", halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.returns = Counter(text = str(self.rep.returns), size_hint=size_hint)
        report.add_widget(self.returns)

        #report.add_widget(Widget())

        report.add_widget(Label(text="Изучения Библии", halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.studies = Counter(text = str(self.rep.studies), size_hint=size_hint)
        report.add_widget(self.studies)

        #report.add_widget(Widget())

        a.add_widget(report)
        tab1.content = a
        self.reportPanel.add_widget(tab1)

        # Вторая вкладка: отчет прошлого месяца

        report2 = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, 1))

        self.lastRepHint = "\n\n[color=%s]" % self.mainMenuButtonColor2 + icon("icon-share-squared") + " Отправить[/color]"

        self.btnRep = Button(text=self.rep.getLastMonthReport()[0]+self.lastRepHint, valign="center", halign="center",
                                  text_size=(Window.size[0]*.7, Window.size[1]*.7), markup=True,
                             color=self.standardTextColor, background_down=self.buttonPressedBG,
                                  background_color=self.tableBGColor, background_normal="",
                             size_hint=(.8, .7))
        self.btnRep.bind(on_press=self.sendLastMonthReport)
        report2.add_widget(self.btnRep)
        tab2.content = report2
        self.reportPanel.add_widget(tab2)
        self.reportPanel.do_default_tab = False
        self.mainList.add_widget(self.reportPanel)

        if self.firstRunFlag == True:
            self.onFirstRun()

    def sendLastMonthReport(self, instance):
        """ Отправка отчета прошлого месяца """
        plyer.email.send(text=self.rep.getLastMonthReport()[1])

    def settingsPressed(self, instance=None):
        """ Настройки """

        self.lastForm = self.displayed.form
        self.displayed.form = "set"
        self.detailsButton.disabled = True
        self.sortButton.disabled = True

        self.mainList.clear_widgets()
        box = BoxLayout(orientation="vertical", size_hint=(1, 1))
        tabbedPanel = TabbedPanel(background_color=self.globalBGColor0)

        if utils.settings[0][5] == "Темная":
            theme = True
        else:
            theme = False

        self.createMultipleInputBox(
            form=box,
            title="Настройки",
            options=[
                "Месячная норма часов",
                "{}«Нет дома» одним кликом",
                "{}Переносить минуты на\nследующий месяц",  # {} = вместо строки ввода должна быть галочка
                "{}Синий цвет всегда ставит\nзапись «отказ»",
                "{}Кредит часов",
                "{}Ввод телефона одним кликом"
            ],
            defaults=[
                utils.settings[0][3],   # норма часов
                utils.settings[0][13],  # нет дома
                utils.settings[0][15],  # переносить минуты
                utils.settings[0][10],  # автоотказ
                utils.settings[0][2],   # кредит часов
                utils.settings[0][20],  # показывать телефон
            ],
            multilines=[False, False, False, False, False, False]
        )

        # Первая вкладка: настройки

        tab1 = TabbedPanelHeader(text="Настройки")
        tab1.content = box
        tabbedPanel.add_widget(tab1)

        # Вторая вкладка: работа с данными

        size_hint = (1, 1)
        text_size = [Window.size[0]/2.5, Window.size[1]/2.5]
        tab2 = TabbedPanelHeader(text="Данные")
        g = GridLayout(rows=2, cols=2, size_hint=(1, 1), spacing="10dp", padding=[30, 30, 30, 30])

        exportEmail = Button(text=icon("icon-share-1") + " Экспорт", markup=True, color=self.tableColor,
                          valign="center", halign="center", text_size=text_size, background_down=self.buttonPressedBG,
                          background_normal="", background_color=self.tableBGColor, size_hint=size_hint)
        def __export(instance):
            if self.platform == "mobile":
                utils.share(email=True)
            else:
                utils.share(doc=True)
        exportEmail.bind(on_press=__export)
        g.add_widget(exportEmail)

        importBtn = Button(text=icon("icon-download-1") + " Импорт", markup=True, background_down=self.buttonPressedBG,
                           text_size=text_size, valign="center", color=self.tableColor,
                           halign="center", background_normal="", background_color=self.tableBGColor,
                           size_hint=size_hint)
        importBtn.bind(on_press=self.importDB)
        g.add_widget(importBtn)

        if self.platform == "desktop":
            g.rows += 1
            importFile = Button(text=icon("icon-folder-open") + " Импорт из файла", markup=True,
                               text_size=text_size, valign="center", color=self.tableColor, background_down=self.buttonPressedBG,
                               halign="center", background_normal="", background_color=self.tableBGColor,
                               size_hint=size_hint)
            def __importFile(instance):
                from tkinter import filedialog
                file = filedialog.askopenfilename()
                if file != "":
                    self.importDB(wordFile=file)
            importFile.bind(on_press=__importFile)
            g.add_widget(importFile)

        restoreBtn = Button(text=icon("icon-upload-1") + " Восстановление", markup=True,
                           text_size=text_size, valign="center", color=self.tableColor, background_down=self.buttonPressedBG,
                           halign="center", background_normal="", background_color=self.tableBGColor,
                           size_hint=size_hint)
        def __restore(instance):
            result = utils.backupRestore(restoreWorking=True)
            if result == True:
                self.rep = report.Report()
                utils.save()
        restoreBtn.bind(on_press=__restore)
        g.add_widget(restoreBtn)

        clearBtn = Button(text=icon("icon-trash-1")+" Очистка", markup=True, text_size=text_size, valign="center",
                          halign="center", background_normal = "", color=self.tableColor, background_down=self.buttonPressedBG,
                          background_color=self.tableBGColor, size_hint=size_hint)
        def __clear(instance):
            self.popup(message="Все пользовательские данные будут полностью удалены из приложения! Вы уверены, что это нужно сделать?",
                       options=[self.button["yes"], self.button["no"]])
            self.popupForm = "clearData"
        clearBtn.bind(on_press=__clear)
        g.add_widget(clearBtn)

        tab2.content = g
        tabbedPanel.add_widget(tab2)

        # Третья вкладка: о программе

        tab3 = TabbedPanelHeader(text="О программе")
        a = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, 1))
        box3 = BoxLayout(orientation="vertical", size_hint=(.9, .5))
        #box3.add_widget(Label(background_normal="icon.png", size=(128, 128)))
        aboutBtn = Button(text=
                            "[color=36ACD8][b]Rocket Ministry %s[/b][/color]\n\n" % utils.Version +\
                            "Универсальная система служения\n\n" + \
                            "Последнее изменение базы данных: %s\n\n" % utils.getDBCreatedTime() + \
                            "Официальный Telegram-канал:\n[color=36ACD8][u]RocketMinistry[/u] " + icon("icon-telegram") + "[/color]",
            markup=True, background_color=self.globalBGColor, text_size=(Window.size[0]*.9, Window.size[1]*.5),
            halign="left", valign="center", color=self.standardTextColor, background_normal="", background_down=self.buttonPressedBG)
        def __telegram(instance):
            webbrowser.open("https://t.me/rocketministry")
        aboutBtn.bind(on_press=__telegram)
        a.add_widget(aboutBtn)
        box3.add_widget(a)

        tab3.content = a
        tabbedPanel.add_widget(tab3)
        tabbedPanel.do_default_tab = False
        self.mainList.add_widget(tabbedPanel)

        self.note.text = icon("icon-help-circled") + " Помощь"

    def searchPressed(self, query="", instance=None):
        self.popupForm = "search"
        self.popup(title="Поиск")

    def find(self):
        self.lastForm = self.displayed.form
        self.contactsEntryPoint = 0
        allContacts = self.getContacts(forSearch=True)
        self.searchResults = []
        self.detailsButton.disabled = True
        #self.note.disabled = True
        for i in range(len(allContacts)):  # start search in flats/contacts
            found = False
            if self.searchQuery in allContacts[i][2].lower() or self.searchQuery in allContacts[i][2].lower() or self.searchQuery in \
                    allContacts[i][3].lower() or self.searchQuery in allContacts[i][8].lower() or self.searchQuery in \
                    allContacts[i][
                        10].lower() or self.searchQuery in allContacts[i][11].lower() or self.searchQuery in allContacts[i][
                12].lower() or self.searchQuery in allContacts[i][13].lower():
                found = True

            if allContacts[i][8] != "virtual":
                for r in range(len(utils.houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[
                                       allContacts[i][7][2]].records)):  # in records in flats
                    if self.searchQuery in utils.houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[
                        allContacts[i][7][2]].records[r].title.lower():
                        found = True
                    if self.searchQuery in utils.houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[
                        allContacts[i][7][2]].records[r].date.lower():
                        found = True
            else:
                for r in range(len(utils.resources[1][allContacts[i][7][0]].porches[0].flats[
                                       0].records)):  # in records in contacts
                    if self.searchQuery in utils.resources[1][allContacts[i][7][0]].porches[0].flats[0].records[
                        r].title.lower():
                        found = True
                    if self.searchQuery in utils.resources[1][allContacts[i][7][0]].porches[0].flats[0].records[
                        r].date.lower():
                        found = True

            if found == True:
                self.searchResults.append([allContacts[i][7], allContacts[i][8], allContacts[i][2]])

        options = []
        for i in range(len(self.searchResults)):  # save results
            number = "%d) " % (i + 1)
            if self.searchResults[i][1] != "virtual":  # for regular flats
                options.append("%s%s-%s" % (number, utils.houses[self.searchResults[i][0][0]].title,
                                             utils.houses[self.searchResults[i][0][0]].porches[self.searchResults[i][0][1]].flats[
                                                 self.searchResults[i][0][2]].title))
            else:  # for standalone contacts
                if utils.resources[1][self.searchResults[i][0][0]].title == "":
                    title = ""
                else:
                    title = utils.resources[1][self.searchResults[i][0][0]].title + ", "
                options.append("%s%s%s" % (
                    number,
                    title,
                    utils.resources[1][self.searchResults[i][0][0]].porches[0].flats[0].title))

        if len(options) == 0:
            options.append("Ничего не найдено")

        self.feed.update(
            form="search",
            title="Поиск по запросу \"%s\"" % self.searchQuery,
            message="Результаты:",
            options=options,
            positive=self.button["ok"],
            negative=self.button["cancel"]
        )
        self.displayed = self.feed
        self.update()

    # Функции по обработке участков

    def houseView(self, house=None, selectedHouse=None):
        """ Вид участка - список подъездов """

        if house == None:
            house = self.house
        if selectedHouse != None:
            house = utils.houses[selectedHouse]

        self.feed.update(
            form="houseView",
            title=house.title,
            options=house.showPorches(),
            positive=icon("icon-plus-circled-1") + " Новый " + house.getPorchType()[0],
            negative=self.button["exit"]
        )
        self.displayed = self.feed

        self.update()

        if house.note.strip() != "":
            self.note.text = icon("icon-sticky-note") + " Заметка"
        else:
            self.note.text = icon("icon-sticky-note-o") + " Заметка"

        self.detailsButton.disabled = False
        self.neutral.disabled = True

    def porchView(self, porch=None, selectedPorch=None, instance=None):
        """ Вид подъезда - список квартир или этажей """
        if self.porch.type == "virtual": # на всякий случай страховка от захода в виртуальный подъезд
            if self.contactsEntryPoint == 1:
                self.conPressed()
                return
            elif self.searchEntryPoint == 1:
                self.find()
                return

        if porch == None:
            porch = self.porch
        if selectedPorch != None:
            porch = self.house[selectedPorch]

        if "подъезд" in porch.type:
            positive = " Квартиры"
        else:
            positive = " Дома"

        options = porch.showFlats()
        self.feed.update(
            title="%s %s" % (porch.type[0:7], porch.title),
            options=options,
            form="porchView",
            positive=icon("icon-plus-circled-1") + positive,
            negative=self.button["exit"]
        )
        self.displayed = self.feed

        self.update()

        if porch.note.strip() != "":
            self.note.text = icon("icon-sticky-note") + " Заметка"
        else:
            self.note.text = icon("icon-sticky-note-o") + " Заметка"

        self.detailsButton.disabled = False

        if "подъезд" in self.porch.type:  # Отрисовка нижних клавиш (positive, view, neutral)
            self.neutral.disabled = False

        if self.porch.floors() == True:
            self.neutral.text = icon("icon-th-1")
        else:
            self.neutral.text = icon("icon-menu")
            self.sortButton.disabled = False

        try: # пытаемся всегда возвраться на последнюю квартиру
            self.scroll.scroll_to(widget=self.btn[self.clickedBtnIndex], padding=0, animate=False)
        except:
            pass

    def findFlatByNumber(self, number):
        """ Находит квартиру по номеру квартиры в данном подъезде и возвращает ее экземпляр
            Number здесь - фактический отображаемый номер квартиры (не индекс) """
        try:
            number = number[0: number.index(" ")].strip()
        except:
            number = number.strip()
        for i in range(len(self.porch.flats)):
            if number == self.porch.flats[i].number:
                return self.porch.flats[i]

    def flatView(self, flat=None, selectedFlat=None, call=True):
        """ Вид квартиры - список записей посещения """
        if flat == None:
            flat = self.flat
        if selectedFlat != None:
            flat = self.porch[selectedFlat]

        self.detailsButton.disabled = False

        if flat.number == "virtual":  # прячем номера отдельных контактов
            number = " "
        else:
            number = flat.number + " "
        if "подъезд" in self.porch.type:
            flatPrefix = "кв. "
        else:
            flatPrefix = ""
        self.flatTitle = flatPrefix + number + flat.getName()
        self.feed.update(
            title=self.flatTitle,
            message="Список посещений:",
            options=flat.showRecords(),
            form="flatView",
            positive= icon("icon-plus-circled-1") + " Новое посещение",
            negative=self.button["exit"]
        )
        self.displayed = self.feed

        if call == False and self.flat.status == "": # всплывающее окно первого посещения
            self.popup(firstCall=True)
            self.porchView()
            #self.scroll.scroll_to(self.btn[self.selectedFlat])

        else:
            if len(self.flat.records) == 0:  # если нет посещения, открывается специальное окно первого посещения
                self.scrollWidget.clear_widgets()#self.displayed.form = "firstCall"
                options2 = ["Имя и (или) описание человека:", "О чем говорили:"]
                defaults = [self.flat.getName(), ""]
                multilines = [False, True]
                self.createMultipleInputBox(
                    title=self.flatTitle + "— первое посещение",
                    options=options2,
                    defaults=defaults,
                    multilines=multilines,
                    addCheckBoxes=True
                )
            else:
                self.update()

            colorBtn = []
            for i, status in zip(range(6), ["0", "1", "2", "3", "4", "5"]):
                colorBtn.append(Button(size_hint_x=1, size_hint_max_y=.8, background_normal="",
                                       background_color=self.getColorForStatus(status)))
                colorBtn[i].bind(on_press=self.colorBtnPressed)
                if self.flat.getStatus()[0][1] == status:
                    colorBtn[i].text = "•"
                    colorBtn[i].font_size = self.fontXXL*1.5
            colorBox = BoxLayout(size_hint=(1, None), height=Window.size[0]/6,
                                 spacing=self.spacing, padding=self.padding)
            colorBox.add_widget(colorBtn[1])
            colorBox.add_widget(colorBtn[2])
            colorBox.add_widget(colorBtn[3])
            colorBox.add_widget(colorBtn[4])
            colorBox.add_widget(colorBtn[0])
            colorBox.add_widget(colorBtn[5])
            self.mainList.add_widget(colorBox)

            if self.flat.phone != "":  # добавляем кнопку телефона
                self.neutral.disabled = False
                self.neutral.text = icon("icon-phone-squared")
            else:
                self.neutral.disabled = True

            self.detailsButton.disabled = False

            if flat.note.strip() != "":
                self.note.text = icon("icon-sticky-note") + " Заметка"
            else:
                self.note.text = icon("icon-sticky-note-o") + " Заметка"

    def recordView(self):
        self.displayed.form = "recordView"
        self.detailsButton.disabled = False
        self.createInputBox(
            title = "%s, %s" % (self.flatTitle, self.record.date),
            message = "О чем говорили?",
            default = self.record.title,
            multiline=True
        )
        self.positive.text = "Изменить"

    # Диалоговые окна

    def createFirstCallBoxes(self, addReport=False):
        """ Создает галочки для первого посещения, возвращает экземпляр с боксом"""
        self.FirstCallBoxes = BoxLayout(orientation="vertical", size_hint=(1, 1))
        size_hint = (1, 1)
        text_size = (Window.size[0]/4, self.standardTextHeight)
        if addReport == True:
            grid2 = GridLayout(rows=3, cols=3, size_hint=size_hint)
            grid2.add_widget(Label(text="[b]В отчет:[/b]", halign="center", valign="center", text_size=text_size,
                               markup=True, height=self.standardTextHeight, size_hint=size_hint,
                                   color=self.standardTextColor))
            grid2.add_widget(Widget())
            grid2.add_widget(Widget())
        else:
            grid2 = GridLayout(rows=3, cols=2, size_hint=size_hint)

        grid2.add_widget(Label(text="публикации", halign="center", valign="center", text_size=text_size,
                               height=self.standardTextHeight, size_hint=size_hint, color=self.standardTextColor))
        grid2.add_widget(Label(text="видео", halign="center", valign="center", text_size=text_size,
                               height=self.standardTextHeight, size_hint=size_hint, color=self.standardTextColor))
        if addReport == True:
            grid2.add_widget(Label(text="повторное", halign="center", valign="center", text_size=text_size,
                               height=self.standardTextHeight, size_hint=size_hint, color=self.standardTextColor))
        self.addPlacement = Counter(text="0", size_hint = (.7, 1))
        grid2.add_widget(self.addPlacement)
        self.addVideo = Counter(text="0", size_hint = (.7, 1))
        grid2.add_widget(self.addVideo)
        if addReport == True:
            self.addReturn = CheckBox(active=False, size_hint = (1, 1), color=self.titleColor)
            grid2.add_widget(self.addReturn)
        self.FirstCallBoxes.add_widget(grid2)

        return self.FirstCallBoxes

    def createInputBox(self, title="", message="", default="", hint="", checkbox=None, active=True, input=True,
                       multiline=False, addCheckBoxes=False):

        self.mainList.clear_widgets()
        self.listTitle.text = title
        self.positive.text = self.button["save"]
        self.negative.text = self.button["cancel"]
        if self.displayed.form != "flatView" and self.displayed.form != "flatDetails" and \
                self.displayed.form != "noteForFlat":
            self.neutral.disabled = True
        elif self.flat.phone != "":
            self.neutral.disabled = False
        self.sortButton.disabled = True
        height = self.standardTextHeight
        a = AnchorLayout(anchor_x="center", anchor_y="top", size_hint=(1, 1))
        if multiline == False:
            hint_y = .8
        else:
            hint_y = 1
        grid = GridLayout(rows=5, cols=1, size_hint=(1, hint_y), spacing=self.spacing*2, padding=self.padding*2)
        self.inputBoxText = Label(text=message, color=self.standardTextColor, valign="center",
                                  halign="center", text_size = (Window.size[0]*.9, self.standardTextHeight*2),
                                  size_hint=(1, hint_y))
        grid.add_widget(self.inputBoxText)
        if input == True:
            if multiline==True:
                size_hint=(1, 1)
            else:
                size_hint = (1, None)
            textbox = BoxLayout(size_hint=(1, 1), pos_hint={"center_x": .5})
            self.inputBoxEntry = TextInput(multiline=multiline, hint_text=hint, size_hint=size_hint, height=height)
            textbox.add_widget(self.inputBoxEntry)
            grid.add_widget(textbox)

        b = BoxLayout(orientation="vertical", size_hint=(1, 1), pos_hint={"center": 1})
        if checkbox != None: # если заказана галочка, добавляем
            grid.add_widget(Widget())
            self.checkbox = CheckBox(active=active, size_hint=(1, None), height=height,
                                     color=self.titleColor)
            b.add_widget(self.checkbox)
            def __on_checkbox_active(checkbox, value): # что происходит при активированной галочке
                if self.displayed.form == "createNewHouse":
                    if value == 1:
                        self.inputBoxText.text = message
                        self.inputBoxEntry.hint_text = hint
                    else:
                        self.inputBoxText.text = "Введите название участка:"
                        self.inputBoxEntry.hint_text = "ул. Радужная / ТЦ Прогресс"

                elif self.displayed.form == "createNewFlat":
                    if value == 1:
                        self.inputBoxText.text = "Введите первый и последний номера добавляемого диапазона:"
                        textbox.remove_widget(self.inputBoxEntry)
                        height = self.standardTextHeight
                        self.inputBoxEntry = TextInput(hint_text = "От", multiline=multiline, height=height,
                                                       size_hint=(Window.size[0]/2, None),
                                                       input_type="number")
                        textbox.add_widget(self.inputBoxEntry)
                        self.inputBoxEntry2 = TextInput(hint_text = "до", multiline=multiline, height=height,
                                                        size_hint=(Window.size[0]/2, None),
                                                        input_type="number")
                        self.inputBoxEntry.bind(on_text_validate=self.positivePressed)
                        self.inputBoxEntry.bind(focus=self.onKeyboardFocusNum)
                        self.inputBoxEntry2.bind(focus=self.onKeyboardFocusNum)
                        textbox.add_widget(self.inputBoxEntry2)
                    else:
                        self.porchView()
                        self.positivePressed()

            self.checkbox.bind(active=__on_checkbox_active)

            b.add_widget(Label(text=checkbox, color=self.standardTextColor, halign="center", valign="top",
                               size_hint=(1, None), height=height, text_size=(Window.size[0], 0)))

            grid.add_widget(b)

        else: # если галочки нет, добавляем пустой виджет
            b.add_widget(Widget(size_hint=(1, 1), height=height))
            if multiline == False:
                grid.size_hint = (1, .5)

        if "recordView" in self.displayed.form or "note" in self.displayed.form: # добавление корзины
            grid.add_widget(self.bin())

        elif addCheckBoxes == True: # добавляем галочки для нового посещения
            grid.add_widget(self.createFirstCallBoxes(addReport=True))
        else:
            grid.add_widget(Widget(size_hint=(1, 1)))

        self.inputBoxEntry.text = default
        self.inputBoxEntry.bind(on_text_validate=self.positivePressed)
        self.inputBoxEntry.bind(focus=self.onKeyboardFocus)
        a.add_widget(grid)
        self.mainList.add_widget(a)

    def createMultipleInputBox(self, form=None, title=None, options=[], defaults=[], multilines=[],
                               addCheckBoxes=False): # форма ввода с разными полями, используется для первого посещения и деталей
        if form == None: # по умолчанию вывод делается на mainlist, но можно вручную указать другую форму
            form = self.mainList
        
        form.clear_widgets()
        if title != None:
            self.listTitle.text = title
        self.positive.text = self.button["save"]
        self.negative.text = self.button["cancel"]
        if self.displayed.form != "flatView" and self.displayed.form != "flatDetails" and \
                self.displayed.form != "noteForFlat":
            self.neutral.disabled = True
        elif self.flat.phone != "":
            self.neutral.disabled = False
        self.sortButton.disabled = True
        grid = GridLayout(rows=len(options), cols=2, size_hint = (1, 1), pos_hint={"top": 1}, spacing=self.spacing*2,
                                                                                            padding=self.padding*2)
        self.multipleBoxLabels = []
        self.multipleBoxEntries = []
        for row, default, multiline in zip( range(len(options)), defaults, multilines):
            if "{}" in str(options[row]):
                text = str(options[row][2:]).strip()
                checkbox = True
            else:
                text = options[row].strip()
                checkbox = False
            if multiline == True:
                y = 1
            else:
                y = 1#None
            if self.displayed.form == "set":
                labelSize_hint=(1, 1)
                entrySize_hint=(.3, y)
                text_size = (Window.size[0]*0.66, self.standardTextHeight*2)
            else:
                labelSize_hint = (.5, 1)
                entrySize_hint = (.5, y)
                text_size = (Window.size[0]/2, self.standardTextHeight*2)

            self.multipleBoxLabels.append(Label(text=text, valign="center", halign="center", size_hint=labelSize_hint,
                                  color = self.standardTextColor, text_size=text_size))

            grid.add_widget(self.multipleBoxLabels[row])
            if checkbox == False:
                self.multipleBoxEntries.append(TextInput(multiline=multiline, size_hint=entrySize_hint, pos_hint={"top": 1},
                                                         height=self.standardTextHeight))
                self.multipleBoxEntries[row].text = str(default)
                if self.displayed.form == "set" or "Дата взятия" in self.multipleBoxLabels[row].text:
                    self.multipleBoxEntries[row].bind(focus=self.onKeyboardFocusNum)
                    self.multipleBoxEntries[row].input_type = "number"
                    self.multipleBoxEntries[row].keyboard_suggestions = False
                else:
                    self.multipleBoxEntries[row].bind(focus=self.onKeyboardFocus)
                    self.multipleBoxEntries[row].input_type = "text"

            else:
                self.multipleBoxEntries.append(CheckBox(active=default, size_hint=entrySize_hint, pos_hint = {"top": 1},
                                               color=self.titleColor))
            grid.add_widget(self.multipleBoxEntries[row])

        grid.rows += 1
        if "Details" in self.displayed.form: # добавление корзины
            while 1:
                if self.displayed.form == "flatDetails" and "подъезд" in self.porch.type and self.porch.floors() == False:
                    grid.add_widget(Widget()) # в квартире подъезда в режиме списка корзины нет
                    grid.add_widget(Widget())
                    break
                elif self.displayed.form == "flatDetails" and "подъезд" in self.porch.type and\
                    self.porch.floors() == True and self.contactsEntryPoint != 1 and self.searchEntryPoint != 1:
                    grid.add_widget(Widget())
                    grid.add_widget(self.bin(" Уменьшить этаж"))
                    break
                else:
                    grid.add_widget(Widget())
                    grid.add_widget(self.bin())
                    break

        elif addCheckBoxes == True: # добавляем галочки для нового посещения
            grid.add_widget(Label(text="В отчет:", color=self.standardTextColor))
            grid.add_widget(self.createFirstCallBoxes(addReport=False))

        elif self.displayed.form == "set": # добавляем выбор темы для настроек
            grid.rows += 1
            grid.add_widget(Label(text="Тема интерфейса", valign="center", halign="center", size_hint=labelSize_hint,
                                  color = self.standardTextColor, text_size=text_size))

            tBox = GridLayout(rows=2, cols=2, size_hint=(.5, .7), padding=self.padding, spacing=self.spacing)
            def __changeTheme(instance):
                if instance.color == self.themeDefault[1]:
                    utils.settings[0][5] = "default"
                elif instance.color == self.themePurple[1]:
                    utils.settings[0][5] = "purple"
                elif instance.background_color == self.themeTeal[0]:
                    utils.settings[0][5] = "teal"
                elif instance.background_color == self.themeDark[0]:
                    utils.settings[0][5] = "dark"
                self.positivePressed()
                self.popup("Для смены темы необходим перезапуск программы. Сделать это сейчас?",
                           options=[self.button["yes"], self.button["no"]])
                self.popupForm = "restart"

            size_hint = (1, 1)
            bt1 = Button(text="[b]A[/b]", markup=True, color=self.themeDefault[1], background_color=self.themeDefault[0],
                         background_normal="", pos_hint={"center_y":.5}, size_hint=size_hint)
            bt2 = Button(text="[b]A[/b]", markup=True, color=self.themePurple[1], background_color=self.themePurple[0],
                         background_normal="", pos_hint={"center_y": .5}, size_hint=size_hint)
            bt3 = Button(text="[b]A[/b]", markup=True, color=self.themeTeal[1], background_color=self.themeTeal[0],
                         background_normal="", pos_hint={"center_y":.5}, size_hint=size_hint)
            bt4 = Button(text="[b]A[/b]", markup=True, color=self.themeDark[1], background_color=self.themeDark[0],
                         background_normal="", pos_hint={"center_y":.5}, size_hint=size_hint)

            bt1.bind(on_press=__changeTheme)
            bt2.bind(on_press=__changeTheme)
            bt3.bind(on_press=__changeTheme)
            bt4.bind(on_press=__changeTheme)
            tBox.add_widget(bt1)
            tBox.add_widget(bt2)
            tBox.add_widget(bt3)
            tBox.add_widget(bt4)
            grid.add_widget(tBox)

        form.add_widget(grid)
        return grid

    def bin(self, label=None):
        """Создание корзины. Возвращает объект, который можно привязать к любому виджету - получится корзина"""
        if label == None:
            size = (Window.size[0] / 4, self.standardTextHeight)
            text = icon("icon-trash-1") + " Удалить"
        else:
            size = (Window.size[0] / 2.2, self.standardTextHeight)
            text = icon("icon-resize-small-1") + " Уменьшить этаж"
        deleteBtn = Button(text=text, markup=True, size_hint=(None, None),
                           size=size, background_normal="", background_down=self.buttonPressedBG,
                           background_color=self.tableBGColor, color=self.tableColor)
        bin = AnchorLayout(anchor_x="right", anchor_y="center", padding=self.padding)
        deleteBtn.bind(on_press=self.deletePressed)
        bin.add_widget(deleteBtn)
        return bin

    def loadForm(self, form):
        """ Вывод заданной формы """
        if form == "ter" or form == "createNewHouse":
            self.terPressed()
        elif form == "houseView" or form == "createNewPorch" or form == "editHouse" or\
            form == "houseDetails":
            self.houseView()
        elif form == "porchView" or form == "createNewFlat" or form == "editPorch" or\
            form == "porchDetails":
            self.porchView()
        elif form == "flatView" or form == "createNewRecord" or form == "editFlat" or\
            form == "flatDetails":
            self.flatView()
        elif form == "recordView":
            self.recordView()
        elif form == "noteGlobal" or form == "noteForFlat" or form == "noteForPorch" or form == "noteForHouse":
            self.notePressed()
        elif form == "rep":
            self.repPressed()
        elif form == "con":
            self.conPressed()
        elif form == "search":
            self.find()
        else:
            self.terPressed()

    # Функции для контактов

    def retrieve(self, containers, h, p, f, contacts):
        """ Retrieve and append contact list """

        name = containers[h].porches[p].flats[f].getName()
        if containers[h].type == "virtual":
            number = ""
        else:
            number = containers[h].porches[p].flats[f].number

        if len(containers[h].porches[p].flats[f].records) > 0:
            lastRecordDate = containers[h].porches[p].flats[f].records[
                len(containers[h].porches[p].flats[f].records) - 1].date
        else:
            lastRecordDate = ""

        contacts.append([  # create list with one person per line with values:
            name,  # 0 contact name
            containers[h].porches[p].flats[f].getStatus()[0],  # 1 status
            containers[h].title,  # 2 house title
            number,  # 3 flat number
            lastRecordDate,  # 4 last record date
            "",  # не используется
            "",  # не используется
            [h, p, f],  # 7 reference to flat
            containers[h].porches[p].type,  # 8 porch type ("virtual" as key for standalone contacts)
            containers[h].porches[p].flats[f].phone,  # 9 phone number

            # Used only for search function:

            containers[h].porches[p].flats[f].title,  # 10 flat title
            containers[h].porches[p].flats[f].note,  # 11 flat note
            containers[h].porches[p].title,  # 12 porch type
            containers[h].note,  # 13 house note
            "",  # не используется

            # Used for checking house type:

            containers[h].type,  # 15 house type ("virtual" as key for standalone contacts)
            containers[h].porches[p].flats[f].getStatus()[1],  # 16 sortable status ("value")
        ])

        return contacts

    def getContacts(self, forSearch=False):
        """ Returns list of all contacts (house contacts: with records and status other than 0 and 9 """

        contacts = []
        for h in range(len(utils.houses)):
            for p in range(len(utils.houses[h].porches)):
                for f in range(len(utils.houses[h].porches[p].flats)):
                    if forSearch == False:  # поиск для списка контактов - только актуальные жильцы
                        if utils.houses[h].porches[p].flats[f].status != "" and utils.houses[h].porches[p].flats[
                            f].status != "0" \
                                and utils.houses[h].porches[p].flats[f].getName() != "" and not "." in \
                                                                                                utils.houses[h].porches[
                                                                                                    p].flats[f].number:
                            self.retrieve(utils.houses, h, p, f, contacts)
                    else:  # поиск для поиска - все контакты вне зависимости от статуса
                        if not "." in utils.houses[h].porches[p].flats[f].number:
                            self.retrieve(utils.houses, h, p, f, contacts)

        for h in range(len(utils.resources[1])):
            self.retrieve(utils.resources[1], h, 0, 0, contacts)  # отдельные контакты - все

        return contacts

    # Вспомогательные функции

    def changeColor1(self, instance):
        """ Мигание нажатой кнопки с векторной иконкой - нажатое состояние"""
        instance.color = self.titleColor
        instance.background_color = self.tableColor

    def changeColor2(self, instance):
        """ Мигание нажатой кнопки с векторной иконкой - обычное (отжатое) состояние"""
        instance.color = self.topButtonColor
        instance.background_color = self.globalBGColor

    def quickReject(self, instance=None, fromPopup=False):
        """ Быстрая простановка отказа """
        if len(self.flat.records) == 0 and fromPopup == False:
            self.flat.updateName(self.multipleBoxEntries[0].text.strip())
            record = self.multipleBoxEntries[1].text.strip()
        else:
            record = ""
        if utils.settings[0][10] == 1 and record == "":
            record = "отказ"
            self.flat.addRecord(record)
        self.flat.status = "0"
        utils.save()
        self.porchView()

    def colorBtnPressed(self, instance=None):

        color = instance.background_color
        if len(self.flat.records) == 0:
            if self.multipleBoxEntries[0].text.strip() != "":
                self.flat.updateName(self.multipleBoxEntries[0].text.strip())
            if self.multipleBoxEntries[1].text.strip() != "":
                self.flat.addRecord(self.multipleBoxEntries[1].text.strip())
            if int(self.addPlacement.get()) > 0:
                self.rep.modify("б" + self.addPlacement.get())
            if int(self.addVideo.get()) > 0:
                self.rep.modify("в" + self.addVideo.get())
        if color == self.getColorForStatus("0"): # отказ
            self.quickReject()

        for i in ["1", "2", "3", "4", "5"]:
            if color == self.getColorForStatus(i):
                self.flat.status = i
        if self.contactsEntryPoint == 1:
            self.conPressed()
        elif self.searchEntryPoint == 1:
            self.find()
        else:
            self.porchView()
        utils.save()

    def onKeyboardFocus(self, instance, value, k=.5):
        if self.platform == "desktop":
            return
        elif value:
            self.interface.size_hint_y = k
            self.titleBox.size_hint_y = 0
            self.boxHeader.size_hint_y = 0
            self.bottomButtons.size_hint_y = .12
            self.interface.remove_widget(self.boxFooter)
        else:
            self.interface.size_hint_y = 1
            self.boxHeader.size_hint_y = self.marginSizeHintY
            self.titleBox.size_hint_y = self.marginSizeHintY
            self.bottomButtons.size_hint_y = self.marginSizeHintY
            self.interface.add_widget(self.boxFooter)

    def onKeyboardFocusNum(self, instance, value):
        """ То же, что функция выше, только обрабатывает значения с цифровой клавиатуры и передает на onKeyboardFocus"""
        self.onKeyboardFocus(instance, value, k=.65)

    def processConsoleInput(self, instance=None, value=None):
        """ Обработка текста в поисковой строке """

        input = self.searchBar.text.lower().strip()

        if input[0:3] == "res" and utils.ifInt(input[3]) == True: # восстановление резервных копий
            copy = int(input[3])
            print("Восстанавливаю копию %d" % copy)
            success = utils.backupRestore(restoreNumber=copy)
            if success == False:
                self.popup(title="Восстановление данных", message="Не удалось восстановить запрошенную копию с таким номером. Скорее всего, она еще не создана.")
            else:
                self.rep = report.Report()
                self.terPressed()

        elif input == "loadcb":
            utils.load(clipboard=True)

        elif input == "save":
            utils.save(silent=False)

        elif input == "lib":
            utils.settings[0][5] = "lib"
            utils.save()
            self.stop()

        elif input == "green":
            utils.settings[0][5] = "green"
            utils.save()
            self.stop()

        elif input != "":
            self.searchQuery = input
            self.find()

        """elif input == "share":
                    utils.share()

        elif input == "load":
            utils.load(forced=True, datafile="/sdcard/data_backup.jsn")"""

    def getColorForStatus(self, status=99):

        if status == "?":
            color = [.65, .65, .65, 1]#[.21, .21, .21, 1] # светло-серый
        elif status == "0":
            color = [0, 0, .5, 1] # синий
        elif status == "1":
            color = [0, .5, 0, 1] # зеленый
        elif status == "2":
            color = [.86, .71, .08, 1] # желтый
        elif status == "3":
            color = [.42, .04, .5, 1] # фиолетовый
        elif status == "4":
            color = [.6, .4, .08, 1]# [.27, .17, .07, 1] # коричневый
        elif status == "5":
            color = [.7, 0, 0, 1] # красный
        else:
            color = self.scrollButtonBackgroundColor#[.56,.56,.56, 1]
        return color

    def hook_keyboard(self, window, key, *largs):
        if key == 27:
            self.backPressed()
            return True

    def deletePressed(self, instance=None):
        """ Действие при нажатии на кнопку с корзиной на форме любых деталей """
        if self.displayed.form == "houseDetails": # удаление участка
            self.popupForm = "confirmDeleteHouse"
            self.popup(title="Удаление участка: %s" % self.house.title,
                       message="Перед удалением участка его желательно сдать. Удаляем?",
                       options=[self.button["yes"], self.button["no"]])

        elif self.displayed.form == "porchDetails": # удаление подъезда
            self.popupForm = "confirmDeletePorch"
            self.popup(title="Удаление %sа: %s" % (self.porch.type[:7], self.porch.title),
                       message="Точно удалить?",
                       options=[self.button["yes"], self.button["no"]])

        elif self.displayed.form == "flatDetails" or self.displayed.form == "flatView": # удаление квартиры
            self.popupForm = "confirmDeleteFlat"
            if self.contactsEntryPoint == 1 or self.searchEntryPoint == 1 or \
                    (self.flat.status != "" and not "подъезд" in self.porch.type):
                self.popup(title="Удаление: %s" % self.flat.getName(),
                           message="Точно удалить?",
                           options=[self.button["yes"], self.button["no"]])
            else:
                self.popupPressed(instance=Button(text=self.button["yes"]))

        elif self.displayed.form == "recordView": # удаление записи посещения
            self.flat.deleteRecord(self.selectedRecord)
            utils.save()
            self.flatView()

        elif self.displayed.form == "noteForFlat":
            self.flat.note = ""
            utils.save()
            self.flatView()

        elif self.displayed.form == "noteForPorch":
            self.porch.note = ""
            utils.save()
            self.porchView()

        elif self.displayed.form == "noteForHouse":
            self.house.note = ""
            utils.save()
            self.houseView()

        elif self.displayed.form == "noteGlobal":
            utils.resources[0][0] = ""
            utils.save()
            self.terPressed()

    def popupPressed(self, instance=None):
        """ Действия при нажатии на кнопки всплывающего окна self.popup """

        if self.popupForm == "timerType":
            if instance.text == "Служение":
                self.rep.modify(")")
            else:
                self.rep.modify("$")

        elif self.popupForm == "clearData":
            if instance.text == self.button["yes"]:
                utils.clearDB()
                utils.removeFiles()
                self.rep = report.Report()

        elif self.popupForm == "newMonth":
            self.repPressed()
            self.notePressed()

        elif self.popupForm == "confirmDeleteFlat":
            if instance.text == self.button["yes"]:
                if self.house.type == "virtual":
                    del utils.resources[1][self.selectedHouse]
                    if self.contactsEntryPoint == 1:
                        self.conPressed()
                    elif self.searchEntryPoint == 1:
                        self.find()
                elif "подъезд" in self.porch.type:
                    if self.contactsEntryPoint == 0 and self.searchEntryPoint == 0:
                        self.porch.shrinkFloor(self.selectedFlat)
                        self.porchView()
                    else:
                        self.flat.wipe()
                        if self.contactsEntryPoint == 1:
                            self.conPressed()
                        elif self.searchEntryPoint == 1:
                            self.find()
                else:
                    self.porch.deleteFlat(self.selectedFlat)
                    if self.contactsEntryPoint == 1:
                        self.conPressed()
                    elif self.searchEntryPoint == 1:
                        self.find()
                    else:
                        self.porchView()
                utils.save()

        elif self.popupForm == "confirmDeletePorch":
            if instance.text == self.button["yes"]:
                del self.house.porches[self.selectedPorch]
                utils.save()
                self.houseView()

        elif self.popupForm == "confirmDeleteHouse":
            if instance.text == self.button["yes"]:
                interest = []  # считаем все квартиры со статусом 1
                for p in range(len(self.house.porches)):
                    for f in range(len(self.house.porches[p].flats)):
                        if self.house.porches[p].flats[f].status != "" and self.house.porches[p].flats[f].status != "?" \
                                and self.house.porches[p].flats[f].status != "0":
                            interest.append([p, f])
                if len(interest) > 0:
                    for int in interest:
                        flat = self.house.porches[int[0]].flats[int[1]]
                        flat.clone(toStandalone=True, title=self.house.title)
                    #utils.log("Участок %s удален" % utils.houses[self.selectedHouse].title)
                del utils.houses[self.selectedHouse]
                utils.save()
                self.terPressed()

        elif self.popupForm == "Telegram":
            if instance.text == self.button["yes"]:
                webbrowser.open("https://t.me/rocketministry")

        elif self.popupForm == "pioneerNorm":
            if instance.text == self.button["yes"]:
                utils.settings[0][3] = 70
                utils.save()
                self.repPressed()

            """self.popupForm = "Telegram" # при первом заходе сразу после запроса о норме предлагаем подписаться на телеграм
            self.popup(title="Rocket Ministry в Telegram",
                       message="Подписаться на [color=36ACD8]%s[/color] Telegram-канал проекта, чтобы оперативно узнавать об обновлениях и получать техподдержку?" % icon(
                           "icon-telegram"),
                       options=[self.button["yes"], self.button["no"]])"""

        elif instance.text == "Помощь":
            webbrowser.open("https://github.com/antorix/Rocket-Ministry/wiki")

        elif self.popupForm == "restart":
            if instance.text == self.button["yes"]:
                self.stop()

        self.popupForm = ""

    def popup(self, message="", options=[], title="Внимание", firstCall=False):
        """Информационное окно с возможностью подтверждения выбора"""

        if firstCall == True: # специальный попап для первого посещения
            self.popupForm = "firstCall"
            title = self.flat.number
            size_hint = (1, .3)#(.6, .4)
            contentMain = BoxLayout(orientation="vertical", size_hint=(1, 1))
            details = Button(text=icon("icon-edit-1"), size_hint=(None, None), background_down=self.buttonPressedBG,
                             size=(self.standardTextHeight, self.standardTextHeight),
                             background_color=self.popupBackgroundColor, background_normal="",
                             pos_hint={"right": 1}, markup=True)
            def __details(instance):
                self.popupEntryPoint = 1
                self.flatView()
                self.detailsPressed()
            details.bind(on_press=__details)
            contentMain.add_widget(details)
            content = GridLayout(rows=1, cols=2, size_hint=(1, 1), spacing=self.spacing*2)
            firstCallBtnReject = Button(text=icon("icon-block-1")+" [b]Отказ[/b]", markup=True, halign="center",
                                        background_normal="", background_down=self.buttonPressedBG,
                                        background_color=self.getColorForStatus("0"))
            def __quickReject(instance):
                self.quickReject(fromPopup=True)
            firstCallBtnReject.bind(on_press=__quickReject)
            content.add_widget(firstCallBtnReject)
            if utils.settings[0][13] == 1:  # Добавляем кнопку нет дома
                content.cols += 1
                firstCallNotAtHome = Button(text=icon("icon-lock-1")+" [b]Нет дома[/b]", markup=True,
                                            background_down=self.buttonPressedBG,
                                            background_normal="", background_color=self.getColorForStatus("?"))
                def __quickNotAtHome(instance):
                    self.flat.addRecord("нет дома")
                    utils.save()
                    self.porchView()
                firstCallNotAtHome.bind(on_press=__quickNotAtHome)
                content.add_widget(firstCallNotAtHome)
            firstCallBtnCall = Button(text=icon("icon-smile")+" [b]Интерес[/b]", markup=True, background_down=self.buttonPressedBG,
                                      background_normal="", background_color=self.getColorForStatus("1"))
            def __firstCall(instance=None):
                self.flatView(call=True)
            firstCallBtnCall.bind(on_press=__firstCall)
            content.add_widget(firstCallBtnCall)
            contentMain.add_widget(content)
            if utils.settings[0][20] == 1:
                #size_hint = (.9, .4)
                self.quickPhone = TextInput(size_hint=(1, None), height=self.standardTextHeight, multiline=False,
                                            input_type="text")
                contentMain.add_widget(self.quickPhone)
                self.quickPhone.hint_text = "Телефон"
                def __getPhone(instance):
                    self.flat.editPhone(self.quickPhone.text.strip())
                    utils.save()
                    self.quickPhone.hint_text = "Телефон сохранен!"
                    self.quickPhone.text = ""
                    self.porchView()
                self.quickPhone.bind(on_text_validate=__getPhone)
                self.quickPhone.bind(focus=self.onKeyboardFocus)

        elif self.popupForm == "search": # поиск
            size_hint = (1, .15)
            self.searchBar = SearchBar()
            self.searchBar.bind(on_text_validate=self.processConsoleInput)
            contentMain = self.searchBar

        else:
            size_hint = (.9, .3)
            text_size = (Window.size[0] * 0.85, Window.size[1] * 0.25)
            contentMain = BoxLayout(orientation="vertical", size_hint=(1, 1))
            contentMain.add_widget(Label(text=message, halign="left", valign="center", text_size=text_size, markup=True))
            if len(options)>0:
                grid = GridLayout(rows=1, cols=1, size_hint=(1, 1))
                self.confirmButtonPositive = Button(text=options[0], markup=True, size_hint_y=None,
                                                    height=self.standardTextHeight)
                self.confirmButtonPositive.bind(on_press=self.popupPressed)
                grid.add_widget(self.confirmButtonPositive)
                if len(options) > 1:
                    grid.cols=3
                    grid.add_widget(Widget())
                    self.confirmButtonNegative = Button(text=options[1], markup=True, size_hint_y=None, height=self.standardTextHeight)
                    self.confirmButtonNegative.bind(on_press=self.popupPressed)
                    grid.add_widget(self.confirmButtonNegative)
                contentMain.add_widget(grid)

        self.mypopup = Popup(title=title, content=contentMain, size_hint=size_hint)#, width=width, height=height, auto_dismiss=True)

        if firstCall == True:
            firstCallBtnReject.bind(on_press=self.mypopup.dismiss)
            if utils.settings[0][13] == 1:
                firstCallNotAtHome.bind(on_press=self.mypopup.dismiss)
            if utils.settings[0][20] == 1:
                self.quickPhone.bind(on_text_validate=self.mypopup.dismiss)
            firstCallBtnCall.bind(on_press=self.mypopup.dismiss)
            details.bind(on_press=self.mypopup.dismiss)
        elif self.popupForm == "search":
            self.searchBar.bind(on_text_validate=self.mypopup.dismiss)
            self.popupForm = ""

        try:
            self.confirmButtonPositive.bind(on_press=self.mypopup.dismiss)
            self.confirmButtonNegative.bind(on_press=self.mypopup.dismiss)
        except:
            pass

        self.mypopup.open()

    def onFirstRun(self):
        """ Срабатывает при первом запуске программы, определяется по отсутствию даты обновления, вызывается из utils.update() """

        self.popupForm = "pioneerNorm"
        self.popup(title="Rocket Ministry",
                   message="Вы общий пионер? Тогда мы пропишем месячную норму часов. Ее можно ввести самостоятельно в настройках.",
                   options=[self.button["yes"], self.button["no"]])

        utils.settings[1] = 1
        self.firstRunFlag = False
        utils.save()

    def onStartup(self):

        utils.backupRestore(delete=True, silent=True)

        print("Определяем начало нового месяца.")
        self.rep.checkNewMonth()

        limit = 200
        print("Оптимизируем размер журнала отчета.")
        if len(utils.resources[2]) > limit:
            extra = len(utils.resources[2]) - limit
            for i in range(extra):
                del utils.resources[2][len(utils.resources[2]) - 1]

        utils.update()

    def transitionTo20(self):
        """ Временная функция для адаптации настроек при переходе с 1.0, убрать через несколько месяцев """

        utils.settings[0][6] = 10 # установка кол-ва резервных копий фиксированно в 10
        if len(utils.resources[0]) == 0: # конвертация блокнота в глобальную заметку
            utils.resources[0].append("")
        else:
            temp = ""
            for note in utils.resources[0]:
                temp += note + "\n"
            del utils.resources[0][:]
            utils.resources[0].append(temp)
            utils.save()

    def importDB(self, instance=None, wordFile=None):
        """ Импорт данных из буфера обмена либо Word-файла"""
        if wordFile == None:
            clipboard = Clipboard.paste()
        else:
            try:
                clipboard = docx2txt.process(wordFile) # имитация буфера обмена, но с Word-файлом
            except:
                self.popup("Не удалось загрузить Word-файл. Скорее всего, файл ошибочного формата или не содержит нужных данных.")
                return
        success = utils.load(clipboard=clipboard)
        if success == True:
            self.transitionTo20()
            self.popup("Данные успешно загружены в программу!")
            self.rep = report.Report()
            utils.save()
