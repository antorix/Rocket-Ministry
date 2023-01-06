#!/usr/bin/python
# -*- coding: utf-8 -*-

import utils
import house
import report
import time
#import buffer
import webbrowser
import iconfonts
from iconfonts import icon
import plyer

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
#from kivy.uix.scatterlayout import ScatterLayout
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
#from kivy.config import Config
#from kivy.lang import Builder
#from kivy.uix.bubble import Bubble, BubbleButton
from kivy import platform
from kivy.clock import Clock
from kivy.uix.slider import Slider
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.modalview import ModalView

if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.CALL_PHONE, Permission.INTERNET, "com.google.android.gms.permission.AD_ID"])
                         #Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])


    #<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />

    #, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

    # Кроме того, при обновлении целевой версии ОС до Android 13 или более поздней потребуется указывать в манифесте
    # приложения обычное разрешение для сервисов Google Play следующим образом:

    # <uses-permission android:name="com.google.android.gms.permission.AD_ID"/>

    import kvdroid
    from kvdroid import activity
    from kvdroid.jclass.android import Rect
    from jnius import autoclass
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    String = autoclass('java.lang.String')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    mActivity = PythonActivity.mActivity

else:
    try:
        import docx2txt
    except:
        from subprocess import check_call
        from sys import executable
        check_call([executable, '-m', 'pip', 'install', 'docx2txt'])
        check_call([executable, '-m', 'pip', 'install', 'plyer'])
        import docx2txt

#Builder.load_file('rm.kv')

class Feed(object):
    def __init__(self, message="", title="", form="", options=[], sort=None, details=None, note=None,
                 positive="", neutral="", negative="", back=True):
        self.message = message
        self.title = title
        self.form = form
        self.options = options
        self.positive = positive
        self.neutral = neutral
        self.negative = negative
        self.sort = sort
        self.details = details
        self.note = note
        self.back = back

class MyTextInput(TextInput):
    def __init__(self, multiline=False, size_hint_y=1, size_hint_x=1, hint_text="", pos_hint = {"center_y": .5},
                 text="", disabled=False, input_type="text", width=0, height=0, mode="resize", shrink=True,
                 popup=False, focus=False, *args, **kwargs):
        super(MyTextInput, self).__init__()
        self.multiline = multiline
        self.size_hint_x = size_hint_x
        self.size_hint_y = size_hint_y
        self.pos_hint = pos_hint
        self.height = height
        self.width = width
        self.input_type = input_type
        self.text = text
        self.disabled = disabled
        self.hint_text = hint_text
        self.foreground_color = RM.standardTextColor
        self.background_normal = ""
        self.background_color = RM.textInputBGColor
        self.cursor_color = RM.titleColor
        self.cursor_color[3] = .5
        self.mode = mode
        self.shrink = shrink
        self.popup = popup
        self.focus = focus
        self.write_tab = False

    def on_text_validate(self):
        if self.popup == False:
            RM.positivePressed()

    def on_focus(self, instance=None, value=None):
        if platform == "android":
            self.keyboard_mode="managed"
            Window.softinput_mode = self.mode
        elif RM.platform == "desktop" and RM.devmode == 0:
            return

        if value:  # вызов клавиатуры
            if RM.model == "huawei":
                # решаем проблему с клавиатурным глюком только на устройствах huawei взамен на хаотичное открывание клавиатуры
                Clock.schedule_once(self.create_keyboard, .1)
            else:
                self.create_keyboard()

            if self.shrink == False or self.mode == "pan":
                return
            else:
                def __getHeight(*args):
                    RM.interface.size_hint_y = None
                    RM.interface.height = Window.height - RM.keyboardHeight() - 10
                    RM.interface.remove_widget(RM.boxFooter)
                    RM.bottomButtons.size_hint_y = RM.marginSizeHintY * 2.5
                    RM.boxHeader.size_hint_y = 0
                    RM.titleBox.size_hint_y = 0
                    if RM.reportBoxesAL in RM.mainList.children and RM.displayed.form != "flatView":
                        RM.reportBoxesAL.anchor_y = "bottom"
                Clock.schedule_once(__getHeight, 0.2)
                #Window.bind(on_key_down=__getHeight)

        else:
            self.hide_keyboard()
            self.keyboard_mode = "auto"
            RM.bottomButtons.size_hint_y = RM.marginSizeHintY
            RM.boxHeader.size_hint_y = RM.marginSizeHintY
            RM.titleBox.size_hint_y = RM.marginSizeHintY
            RM.interface.size_hint_y = 1
            if RM.reportBoxesAL in RM.mainList.children:
                RM.reportBoxesAL.anchor_y = "center"
            if RM.boxFooter not in RM.interface.children:
                RM.interface.add_widget(RM.boxFooter)

    def create_keyboard(self, *args):
        self.show_keyboard()

    def remove_focus_decorator(function):
        def wrapper(self, touch):
            if not self.collide_point(*touch.pos):
                self.focus = False
            function(self, touch)
        return wrapper

    @remove_focus_decorator
    def on_touch_down(self, touch):
        super().on_touch_down(touch)

class SearchBar(MyTextInput):
    def __init__(self):
        super(SearchBar, self).__init__()
        self.multiline=False
        self.size_hint=(1, None)
        self.pos_hint={"center_y": .5}
        self.height=RM.standardTextHeight*1.1
        self.hint_text="Введите запрос"
        self.input_type = "text"
        self.popup = True
        self.shrink = False
        self.focus = True

    def on_text_validate(self):
        RM.processConsoleInput(instance=self)

    def on_focus(self, instance=None, value=None):
        if value == False:
            RM.mypopup.dismiss()

class TTab(TabbedPanelHeader):
    """ Вкладки панелей """
    def __init__(self, text=""):
        super(TTab, self).__init__()
        self.background_normal = "void.png"
        if RM.theme == "dark":
            self.color = "white"
        else:
            self.color = RM.themeDefault[1]
        self.text = text

        if RM.theme == "purple":
            self.background_down = "tab_background_purple.png"
        else:
            self.background_down = "tab_background_blue.png"

    def on_press(self):
        RM.buttonFlash(instance=self)

class TopButton(Button):
    """ Кнопки поиска и настроек"""
    def __init__(self, text=""):
        super(TopButton, self).__init__()
        self.text = text
        self.font_size = RM.fontXXL*.85
        self.markup=True
        self.size_hint = (1, None)
        self.pos_hint = {"center_y": .5}
        self.color = RM.topButtonColor
        self.background_color = RM.globalBGColor
        self.background_normal = ""
        if RM.theme == "dark":
            self.background_down = ""
        else:
            self.background_down = RM.buttonPressedBG

    def on_press(self):
        RM.buttonFlash(instance=self)
        if RM.theme == "dark" and self.background_color != RM.tableBGColor:
            self.background_color = RM.buttonPressedOnDark
            Clock.schedule_once(self.restoreBlackBG, RM.onClickFlash)

    def restoreBlackBG(self, *args):
        self.background_color = "black"

class TableButton(Button):
    def __init__(self, text="", size_hint_x=1, size_hint_y=1, height=0, width=0, background_color=None, color=None,
                 pos_hint=None, size=None, **kwargs):
        super(TableButton, self).__init__()
        self.text = text.strip()
        self.markup = True
        self.size_hint_x = size_hint_x
        self.size_hint_y = size_hint_y
        self.height = height
        self.width = width
        if size != None:
            self.size = size
        if pos_hint != None:
            self.pos_hint = pos_hint
        else:
            self.pos_hint = {"center_y": .5}
        if color != None:
            self.color = color
        elif RM.theme == "teal" and background_color == None:
            self.color = RM.themeTeal[1]
        elif RM.theme == "teal":
            self.color = RM.themeDefault[1]
        else:
            self.color = RM.tableColor
        if background_color == None:
            self.background_color = RM.tableBGColor
        else:
            self.background_color = background_color
        self.background_normal = ""
        self.background_disabled_normal = ""
        if RM.theme == "dark" and self.background_color == "black":
            self.background_down = ""
        else:
            self.background_down = RM.buttonPressedBG

    def on_press(self):
        RM.buttonFlash(instance=self)
        if RM.theme == "dark" and self.background_color != RM.tableBGColor:
            self.background_color = RM.buttonPressedOnDark
            Clock.schedule_once(self.restoreBlackBG, RM.onClickFlash)

    def restoreBlackBG(self, *args):
        self.background_color = "black"

class TButton(Button):
    """ Кнопки удаления и уменьшения этажа, в разделе данных и отправка отчета"""
    def __init__(self, text="", size_hint_x=1, size_hint_y=1, halign="center", background_color=None, color=None,
                 markup=True, height=0, **kwargs):
        super(TButton, self).__init__()
        self.background_normal = ""
        self.background_down = RM.buttonPressedBG
        if background_color == None:
            self.background_color = RM.tableBGColor
        else:
            self.background_color = background_color
        if color != None:
            self.color = color
        elif RM.theme == "teal" and background_color == None:
            self.color = RM.themeTeal[1]
        elif RM.theme == "teal":
            self.color = RM.themeDefault[1]
        else:
            self.color = RM.tableColor
        self.markup = markup
        self.text = text
        self.size_hint_x = size_hint_x
        self.size_hint_y = size_hint_y
        self.width = RM.standardTextWidth
        self.height = height
        self.halign = halign

    def on_press(self):
        RM.buttonFlash(instance=self)

class RButton(Button):
    def __init__(self, text="", size_hint_x=1, size_hint_y=1, height=0, text_size=(None, None), halign="center",
                 valign="center", size=Window.size, background_normal="", color="", background_color="",
                 markup=True, background_down="", radius=[12], black=False, quickFlash=False, **kwargs):
        super(RButton, self).__init__()
        if RM.platform == "desktop":
            self.radius = [radius[0]/2] # поменьше скругление на ПК
        else:
            self.radius = radius
        self.background_normal = background_normal
        self.background_down = background_down
        if background_color == "":
            self.background_color = RM.tableBGColor
        else:
            self.background_color = background_color
        if color == "":
            self.origColor = RM.tableColor
        else:
            self.origColor = color
        self.color = self.origColor
        self.markup = markup
        self.text = text
        self.size_hint_x = size_hint_x
        self.size_hint_y = size_hint_y
        self.height = height
        self.size = size
        self.halign = halign
        self.valign = valign
        self.text_size = text_size
        if quickFlash == True:
            self.k = .5
        else:
            self.k = 1

        if black==True:
            self.size_hint = (1, None)
            self.background_color = RM.themeDark[0]
            self.color = self.origColor = "white"
            self.height = RM.standardTextHeight

        self.background_color[3] = 0

        with self.canvas.before:
            self.shape_color = Color(rgba=[self.background_color[0], self.background_color[1],
                                           self.background_color[2], 1])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def on_press(self, *args):
        with self.canvas.before:
            self.shape_color = Color(rgba=[self.background_color[0]*RM.onClickColK,
                                           self.background_color[1]*RM.onClickColK,
                                           self.background_color[2]*RM.onClickColK, 1])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            self.bind(pos=self.update_shape, size=self.update_shape)
        self.color = RM.titleColor
        Clock.schedule_once(self.restoreColor, RM.onClickFlash * self.k)

    def restoreColor(self, *args):
        with self.canvas.before:
            self.shape_color = Color(rgba=[self.background_color[0], self.background_color[1],
                                           self.background_color[2], 1])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            self.bind(pos=self.update_shape, size=self.update_shape)
        self.color = self.origColor

class PopupNoAnimation(Popup):
    """ Попап, в котором отключена анимация при закрытии"""
    def __init__(self, **kwargs):
        super(PopupNoAnimation, self).__init__(**kwargs)

    def dismiss(self, *largs, **kwargs):
        if self._window is None:
            return
        if self.dispatch('on_dismiss') is True:
            if kwargs.get('force', False) is not True:
                return
        self._anim_alpha = 0
        self._real_remove_widget()

class SortListButton(Button):
    def __init__(self, text):
        super(SortListButton, self).__init__()
        self.text = text
        self.size_hint_y = None
        self.height = RM.standardTextHeight
        self.background_color = RM.tableBGColor
        self.background_normal = ""
        self.background_down = RM.buttonPressedBG
        self.color = RM.tableColor

    def on_press(self):
        RM.buttonFlash(instance=self)
        Clock.schedule_once(self.restoreColor, RM.onClickFlash)

    def restoreColor(self, *args):
        self.background_color = RM.tableBGColor

class ScrollButton(Button):
    # Все пункты списка, кроме квадратиков квартир в поэтажном режиме
    def __init__(self, text="", height=0, valign="center", color="", background_color=""):
        super(ScrollButton, self).__init__()
        self.size_hint_y = 1
        self.height = height
        self.halign = "center"
        self.valign = valign
        self.text_size = (Window.size[0]*.95, height)
        self.background_normal = ""
        if RM.theme == "teal" and background_color == None:
            self.originalColor = RM.themeTeal[1]
        elif RM.theme == "teal":
            self.originalColor = RM.themeDefault[1]
        else:
            self.originalColor = RM.tableColor
        self.color = self.originalColor

        if background_color == "":
            self.background_color = RM.globalBGColor
        else:
            self.background_color = background_color

        if RM.theme == "dark":
            self.background_down = ""
        else:
            self.background_down = RM.buttonPressedBG

        self.markup = True
        self.text = text

    def on_press(self):
        if RM.theme == "dark":
            self.background_color = [RM.buttonPressedOnDark[0]/2, RM.buttonPressedOnDark[1]/2, RM.buttonPressedOnDark[2]/2]
            Clock.schedule_once(self.restoreBlackBG, RM.onClickFlash)

    def restoreBlackBG(self, *args):
        self.background_color = "black"

    def on_release(self):
        RM.clickOnList(instance=self)

class FlatButton(Button):
    """ Кнопка квартиры """
    def __init__(self, text="", status="", size_hint_x=1, size_hint_y=1, width=0, height=0, pos_hint={"top": 0},
                 radius=[10], **kwargs):
        super(FlatButton, self).__init__()
        if RM.platform == "desktop":
            self.radius = [radius[0]/2] # поменьше скругление на ПК
        else:
            self.radius = radius
        self.text = text
        self.background_color = RM.getColorForStatus(status)
        self.background_color[3] = 0
        self.background_normal = ""
        self.markup = True
        self.halign = "center"
        self.valign = "middle"
        self.pos_hint = pos_hint
        self.color = RM.standardScrollColor
        self.text_size = (Window.size[0]*.95, height)
        self.size_hint_x = size_hint_x
        self.size_hint_y = size_hint_y
        self.origWidth = width
        self.origHeight = height
        self.width = self.origWidth
        self.height = self.origHeight
        self.background_down = RM.buttonPressedBG

        with self.canvas.before:
            self.shape_color = Color(rgba=[self.background_color[0],
                                           self.background_color[1],
                                           self.background_color[2], 1])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def on_press(self):
        with self.canvas.before:
            self.shape_color = Color(rgba=[self.background_color[0]*RM.onClickColK,
                                           self.background_color[1]*RM.onClickColK,
                                           self.background_color[2]*RM.onClickColK, 1])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            self.bind(pos=self.update_shape, size=self.update_shape)
        Clock.schedule_once(self.restoreColor, RM.onClickFlash)

    def restoreColor(self, *args):
        with self.canvas.before:
            self.shape_color = Color(rgba=[self.background_color[0],
                                           self.background_color[1],
                                           self.background_color[2], 1])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            self.bind(pos=self.update_shape, size=self.update_shape)

    def on_release(self):
        RM.clickOnList(instance=self)

class CounterButton(Button):
    def __init__(self, mode):
        super(CounterButton, self).__init__()
        self.mode = mode
        if mode == "plus":
            self.text = icon("icon-plus-circled-1")
        elif mode == "minus":
            self.text = icon("icon-minus-circled-1")
        else:
            self.text = icon("icon-clock-1")
        self.markup = True
        self.size_hint_x = None
        self.font_size = RM.fontL
        self.pos_hint = {"center_y": .5}
        if RM.theme == "dark":
            self.color = "black"
        elif RM.theme == "teal":
            self.color = RM.themeDefault[1]
        else:
            self.color = RM.mainMenuButtonColor
        self.background_color = RM.topButtonColor
        self.background_normal = ""
        self.background_down = RM.buttonPressedBG
        self.size = (RM.counterHeight/2, RM.standardTextHeight)

    def on_release(self):
        if self.text == icon("icon-clock-1"):
            RM.popupForm = "showTimePicker"
            RM.popup(title=self.mode)
        else:
            RM.counterChanged = True

class Counter(AnchorLayout):
    def __init__(self, type="int", text="0", size_hint=(1, 1), fixed=False, disabled=False, shrink=True, picker=None,
                 mode="resize", focus=False):
        super(Counter, self).__init__()
        self.anchor_x = "center"
        self.anchor_y = "center"

        box = BoxLayout(size_hint=size_hint)

        self.input = MyTextInput(text=text, focus=focus, disabled=disabled, multiline=False,
                            pos_hint={"center_y": .5}, input_type="number", shrink=shrink, mode=mode)

        def __changed(instance, value):
            RM.counterChanged = True
            if utils.ifInt(self.input.text) == True and int(self.input.text) < 0:
                self.input.text = "0"
            else:
                try:
                    if self.input.text[0] == "-":
                        self.input.text = self.input.text[1:]
                except:
                    pass#self.input.text = "0"
        self.input.bind(focus=__changed)

        if fixed != False: # можно задать фиксированную высоту счетчика
            box.size_hint = (None, None)
            box.height = RM.counterHeight
            if RM.orientation == "h":
                box.height *= .7
            box.width = RM.counterHeight*1.3
            self.input.size_hint_x = None
            self.input.width = RM.counterHeight*.8

        box.add_widget(self.input)

        box2 = BoxLayout(orientation="vertical", spacing=RM.spacing)

        if picker == None: # обычный счетчик с кнопками + и -

            aUp = AnchorLayout(anchor_x="left", anchor_y="top")
            btnUp = CounterButton("plus")  # кнопка вверх
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
            btnUp.bind(on_release=__countUp)
            aUp.add_widget(btnUp)

            aDown = AnchorLayout(anchor_x="left", anchor_y="bottom")
            btnDown = CounterButton("minus") # кнопка вниз
            def __countDown(instance=None):
                try:
                    if type != "time":
                        if int(self.input.text) > 0:
                            self.input.text = str(int(self.input.text) - 1)
                    else:
                        hours = self.input.text[: self.input.text.index(":")]
                        minutes = self.input.text[self.input.text.index(":") + 1:]
                        self.input.text = "%d:%s" % (int(hours) - 1, minutes)
                except:
                    pass
            btnDown.bind(on_release=__countDown)
            aDown.add_widget(btnDown)
            box2.add_widget(aUp)
            box2.add_widget(aDown)

        else: # счетчик для времени с пикером

            box2.add_widget(CounterButton(picker))

        box.add_widget(box2)
        self.add_widget(box)

    def get(self):
        return self.input.text
        if not ":" in self.input.text and utils.ifInt(self.input.text) == True:
            return self.input.text
        elif ":" in self.input.text:
            return self.input.text
        else:
            return "0"

    def update(self, update):
        self.input.text = update

    def flash(self):
        self.input.background_color = RM.reportFlashColor
        def __removeFlash(instance):
            self.input.background_color = "white"
            unflash.cancel()
        unflash = Clock.schedule_interval(__removeFlash, 0.5)

class Timer(Button):
    def __init__(self):
        super(Timer, self).__init__()
        self.pos_hint = {"center_y": .5}
        self.font_size = RM.fontXXL*2
        self.markup = True
        self.halign = "left"
        self.background_color = RM.globalBGColor
        self.background_normal = ""
        self.size_hint = (None, None)
        self.width = RM.standardTextHeight*1.5
        self.originalColor = self.color
        if RM.theme == "dark":
            self.background_down = ""
        else:
            self.background_down = RM.buttonPressedBG

    def on_press(self):
        self.font_size = RM.fontXXL*1.9
        Clock.schedule_once(self.step1, RM.onClickFlash/2.3)
        if RM.theme == "dark" and self.background_color != RM.tableBGColor:
            self.background_color = RM.buttonPressedOnDark
            Clock.schedule_once(self.restoreBlackBG, RM.onClickFlash)

    def restoreBlackBG(self, *args):
        self.background_color = "black"

    def step1(self, *args):
        self.font_size = RM.fontXXL*1.8
        Clock.schedule_once(self.step2, RM.onClickFlash/2.3)

    def step2(self, *args):
        self.font_size = RM.fontXXL*2

    def on_release(self):
        RM.timerPressed()

    def on(self):
        """ Включение таймера """
        self.text = icon("icon-stop-circle")
        self.color = RM.getColorForStatus("5")# "crimson"

    def off(self):
        """ Выключение таймера """
        self.text = icon("icon-play-circled-1")
        self.color = RM.getColorForStatus("1") #"limegreen"

class ColorStatusButton(Button):
    def __init__(self, status="", text=""):
        super(ColorStatusButton, self).__init__()
        self.size_hint_max_y = .5
        self.side = (RM.mainList.size[0] - RM.padding*2 - RM.spacing*25.5) / 6
        self.size_hint = (None, None)
        if RM.orientation == "v":
            self.height = self.side
        else:
            self.height = RM.standardTextHeight
        self.width = self.side
        self.text = text
        self.status = status
        self.markup = True
        self.background_normal = ""
        self.background_color = RM.getColorForStatus(self.status)
        self.background_color[3] = 0

        with self.canvas.before:
            self.shape_color = Color(rgba=[RM.getColorForStatus(self.status)[0], RM.getColorForStatus(self.status)[1],
                                           RM.getColorForStatus(self.status)[2], 1])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
            self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def on_press(self, *args):
        for button in RM.colorBtn:
            button.text = ""
        self.text = icon("icon-dot-circled")
        with self.canvas.before:
            self.shape_color = Color(rgba=[RM.getColorForStatus(self.status)[0]*RM.onClickColK,
                                           RM.getColorForStatus(self.status)[1]*RM.onClickColK,
                                           RM.getColorForStatus(self.status)[2]*RM.onClickColK, 1])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
            self.bind(pos=self.update_shape, size=self.update_shape)
        Clock.schedule_once(self.restoreColor, RM.onClickFlash/2)

    def restoreColor(self, *args):
        with self.canvas.before:
            self.shape_color = Color(rgba=[RM.getColorForStatus(self.status)[0], RM.getColorForStatus(self.status)[1],
                                           RM.getColorForStatus(self.status)[2], 1])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
            self.bind(pos=self.update_shape, size=self.update_shape)

    def on_release(self, instance=None):
        RM.colorBtnPressed(color=self.status)

class MainMenuButton(Button):
    def __init__(self, text):
        super(MainMenuButton, self).__init__()
        self.markup = True
        self.height = 0
        terNormal  = icon("icon-building") + "\nУчастки"
        terPressed = icon("icon-building-filled") + "\nУчастки"
        conNormal  = icon ("icon-address-book-o") + "\nКонтакты"
        conPressed = icon ("icon-address-book-1") + "\nКонтакты"
        repNormal  = icon("icon-doc-text") + "\nОтчет"
        repPressed = icon("icon-doc-text-inv") + "\nОтчет"
        self.background_down = RM.buttonPressedBG
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
        if RM.platform == "mobile":
            self.font_size = RM.fontL*.8
        else:
            self.font_size = RM.fontL * 1.1
        self.background_color = RM.tableBGColor
        self.background_normal = ""
        self.color = RM.mainMenuButtonColor
        def __change1(instance):
            if self.text == terNormal:
                self.text = terPressed
            elif self.text == conNormal:
                self.text = conPressed
            elif self.text == repNormal:
                self.text = repPressed
        def __change2(instance):
            if self.text == terPressed:
                self.text = terNormal
            elif self.text == conPressed:
                self.text = conNormal
            elif self.text == repPressed:
                self.text = repNormal

    def on_press(self):
        RM.buttonFlash(instance=self)

    def activate(self):
        return

    def deactivate(self):
        return

class RejectColorSelectButton(BoxLayout):
    def __init__(self):
        if utils.settings[0][18] == "4":
            text1 = icon("icon-dot-circled")
            text2 = ""
            text3 = ""
        elif utils.settings[0][18] == "5":
            text1 = ""
            text2 = ""
            text3 = icon("icon-dot-circled")
        else:
            text1 = ""
            text2 = icon("icon-dot-circled")
            text3 = ""

        super(RejectColorSelectButton, self).__init__()
        self.b1 = RButton(text=text1, markup=True, background_color=RM.getColorForStatus("4"), background_normal="",
                    color="white", background_down = RM.buttonPressedBG)
        self.b2 = RButton(text=text2, markup=True, background_color=RM.getColorForStatus("0"), background_normal="",
                    color = "white", background_down = RM.buttonPressedBG)
        self.b3 = RButton(text=text3, markup=True, background_color=RM.getColorForStatus("5"), background_normal="",
                    color = "white", background_down = RM.buttonPressedBG)
        self.b1.bind(on_press=self.change)
        self.b2.bind(on_press=self.change)
        self.b3.bind(on_press=self.change)
        self.spacing = RM.spacing
        self.padding = (0, RM.padding*3)
        self.add_widget(self.b1)
        self.add_widget(self.b2)
        self.add_widget(self.b3)

    def change(self, instance):
        self.b1.text = ""
        self.b2.text = ""
        self.b3.text = ""
        instance.text = icon("icon-dot-circled")

    def get(self):
        if self.b1.text == icon("icon-dot-circled"):
            return "4"
        elif self.b2.text == icon("icon-dot-circled"):
            return "0"
        else:
            return "5"

class RMApp(App):
    """ Главный класс приложения """

    def build(self):
        self.firstRunFlag = True
        utils.load()
        self.setParameters()
        self.setTheme()
        self.createInterface()
        self.terPressed()
        Clock.schedule_interval(self.updateTimer, 1)
        if self.devmode == 0:
            self.onStartup()
        return self.globalAnchor

    # Подготовка переменных

    def setParameters(self):
        if platform != "win" and platform != "linux":
            self.platform = "mobile"
        else:
            self.platform = "desktop"
        self.rep = report.Report()
        iconfonts.register('default_font', 'fontello.ttf', 'fontello.fontd')
        self.contactsEntryPoint = self.searchEntryPoint = self.popupEntryPoint = 0
        self.porch = house.House().Porch()
        self.stack = []
        self.showSlider = False
        self.devmode = utils.Devmode
        self.restore = 0
        self.button = {
            "save":     str(icon("icon-floppy") + " Сохранить"),
            "cancel":   "Отмена", # str(icon("icon-left-big")
            "exit":     "Выход", # str(icon("icon-left-big") +
            "ok":       str(icon("icon-ok-1") + " OK"),
            "change":   str(icon("icon-pencil-squared") + " Изменить"),
            "details":  icon("icon-pencil-1"),
            "yes":      "Да",
            "no":       "Нет"
        }

        Window.fullscreen = False
        self.spacing = Window.size[1]/400
        self.padding = Window.size[1]/300
        self.porchPos = [0, 0] # положение сетки подъезда без масштабирования
        self.standardTextHeight = self.standardBarWidth = Window.size[1] * .04 #90
        self.standardTextWidth = self.standardTextHeight * 1.3
        self.marginSizeHintY = 0.08
        self.counterHeight = self.standardTextHeight * 2.5 # размер счетчика в фиксированном состоянии
        self.onClickColK = .7 # коэффициент затемнения фона кнопки при клике
        self.onClickFlash = .08 # время появления теневого эффекта на кнопках
        self.mypopup = PopupNoAnimation()
        self.buttonPressedBG = "button_background.png"
        self.defaultKeyboardHeight = Window.size[1]*.4
        self.fontXXL =  Window.size[1] / 30
        self.fontXL =   Window.size[1] / 35
        self.fontL =    Window.size[1] / 40
        self.fontM =    Window.size[1] / 45
        self.fontS =    Window.size[1] / 50
        self.fontXS =   Window.size[1] / 55
        self.fontXXS =  Window.size[1] / 60
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

        if self.platform == "desktop":
            self.model = "pc"
            self.title = 'Rocket Ministry'
            Window.icon = "icon.png"
            self.icon = "icon.png"
            try: # сначала смотрим положение и размер окна в файле win.ini, если он есть
                with open("win.ini", mode="r") as file:
                    lines = file.readlines()
                Window.size = ( int(lines[0]), int(lines[1]) )
                Window.top = int(lines[2])
                Window.left = int(lines[3])
            except:
                pass

            def __dropFile(*args):
                self.importDB(wordFile=args[1].decode())
                self.terPressed()
            Window.bind(on_drop_file=__dropFile)
            def __close(*args):
                print("Выход из программы.")
                utils.save(export=True)
                self.checkOrientation(width=args[0].size[0], height=args[0].size[1])
            Window.bind(on_request_close=__close)
            Window.bind(on_resize=self.checkOrientation)

        elif platform == "android":
            plyer.orientation.set_portrait()
            from kvdroid.tools.deviceinfo import device_info
            self.model = device_info("manufacturer").lower()

        else:
            plyer.orientation.set_portrait()
            self.model = "unknown"

    # Создание интерфейса

    def createInterface(self):
        """ Создание основных элементов """

        self.globalAnchor = AnchorLayout(anchor_x="center", anchor_y="top")
        self.interface = BoxLayout(orientation="vertical")
        self.boxHeader = BoxLayout(size_hint_y=self.marginSizeHintY, spacing=self.spacing, padding=self.padding)

        # Таймер

        self.timerBox = BoxLayout(size_hint=(0.33, 1), spacing=self.spacing, padding=(self.padding, 0))
        self.timer = Timer()
        self.timerBox.add_widget(self.timer)
        self.timerText = Label(halign="left", valign="center", font_size=self.fontXL,
                               color=self.topButtonColor, width=self.standardTextWidth,
                               markup=True, size_hint=(None, None), pos_hint={"center_y": .5})
        self.timerBox.add_widget(self.timerText)
        self.boxHeader.add_widget(self.timerBox)

        # Заголовок таблицы

        self.headBox = BoxLayout()#size_hint_min_y=self.marginSizeHintY)
        self.pageTitle = Label(text="Заголовок страницы", color=self.titleColor, halign="center",
                               valign="center", text_size=(Window.size[0] * .4, None))
        self.headBox.add_widget(self.pageTitle)
        self.boxHeader.add_widget(self.headBox)

        # Поиск и настройки

        self.setBox = BoxLayout(size_hint_x=.33, padding=self.padding, spacing=self.spacing)
        self.search = TopButton(text=icon("icon-search-1"))
        self.search.bind(on_release=self.searchPressed)
        self.setBox.add_widget(self.search)

        self.settings = TopButton(text="  " + icon("icon-dots") + "  ")
        self.settings.bind(on_release=self.settingsPressed)
        self.setBox.add_widget(self.settings)
        self.boxHeader.add_widget(self.setBox)
        self.interface.add_widget(self.boxHeader)

        self.boxCenter = BoxLayout()
        self.mainBox = BoxLayout()
        self.boxCenter.add_widget(self.mainBox)
        self.listarea = BoxLayout(orientation="vertical")
        self.mainBox.add_widget(self.listarea)

        #  Верхние кнопки таблицы

        self.titleBox = BoxLayout(size_hint_y=self.marginSizeHintY)#size_hint_y=None, height=Window.size[1]*self.marginSizeHintY
        self.listarea.add_widget(self.titleBox)
        self.backButton = TableButton(text=icon("icon-left-big"))
        self.backButton.bind(on_release=self.backPressed)
        self.titleBox.add_widget(self.backButton)

        self.dropSortMenu = DropDown()
        self.sortButton = TableButton(text=icon("icon-sort-alt-up"))
        self.titleBox.add_widget(self.sortButton)
        self.sortButton.bind(on_press=self.sortPressed)

        self.detailsButton = TableButton(text=icon("icon-pencil-1"))
        self.detailsButton.bind(on_release=self.detailsPressed)
        self.titleBox.add_widget(self.detailsButton)

        self.note = TableButton(text=icon("icon-edit-1"))
        self.titleBox.add_widget(self.note)
        self.note.bind(on_release=self.notePressed)

        # Главный список

        self.mainList = BoxLayout(orientation="vertical", padding=(0, self.padding))
        AL = AnchorLayout(anchor_x="center", anchor_y="top")
        AL.add_widget(self.mainList)
        self.listarea.add_widget(AL)#self.mainList)

        self.reportBoxesAL = AnchorLayout(anchor_x="center", anchor_y="center") # для счетчиков в новом посещении

        # Слайдер и джойстик выбора позиции

        self.sliderBox = BoxLayout()
        self.slider = Slider(pos=(0, Window.size[1] * .75), orientation='horizontal', min=0.4, max=2,
                             padding=0, value=utils.settings[0][8], cursor_image=self.sliderImage)
        self.sliderBox.add_widget(self.slider)
        self.posSelector = GridLayout(pos=(Window.size[0]/2, Window.size[1]/2), rows=3, cols=3, size_hint=(None, None),
                                      padding=self.padding,
                                      size=(self.standardTextHeight*5, self.standardTextHeight*8))
        buttons = []
        for i in [1,2,3,4,5,6,7,8,9]:
            buttons.append(Button(text=icon("icon-target-1"), background_down=self.buttonPressedBG,
                                  background_normal="", markup=True, color=self.tableColor,
                background_color=[self.tableBGColor[0], self.tableBGColor[1], self.tableBGColor[2], .9]))
            self.posSelector.add_widget(buttons[len(buttons)-1])
            def __click1(instance): self.changePorchPos(1)
            def __click2(instance): self.changePorchPos(2)
            def __click3(instance): self.changePorchPos(3)
            def __click4(instance): self.changePorchPos(4)
            def __click5(instance): self.changePorchPos(5)
            def __click6(instance): self.changePorchPos(6)
            def __click7(instance): self.changePorchPos(7)
            def __click8(instance): self.changePorchPos(8)
            def __click9(instance): self.changePorchPos(9)
            if i == 1: buttons[len(buttons)-1].bind(on_release=__click1)
            elif i == 2: buttons[len(buttons) - 1].bind(on_release=__click2)
            elif i == 3: buttons[len(buttons) - 1].bind(on_release=__click3)
            elif i == 4: buttons[len(buttons) - 1].bind(on_release=__click4)
            elif i == 5: buttons[len(buttons) - 1].bind(on_release=__click5)
            elif i == 6: buttons[len(buttons) - 1].bind(on_release=__click6)
            elif i == 7: buttons[len(buttons) - 1].bind(on_release=__click7)
            elif i == 8: buttons[len(buttons) - 1].bind(on_release=__click8)
            elif i == 9: buttons[len(buttons) - 1].bind(on_release=__click9)
            buttons[len(buttons)-1].bind(on_press=self.buttonFlash)
        self.slider.bind(on_touch_move=self.sliderGet)
        self.slider.bind(on_touch_up=self.sliderGet)

        # Нижние кнопки таблицы

        self.bottomButtons = BoxLayout(size_hint_y=self.marginSizeHintY)
        self.listarea.add_widget(self.bottomButtons)

        self.positive = TableButton(background_color=self.globalBGColor)
        self.positive.bind(on_release=self.positivePressed)
        self.bottomButtons.add_widget(self.positive)

        self.neutral = TableButton(size_hint_x=0.25, background_color=self.globalBGColor)
        self.neutral.bind(on_release=self.neutralPressed)
        self.bottomButtons.add_widget(self.neutral)

        self.negative = TableButton(background_color=self.globalBGColor)
        self.negative.bind(on_release=self.backPressed)
        self.bottomButtons.add_widget(self.negative)
        self.interface.add_widget(self.boxCenter)

        # Подвал и кнопки меню

        self.boxFooter = BoxLayout(size_hint_y=self.marginSizeHintY, height=0)#, padding=(0, self.padding*2))
        self.buttonTer = MainMenuButton(text="Участки")  # text="Участки")#
        self.buttonTer.bind(on_release=self.terPressed)
        b1 = AnchorLayout(anchor_x="center")
        b1.add_widget(self.buttonTer)
        self.boxFooter.add_widget(b1)
        self.buttonCon = MainMenuButton(text="Контакты")  # (text="Контакты")
        self.buttonCon.bind(on_release=self.conPressed)
        b2 = AnchorLayout(anchor_x="center")
        b2.add_widget(self.buttonCon)
        self.boxFooter.add_widget(b2)
        self.buttonRep = MainMenuButton(text="Отчет")  # Button(text="Отчет")
        self.buttonRep.bind(on_release=self.repPressed)
        b3 = AnchorLayout(anchor_x="center")
        b3.add_widget(self.buttonRep)
        self.boxFooter.add_widget(b3)
        self.interface.add_widget(self.boxFooter)
        self.globalAnchor.add_widget(self.interface)

        self.checkOrientation()

    def setTheme(self):

        self.themeDefault = [0.92, 0.92, 0.92, .9], [0, .15, .35, .8], [.18, .65, .83, 1] # цвет фона, кнопок и title
        self.themePurple = [0.92, 0.92, 0.92, .9], [.36, .24, .53, .9], [.62, .15, .70, 1]
        self.themeTeal = [0.2, 0.64, 0.81, .9], "white", self.themeDefault[2]
        self.themeDark = [.22, .22, .22, .9], "white", "white"

        self.theme = utils.settings[0][5]

        if self.firstRunFlag == True and platform == "android": # определяем темную тему на мобильном устройстве при первом запуске
            from kvdroid.tools.darkmode import dark_mode
            if dark_mode() == True:
                self.theme = utils.settings[0][5] = "dark"
                utils.save()

        elif self.devmode==0: # пытаемся получить тему из файла на ПК
            try:
                with open("theme.ini", mode="r") as file:
                    t = int(file.readlines()[0])
                if t == 1:
                    self.theme = "default"
                elif t == 2:
                    self.theme = "purple"
                elif t == 3:
                    self.theme = "teal"
                elif t == 4:
                    self.theme = "dark"
            except:
                pass

        if self.theme == "dark":
            self.globalBGColor = self.globalBGColor0 = "black"#self.themeDark # фон программы
            Window.clearcolor = self.globalBGColor
            self.mainMenuButtonColor =  self.themeDark[1]
            self.mainMenuButtonColor2= "FFFFFF"
            self.topButtonColor = [.75,.75,.75]#"lightgray" # поиск, настройки и кнопки счетчиков
            self.tableBGColor = self.themeDark[0] # цвет фона кнопок таблицы
            self.standardTextColor = "white" # основной текст всех шрифтов
            self.interestColor = "00BC7F"  # "00CA94" # должен соответствовать зеленому статусу или чуть светлее
            self.titleColor = [.3, .82, 1] # неон - цвет нажатой кнопки и заголовка
            self.titleColor2 = "189CD8"
            self.popupBackgroundColor = [.16, .16, .16] # фон всплывающего окна
            self.tableColor = self.themeDark[1] # цвет текста на плашках таблицы и кнопках главного меню
            self.standardScrollColor = "white" # текст пунктов списка
            self.scrollButtonBackgroundColor = [.38,.38,.38]#[.14, .14, .14] # фон пунктов списка
            self.scrollButtonBackgroundColor2 = [.28, .28, .28] # более темный цвет списка (создать подъезд + нет дома)
            self.createNewPorchButton = [.2, .2, .2] # пункт списка создания нового подъезда
            self.textInputBGColor = [.1, .1, .1, 1]
            self.buttonPressedOnDark = [.3, .3, .3] # цвет только в темной теме, определяющий засветление фона кнопки
            self.sliderImage = "slider_cursor.png"

        else:
            self.globalBGColor = (1, 1, 1, 1)
            self.globalBGColor0 = (1, 1, 1, 0)
            Window.clearcolor = self.globalBGColor
            self.topButtonColor = [.75,.75,.75]
            self.standardTextColor = [.1, .1, .1]
            self.interestColor = "00BC7F"  # "00CA94" # должен соответствовать зеленому статусу или чуть светлее
            self.titleColor = self.themeDefault[2]
            self.titleColor2 = "2FA7D4"
            self.tableBGColor = self.themeDefault[0]
            self.popupBackgroundColor = [.16, .16, .16]
            self.standardScrollColor = "white"
            self.scrollButtonBackgroundColor = [.56,.56,.56]
            self.scrollButtonBackgroundColor2 = [.46,.46,.46]
            self.createNewPorchButton = "dimgray"
            self.phoneNeutralButton = "lightgreen"
            self.reportFlashColor = "lightgreen"
            self.textInputBGColor = [.97, .97, .97, 1]
            self.sliderImage = "slider_cursor.png"

            if self.theme == "purple": # под Library
                self.titleColor = [.62, .15, .70, .95]
                self.titleColor2 = "B24CCC"
                self.tableColor = self.mainMenuButtonColor = self.themePurple[1]
                self.mainMenuButtonColor2 = "5C3D87"
                self.sliderImage = "slider_cursor_purple.png"

            elif self.theme == "green": # секретная тема
                self.titleColor = [.09, .65, .58, 1]
                self.titleColor2 = "009999"
                self.tableColor = self.mainMenuButtonColor = [0, .4, .4]
                self.mainMenuButtonColor2 = "000A0A"

            elif self.theme == "teal": # тема 2.0.1 бирюзовая
                self.tableColor = self.mainMenuButtonColor = self.themeTeal[1]
                self.tableBGColor = self.themeTeal[0]
                self.mainMenuButtonColor2 = "FFFFFF"

            else:
                self.tableColor = self.mainMenuButtonColor = self.themeDefault[1]
                self.mainMenuButtonColor2 = "2F4E77"

        #buffer.Color = self.titleColor

    # Основные действия с центральным списком

    def updateList(self):#, a=1, b=1):
        """Заполнение главного списка элементами"""

        if 1:#self.devmode==1:
        #try:
            #a/b
            self.stack = list(dict.fromkeys(self.stack))
            #print(self.stack)
            self.mainList.clear_widgets()
            self.popupEntryPoint = 0
            if self.showSlider == False:
                self.sortButton.disabled = True

            if self.displayed.positive != "": # выставление параметров, полученных из Feed
                self.positive.disabled = False
                self.positive.text = self.displayed.positive
            else:
                self.positive.text = ""
                self.positive.disabled = True

            if self.displayed.neutral != "":
                self.neutral.disabled = False
                self.neutral.text = self.displayed.neutral
            else:
                self.neutral.text = ""
                self.neutral.disabled = True

            if self.displayed.negative != "":
                self.negative.disabled = False
                self.negative.text = self.displayed.negative
            else:
                self.negative.text = ""
                self.negative.disabled = True

            if self.displayed.sort != None:
                self.sortButton.disabled = False
                self.sortButton.text = self.displayed.sort
            else:
                self.sortButton.text = ""
                self.sortButton.disabled = True
            if self.displayed.details != None:
                self.detailsButton.disabled = False
                self.detailsButton.text = self.displayed.details
            else:
                self.detailsButton.text = ""
                self.detailsButton.disabled = True
            if self.displayed.note != None:
                self.note.disabled = False
                self.note.text = self.displayed.note
            else:
                self.note.text = ""
                self.note.disabled = True
            if self.displayed.back == False:
                self.backButton.disabled = True
            else:
                self.backButton.disabled = False

            # Обычный список (этажей нет)

            if self.displayed.form != "porchView" or \
                    (self.displayed.form == "porchView" and self.porch.floors() == False):#or self.porch.rows==1:
                height1 = self.standardTextHeight*1.5
                height = height1
                self.scrollWidget = GridLayout(cols=1, spacing=(self.spacing, self.spacing*2), padding=self.padding,
                                               size_hint_y=None)
                self.scrollWidget.bind(minimum_height=self.scrollWidget.setter('height'))
                self.scroll = ScrollView(size=(self.mainList.size[0]*.9, self.mainList.size[1]*.9),
                                         bar_width=self.standardBarWidth, scroll_type=['bars', 'content'])
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
                        background_color = self.scrollButtonBackgroundColor2
                        status = ""
                    else:
                        background_color = self.scrollButtonBackgroundColor
                        status = ""

                    if self.displayed.form != "porchView":
                        background_color = ""
                        color = ""
                    else:
                        color = "white"

                    addPhone = addNote = addRecord = False
                    valign = "center"
                    if self.displayed.form == "porchView" and len(self.indexes) > 0:
                        flat = self.porch.flats[self.indexes[i]]
                        if len(flat.records) > 0:
                            addRecord = True
                        if flat.phone != "":
                            addPhone = True
                        if flat.note != "":
                            addNote = True
                    elif self.displayed.form == "flatView":
                        height = height1
                        valign = "top"

                    # Добавление пункта списка

                    if "Ничего не найдено" in label or "Здесь будут" in label or self.displayed.form == "repLog":
                        # отдельный механизм добавления записей журнала отчета + ничего не найдено в поиске
                        self.scrollWidget.add_widget(Label(text=label.strip(), color=self.standardTextColor, halign="left",
                                                           valign="top", size_hint_y=None, height=height1, markup=True,
                                                            text_size=(Window.size[0] - 50, height1)))

                    else: # стандартное добавление

                        height = self.standardTextHeight * 1.2 # коэффициент, на который квартира выше пункта в стандартном списке
                        gap = 1.05 # зазор между квартирами в списке
                        box = BoxLayout(orientation="vertical", size_hint_y=None)

                        if self.displayed.form != "porchView": # вид для всех списков, кроме подъезда - без фона
                            self.btn.append(ScrollButton(text=label.strip(), height=height, valign=valign,
                                                     color = color, background_color=background_color))

                        else: # вид для списка подъезда - с фоном и закругленными квадратиками
                            self.scrollWidget.spacing = (self.spacing, 0)
                            self.scrollWidget.padding = (self.padding, 0)
                            self.btn.append(FlatButton(text=label.strip(), height=height, status=status,
                                                       size_hint_y=None))
                        last = len(self.btn)-1
                        box.add_widget(self.btn[last])

                        if addRecord == True or addPhone == True or addNote == True: # если есть запись посещения, телефон или заметка, добавляем снизу
                            gray = "919191"
                            br = ""
                            if flat.phone != "":
                                myicon = icon("icon-phone-1")
                                phone = f"[color={gray}]{myicon}[/color]\u00A0{flat.phone}\u00A0\u00A0\u00A0\u00A0\u00A0"
                                br = "\n"
                            else:
                                phone = ""
                            if flat.note != "":
                                myicon = icon("icon-sticky-note")
                                note = f"[color={gray}]{myicon}[/color]\u00A0{flat.note}"
                                br = "\n"
                            else:
                                note = ""
                            if len(flat.records) > 0:
                                myicon = icon("icon-chat")
                                record = f"{br}[color={gray}]{myicon}[/color]\u00A0[i]{flat.records[0].title}[/i]"
                            else:
                                record = ""
                            text = phone + note + record
                            box.add_widget( Label(
                                text=text, markup=True, color=self.standardTextColor, halign="left", valign="top", size_hint_y=None,
                                height=height1, text_size = (Window.size[0]-50, height1)
                                )
                            )
                            box.height = height * gap + height1
                        else:
                            box.height = height * gap

                        self.scrollWidget.add_widget(box)

                self.scrollWidget.add_widget(Button(size_hint_y=None, # пустая кнопка для решения бага последней записи
                                                    height=height, halign="center", valign="center",
                                                    text_size = (Window.size[0]-15, height-10), background_normal="",
                                                    background_color=self.globalBGColor, background_down=""))

                self.scroll.add_widget(self.scrollWidget)
                self.mainList.add_widget(self.scroll)
                self.positive.text = self.displayed.positive
                self.negative.text = self.displayed.negative

            # Вид подъезда с этажами

            elif utils.settings[0][7] == 1: # поэтажная раскладка с масштабированием

                spacing = self.spacing * 2

                self.floorview = GridLayout(cols=self.porch.columns+1, rows=self.porch.rows, spacing=spacing,
                                            padding=spacing*2)
                for label in self.displayed.options:
                    if "│" in label: # показ цифры этажа
                        self.floorview.add_widget(Label(text=label[: label.index("│")], halign="right",
                                color=self.standardTextColor, width=self.standardTextHeight/3,
                                                        size_hint_x=None, font_size=self.fontXS))
                    elif "." in label:
                        self.floorview.add_widget(Widget())
                    else:
                        status = label[label.index("{")+1 : label.index("}")] # определение цвета по статусу
                        b = FlatButton(text=label[label.index("}")+1 : ], status=status, size_hint_y=0)#, radius=[12])
                        self.floorview.add_widget(b)
                self.sliderToggle()
                self.mainList.add_widget(self.floorview)

            else: # без масштабирования

                if utils.settings[0][8] != 0: # расчеты расстояний и зазоров
                    size = self.standardTextHeight * utils.settings[0][8]
                else:
                    size = self.standardTextHeight

                noScaleSpacing = self.spacing * 2

                floorLabelWidth = size / 6

                diffX = self.mainList.size[0] - (size * self.porch.columns + size/4) - (noScaleSpacing * self.porch.columns)
                diffY = self.mainListSize1 - (size * self.porch.rows) - (noScaleSpacing * self.porch.rows)

                # Определение центровки

                if utils.settings[0][1] == 1:
                    self.noScalePadding = [0, 0, diffX, diffY / 2]  # влево вверху
                elif utils.settings[0][1] == 2:
                    self.noScalePadding = [diffX / 2, 0, diffX / 2, diffY]  # по центру вверху
                elif utils.settings[0][1] == 3:
                    self.noScalePadding = [diffX, 0, diffY, 0]  # справа вверху
                elif utils.settings[0][1] == 4:
                    self.noScalePadding = [0, diffY / 2, diffX, diffY / 2] # влево по центру
                elif utils.settings[0][1] == 6:
                    self.noScalePadding = [diffX, diffY / 2, 0, diffY / 2]  # справа по центру
                elif utils.settings[0][1] == 7:
                    self.noScalePadding = [0, diffY, diffX, 0 / 2]  # влево внизу
                elif utils.settings[0][1] == 8:
                    self.noScalePadding = [diffX/2, diffY, 0, diffX/2]  # снизу по центру
                elif utils.settings[0][1] == 9:
                    self.noScalePadding = [diffX, diffY, 0, 0]  # справа снизу
                else:
                    self.noScalePadding = [diffX / 2, diffY / 2, diffX / 2, diffY / 2]  # по центру

                if self.noScalePadding[0] < 0 or self.noScalePadding[1] < 0: # если слишком большой подъезд, включаем масштабирование
                    utils.settings[0][7]=1
                    self.porchView()
                    return

                BL = BoxLayout()
                self.floorview = GridLayout(row_force_default=True, row_default_height=size, # отрисовка
                                            col_force_default=True, col_default_width=size,
                                            cols_minimum={0: floorLabelWidth},
                                            cols=self.porch.columns + 1,
                                            rows=self.porch.rows, spacing=noScaleSpacing, padding=self.noScalePadding)

                for label in self.displayed.options:
                    if "│" in label: # показ цифры этажа
                        self.floorview.add_widget(Label(text=label[: label.index("│")], halign="right",
                                                        valign="center",
                                                        width=floorLabelWidth, font_size=self.fontXS, height=size,
                                                        size_hint=(None, None),
                                                        color=self.standardTextColor))
                    elif "." in label:
                        self.floorview.add_widget(Widget())
                    else:
                        status = label[label.index("{")+1 : label.index("}")] # определение цвета по статусу
                        b = FlatButton(text=label[label.index("}")+1 : ], status=status, width=size, height=size,
                                   size_hint_x=None, size_hint_y=None)
                        self.floorview.add_widget(b)
                BL.add_widget(self.floorview)
                self.mainList.add_widget(BL)
                self.sliderToggle()

            self.pageTitle.text = self.displayed.title

            # Срабатывает при первом запуске программы

            if self.firstRunFlag == True:
                self.firstRunFlag = False
                def __onFirstRun(*args):
                    self.popupForm = "pioneerNorm"
                    self.popup(title="Rocket Ministry",
                               message="Вы общий пионер? Тогда мы пропишем месячную норму часов. Ее можно ввести самостоятельно в настройках.",
                               options=[self.button["yes"], self.button["no"]])
                Clock.schedule_once(__onFirstRun, 2)

        """except: # в случае ошибки пытаемся восстановить последнюю резервную копию
            if self.restore < 10:
                print(f"Файл базы данных поврежден, пытаюсь восстановить резервную копию {self.restore}.")
                result = utils.backupRestore(restoreNumber = self.restore, allowSave=False)
                if result != False:
                    print("Резервная копия восстановлена.")
                    self.restore += 1
                    self.rep = report.Report()
                    utils.save(backup=False)
                    self.updateList()
                else:
                    print("Резервных копий больше нет.")
                    self.restore = 10

            else:
                self.popupForm = "emergencyExport"
                self.popup(title="Ошибка базы данных",
                       message="Программа не может продолжить работу. Попробуйте удалить объект, созданный последним. Если это не помогает, зайдите в настройки, сделайте экспорт данных в Google Диск и отправьте файл разработчикам для анализа проблемы. Также вы можете выполнить очистку данных и начать работу с нуля.")
"""
    def sliderToggle(self, mode=""):
        utils.settings[0][7] = 0
        if mode == "off":
            self.showSlider = False
        if self.showSlider == True and not self.sliderBox in self.boxHeader.children:
            self.boxHeader.remove_widget(self.timerBox)
            self.boxHeader.remove_widget(self.headBox)
            self.boxHeader.remove_widget(self.setBox)
            self.boxHeader.add_widget(self.sliderBox)
            self.boxFooter.add_widget(self.posSelector)
        if self.showSlider == False and self.sliderBox in self.boxHeader.children:
            self.boxHeader.remove_widget(self.sliderBox)
            self.boxHeader.add_widget(self.timerBox)
            self.boxHeader.add_widget(self.headBox)
            self.boxHeader.add_widget(self.setBox)
            self.boxFooter.remove_widget(self.posSelector)
        utils.save()

    def sliderGet(self, x, y):
        utils.settings[0][8] = self.slider.value
        self.porchView()

    def clickOnList(self, instance, touch=None):
        """Действия, которые совершаются на указанных экранах по нажатию на кнопку главного списка"""

        def __do(*args): # действие всегда выполняется с запаздыванием, чтобы отобразилась анимация на кнопке

            if "Создайте" in instance.text or "Здесь будут" in instance.text:
                self.positivePressed()
            elif "Создать подъезд" in instance.text:
                text = instance.text[19:]
                if "[/i]" in text:
                    text = text[ : text.index("[")]
                self.house.addPorch(text.strip())
                utils.save()
                self.houseView(instance=instance)

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
                        self.houseView(instance=instance) # вход в дом

                    elif self.displayed.form == "houseView":
                        self.porch = self.house.porches[self.choice] # начиная отсюда знаем подъезд и его индекс
                        self.selectedPorch = self.choice
                        self.porchView(instance=instance) # вход в подъезд

                    elif self.displayed.form == "porchView":
                        try:
                            number = instance.text[instance.text.index("[b]")+3 : instance.text.index("[/b]")].strip()
                        except:
                            number = instance.text.strip()

                        for i in range(len(self.porch.flats)):
                            if number == self.porch.flats[i].number:
                                self.flat = self.porch.flats[i]
                                self.selectedFlat = i # отсюда знаем квартиру, ее индекс и фактический номер
                                break

                        if self.porch.floors() == False and len(self.btn) > 10: # определяем индекс нажатой конкретной кнопки скролла, чтобы затем промотать до нее вид
                            for i in range(len(self.btn)):
                                if self.btn[i].text == instance.text:
                                    self.clickedBtnIndex = i
                                    break

                        self.flatView(call=False, instance=instance) # вход в квартиру

                    elif self.displayed.form == "flatView": # режим редактирования записей
                        self.selectedRecord = self.choice # отсюда знаем запись и ее индекс
                        self.record = self.flat.records[self.selectedRecord]

                        if len(self.btn) > 10:
                            for i in range(len(self.btn)): # определяем индекс нажатой кнопки скролла
                                if self.btn[i].text == instance.text:
                                    self.clickedBtnIndex = i
                                    break

                        self.recordView(instance=instance) # вход в запись посещения

                    elif self.displayed.form == "con": # контакты
                        contactText = self.displayed.options[self.choice]

                        for w in range(len(self.displayed.options)):
                            if contactText == self.displayed.options[w]:
                                self.selectedCon = w # знаем индекс контакта в списке контактов
                                break

                        if len(self.btn) > 10:
                            for i in range(len(self.btn)): # определяем индекс нажатой кнопки скролла
                                if self.btn[i].text == instance.text:
                                    self.clickedBtnIndex = i
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
                        self.flatView(instance=instance)

                    elif self.displayed.form == "search": # поиск
                        contactText = self.displayed.options[self.choice]

                        for w in range(len(self.displayed.options)):
                            if contactText == self.displayed.options[w]:
                                self.selectedCon = w  # знаем индекс контакта в поисковой выдаче
                                self.clickedBtnIndex = i
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
                        self.flatView(instance=instance)

                    break

        Clock.schedule_once(__do, self.onClickFlash/2)

    def detailsPressed(self, instance=None):
        """ Нажата кнопка настроек рядом с заголовком (редактирование данного объекта) """
        self.showSlider = False
        self.sliderToggle()
        if self.displayed.form == "houseView" or self.displayed.form == "noteForHouse" or \
            self.displayed.form == "createNewPorch":  # детали участка
            self.displayed.form = "houseDetails"
            if self.house.type == "private":
                title = "Название участка:"
            else:
                title = "Адрес:"
            self.createMultipleInputBox(
                title=self.house.title + " – правка",
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
                title=f"{self.porch.type[:7]} {self.porch.title} – правка",
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
                multilines.append(False)
            elif self.house.type != "condo":
                options.append("Номер %s:" % self.house.getPorchType()[1])
                defaults.append(self.flat.number)
                multilines.append(False)
            self.createMultipleInputBox(
                title=self.flatTitle + " – правка",
                options=options,
                defaults=defaults,
                multilines=multilines
            )

    def backPressed(self, instance=None):
        """Нажата кнопка «назад»"""

        self.showSlider = False
        self.sliderToggle()

        if len(self.stack) > 0:
            del self.stack[0]

        if self.displayed.form == "repLog":
            self.repPressed()

        else:
            if len(self.stack) > 0:#try:
                if self.stack[0] == "ter":
                    self.terPressed()
                elif self.stack[0] == "con":
                    self.conPressed()
                elif self.stack[0] == "search":
                    self.find()
                elif self.stack[0] == "houseView":
                    self.houseView()
                elif self.stack[0] == "porchView":
                    self.porchView()
                elif self.stack[0] == "flatView":
                    self.flatView()
                #elif self.stack[0] == "repLog":
                #    self.repPressed()

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
                btn = SortListButton(text=sortTypes[i])
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
                btn.bind(on_press=__resortHouses)
                self.dropSortMenu.add_widget(btn)
            self.dropSortMenu.bind(on_select=lambda instance, x: setattr(self.sortButton, 'text', x))
            self.sortButton.bind(on_release=self.dropSortMenu.open)

        elif self.displayed.form == "porchView":
            if self.porch.floors() == False: # меню сортировки квартир в подъезде
                sortTypes = ["Номер", "Номер обр.", "Статус", "Заметка", "Телефон"]
                for i in range(len(sortTypes)):
                    btn = SortListButton(text=sortTypes[i])
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
                    btn.bind(on_press=__resortFlats)
                    self.dropSortMenu.add_widget(btn)
                self.dropSortMenu.bind(on_select=lambda instance, x: setattr(self.sortButton, 'text', x))
                self.sortButton.bind(on_release=self.dropSortMenu.open)

            else: # слайдер
                if self.showSlider == True:
                    self.showSlider = False
                    utils.save()
                else:
                    self.showSlider = True
                self.porchView()
                self.sliderToggle("on")

        elif self.displayed.form == "con":  # меню сортировки контактов
            self.dropSortMenu.clear_widgets()
            sortTypes = [
                "Имя",
                "Статус",
                "Адрес",
                "Телефон",
                "Заметка"
            ]
            for i in range(len(sortTypes)):
                btn = SortListButton(text=sortTypes[i])
                def __resortCons(instance=None):
                    if instance.text == sortTypes[0]:
                        utils.settings[0][4] = "и"
                    elif instance.text == sortTypes[1]:
                        utils.settings[0][4] = "с"
                    elif instance.text == sortTypes[2]:
                        utils.settings[0][4] = "а"
                    elif instance.text == sortTypes[3]:
                        utils.settings[0][4] = "т"
                    elif instance.text == sortTypes[4]:
                        utils.settings[0][4] = "з"
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
            self.timerText.text = f"  [b]{utils.timeFloatToHHMM(self.time2)}[/b]"
        else:
            self.timerText.text = ""

        if ":" in self.timerText.text:
            self.timer.on()
        else:
            self.timer.off()

    def timerPressed(self, instance=None):
        self.updateTimer()
        result = self.rep.toggleTimer()
        if result == 1:
            self.rep.modify(")") # кредит выключен, записываем время служения сразу
            if self.displayed.form == "rep":
                self.repPressed()
        elif result == 2: # кредит включен, сначала спрашиваем, что записать
            self.popupForm = "timerType"
            self.popup(title="Таймер", message=f"Подсчитанное время: {self.timerText.text.strip()}. Куда записать?",
                        options=["Служение", "Кредит"])

    def notePressed(self, instance=None):

        self.showSlider = False
        self.sliderToggle()

        if instance != None and "Помощь" in instance.text:
            webbrowser.open("https://github.com/antorix/Rocket-Ministry/wiki")

        elif self.displayed.form == "ter" or self.displayed.form == "set" or self.displayed.form == "con"\
                or self.displayed.form == "createNewHouse" or \
             self.displayed.form == "createNewCon" or self.displayed.form == "search":
            self.displayed.form = "noteGlobal"
            self.createInputBox(
                title="Глобальная заметка",
                message="Любая произвольная информация для себя:",
                default=utils.resources[0][0],
                multiline=True
            )

        elif self.displayed.form == "houseView" or self.displayed.form == "houseDetails" or \
                self.displayed.form == "createNewPorch":
            self.displayed.form = "noteForHouse"
            self.createInputBox(
                title=self.house.title + " – заметка",
                message="Любая информация об участке:",
                default=self.house.note,
                multiline=True
            )

        elif self.displayed.form == "porchView" or self.displayed.form == "porchDetails"  or \
                self.displayed.form == "createNewFlat":
            self.displayed.form = "noteForPorch"
            self.createInputBox(
                title=f"{self.porch.type[:7]} {self.porch.title} – заметка",
                message=f"Любая информация о {self.porch.type[:7]}е:",
                default=self.porch.note,
                multiline=True
            )

        elif self.displayed.form == "flatView" or self.displayed.form == "flatDetails" or \
                self.displayed.form == "createNewRecord" or self.displayed.form == "recordView":
            self.displayed.form = "noteForFlat"
            self.createInputBox(
                title=f"{self.flatTitle} – заметка",
                message="Любая информация о человеке/квартире:",
                default=self.flat.note,
                multiline=True
            )

        elif "Журнал" in instance.text: # журнал отчета
            options=[]
            for line in utils.resources[2]:
                options.append(line)
            self.displayed = Feed(
                title="Журнал отчета",
                options=options,
                form="repLog",
                positive="",#self.button["save"],
                negative=self.button["exit"]
            )
            if instance != None:
                self.stack.insert(0, self.displayed.form)
            self.updateList()

    # Действия главных кнопок positive, neutral, negative

    def positivePressed(self, instance=None, value=None):
        """ Что выполняет левая кнопка в зависимости от экрана """
        self.showSlider = False
        self.sliderToggle()

        # Отчет

        if self.displayed.form == "rep":
            if self.reportPanel.current_tab.text == utils.monthName()[0]:
                success = 1
                change = 0
                try:
                    temp = int(self.placements.get().strip())
                except:
                    success = 0
                else:
                    if temp != self.rep.placements:
                        change = 1
                    temp_placements = temp

                try:
                    temp = int(self.video.get().strip())
                except:
                    success = 0
                else:
                    if temp != self.rep.videos:
                        change = 1
                    temp_videos = temp

                try:
                    temp = utils.timeHHMMToFloat(self.hours.get().strip())
                    if temp == None: # если конвертация не удалась, создаем ошибку
                        5/0
                except:
                    success = 0
                else:
                    if temp != self.rep.hours:
                        change = 1
                    temp_hours = temp

                try:
                    if utils.settings[0][2]==1:
                        temp = utils.timeHHMMToFloat(self.credit.get().strip())
                        if temp == None:
                            5/0
                    else:
                        temp = 0
                except:
                    success = 0
                else:
                    if utils.settings[0][2] == 1:
                        if temp != self.rep.credit:
                            change = 1
                        temp_credit = temp

                try:
                    temp = int(self.returns.get().strip())
                except:
                    success = 0
                else:
                    if temp != self.rep.returns:
                        change = 1
                    temp_returns = temp

                try:
                    temp = int(self.studies.get().strip())
                except:
                    success = 0
                else:
                    if temp != self.rep.studies:
                        change = 1
                    temp_studies = temp

                if success == 0:
                    self.popup("Ошибка в каком-то из полей, проверьте данные!")

                elif success == 1 and change == 1 and self.counterChanged == True:
                    self.rep.modify() # для проверки нового месяца
                    self.rep.placements = temp_placements
                    self.rep.videos = temp_videos
                    self.rep.hours = temp_hours
                    self.rep.returns = temp_returns
                    self.rep.studies = temp_studies
                    if utils.settings[0][2] == 1:
                        self.rep.credit = temp_credit
                        credit = "кред.: %s, " % utils.timeFloatToHHMM(self.rep.credit)
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

                self.counterChanged = False

            elif "Служ" in self.reportPanel.current_tab.text:
                self.recalcServiceYear()

            else:
                if self.rep.getLastMonthReport()[0] != "":
                    utils.log("Отчет за прошлый месяц уже сохранен и будет здесь весь месяц!")
                else:
                    utils.log("Отчет за прошлый месяц сохраняется автоматически в начале следующего месяца!")

        #elif self.displayed.form == "repLog":
        #    self.repPressed()

        # Настройки

        elif self.displayed.form == "set":

            if self.settingsPanel.current_tab.text == "Настройки":
                if utils.settings[0][7] == 1 and self.multipleBoxEntries[6].active == False:
                    self.slider.value = utils.settings[0][8] = 1
                    self.showSlider = False
                try:
                    if self.multipleBoxEntries[0].text.strip() == "":
                        utils.settings[0][3] = 0
                    else:
                        utils.settings[0][3] = int(self.multipleBoxEntries[0].text.strip()) # норма часов
                except:
                    pass
                utils.settings[0][13] = self.multipleBoxEntries[1].active # нет дома
                utils.settings[0][15] = self.multipleBoxEntries[2].active # переносить минуты
                utils.settings[0][18] = self.multipleBoxEntries[3].get()  # цвет отказа
                utils.settings[0][10] = self.multipleBoxEntries[4].active # автоотказ
                utils.settings[0][2] = self.multipleBoxEntries[5].active  # кредит
                utils.settings[0][20] = self.multipleBoxEntries[6].active # показывать телефон
                utils.settings[0][0] = self.multipleBoxEntries[7].active  # уведомление при запуске таймера
                utils.save()
                self.backPressed(instance)
                utils.log("Настройки сохранены")

            elif self.settingsPanel.current_tab.text == "Данные":
                utils.save()
                self.backPressed(instance)
                utils.log("Данные сохранены")

        elif self.displayed.form == "con":
            self.detailsButton.disabled = True
            self.displayed.form = "createNewCon"
            self.createInputBox(
                title="Создание контакта",
                message="Введите имя и (или) описание человека:",
                multiline=False
            )

        elif self.displayed.form == "flatView":
            if len(self.flat.records) > 0:
                self.displayed.form = "createNewRecord" # в этом случае позитивная кнопка - создание посещения
                self.createInputBox(
                    title=f"{self.flatTitle} — новое посещение",
                    message="О чем говорили:",
                    multiline=True,
                    addCheckBoxes=True
                )
            else: # в этом случае - сохранение первого посещения и выход в подъезд
                newName = self.multipleBoxEntries[0].text.strip()
                if self.house.type != "virtual" or newName != "":
                    self.flat.updateName(newName)
                if self.multipleBoxEntries[1].text.strip() != "":
                    self.flat.addRecord(self.multipleBoxEntries[1].text.strip())
                self.processReportCounters()
                if self.contactsEntryPoint == 1:
                    self.conPressed()
                elif self.searchEntryPoint == 1:
                    self.find()
                else:
                    self.porchView()
                utils.save()

        elif self.displayed.form == "search" or self.popupForm == "firstCall":
            self.backPressed()

        # Форма создания квартир/домов

        elif self.displayed.form == "porchView":
            self.stack.insert(0, self.stack[0]) # дублирование последнего шага стека, чтобы предотвратить уход со страницы
            self.detailsButton.disabled = False
            self.sortButton.disabled = True
            self.neutral.disabled = True
            self.displayed.form = "createNewFlat"
            if self.house.type == "condo": # многоквартирный дом
                self.mainList.clear_widgets()
                self.pageTitle.text = "Квартиры подъезда %s" % self.porch.title
                self.positive.text = self.button["save"]
                self.negative.text = self.button["cancel"]
                a = AnchorLayout(anchor_x="center", anchor_y="top")#, size_hint_x=.95)
                grid = GridLayout(rows=4, cols=2, size_hint=(.85, .9), height=self.mainList.size[1]*.75)
                align="center"
                if len(self.porch.flats)==0: # определяем номер первой и последней квартир, сначала если это первый подъезд:
                    firstflat = "1"
                    lastflat = "20"
                    floors = "5"
                    if self.selectedPorch > 0:
                        prevFirst = int(self.house.porches[self.selectedPorch - 1].getFirstAndLastNumbers()[0])
                        prevLast = int(self.house.porches[self.selectedPorch - 1].getFirstAndLastNumbers()[1])
                        floors = self.house.porches[self.selectedPorch - 1].getFirstAndLastNumbers()[2]
                        prevRange = prevLast - prevFirst
                        firstflat = str(int(prevLast) + 1)
                        lastflat = str(int(prevLast) + 1 + prevRange)
                else: # если уже есть предыдущие подъезды:
                    firstflat, lastflat, floors = self.porch.getFirstAndLastNumbers()
                text_size = (None, self.counterHeight)

                grid.add_widget(Label(text="Квартир:", halign=align, valign=align, color=self.standardTextColor,
                                      text_size=text_size))
                b1 = BoxLayout()
                b1.add_widget(Label(text="c", color=self.standardTextColor))
                a1 = AnchorLayout(anchor_x="center", anchor_y="center")
                self.flatRangeStart = MyTextInput(text=firstflat, multiline=False, size_hint_y=None, size_hint_x=None,
                                                height=self.standardTextHeight, width=self.counterHeight*.6,
                                                input_type="number", shrink=False)
                a1.add_widget(self.flatRangeStart)
                b1.add_widget(a1)
                b1.add_widget(Label(text="по", color=self.standardTextColor))
                a2 = AnchorLayout(anchor_x="center", anchor_y="center")
                self.flatRangeEnd = MyTextInput(text=lastflat, multiline=False, size_hint_y=None, size_hint_x=None,
                                              height=self.standardTextHeight, width=self.counterHeight*.6,
                                              input_type="number", shrink=False)
                a2.add_widget(self.flatRangeEnd)

                b1.add_widget(a2)
                grid.add_widget(b1)
                grid.add_widget(Label(text="Этажей:", halign=align, valign=align, color=self.standardTextColor,
                                      text_size=text_size))
                self.floors = Counter(text=floors, size_hint=(.7, .5), fixed=True, shrink=False)
                grid.add_widget(self.floors)
                grid.add_widget(Label(text="Номер 1-го\nэтажа:", halign=align, valign=align, color=self.standardTextColor,
                                      text_size=text_size))
                self.floor1 = Counter(text=str(self.porch.floor1), size_hint=(.7, .5), fixed=True, shrink=False)
                grid.add_widget(self.floor1)
                grid.add_widget(Widget())
                grid.add_widget(self.flatListButton())
                a.add_widget(grid)
                self.mainList.add_widget(a)

            else: # универсальный участок
                self.createInputBox(
                    title="Новые дома",
                    message="Введите номер дома (или другого объекта):",
                    checkbox="Массовое добавление",
                    active=False,
                    hint="1 / 1а / красный дом"
                )

                self.mainList.add_widget(self.flatListButton())

        # Формы добавления

        elif self.displayed.form == "ter": # добавление участка
            self.detailsButton.disabled = True
            self.displayed.form = "createNewHouse"
            self.createInputBox(
                title="Новый участок",
                checkbox="Многоквартирный дом",
                active=True,
                message="Введите адрес участка:",
                hint="Пушкина, 30"
            )

        elif self.displayed.form == "houseView": # добавление подъезда
            self.displayed.form = "createNewPorch"
            if self.house.type == "condo":
                message = "Введите заголовок подъезда:"
                hint = "Номер или описание"
            else:
                message = "Для удобства участок можно разделить на части, или сегменты. Введите название нового сегмента:"
                hint = "1 / южная часть"
            self.createInputBox(
                title="Новый %s" % self.house.getPorchType()[0],
                message=message,
                hint=hint
            )

        elif self.displayed.form == "createNewRecord": # добавление новой записи посещения
            self.displayed.form = "flatView"
            record = self.inputBoxEntry.text.strip()
            self.flat.addRecord(record)
            self.processReportCounters()
            utils.save()
            self.flatView()

        # Формы сохранения

        elif self.displayed.form == "createNewHouse":  # сохранение нового участка
            self.displayed.form = "ter"
            newTer = self.inputBoxEntry.text
            condo = self.checkbox.active
            if newTer == "":
                self.inputBoxText.text = "Не сработало, попробуйте еще раз."
            else:
                for house in utils.houses:
                    if newTer.upper().strip() == house.title.upper().strip():
                        #self.inputBoxText.text = "Уже есть участок с таким названием, выберите другое!"
                        self.popup("Уже есть участок с таким названием, выберите другое!")
                        self.terPressed()
                        self.positivePressed()
                        break
                else:
                    utils.addHouse(utils.houses, newTer, condo)
                    utils.log("Создан участок «%s»" % newTer.upper())
                    utils.save()
                    self.terPressed()

        elif self.displayed.form == "createNewPorch":  # сохранение нового подъезда
            self.displayed.form = "houseView"
            newPorch = self.inputBoxEntry.text
            if newPorch == None:
                self.houseView()
                self.updateList()
            elif newPorch == "":
                self.inputBoxText.text = "Не сработало, попробуйте еще раз."
            else:
                for porch in self.house.porches:
                    if newPorch.strip() == porch.title:
                        self.popup(f"Уже есть {self.house.getPorchType()[0]} с таким названием, выберите другое!")
                        self.houseView()
                        self.positivePressed()
                        break
                else:
                    self.house.addPorch(newPorch, self.house.getPorchType()[0])
                    utils.save()
                    self.houseView()

        elif self.displayed.form == "createNewFlat": # сохранение формы квартир
            self.displayed.form = "porchView"
            if self.house.type == "condo": # многоквартирный подъезд
                try:
                    start = int(self.flatRangeStart.text.strip())
                    finish = int(self.flatRangeEnd.text.strip())
                    floors = int(self.floors.get())
                    f1 = int(self.floor1.get())
                    if start > finish or floors < 1:
                        5 / 0
                except:
                    self.popup(title="Что-то не сработало",
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

            else: # сохранение домов в сегменте универсального участка
                addFlat = self.inputBoxEntry.text.strip()
                if self.checkbox.active == True:
                    addFlat2 = self.inputBoxEntry2.text.strip()
                if self.checkbox.active == False:
                    if not "." in addFlat and not "," in addFlat:
                        self.porch.addFlat("+" + addFlat)
                        utils.save()
                        self.porchView()
                    else:
                        self.popup("В названии не допускаются точки и запятые!")
                        self.porchView()
                        self.positivePressed()
                else:
                    try:
                        if int(addFlat) > int(addFlat2):
                            5/0
                        self.porch.addFlats("+%d-%d" % (int(addFlat), int(addFlat2)))
                    except:
                        self.popup("Оба значения должны содержать числа, первое должно быть не больше второго!")
                        def __repeat(*args):
                            self.porchView()
                            self.positivePressed()
                            self.checkbox.active = True
                        Clock.schedule_once(__repeat, 0.5)
                    else:
                        utils.save()
                        self.porchView()

        elif self.displayed.form == "recordView":  # сохранение существующей записи посещения
            self.displayed.form = "flatView"
            newRec = self.inputBoxEntry.text.strip()
            self.flat.editRecord(self.selectedRecord, newRec)
            utils.save()
            self.flatView()

        elif self.displayed.form == "createNewCon":  # сохранение нового контакта
            self.displayed.form = "con"
            newContact = self.inputBoxEntry.text.strip()
            if self.inputBoxEntry.text.strip != "":
                utils.addHouse(utils.resources[1], "", "virtual")  # создается новый виртуальный дом
                utils.resources[1][len(utils.resources[1]) - 1].addPorch(input="virtual", type="virtual")
                utils.resources[1][len(utils.resources[1]) - 1].porches[0].addFlat("+" + newContact, virtual=True)
                utils.resources[1][len(utils.resources[1]) - 1].porches[0].flats[0].status = "1"
                utils.log("Создан контакт %s" % utils.resources[1][len(utils.resources[1]) - 1].porches[0].flats[
                    0].getName())
                utils.save()
                self.conPressed()

        # Заметки

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

        elif self.displayed.form == "noteForFlat": # заметка квартиры/контакта
            self.displayed.form = "flatView"
            self.flat.editNote(self.inputBoxEntry.text.strip())
            utils.save()
            if self.popupEntryPoint == 0:
                self.flatView()
            else:
                self.porchView()

        elif self.displayed.form == "noteGlobal":  # глобальная заметка
            self.displayed.form = "ter"
            utils.resources[0][0] = self.inputBoxEntry.text.strip()
            utils.save()
            self.terPressed()

        # Детали

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
                self.popup("Уже есть участок с таким названием!")
                return

            newDate = self.multipleBoxEntries[1].text.strip()
            if utils.checkDate(newDate)==True:
                self.house.date = newDate
                utils.save()
                self.houseView()
            else:
                self.detailsPressed()
                self.multipleBoxEntries[1].text = newDate
                self.popup("Дата должна быть в формате ГГГГ-ММ-ДД!\n\nНапример: 2023-03-25.")
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
                self.popup(f"Уже есть {self.porch.type[:7]} с таким названием!")

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
                    self.popup("Уже есть дом с таким названием!")
            if success == True:
                utils.save()
                if self.popupEntryPoint == 0:
                    self.flatView()
                else:
                    self.popupEntryPoint = 0
                    self.porchView()

    def neutralPressed(self, instance=None, value=None):
        self.showSlider = False
        self.sliderToggle()

        if self.displayed.form == "porchView":
            if self.porch.floors() == True:
                self.porch.flatsLayout = "н"
            elif self.porch.floors() == False:
                self.porch.flatsLayout = self.porch.type[7:] # определение этажей по цифре в типе подъезда
                if self.porch.flatsLayout == "":
                    self.popup("Для этого подъезда еще не задавались этажи. Задайте их в разделе «Квартиры».")
            utils.save()
            self.porchView()

        if self.displayed.form == "houseView":
            #plyer.maps.route(self.house.title)
            #return
            try:
                address = f"google.navigation:q={self.house.title}"
                intent = Intent(Intent.ACTION_VIEW, Uri.parse(address))
                mActivity.startActivity(intent)
            except:
                webbrowser.open(f"https://www.google.com/maps/place/{self.house.title}")

        elif icon("icon-phone-squared") in instance.text:
            if self.platform == "mobile":
                plyer.call.makecall(tel=self.flat.phone)
            else:
                Clipboard.copy(self.flat.phone)
                self.popup("Номер телефона %s скопирован в буфер обмена." % self.flat.phone)

    # Действия других кнопок

    def terPressed(self, instance=""):
        self.contactsEntryPoint = 0
        self.searchEntryPoint = 0

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
                interested = f" [color={self.interestColor}][b]%d[/b][/color] " % house.getHouseStats()[1]
            else:
                interested = " "

            if house.due() == True:
                houseDue = "[color=F4CA16]" + icon("icon-attention")+" [/color]"
            else:
                houseDue = ""
            if house.type == "condo":
                listIcon = icon('icon-building-filled')
            else:
                listIcon = icon('icon-home-1')

            housesList.append( f"{listIcon} {house.title} ({utils.shortenDate(house.date)}) " +\
                               f"[i]{int(house.getProgress()[0] * 100)}%[/i]{interested}{houseDue}")

        if len(housesList) == 0:
            housesList.append("Создайте свой первый участок")

        if utils.resources[0][0].strip() != "":
            note = icon("icon-sticky-note") + " Заметка"
        else:
            note = icon("icon-sticky-note-o") + " Заметка"

        self.displayed = Feed(  # display list of houses and options
            title="Участки (%d)" % len(utils.houses),
            message="Список участков:",
            options=housesList,
            form="ter",
            sort=icon("icon-sort-alt-up"),
            note=note,
            positive=icon("icon-plus-circled-1") + " Новый участок",
            negative="",
            back=False
        )
        if instance != None:
            self.stack.insert(0, self.displayed.form)
        self.updateList()

    def conPressed(self, instance=None):

        self.contactsEntryPoint = 1
        self.searchEntryPoint = 0
        self.showSlider = False
        self.sliderToggle()
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
        elif utils.settings[0][4] == "з":
            self.allcontacts.sort(key=lambda x: x[11], reverse=True)  # by note

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
                phone = "%s\u00A0%s " % (icon("icon-phone-1"), self.allcontacts[i][9])  # phone
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
                note = icon("icon-sticky-note") + "\u00A0" + self.allcontacts[i][11]
            else:
                note = ""

            if self.allcontacts[i][1][1]=="0":
                color = "008ABA"
            elif self.allcontacts[i][1][1]=="1":
                color = "00BD80"
            elif self.allcontacts[i][1][1]=="2":
                color = "4C8075"
            elif self.allcontacts[i][1][1]=="3":
                color = "875EC2"
            elif self.allcontacts[i][1][1]=="4":
                color = "804538"
            else:#elif x[16]=="5":
                color = "CF3D2B"

            listIcon = f"[color={color}]" + icon("icon-user-1") + "[/color]"
            options.append(
                "%s%s %s %s%s%s%s" % (
                    self.allcontacts[i][1],
                    listIcon,
                    self.allcontacts[i][0],
                    address,
                    appointment,
                    phone,
                    note,
                )
            )

        if len(options) == 0:
            options.append("Здесь будут отображаться жильцы со всех участков и отдельные контакты, созданные вами.")

        if utils.resources[0][0].strip() != "":
            note = icon("icon-sticky-note") + " Заметка"
        else:
            note = icon("icon-sticky-note-o") + " Заметка"

        self.displayed = Feed(
            form="con",
            title="Контакты (%d)" % len(self.allcontacts),
            message="Список контактов:",
            options=options,
            note=note,
            sort=icon("icon-sort-alt-up"),
            positive=icon("icon-plus-circled-1") + " Новый контакт",
            negative="",
            back=False
        )
        if instance != None:
            self.stack.insert(0, self.displayed.form)
        self.updateList()

        if len(options) >= 10:
            try:  # пытаемся всегда вернуться на последний контакт
                self.scroll.scroll_to(widget=self.btn[self.clickedBtnIndex], padding=0, animate=False)
            except:
                pass

    def repPressed(self, instance=None):

        self.stack.insert(0, self.stack[0]) # дублирование последнего шага стека, чтобы предотвратить уход со страницы
        self.counterChanged = False
        self.backButton.disabled = False
        self.neutral.disabled = True
        self.neutral.text = ""
        self.sortButton.disabled = True
        self.sortButton.text = ""
        self.showSlider = False
        self.sliderToggle()
        self.note.text = icon("icon-history") + " Журнал"
        self.displayed.form = "rep"
        self.pageTitle.text = "Отчет"
        self.detailsButton.disabled = True
        self.detailsButton.text = ""
        self.positive.text = self.button["save"]
        self.negative.text = self.button["cancel"]
        self.negative.disabled = False

        self.reportPanel = TabbedPanel(background_color=self.globalBGColor0, background_image="")
        tab1 = TTab(text=utils.monthName()[0])
        tab2 = TTab(text=utils.monthName()[2])
        tab3 = TTab(text="Служ. год")

        self.pageTitle.text = "Отчет %s" % self.rep.getCurrentHours()[2]

        text_size = (Window.size[0]/3, None)

        self.mainList.clear_widgets()
        a = AnchorLayout(anchor_x="center", anchor_y="center")
        report = GridLayout(cols=2, rows=7, spacing=self.spacing, padding=self.padding, pos_hint={"center_x": .7})

        report.add_widget(Label(text="Публикации", halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.placements = Counter(text = str(self.rep.placements), fixed=1, shrink=False)
        report.add_widget(self.placements)

        report.add_widget(Label(text="Видео", halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.video = Counter(text=str(self.rep.videos), fixed=1, shrink=False)
        report.add_widget(self.video)

        report.add_widget(Label(text="Часы", halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.hours = Counter(picker="Сколько добавить к времени служения?", type="time",
                             text=utils.timeFloatToHHMM(self.rep.hours), fixed=1, shrink=False)
        report.add_widget(self.hours)

        if utils.settings[0][2]==1:
            report.add_widget(Label(text="Кредит (итого с часами %s)" % self.rep.getCurrentHours()[0], markup=True,
                                    halign="center", valign="center", text_size = text_size, color=self.standardTextColor))
            self.credit = Counter(picker="Сколько добавить к времени кредита?", type="time",
                                  text=utils.timeFloatToHHMM(self.rep.credit), fixed=1, mode="pan")
            report.add_widget(self.credit)

        report.add_widget(Label(text="Повторные посещения", halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.returns = Counter(text = str(self.rep.returns), fixed=1, mode="pan")
        report.add_widget(self.returns)

        report.add_widget(Label(text="Изучения", halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.studies = Counter(text = str(self.rep.studies), fixed=1, mode="pan")
        report.add_widget(self.studies)

        a.add_widget(report)
        tab1.content = a
        self.reportPanel.add_widget(tab1)

        # Вторая вкладка: отчет прошлого месяца

        report2 = AnchorLayout(anchor_x="center", anchor_y="center")

        self.lastRepHint = "\n\n" + icon("icon-share-squared") + " Отправить"

        if self.rep.getLastMonthReport()[0] == "":
            rep = "Здесь будет ваш отчет за\nтекущий месяц, когда\nон закончится.\n"
        else:
            rep = self.rep.getLastMonthReport()[0]
        self.btnRep = RButton(text=rep+self.lastRepHint, halign="left",
                              size=(Window.size[0]*.7, Window.size[1]*.5), size_hint_x=.7, size_hint_y=.5)
        if self.orientation == "h":
            self.btnRep.size_hint_x = .5
            self.btnRep.size_hint_y = .8
        self.btnRep.bind(on_release=self.sendLastMonthReport)
        report2.add_widget(self.btnRep)
        tab2.content = report2
        self.reportPanel.add_widget(tab2)
        self.reportPanel.do_default_tab = False
        self.mainList.add_widget(self.reportPanel)

        # Третья вкладка: служебный год

        if self.orientation == "v":
            x = .5
            y = .9
            k = .85
            spacing = self.spacing
            row_force_default = False
        else:
            x = .3
            y = 1
            k = .75
            spacing = 0
            row_force_default = True
        width = self.standardTextWidth
        height = self.standardTextHeight * k

        report3 = AnchorLayout(anchor_x="center", anchor_y="center")

        b3 = BoxLayout(spacing=spacing, padding=self.padding)
        mGrid = GridLayout(rows=12, cols=2, size_hint=(x, y), padding=self.padding, spacing=self.spacing,
                            row_force_default = row_force_default,
                            col_default_width=width, row_default_height = height,
                            pos_hint={"center_y": .5})
        self.months = []

        for i, month in zip(range(12),
                            ["сентябрь", "октябрь", "ноябрь", "декабрь", "январь", "февраль", "март", "апрель",
                             "май", "июнь", "июль", "август"]):
            mGrid.add_widget(Label(text=month[:3], halign="center", valign="center", width=width, height=height,
                                   text_size=(width, height), pos_hint={"center_y": .5},
                                   color=self.standardTextColor))
            if utils.settings[4][i] != None:
                text = str(utils.settings[4][i])
            else:
                text = ""
            if i<6:
                mode = ""
            else:
                mode = "pan"
            self.months.append(
                MyTextInput(text=text, multiline=False, input_type="number", width=self.standardTextWidth * 1.1,
                            height=height, size_hint_x=None, size_hint_y=None, mode=mode, shrink=False))
            mGrid.add_widget(self.months[i])
            self.analyticsMessage = Label(markup=True, color=self.standardTextColor, valign="center",
                                          text_size=(Window.size[0] / 2, self.mainList.size[1]),
                                          height=self.mainList.size[1],
                                          width=Window.size[0] / 2, pos_hint={"center_y": .5})
            self.months[i].bind(focus=self.recalcServiceYear)

        self.recalcServiceYear()

        b3.add_widget(mGrid)
        b3.add_widget(self.analyticsMessage)
        report3.add_widget(b3)
        tab3.content = report3
        self.reportPanel.add_widget(tab3)

        if self.firstRunFlag == True:
            self.popupForm = "pioneerNorm"
            self.popup(title="Rocket Ministry",
                       message="Вы общий пионер? Тогда мы пропишем месячную норму часов. Ее можно ввести самостоятельно в настройках.",
                       options=[self.button["yes"], self.button["no"]])
            self.firstRunFlag = False

    def settingsPressed(self, instance=None):
        """ Настройки """

        self.stack.insert(0, self.stack[0]) # дублирование последнего шага стека, чтобы предотвратить уход со страницы
        self.displayed.form = "set"
        self.backButton.disabled = False
        self.showSlider = False
        self.sliderToggle()
        self.mainList.clear_widgets()
        box = BoxLayout(orientation="vertical")
        self.settingsPanel = TabbedPanel(background_color=self.globalBGColor0)

        self.createMultipleInputBox(
            form=box,
            title="Настройки",
            note=icon("icon-help-circled") + " Помощь",
            details="",
            options=[
                "Месячная норма часов",
                "{}«Нет дома» одним кликом", # {} = вместо строки ввода должна быть галочка
                "{}Переносить минуты на следующий месяц",
                "<>Цвет отказа", # выбор цвета
                "{}Цвет отказа всегда ставит запись «отказ»",
                "{}Кредит часов",
                "{}Быстрый ввод телефона",
                "{}Уведомление при запуске таймера",
            ],
            defaults=[
                utils.settings[0][3],   # норма часов
                utils.settings[0][13],  # нет дома
                utils.settings[0][15],  # переносить минуты
                utils.settings[0][18],  # цвет отказа
                utils.settings[0][10],  # автоотказ
                utils.settings[0][2],   # кредит часов
                utils.settings[0][20],  # показывать телефон
                utils.settings[0][0]    # уведомление при запуске таймера
            ],
            multilines=[False, False, False, False, False, False, False, False]
        )

        """ Также заняты настройки:
        utils.settings[0][1] - позиция подъезда в окне
        utils.settings[0][4] - сортировка контактов
        utils.settings[0][7] - масштабирование подъезда
        utils.settings[0][8] - значение слайдера        
        
        """

        # Первая вкладка: настройки

        tab1 = TTab(text="Настройки")
        tab1.content = box
        self.settingsPanel.add_widget(tab1)

        # Вторая вкладка: работа с данными

        text_size = [Window.size[0]/2.5, Window.size[1]/2.5]
        tab2 = TTab(text="Данные")
        g = GridLayout(rows=2, cols=2, spacing="10dp", padding=[30, 30, 30, 30])

        exportEmail = RButton(text=icon("icon-share-1") + " Экспорт", size=text_size)
        def __export(instance):
            if self.platform == "mobile":
                utils.share(email=True)
            else:
                utils.share(doc=True)
        exportEmail.bind(on_release=__export)
        g.add_widget(exportEmail)

        importBtn = RButton(text=icon("icon-download-1") + " Импорт", size=text_size)
        importBtn.bind(on_release=self.importDB)
        g.add_widget(importBtn)

        if self.platform == "desktop":
            g.rows += 1
            importFile = RButton(text=icon("icon-folder-open") + " Импорт из файла", size=text_size)

            def __importFile(instance):
                #from tkinter import filedialog
                #file = filedialog.askopenfilename()
                def __handleSelection(selection):
                    file = selection[0]
                    self.importDB(file=file)
                plyer.filechooser.open_file(on_selection=__handleSelection)

            importFile.bind(on_release=__importFile)
            g.add_widget(importFile)

        restoreBtn = RButton(text=icon("icon-upload-1") + " Восстановление", size=text_size)
        def __restore(instance):
            result = utils.backupRestore(restoreWorking=True, silent=False)
            if result == True:
                self.rep = report.Report()
                utils.save()
        restoreBtn.bind(on_release=__restore)
        g.add_widget(restoreBtn)

        clearBtn = RButton(text=icon("icon-trash-1")+" Очистка", size=text_size)
        def __clear(instance):
            self.popup(message="Все пользовательские данные будут полностью удалены из приложения! Вы уверены, что это нужно сделать?",
                       options=[self.button["yes"], self.button["no"]])
            self.popupForm = "clearData"
        clearBtn.bind(on_release=__clear)
        g.add_widget(clearBtn)

        tab2.content = g
        self.settingsPanel.add_widget(tab2)

        # Третья вкладка: о программе

        tab3 = TTab(text="О программе")
        a = AnchorLayout(anchor_x="center", anchor_y="center")
        box3 = BoxLayout(orientation="vertical")#, size_hint=(.9, .5))
        aboutBtn = Button(text=
                            f"[color={self.titleColor2}][b]Rocket Ministry {utils.Version}[/b][/color]\n\n" +\
                            "Универсальный органайзер\n\n" + \
                            #"Последнее изменение базы данных:\n%s\n\n" % utils.getDBCreatedTime() + \
                            "Официальный Telegram-канал: [color=36ACD8][u]RocketMinistry[/u] " + icon("icon-telegram") + "[/color]",
            markup=True, background_color=self.globalBGColor,# text_size=(Window.size[0]*.9, Window.size[1]*.5),
            halign="left", valign="center", color=self.standardTextColor, background_normal="", background_down="")#self.buttonPressedBG)
        def __telegram(instance):
            webbrowser.open("https://t.me/rocketministry")
        aboutBtn.bind(on_release=__telegram)
        a.add_widget(aboutBtn)
        box3.add_widget(a)

        tab3.content = a
        self.settingsPanel.add_widget(tab3)
        self.settingsPanel.do_default_tab = False
        self.mainList.add_widget(self.settingsPanel)

    def searchPressed(self, instance=None):
        self.popupForm = "search"
        self.popup(title="Поиск")

    def find(self, instance=None):
        self.contactsEntryPoint = 0
        allContacts = self.getContacts(forSearch=True)
        self.searchResults = []
        for i in range(len(allContacts)):  # start search in flats/contacts
            found = False
            if self.searchQuery in allContacts[i][2].lower() or self.searchQuery in allContacts[i][2].lower() or self.searchQuery in \
                    allContacts[i][3].lower() or self.searchQuery in allContacts[i][8].lower() or self.searchQuery in \
                    allContacts[i][10].lower() or self.searchQuery in allContacts[i][11].lower() or self.searchQuery in \
                    allContacts[i][12].lower() or self.searchQuery in allContacts[i][13].lower() or\
                    self.searchQuery in allContacts[i][9].lower():
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

        if utils.resources[0][0].strip() != "":
            note = icon("icon-sticky-note") + " Заметка"
        else:
            note = icon("icon-sticky-note-o") + " Заметка"

        self.displayed = Feed(
            form="search",
            title="Поиск по запросу \"%s\"" % self.searchQuery,
            message="Результаты:",
            options=options,
            note=note,
            back=False
        )
        if instance != None:
            self.stack.insert(0, self.displayed.form)
        self.mypopup.dismiss()
        self.updateList()

        if len(options) >= 10:
            try:  # пытаемся всегда вернуться в последний элемент поиска
                self.scroll.scroll_to(widget=self.btn[self.clickedBtnIndex], padding=0, animate=False)
            except:
                pass

    # Функции по обработке участков

    def houseView(self, house=None, selectedHouse=None, instance=None):
        """ Вид участка - список подъездов """
        if "virtual" in self.house.type: # страховка от захода в виртуальный дом
            if self.contactsEntryPoint == 1:
                self.conPressed()
            elif self.searchEntryPoint == 1:
                self.find(instance=instance)
            return

        self.mainListSize1 = self.mainList.size[1] # высота окна замеряется здесь для вида подъезда, потому что иначе она не успевает пересчитываться после убирания клавиатуры

        if house == None:
            house = self.house
        if selectedHouse != None:
            house = utils.houses[selectedHouse]

        if house.due() == True:
            due="\nУчасток просрочен!"
        else:
            due=""

        if house.note.strip() != "":
            note = icon("icon-sticky-note") + " Заметка"
        else:
            note = icon("icon-sticky-note-o") + " Заметка"

        self.displayed = Feed(
            form="houseView",
            title=house.title+due,
            options=house.showPorches(),
            note=note,
            details=self.button["details"],
            positive=icon("icon-plus-circled-1") + " Новый " + house.getPorchType()[0],
            neutral=icon("icon-direction"),
            negative=self.button["exit"]
        )
        if instance != None:
            self.stack.insert(0, self.displayed.form)
        self.updateList()

    def porchView(self, porch=None, selectedPorch=None, instance=None):
        """ Вид подъезда - список квартир или этажей """
        if "virtual" in self.porch.type: # страховка от захода в виртуальный подъезд
            if self.contactsEntryPoint == 1:
                self.conPressed()
            elif self.searchEntryPoint == 1:
                self.find(instance=instance)
            return

        if porch == None:
            porch = self.porch
        if selectedPorch != None:
            porch = self.house[selectedPorch]

        if "подъезд" in porch.type:
            positive = " Квартиры"
        else:
            positive = " Дома"

        if "подъезд" in self.porch.type:
            segment = ", под. " + self.porch.title
        else:
            segment = ", " + self.porch.title

        options = porch.showFlats()

        if self.house.type != "condo":
            neutral = ""
        elif self.porch.floors() == True:
            neutral = icon("icon-th-1")
        elif not "подъезд" in self.porch.type:  # Отрисовка нижних клавиш (positive, view, neutral)
            neutral = ""
        else:
            neutral = icon("icon-menu")

        if self.porch.floors() == True:
            sort = icon("icon-resize-full-alt-1")
        else:
            sort = icon("icon-sort-alt-up")

        if porch.note.strip() != "":
            note = icon("icon-sticky-note") + " Заметка"
        else:
            note = icon("icon-sticky-note-o") + " Заметка"

        self.displayed = Feed(
            title=self.house.title+segment,
            options=options,
            form="porchView",
            note=note,
            sort=sort,
            details=self.button["details"],
            positive=icon("icon-plus-circled-1") + positive,
            neutral=neutral,
            negative=self.button["exit"]
        )
        if instance != None:
            self.stack.insert(0, self.displayed.form)
        self.updateList()

        if len(self.porch.flats) == 0: # если нет квартир, сразу форма создания
            self.positivePressed()
            return

        if self.porch.floors() == False and len(self.porch.flats) >= 10:
            try: # пытаемся всегда вернуться в последнюю квартиру
                self.scroll.scroll_to(widget=self.btn[self.clickedBtnIndex], padding=0, animate=False)
            except:
                pass

    def flatView(self, flat=None, selectedFlat=None, call=True, instance=None):
        """ Вид квартиры - список записей посещения """
        if flat == None:
            flat = self.flat
        if selectedFlat != None:
            flat = self.porch[selectedFlat]

        if flat.number == "virtual":  # прячем номера отдельных контактов
            number = " "
        else:
            number = flat.number + " "
        if "подъезд" in self.porch.type:
            flatPrefix = "кв. "
        else:
            flatPrefix = ""
        self.flatTitle = (flatPrefix + number + flat.getName()).strip()
        if self.flat.phone != "":  # добавляем кнопку телефона
            self.neutral.disabled = False
            neutral = icon("icon-phone-squared")
        else:
            self.neutral.disabled = True
            neutral = ""
        records = flat.showRecords()

        if flat.note.strip() != "":
            note = icon("icon-sticky-note") + " Заметка"
        else:
            note = icon("icon-sticky-note-o") + " Заметка"

        self.displayed = Feed(
            title=self.flatTitle,
            message="Список посещений:",
            options=records,
            form="flatView",
            note=note,
            details=self.button["details"],
            positive=icon("icon-plus-circled-1") + " Новое посещение",
            neutral=neutral,
            negative=self.button["exit"]
        )

        if call == False and self.flat.status == "": # всплывающее окно первого посещения
            self.popup(firstCall=True)

        else:
            if len(self.flat.records) == 0:  # если нет посещения, открывается специальное окно первого посещения

                self.scrollWidget.clear_widgets()
                self.createMultipleInputBox(
                    title=self.flatTitle + " — первое посещение",
                    options=["Имя и (или) описание человека:", "О чем говорили:"],
                    defaults=[self.flat.getName(), ""],
                    multilines=[False, True],
                    note=note,
                    allowStackDuplicate=False,
                    addCheckBoxes=True
                )
                if instance != None and "Интерес" in instance.text:
                    self.multipleBoxEntries[0].focus = True  # принудительная фокусировка ввода на первом тексте
            else:
                if instance != None:
                    self.stack.insert(0, self.displayed.form)
                self.updateList()

            self.colorBtn = []
            for i, status in zip(range(6), ["0", "1", "2", "3", "4", "5"]):
                self.colorBtn.append(ColorStatusButton(status))
                if self.flat.getStatus()[0][1] == status:
                    self.colorBtn[i].text = icon("icon-dot-circled")
                    self.colorBtn[i].markup = True
            colorBox = BoxLayout(size_hint_y=None, height=self.mainList.size[0]/6,
                                 spacing=self.spacing*4, padding=(self.padding*3, self.padding))
            if self.orientation == "h":
                colorBox.height = self.standardTextHeight
            colorBox.add_widget(self.colorBtn[1])
            colorBox.add_widget(self.colorBtn[2])
            colorBox.add_widget(self.colorBtn[3])
            colorBox.add_widget(self.colorBtn[4])
            colorBox.add_widget(self.colorBtn[0])
            colorBox.add_widget(self.colorBtn[5])
            self.mainList.add_widget(colorBox)

            if len(records) >= 10:
                try:  # пытаемся всегда вернуться на последнюю запись посещения
                    self.scroll.scroll_to(widget=self.btn[self.clickedBtnIndex], padding=0, animate=False)
                except:
                    pass

    def recordView(self, instance=None):
        self.displayed.form = "recordView"
        if self.flat.note.strip() != "":
            note = icon("icon-sticky-note") + " Заметка"
        else:
            note = icon("icon-sticky-note-o") + " Заметка"
        self.createInputBox(
            title = f"{self.flatTitle} – посещение от {self.record.date}",
            message = "О чем говорили:",
            default = self.record.title,
            multiline=True,
            note=note
        )

    # Диалоговые окна

    def createReportBoxes(self, addReturn=False):
        """ Создает галочки для отчета, возвращает экземпляр с боксом"""

        self.reportBoxesAL.clear_widgets()
        grid2 = GridLayout(rows=3, cols=2, size_hint_y=None)
        if addReturn == True:
            grid2.cols += 1
        grid2.add_widget(Label(text="публикации", halign="center", valign="center", color=self.standardTextColor))
        grid2.add_widget(Label(text="видео", halign="center", valign="center", color=self.standardTextColor))
        if addReturn == True:
            grid2.add_widget(Label(text="повторное", halign="center", valign="center", color=self.standardTextColor))
        self.addPlacement = Counter(text="0", fixed=True)
        grid2.add_widget(self.addPlacement)
        self.addVideo = Counter(text="0", fixed=True)
        grid2.add_widget(self.addVideo)
        if addReturn == True:
            self.addReturn = CheckBox(active=True, color=self.titleColor)
            grid2.add_widget(self.addReturn)
        grid2.height = self.counterHeight + self.standardTextHeight
        self.reportBoxesAL.add_widget(grid2)
        self.mainList.add_widget(self.reportBoxesAL)

    def createInputBox(self, title="", message="", default="", hint="", checkbox=None, active=True, input=True,
                       note=None, details=None, multiline=False, addCheckBoxes=False):
        """ Форма ввода данных с одним полем """
        self.stack.insert(0, self.stack[0]) # дублирование последнего шага стека, чтобы предотвратить уход со страницы
        self.mainList.clear_widgets()
        self.pageTitle.text = title
        self.positive.text = self.button["save"]
        self.negative.text = self.button["cancel"]
        self.negative.disabled = False
        if self.displayed.form != "flatView" and self.displayed.form != "flatDetails" and \
                self.displayed.form != "noteForFlat" and self.displayed.form != "createNewRecord" and \
                self.displayed.form != "recordView":
            self.neutral.disabled = True
        elif self.flat.phone != "":
            self.neutral.disabled = False
        self.sortButton.disabled = True
        self.sortButton.text = ""
        self.backButton.disabled = False
        if note != None:
            self.note.text = note
        if details != None:
            self.detailsButton.text = details
        height = self.standardTextHeight
        pos_hint = {"top": 1}
        a = AnchorLayout(anchor_x="center", anchor_y="top")
        grid = GridLayout(rows=5, cols=1, spacing=self.spacing, padding=self.padding*2, size_hint_y=None)

        if multiline == False:
            size_hint_y = None
            grid.size_hint_y = None#.5
            grid.height = self.mainList.size[1] / 2
        else:
            size_hint_y = 1
            grid.size_hint_y = 1

        self.inputBoxText = Label(text=message, color=self.standardTextColor, valign="center",
                                  halign="center", text_size = (Window.size[0]*.9, self.mainList.size[1] / 7),
                                  height=self.mainList.size[1] / 7,
                                  size_hint_y=None)
        grid.add_widget(self.inputBoxText)

        if input == True:
            textbox = BoxLayout(size_hint_y=None, height=self.mainList.size[1]*.25, padding=(0, self.padding))
            self.inputBoxEntry = MyTextInput(multiline=multiline, hint_text=hint, size_hint_y=size_hint_y,
                                             height=height, pos_hint=pos_hint)
            textbox.add_widget(self.inputBoxEntry)
            grid.add_widget(textbox)

        if checkbox != None: # если заказана галочка, добавляем
            b = BoxLayout(orientation="vertical", spacing=self.spacing*2)
            self.checkbox = CheckBox(active=active, color=self.titleColor)
            b.add_widget(self.checkbox)
            def __on_checkbox_active(checkbox, value): # что происходит при активированной галочке
                if self.displayed.form == "createNewHouse":
                    if value == 1:
                        self.inputBoxText.text = message
                        self.inputBoxEntry.hint_text = hint
                    else:
                        self.inputBoxText.text = "Введите название участка:"
                        self.inputBoxEntry.hint_text = "ул. Радужная"

                elif self.displayed.form == "createNewFlat":
                    if value == 1:
                        self.inputBoxText.text = "Введите первый и последний номера добавляемого диапазона:"
                        filled = self.inputBoxEntry.text
                        textbox.remove_widget(self.inputBoxEntry)
                        height = self.standardTextHeight
                        self.inputBoxEntry = MyTextInput(text=filled, hint_text = "От", multiline=multiline, height=height,
                                                       size_hint_x=Window.size[0]/2, size_hint_y=None, pos_hint=pos_hint,
                                                       input_type="number")
                        textbox.add_widget(self.inputBoxEntry)
                        self.inputBoxEntry2 = MyTextInput(hint_text = "до", multiline=multiline, height=height,
                                                        size_hint_x=Window.size[0]/2, size_hint_y=None, pos_hint=pos_hint,
                                                        input_type="number")
                        textbox.add_widget(self.inputBoxEntry2)
                    else:
                        self.porchView()
                        self.positivePressed()

            self.checkbox.bind(active=__on_checkbox_active)
            if self.orientation == "v":
                lb = ""
            else:
                lb = "\n\n"
            b.add_widget(Label(text=f"{lb}{checkbox}", color=self.standardTextColor, halign="center", valign="bottom",
                               height=self.standardTextHeight, text_size=(None, self.standardTextHeight)))
            grid.add_widget(b)

        self.inputBoxEntry.text = default
        a.add_widget(grid)
        self.mainList.add_widget(a)

        if "recordView" in self.displayed.form or "note" in self.displayed.form: # добавление корзины
            self.mainList.add_widget(self.bin())
            textbox.size_hint_y = 1
        elif addCheckBoxes == True: # добавляем галочки для нового посещения)
            self.createReportBoxes(addReturn=True)

    def createMultipleInputBox(self, form=None, title=None, options=[], defaults=[], multilines=[],
                               note=None, details=None, allowStackDuplicate=False, addCheckBoxes=False):
        """ Форма ввода данных с несколькими полями """

        if form == None: # по умолчанию вывод делается на mainlist, но можно вручную указать другую форму
            form = self.mainList
        form.clear_widgets()
        if 1:#allowStackDuplicate == True:
            self.stack.insert(0, self.stack[0]) # дублирование последнего шага стека, чтобы предотвратить уход со страницы
        if title != None:
            self.pageTitle.text = title
        self.positive.text = self.button["save"]
        self.negative.text = self.button["cancel"]
        self.negative.disabled = False
        if self.displayed.form != "flatView" and self.displayed.form != "flatDetails" and \
                self.displayed.form != "noteForFlat":
            self.neutral.disabled = True
            self.neutral.text = ""
        elif self.flat.phone != "":
            self.neutral.disabled = False
            self.neutral.text = icon("icon-phone-squared")
        else:
            self.neutral.disabled = True
            self.neutral.text = ""
        self.sortButton.disabled = True
        self.sortButton.text = ""
        self.backButton.disabled = False
        if note != None:
            self.note.text = note
        if details != None:
            self.detailsButton.text = details

        grid = GridLayout(rows=len(options), spacing=self.spacing, padding=self.padding*2, cols=2, pos_hint={"top": 1})
        self.multipleBoxLabels = []
        self.multipleBoxEntries = []

        for row, default, multiline in zip( range(len(options)), defaults, multilines ):
            if "{}" in str(options[row]): # галочка
                text = str(options[row][2:]).strip()
                checkbox = True
                colorSelect = False
            elif "<>" in str(options[row]): # выбор цвета отказа
                text = str(options[row][2:]).strip()
                checkbox = True
                colorSelect = True
            else:
                text = options[row].strip()
                checkbox = False
                colorSelect = False
            if multiline == True:
                y = 1
            else:
                y = None
            if self.displayed.form == "set":
                height = self.mainList.size[1] / len(options)
                labelSize_hint=(1, 1)
                entrySize_hint=(.3, 1)
                text_size = (Window.size[0]*0.66, height)
            else:
                height = self.standardTextHeight
                labelSize_hint = (.5, y)
                entrySize_hint = (.5, y)
                text_size = (Window.size[0]/3, height)

            self.multipleBoxLabels.append(Label(text=text, valign="center", halign="center", size_hint=labelSize_hint,
                                  color = self.standardTextColor, text_size = (Window.size[0]/2, height),
                                                height=height))
            grid.add_widget(self.multipleBoxLabels[row])
            textbox = BoxLayout(size_hint=entrySize_hint, height=height, pos_hint={"center_x": .5})

            if colorSelect == True:
                self.multipleBoxEntries.append(RejectColorSelectButton())
            elif checkbox == False:
                if self.displayed.form == "set" or "Дата взятия" in self.multipleBoxLabels[row].text:
                    input_type = "number"
                else:
                    input_type = "text"
                self.multipleBoxEntries.append(MyTextInput(multiline=multiline, size_hint_x=entrySize_hint[0],
                                                           size_hint_y=entrySize_hint[1],
                                                           input_type = input_type,
                                                           pos_hint={"top": 1}, height=height*.9))
                self.multipleBoxEntries[row].text = str(default)

            else:
                self.multipleBoxEntries.append(CheckBox(active=default, size_hint_x=entrySize_hint[0],
                                                        size_hint_y=entrySize_hint[1], pos_hint = {"top": 1},
                                                        color=self.titleColor))
            textbox.add_widget(self.multipleBoxEntries[row])

            grid.add_widget(textbox)

        if self.displayed.form == "set": # добавляем выбор темы для настроек
            grid.rows += 1
            grid.add_widget(Label(text="Тема интерфейса", valign="center", halign="center", size_hint=labelSize_hint,
                                  color = self.standardTextColor, text_size=text_size))

            tBox = GridLayout(rows=2, cols=2, size_hint=(.5, .7))
            def __changeTheme(instance):
                if instance.color == self.themeDefault[2]:
                    utils.settings[0][5] = "default"
                elif instance.color == self.themePurple[2]:
                    utils.settings[0][5] = "purple"
                elif instance.background_color == self.themeTeal[0]:
                    utils.settings[0][5] = "teal"
                elif instance.background_color == self.themeDark[0]:
                    utils.settings[0][5] = "dark"
                self.positivePressed()
                self.popup("Для смены темы необходим перезапуск программы. Сделать это сейчас?",
                           options=[self.button["yes"], self.button["no"]])
                self.popupForm = "restart"

            bt1 = Button(text=icon("icon-font-1"), markup=True, color=self.themeDefault[2], background_color=self.themeDefault[0],
                         background_normal="", pos_hint={"center_y":.5})
            bt2 = Button(text=icon("icon-font-1"), markup=True, color=self.themePurple[2], background_color=self.themePurple[0],
                         background_normal="", pos_hint={"center_y": .5})
            bt3 = Button(text=icon("icon-font-1"), markup=True, color=self.themeTeal[1], background_color=self.themeTeal[0],
                         background_normal="", pos_hint={"center_y":.5})
            bt4 = Button(text=icon("icon-font-1"), markup=True, color=self.themeDark[1], background_color=self.themeDark[0],
                         background_normal="", pos_hint={"center_y":.5})

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

        if addCheckBoxes == True: # добавляем галочки для нового посещения
            self.createReportBoxes(addReturn=False)
            self.multipleBoxEntries[1].height = self.mainList.size[1]

        elif "Details" in self.displayed.form: # добавление корзины
            while 1:
                if not "flat" in self.displayed.form:
                    self.mainList.add_widget(Widget())
                    self.mainList.add_widget(self.bin())
                    break
                else:
                    if self.contactsEntryPoint == 1 or self.searchEntryPoint == 1:
                        self.mainList.add_widget(Widget())
                        self.mainList.add_widget(self.bin())
                        break
                    elif self.porch.type == "сегмент":
                        self.mainList.add_widget(Widget())
                        self.mainList.add_widget(self.bin())
                        break
                    elif self.displayed.form == "flatDetails" and "подъезд" in self.porch.type and \
                        self.porch.floors() == True:
                            self.mainList.add_widget(Widget())
                            self.mainList.add_widget(self.bin(" Уменьшить этаж"))
                            break
                    elif self.porch.floors() == False:
                        break
                    else:
                        self.mainList.add_widget(Widget())
                        self.mainList.add_widget(self.bin())
                        break

    def bin(self, label=None):
        """Создание корзины. Возвращает объект, который можно привязать к любому виджету - получится корзина"""
        if label == None:
            size = (Window.size[0] / 4, self.standardTextHeight)
            text = icon("icon-trash-1") + " Удалить"
        else:
            size = (Window.size[0] / 2.2, self.standardTextHeight)
            text = icon("icon-right-dir") + " Уменьшить этаж"

        deleteBtn = TableButton(text=text, size_hint_x=None, size_hint_y=None, width=size[0],
                                height=self.standardTextHeight, background_color=self.globalBGColor)
        bin = AnchorLayout(anchor_x="right", anchor_y="top", size_hint_y=None, padding=self.padding,
                           height=self.mainList.size[1]*.2)
        deleteBtn.bind(on_release=self.deletePressed)
        bin.add_widget(deleteBtn)
        return bin

    def flatListButton(self):
        """ Кнопка создания квартир/домов списком"""
        height = self.standardTextHeight
        addList = TableButton(text=icon("icon-doc-text-inv") + " Список", size_hint_x=None, size_hint_y=None,
                              size=(Window.size[0] / 4, self.standardTextHeight),
                              height=height, background_color=self.globalBGColor)
        AL = AnchorLayout(anchor_x="right", anchor_y="center", padding=self.padding)
        addList.bind(on_release=self.addList)
        AL.add_widget(addList)
        return AL

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
                            f].status != utils.settings[0][18] \
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

    def recalcServiceYear(self, instance=None, value=None):
        """ Подсчет статистики служебного года """

        if value == 1:
            return
        for i in range(12):
            month = self.months[i]
            month.text = month.text.strip()
            if utils.ifInt(month.text) == True:
                utils.settings[4][i] = int(month.text)
                if int(month.text) < utils.settings[0][3]:
                    month.background_color = self.getColorForStatus("5")
                elif int(month.text) == utils.settings[0][3]:
                    month.background_color = self.getColorForStatus("0")
                else:
                    month.background_color = self.getColorForStatus("1")
                month.background_color[3] = 0.4
            else:
                utils.settings[4][i] = None
                month.background_color = self.textInputBGColor

        hourSum = 0.0  # total sum of hours
        monthNumber = 0  # months entered
        for i in range(len(utils.settings[4])):
            if utils.settings[4][i] != None:
                hourSum += utils.settings[4][i]
                monthNumber += 1
        yearNorm = float(utils.settings[0][3]) * 12  # other stats
        gap = (12 - monthNumber) * float(utils.settings[0][3]) - (yearNorm - hourSum)
        if monthNumber != 12:
            average = (yearNorm - hourSum) / (12 - monthNumber)  # average
        else:
            average = yearNorm - hourSum
        if gap >= 0:
            gapEmo = icon("icon-smile")
            gapWord = "Запас"
        elif gap < 0:
            gapEmo = icon("icon-frown")
            gapWord = "Отставание"
        else:
            gapEmo = ""
        self.analyticsMessage.text = "[b]Годовые показатели[/b]\n\n" + \
                                     "Месяцев введено: [b]%d[/b]\n\n" % monthNumber + \
                                     "Часов введено: [b]%d[/b]\n\n" % hourSum + \
                                     "Годовая норма¹: [b]%d[/b]\n\n" % yearNorm + \
                                     "Осталось часов: [b]%d[/b]\n\n" % (yearNorm - hourSum) + \
                                     "%s: [b]%d[/b] %s\n\n" % (gapWord, abs(gap), gapEmo) + \
                                     "Среднее за месяц²: [b]%0.f[/b]\n\n" % average + \
                                     "____\n" + \
                                     "¹ Равна 12 * месячная норма (в настройках).\n\n" + \
                                     "² Среднее число часов, которые нужно служить каждый месяц в оставшиеся (не введенные) месяцы."
        utils.save()

    def sendLastMonthReport(self, instance=None):
        """ Отправка отчета прошлого месяца """
        plyer.email.send(subject="Отчет", text=self.rep.getLastMonthReport()[1], create_chooser=True)

    def addList(self, instance):
        """ Добавление квартир списком"""

        if self.orientation == "v":
            size_hint = (.9, .7)
        else:
            size_hint = (.6, .7)
        width = self.mainList.width * size_hint[0]*.9
        #height = self.standardTextHeight * 5
        box = BoxLayout(orientation="vertical", size_hint=(.95, .95), padding=self.padding)
        if "подъезд" in self.porch.type:
            warning = " Но учтите, что это приведет к отключению поэтажного вида подъезда!"
        else:
            warning = ""
        text = MyTextInput(hint_text="Список номеров через запятую", multiline=True, size_hint_y=None,
                           height=self.standardTextHeight * 3, shrink=False)
        box.add_widget(text)
        btnPaste = TButton(text="Вставить из буфера", size_hint_y=None, width=width, height=self.standardTextHeight,
                           background_color=self.textInputBGColor)
        def __paste(instance):
            text.text = Clipboard.paste()
        btnPaste.bind(on_release=__paste)
        box.add_widget(btnPaste)
        description = Label(
            text=f"Здесь можно добавить новые {self.house.getPorchType()[1]} простым списком номеров через запятую.{warning}",
            text_size=(width, None), valign="top")
        box.add_widget(description)
        grid = GridLayout(cols=3, size_hint=(1, None))
        btnSave = RButton(text="Добавить", black=True)
        def __save(instance):
            try:
                flats = text.text.strip()
                last = len(flats)-1
                if utils.ifInt(flats[last]) == False:
                    flats = flats[:last]
                flats = [int(x) for x in flats.split(',')]
            except:
                description.text = "Ошибка ввода. Строка должна представлять собой список любых чисел через запятую. Никакие другие символы не допускаются."
            else:
                if "подъезд" in self.porch.type:
                    self.porch.type = "подъезд"
                    self.porch.flatsLayout = "н"
                for flat in flats:
                    self.porch.addFlat(f"+{flat}")
                utils.save()
                modal.dismiss()
                self.backPressed()
        btnSave.bind(on_release=__save)
        btnClose = RButton(text="Отмена", black=True)
        def __close(instance):
            modal.dismiss()
        btnClose.bind(on_release=__close)
        grid.add_widget(btnSave)
        grid.add_widget(Widget())
        grid.add_widget(btnClose)
        box.add_widget(grid)
        modal = Popup(title="Список", content=box, size_hint=size_hint)
        modal.open()

    def processReportCounters(self):
        report = "{"
        for i in range(int(self.addPlacement.get())):
            report += "б"
            self.rep.placements += 1
        for i in range(int(self.addVideo.get())):
            report += "в"
            self.rep.videos += 1
        try:
            if self.addReturn.active == True:
                report += "п"
                self.rep.returns += 1
            self.addReturn.active = False
        except:
            pass

        self.rep.modify(report)

    def changeColor1(self, instance):
        """ Мигание нажатой кнопки с векторной иконкой - нажатое состояние"""
        instance.color = self.titleColor
        instance.background_color = self.tableColor

    def changeColor2(self, instance):
        """ Мигание нажатой кнопки с векторной иконкой - обычное (отжатое) состояние"""
        instance.color = self.topButtonColor
        instance.background_color = self.globalBGColor

    def keyboardHeight(self, *args):
        """ Возвращает высоту клавиатуры в str"""
        if platform == "android":
            rect = Rect(instantiate=True)
            activity.getWindow().getDecorView().getWindowVisibleDisplayFrame(rect)
            rect.top = 0
            height = activity.getWindowManager().getDefaultDisplay().getHeight() - (rect.bottom - rect.top)
            if height >= 400:
                self.defaultKeyboardHeight = height
            else:
                height = self.defaultKeyboardHeight
            return height
        else:
            #print("Не удалось получить высоту клавиатуры.")
            return self.defaultKeyboardHeight

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
        self.flat.status = utils.settings[0][18] # "0"
        utils.save()
        self.porchView()

    def colorBtnPressed(self, color):
        """ Нажатие на цветной квадрат статуса """

        if len(self.flat.records) == 0:
            if self.multipleBoxEntries[0].text.strip() != "":
                self.flat.updateName(self.multipleBoxEntries[0].text.strip())
            if self.multipleBoxEntries[1].text.strip() != "":
                self.flat.addRecord(self.multipleBoxEntries[1].text.strip())
            self.processReportCounters()

        if color == utils.settings[0][18]:  # отказ
            self.quickReject()
        for i in ["0", "1", "2", "3", "4", "5"]:
            if color == i:
                self.flat.status = i
        if self.contactsEntryPoint == 1:
            self.conPressed()
        elif self.searchEntryPoint == 1:
            self.find(instance=True)
        else:
            self.porchView()
        utils.save()

    def processConsoleInput(self, instance=None, value=None):
        """ Обработка текста в поисковой строке """

        input = self.searchBar.text.lower().strip()

        if input[0:3] == "res" and utils.ifInt(input[3]) == True: # восстановление резервных копий
            copy = int(input[3])
            print("Восстанавливаю копию %d" % copy)
            result = utils.backupRestore(restoreNumber=copy, allowSave=False)
            if result == False:
                self.popup(title="Восстановление данных", message="Не удалось восстановить запрошенную копию с таким номером. Скорее всего, она еще не создана.")
            else:
                self.popup(title="Восстановление данных", message=f"Восстановлена копия {result}.")
                self.rep = report.Report()
                self.terPressed()

        elif input == "loadcb":
            self.importDB()

        elif input == "green":
            utils.settings[0][5] = "green"
            utils.save()
            self.restart()

        elif input == "report":
            self.rep.checkNewMonth(forceDebug=True)

        elif input == "error":
            self.updateList(5, 0)

        elif input != "":
            self.searchBar.text = "Ищем, подождите…"
            self.searchQuery = input
            self.find(instance=instance)

    def getColorForStatus(self, status=99):

        if status == "?":
            color = self.scrollButtonBackgroundColor2# [.4, .4, .4, 1]#[.21, .21, .21, 1] # темно-серый
        elif status == "0":
            color = [0, .54, .73, 1] # синий
        elif status == "1":
            color = [0, .74, .50, 1] # зеленый
        elif status == "2":
            color = [.30, .50, .46, 1] # темно-зеленый
        elif status == "3":
            color = [.53, .37, .76, 1] # фиолетовый
        elif status == "4":
            color = [.50, .27, .22, 1]# [.27, .17, .07, 1] # коричневый
        elif status == "5":
            color = [.81, .24, .17, 1] # красный
        else:
            color = self.scrollButtonBackgroundColor#[.56,.56,.56, 1]
        return color

    def hook_keyboard(self, window, key, *largs):
        if key == 27:
            if self.backButton.disabled == False:
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
                self.popup(title="Удаление: %s" % self.flatTitle,
                           message="Точно удалить?",
                           options=[self.button["yes"], self.button["no"]])
            else:
                self.popupPressed(instance=Button(text=self.button["yes"]))

        elif self.displayed.form == "recordView": # удаление записи посещения
            self.popupForm = "confirmDeleteRecord"
            self.popup(title="Удаление записи посещения",
                       message=f"Удалить запись от {self.record.date}?",
                       options=[self.button["yes"], self.button["no"]])

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
            if self.contactsEntryPoint == 1:
                self.conPressed()
            elif self.searchEntryPoint == 1:
                self.find(instance=instance)
            else:
                self.terPressed()

    def popupPressed(self, instance=None):
        """ Действия при нажатии на кнопки всплывающего окна self.popup """

        self.mypopup.dismiss()

        if self.popupForm == "timerType":
            if instance.text == "Служение":
                self.rep.modify(")")
            else:
                self.rep.modify("$")
            if self.displayed.form == "rep":
                self.repPressed()

        elif self.popupForm == "clearData":
            if instance.text == self.button["yes"]:
                utils.clearDB()
                utils.removeFiles()
                self.rep = report.Report()

        elif self.popupForm == "newMonth":
            self.repPressed()
            self.notePressed()

        elif self.popupForm == "confirmDeleteRecord":
            if instance.text == self.button["yes"]:
                self.flat.deleteRecord(self.selectedRecord)
                utils.save()
                self.flatView()

        elif self.popupForm == "confirmDeleteFlat":
            if instance.text == self.button["yes"]:
                if self.house.type == "virtual":
                    del utils.resources[1][self.selectedHouse]
                    if self.contactsEntryPoint == 1:
                        self.conPressed()
                    elif self.searchEntryPoint == 1:
                        self.find(instance=instance)
                elif "подъезд" in self.porch.type:
                    if self.contactsEntryPoint == 0 and self.searchEntryPoint == 0:
                        self.porch.shrinkFloor(self.selectedFlat)
                        self.porchView()
                    else:
                        self.flat.wipe()
                        if self.contactsEntryPoint == 1:
                            self.conPressed()
                        elif self.searchEntryPoint == 1:
                            self.find(instance=instance)
                else:
                    self.porch.deleteFlat(self.selectedFlat)
                    if self.contactsEntryPoint == 1:
                        self.conPressed()
                    elif self.searchEntryPoint == 1:
                        self.find(instance=instance)
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
                        flat = self.house.porches[p].flats[f]
                        if flat.status != "" and flat.status != "?" and flat.status != utils.settings[0][18]\
                                and flat.getName() != "":
                            interest.append([p, f])
                if len(interest) > 0:
                    for int in interest:
                        flat = self.house.porches[int[0]].flats[int[1]]
                        flat.clone(toStandalone=True, title=self.house.title)
                del utils.houses[self.selectedHouse]
                utils.save()
                self.terPressed()

        elif self.popupForm == "pioneerNorm":
            if instance.text == self.button["yes"]:
                utils.settings[0][3] = 70
                utils.save()
                self.repPressed()
                self.popup("Теперь вы будете видеть запас или отставание от месячной нормы на сегодняшний день в заголовке отчета (в скобках).")

        elif self.popupForm == "restart":
            if instance.text == self.button["yes"]:
                self.restart()

        self.popupForm = ""

    def popup(self, message="", options=[], title="Внимание", firstCall=False):
        """Информационное окно с возможностью подтверждения выбора"""

        # Специальный попап для первого посещения

        if firstCall == True:
            self.popupForm = "firstCall"
            title = self.flat.number
            if self.orientation == "v":
                size_hint = (.9, .5)
            else:
                size_hint = (.5, .6)
            contentMain = BoxLayout(orientation="vertical", padding=self.padding)
            content = GridLayout(rows=1, cols=2, padding=self.padding, spacing=self.spacing*2)
            content2 = GridLayout(rows=1, cols=0, padding=self.padding, spacing=self.spacing*2)

            details = TableButton(text=icon("icon-pencil-1"), size_hint_x=None, size_hint_y=None, color="white",
                                size=(self.standardTextHeight, self.standardTextHeight),
                                background_color=self.popupBackgroundColor, pos_hint={"right": 1})

            def __details(instance):
                self.mypopup.dismiss()
                self.buttonFlash(instance)
                self.popupEntryPoint = 1
                self.flatView()
                self.detailsPressed()
            details.bind(on_release=__details)
            contentMain.add_widget(details)

            if utils.settings[0][20] == 1:
                self.quickPhone = MyTextInput(size_hint_y=None, hint_text = "Телефон", height=self.standardTextHeight,
                                              multiline=False, input_type="text", popup=True, shrink=False, focus=True)
                contentMain.add_widget(self.quickPhone)
                def __getPhone(instance):
                    self.mypopup.dismiss()
                    self.quickPhone.hint_text = "Телефон сохранен!"
                    self.popupForm = "quickPhone"
                    self.flat.editPhone(self.quickPhone.text.strip())
                    utils.save()
                    self.quickPhone.text = ""
                    self.buttonFlash(instance=details, timeout=5)
                    self.porchView()
                self.quickPhone.bind(on_text_validate=__getPhone)

                def __dismiss(instance, value):
                    if value == 0:
                        self.mypopup.dismiss()
                self.quickPhone.bind(focus=__dismiss)

            if utils.settings[0][13] == 1:  # кнопка нет дома
                content.cols += 1
                firstCallNotAtHome = RButton(text=icon("icon-lock-1")+" [b]Нет дома[/b]", color="white",
                                             background_color=self.getColorForStatus("?"), quickFlash=True)
                def __quickNotAtHome(instance):
                    self.mypopup.dismiss()
                    self.flat.addRecord("нет дома")
                    utils.save()
                    self.porchView()
                firstCallNotAtHome.bind(on_release=__quickNotAtHome)
                content.add_widget(firstCallNotAtHome)

            firstCallBtnCall = RButton(text=icon("icon-smile")+" [b]Интерес[/b]", # кнопка интерес
                                      color="white", background_color=self.getColorForStatus("1"), quickFlash=True)
            def __firstCall(instance):
                self.mypopup.dismiss()
                self.flatView(call=True, instance=instance)
            firstCallBtnCall.bind(on_release=__firstCall)
            content.add_widget(firstCallBtnCall)

            rejectColor = self.getColorForStatus(utils.settings[0][18])  # кнопка отказ
            if rejectColor == self.scrollButtonBackgroundColor:
                rejectColor = self.getColorForStatus("0")
                utils.settings[0][18] = "0"
                utils.save()
            firstCallBtnReject = RButton(text=icon("icon-block-1") + " [b]Отказ[/b]", background_color=rejectColor,
                                         color="white", quickFlash=True)
            def __quickReject(instance):
                self.mypopup.dismiss()
                self.quickReject(fromPopup=True)
            firstCallBtnReject.bind(on_release=__quickReject)
            content2.add_widget(firstCallBtnReject)

            contentMain.add_widget(content)
            contentMain.add_widget(content2)

            self.popupForm = ""

        # Строка поиска

        elif self.popupForm == "search":
            self.popupForm = ""
            self.mypopup.dismiss()
            size_hint = (1, .15)
            self.searchBar = SearchBar()
            contentMain = self.searchBar

        # Выбор времени для отчета

        elif self.popupForm == "showTimePicker":
            self.popupForm = ""
            if self.orientation == "v":
                size_hint = (.9, .6)
            else:
                size_hint = (.4, .8)
            pickerForm = BoxLayout(orientation="vertical", padding=self.padding, spacing=self.spacing*2)

            from circulartimepicker import CircularTimePicker
            picker = CircularTimePicker() # часы
            self.pickedTime = "00:00"
            def __setTime(instance, time):
                self.pickedTime = time
            picker.bind(time=__setTime)
            pickerForm.add_widget(picker)

            save = RButton(text="Добавить", size_hint_y=None,  background_color=self.themeDark[0], color="white",
                                            size=(self.standardTextWidth, self.standardTextHeight)) # кнопка сохранения
            def __closeTimePicker(instance):
                self.mypopup.dismiss()
                time2 = str(self.pickedTime)[:5] # время, выбранное на пикере (HH:MM)
                #time2F = utils.timeHHMMToFloat(time2) # это же время во float
                if "служения" in title:
                    #time1 = self.hours.get()  # исходное время на счетчике (HH:MM)
                    if self.pickedTime != "00:00":
                        self.rep.modify(f"ч{time2}")
                        self.hours.update(utils.timeFloatToHHMM(self.rep.hours))#time3)
                        self.backPressed()
                        self.counterChanged = False
                else:
                    #time1 = self.credit.get()  # исходное время на счетчике (HH:MM)
                    #time3F = utils.timeHHMMToFloat(time1) + time2F  # сумма двух времен во float
                    #time3 = utils.timeFloatToHHMM(time3F)  # сумма двух времен в HH:MM
                    if self.pickedTime != "00:00":
                        self.rep.modify(f"р{time2}")
                        self.credit.update(utils.timeFloatToHHMM(self.rep.credit))
                        self.backPressed()
                        self.counterChanged = False
            save.bind(on_release=__closeTimePicker)
            pickerForm.add_widget(save)

            contentMain = pickerForm

        # Стандартное информационное окно либо запрос да/нет

        else:
            if self.orientation == "v":
                size_hint = (.9, .35)
            else:
                size_hint = (.5, .4)
            text_size = (Window.size[0] * size_hint[0]*.9, None)

            contentMain = BoxLayout(orientation="vertical")
            contentMain.add_widget(Label(text=message, halign="left", valign="center", text_size=text_size, markup=True))

            if len(options)>0: # заданы кнопки да/нет
                grid = GridLayout(rows=1, cols=1)
                self.confirmButtonPositive = RButton(text=options[0], black=True)
                self.confirmButtonPositive.bind(on_release=self.popupPressed)
                grid.add_widget(self.confirmButtonPositive)
                if len(options) > 1:
                    grid.cols=3
                    grid.add_widget(Widget())
                    self.confirmButtonNegative = RButton(text=options[1], black=True)
                    self.confirmButtonNegative.bind(on_release=self.popupPressed)
                    grid.add_widget(self.confirmButtonNegative)
                contentMain.add_widget(grid)

        self.mypopup = PopupNoAnimation(title=title, content=contentMain, size_hint=size_hint,
                                        separator_color = self.titleColor)#, width=width, height=height, auto_dismiss=True)

        if firstCall == True:
            def __gotoPorch(instance):
                self.porchView()
            self.mypopup.bind(on_dismiss=__gotoPorch)
            self.popupForm = ""

        self.mypopup.open()

    def changePorchPos(self, pos):
        """ Центровка подъезда по кнопке на джойстике """
        if self.noScalePadding[0] < 0 or self.noScalePadding[1] < 0:
            return
        utils.settings[0][1] = pos
        utils.save()
        self.updateList()

    def onStartup(self):

        utils.backupRestore(delete=True, silent=True)

        utils.update()

        print("Определяем начало нового месяца.")
        self.rep.checkNewMonth()

        limit = 200
        print("Оптимизируем размер журнала отчета.")
        if len(utils.resources[2]) > limit:
            extra = len(utils.resources[2]) - limit
            for i in range(extra):
                del utils.resources[2][len(utils.resources[2]) - 1]

    def importDB(self, instance=None, file=None):
        """ Импорт данных из буфера обмена либо файла"""

        if file == None:
            clipboard = Clipboard.paste()
            success = utils.load(clipboard=clipboard)
        else:
            success = utils.load(forced=True, datafile=file, silent=True) # сначала пытаемся загрузить текстовый файл

            if success == False: # файл не текстовый, пробуем загрузить Word-файл
                try:
                    clipboard = docx2txt.process(file) # имитация буфера обмена, но с Word-файлом
                    success = utils.load(clipboard=clipboard)
                except:
                    self.popup("Не удалось загрузить файл. Скорее всего, он ошибочного формата или не содержит нужных данных.")

        if success == True:
            self.rep = report.Report()
            self.popup("Данные успешно загружены!")

    def checkOrientation(self, window=None, width=None, height=None):
        """ Проверка ориентации экрана, и если она горизонтальная, адаптация интерфейса"""
        if Window.size[0] <= Window.size[1]:
            self.orientation = "v"
            self.boxHeader.size_hint_y = self.marginSizeHintY
            self.titleBox.size_hint_y = self.marginSizeHintY
            self.boxFooter.size_hint_y = self.marginSizeHintY
            self.standardTextHeight = Window.size[1] * .05  # 90
        else:
            self.orientation = "h"
            self.boxHeader.size_hint_y = self.marginSizeHintY * 1.2
            self.titleBox.size_hint_y = self.marginSizeHintY * 1.2
            self.boxFooter.size_hint_y = self.marginSizeHintY * 1.3
            self.standardTextHeight = Window.size[1] * .06  # 90

        if self.platform == "desktop":
            with open("win.ini", "w") as file:
                file.write(str(width)+"\n")
                file.write(str(height)+"\n")
                file.write(str(Window.top)+"\n")
                file.write(str(Window.left))
            self.standardTextHeight = 40

    def buttonFlash(self, instance=None, timeout=None):

        if timeout == None:
            timeout = RM.onClickFlash

        if instance != None:
            color = instance.color
            instance.color = self.titleColor
        def __restoreColor(*args):
            if instance != None:
                instance.color = color
            else:
                pass
        Clock.schedule_once(__restoreColor, timeout)

    def restart(self):
        if self.platform == "mobile":
            kvdroid.tools.restart_app()
        else:
            self.stop()
            from os import startfile
            startfile("main.py")

RM = RMApp()