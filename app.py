#!/usr/bin/python
# -*- coding: utf-8 -*-
import utils
import house
import report
import time
import webbrowser
import iconfonts
from iconfonts import icon
import plyer

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.base import EventLoop
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown
from kivy.core.clipboard import Clipboard
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy import platform
from kivy.clock import Clock
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_hex_from_color

if platform == "android":
    from android.permissions import request_permissions, Permission
    import kvdroid
    from kvdroid import activity
    from kvdroid.jclass.android import Rect
    from jnius import autoclass
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    String = autoclass('java.lang.String')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    mActivity = PythonActivity.mActivity

#Builder.load_file('rm.kv')

class Feed(object):
    def __init__(self, message="", title="", form="", options=[], sort=None, details=None, resize=None,
                 positive="", neutral="", tip=None, back=True):
        self.message = message
        self.title = title
        self.form = form
        self.options = options
        self.positive = positive
        self.neutral = neutral
        self.sort = sort
        self.details = details
        self.resize = resize
        self.back = back
        self.tip = tip

class MyToggleButton(ToggleButton):
    def __init__(self, text="", group="", state="normal", *args, **kwargs):
        super(MyToggleButton, self).__init__()
        self.text = text
        self.group = group
        self.state = state
        self.background_normal = ""
        self.background_down = ""
        self.allow_no_selection = False
        self.background_color = RM.globalBGColor

        if RM.theme != "teal":
            self.color = RM.tableColor
        else:
            self.color = RM.standardTextColor

    def on_state(self, *args):
        if self.state == "normal":
            if RM.theme != "teal":
                self.color = RM.tableColor
            else:
                self.color = RM.standardTextColor
            self.background_color = RM.globalBGColor
        else:
            self.color = "white"
            self.background_color = RM.titleColor

class MyLabel(Label):
    def __init__(self, text="", markup=None, color=None, halign=None, valign=None, text_size=None, size_hint=None, size_hint_y=1,
                 height=None, width=None, pos_hint=None, *args, **kwargs):
        super(MyLabel, self).__init__()

        if markup != None:
            self.markup = markup
        if color != None:
            self.color = color
        if halign != None:
            self.halign = halign
        if valign != None:
            self.valign = valign
        if text_size != None:
            self.text_size = text_size
        if height != None:
            self.height = height
        if width != None:
            self.width = width
        if size_hint != None:
            self.size_hint = size_hint
        if size_hint_y != 1:
            self.size_hint_y = size_hint_y
        if pos_hint != None:
            self.pos_hint = pos_hint

        if RM.language == "ka": # шрифт - его нужно изменить только для грузинского, для остальных языков по умолчанию
            self.font_name = 'DejaVuSans.ttf'

        self.text = text

class MyTextInput(TextInput):
    def __init__(self, multiline=False, size_hint_y=1, size_hint_x=1, hint_text="", pos_hint = {"center_y": .5},
                 text="", disabled=False, input_type="text", width=0, height=0, mode="resize", hack=False,
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
        #self.selection_color = RM.tableBGColor

        self.foreground_color = RM.textInputColor
        self.background_color = RM.textInputBGColor
        self.hint_text = hint_text
        self.hint_text_color = RM.topButtonColor

        if RM.theme == "dark" or RM.theme == "gray" or RM.theme == "retro":
            self.disabled_foreground_color = "darkgray"
            self.hint_text_color = RM.topButtonColor
        else:
            self.hint_text_color = [.5, .5, .5]
        if RM.theme != "retro":
            self.background_normal = ""
            self.background_disabled_normal = ""

        self.cursor_color = RM.titleColor
        self.cursor_color[3] = .9
        self.mode = mode
        self.popup = popup
        self.focus = focus
        self.write_tab = False
        self.hack = hack # альтернативный способ открыть клавиатуру с задержкой в on_focus

        if RM.language == "ka": # шрифт - его нужно изменить только для грузинского, для остальных языков по умолчанию
            self.font_name = 'DejaVuSans.ttf'

    def on_text_validate(self):
        if self.popup == False:
            RM.positivePressed(instance=self)

    def on_focus(self, instance=None, value=None):
        if platform == "android":
            self.keyboard_mode="managed"
            Window.softinput_mode = self.mode
        elif RM.platform == "desktop" and RM.devmode == 0:
            return

        if value:  # вызов клавиатуры
            if RM.model == "huawei" and (RM.inputForm == "multi" or self.hack == True):
                # решаем проблему с клавиатурным глюком только на устройствах huawei взамен на хаотичное открывание клавиатуры
                Clock.schedule_once(self.create_keyboard, .1)
            else:
                self.create_keyboard()

            if self.multiline == False or self.mode == "pan":
                return
            else:
                def __raiseKeyboard(*args):
                    RM.interface.size_hint_y = None
                    RM.interface.height = Window.height - RM.keyboardHeight() - RM.standardTextHeight
                    RM.interface.remove_widget(RM.boxFooter)
                    RM.boxHeader.size_hint_y = 0
                    RM.titleBox.size_hint_y = 0
                    RM.bottomButtons.size_hint_y = RM.bottomButtonsSizeHintY * 1.5
                Clock.schedule_once(__raiseKeyboard, .12)

        else:
            self.hide_keyboard()
            self.keyboard_mode = "auto"
            RM.boxHeader.size_hint_y = RM.marginSizeHintY
            RM.titleBox.size_hint_y = RM.marginSizeHintY
            RM.interface.size_hint_y = 1
            RM.bottomButtons.size_hint_y = RM.bottomButtonsSizeHintY
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

class MyCheckBox(CheckBox):
    def __init__(self, active=False, size_hint=(1, 1), pos_hint=None, *args, **kwargs):
        super(MyCheckBox, self).__init__()
        self.active = active
        self.size_hint = size_hint
        self.color = RM.checkBoxColor
        if pos_hint != None:
            self.pos_hint = pos_hint

class TTab(TabbedPanelHeader):
    """ Вкладки панелей """
    def __init__(self, text=""):
        super(TTab, self).__init__()
        self.text = text
        self.background_normal = "void.png"
        if RM.theme == "dark":
            self.color = "white"
            self.background_down = "tab_background_blue.png"
        elif RM.theme == "purple":
            self.color = RM.titleColor
            self.background_down = "tab_background_purple.png"
        elif RM.theme == "gray":
            self.color = RM.titleColor
            self.background_down = "tab_background_gray.png"
        elif RM.theme == "retro":
            self.color = RM.tableColor
            self.background_down = "tab_background_lime.png"
        else:
            self.color = RM.themeDefault[1]
            self.background_down = "tab_background_blue.png"

        if RM.theme == "green":
            self.background_down = "tab_background_green.png"


        if RM.language == "ka": # шрифт - его нужно изменить только для грузинского, для остальных языков по умолчанию
            self.font_name = 'DejaVuSans.ttf'

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

        if RM.language == "ka": # шрифт - его нужно изменить только для грузинского, для остальных языков по умолчанию
            self.font_name = 'DejaVuSans.ttf'

    def on_press(self):
        if RM.theme != "retro":
            RM.buttonFlash(instance=self)
            if RM.theme == "dark" and self.background_color != RM.tableBGColor:
                self.background_color = RM.buttonPressedOnDark
                Clock.schedule_once(self.restoreBlackBG, RM.onClickFlash)

    def restoreBlackBG(self, *args):
        self.background_color = "black"

class TableButton(Button):
    def __init__(self, text="", size_hint_x=.25, size_hint_y=1, height=0, width=0, background_color=None,
                 color=None, pos_hint=None, size=None, disabled=False, font_name=None, **kwargs):
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
        if background_color == None:
            self.default_background_color = RM.tableBGColor
        else:
            self.default_background_color = background_color
        if RM.theme != "retro":
            if color != None:
                self.color = color
            elif RM.theme == "teal" and background_color == None:
                self.color = RM.tableColor
            elif RM.theme == "teal":
                self.color = RM.themeDefault[1]
            else:
                self.color = RM.tableColor
            self.background_normal = ""
            self.background_color = self.default_background_color
            if RM.theme == "dark" and self.background_color == "black":
                self.background_down = ""
            else:
                self.background_down = RM.buttonPressedBG
            self.background_disabled_normal = ""
        else:
            self.color = RM.mainMenuButtonColor

        self.disabled = disabled

        if font_name != None:
            self.font_name = font_name

        if RM.language == "ka":
            self.font_name = 'DejaVuSans.ttf'

    def on_press(self):
        if RM.theme != "retro":
            RM.buttonFlash(instance=self)
            if RM.theme == "dark" and self.background_color != RM.tableBGColor:
                self.background_color = RM.buttonPressedOnDark
                Clock.schedule_once(self.restoreBlackBG, RM.onClickFlash)

    def restoreBlackBG(self, *args):
        self.background_color = "black"

    def flash(self, mode):
        if mode == "on":
            self.background_color[3] = .6
        else:
            self.background_color = self.default_background_color

class RButton(Button):
    def __init__(self, text="", size_hint_x=1, size_hint_y=1, height=0, text_size=(None, None), halign="center",
                 valign="center", size=Window.size, background_normal="", color="", background_color="",
                 markup=True, background_down="", radius=[12], onPopup=False, fontsize=None, quickFlash=False, **kwargs):
        super(RButton, self).__init__()

        if fontsize != None:
            self.font_size = fontsize
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

        if RM.theme != "retro":
            if RM.platform == "desktop":
                self.radius = [radius[0]/2] # поменьше скругление на ПК
            else:
                self.radius = radius
            self.background_down = background_down
            if onPopup == True:
                self.background_color = [.22, .22, .22, .9]
            elif background_color == "":
                self.background_color = RM.tableBGColor
            else:
                self.background_color = background_color
            self.background_normal = background_normal
            if color == "":
                self.origColor = RM.tableColor
            else:
                self.origColor = color
            self.color = self.origColor

            self.background_color[3] = 0

            with self.canvas.before:
                self.shape_color = Color(rgba=[self.background_color[0], self.background_color[1],
                                               self.background_color[2], 1])
                self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
                self.bind(pos=self.update_shape, size=self.update_shape)

        else:
            if color != "":
                self.color = color
            if background_color != "":
                self.background_color = background_color
                self.background_normal = ""

        if onPopup == True:
            self.size_hint = (1, None)
            self.height = RM.standardTextHeight
            self.color = self.origColor = "white"

        if RM.language == "ka":
            self.font_name = 'DejaVuSans.ttf'

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def on_press(self, *args):
        if RM.theme != "retro":
            if RM.titleBox.size_hint_y != 0: # не должно срабатывать, когда кнопка "Сохранить" на поднятой клавиатуре
                with self.canvas.before:
                    self.shape_color = Color(rgba=[self.background_color[0]*RM.onClickColK,
                                                   self.background_color[1]*RM.onClickColK,
                                                   self.background_color[2]*RM.onClickColK, 1])
                    self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
                    self.bind(pos=self.update_shape, size=self.update_shape)
            self.color = RM.titleColor
            Clock.schedule_once(self.restoreColor, RM.onClickFlash * self.k)

    def restoreColor(self, *args):
        if RM.titleBox.size_hint_y != 0 and RM.theme != "retro":
            with self.canvas.before:
                self.shape_color = Color(rgba=[self.background_color[0], self.background_color[1],
                                               self.background_color[2], 1])
                self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
                self.bind(pos=self.update_shape, size=self.update_shape)
        if RM.theme != "retro":
            self.color = self.origColor

    def saveModeUpdate(self, *args):
        if RM.msg[5] in self.text:
            self.color = RM.mainMenuActivated
        else:
            self.color = RM.tableColor

class PopupNoAnimation(Popup):
    """ Попап, в котором отключена анимация при закрытии"""
    def __init__(self, **kwargs):
        super(PopupNoAnimation, self).__init__(**kwargs)

        if RM.language == "ka":
            self.title_font =  'DejaVuSans.ttf'

    def dismiss(self, *largs, **kwargs):
        if self._window is None:
            return
        if self.dispatch('on_dismiss') is True:
            if kwargs.get('force', False) is not True:
                return
        self._anim_alpha = 0
        self._real_remove_widget()

class SortListButton(Button):
    def __init__(self, text, font_name=None):
        super(SortListButton, self).__init__()
        self.text = text
        self.markup = True
        self.size_hint_y = None
        self.height = RM.standardTextHeight
        self.background_color = RM.textInputBGColor
        self.background_normal = ""
        self.background_down = RM.buttonPressedBG
        self.color = RM.textInputColor
        if font_name != None:
            self.font_name = font_name
        if RM.language == "ka": # шрифт - его нужно изменить только для грузинского, для остальных языков по умолчанию
            self.font_name = 'DejaVuSans.ttf'

    def on_press(self):
        RM.buttonFlash(instance=self)
        Clock.schedule_once(self.restoreColor, RM.onClickFlash)

    def restoreColor(self, *args):
        self.background_color = RM.textInputBGColor

class ScrollButton(Button):
    # Все пункты списка, кроме квадратиков квартир в поэтажном режиме
    def __init__(self, text="", height=0, valign="center", color="", background_color=""):
        super(ScrollButton, self).__init__()
        self.size_hint_y = 1
        self.height = height
        self.halign = "center"
        self.valign = valign
        self.text_size = (Window.size[0]*.95, height)
        if RM.language == "ka": # шрифт - его нужно изменить только для грузинского, для остальных языков по умолчанию
            self.font_name = 'DejaVuSans.ttf'

        self.originalColor = ""

        if RM.theme == "teal" and background_color == None:
            self.originalColor = RM.themeTeal[1]
        elif RM.theme == "teal":
            self.originalColor = RM.themeDefault[1]
            self.background_normal = ""
        elif RM.theme != "retro":
            self.background_normal = ""
            self.originalColor = RM.tableColor

        if self.originalColor != "":
            self.color = self.originalColor

        if background_color == "" and RM.theme != "retro":
            self.background_color = RM.globalBGColor
        elif RM.theme != "retro":
            self.background_color = background_color

        if RM.theme == "dark":
            self.background_down = ""
        elif RM.theme != "retro":
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
        self.text = text
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
        self.background_normal = ""
        self.background_color = RM.getColorForStatus(status)
        if RM.language == "ka": # шрифт - его нужно изменить только для грузинского, для остальных языков по умолчанию
            self.font_name = 'DejaVuSans.ttf'

        if RM.theme != "retro":
            if RM.platform == "desktop":
                self.radius = [radius[0] / 2]  # поменьше скругление на ПК
            else:
                self.radius = radius

            self.background_color[3] = 0
            self.background_down = RM.buttonPressedBG
            if RM.msg[11] in text:
                self.background_color = RM.globalBGColor
                if RM.theme != "teal":
                    self.color = RM.tableColor
                else:
                    self.color = RM.themeDefault[1]
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
        if RM.theme == "retro":
            return
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

    def on_release(self, mode="floors"):
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
        if RM.theme != "retro":
            if RM.theme == "dark":
                self.color = "black"
            elif RM.theme == "teal":
                self.color = RM.themeDefault[1]
            elif RM.theme == "purple":
                self.color = RM.titleColor
            else:
                self.color = RM.mainMenuButtonColor
            if RM.theme == "gray":
                self.color = RM.tableBGColor
                self.background_color = RM.topButtonColor
            else:
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
        RM.inputForm = "single"

        box = BoxLayout(size_hint=size_hint)
        self.input = MyTextInput(text=text, focus=focus, disabled=disabled, multiline=False,
                            pos_hint={"center_y": .5}, input_type="number", shrink=shrink, mode=mode)

        def __edit(instance, value):
            RM.counterChanged = True
            if utils.ifInt(self.input.text) == True and int(self.input.text) < 0:
                self.input.text = "0"
            else:
                try:
                    if self.input.text[0] == "-":
                        self.input.text = self.input.text[1:]
                except:
                    pass
            
            if value == 0 and self.input.text.strip() == "":
                self.input.text = "0"
        self.input.bind(focus=__edit)

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
        #self.size_hint = (None, None)
        #self.width = RM.standardTextHeight*1.5
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
        if RM.theme == "retro" or RM.theme == "green":
            self.color = RM.titleColor
        else:
            self.color = RM.getColorForStatus("1") #"limegreen"

class ColorStatusButton(Button):
    def __init__(self, status="", text=""):
        super(ColorStatusButton, self).__init__()
        self.size_hint_max_y = .5
        self.side = (RM.mainList.size[0] - RM.padding*2 - RM.spacing*14.5) / 7
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

        if RM.theme != "retro":
            if RM.platform == "mobile":
                self.radius = [15]
            else:
                self.radius = [7]
            self.background_color[3] = 0
            with self.canvas.before:
                self.shape_color = Color(rgba=[RM.getColorForStatus(self.status)[0], RM.getColorForStatus(self.status)[1],
                                               RM.getColorForStatus(self.status)[2], 1])
                self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
                self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def on_press(self, *args):
        for button in RM.colorBtn:
            button.text = ""
        self.text = RM.button["dot"]
        if RM.theme != "retro":
            with self.canvas.before:
                self.shape_color = Color(rgba=[RM.getColorForStatus(self.status)[0]*RM.onClickColK,
                                               RM.getColorForStatus(self.status)[1]*RM.onClickColK,
                                               RM.getColorForStatus(self.status)[2]*RM.onClickColK, 1])
                self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
                self.bind(pos=self.update_shape, size=self.update_shape)
            Clock.schedule_once(self.restoreColor, RM.onClickFlash/2)

    def restoreColor(self, *args):
        with self.canvas.before:
            self.shape_color = Color(rgba=[RM.getColorForStatus(self.status)[0], RM.getColorForStatus(self.status)[1],
                                           RM.getColorForStatus(self.status)[2], 1])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            self.bind(pos=self.update_shape, size=self.update_shape)

    def on_release(self, instance=None):
        RM.colorBtnPressed(color=self.status)

class MainMenuButton(Button):
    def __init__(self, text):
        super(MainMenuButton, self).__init__()
        self.markup = True
        self.height = 0
        self.pos_hint = {"center_y": .5}
        self.text = text
        if text == RM.msg[2]: # участки
            if RM.language == "ru":
                self.text = f"[size={RM.fontL}]{icon('icon-building')}[/size]\n{text}"
            else:
                self.text = f"[size={RM.fontL}]{icon('icon-map-o')}[/size]\n{text}"
        elif text == RM.msg[3]: # контакты
            self.text = f"[size={RM.fontL}]{icon('icon-address-book-o')}[/size]\n{text}"
        elif text == RM.msg[4]: # отчет
            self.text = f"[size={RM.fontL}]{icon('icon-doc-text')}[/size]\n{text}"
        if RM.platform == "mobile":
            self.font_size = RM.fontL*.7
        self.valign = self.halign = "center"
        self.size_hint = (1, 1)
        self.markup = True
        if RM.theme == "retro":
            self.background_color = RM.globalBGColor#[.82, .9, .9]
        else:
            self.background_color = RM.tableBGColor
            self.background_down = RM.buttonPressedBG
        self.background_normal = ""
        self.color = RM.mainMenuButtonColor

        if RM.language == "ka": # шрифт - его нужно изменить только для грузинского, для остальных языков по умолчанию
            self.font_name = 'DejaVuSans.ttf'

    def on_press(self):
        RM.buttonFlash(instance=self)

    def activate(self):
        self.color = RM.mainMenuActivated
        if RM.msg[2] in self.text:
            if RM.language == "ru":
                self.text = f"[size={RM.fontL}]{icon('icon-building-filled')}[/size]\n{RM.msg[2]}"
            else:
                self.text = f"[size={RM.fontL}]{icon('icon-map')}[/size]\n{RM.msg[2]}"
        elif RM.msg[3] in self.text:
            self.text = f"[size={RM.fontL}]{icon('icon-address-book-1')}[/size]\n{RM.msg[3]}"
        elif RM.msg[4] in self.text:
            self.text = f"[size={RM.fontL}]{icon('icon-doc-text-inv')}[/size]\n{RM.msg[4]}"

    def deactivate(self):
        self.color = RM.mainMenuButtonColor

        if RM.msg[2] in self.text:
            if RM.language == "ru":
                self.text = f"[size={RM.fontL}]{icon('icon-building')}[/size]\n{RM.msg[2]}"
            else:
                self.text = f"[size={RM.fontL}]{icon('icon-map-o')}[/size]\n{RM.msg[2]}"
        elif RM.msg[3] in self.text:
            self.text = f"[size={RM.fontL}]{icon('icon-address-book-o')}[/size]\n{RM.msg[3]}"
        elif RM.msg[4] in self.text:
            self.text = f"[size={RM.fontL}]{icon('icon-doc-text')}[/size]\n{RM.msg[4]}"

    def on_release(self):
        Clock.schedule_once(RM.updateMainMenuButtons, 0.08)

class RejectColorSelectButton(AnchorLayout):
    def __init__(self):
        super(RejectColorSelectButton, self).__init__()
        if utils.settings[0][18] == "4":
            text1 = RM.button["dot"]
            text2 = ""
            text3 = ""
        elif utils.settings[0][18] == "5":
            text1 = ""
            text2 = ""
            text3 = RM.button["dot"]
        else:
            text1 = ""
            text2 = RM.button["dot"]
            text3 = ""

        self.b1 = RButton(text=text1, markup=True, background_color=RM.getColorForStatus("4"), background_normal="",
                    color="white", background_down = RM.buttonPressedBG)
        self.b2 = RButton(text=text2, markup=True, background_color=RM.getColorForStatus("0"), background_normal="",
                    color = "white", background_down = RM.buttonPressedBG)
        self.b3 = RButton(text=text3, markup=True, background_color=RM.getColorForStatus("5"), background_normal="",
                    color = "white", background_down = RM.buttonPressedBG)
        self.b1.bind(on_press=self.change)
        self.b2.bind(on_press=self.change)
        self.b3.bind(on_press=self.change)
        self.anchor_x = "center"
        self.anchor_y = "center"
        box = BoxLayout()
        box.spacing = RM.spacing
        box.size_hint = (1, .6)
        self.add_widget(box)
        box.add_widget(self.b1)
        box.add_widget(self.b2)
        box.add_widget(self.b3)

    def change(self, instance):
        self.b1.text = ""
        self.b2.text = ""
        self.b3.text = ""
        instance.text = RM.button["dot"]

    def get(self):
        if self.b1.text == RM.button["dot"]:
            return "4"
        elif self.b2.text == RM.button["dot"]:
            return "0"
        else:
            return "5"

class RMApp(App):
    """ Главный класс приложения """

    def build(self):

        if platform == "android":
            request_permissions([Permission.CALL_PHONE, Permission.INTERNET, "com.google.android.gms.permission.AD_ID"])
        utils.load()
        self.setParameters()
        self.setTheme()
        self.globalAnchor = AnchorLayout(anchor_x="center", anchor_y="top")
        self.createInterface()
        self.terPressed()
        Clock.schedule_interval(self.updateTimer, 1)
        if self.devmode == 0:
            self.onStartup()
        return self.globalAnchor

    # Подготовка переменных

    def setParameters(self, reload=False):

        if platform != "win" and platform != "linux": # определение платформы
            self.platform = "mobile"
        else:
            self.platform = "desktop"

        if utils.settings[0][6] not in utils.Languages.keys(): # определение языка на устройстве
            if platform == "android":
                from kvdroid.tools.lang import device_lang
                DL = device_lang()
            elif platform == "win":
                import locale
                locale.getdefaultlocale()
                import ctypes
                windll = ctypes.windll.kernel32
                DL = locale.windows_locale[windll.GetUserDefaultUILanguage()][0:2]
            elif platform == "linux":
                try:
                    from os import environ
                    DL = environ['LANG'][0:2]
                except:
                    DL = "en"
            else:
                DL = "en"

            if DL == "ru" or DL == "ua" or DL == "by" or DL == "kz":
                self.language = "ru"
            elif DL == "ka":
                self.language = "ka"
            else:
                self.language = "en"

            utils.settings[0][6] = self.language
            utils.save()
        else:
            self.language = utils.settings[0][6]

        try:
            with open(f"{self.language}.lang", mode="r", encoding="utf-8") as file: # загрузка языкового файла
                self.msg = file.read().splitlines()
            self.msg.insert(0, "")
        except:
            from tkinter import messagebox
            messagebox.showerror(title="Error",
                message="Не найден языковой файл! Переустановите приложение.\n\nLanguage file not found! Please re-install the app.")
            self.stop()

        self.rep = report.Report() # инициализация отчета

        iconfonts.register('default_font', 'fontello.ttf', 'fontello.fontd')  # шрифты с иконками

        self.button = {  # кнопки с иконками
            "save": f" {icon('icon-ok-circled')} {self.msg[5]}",
            "plus": icon("icon-plus-circled"),
            "ok": icon("icon-ok-1") + " OK",
            "back": icon("icon-left-2"),
            "details": icon("icon-pencil-1"),
            "search": icon("icon-search-1"),
            "search2": icon("icon-search-circled"),
            "dot": icon("icon-dot-circled"),
            "menu": icon("icon-menu"),
            "cog": icon("icon-cog-1"),
            "reject": icon("icon-block-1"),
            "contact": icon("icon-user-plus"),
            "phone": icon("icon-phone-circled"),
            "phone1": icon("icon-phone-1"),
            "resize": icon("icon-resize-full-alt-2"),
            "sort": icon("icon-sort-alt-up"),
            "target": icon("icon-target-1"),
            "shrink": icon("icon-right-dir"),
            "list": icon("icon-doc-text-inv"),
            "bin": icon("icon-trash-1"),
            "nav": icon("icon-location-circled"),
            "note": icon("icon-sticky-note"),
            "chat": icon("icon-chat"),
            "log": icon("icon-history"),
            "info": icon('icon-info-circled'),
            "share": icon("icon-share-squared"),
            "export": icon("icon-upload-cloud"),
            "import": icon("icon-download-cloud"),
            "open": icon("icon-folder-open"),
            "restore": icon("icon-upload-1"),
            "wipe": icon("icon-trash-1"),
            "help": icon("icon-help-circled"),
            "flist": icon("icon-align-justify"),
            "fgrid": icon("icon-th-large"),
            "lock": icon("icon-lock-1"),
            "record": icon("icon-pencil-1"),
            "warn": icon("icon-attention"),
            "up": icon("icon-up-1"),
            "down": icon("icon-down-1"),
            "user": icon("icon-user-1"),
            "yes": self.msg[297],
            "no": self.msg[298],
            "cancel": self.msg[190]
        }

        if reload == False:  # при мягкой перезагрузке сохраняем стек
            self.contactsEntryPoint = self.searchEntryPoint = self.popupEntryPoint = 0 # различные переменные
            self.porch = house.House().Porch()
            self.stack = []
            self.showSlider = False
            self.devmode = utils.Devmode
            self.restore = 0
            self.mypopup = PopupNoAnimation()
            self.onClickColK = .7  # коэффициент затемнения фона кнопки при клике
            self.onClickFlash = .08  # время появления теневого эффекта на кнопках
            self.buttonPressedBG = "button_background.png"

            Window.fullscreen = False # размеры и габариты
            self.spacing = Window.size[1]/400
            self.padding = Window.size[1]/300
            self.porchPos = [0, 0] # положение сетки подъезда без масштабирования
            self.standardTextHeight = self.standardBarWidth = Window.size[1] * .04 #90
            self.standardTextWidth = self.standardTextHeight * 1.3
            self.marginSizeHintY = 0.08
            self.bottomButtonsSizeHintY = .1
            self.counterHeight = self.standardTextHeight * 2.5 # размер счетчика в фиксированном состоянии
            self.defaultKeyboardHeight = Window.size[1]*.4

            self.fontXXL =  int(Window.size[1] / 30)
            self.fontXL =   int(Window.size[1] / 35)
            self.fontL =    int(Window.size[1] / 40)
            self.fontM =    int(Window.size[1] / 45)
            self.fontS =    int(Window.size[1] / 50)
            self.fontXS =   int(Window.size[1] / 55)
            self.fontXXS =  int(Window.size[1] / 60)

        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

        # Действия в зависимости от платформы



        if self.platform == "desktop":
            self.model = "pc"
            self.title = 'Rocket Ministry'
            Window.icon = "icon.png"
            self.icon = "icon.png"
            try: # сначала смотрим положение и размер окна в файле win.ini, если он есть
                with open("win.ini", mode="r") as file:
                    lines = file.readlines()
                if self.devmode == 1:
                    k = .4
                    Window.size = (1120 * k, 2340 * k)
                else:
                    Window.size = ( int(lines[0]), int(lines[1]) )
                Window.top = int(lines[2])
                Window.left = int(lines[3])
            except:
                pass
            def __dropFile(*args):
                self.importDB(file=args[1].decode())
                self.terPressed()
            Window.bind(on_drop_file=__dropFile)
            def __close(*args):
                if self.devmode == 1:
                    print("Выход из программы.")
                utils.save(export=True)
                self.checkOrientation(width=args[0].size[0], height=args[0].size[1])
            Window.bind(on_request_close=__close)
            Window.bind(on_resize=self.checkOrientation)

        elif platform == "android":
            from kvdroid.tools.deviceinfo import device_info
            self.model = device_info("manufacturer").lower()
            plyer.orientation.set_portrait()

        elif platform == "mobile":
            self.model = "unknown"
            plyer.orientation.set_portrait()

    # Создание интерфейса

    def createInterface(self):
        """ Создание основных элементов """

        self.interface = BoxLayout(orientation="vertical")
        self.boxHeader = BoxLayout(size_hint_y=self.marginSizeHintY, spacing=self.spacing, padding=self.padding)

        # Таймер

        self.timerBox = BoxLayout(size_hint_x=.25, spacing=self.spacing, padding=(self.padding, 0))
        self.timer = Timer()
        self.timerBox.add_widget(self.timer)
        self.timerText = Label(halign="left", valign="center", #font_size=self.fontM,
                               color=[self.standardTextColor[0], self.standardTextColor[1], self.standardTextColor[2], .9],
                               width=self.standardTextWidth, markup=True,
                               #size_hint=(None, None),
                               pos_hint={"center_y": .5})
        self.timerBox.add_widget(self.timerText)
        self.boxHeader.add_widget(self.timerBox)

        # Заголовок таблицы

        self.headBox = BoxLayout(size_hint_x=.5, spacing=self.spacing)
        self.pageTitle = MyLabel(text="", color=self.titleColor, halign="center", valign="center", markup=True,
                                 text_size=(Window.size[0] * .4, None))
        self.pageTitle.bind(on_ref_press=self.titlePressed)
        self.headBox.add_widget(self.pageTitle)
        self.boxHeader.add_widget(self.headBox)

        # Поиск и настройки

        self.setBox = BoxLayout(size_hint_x=.25, spacing=self.spacing, padding=(self.padding, 0))
        self.search = TopButton(text=self.button["search"])
        self.search.bind(on_release=self.searchPressed)
        self.setBox.add_widget(self.search)

        self.settings = TopButton(text=self.button["menu"])
        self.settings.bind(on_release=self.settingsPressed)
        self.setBox.add_widget(self.settings)
        self.boxHeader.add_widget(self.setBox)
        self.interface.add_widget(self.boxHeader)

        self.boxCenter = BoxLayout()
        self.mainBox = BoxLayout()
        self.boxCenter.add_widget(self.mainBox)
        self.listarea = BoxLayout(orientation="vertical")
        self.mainBox.add_widget(self.listarea)

        # Верхние кнопки таблицы

        self.titleBox = BoxLayout(size_hint_y=self.marginSizeHintY)
        self.listarea.add_widget(self.titleBox)
        self.backButton = TableButton(text=self.button["back"], size_hint_x=.3)
        self.backButton.bind(on_release=self.backPressed)
        self.titleBox.add_widget(self.backButton)

        self.dropSortMenu = DropDown()
        self.sortButton = TableButton(size_hint_x=.3)
        self.titleBox.add_widget(self.sortButton)
        self.sortButton.bind(on_press=self.sortPressed)

        self.resizeButton = TableButton(size_hint_x=.1)
        self.titleBox.add_widget(self.resizeButton)
        self.resizeButton.bind(on_release=self.resizePressed)

        self.detailsButton = TableButton(size_hint_x=.3)
        self.detailsButton.bind(on_release=self.detailsPressed)
        self.titleBox.add_widget(self.detailsButton)

        # Главный список

        self.mainList = BoxLayout(orientation="vertical", padding=(0, self.padding))
        AL = AnchorLayout(anchor_x="center", anchor_y="top")
        AL.add_widget(self.mainList)
        self.listarea.add_widget(AL)

        # Слайдер и джойстик выбора позиции

        self.sliderBox = BoxLayout()
        self.slider = Slider(pos=(0, Window.size[1] * .75), orientation='horizontal', min=0.4, max=2,
                             padding=0, value=utils.settings[0][8], cursor_image=self.sliderImage)
        self.sliderBox.add_widget(self.slider)
        self.posSelector = GridLayout(#pos=(Window.size[0]/3, Window.size[1]/3),
                                      rows=3, cols=3, size_hint=(None, None),
                                      padding=self.padding,
                                      size=(Window.size[0]/3, Window.size[1]/4))
        buttons = []
        for i in [1,2,3,4,5,6,7,8,9]:
            buttons.append(TableButton(text=self.button["target"]))
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
        self.slider.bind(on_touch_move=self.sliderGet)
        self.slider.bind(on_touch_up=self.sliderGet)

        # Нижние кнопки таблицы

        self.bottomButtons = BoxLayout(size_hint_y=self.bottomButtonsSizeHintY)
        self.listarea.add_widget(self.bottomButtons)
        self.navButton = TableButton(text=self.button['nav'], background_color=self.globalBGColor, size_hint_x=.15)
        self.bottomButtons.add_widget(self.navButton)
        self.navButton.bind(on_release=self.navPressed)

        if self.theme == "retro":# or Window.size[0] > Window.size[1]:
            self.positive = TableButton(background_color=self.globalBGColor, size_hint_x=.7)
        else:
            self.bottomButtons.spacing = self.spacing * 5
            self.bottomButtons.padding = (0, self.padding * 2, 0, self.padding * 4)
            self.positive = RButton(background_color=self.tableBGColor, color=self.tableColor, size_hint_x=.7,
                                    radius=[40])

        self.positive.bind(on_release=self.positivePressed)
        self.bottomButtons.add_widget(self.positive)

        self.neutral = TableButton(background_color=self.globalBGColor, size_hint_x=.15)
        self.neutral.bind(on_release=self.neutralPressed)
        self.bottomButtons.add_widget(self.neutral)

        self.negative = TableButton(background_color=self.globalBGColor, size_hint_x=0)
        self.negative.bind(on_release=self.backPressed)
        #self.bottomButtons.add_widget(self.negative)
        self.interface.add_widget(self.boxCenter)

        # Подвал и кнопки меню

        self.boxFooter = BoxLayout(size_hint_y=self.marginSizeHintY, height=0)

        self.buttonTer = MainMenuButton(text=self.msg[2])
        self.buttonTer.bind(on_release=self.terPressed)
        b1 = AnchorLayout(anchor_x="center")
        b1.add_widget(self.buttonTer)
        self.boxFooter.add_widget(b1)

        self.buttonCon = MainMenuButton(text=self.msg[3])
        self.buttonCon.bind(on_release=self.conPressed)
        b2 = AnchorLayout(anchor_x="center")
        b2.add_widget(self.buttonCon)
        self.boxFooter.add_widget(b2)

        self.buttonRep = MainMenuButton(text=self.msg[4])
        self.buttonRep.bind(on_release=self.repPressed)
        b3 = AnchorLayout(anchor_x="center")
        b3.add_widget(self.buttonRep)
        self.boxFooter.add_widget(b3)

        self.interface.add_widget(self.boxFooter)
        self.globalAnchor.add_widget(self.interface)

        self.checkOrientation()

    def setTheme(self):

        self.themes = {
            self.msg[301]: "dark",
            self.msg[302]: "gray",
            self.msg[303]: "retro",
            self.msg[304]: "green",
            self.msg[305]: "teal",
            self.msg[306]: "purple",
            self.msg[307]: "default"
        }

        self.themeDefault = [0.93, 0.93, 0.93, .9], [0, .15, .35, .85], [.18, .65, .83, 1] # цвет фона таблицы, кнопок таблицы и title

        self.theme = utils.settings[0][5]

        if utils.settings[1] == "" and platform == "android": # определяем темную тему на мобильном устройстве при первом запуске
            from kvdroid.tools.darkmode import dark_mode
            if dark_mode() == True:
                self.theme = utils.settings[0][5] = "dark"
                utils.save()
            else:
                self.theme = "default"

        elif self.devmode==0: # пытаемся получить тему из файла на ПК
            try:
                with open("theme.ini", mode="r") as file:
                    self.theme = file.readlines()[0]
            except:
                pass

        if self.theme == "dark":
            self.globalBGColor = self.globalBGColor0 = [0, 0, 0]#self.themeDark # фон программы
            self.mainMenuButtonColor = [1, 1, 1, 1]#"white"
            self.mainMenuButtonColor2= "FFFFFF"
            self.tableBGColor = [.2, .2, .2, .9] # цвет фона кнопок таблицы
            self.standardTextColor = self.textInputColor = [1, 1, 1, 1]#"white" # основной текст всех шрифтов
            self.titleColor = self.mainMenuActivated = [.3, .82, 1, 1] # неон - цвет нажатой кнопки и заголовка
            self.titleColor2 = get_hex_from_color(self.titleColor)
            self.checkBoxColor = [1, 1, 1, 1]
            self.popupBackgroundColor = [.16, .16, .16, 1] # фон всплывающего окна
            self.tableColor = [1, 1, 1, 1]#"white" # цвет текста на плашках таблицы и кнопках главного меню
            self.standardScrollColor = [1, 1, 1, 1]#"white" # текст пунктов списка
            self.scrollButtonBackgroundColor = [.38,.38,.38, 1]#[.14, .14, .14] # фон пунктов списка
            self.scrollButtonBackgroundColor2 = [.28, .28, .28, 1] # более темный цвет списка (создать подъезд + нет дома)
            self.createNewPorchButton = [.2, .2, .2, 1] # пункт списка создания нового подъезда
            self.textInputBGColor = [.3, .3, .3, .9]
            self.buttonPressedOnDark = [.3, .3, .3, 1] # цвет только в темной теме, определяющий засветление фона кнопки
            self.interestColor = get_hex_from_color(self.getColorForStatus("1"))  # "00BC7F"  # "00CA94" # должен соответствовать зеленому статусу или чуть светлее
            self.sliderImage = "slider_cursor.png"

        else:
            self.globalBGColor = (1, 1, 1, 1)
            self.globalBGColor0 = (1, 1, 1, 0)
            Window.clearcolor = self.globalBGColor
            self.tableColor = self.mainMenuButtonColor = self.themeDefault[1]
            k=2.5
            self.mainMenuActivated = [self.mainMenuButtonColor[0]*k, self.mainMenuButtonColor[1]*k, self.mainMenuButtonColor[2]*k, 1]
            self.mainMenuButtonColor2 = get_hex_from_color(self.mainMenuButtonColor)
            self.standardTextColor = self.textInputColor = [.1, .1, .1]
            self.titleColor = self.themeDefault[2]
            self.titleColor2 = get_hex_from_color(self.titleColor)
            self.activatedColor = [0, .15, .35, .9]
            self.checkBoxColor = [.8, .8, .9]
            self.tableBGColor = self.themeDefault[0]
            self.popupBackgroundColor = [.16, .16, .16]
            self.standardScrollColor = "white"
            self.scrollButtonBackgroundColor = [.56,.56,.56]
            self.scrollButtonBackgroundColor2 = [.46,.46,.46]
            self.createNewPorchButton = "dimgray"
            self.phoneNeutralButton = "lightgreen"
            self.reportFlashColor = "lightgreen"
            self.textInputBGColor = [.97, .97, .97, .9]
            self.interestColor = get_hex_from_color(self.getColorForStatus("1"))
            self.sliderImage = "slider_cursor.png"

            if self.theme == "purple": # Пурпур
                self.mainMenuButtonColor = [.32, .32, .34]
                self.mainMenuButtonColor2 = get_hex_from_color(self.mainMenuButtonColor)
                self.titleColor = self.tableColor = self.mainMenuActivated = [.36, .24, .53, 1]
                self.titleColor2 = "5B3C88"
                self.checkBoxColor = [1, .5, 1, 1]
                self.tableBGColor = [0.83, 0.83, 0.83, .9]
                self.sliderImage = "slider_cursor_purple.png"

            elif self.theme == "green": # Эко
                self.titleColor = self.mainMenuActivated = [.09, .65, .58, 1]
                self.checkBoxColor = [1, 1, .7]
                self.titleColor2 = get_hex_from_color(self.titleColor)
                self.tableColor = self.mainMenuButtonColor = [0, .4, .4]
                self.tableBGColor = [0.92, 0.94, 0.92, .9]
                self.mainMenuButtonColor2 = get_hex_from_color(self.mainMenuButtonColor)
                self.sliderImage = "slider_cursor_green.png"

            elif self.theme == "teal": # Бирюза
                self.mainMenuActivated = [.9, 1, .9]
                self.tableColor = self.mainMenuButtonColor = "white"
                self.tableBGColor = [0.2, 0.7, 0.8, .85]
                self.checkBoxColor = [1, 1, .9]
                self.mainMenuButtonColor2 = "FFFFFF"

            elif self.theme == "gray": # Вечер
                self.titleColor = self.mainMenuActivated = [.7, .8, 1, 1]
                self.titleColor2 = get_hex_from_color(self.titleColor)
                self.checkBoxColor = [1, .8, 1]
                self.tableColor = self.mainMenuButtonColor = "white"
                self.standardTextColor = self.textInputColor = [.95, .95, .95]
                self.tableBGColor = [.12, .3, .5, .95]
                self.textInputBGColor = [.31, .3, .3, .9]
                self.mainMenuButtonColor2 = "FFFFFF"
                self.globalBGColor = [.2, .2, .2]
                self.sliderImage = "slider_cursor_gray.png"

            elif self.theme == "retro": # Ретро
                self.titleColor = self.mainMenuActivated = [.5, 1, .5]
                self.titleColor2 = "80FF80"
                self.checkBoxColor = [.8, 1, .5]
                self.mainMenuButtonColor = self.tableColor = [.95, 1, .95]
                self.mainMenuButtonColor2 = get_hex_from_color(self.mainMenuButtonColor)
                self.textInputBGColor = [.5, .5, .5, .9]
                self.textInputColor = self.standardTextColor = [.95, .95, .95]
                self.globalBGColor = [.3, .3, .3]
                self.interestColor = get_hex_from_color(self.titleColor)

        self.topButtonColor = [.75, .75, .75]  # "lightgray" # поиск, настройки и кнопки счетчиков
        self.topButtonColor2 = get_hex_from_color(self.topButtonColor)

        Window.clearcolor = self.globalBGColor

    # Основные действия с центральным списком

    def updateList(self, form=None, instance=None):#, a=1, b=1):
        """Заполнение главного списка элементами"""

        #if 1:# self.devmode==1:
        try:
            if form == None:
                form = self.mainList
            self.stack = list(dict.fromkeys(self.stack))
            form.clear_widgets()
            self.popupEntryPoint = 0
            if self.showSlider == False:
                self.sortButton.disabled = True

            self.navButton.disabled = True
            self.navButton.text = ""

            # Выставление параметров, полученных из Feed

            if "View" in self.displayed.form:
                self.pageTitle.text = f"[ref=title]{self.displayed.title}[/ref]"
            else:
                self.pageTitle.text = self.displayed.title

            if self.displayed.positive != "":
                self.positive.disabled = False
                self.positive.text = self.displayed.positive
                self.positive.color = self.tableColor
            else:
                self.positive.text = ""
                self.positive.disabled = True

            if self.displayed.neutral != "":
                self.neutral.disabled = False
                self.neutral.text = self.displayed.neutral
            else:
                self.neutral.text = ""
                self.neutral.disabled = True

            if self.displayed.sort != None:
                self.sortButton.disabled = False
                self.sortButton.text = self.displayed.sort
            else:
                self.sortButton.text = ""
                self.sortButton.disabled = True

            if self.displayed.resize != None:
                self.resizeButton.disabled = False
                self.resizeButton.text = self.displayed.resize
            else:
                self.resizeButton.text = ""
                self.resizeButton.disabled = True

            if self.displayed.details != None:
                self.detailsButton.disabled = False
                self.detailsButton.text = self.displayed.details
            else:
                self.detailsButton.text = ""
                self.detailsButton.disabled = True

            if self.displayed.back == False:
                self.backButton.disabled = True
            else:
                self.backButton.disabled = False

            if self.displayed.tip != None:
                if len(self.displayed.tip) == 2:
                    if self.displayed.tip[0] != None:
                        form.add_widget(self.tip(text=self.displayed.tip[0], icon=self.displayed.tip[1]))
                else:
                    form.add_widget(self.tip(self.displayed.tip))

            if "View" in self.displayed.form:
                self.navButton.disabled = False
                self.navButton.text = self.button['nav']

            # Обычный список (этажей нет)

            if self.displayed.form != "porchView" or \
                    (self.displayed.form == "porchView" and self.porch.floors() == False):
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
                    elif self.msg[6] in label:
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

                    if self.msg[8] in label or self.displayed.form == "repLog":
                        # отдельный механизм добавления записей журнала отчета + ничего не найдено в поиске
                        self.scrollWidget.add_widget(MyLabel(text=label.strip(), color=self.standardTextColor, halign="left",
                                                           valign="top", size_hint_y=None, height=height1, markup=True,
                                                            text_size=(Window.size[0] - 50, height1)))
                    else: # стандартное добавление

                        height = self.standardTextHeight * 1.2 # коэффициент, на который квартира выше пункта в стандартном списке
                        gap = 1.05 # зазор между квартирами в списке
                        box = BoxLayout(orientation="vertical", size_hint_y=None)

                        if self.displayed.form != "porchView": # вид для всех списков, кроме подъезда - без фона
                            self.btn.append(ScrollButton(text=label.strip(), height=height, valign=valign,
                                                     color=color, background_color=background_color))

                        else: # вид для списка подъезда - с фоном и закругленными квадратиками
                            self.scrollWidget.spacing = (self.spacing, 0)
                            self.scrollWidget.padding = (self.padding, 0)
                            self.btn.append(FlatButton(text=label.strip(), height=height, status=status, size_hint_y=None))
                        last = len(self.btn)-1
                        box.add_widget(self.btn[last])

                        if addRecord == True or addPhone == True or addNote == True: # если есть запись посещения, телефон или заметка, добавляем снизу
                            gray = self.topButtonColor2
                            br = ""
                            if flat.phone != "":
                                myicon = self.button["phone1"]
                                phone = f"[color={gray}]{myicon}[/color]\u00A0{flat.phone}\u00A0\u00A0\u00A0\u00A0\u00A0"
                                br = "\n"
                            else:
                                phone = ""
                            if flat.note != "":
                                myicon = self.button["note"]
                                note = f"[color={gray}]{myicon}[/color]\u00A0{flat.note}"
                                br = "\n"
                            else:
                                note = ""
                            if len(flat.records) > 0:
                                myicon = self.button["chat"]
                                record = f"{br}[color={gray}]{myicon}[/color]\u00A0[i]{flat.records[0].title}[/i]"
                            else:
                                record = ""
                            text = phone + note + record
                            box.add_widget( MyLabel(
                                text=text, markup=True, color=self.standardTextColor, halign="left", valign="top",
                                size_hint_y=None, height=height1, text_size = (Window.size[0]-50, height1)
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
                form.add_widget(self.scroll)

            # Вид подъезда с этажами

            elif utils.settings[0][7] == 1: # поэтажная раскладка с масштабированием

                spacing = self.spacing * 2

                self.floorview = GridLayout(cols=self.porch.columns+1, rows=self.porch.rows, spacing=spacing,
                                            padding=spacing*2)
                for label in self.displayed.options:
                    if "│" in label: # показ цифры этажа
                        self.floorview.add_widget(Label(text=label[: label.index("│")], halign="right",
                                color=self.standardTextColor, width=self.standardTextHeight/3,
                                                        size_hint_x=None, font_size=self.fontXS*.9))
                    elif "." in label:
                        self.floorview.add_widget(Widget())
                    else:
                        status = label[label.index("{")+1 : label.index("}")] # определение цвета по статусу
                        b = FlatButton(text=label[label.index("}")+1 : ], status=status, size_hint_y=0)
                        self.floorview.add_widget(b)
                self.sliderToggle()
                form.add_widget(self.floorview)

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
                                                        width=floorLabelWidth, font_size=self.fontXS*.9, height=size,
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
                form.add_widget(BL)
                self.sliderToggle()

            # Срабатывает при первом запуске программы

            if utils.settings[1] == "":
                utils.settings[1] = 1
                def __onFirstRun(*args):
                    self.popupForm = "pioneerNorm"
                    self.popup(message=self.msg[7], options=[self.button["yes"], self.button["no"]])
                Clock.schedule_once(__onFirstRun, 3)

            """
            # Если запуск не первый, на телефоне определяем версию и показываем, что новое в случае обновления

            elif self.platform == "mobile":
                vFile = utils.UserPath + "version.ini"
                if os.path.exists(vFile):
                    with open(vFile, mode="r") as file:
                        version = int(file.read())
                    if utils.Code > version:
                        print("new version!")
                        if utils.resources[0][1][3] == 0:
                            self.popup(title=self.msg[328], message=)
                    else:
                        print("old version")
                else:
                    print("version file not found, create it")
                    with open(vFile, "w") as file:
                        file.write(str(utils.Code))"""

        except: # в случае ошибки пытаемся восстановить последнюю резервную копию
            if self.restore < 10:
                if self.devmode == 1:
                    print(f"Файл базы данных поврежден, пытаюсь восстановить резервную копию {self.restore}.")
                result = utils.backupRestore(restoreNumber = self.restore, allowSave=False)
                if result != False:
                    if self.devmode == 1:
                        print("Резервная копия восстановлена.")
                    self.restore += 1
                    self.rep = report.Report()
                    utils.save(backup=False)
                    self.updateList()
                else:
                    if self.devmode == 1:
                        print("Резервных копий больше нет.")
                    self.restore = 10

            else:
                self.popupForm = "emergencyExport"
                self.popup(title=self.msg[9],
                       message=self.msg[10])

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

    def clickOnList(self, instance, mode=""):
        """Действия, которые совершаются на указанных экранах по нажатию на кнопку главного списка"""

        def __do(*args): # действие всегда выполняется с запаздыванием, чтобы отобразилась анимация на кнопке

            if self.msg[6] in instance.text: # "создать подъезд"
                if self.language == "ru":
                    char = 19 # цифра должна точно соответствовать числу символов во фразе msg[6] + 3
                elif self.language == "en":
                    char = 16
                elif self.language == "ka":
                    char = 23
                text = instance.text[char:]
                if "[/i]" in text:
                    text = text[ : text.index("[")]
                self.house.addPorch(text.strip())
                utils.save()
                self.houseView(instance=instance)
            elif self.msg[11] in instance.text: # "создайте"
                self.positivePressed()

            for i in range(len(self.displayed.options)):

                if self.displayed.form == "porchView" or self.displayed.form == "con":
                    if self.showSlider == True:
                        self.showSlider = False
                        self.sliderToggle()
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

                        if len(self.btn) > 10: # определяем индекс нажатой конкретной кнопки скролла, чтобы затем промотать до нее вид
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

        if mode == "floors":
            try:
                number = instance.text[instance.text.index("[b]") + 3: instance.text.index("[/b]")].strip()
            except:
                number = instance.text.strip()
            for i in range(len(self.porch.flats)):
                if number == self.porch.flats[i].number:
                    self.flat = self.porch.flats[i]
                    self.selectedFlat = i  # отсюда знаем квартиру, ее индекс и фактический номер
                    break
            self.flatView(call=False, instance=instance)  # вход в квартиру
        else:
            Clock.schedule_once(__do, 0)

    def titlePressed(self, instance, value):
        def __edit(*args):
            try:
                if value == "title":
                    self.multipleBoxEntries[0].focus = True
                elif value == "note":
                    if self.msg[152] in instance.text:
                        self.multipleBoxEntries[1].focus = True
                    else:
                        for i in range(len(self.multipleBoxEntries)):
                            if self.multipleBoxLabels[i].text == self.msg[18]:
                                self.multipleBoxEntries[i].focus = True
                                break
            except:
                pass

        if value == "title":
            self.detailsPressed()
            Clock.schedule_once(__edit, .3)
        elif value == "report" and utils.settings[0][3] > 0:
            self.popup(title=self.msg[247], message=self.msg[202])
        elif value == "note":
            self.detailsPressed()
            Clock.schedule_once(__edit, .3)

    def detailsPressed(self, instance=None):
        """ Нажата кнопка настроек рядом с заголовком (редактирование данного объекта) """
        self.showSlider = False
        self.sliderToggle()
        if self.displayed.form == "houseView" or self.displayed.form == "noteForHouse" or \
            self.displayed.form == "createNewPorch":  # детали участка
            self.displayed.form = "houseDetails"
            if self.house.type == "private":
                title = self.msg[14]
            else:
                title = self.msg[15]
            self.createMultipleInputBox(
                title=f"{self.house.title} – {self.msg[16]}",
                options=[title, self.msg[17], self.msg[18]],
                defaults=[self.house.title, self.house.date, self.house.note],
                multilines=[False, False, True],
                disabled=[False, False, False]
            )

        elif self.displayed.form == "porchView" or self.displayed.form == "noteForPorch" or \
            self.displayed.form == "createNewFlat": # детали подъезда
            self.displayed.form = "porchDetails"
            if self.porch.type == "сегмент":
                settings = self.msg[20]
            else:
                settings = self.msg[19]
            options = [settings, self.msg[18]]
            defaults = [self.porch.title, self.porch.note]
            self.createMultipleInputBox(
                title=f"{self.house.getPorchType()[1]} {self.porch.title} – {self.msg[16]}",
                options=options,
                defaults=defaults,
                sort="",
                resize="",
                neutral="",
                multilines=[False, True],
                disabled = [False, False]
            )

        elif self.displayed.form == "flatView" or self.displayed.form == "noteForFlat" or\
            self.displayed.form == "createNewRecord" or self.displayed.form == "recordView": # детали квартиры
            self.displayed.form = "flatDetails"
            options = [self.msg[22], self.msg[23], self.msg[15], self.msg[24], self.msg[18]]
            defaults = [self.flat.getName(), self.flat.phone, self.house.title, self.flat.number, self.flat.note]
            multilines = [False, False, False, False, True]
            if self.house.type == "virtual":
                addressDisabled = False
            else:
                addressDisabled = True
            if "подъезд" in self.porch.type or self.flat.number == "virtual":
                numberDisabled = True
            else:
                numberDisabled = False
            disabled = [False, False, addressDisabled, numberDisabled, False]
            if self.house.type == "condo":
                disabled.append(False)
            else:
                disabled.append(True)

            self.createMultipleInputBox(
                title=self.flatTitle + f" – {self.msg[16]}",
                options=options,
                defaults=defaults,
                multilines=multilines,
                disabled=disabled,
                neutral=self.button["phone"]
            )

        elif self.displayed.form == "rep": # журнал отчета
            options=[]
            for line in utils.resources[2]:
                options.append(line)
            if len(options) == 0:
                tip = self.msg[25]
            else:
                tip = None
            self.displayed = Feed(
                title=self.msg[26],
                options=options,
                form="repLog",
                positive="",
                tip=tip
            )
            if instance != None:
                self.stack.insert(0, self.displayed.form)
            self.updateList()

        elif self.displayed.form == "set": # Помощь
            if self.language == "ru":
                webbrowser.open("https://github.com/antorix/Rocket-Ministry/wiki/ru")
            else:
                webbrowser.open("https://github.com/antorix/Rocket-Ministry/wiki")

    def backPressed(self, instance=None):
        """Нажата кнопка «назад»"""

        if len(self.stack) > 0:
            del self.stack[0]

        if self.displayed.form == "repLog":
            self.repPressed()
        elif len(self.stack) > 0:
            if self.stack[0] == "ter":
                self.terPressed()
            elif self.stack[0] == "con":
                self.conPressed()
            elif self.stack[0] == "search":
                self.find()
            elif self.stack[0] == "houseView":
                self.showSlider = False
                self.sliderToggle()
                self.houseView()
            elif self.stack[0] == "porchView" or self.msg[162] in self.pageTitle.text: # первое посещение
                self.porchView()
            elif self.stack[0] == "flatView":
                self.flatView()

        self.updateMainMenuButtons()

    def resizePressed(self, instance=None):
        """ слайдер """
        if utils.resources[0][1][1] == 0:
            utils.resources[0][1][1] = 1
            utils.save()
            self.popup(title=self.msg[247], message=self.msg[300] % self.button['resize'])
        if self.showSlider == True:
            self.showSlider = False
            utils.save()
        else:
            self.showSlider = True
        self.porchView()
        self.sliderToggle("on")

    def sortPressed(self, instance=None):
        self.dropSortMenu.clear_widgets()
        if self.displayed.form == "ter":  # меню сортировки участков
            sortTypes = [
                self.msg[29], # название
                self.msg[30], # дата
                self.msg[31], # интерес
                f"{self.msg[32]} {self.button['down']}", # обработка
                f"{self.msg[32]} {self.button['up']}"    # обработка назад
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
                btn.bind(on_release=__resortHouses)
                self.dropSortMenu.add_widget(btn)
            self.dropSortMenu.bind(on_select=lambda instance, x: setattr(self.sortButton, 'text', x))
            self.sortButton.bind(on_release=self.dropSortMenu.open)

        elif self.displayed.form == "porchView":
            if self.porch.floors() == False: # меню сортировки квартир в подъезде
                sortTypes = [
                    f"{self.msg[34]} {self.button['down']}", # номер
                    f"{self.msg[34]} {self.button['up']}", # номер обратно
                    self.msg[36], # статус
                    self.msg[37], # заметка
                    self.msg[35]  # телефон
                ]
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
                    btn.bind(on_release=__resortFlats)
                    self.dropSortMenu.add_widget(btn)
                self.dropSortMenu.bind(on_select=lambda instance, x: setattr(self.sortButton, 'text', x))
                self.sortButton.bind(on_release=self.dropSortMenu.open)

        elif self.displayed.form == "con":  # меню сортировки контактов
            sortTypes = [
                self.msg[21],
                self.msg[33],
                self.msg[35],
                self.msg[37]
            ]
            for i in range(len(sortTypes)):
                btn = SortListButton(text=sortTypes[i])
                def __resortCons(instance=None):
                    if instance.text == sortTypes[0]:
                        utils.settings[0][4] = "и"
                    elif instance.text == sortTypes[1]:
                        utils.settings[0][4] = "а"
                    elif instance.text == sortTypes[2]:
                        utils.settings[0][4] = "т"
                    elif instance.text == sortTypes[3]:
                        utils.settings[0][4] = "з"
                    utils.save()
                    self.conPressed()
                btn.bind(on_release=__resortCons)
                self.dropSortMenu.add_widget(btn)
            self.dropSortMenu.bind(on_select=lambda instance, x: setattr(self.sortButton, 'text', x))
            self.sortButton.bind(on_release=self.dropSortMenu.open)

    def clearTable(self):
        """ Очистка верхних кнопок таблицы для некоторых форм"""
        self.backButton.disabled = False
        self.detailsButton.disabled = False
        self.sortButton.disabled = True
        self.sortButton.text = ""
        self.resizeButton.disabled = True
        self.resizeButton.text = ""
        self.neutral.disabled = True
        self.neutral.text = ""
        self.navButton.disabled = True
        self.navButton.text = ""
        self.showSlider = False
        self.sliderToggle()

    # Таймер

    def updateTimer(self, *args):
        """ Обновление таймера """
        endTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
            time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
        updated = (endTime - utils.settings[2][6]) / 3600
        if updated >= 0:
            self.time2 = updated
        else:
            self.time2 = updated + 24
        if utils.settings[2][6] > 0:
            if ":" in self.timerText.text:
                mytime = utils.timeFloatToHHMM(self.time2)
                mytime2 = mytime[: mytime.index(":")]
                mytime3 = mytime[mytime.index(":") + 1:]
                mytime4 = f"{mytime2} {mytime3}"
                self.timerText.text = mytime4
            else:
                self.timerText.text = utils.timeFloatToHHMM(self.time2)
        else:
            self.timerText.text = ""
        if self.timerText.text != "":
            self.timer.on()
        else:
            self.timer.off()

    def timerPressed(self, instance=None):
        if utils.resources[0][1][2] == 0:
            self.popup(title=self.msg[247], message=self.msg[217])
            utils.resources[0][1][2] = 1
            utils.save()
        self.updateTimer()
        result = self.rep.toggleTimer()
        if result == 1:
            self.rep.modify(")") # кредит выключен, записываем время служения сразу
            if self.displayed.form == "rep":
                self.repPressed()
        elif result == 2: # кредит включен, сначала спрашиваем, что записать
            self.popupForm = "timerType"
            self.popup(title=self.msg[40], message=self.msg[41], options=[self.msg[42], self.msg[43]])

    # Действия главных кнопок positive, neutral

    def navPressed(self, instance=None):
        #from plyer import maps
        #maps.route(self.house.title)
        #return
        try:
            if self.house.type == "condo":
                dest = self.house.title
            else:
                dest = f"{self.house.title} {self.porch.title}"
            address = f"google.navigation:q={dest}"
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(address))
            mActivity.startActivity(intent)
        except:
            webbrowser.open(f"https://www.google.com/maps/place/{dest}")

    def positivePressed(self, instance=None, value=None):
        """ Что выполняет левая кнопка в зависимости от экрана """
        self.showSlider = False
        self.sliderToggle()

        # Поиск

        if self.msg[146] in self.pageTitle.text:

            input = self.inputBoxEntry.text.lower().strip()

            if input[0:3] == "res" and utils.ifInt(input[3]) == True:  # восстановление резервных копий
                copy = int(input[3])
                if self.devmode == 1:
                    print("Восстанавливаю копию %d" % copy)
                result = utils.backupRestore(restoreNumber=copy, allowSave=False)
                if result == False:
                    self.popup(title=self.msg[44], message=self.msg[45])
                else:
                    self.popup(title="Восстановление данных", message=f"Восстановлена копия {result}.")
                    self.rep = report.Report()
                    self.terPressed()

            elif input == "report000":
                self.rep.checkNewMonth(forceDebug=True)

            elif input == "error000":
                self.updateList(5, 0)

            elif input == "file000":
                def __handleSelection(selection):
                    if len(selection) > 0:
                        file = selection[0]
                        self.pageTitle.text = file
                        self.importDB(file=file)
                plyer.filechooser.open_file(on_selection=__handleSelection)

            elif input != "":
                self.searchQuery = input
                self.find(instance=instance)

        # Отчет

        elif self.displayed.form == "rep":
            if self.reportPanel.current_tab.text == utils.monthName()[0]:
                self.rep.modify()  # для проверки нового месяца
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
                    self.popup(self.msg[46])

                elif success == 1 and change == 1 and self.counterChanged == True:
                    self.rep.placements = temp_placements
                    self.rep.videos = temp_videos
                    self.rep.hours = temp_hours
                    self.rep.returns = temp_returns
                    self.rep.studies = temp_studies
                    if utils.settings[0][2] == 1:
                        self.rep.credit = temp_credit
                        credit = f"{self.msg[47]}, " % utils.timeFloatToHHMM(self.rep.credit)
                    else:
                        credit = ""
                    self.rep.saveReport(
                        message=self.msg[48] % (
                            self.rep.placements,
                            self.rep.videos,
                            utils.timeFloatToHHMM(self.rep.hours),
                            credit,
                            self.rep.returns,
                            self.rep.studies
                        )
                    )
                    self.pageTitle.text = f"[ref=report]{self.msg[4]}{self.rep.getCurrentHours()[2]}[/ref]"

                self.counterChanged = False

            elif self.reportPanel.current_tab.text == self.msg[49]:
                self.recalcServiceYear()

            else:
                if self.rep.getLastMonthReport()[0] != "":
                    utils.log(self.msg[50])
                else:
                    utils.log(self.msg[51])

        # Настройки

        elif self.displayed.form == "set":

            if self.settingsPanel.current_tab.text == self.msg[52]:
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
                utils.settings[0][13] = self.multipleBoxEntries[1].active   # нет дома
                utils.settings[0][15] = self.multipleBoxEntries[2].active   # переносить минуты
                utils.settings[0][18] = self.multipleBoxEntries[3].get()    # цвет отказа
                utils.settings[0][2] = self.multipleBoxEntries[4].active    # кредит
                utils.settings[0][20] = self.multipleBoxEntries[5].active   # показывать телефон
                utils.settings[0][0] = self.multipleBoxEntries[6].active    # уведомление при запуске таймера
                for i in range(len(utils.Languages)):                       # язык
                    if list(utils.Languages.values())[i] in self.languageButton.text:
                        utils.settings[0][6] = list(utils.Languages.keys())[i]
                        break

                utils.settings[0][5] = self.themes[self.themeButton.text]   # тема

                utils.save()
                utils.log(self.msg[53])
                self.restart("soft")
                Clock.schedule_once(self.settingsPressed, .1)

            elif self.settingsPanel.current_tab.text == self.msg[54]:
                utils.save(backup=True)
                utils.log(self.msg[56])

            elif self.settingsPanel.current_tab.text == self.msg[55]:
                utils.resources[0][0] = self.inputBoxEntry.text.strip()
                utils.save()

        # Форма создания квартир/домов

        elif self.displayed.form == "porchView":
            self.clearTable()
            self.displayed.form = "createNewFlat"
            if self.house.type == "condo": # многоквартирный дом
                if len(self.porch.flats) > 0:
                    self.stack.insert(0, self.stack[0])
                self.mainList.clear_widgets()
                self.pageTitle.text = f"{self.msg[57]} {self.porch.title}"
                self.positive.text = self.button["save"]
                self.negative.text = self.button["cancel"]
                a = AnchorLayout(anchor_x="center", anchor_y="top")
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

                grid.add_widget(MyLabel(text=self.msg[58], halign=align, valign=align, color=self.standardTextColor,
                                      text_size=text_size))
                b1 = BoxLayout()
                b1.add_widget(MyLabel(text=self.msg[59], color=self.standardTextColor))
                a1 = AnchorLayout(anchor_x="center", anchor_y="center")
                self.flatRangeStart = MyTextInput(text=firstflat, multiline=False, size_hint_y=None, size_hint_x=None,
                                                height=self.standardTextHeight, width=self.counterHeight*.6,
                                                input_type="number", shrink=False)
                a1.add_widget(self.flatRangeStart)
                b1.add_widget(a1)
                b1.add_widget(MyLabel(text=self.msg[60], color=self.standardTextColor))
                a2 = AnchorLayout(anchor_x="center", anchor_y="center")
                self.flatRangeEnd = MyTextInput(text=lastflat, multiline=False, size_hint_y=None, size_hint_x=None,
                                              height=self.standardTextHeight, width=self.counterHeight*.6,
                                              input_type="number", shrink=False)
                a2.add_widget(self.flatRangeEnd)

                b1.add_widget(a2)
                grid.add_widget(b1)
                grid.add_widget(MyLabel(text=self.msg[61], halign=align, valign=align, color=self.standardTextColor,
                                      text_size=text_size))
                self.floors = Counter(text=floors, size_hint=(.7, .5), fixed=True, shrink=False)
                grid.add_widget(self.floors)
                grid.add_widget(MyLabel(text=self.msg[62], halign=align, valign=align, color=self.standardTextColor,
                                      text_size=text_size))
                self.floor1 = Counter(text=str(self.porch.floor1), size_hint=(.7, .5), fixed=True, shrink=False)
                grid.add_widget(self.floor1)
                grid.add_widget(Widget())
                grid.add_widget(self.flatListButton())
                a.add_widget(grid)
                self.mainList.add_widget(a)

            else: # универсальный участок
                self.createInputBox(
                    title=self.msg[63],
                    message=self.msg[64],
                    checkbox=self.msg[65],
                    active=False,
                    hint=self.msg[66]
                )
                self.mainList.add_widget(self.flatListButton())

        # Формы добавления

        elif self.displayed.form == "ter": # добавление участка
            self.detailsButton.disabled = True
            self.displayed.form = "createNewHouse"
            if self.language == "ru":
                active = True
                hint = self.msg[70]
            else:
                active = False
                hint = self.msg[166]
            self.createInputBox(
                title=self.msg[67],
                checkbox=self.msg[68],
                active=active,
                message=self.msg[69],
                sort="",
                hint=hint,
                tip=self.msg[71]
            )

        elif self.displayed.form == "houseView": # добавление подъезда
            self.displayed.form = "createNewPorch"
            if self.house.type == "condo":
                message=self.msg[72]
                hint=self.msg[73]
                tip=self.msg[74]
            else:
                message = self.msg[75]
                hint = self.msg[76]
                tip = self.msg[77]
            self.createInputBox(
                title=f"{self.msg[78]} {self.house.getPorchType()[1]}",
                message=message,
                hint=hint,
                tip=tip
            )

        elif self.displayed.form == "con": # добавление контакта
            self.detailsButton.disabled = True
            self.displayed.form = "createNewCon"
            self.createInputBox(
                title=self.msg[79],
                message=self.msg[80],
                multiline=False,
                sort="",
                tip=self.msg[81]
            )

        elif self.displayed.form == "flatView": # добавление посещения
            if len(self.flat.records) > 0:
                self.displayed.form = "createNewRecord" # в этом случае позитивная кнопка - создание посещения
                self.createInputBox(
                    title=f"{self.flatTitle} – {self.msg[82]}",
                    message=self.msg[83],
                    multiline=True,
                    addCheckBoxes=True,
                    details=self.button["cog"] + self.flatType,
                    neutral=self.button["phone"]
                )
            else: # в этом случае - сохранение первого посещения и выход в подъезд
                newName = self.multipleBoxEntries[0].text.strip()
                if newName != "":
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

        elif self.displayed.form == "createNewRecord": # добавление новой записи посещения (повторное)
            self.displayed.form = "flatView"
            record = self.inputBoxEntry.text.strip()
            self.flat.addRecord(record)
            self.processReportCounters()
            utils.save()
            self.flatView()

        # Формы сохранения

        elif self.displayed.form == "createNewHouse":  # сохранение участка
            self.displayed.form = "ter"
            newTer = self.inputBoxEntry.text
            condo = self.checkbox.active
            if newTer == "":
                self.inputBoxText.text = self.msg[84]
            else:
                for house in utils.houses:
                    if newTer.strip() == house.title.strip():
                        self.popup(self.msg[85])
                        self.terPressed()
                        self.positivePressed()
                        break
                else:
                    if self.language == "ka":
                        forceUpper = False
                        utils.addHouse(utils.houses, newTer, condo, forceUpper=forceUpper)
                        utils.log(self.msg[86] % newTer)
                    else:
                        forceUpper = True
                        utils.addHouse(utils.houses, newTer, condo, forceUpper=forceUpper)
                        utils.log(self.msg[86] % newTer.upper())
                    utils.save()
                    self.terPressed()

        elif self.displayed.form == "createNewPorch":  # сохранение подъезда
            self.displayed.form = "houseView"
            newPorch = self.inputBoxEntry.text
            if newPorch == None:
                self.houseView()
                self.updateList()
            elif newPorch == "":
                self.inputBoxText.text = self.msg[84]
            else:
                for porch in self.house.porches:
                    if newPorch.strip() == porch.title:
                        self.popup(self.msg[87] % self.house.getPorchType()[1])
                        self.houseView()
                        self.positivePressed()
                        break
                else:
                    self.house.addPorch(newPorch, self.house.getPorchType()[0])
                    utils.save()
                    self.houseView()

        elif self.displayed.form == "createNewFlat": # сохранение квартир
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
                    self.popup(message = self.msg[88])
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
                        self.popup(self.msg[89])
                        self.porchView()
                        self.positivePressed()
                else:
                    try:
                        if int(addFlat) > int(addFlat2):
                            5/0
                        self.porch.addFlats("+%d-%d" % (int(addFlat), int(addFlat2)))
                    except:
                        self.popup(self.msg[90])
                        def __repeat(*args):
                            self.porchView()
                            self.positivePressed()
                            self.checkbox.active = True
                        Clock.schedule_once(__repeat, 0.5)
                    else:
                        utils.save()
                        self.porchView()

        elif self.displayed.form == "recordView": # сохранение существующей записи посещения
            self.displayed.form = "flatView"
            newRec = self.inputBoxEntry.text.strip()
            self.flat.editRecord(self.selectedRecord, newRec)
            utils.save()
            self.flatView()

        elif self.displayed.form == "createNewCon": # сохранение контакта
            self.displayed.form = "con"
            name = self.inputBoxEntry.text.strip()
            if name != "":
                utils.addHouse(utils.resources[1], "", "virtual")  # создается новый виртуальный дом
                utils.resources[1][len(utils.resources[1]) - 1].addPorch(input="virtual", type="virtual")
                utils.resources[1][len(utils.resources[1]) - 1].porches[0].addFlat("+" + name, virtual=True)
                utils.resources[1][len(utils.resources[1]) - 1].porches[0].flats[0].status = "1"
                utils.log(self.msg[91] % utils.resources[1][len(utils.resources[1]) - 1].porches[0].flats[0].getName())
                utils.save()
                self.conPressed()
            else:
                self.inputBoxText.text = self.msg[84]


        # Детали

        elif self.displayed.form == "houseDetails":  # детали участка
            self.displayed.form = "houseView"
            self.house.note = self.multipleBoxEntries[2].text.strip()
            if self.language == "ka": # для грузинского без заглавных букв
                newTitle = self.multipleBoxEntries[0].text.strip()  # попытка изменить адрес - сначала проверяем, что нет дублей
            else:
                newTitle = self.multipleBoxEntries[0].text.upper().strip()
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
                self.popup(self.msg[85])
                return

            newDate = self.multipleBoxEntries[1].text.strip()
            if utils.checkDate(newDate)==True:
                self.house.date = newDate
                utils.save()
                self.houseView()
            else:
                self.detailsPressed()
                self.multipleBoxEntries[1].text = newDate
                self.popup(self.msg[92])
                return

        elif self.displayed.form == "porchDetails":  # детали подъезда
            self.displayed.form = "porchView"
            self.porch.note = self.multipleBoxEntries[1].text.strip()
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
                self.popup(self.msg[87] % self.house.getPorchType()[1])

        elif self.displayed.form == "flatDetails":  # детали квартиры
            success = True
            self.displayed.form = "flatView"
            self.flat.note = self.multipleBoxEntries[4].text.strip()
            newName = self.multipleBoxEntries[0].text.strip()
            if newName != "" or self.house.type != "virtual":
                self.flat.updateName(newName)
            self.flat.editPhone(self.multipleBoxEntries[1].text.strip())
            if self.house.type == "virtual":
                self.house.title = self.multipleBoxEntries[2].text.strip()
            elif self.house.type != "condo": # попытка изменить номер дома - сначала проверяем, что нет дублей
                newNumber = self.multipleBoxEntries[3].text.strip()
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
                    self.multipleBoxEntries[3].text = newNumber
                    self.popup(self.msg[93])
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
            if utils.resources[0][1][3] == 0:
                self.popup(title=self.msg[247], message=self.msg[171])
                utils.resources[0][1][3] = 1
                utils.save()
            if self.porch.floors() == True:
                self.porch.flatsLayout = "н"
            elif self.porch.floors() == False:
                self.porch.flatsLayout = self.porch.type[7:] # определение этажей по цифре в типе подъезда
                if self.porch.flatsLayout == "":
                    self.popup(self.msg[94])
            utils.save()
            self.porchView()

        elif self.button["phone"] in instance.text:
            inform = self.msg[28] % self.flat.phone
            if self.flat.phone.strip() == "":
                utils.log(self.msg[27])
            else:
                if self.platform == "mobile":
                    try:
                        plyer.call.makecall(tel=self.flat.phone)
                    except:
                        Clipboard.copy(self.flat.phone)
                        self.popup(inform)

                else:
                    Clipboard.copy(self.flat.phone)
                    self.popup(inform)

    def updateMainMenuButtons(self, deactivateAll=False):
        """ Обновляет статус трех главных кнопок """
        #return
        if deactivateAll == True:
            self.buttonRep.deactivate()
            self.buttonTer.deactivate()
            self.buttonCon.deactivate()
        elif self.displayed.form == "rep":
            self.buttonRep.activate()
            self.buttonTer.deactivate()
            self.buttonCon.deactivate()
        elif self.displayed.form == "con" or self.contactsEntryPoint == True:
            self.buttonCon.activate()
            self.buttonTer.deactivate()
            self.buttonRep.deactivate()
        elif self.displayed.form == "ter" or "view" in self.displayed.form.lower():
            self.buttonTer.activate()
            self.buttonCon.deactivate()
            self.buttonRep.deactivate()

    # Действия других кнопок

    def terPressed(self, instance=""):
        self.buttonTer.activate()
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
                houseDue = "[color=F4CA16]" + self.button['warn']+" [/color]"
            else:
                houseDue = ""
            if house.type == "condo":
                listIcon = icon('icon-building-filled')
            else:
                listIcon = icon('icon-home-1')

            housesList.append( f"{listIcon} {house.title} ({utils.shortenDate(house.date)}) " +\
                               f"[i]{int(house.getProgress()[0] * 100)}%[/i]{interested}{houseDue}")

        if len(housesList) == 0:
            housesList.append(self.msg[95])

        self.displayed = Feed(  # display list of houses and options
            title=f"{self.msg[2]} ({len(utils.houses)})",
            message=self.msg[97],
            options=housesList,
            form="ter",
            sort=self.button['sort'],
            positive=f"{self.button['plus']} {self.msg[98]}",
            back=False
        )
        if instance != None:
            self.stack.insert(0, self.displayed.form)
        self.updateList()
        self.updateMainMenuButtons()

    def conPressed(self, instance=None):
        self.buttonCon.activate()
        self.contactsEntryPoint = 1
        self.searchEntryPoint = 0
        self.showSlider = False
        self.sliderToggle()
        self.allcontacts = self.getContacts()
        options = []

        # Sort
        if utils.settings[0][4] == "и":
            self.allcontacts.sort(key=lambda x: x[0]) # by name
        elif utils.settings[0][4] == "с":
            self.allcontacts.sort(key=lambda x: x[16]) # by status
        elif utils.settings[0][4] == "а":
            self.allcontacts.sort(key=lambda x: x[2]) # by address
        elif utils.settings[0][4] == "т":
            self.allcontacts.sort(key=lambda x: x[9], reverse=True) # by phone number
        elif utils.settings[0][4] == "з":
            self.allcontacts.sort(key=lambda x: x[11], reverse=True) # by note

        for i in range(len(self.allcontacts)):
            if self.allcontacts[i][15] != "condo" and self.allcontacts[i][15] != "virtual":
                porch = self.allcontacts[i][12] + ", "
                gap = ", "
            else:
                porch = gap = ""
            if self.allcontacts[i][5] != "":
                appointment = "%s " % self.allcontacts[i][5][0:5] # appointment
            else:
                appointment = ""
            if self.allcontacts[i][9] != "":
                phone = "%s\u00A0%s " % (self.button['phone1'], self.allcontacts[i][9]) # phone
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
                note = self.button["note"] + "\u00A0" + self.allcontacts[i][11]
            else:
                note = ""

            listIcon = f"[color=00BD80]" + self.button['user'] + "[/color]"
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
            tip = self.msg[99]
        else:
            tip = None

        self.displayed = Feed(
            form="con",
            title=f"{self.msg[3]} ({len(self.allcontacts)})",
            message=self.msg[96],
            options=options,
            sort=self.button['sort'],
            positive=f"{self.button['plus']} {self.msg[100]}",
            back=False,
            tip=tip
        )
        if instance != None:
            self.stack.insert(0, self.displayed.form)
        self.updateList()

        if len(options) >= 10:
            try:  # пытаемся всегда вернуться на последний контакт
                self.scroll.scroll_to(widget=self.btn[self.clickedBtnIndex], padding=0, animate=False)
            except:
                pass

        self.updateMainMenuButtons()

    def repPressed(self, instance=None):
        self.buttonRep.activate()
        if len(self.stack) > 0:
            self.stack.insert(0, self.stack[0]) # дублирование последнего шага стека, чтобы предотвратить уход со страницы
        self.clearTable()
        self.counterChanged = False
        self.neutral.disabled = True
        self.neutral.text = ""
        self.sortButton.disabled = True
        self.sortButton.text = ""
        self.resizeButton.disabled = True
        self.resizeButton.text = ""
        self.detailsButton.text = f"{self.button['log']} {self.msg[101]}"
        self.detailsButton.disabled = False
        self.displayed.form = "rep"
        self.positive.text = self.button["save"]
        self.positive.disabled = False
        self.negative.text = self.button["cancel"]
        self.negative.disabled = False
        self.pageTitle.text = f"[ref=report]{self.msg[4]}{self.rep.getCurrentHours()[2]}[/ref]"

        self.reportPanel = TabbedPanel(background_color=self.globalBGColor0, background_image="")
        text_size = (Window.size[0] / 3, None)
        self.mainList.clear_widgets()

        # Первая вкладка: отчет прошлого месяца

        tab2 = TTab(text=utils.monthName()[2])

        report2 = AnchorLayout(anchor_x="center", anchor_y="center")

        send = f"\n{self.button['share']} {self.msg[110]}"

        if self.rep.getLastMonthReport()[0] == "":
            self.btnRep = self.tip(self.msg[111])
        else:
            self.btnRep = RButton(text=self.rep.getLastMonthReport()[0]+send, halign="left",
                                  size=(Window.size[0] * .7, Window.size[1] * .5), size_hint_x=.7, size_hint_y=.5)
        if self.orientation == "h":
            self.btnRep.size_hint_x = .5
            self.btnRep.size_hint_y = .8
        self.btnRep.bind(on_release=self.sendLastMonthReport)

        report2.add_widget(self.btnRep)
        tab2.content = report2
        self.reportPanel.add_widget(tab2)
        self.reportPanel.do_default_tab = False

        # Вторая вкладка: текущий месяц

        tab1 = TTab(text=utils.monthName()[0])
        a = AnchorLayout(anchor_x="center", anchor_y="center")
        report = GridLayout(cols=2, rows=7, spacing=self.spacing, padding=self.padding, pos_hint={"center_x": .7})

        report.add_widget(MyLabel(text=self.msg[102], halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.placements = Counter(text = str(self.rep.placements), fixed=1, shrink=False)
        report.add_widget(self.placements)

        report.add_widget(MyLabel(text=self.msg[103], halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.video = Counter(text=str(self.rep.videos), fixed=1, shrink=False)
        report.add_widget(self.video)

        report.add_widget(MyLabel(text=self.msg[104], halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.hours = Counter(picker=self.msg[105], type="time",
                             text=utils.timeFloatToHHMM(self.rep.hours), fixed=1, shrink=False)
        report.add_widget(self.hours)

        if utils.settings[0][2]==1:
            report.add_widget(MyLabel(text=self.msg[106] % self.rep.getCurrentHours()[0], markup=True,
                                    halign="center", valign="center", text_size = text_size, color=self.standardTextColor))
            self.credit = Counter(picker=self.msg[107], type="time",
                                  text=utils.timeFloatToHHMM(self.rep.credit), fixed=1, mode="pan")
            report.add_widget(self.credit)

        report.add_widget(MyLabel(text=self.msg[108], halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.returns = Counter(text = str(self.rep.returns), fixed=1, mode="pan")
        report.add_widget(self.returns)

        report.add_widget(MyLabel(text=self.msg[109], halign="center", valign="center", text_size = text_size,
                                color=self.standardTextColor, markup=True))
        self.studies = Counter(text = str(self.rep.studies), fixed=1, mode="pan")
        report.add_widget(self.studies)

        a.add_widget(report)
        tab1.content = a
        self.reportPanel.add_widget(tab1)

        # Третья вкладка: служебный год

        if utils.settings[0][3] > 0:
            tab3 = TTab(text=self.msg[49])

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
            width = self.standardTextWidth*1.3
            height = self.standardTextHeight * k

            report3 = AnchorLayout(anchor_x="center", anchor_y="center")

            b3 = BoxLayout(spacing=spacing, padding=self.padding)
            mGrid = GridLayout(rows=12, cols=2, size_hint=(x, y), padding=spacing, spacing=spacing,
                                row_force_default = row_force_default,
                                col_default_width=width, row_default_height = height,
                                pos_hint={"center_y": .5})
            self.months = []

            for i, month in zip(range(12),
                                [self.msg[112], self.msg[113], self.msg[114], self.msg[115], self.msg[116],
                                 self.msg[117], self.msg[118], self.msg[119], self.msg[120], self.msg[121],
                                 self.msg[122], self.msg[123]]): # месяцы года

                mGrid.add_widget(MyLabel(text=month, halign="center", valign="center", width=width, height=height,
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
                self.analyticsMessage = MyLabel(markup=True, color=self.standardTextColor, valign="center",
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

        self.mainList.add_widget(self.reportPanel)

        Clock.schedule_once(lambda dt: self.reportPanel.switch_to(tab1), 0)

    def settingsPressed(self, instance=None):
        """ Настройки """

        if len(self.stack) > 0:
            self.stack.insert(0, self.stack[0]) # дублирование последнего шага стека, чтобы предотвратить уход со страницы
        self.displayed.form = "set"
        self.updateMainMenuButtons(deactivateAll=True)
        self.clearTable()
        self.mainList.clear_widgets()
        box = BoxLayout(orientation="vertical")
        self.settingsPanel = TabbedPanel(background_color=self.globalBGColor0)

        self.createMultipleInputBox(
            form=box,
            title="",#"Настройки",
            options=[
                self.msg[124], # норма часов
                "{}" + self.msg[125] % self.msg[206], # нет дома {} = вместо строки ввода должна быть галочка
                "{}" + self.msg[126], # переносить минуты
                "<>" + self.msg[127], # выбор цвета отказа
                "{}" + self.msg[128], # кредит часов
                "{}" + self.msg[129], # быстрый ввод телефона
                "{}" + self.msg[130], # уведомление при таймере
                "()" + self.msg[131], # язык () = togglebutton
            ],
            defaults=[
                utils.settings[0][3],   # норма часов
                utils.settings[0][13],  # нет дома
                utils.settings[0][15],  # переносить минуты
                utils.settings[0][18],  # цвет отказа
                utils.settings[0][2],   # кредит часов
                utils.settings[0][20],  # показывать телефон
                utils.settings[0][0],   # уведомление при запуске таймера
                utils.settings[0][6]    # язык
            ],
            multilines=[False, False, False, False, False, False, False, False]
        )
        #self.pageTitle.text = "123"

        """ Также заняты настройки:
        utils.settings[0][1] - позиция подъезда в окне
        utils.settings[0][4] - сортировка контактов
        utils.settings[0][5] - тема интерфейса
        utils.settings[0][7] - масштабирование подъезда
        utils.settings[0][8] - значение слайдера        
        """

        # Первая вкладка: настройки

        tab1 = TTab(text=self.msg[52])
        tab1.content = box
        self.settingsPanel.add_widget(tab1)

        # Вторая вкладка: работа с данными

        text_size = [Window.size[0]/2.5, Window.size[1]/2.5]
        tab2 = TTab(text=self.msg[54])
        g = GridLayout(rows=2, cols=2, spacing="10dp", padding=[30, 30, 30, 30])

        exportEmail = RButton(text=f"{self.button['export']} {self.msg[132]}", size=text_size)
        def __export(instance):
            if self.platform == "mobile":
                utils.share(email=True)
            else:
                utils.share(file=True)
        exportEmail.bind(on_release=__export)
        g.add_widget(exportEmail)

        importBtn = RButton(text=f"{self.button['import']} {self.msg[133]}", size=text_size)
        importBtn.bind(on_release=self.importDB)
        g.add_widget(importBtn)

        if self.platform == "desktop":
            g.rows += 1
            importFile = RButton(text=f"{self.button['open']} {self.msg[134]}", size=text_size)

            def __importFile(instance):
                from tkinter import filedialog
                file = filedialog.askopenfilename()
                if file != "":
                    self.importDB(file=file)
                """def __handleSelection(selection):
                    if len(selection)>0:
                        file = selection[0]
                        self.importDB(file=file)
                plyer.filechooser.open_file(on_selection=__handleSelection)"""

            importFile.bind(on_release=__importFile)
            g.add_widget(importFile)

        restoreBtn = RButton(text=f"{self.button['restore']} {self.msg[135]}", size=text_size)
        def __restore(instance):
            self.popup(
                message=self.msg[137],
                options=[self.button["yes"], self.button["no"]])
            self.popupForm = "restoreData"
        restoreBtn.bind(on_release=__restore)
        g.add_widget(restoreBtn)

        clearBtn = RButton(text=f"{self.button['wipe']} {self.msg[136]}", size=text_size)
        def __clear(instance):
            self.popup(message=self.msg[138], options=[self.button["yes"], self.button["no"]])
            self.popupForm = "clearData"
        clearBtn.bind(on_release=__clear)
        g.add_widget(clearBtn)

        tab2.content = g
        self.settingsPanel.add_widget(tab2)

        # Третья вкладка: о программе

        tab3 = TTab(text=self.msg[139])
        a = AnchorLayout(anchor_x="center", anchor_y="center")
        aboutBtn = MyLabel(text=
                          f"[color={self.titleColor2}][b]Rocket Ministry {utils.Version}[/b][/color]\n\n" +\
                          f"{self.msg[140]}\n\n" + \
                          f"{self.msg[141]}:\n[ref=telegram][color={self.titleColor2}]{icon('icon-telegram')} [u]RocketMinistry[/u][/color][/ref]\n\n" +\
                          f"{self.msg[142]} [ref=web][color={self.titleColor2}][u]{self.msg[143]}[/u][/color][/ref]\n\n" % icon('icon-github') +\
                          f"{self.msg[308]} [ref=email][color={self.titleColor2}]{icon('icon-mail-alt')} [u]antorix@outlook.com[/u][/color][/ref]\n\n" + \
                          f"Startup image: [ref=vecteezy][color={self.titleColor2}][u]Vecteezy.com[/u][/color]",

            markup=True, halign="left", valign="center", color=self.standardTextColor,
            text_size=[self.mainList.size[0]*.8, None]
            )
        def __click(instance, value):
            if value == "telegram":
                webbrowser.open("https://t.me/rocketministry")
            elif value == "web":
                if self.language == "ru":
                    webbrowser.open("https://github.com/antorix/Rocket-Ministry/wiki/ru")
                else:
                    webbrowser.open("https://github.com/antorix/Rocket-Ministry/")
            elif value == "email":
                webbrowser.open("mailto:antorix@outlook.com")
            elif value == "vecteezy":
                webbrowser.open("https://www.vecteezy.com/free-vector/modern")
        aboutBtn.bind(on_ref_press=__click)
        a.add_widget(aboutBtn)
        tab3.content = a
        self.settingsPanel.add_widget(tab3)
        self.settingsPanel.do_default_tab = False
        self.mainList.add_widget(self.settingsPanel)

        # Четвертая вкладка: блокнот

        tab4 = TTab(text=self.msg[55])
        a4 = AnchorLayout(anchor_x="center", anchor_y="center")

        self.backButton.disabled = False
        self.showSlider = False
        self.detailsButton.text = ""
        self.detailsButton.disabled = True
        self.sliderToggle()
        self.createInputBox(
            form=a4,
            default=utils.resources[0][0],
            multiline=True,
            details=f"{self.button['help']} {self.msg[144]}",
            hint=self.msg[145]
        )
        tab4.content = a4
        self.settingsPanel.add_widget(tab4)

        #self.pageTitle.text = "Настройки"

    def searchPressed(self, instance=None):
        self.clearTable()
        if self.platform == "desktop" or self.model != "huawei":
            focus = True
        else:
            focus = False
        self.createInputBox(
            title=self.msg[146],
            message=self.msg[147],
            multiline=False,
            positive=f"{self.button['search2']} {self.msg[148]}",
            details="",
            focus=focus
        )
        self.updateMainMenuButtons(deactivateAll=True)

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
            options.append(self.msg[149])

        self.displayed = Feed(
            form="search",
            title=f"{self.msg[150]}" % self.searchQuery,
            message=self.msg[151],
            options=options,
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

        if self.house.note != "":
            note = self.house.note
        else:
            note = None

        self.displayed = Feed(
            form="houseView",
            title=f"{house.title}",
            options=house.showPorches(),
            details=f"{self.button['cog']} {self.msg[153]}",
            positive=f"{self.button['plus']} {self.msg[154]} {house.getPorchType()[1]}",
            tip=[note, "note"]
        )
        if instance != None:
            self.stack.insert(0, self.displayed.form)
        self.updateList()
        if house.due() == True:
            self.mainList.add_widget(self.tip(text=self.msg[152], icon="warn"))
            self.mainList.add_widget(Widget(size_hint_y=None))

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
            positive = f" {self.msg[155]}"
        else:
            positive = f" {self.msg[156]}"

        if "подъезд" in self.porch.type:
            segment = f", {self.msg[157]} {self.porch.title}"
        else:
            segment = f", {self.porch.title}"

        options = porch.showFlats()

        if self.house.type != "condo":
            neutral = ""
        elif self.porch.floors() == True:
            neutral = self.button['fgrid']
        elif not "подъезд" in self.porch.type:
            neutral = ""
        else:
            neutral = self.button['flist']
        if self.porch.note != "":
            note = self.porch.note
        else:
            note = None
        if self.porch.floors() == True:
            noteButton = self.button["resize"]
            note = None
            sort = None
        else:
            noteButton = None
            sort = self.button["sort"]

        if self.language == "ka": # для грузинского без заглавных букв
            porch = f" {self.house.getPorchType()[1]}"
        else:
            porch = f" {self.house.getPorchType()[1][0].upper()}{self.house.getPorchType()[1][1:]}"

        self.displayed = Feed(
            title=self.house.title+segment,
            options=options,
            form="porchView",
            sort=sort,
            resize=noteButton,
            details=self.button["cog"] + porch,
            positive=self.button["plus"] + positive,
            neutral=neutral,
            tip=[note, "note"]
        )
        if instance != None:
            self.stack.insert(0, self.displayed.form)
        self.updateList()

        if self.house.type == "condo" and len(self.porch.flats) == 0: # если нет квартир, сразу форма создания
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
            flatPrefix = f"{self.msg[214]} "
        else:
            flatPrefix = ""
        self.flatTitle = (flatPrefix + number + flat.getName()).strip()

        records = flat.showRecords()

        if self.flat.number == "virtual" or self.contactsEntryPoint == 1:
            self.flatType = f" {self.msg[158]}"
        elif self.house.type == "condo":
            self.flatType = f" {self.msg[159]}"
        else:
            self.flatType = f" {self.msg[63]}"

        if self.flat.note != "":
            note = self.flat.note
        else:
            note = None
        self.displayed = Feed(
            title=self.flatTitle,
            message=self.msg[160],
            options=records,
            form="flatView",
            details=self.button["cog"] + self.flatType,
            positive=f"{self.button['plus']} {self.msg[161]}",
            neutral=self.button["phone"],
            tip=[note, "note"]
        )
        if call == False and self.flat.status == "": # всплывающее окно первого посещения
            self.popup(firstCall=True)

        else:
            if len(self.flat.records) == 0:  # если нет посещения, открывается специальное окно первого посещения
                self.scrollWidget.clear_widgets()
                self.navButton.disabled = False
                self.navButton.text = self.button['nav']
                self.createMultipleInputBox(
                    title=f"{self.flatTitle} — {self.msg[162]}",
                    options=[self.msg[22], self.msg[83]],
                    defaults=[self.flat.getName(), ""],
                    multilines=[False, True],
                    disabled=[False, False],
                    details=self.button["cog"] + self.flatType,
                    neutral=self.button["phone"],
                    resize="",
                    sort="",
                    addCheckBoxes=True
                )
            else:
                if instance != None:
                    self.stack.insert(0, self.displayed.form)
                self.updateList()

            if self.contactsEntryPoint == 0 and self.searchEntryPoint == 0:
                self.colorBtn = []
                for i, status in zip(range(7), ["0", "1", "2", "3", "4", "5", ""]):
                    self.colorBtn.append(ColorStatusButton(status))
                    if status == self.flat.getStatus()[0][1]:
                        self.colorBtn[i].text = self.button["dot"]
                        self.colorBtn[i].markup = True

                colorBox = BoxLayout(size_hint_y=None, height=self.mainList.size[0]/7,
                                     spacing=self.spacing*2, padding=(self.padding * 2, self.padding))
                if self.orientation == "h":
                    colorBox.height = self.standardTextHeight
                colorBox.add_widget(self.colorBtn[1])
                colorBox.add_widget(self.colorBtn[2])
                colorBox.add_widget(self.colorBtn[3])
                colorBox.add_widget(self.colorBtn[4])
                colorBox.add_widget(self.colorBtn[0])
                colorBox.add_widget(self.colorBtn[5])
                colorBox.add_widget(self.colorBtn[6])
                self.mainList.add_widget(colorBox)

            if len(records) >= 10:
                try:  # пытаемся всегда вернуться на последнюю запись посещения
                    self.scroll.scroll_to(widget=self.btn[self.clickedBtnIndex], padding=0, animate=False)
                except:
                    pass

    def recordView(self, instance=None):
        self.displayed.form = "recordView"
        self.createInputBox(
            title = f"{self.flatTitle} – {self.msg[164]} {self.record.date}",
            message = self.msg[83],
            default = self.record.title,
            multiline=True,
            details=self.button["cog"] + self.flatType,
            neutral=self.button["phone"]
        )

    # Диалоговые окна

    def createInputBox(self, title="", form=None, message="", default="", hint="", checkbox=None, active=True, input=True,
                       positive=None, sort=None, resize=None, details=None, neutral=None, multiline=False, tip=None,
                       addCheckBoxes=False, focus=False):
        """ Форма ввода данных с одним полем """
        if len(self.stack) > 0:
            self.stack.insert(0, self.stack[0]) # дублирование последнего шага стека, чтобы предотвратить уход со страницы
        if form == None:
            form = self.mainList
        form.clear_widgets()
        self.backButton.disabled = False
        self.inputForm = "single"
        self.pageTitle.text = f"[ref=title]{title}[/ref]"
        self.positive.disabled = False
        self.negative.text = self.button["cancel"]
        self.negative.disabled = False

        if positive != None:
            self.positive.text = positive
        else:
            self.positive.text = self.button["save"]


        if neutral != None:
            self.neutral.text = neutral
            self.neutral.disabled = False
        if sort == "":
            self.sortButton.text = sort
            self.sortButton.disabled = True
        elif sort != None:
            self.sortButton.text = sort
            self.sortButton.disabled = False
        if resize != None:
            self.resizeButton.text = resize
            self.resizeButton.disabled = False
        if details == "":
            self.detailsButton.text = details
            self.detailsButton.disabled = True
        elif details != None:
            self.detailsButton.text = details
            self.detailsButton.disabled = False

        pos_hint = {"top": 1}
        grid = GridLayout(rows=2, cols=1, spacing=self.spacing, padding=self.padding*2)

        if message != "":
            self.inputBoxText = MyLabel(text=message, color=self.standardTextColor, valign="center",
                                  halign="center", text_size = (Window.size[0]*.9, None),
                                  size_hint_y=None)
            grid.add_widget(self.inputBoxText)

        if input == True:
            textbox = BoxLayout(padding=(0, self.padding))
            if multiline == False:
                size_hint_y = None
            else:
                size_hint_y = 1
            self.inputBoxEntry = MyTextInput(multiline=multiline, hint_text=hint, size_hint_y=size_hint_y,
                                             height=self.standardTextHeight, pos_hint=pos_hint, focus=focus)
            textbox.add_widget(self.inputBoxEntry)
            grid.add_widget(textbox)

        if checkbox != None: # если заказана галочка, добавляем
            if self.orientation == "v":
                grid.rows += 2
                grid.add_widget(Widget())
                gridCB = GridLayout(rows=2, size_hint_y=None)
            else:
                grid.rows += 1
                gridCB = GridLayout(rows=2)
            self.checkbox = MyCheckBox(active=active)
            gridCB.add_widget(self.checkbox)

            def __on_checkbox_active(checkbox, value): # что происходит при активированной галочке
                if self.displayed.form == "createNewHouse":
                    if value == 1:
                        self.inputBoxText.text = message
                        self.inputBoxEntry.hint_text = self.msg[70]
                    else:
                        self.inputBoxText.text = self.msg[165]
                        self.inputBoxEntry.hint_text = self.msg[166]
                elif self.displayed.form == "createNewFlat":
                    if value == 1:
                        self.inputBoxText.text = self.msg[167]
                        filled = self.inputBoxEntry.text
                        textbox.remove_widget(self.inputBoxEntry)
                        height = self.standardTextHeight
                        self.inputBoxEntry = MyTextInput(text=filled, hint_text=self.msg[59], multiline=multiline, height=height,
                                                       size_hint_x=Window.size[0]/2, size_hint_y=None, pos_hint=pos_hint,
                                                       input_type="number")
                        textbox.add_widget(self.inputBoxEntry)
                        self.inputBoxEntry2 = MyTextInput(hint_text = self.msg[60], multiline=multiline, height=height,
                                                        size_hint_x=Window.size[0]/2, size_hint_y=None, pos_hint=pos_hint,
                                                        input_type="number")
                        textbox.add_widget(self.inputBoxEntry2)
                    else:
                        self.porchView()
                        self.positivePressed()

            self.checkbox.bind(active=__on_checkbox_active)
            gridCB.add_widget(MyLabel(text=checkbox, color=self.standardTextColor))
            grid.add_widget(gridCB)

        self.inputBoxEntry.text = default

        if addCheckBoxes == True: # добавление галочек нового посещения
            grid.rows += 1
            grid.add_widget(self.reportBoxes(addReturn=True))

        if tip != None: # добавление подсказки
            tipText = self.tip(tip)
            if self.orientation == "v":
                grid.rows += 3
                grid.add_widget(Widget())
                grid.add_widget(tipText)
                grid.add_widget(Widget())
            else:
                grid.rows += 1
                grid.add_widget(tipText)

        form.add_widget(grid)

        if "recordView" in self.displayed.form: # добавление корзины
            form.add_widget(self.bin())

    def createMultipleInputBox(self, form=None, title=None, options=[], defaults=[], multilines=[], disabled=[],
                               sort=None, resize=None, details=None, neutral=None, addCheckBoxes=False):
        """ Форма ввода данных с несколькими полями """

        if form == None: # по умолчанию вывод делается на mainlist, но можно вручную указать другую форму
            form = self.mainList
        form.clear_widgets()
        self.inputForm = "multi"
        if len(self.stack) > 0:
            self.stack.insert(0, self.stack[0]) # дублирование последнего шага стека, чтобы предотвратить уход со страницы
        self.backButton.disabled = False
        self.positive.text = self.button["save"]
        self.positive.disabled = False
        #self.positive.saveModeUpdate()
        self.negative.text = self.button["cancel"]
        self.negative.disabled = False
        self.detailsButton.disabled = True
        self.showSlider = False
        self.sliderToggle()

        if title != None:
            self.pageTitle.text = f"[ref=title]{title}[/ref]"
        if neutral == "":
            self.neutral.text = neutral
            self.neutral.disabled = True
        elif neutral != None:
            self.neutral.disabled = False
            self.neutral.text = neutral
        if sort == "":
            self.sortButton.text = sort
            self.sortButton.disabled = True
        elif sort != None:
            self.sortButton.text = sort
            self.sortButton.disabled = False
        if resize == "":
            self.resizeButton.text = resize
            self.resizeButton.disabled = True
        elif resize != None:
            self.resizeButton.text = resize
            self.resizeButton.disabled = False
        if details != None:
            self.detailsButton.text = details
            self.detailsButton.disabled = False

        grid = GridLayout(rows=len(options), spacing=self.spacing, padding=self.padding*2, cols=2, pos_hint={"top": 1})
        self.multipleBoxLabels = []
        self.multipleBoxEntries = []

        if len(disabled) < len(defaults):
            for i in range(len(multilines)):
                disabled.append(False)

        for row, default, multiline, disable in zip( range(len(options)), defaults, multilines, disabled):
            if "{}" in str(options[row]): # галочка
                text = str(options[row][2:]).strip()
                checkbox = True
                colorSelect = langSelect = False
            elif "<>" in str(options[row]): # выбор цвета отказа
                text = str(options[row][2:]).strip()
                checkbox = colorSelect = True
                langSelect = False
            elif "()" in str(options[row]): # выбор языка
                text = str(options[row][2:]).strip()
                checkbox = colorSelect = False
                langSelect = True
            else:
                text = options[row].strip()
                checkbox = colorSelect = langSelect = False
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

            self.multipleBoxLabels.append(MyLabel(text=text, valign="center", halign="center", size_hint=labelSize_hint,
                                                color = self.standardTextColor, text_size = (Window.size[0]/2, height),
                                                height=height))
            if default != "virtual":
                grid.add_widget(self.multipleBoxLabels[row])
            textbox = BoxLayout(size_hint=entrySize_hint, height=height, pos_hint={"center_x": .5})

            if colorSelect == True:
                self.multipleBoxEntries.append(RejectColorSelectButton())

            elif langSelect == True:
                self.multipleBoxEntries.append(self.languageSelector())

            elif checkbox == False:
                if self.displayed.form == "set" or self.msg[17] in self.multipleBoxLabels[row].text:
                    input_type = "number"
                else:
                    input_type = "text"
                self.multipleBoxEntries.append(MyTextInput(multiline=multiline, size_hint_x=entrySize_hint[0],
                                                           size_hint_y=entrySize_hint[1], hack=addCheckBoxes,
                                                           input_type = input_type, disabled=disable,
                                                           pos_hint={"top": 1}, height=height*.9))

                if default != "virtual":
                    self.multipleBoxEntries[row].text = str(default)
                else:
                    self.multipleBoxEntries[row].text = "–"
            else:
                self.multipleBoxEntries.append(MyCheckBox(active=default, size_hint=(entrySize_hint[0], entrySize_hint[1]),
                                                          pos_hint = {"top": 1}, color=self.titleColor))
            if default != "virtual":
                textbox.add_widget(self.multipleBoxEntries[row])
                grid.add_widget(textbox)

        if self.displayed.form == "set": # добавляем выбор темы для настроек
            grid.rows += 1
            grid.add_widget(MyLabel(text=self.msg[168], valign="center", halign="center", size_hint=labelSize_hint,
                                    color = self.standardTextColor, text_size=text_size))
            grid.add_widget(self.themeSelector())

        form.add_widget(grid)

        if addCheckBoxes == True: # добавляем галочки для нового посещения
            form.add_widget(self.reportBoxes(addReturn=False))
            self.multipleBoxEntries[1].height = self.mainList.size[1]

        if "Details" in self.displayed.form: # добавление корзины
            while 1:
                if not "flat" in self.displayed.form:
                    form.add_widget(self.bin())
                    break
                else:
                    if self.contactsEntryPoint == 1 or self.searchEntryPoint == 1:
                        form.add_widget(self.bin())
                        break
                    elif self.porch.type == "сегмент":
                        form.add_widget(self.bin())
                        break
                    elif self.displayed.form == "flatDetails" and "подъезд" in self.porch.type and \
                        self.porch.floors() == True:
                            form.add_widget(self.bin(f" {self.msg[169]}"))
                            break
                    elif self.porch.floors() == False:
                        form.add_widget(self.bin("empty"))
                        break
                    else:
                        form.add_widget(self.bin())
                        break

    # Генераторы интерфейсных элементов
    
    def reportBoxes(self, addReturn=False):
        """ Счетчики и галочка повторных посещений для первого и повторного посещений"""
        a = AnchorLayout(anchor_x="center", anchor_y="center")  # для счетчиков в новом посещении
        grid2 = GridLayout(rows=3, cols=2, size_hint_y=None)
        if addReturn == True:
            grid2.cols += 1
        grid2.add_widget(MyLabel(text=self.msg[102], halign="center", valign="center", color=self.standardTextColor))
        grid2.add_widget(MyLabel(text=self.msg[103], halign="center", valign="center", color=self.standardTextColor))
        if addReturn == True:
            grid2.add_widget(MyLabel(text=self.msg[13], halign="center", valign="center", color=self.standardTextColor))
        self.addPlacement = Counter(text="0", fixed=True, mode="pan")
        grid2.add_widget(self.addPlacement)
        self.addVideo = Counter(text="0", fixed=True, mode="pan")
        grid2.add_widget(self.addVideo)
        if addReturn == True:
            self.addReturn = MyCheckBox(active=True)
            grid2.add_widget(self.addReturn)
        grid2.height = self.counterHeight + self.standardTextHeight
        a.add_widget(grid2)
        return a
    
    def themeSelector(self):
        """ Выбор темы для настроек """
        if self.orientation == "v":
            k = 0.6
        else:
            k = 0.4
        a = AnchorLayout(size_hint_x=k)
        self.dropThemeMenu = DropDown()
        currentTheme = list({i for i in self.themes if self.themes[i] == self.theme})[0]
        options = list(self.themes.keys())
        for option in options:
            btn = SortListButton(text=option)
            btn.bind(on_release=lambda btn: self.dropThemeMenu.select(btn.text))
            self.dropThemeMenu.add_widget(btn)
        self.themeButton = TableButton(text=currentTheme, size_hint_x=1, size_hint_y=.6)
        self.dropThemeMenu.bind(on_select=lambda instance, x: setattr(self.themeButton, 'text', x))
        self.themeButton.bind(on_release=self.dropThemeMenu.open)
        a.add_widget(self.themeButton)
        return a

    def languageSelector(self):
        """ Выбор языка для настроек """
        a = AnchorLayout()
        self.dropLangMenu = DropDown()
        options = list(utils.Languages.values())
        for option in options:
            btn = SortListButton(font_name='DejaVuSans.ttf', text=option)
            btn.bind(on_release=lambda btn: self.dropLangMenu.select(btn.text))
            self.dropLangMenu.add_widget(btn)
        self.languageButton = TableButton(font_name='DejaVuSans.ttf', text=self.msg[1], size_hint_x=1, size_hint_y=.6)
        self.dropLangMenu.bind(on_select=lambda instance, x: setattr(self.languageButton, 'text', x))
        self.languageButton.bind(on_release=self.dropLangMenu.open)
        a.add_widget(self.languageButton)
        return a

    def bin(self, label=None):
        """ Корзина на текстовых формах """
        if label == None:
            text = f"{self.button['bin']} {self.msg[173]}"
            disabled = False
        elif label == "empty":
            text = ""
            disabled = True
        else:
            text = f"{self.button['shrink']} {self.msg[169]}"
            disabled = False
        if self.orientation == "v":
            k = 2#2.04
        else:
            k = 4
        deleteBtn = TableButton(text=text, size_hint_x=None, size_hint_y=None, width=Window.size[0]/k, disabled=disabled,
                                height=self.standardTextHeight, background_color=self.globalBGColor)
        bin = AnchorLayout(anchor_x="right", anchor_y="top", size_hint_y=None, padding=(0, self.padding),
                           height=self.mainList.size[1]*.2)
        deleteBtn.bind(on_release=self.deletePressed)
        bin.add_widget(deleteBtn)
        return bin

    def tip(self, text="", icon="info"):
        """ Подсказка """
        if icon == "warn":
            color = "F4CA16" # желтый
            size_hint_y = None
        elif icon == "info":
            color = self.titleColor2
            size_hint_y = 1
        elif icon == "note":
            color = self.titleColor2
            size_hint_y = None

        if len(text) > 80:
            size_hint_y = 1

        tip = MyLabel(color=self.standardTextColor, markup=True, size_hint_y=size_hint_y,
                        text=f"[ref=note][color={color}]{self.button[icon]}[/color] {text}[/ref]",
                        text_size=(self.mainList.size[0] * .75, None), valign="center")
        if icon == "note" or icon == "warn":
            tip.bind(on_ref_press=self.titlePressed)
        return tip

    def flatListButton(self):
        """ Кнопка создания квартир/домов списком"""
        height = self.standardTextHeight
        addList = TableButton(text=f"{self.button['list']} {self.msg[191]}", size_hint_x=None, size_hint_y=None,
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
                    flat = utils.houses[h].porches[p].flats[f]
                    if forSearch == False:  # поиск для списка контактов - только светло-зеленые жильцы и все отдельные контакты
                        if flat.status == "1" or flat.number == "virtual":
                            self.retrieve(utils.houses, h, p, f, contacts)
                    else:  # поиск для поиска - все контакты вне зависимости от статуса
                        if not "." in flat.number:
                            self.retrieve(utils.houses, h, p, f, contacts)

        for h in range(len(utils.resources[1])):
            self.retrieve(utils.resources[1], h, 0, 0, contacts)  # отдельные контакты - все

        return contacts

    # Обработка клавиатуры

    def hook_keyboard(self, window, key, *largs):
        if key == 27:
            if self.backButton.disabled == False:
                self.backPressed()
            return True

    def keyboardHeight(self, *args):
        """ Возвращает высоту клавиатуры в str"""
        if platform == "android":
            rect = Rect(instantiate=True)
            activity.getWindow().getDecorView().getWindowVisibleDisplayFrame(rect)
            rect.top = 0
            height = activity.getWindowManager().getDefaultDisplay().getHeight() - (rect.bottom - rect.top)
            if height > 300:
                self.defaultKeyboardHeight = height
            else:
                height = self.defaultKeyboardHeight
            return height
        else:
            return self.defaultKeyboardHeight

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
                    if self.theme != "green" and self.theme != "retro":
                        month.background_color = self.titleColor
                    else:
                        month.background_color = self.getColorForStatus("0")
                else:
                    if self.theme == "green" or self.theme == "retro":
                        month.background_color = self.titleColor
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
            gapWord = self.msg[174]
        elif gap < 0:
            gapEmo = icon("icon-frown")
            gapWord = self.msg[175]
        else:
            gapEmo = ""
        self.analyticsMessage.text = f"[b]{self.msg[176]}[/b]\n\n" + \
                                     f"{self.msg[177]}: [b]%d[/b]\n\n" % monthNumber + \
                                     f"{self.msg[178]}: [b]%d[/b]\n\n" % hourSum + \
                                     f"{self.msg[179]}¹: [b]%d[/b]\n\n" % yearNorm + \
                                     f"{self.msg[180]}: [b]%d[/b]\n\n" % (yearNorm - hourSum) + \
                                     f"%s: [b]%d[/b] %s\n\n" % (gapWord, abs(gap), gapEmo) + \
                                     f"{self.msg[181]}²: [b]%0.f[/b]\n\n" % average + \
                                     "____\n" + \
                                     f"¹ {self.msg[182]}\n\n" + \
                                     f"² {self.msg[183]}"
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
        box = BoxLayout(orientation="vertical", size_hint=(.95, .95), padding=self.padding)
        if self.house.type == "condo":
            warning = f" {self.msg[184]}"
        else:
            warning = f" {self.msg[245]}"
        if self.house.type == "condo":
            hint = self.msg[185]
        else:
            hint = self.msg[309]
        text = MyTextInput(hint_text=hint, multiline=True, size_hint_y=None,
                           height=self.standardTextHeight * 3, shrink=False)
        box.add_widget(text)
        btnPaste = TableButton(text=self.msg[186], size_hint_x=1, size_hint_y=None, width=width, height=self.standardTextHeight,
                           background_color=self.textInputBGColor)
        def __paste(instance):
            text.text = Clipboard.paste()
        btnPaste.bind(on_release=__paste)
        box.add_widget(btnPaste)
        description = MyLabel(
            text=self.msg[187] + warning,
            text_size=(width, None), valign="top")
        box.add_widget(description)
        grid = GridLayout(cols=3, size_hint=(1, None))
        btnSave = RButton(text=self.msg[188], onPopup=True)
        def __save(instance):
            flats = text.text.strip()
            if "." in flats:
                description.text = self.msg[38]
                return
            elif self.house.type == "private":
                flats = [x for x in flats.split(',')]
            else:
                try:
                    flats = [int(x) for x in flats.split(',')]
                except:
                    description.text = self.msg[189]
                    return
            if "подъезд" in self.porch.type: # отключение поэтажного вида
                self.porch.type = "подъезд"
                self.porch.flatsLayout = "н"
            for flat in flats:
                self.porch.addFlat(f"+{flat}")
            utils.save()
            modal.dismiss()
            self.backPressed()
        btnSave.bind(on_release=__save)
        btnClose = RButton(text=self.msg[190], onPopup=True)
        def __close(instance):
            modal.dismiss()
        btnClose.bind(on_release=__close)
        grid.add_widget(btnSave)
        grid.add_widget(Widget())
        grid.add_widget(btnClose)
        box.add_widget(grid)
        modal = Popup(title=self.msg[191], content=box, size_hint=size_hint, separator_color = self.titleColor)
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
            if not self.msg[162] in self.pageTitle.text and self.addReturn.active == True:
                report += "п"
                self.rep.returns += 1
            self.addReturn.active = False
        except:
            pass

        self.rep.modify(report)

    def quickReject(self, instance=None, fromPopup=False):
        """ Быстрая простановка отказа """
        if len(self.flat.records) == 0 and fromPopup == False:
            self.flat.updateName(self.multipleBoxEntries[0].text.strip())
        if fromPopup == True:
            record = self.msg[207][0].lower() + self.msg[207][1:] # отказ
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
        for i in ["0", "1", "2", "3", "4", "5", ""]:
            if color == "":
                self.popup(self.msg[193], options=[self.button["yes"], self.button["no"]])
                self.popupForm = "resetFlatToGray"
                return
            elif color == i:
                self.flat.status = i
                break

        if self.contactsEntryPoint == 1:
            self.conPressed()
        elif self.searchEntryPoint == 1:
            self.find(instance=True)
        else:
            self.porchView()
        utils.save()

    def getColorForStatus(self, status=99):

        if status == "?":
            color = self.scrollButtonBackgroundColor2 # темно-серый
        elif status == "0":
            color = [0, .54, .73, 1] # синий
        elif status == "1":
            color = [0, .74, .50, 1] # зеленый
        elif status == "2":
            color = [.30, .50, .46, 1] # темно-зеленый
        elif status == "3":
            color = [.53, .37, .76, 1] # фиолетовый
        elif status == "4":
            color = [.50, .27, .22, 1] # коричневый
        elif status == "5":
            color = [.81, .24, .17, 1] # красный
        else:
            color = self.scrollButtonBackgroundColor
        return color

    def deletePressed(self, instance=None):
        """ Действие при нажатии на кнопку с корзиной на форме любых деталей """
        if self.displayed.form == "houseDetails": # удаление участка
            self.popupForm = "confirmDeleteHouse"
            self.popup(title=f"{self.msg[194]}: {self.house.title}",
                       message=self.msg[195],
                       options=[self.button["yes"], self.button["no"]])

        elif self.displayed.form == "porchDetails": # удаление подъезда
            self.popupForm = "confirmDeletePorch"
            if self.house.type == "condo":
                title = self.msg[196]
            else:
                title = self.msg[197]
            
            self.popup(title=f"{title}: {self.porch.title}", message=self.msg[198],
                       options=[self.button["yes"], self.button["no"]])

        elif self.displayed.form == "flatDetails" or self.displayed.form == "flatView": # удаление квартиры
            self.popupForm = "confirmDeleteFlat"
            if self.contactsEntryPoint == 1 or self.searchEntryPoint == 1 or \
                    (self.flat.status != "" and not "подъезд" in self.porch.type):
                self.popup(title=f"{self.msg[199]}: {self.flatTitle}", message=self.msg[198],
                           options=[self.button["yes"], self.button["no"]])
            else:
                self.popupPressed(instance=Button(text=self.button["yes"]))

        elif self.displayed.form == "recordView": # удаление записи посещения
            self.popupForm = "confirmDeleteRecord"
            self.popup(title=self.msg[200],
                       message=f"{self.msg[201]} {self.record.date}?",
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

        elif self.displayed.form == "notes":
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
            if instance.text == self.msg[42]:
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
                utils.log(self.msg[192])

        elif self.popupForm == "restoreData":
            if instance.text == self.button["yes"]:
                result = utils.backupRestore(restoreWorking=True, silent=False)
                if result == True:
                    self.rep = report.Report()
                    utils.save()

        elif self.popupForm == "importHelp":
            if instance.text == self.button["yes"]:
                if self.language == "ru":
                    webbrowser.open("https://github.com/antorix/Rocket-Ministry/wiki/ru#синхронизация-и-резервирование-данных")
                else:
                    webbrowser.open("https://github.com/antorix/Rocket-Ministry/wiki#data-synchronization-and-backup")

        elif self.popupForm == "newMonth":
            self.repPressed()
            self.resizePressed()

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
                        if utils.resources[0][1][0] == 0:
                            self.popupForm = "confirmShrinkFloor"
                            self.popup(title=self.msg[247], message=self.msg[299], checkboxText=self.msg[170],
                                       options=[self.button["yes"], self.button["no"]])
                            return
                        else:
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

        elif self.popupForm == "confirmShrinkFloor":
            if instance.text == self.button["yes"]:
                self.porch.shrinkFloor(self.selectedFlat)
                self.porchView()
                if self.popupCheckbox.active == True:
                    utils.resources[0][1][0] = 1
                utils.save()

        elif self.popupForm == "confirmDeletePorch":
            if instance.text == self.button["yes"]:
                del self.house.porches[self.selectedPorch]
                utils.save()
                self.houseView()

        elif self.popupForm == "confirmDeleteHouse":
            if instance.text == self.button["yes"]:
                for p in range(len(self.house.porches)):
                    for f in range(len(self.house.porches[p].flats)):
                        flat = self.house.porches[p].flats[f]
                        if flat.status == "1":
                            if flat.getName() == "":
                                flat.updateName("?")
                            flat.clone(toStandalone=True, title=self.house.title)
                del utils.houses[self.selectedHouse]
                utils.save()
                self.terPressed()

        elif self.popupForm == "pioneerNorm":
            if instance.text == self.button["yes"]:
                utils.settings[0][3] = 70
                utils.save()
                self.settingsPressed()

        elif self.popupForm == "restart":
            if instance.text == self.button["yes"]:
                self.restart()

        elif self.popupForm == "resetFlatToGray":
            if instance.text == self.button["yes"]:
                if self.flat.number == "virtual":
                    del utils.resources[1][self.selectedHouse]
                else:
                    self.flat.wipe()
                if self.contactsEntryPoint == 1:
                    self.conPressed()
                elif self.searchEntryPoint == 1:
                    self.find(instance=True)
                else:
                    self.porchView()
                utils.save()
            else:
                self.colorBtn[6].text = ""
                for i, status in zip(range(7), ["0", "1", "2", "3", "4", "5", ""]):
                    if status == self.flat.getStatus()[0][1]:
                        self.colorBtn[i].text = self.button["dot"]
                        self.colorBtn[i].markup = True

        self.popupForm = ""

    def popup(self, message="", options="Close", title=None, firstCall=False, checkboxText=None):
        """Информационное окно с возможностью подтверждения выбора"""

        # Специальный попап для первого посещения

        if title == None:
            title = self.msg[203]

        if options == "Close":
            options = [self.msg[39]]

        auto_dismiss = True

        if firstCall == True:
            self.popupForm = "firstCall"
            title = self.flat.number
            if self.orientation == "v":
                size_hint = (.8, .5)
            else:
                size_hint = (.5, .6)
            contentMain = BoxLayout(orientation="vertical", padding=self.padding)
            content = GridLayout(rows=1, cols=1, padding=self.padding, spacing=self.spacing*2)
            content2 = GridLayout(rows=1, cols=1, padding=[self.padding, self.padding/2, self.padding, self.padding],
                                  spacing=self.spacing*2)
            details = TableButton(text=self.button["cog"], size_hint_x=None, size_hint_y=None, color="white",
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
                self.keyboardCloseTime = .1
                self.inputForm = "single"
                if self.platform == "desktop":
                    focus = True
                else:
                    focus = False
                self.quickPhone = MyTextInput(size_hint_y=None, hint_text = self.msg[35], height=self.standardTextHeight,
                                              focus=focus, multiline=False, input_type="text", popup=True, shrink=False)
                contentMain.add_widget(self.quickPhone)
                def __getPhone(instance):
                    self.mypopup.dismiss()
                    self.quickPhone.hint_text = self.msg[204]
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
                if self.platform == "desktop": # на компьютере закрываем попап при дефокусе строки поиска
                    self.quickPhone.bind(focus=__dismiss)

            if utils.settings[0][13] == 1:  # кнопка нет дома
                content.cols += 1
                if self.theme == "retro":
                    colorBG = ""
                else:
                    colorBG = [.25, .25, .25]
                firstCallNotAtHome = RButton(text=f"{self.button['lock']} [b]{self.msg[206]}[/b]", color="white",
                                             quickFlash=True, background_color=colorBG)
                def __quickNotAtHome(instance):
                    self.mypopup.dismiss()
                    self.flat.addRecord(self.msg[206][0].lower()+self.msg[206][1:])
                    utils.save()
                    self.porchView()

                    if utils.resources[0][1][4] == 0:
                        self.popup(title=self.msg[247], message=self.msg[205] % self.msg[206])
                        utils.resources[0][1][4] = 1
                        utils.save()

                firstCallNotAtHome.bind(on_release=__quickNotAtHome)
                content.add_widget(firstCallNotAtHome)

            if self.theme == "dark":
                color = self.popupBackgroundColor
                colorBG = self.themeDefault[0]
            elif self.theme == "teal":
                color = self.themeDefault[1]
                colorBG = self.themeDefault[0]
            elif self.theme == "gray":
                color = self.tableBGColor
                colorBG = self.topButtonColor
            elif self.theme == "retro":
                color = self.titleColor
                colorBG = ""
            else:
                color = self.tableColor
                colorBG = self.tableBGColor
            firstCallBtnCall = RButton(text=f"{self.button['record']} [b]{self.msg[163]}[/b]", quickFlash=True,# кнопка интерес
                                        color=color, background_color=colorBG)
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
            if self.theme == "retro":
                color = rejectColor
                colorBG = ""
            else:
                color = "white"
                colorBG = rejectColor
            firstCallBtnReject = RButton(text=f"{self.button['reject']} [b]{self.msg[207]}[/b]", background_color=colorBG,
                                         color=color, quickFlash=True)
            def __quickReject(instance):
                self.mypopup.dismiss()
                self.quickReject(fromPopup=True)
            firstCallBtnReject.bind(on_release=__quickReject)
            content2.add_widget(firstCallBtnReject)

            contentMain.add_widget(content)
            contentMain.add_widget(content2)

            self.popupForm = ""

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

            save = RButton(text=self.msg[188], onPopup=1, size_hint_y=None, #background_color=self.themeDark[0], color="white",
                           size=(self.standardTextWidth, self.standardTextHeight))  # кнопка сохранения

            def __closeTimePicker(instance):
                self.mypopup.dismiss()
                time2 = str(self.pickedTime)[:5] # время, выбранное на пикере (HH:MM)
                if title == self.msg[105]:
                    time1 = self.hours.get()  # исходное время на счетчике (HH:MM)
                    if self.pickedTime != "00:00":
                        self.time3 = utils.sumHHMM([time1, time2]) # сумма исходного и добавленного времени (HH:MM)
                        self.rep.modify(f"ч{time2}")
                        self.hours.update(self.time3)
                        self.counterChanged = False
                        self.pageTitle.text = f"[ref=report]{self.msg[4]}{self.rep.getCurrentHours()[2]}[/ref]"
                else:
                    time1 = self.credit.get()  # исходное время на счетчике (HH:MM)
                    self.time3 = utils.sumHHMM([time1, time2])  # сумма двух времен в HH:MM
                    if self.pickedTime != "00:00":
                        self.rep.modify(f"р{time2}")
                        self.credit.update(self.time3)
                        self.counterChanged = False
                        self.pageTitle.text = f"[ref=report]{self.msg[4]}{self.rep.getCurrentHours()[2]}[/ref]"
            save.bind(on_release=__closeTimePicker)
            pickerForm.add_widget(save)
            contentMain = pickerForm

        # Стандартное информационное окно либо запрос да/нет

        else:
            #if len(options) == 2:
            #    auto_dismiss = False
            if self.orientation == "v":
                if checkboxText != None:
                    size_hint = (.9, .6)
                else:
                    size_hint = (.9, .4)
            else:
                if checkboxText != None:
                    size_hint = (.5, .6)
                else:
                    size_hint = (.5, .4)
            text_size = (Window.size[0] * size_hint[0] * .9, None)

            contentMain = BoxLayout(orientation="vertical")
            contentMain.add_widget(MyLabel(text=message, halign="left", valign="center", text_size=text_size, markup=True))

            if checkboxText != None: # задана галочка
                CL = BoxLayout(size_hint_y=None)
                self.popupCheckbox = MyCheckBox(size_hint=(.1, None))
                CL.add_widget(self.popupCheckbox)
                CL.add_widget(MyLabel(text=checkboxText, halign="center", valign="center", size_hint=(.85, None),
                                    text_size=text_size))
                contentMain.add_widget(CL)

            if len(options) > 0: # заданы кнопки да/нет
                grid = GridLayout(rows=1, cols=1, size_hint_y=None)
                self.confirmButtonPositive = RButton(text=options[0], onPopup=True, pos_hint={"bottom": 1})
                self.confirmButtonPositive.bind(on_release=self.popupPressed)
                if len(options) == 1:
                    grid.rows += 1
                    grid.add_widget(Widget())
                grid.add_widget(self.confirmButtonPositive)
                if len(options) > 1:
                    grid.cols=3
                    grid.add_widget(Widget())
                    self.confirmButtonNegative = RButton(text=options[1], onPopup=True)
                    self.confirmButtonNegative.bind(on_release=self.popupPressed)
                    grid.add_widget(self.confirmButtonNegative)
                contentMain.add_widget(grid)

        self.mypopup = PopupNoAnimation(title=title, content=contentMain, size_hint=size_hint,
                                        separator_color=self.titleColor, auto_dismiss=auto_dismiss)

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
        """ Запускается каждый раз в начале работы """
        def __do(*args):
            utils.backupRestore(delete=True, silent=True)

            utils.update()

            if self.devmode == 1:
                print("Определяем начало нового месяца.")
            self.rep.checkNewMonth()

            limit = 300
            if self.devmode == 1:
                print("Оптимизируем размер журнала отчета.")
            if len(utils.resources[2]) > limit:
                extra = len(utils.resources[2]) - limit
                for i in range(extra):
                    del utils.resources[2][len(utils.resources[2]) - 1]

        Clock.schedule_once(__do, 2)

    def importDB(self, instance=None, file=None):
        """ Импорт данных из буфера обмена либо файла"""

        if file == None:
            clipboard = Clipboard.paste()
            success = utils.load(clipboard=clipboard)
        else:
            success = utils.load(forced=True, datafile=file, silent=True) # сначала пытаемся загрузить текстовый файл

            if success == False: # файл не текстовый, пробуем загрузить Word-файл
                self.popup(self.msg[208])

        if success == True:
            self.popup(self.msg[209])
            self.restart("soft")
            self.terPressed()
        elif file == None:
            self.popupForm = "importHelp"
            if success == False:
                self.popup(self.msg[210], options=[self.button["yes"], self.button["no"]])
            else: # тоже неудачно, но другой вид ошибки
                self.popup(success)

    def checkOrientation(self, window=None, width=None, height=None):
        """ Проверка ориентации экрана, и если она горизонтальная, адаптация интерфейса"""
        if Window.size[0] <= Window.size[1]:
            self.orientation = "v"
            self.boxHeader.size_hint_y = self.marginSizeHintY
            self.titleBox.size_hint_y = self.marginSizeHintY
            self.boxFooter.size_hint_y = self.marginSizeHintY
            self.standardTextHeight = Window.size[1] * .05  # 90
            self.positive.size_hint_x=.7
        else:
            self.orientation = "h"
            self.boxHeader.size_hint_y = self.marginSizeHintY * 1.2
            self.titleBox.size_hint_y = self.marginSizeHintY * 1.2
            self.boxFooter.size_hint_y = self.marginSizeHintY * 1.3
            self.standardTextHeight = Window.size[1] * .06  # 90
            if self.theme != "retro":
                self.positive.size_hint_x = .15

        if self.platform == "desktop":
            try:
                with open("win.ini", "w") as file:
                    file.write(str(width)+"\n")
                    file.write(str(height)+"\n")
                    file.write(str(Window.top)+"\n")
                    file.write(str(Window.left))
            except:
                pass
            self.standardTextHeight = 40

    def buttonFlash(self, instance=None, timeout=None):
        if self.theme == "retro":
            return

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

    def restart(self, mode="hard"):
        self.checkOrientation(width=Window.size[0], height=Window.size[1])
        if mode == "soft": # простая перерисовка интерфейса
            self.setParameters(reload=True)
            self.globalAnchor.clear_widgets()
            utils.load()
            self.setTheme()
            self.createInterface()

            """self.timerBox.size_hint_x = .33#, spacing=self.spacing, padding=(self.padding, 0))
            self.headBox.size_hint_x = .34
            self.setBox.size_hint_x = .33


            self.timerBox.remove_widget(self.timer)
            self.timerBox.remove_widget(self.timerText)
            self.timerBox.add_widget(self.timer)
            self.timerBox.add_widget(self.timerText)

            self.boxHeader.remove_widget(self.timerBox)
            self.boxHeader.remove_widget(self.headBox)
            self.boxHeader.remove_widget(self.setBox)
            self.boxHeader.add_widget(self.timerBox)
            self.boxHeader.add_widget(self.headBox)
            self.boxHeader.add_widget(self.setBox)"""


        else:# полная перезагрузка приложения
            if self.platform == "mobile":
                kvdroid.tools.restart_app()
            else:
                self.stop()
                from os import startfile
                startfile("main.py")

RM = RMApp()
