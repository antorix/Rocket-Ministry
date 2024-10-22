#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import argv
Devmode = 1 if "dev" in argv else 0
Mobmode = 1 if "mob" in argv else 0
Version = "2.15.001"

""" 
* Исправлен баг, при котором программа могла упасть при заходе в просроченный участок.
* Постановка таймера на паузу.
* Текстовые метки (описания) после каждого служения и любой другой записи в журнале служения.
* Создание новых записей журнала, их редактирование и фильтрация.
* Убрана кнопка сохранения из отчета и настроек, данные запоминаются в реальном времени.
* Небольшие интерфейсные изменения и улучшения. 
* Исправления и оптимизации.

Известные баги:
* Прыгают элементы при перерисовке интерфейса из настроек (def restart). 
"""

try: # на ПК проверяем версию Kivy и обновляем при необходимости
    from subprocess import check_call
    from sys import executable
    from importlib.metadata import version
    if version("kivy") != "2.3.0":
        check_call([executable, '-m', 'pip', 'install', 'kivy==2.3.0'])
except ImportError as e:
    try: check_call([executable, '-m', 'pip', 'install', 'kivy==2.3.0'])
    except: pass

from kivy.app import App
from kivy.uix.behaviors import DragBehavior
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.behaviors.touchripple import TouchRippleBehavior
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.bubble import Bubble
from kivy.properties import ObjectProperty
from kivy.graphics import PushMatrix, PopMatrix, Callback
from kivy.graphics import Color, SmoothRoundedRectangle
from kivy.graphics.context_instructions import Transform
from kivy.metrics import inch
from kivy.uix.behaviors import FocusBehavior
from weakref import ref
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.base import EventLoop
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.core.clipboard import Clipboard
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.clock import Clock, mainthread
from kivy.animation import Animation
from kivy.utils import get_hex_from_color
from kivy import platform
from kivy import __version__

import utils as ut
import os
import time
import json
import shutil
import datetime
import webbrowser
from functools import partial
from copy import copy
from iconfonts import icon
from iconfonts import register

try:
    import plyer
except ImportError as e:
    from subprocess import check_call
    from sys import executable
    check_call([executable, '-m', 'pip', 'install', 'plyer'])
    import plyer

try:
    from dateutil import relativedelta
except ImportError as e:
    from subprocess import check_call
    from sys import executable
    check_call([executable, '-m', 'pip', 'install', 'python-dateutil'])
    from dateutil import relativedelta

if platform == "android":
    from android.permissions import request_permissions, Permission
    from android.storage import app_storage_path
    from androidstorage4kivy import SharedStorage, Chooser
    from kvdroid import activity, autoclass
    from kvdroid.jclass.android import Rect
    rect = Rect(instantiate=True)
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    mActivity = PythonActivity.mActivity
else:
    import _thread
    try:
        import requests
    except ImportError as e:
        from subprocess import check_call
        from sys import executable
        check_call([executable, '-m', 'pip', 'install', 'requests'])
        import requests
    if platform == "win" and not Devmode:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0) # убираем консоль на Windows

# Классы объектов участка

class House(object):
    """ Класс участка """
    def __init__(self, title="", porchesLayout="н", note="", type=""):
        self.title = title
        self.porchesLayout = porchesLayout # сортировка подъездов
        self.note = note
        self.type = type # condo, private
        self.porches = []
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        self.statsCached = None # кеш статистики, несохр.
        self.dueCached = None # кеш просроченности, несохр.

    def sort(self):
        """ Сортировка в списке участков по типу с учетом участка-списка """
        if RM.language == "ru" or RM.language == "uk" or RM.language == "ka" or RM.language == "hy": # должно соответствовать списку выбора типа участков
            if self.listType(): return 3
            elif self.type == "condo": return 1
            elif self.type == "private": return 2
        else:
            if self.listType(): return 3
            elif self.type == "private": return 1
            elif self.type == "condo": return 2

    def getHouseStats(self):
        """ Подсчет посещенных и интересующихся на участке """
        if self.statsCached is None:
            visited = interest = totalFlats = lastVisit = 0
            for porch in self.porches:
                for flat in porch.flats:
                    if not "." in str(flat.number) or self.type == "private": totalFlats += 1
                    if len(flat.records) > 0: visited += 1
                    if flat.status == "1": interest += 1
                    if isinstance(flat.lastVisit, float) and flat.lastVisit > lastVisit: lastVisit = flat.lastVisit
            ratio = visited / totalFlats if totalFlats != 0 else 0
            self.statsCached = visited, interest, ratio, totalFlats, lastVisit
        return self.statsCached

    def due(self):
        """ Определяет, что участок просрочен """
        if self.dueCached is None:
            start = datetime.datetime.strptime(self.date, "%Y-%m-%d")
            end = datetime.datetime.strptime(time.strftime("%Y-%m-%d", time.localtime()), "%Y-%m-%d")
            delta = relativedelta.relativedelta(end, start)
            diff = delta.months + (delta.years * 12)
            self.dueCached = True if diff >= 4 else False
        return self.dueCached

    def getPorchType(self):
        """ Выдает название подъезда своего типа (всегда именительный падеж), [0] для программы и [1] для пользователя """
        if self.type == "private": return "сегмент", RM.msg[211]
        else: return "подъезд", RM.msg[212]

    def showPorches(self):
        """ Вывод списка подъездов """
        list = []
        if self.porchesLayout == "н" or self.porchesLayout == "а": # сортировка подъездов по номеру/названию
            self.porches.sort(key=lambda x: x.title, reverse=False)
            self.porches.sort(key=lambda x: ut.numberize(x.title), reverse=False)
        elif self.porchesLayout == "п": # сортировка подъездов по дате последнего посещения
            self.porches.sort(key=lambda x: x.getLastVisit(), reverse=False)
        elif self.porchesLayout == "р": # сортировка подъездов по размеру (кол-ву квартир)
            self.porches.sort(key=lambda x: x.getSize(), reverse=False)
        elif self.porchesLayout == "о": # сортировка по размеру обратная
            self.porches.sort(key=lambda x: x.getSize(), reverse=True)
        porchString = RM.msg[212][0].upper() + RM.msg[212][1:] if RM.language != "ka" else RM.msg[212]
        for porch in self.porches:
            listIcon = f"{RM.button['porch']} {porchString}" if self.type == "condo" else RM.button['pin']
            list.append(f"{listIcon} [b]{porch.title}[/b] {porch.getFlatsRange()}")
        if self.type != "condo" and len(list) == 0:
            list.append(f"{RM.button['plus-1']}{RM.button['pin']} {RM.msg[213]}") # создайте первую улицу
            #RM.createFirstHouse = True
        if self.type == "condo" and self.porchesLayout == "н" or self.porchesLayout == "а":
            list.append(f"{RM.button['porch_inv']} {RM.msg[6]} {self.getLastPorchNumber()}")
        return list

    def getLastPorchNumber(self):
        """ Определяет номер следующего подъезда в доме (+1 к уже существующим) """
        if len(self.porches) == 0: number = 1
        else:
            last = len(self.porches) - 1
            if self.porches[last].title.isnumeric():
                number = int(self.porches[last].title) + 1
            else:
                number = int(ut.numberize(self.porches[last].title)) + 1
        return number

    def addPorch(self, input="", type="подъезд"):
        """ Создает новый подъезд и возвращает его """
        newPorch = Porch(title=input.strip(), type=type, pos=[True, [0, 0]])
        self.porches.append(newPorch)
        return newPorch

    def deletePorch(self, porch):
        selectedPorch = self.porches.index(porch)
        del self.porches[selectedPorch]

    def noSegment(self):
        """ Проверяет, что в участке отключены сегменты. Это проверяется только по названию первого сегмента """
        if len(self.porches) == 1 and RM.invisiblePorchName in self.porches[0].title:
            return True
        else: return False

    def listType(self):
        """ Проверяет, что участок списочного типа. Это проверяется только по названию первого сегмента """
        if len(self.porches) == 1 and self.porches[0].title == RM.listTypePorchName:
            return True
        else: return False

    def export(self):
        return [
            self.title, self.porchesLayout, self.date, self.note, self.type, [porch.export() for porch in self.porches]
        ]

class Porch(object):
    """ Класс подъезда """
    def __init__(self, title="", pos=None, flatsLayout="н", floor1=1, note="", type=""):
        if pos is None: pos = [True, [0, 0]]
        self.title = title
        self.pos = pos # True = свободный режим, False = заполнение. [0, 0] = координаты в свободном режиме
        self.flatsLayout = flatsLayout
        self.floor1 = floor1 # number of first floor
        self.note = note
        self.type = type # "сегмент" или "подъезд"/"подъездX", где Х - число этажей. В программе сегмент теперь улица
        self.flats = []

        if len(self.pos) != 2 or len(self.pos[1]) != 2:
            self.pos = [True, [0, 0]] # конвертация настроек позиционирования начиная с версии 2.13.003

        # Переменные, не сохраняемые в базе:

        self.flatsNonFloorLayoutTemp = None # кеширование сортировки
        self.highestNumber = 0 # максимальный номер квартиры
        self.floorview = None # кешированная сетка подъезда
        self.scrollview = None # кешированный список подъезда/сегмента

    def restoreFlat(self, instance):
        """ Восстанавление квартир (нажатие на плюсик) """
        self.scrollview = None
        def __oldRandomNumber(number):
            """ Проверка, что это не длинный номер, созданный random() в предыдущих версиях """
            if "." in number:
                pos = number.index(".")+1
                length = len(number[pos:])
                if length <= 1: return False
                else: return True
            else: return False
        if ".5" in instance.flat.number and not __oldRandomNumber(instance.flat.number): # восстановление удаленной квартиры с таким же номером
            instance.flat.number = instance.flat.number[ : instance.flat.number.index(".")]
        elif "." in instance.flat.number: # либо удаление заглушки путем сдвига квартир налево
            self.deleteFlat(instance.flat, regularDelete=True)
            for flat in self.flats:
                if ".1" in flat.number and float(flat.number) > float(instance.flat.number):
                    flat.number = "%.1f" % (float(flat.number)+1)
            self.flats.append(Flat(number=f"{int(self.highestNumber+1)}"))

    def deleteFlat(self, deletedFlat, regularDelete=False):
        """ Удаление квартиры - переводит на сдвиг (если подъезд) или простое удаление (если не подъезд) """
        self.scrollview = None
        RM.porch.flat = None
        if self.floors() and not regularDelete: # если подъезд c сеткой
            for f in self.flats:
                if f.number == self.lastFlatNumber:
                    if f.status != "" or f.color2 != 0 or f.emoji != "": # проверка, чтобы последняя квартира была пустой
                        RM.popup(message=RM.msg[215])
                        return True
                    break
            i = self.flats.index(deletedFlat)
            popped = self.flats.pop(i)
            self.flats.append(popped)
            adjustedNumber = ut.numberize(deletedFlat.number) - 1 + .1
            self.flats.insert(i, Flat(number="%.1f" % adjustedNumber))
            for i in range(len(self.flats)):
                if ".1" in self.flats[i].number and float(self.flats[i].number) > adjustedNumber:
                    self.flats[i].number = "%.1f" % (float(self.flats[i].number)-1)
            self.flatsLayout = str(self.rows)
            self.sortFlats() # повторная сортировка, чтобы обновить lastFlatNumber
        else: # простое удаление
            i = self.flats.index(deletedFlat)
            del self.flats[i]

    def getFirstAndLastNumbers(self):
        """ Возвращает первый и последний номера в подъезде и кол-во этажей """
        numbers = []
        for flat in self.flats:
            if "." not in flat.number: numbers.append(int(ut.numberize(flat.number)))
        numbers.sort()
        try:
            first = str(numbers[0])
            last = str(numbers[len(numbers) - 1])
            floors = self.type[7:]
            if floors == "": floors = "1"
        except:
            try: first, last, floors = RM.settings[0][9]
            except:
                first = "1"
                last = "20"
                floors = "5"
        return first, last, floors

    def getSize(self):
        """ Выдает размер подъезда (кол-во квартир) в целях сортировки подъездов """
        if self.type == "сегмент":
            count = len(self.flats)
        else:
            count = 0
            for flat in self.flats:
                if "." not in flat.number: count += 1
        return count

    def getLastVisit(self):
        """ Выдает дату последнего посещения квартиры внутри подъезда для сортировки """
        self.flats.sort(key=lambda x: x.lastVisit, reverse=True)
        return self.flats[0].lastVisit if len(self.flats) > 0 else 0

    def getFlatsRange(self):
        """ Выдает диапазон квартир в подъезде """
        list = []
        alpha = False
        check = True
        range = ""
        for flat in self.flats:
            if not "." in flat.number or self.type == "сегмент":
                list.append(flat)
                if check and not flat.number.isnumeric():
                    alpha = True
                    check = False
        if len(list) == 1:
            if "подъезд" in self.type: range = f" {RM.msg[214]} [i]{list[0].number}[/i]"
            else: range = f" [i]{list[0].number}[/i]"
        elif len(list) > 1:
            if "подъезд" in self.type:
                if not alpha:
                    list.sort(key=lambda x: int(x.number))
                else:
                    list.sort(key=lambda x: x.number)
                    list.sort(key=lambda x: ut.numberize(x.number))
            if "подъезд" in self.type: range = f" {RM.msg[214]} [i]{list[0].number}–{list[len(list)-1].number}[/i]"
            else: range = f" [i]{list[0].number}–{list[len(list)-1].number}[/i]"
        return range

    def clearCache(self, type=""):
        """ Удаляет кеш раскладки в зависимости от сортировки. Если получает тип сортировки, то удаляет только при совпадении """
        result = False
        if type != "":
            if type == self.flatsLayout:
                self.scrollview = None
                result = True
        elif self.flatsLayout == "с" or self.flatsLayout == "с2" or self.flatsLayout == "д" \
                or self.flatsLayout == "т" or self.flatsLayout == "з" or self.flatsLayout == "и":
            self.scrollview = None
            result = True
        return result

    def sortFlats(self, type=None):
        """ Сортировка квартир """
        if type is not None: self.flatsLayout = type
        self.clearCache()

        if self.flatsLayout == "н":  # numeric by number
            self.flatsNonFloorLayoutTemp = self.flatsLayout
            self.flats.sort(key=lambda x: x.number)
            self.flats.sort(key=lambda x: ut.numberize(x.number))

        elif self.flatsLayout == "о":  # numeric by number reversed
            self.flatsNonFloorLayoutTemp = self.flatsLayout
            self.flats.sort(key=lambda x: x.number, reverse=True)
            self.flats.sort(key=lambda x: ut.numberize(x.number), reverse=True)

        else:
            self.flats.sort(key=lambda x: x.number) # две числовые сортировки обязательны перед всеми остальными
            self.flats.sort(key=lambda x: ut.numberize(x.number))
            self.lastFlatNumber = self.flats[len(self.flats)-1].number # определяем номер в виде строки последней квартиры (максимальной по нумерации)

            if self.flatsLayout == "с": # статус (основной цвет)
                self.flatsNonFloorLayoutTemp = self.flatsLayout
                self.flats.sort(key=lambda x: x.getStatus()[1])

            elif self.flatsLayout == "с2": # цвет 2
                self.flatsNonFloorLayoutTemp = self.flatsLayout
                self.flats.sort(key=lambda x: x.color2, reverse=True)

            elif self.flatsLayout == "д": # дата последнего посещения
                self.flatsNonFloorLayoutTemp = self.flatsLayout
                self.flats.sort(key=lambda x: x.lastVisit)

            elif self.flatsLayout == "т": # телефон
                self.flatsNonFloorLayoutTemp = self.flatsLayout
                self.flats.sort(key=lambda x: x.phone, reverse=True)

            elif self.flatsLayout == "з": # заметка
                self.flatsNonFloorLayoutTemp = self.flatsLayout
                self.flats.sort(key=lambda x: x.note, reverse=True)

            elif self.flatsLayout == "и": # иконка
                self.flatsNonFloorLayoutTemp = self.flatsLayout
                self.flats.sort(key=lambda x: RM.icons.index(x.emoji))

            elif str(self.flatsLayout).isnumeric(): # сортировка по этажам
                self.rows = int(self.flatsLayout)
                self.columns = int(len(self.flats) / self.rows)
                row = [i for i in range(self.rows)]
                i = 0
                for r in range(self.rows):
                    row[r] = self.flats[i:i + self.columns]
                    i += self.columns
                row = row[::-1]
                del self.flats[:]
                for r in range(self.rows): self.flats += row[r]
                self.type = f"подъезд{self.rows}"

    def floors(self):
        """ Возвращает True, если в подъезде включен поэтажный вид """
        try:
            if str(self.flatsLayout).isnumeric(): return True
            else: return False
        except: return False

    def deleteHiddenFlats(self):
        """ Удаление скрытых квартир """
        finish = False
        while not finish:
            for i in range(len(self.flats)):
                if "." in self.flats[i].number and "подъезд" in self.type:
                    del self.flats[i]
                    break
            else:
                finish = True

    def adjustFloors(self, floors=None):
        """ Добавляем квартиры-заглушки до конца этажа, если запрошена неровная раскладка """
        if floors is None: floors = self.rows
        self.sortFlats("н")
        while 1:
            a = len(self.flats) / floors
            if not a.is_integer(): # собрать этажность не удалось, добавляем квартиру-заглушку в начало и пробуем снова
                self.flats.insert(0, Flat(number="0.1"))
            else:
                self.flatsLayout = floors
                self.rows = floors
                self.sortFlats()
                break

    def showFlats(self):
        """ Вывод квартир для вида подъезда """
        self.sortFlats()
        options = []
        if str(self.flatsLayout).isnumeric(): # вывод подъезда в этажной раскладке
            self.rows = int(self.flatsLayout)
            self.columns = int(len(self.flats) / self.rows)
            i = self.highestNumber = 0
            for r in range(self.rows):
                options.append(str(self.rows - r + self.floor1 - 1))
                for c in range(self.columns):
                    options.append(self.flats[i])
                    highest = int(ut.numberize(self.flats[i].number))
                    if highest > self.highestNumber:
                        self.highestNumber = highest
                    i += 1
        else: # вывод подъезда/сегмента простым списком
            self.rows = 1
            self.columns = 999
            options = self.flats
        if len(options) == 0 and self.type == "сегмент": RM.createFirstHouse = True
        return options

    def addFlat(self, input, virtual=False):
        """ Создает одну квартиру """
        input = input.strip()
        if input == "": return None
        self.flats.append(Flat(title=input.strip(), number=input.strip() if not virtual else "virtual", porchRef=self))
        last = len(self.flats)-1
        if "подъезд" in self.type: # в подъезде добавляем только новые квартиры, заданные диапазоном
            delete = False
            for i in range(last):
                if self.flats[i].number == self.flats[last].number: # flat with identical number (i) found
                    if self.flats[i].status == "" and self.flats[i].color2 == 0 and self.flats[i].emoji == "":
                        delete = True # no tenant and no records, delete silently
                    else: del self.flats[last] # delete the newly created empty flat
                    break
            if delete: del self.flats[i]

    def addFlats(self, start, finish, floors=None):
        """ Массовое создание квартир """
        for i in range(start, finish+1): self.addFlat("%s" % (str(i)))
        if "подъезд" in self.type:
            self.flatsLayout = str(floors)
            self.adjustFloors(int(floors))

    def export(self):
        return [
            self.title, self.pos, self.flatsLayout, self.floor1, self.note, self.type,
            [flat.export() for flat in self.flats]
        ]

class Flat(object):
    """ Класс квартиры/контакта"""
    def __init__(self, title="", note="", number="virtual", status="", color2=0, emoji="", phone="", lastVisit=0,
                 porchRef=None, extra=None):
        self.title = title # объединенный заголовок квартиры, например: "20, Василий 30 лет"
        self.note = note # заметка
        self.number = number # у адресных жильцов автоматически создается из первых символов title до запятой: "20"
                         # у виртуальных автоматически присваивается "virtual", а обычного номера нет
        self.status = status # статус, формируется динамически
        self.color2 = color2 # цвет кружочка
        self.emoji = emoji #"\U0001F601" # смайлик U+1F600 -> \U0001F600
        self.phone = phone # телефон
        self.lastVisit = lastVisit # дата последней встречи в абсолютных секундах (формат time.time())
        self.records = [] # список записей посещений
        if extra is None: extra = []
        self.extra = extra # пустой список на будущее
        self.porchRef = porchRef # указатель на подъезд, в котором находится квартира (не сохр.)
        self.buttonID = None # указатель на кнопку этой квартиры, если она есть (не сохр.)

    def getName(self):
        """ Генерирует имя жильца из title """
        if "," in self.title:
            return self.title[self.title.index(",") + 1:].strip()
        elif self.title.isnumeric(): # один номер
            if self.number != "virtual": return ""
            else: return self.title
        elif not self.title.isnumeric() and self.number == "virtual": # что-то помимо номера, но не запятая
            return self.title
        else: return ""

    def wipe(self):
        """ Полностью очищает квартиру, оставляя только номер """
        del self.records[:]
        self.status = self.note = self.phone = self.emoji = ""
        self.color2 = self.lastVisit = 0
        self.title = self.number
        if self.title == "virtual": self.title = ""

    def clone(self, flat2=None, title="", toStandalone=False):
        """ Делает из себя копию полученной квартиры """
        if toStandalone == False:
            self.title = copy(flat2.title)
            self.number = copy(flat2.number)
            self.phone = copy(flat2.phone)
            self.lastVisit = copy(flat2.lastVisit)
            self.status = copy(flat2.status)
            self.note = copy(flat2.note)
            for record in flat2.records:
                self.records.append(copy(record))

        else: # создаем отдельный контакт
            tempFlatNumber = self.title[0: self.title.index(",")] if "," in self.title else self.title
            RM.resources[1].append(House()) # create house address
            newVirtualHouse = RM.resources[1][len(RM.resources[1]) - 1]
            porch = self.porchRef.title if "подъезд" in self.porchRef.type else ""
            newVirtualHouse.addPorch(input=porch, type="virtual") # create virtual porch
            newVirtualHouse.porches[0].addFlat(self.getName(), virtual=True) # create flat
            newContact = newVirtualHouse.porches[0].flats[0]
            newContact.title = newContact.getName()
            if RM.house.type == "condo": newVirtualHouse.title = "%s–%s" % (title, tempFlatNumber)
            elif RM.house.noSegment():
                newVirtualHouse.title = tempFlatNumber if RM.house.listType() else f"{RM.house.title}, {tempFlatNumber}"
            else: newVirtualHouse.title = f"{self.porchRef.title}, {tempFlatNumber}"
            newVirtualHouse.type = "virtual"
            newContact.number = "virtual"
            newContact.records = copy(self.records)
            newContact.note = copy(self.note)
            newContact.status = copy(self.status)
            newContact.phone = copy(self.phone)
            newContact.lastVisit = copy(self.lastVisit)
            return newContact.title

    def showRecords(self):
        options = []
        for i in range(len(self.records)): # добавляем записи разговоров
            options.append(f"{RM.button['entry']} {self.records[i].date}|{self.records[i].title}")
        return options

    def addRecord(self, input):
        self.records.insert(0, Record(title=input))
        if len(self.records)==1 and self.status == "" and self.number != "virtual": # при первой записи ставим статус ?
            self.status="?"
        date = time.strftime("%d", time.localtime())
        if date[0] == "0": date = date[1:]
        month = RM.monthName()[5]
        timeCur = time.strftime("%H:%M", time.localtime())
        self.records[0].date = "%s %s %s" % (date, month, timeCur)
        self.lastVisit = time.time()
        return len(self.records)-1

    def editRecord(self, record, input):
        record.title = input
        self.updateStatus()

    def deleteRecord(self, record):
        i = self.records.index(record)
        del self.records[i]
        self.updateStatus()

    def is_empty(self):
        """ Проверяет, что в квартире нет никаких данных (кроме цвета 2 и иконки) """
        if len(self.records) == 0 and self.getName() == "" and self.note == "" and self.phone == "":
            return True
        else: return False

    def updateStatus(self):
        """ Обновление статуса квартиры после любой операции """
        if self.is_empty() and self.status == "?":      self.status = ""
        elif not self.is_empty() and self.status == "": self.status = "?"

    def updateName(self, choice):
        """ Получаем только имя и соответственно обновляем заголовок """
        if choice == "": self.title = self.number
        elif self.number == "virtual": self.title = choice
        else: self.title = self.number + ", " + choice
        self.updateStatus()

    def updateTitle(self, choice):
        """ Обновляем только заголовок (для немногоквартирных участков) """
        if choice == "": return
        elif self.getName() != "":
            self.number = choice
            self.title = self.number + ", " + self.getName()
        else:
            self.number = choice
            self.title = self.number
        self.updateStatus()

    def editNote(self, choice):
        self.note = choice.strip()
        self.updateStatus()

    def editPhone(self, choice):
        self.phone = choice.strip()
        self.updateStatus()

    def getStatus(self):
        """ Возвращает иконку и сортировочное значение статуса в int """
        if self.status == "":
            string = "{ }"
            value = 9
        elif self.status[0] == "0":
            string = "{0}"
            value = 6 # value нужно для сортировки квартир по статусу
        elif self.status[0] == "1":
            string = "{1}"
            value = 0
        elif self.status[0] == "2":
            string = "{2}"
            value = 1
        elif self.status[0] == "3":
            string = "{3}"
            value = 2
        elif self.status[0] == "4":
            string = "{4}"
            value = 3
        elif self.status[0] == "?":
            string = "{?}"
            value = 10
        elif self.status[0] == "5":
            string = "{5}"
            value = 7
        else:
            string = "{ }"
            value = 9
        return string, value

    def export(self):
        return [
            self.title, self.note, self.number, self.status, self.phone,
            self.lastVisit, self.color2, self.emoji, self.extra,
            [record.export() for record in self.records]
        ]

class Record(object):
    """ Класс записи посещения """
    def __init__(self, title="", date=""):
        self.title = title
        self.date = date

    def export(self):
        return [self.date, self.title]

# Класс отчета

class Report(object):
    def __init__(self):
        self.hours = RM.settings[2][0]
        self.credit = RM.settings[2][1]
        #self.placements = RM.settings[2][2]
        #self.videos = RM.settings[2][3]
        #self.returns = RM.settings[2][4]
        self.studies = RM.settings[2][5]
        self.startTime = RM.settings[2][6]
        self.endTime = RM.settings[2][7]
        self.reportTime = RM.settings[2][8]
        self.pauseTime = RM.settings[2][9]
        self.note = RM.settings[2][10]
        self.reminder = RM.settings[2][11]
        self.lastMonth = RM.settings[2][12]
        self.reportLogLimit = 100

    def getPauseDur(self):
        """ Возвращает длительность паузы, если она включена """
        if self.pauseTime == 0:
            difTime = 0
        else:
            curTime = int(time.strftime("%H", time.localtime())) * 3600 + \
                      int(time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
            difTime = curTime - self.pauseTime
        return difTime

    def saveReport(self, message="", mute=False, log=True, save=True, verify=False, forceNotify=False, tag=""):
        """ Выгрузка данных из класса в настройки, сохранение и оповещение """
        RM.settings[2] = [
            self.hours,
            self.credit,
            None, # бывшее self.placements,
            None, # бывшее self.videos,
            None, # бывшее self.returns,
            self.studies,
            self.startTime,
            self.endTime,
            self.reportTime,
            self.pauseTime,
            self.note,
            self.reminder,
            self.lastMonth
        ]
        date = time.strftime("%d.%m", time.localtime()) + "." + str(int(time.strftime("%Y", time.localtime())) - 2000)
        time2 = time.strftime("%H:%M:%S", time.localtime())
        if not mute:
            RM.resources[2].insert(0, f"\n{date} {time2}  {message}{tag}") # запись в журнал
        if log:
            message = message.replace("[b]", "")
            message = message.replace("[/b]", "")
            RM.log(message, forceNotify=forceNotify) # вывод на toast или уведомление
        if save: RM.save(verify=verify)

    def checkNewMonth(self, forceDebug=False):
        if Devmode: return
        RM.dprint("Определяем начало нового месяца.")
        savedMonth = RM.settings[3]
        currentMonth = time.strftime("%b", time.localtime())
        if savedMonth != currentMonth or forceDebug:
            if RM.displayed.form == "rep": RM.mainList.clear_widgets()
            saveTimer = self.startTime
            Clock.schedule_once(lambda x: RM.popup(message=RM.msg[221], options=[RM.button["yes"], RM.button["no"]]), 2)
            RM.popupForm = "submitReport"

            # Calculate rollovers
            rolloverHours = round(self.hours, 2) - int(round(self.hours, 2))
            self.hours = int(round(self.hours, 2) - rolloverHours)
            rolloverCredit = round(self.credit, 2) - int(round(self.credit, 2))
            self.credit = int(round(self.credit, 2) - rolloverCredit)

            if RM.settings[0][2] and self.credit > 0.0:
                credit = f"{RM.msg[222]} {ut.timeFloatToHHMM(self.credit)[0: ut.timeFloatToHHMM(self.credit).index(':')]}\n"
            else: credit = ""

            # Save file of last month
            service = f"{RM.msg[42]}{':' if RM.language != 'hy' else '.'} {RM.emoji['check']}\n" # служение было
            studies = f"{RM.msg[103]}{RM.col} {self.studies}\n" if self.studies > 0 else ""
            hours = f"{RM.msg[104]}{RM.col} {ut.timeFloatToHHMM(self.hours)[0: ut.timeFloatToHHMM(self.hours).index(':')]}\n" \
                if self.hours >= 1 else ""
            self.lastMonth = RM.msg[223] % RM.monthName()[3] + "\n" + service + studies + hours
            if credit != "": self.lastMonth += f"{RM.msg[224]}{RM.col} %s" % credit

            # Clear service year in October
            if int(time.strftime("%m", time.localtime())) == 10:
                RM.settings[4] = [None, None, None, None, None, None, None, None, None, None, None, None]

            hourCap = 55
            if self.hours >= hourCap: # обрезаем общий итог до 55 часов, если нужно
                self.credit = 0
            elif self.hours + self.credit >= hourCap:
                self.hours = hourCap
                self.credit = 0

            # Save last month hour+credit into service year
            RM.settings[4][RM.monthName()[7] - 1] = self.hours + self.credit
            RM.analyticsMessageCached = None

            self.clear(rolloverHours, rolloverCredit)
            RM.settings[3] = time.strftime("%b", time.localtime())
            self.reminder = 1
            self.saveReport(mute=True, log=False)
            if saveTimer != 0: # если при окончании месяца работает таймер, принудительно выключаем его
                self.startTime = saveTimer
                Clock.schedule_once(RM.timerPressed, 0.1)

    def toggleTimer(self):
        result = 0
        if not self.startTime and self.getPauseDur() == 0:
            self.modify("(")
        elif self.getPauseDur() != 0:
            self.modify("+")
        else: result = 1 if RM.settings[0][2] == 0 else 2 # если в настройках включен кредит, спрашиваем
        return result

    def getCurrentHours(self):
        """ Выдает общее количество часов в этом месяце с кредитом (str) [0],
            запас/отставание (float) [1] и
            строку с текстом показа запаса/отставания (str) [2] """
        value = self.hours + (self.credit if RM.settings[0][2] else 0)
        gap = value - float(time.strftime("%d", time.localtime())) * RM.settings[0][3] / ut.days()
        if RM.settings[0][3] == 0: gap_str = ""
        elif gap >= 0: gap_str = " (+%s)" % ut.timeFloatToHHMM(gap)
        else: gap_str = " (-%s)" % ut.timeFloatToHHMM(-gap)
        return ut.timeFloatToHHMM(value), gap, gap_str

    def clear(self, rolloverHours, rolloverCredit):
        """ Clears all fields of report """
        self.hours = 0.0 + rolloverHours
        self.credit = 0.0 + rolloverCredit
        #self.placements = 0 не используется с октября 2023, но пока не удаляем
        #self.videos = 0
        #self.returns = 0
        self.studies = 0
        self.startTime = 0
        self.endTime = 0
        self.reportTime = 0.0
        self.pauseTime = 0
        self.note = ""
        self.reminder = 1

    def modify(self, input=" "):
        """ Modifying report on external commands using internal syntax """
        tag = f"|{RM.serviceTag}" if RM.serviceTag != "" else "" # символ "|" служит для отделения подписи от остальной записи

        if input == "(":  # запуск таймера
            self.startTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
                time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
            forceNotify = True if RM.settings[0][0] == 1 else False
            self.saveReport(RM.msg[225], forceNotify=forceNotify)

        elif input == "-":  # постановка на паузу
            self.pauseTime = int(time.strftime("%H", time.localtime())) * 3600 + \
                             int(time.strftime("%M", time.localtime())) * 60 + \
                             int(time.strftime("%S", time.localtime()))
            self.saveReport(RM.msg[327], mute=True)

        elif input == "+":  # снятие с паузы
            self.startTime += self.getPauseDur()
            self.pauseTime = 0
            forceNotify = True if RM.settings[0][0] == 1 else False
            self.saveReport(RM.msg[328], mute=True, forceNotify=forceNotify)

        elif input == ")": # остановка таймера
            if self.startTime > 0:
                self.endTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
                    time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
                self.reportTime = (self.endTime - self.startTime) / 3600 # получаем часы из секунд
                if self.reportTime < 0: self.reportTime += 24  # if timer worked after 0:00
                self.hours += self.reportTime
                self.startTime = self.pauseTime = 0
                self.saveReport(RM.msg[226] % ut.timeFloatToHHMM(self.reportTime), save=False, tag=tag)
                RM.serviceTag = ""
                self.reportTime = 0.0
                self.saveReport(mute=True, log=False, save=True)

        elif input == "$": # остановка таймера с кредитом
            if self.startTime > 0:
                self.endTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
                    time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
                self.reportTime = (self.endTime - self.startTime) / 3600
                if self.reportTime < 0: self.reportTime += 24 # if timer worked after 0:00
                self.credit += self.reportTime
                self.startTime = 0
                self.saveReport(RM.msg[227] % ut.timeFloatToHHMM(self.reportTime), save=False, tag=tag)
                RM.serviceTag = ""
                self.reportTime = 0.0
                self.saveReport(mute=True, log=False, save=True) # после выключения секундомера делаем резервную копию принудительно

        elif "ч" in input or "к" in input:
            if input[0] == "ч": # часы
                if input == "ч":
                    self.hours += 1
                else:
                    self.hours = ut.timeHHMMToFloat(RM.time3)
                self.saveReport(RM.msg[321] % input[1:], log=False, tag=tag)
                RM.serviceTag = ""
            elif input[0] == "к": # кредит
                if input == "к":
                    self.credit += 1
                else:
                    self.credit = ut.timeHHMMToFloat(RM.time3)
                self.saveReport(RM.msg[322] % input[1:], log=False, tag=tag)
                RM.serviceTag = ""

    def optimizeReportLog(self):
        if Devmode: return
        RM.dprint("Оптимизируем размер журнала отчета.")
        def __optimize(*args):
            if len(RM.resources[2]) > self.reportLogLimit:
                extra = len(RM.resources[2]) - self.reportLogLimit
                for i in range(extra):
                    del RM.resources[2][len(RM.resources[2]) - 1]
        if RM.desktop: _thread.start_new_thread(__optimize, ("Thread-Cut", 0,))
        else: __optimize()


    def getCurrentMonthReport(self):
        """ Выдает отчет текущего месяца """
        credit = f"{RM.msg[222]} {ut.timeFloatToHHMM(self.credit)[0: ut.timeFloatToHHMM(self.credit).index(':')]}\n" \
            if RM.settings[0][2] else ""
        service = f"{RM.msg[42]}{':' if RM.language != 'hy' else '.'} {RM.emoji['check']}\n" # служение было
        studies = f"{RM.msg[103]}{RM.col} {self.studies}\n" if self.studies > 0 else ""
        hours = f"{RM.msg[104]}{RM.col} {ut.timeFloatToHHMM(self.hours)[0: ut.timeFloatToHHMM(self.hours).index(':')]}\n" \
            if self.hours >= 1 else ""
        result = RM.msg[223] % RM.monthName()[1] + "\n" + service + studies + hours
        if credit != "": result += f"{RM.msg[224]}{RM.col} %s" % credit
        return result

    def getLogEntry(self, type):
        """ Выдает строку для записи в журнал """
        if type == "studies":
            result = f"{RM.msg[103]}{RM.col} [b]{self.studies}[/b]"
        elif type == "+1 study":
            result = f"{RM.msg[103]}{RM.col} [b]+1[/b]"
        elif type == "-1 study":
            result = f"{RM.msg[103]}{RM.col} [b]-1[/b]"
        elif type == "hours":
            result = f"{RM.msg[104]}{RM.col} [b]{ut.timeFloatToHHMM(self.hours)}[/b]"
        elif type == "credit":
            result = f"{RM.msg[43]}{RM.col} [b]{ut.timeFloatToHHMM(self.credit)}[/b]"
        else:
            result = ""
        return result

# Классы интерфейса

class DisplayedList(object):
    """ Класс, описывающий содержимое и параметры списка, выводимого на RM.mainList """
    def __init__(self):
        self.update()

    def update(self, message="", title="", form="", options=None, sort=None, details=None,
               footer=None, positive="", neutral="", nav=None, jump=None, tip=None, back=True):
        if options is None: options = []
        if footer is None: footer = []
        self.message = message
        self.title = title
        self.form = form
        self.options = options
        self.positive = positive
        self.neutral = neutral
        self.sort = sort
        self.details = details
        self.nav = nav
        self.footer = footer
        self.back = back
        self.jump = jump
        self.tip = tip

class TipButton(Button):
    """ Заметки и предупреждения (невидимые кнопки) """
    def __init__(self, text="", size_hint_y=1, font_size=None, color=None, background_color=None, height=None,
                 size_hint_x=1,
                 padding=None, font_size_force=False, halign="left", valign="center", *args, **kwargs):
        super(TipButton, self).__init__()
        self.text = text
        self.size_hint_x = size_hint_x
        self.size_hint_y = size_hint_y
        if RM.specialFont is not None: self.font_name = RM.specialFont
        if height is not None: self.height = height
        if not RM.desktop or font_size_force:
            self.font_size = font_size if font_size is not None else RM.fontS * RM.fontScale()
        if RM.bigLanguage: self.font_size = self.font_size * .9
        self.markup = True
        self.background_normal = ""
        self.background_down = ""
        self.halign = halign
        self.valign = valign
        self.padding = [RM.padding*3, RM.padding] if padding is None else padding
        self.pos_hint = {"center_x": .5}
        self.color = RM.standardTextColor
        if color is not None: self.color = color
        self.background_color = background_color if background_color is not None else RM.globalBGColor

class EmptyButton(Widget):
    """ Невидимая последняя кнопка в списке для решения бага, когда последняя кнопка не нажимается """
    def __init__(self, height):
        super(EmptyButton, self).__init__()
        self.size_hint_y = None
        self.height = height * .7

class MainScroll(GridLayout):
    def __init__(self, *args, **kwargs):
        super(MainScroll, self).__init__()
        self.spacing = RM.spacing * 1.5
        self.padding = RM.padding * 2
        self.size_hint_y = None

class MyLabel(Label):
    def __init__(self, text="", color=None, halign=None, valign=None, text_size=None, size_hint=None,
                 size_hint_y=1, font_size_force=False, padding=(0,0),
                 height=None, width=None, pos_hint=None, font_size=None, *args, **kwargs):
        super(MyLabel, self).__init__()
        self.markup = True
        self.color = color if color is not None else RM.standardTextColor
        if halign is not None: self.halign = halign
        if valign is not None: self.valign = valign
        if text_size is not None: self.text_size = text_size
        if height is not None: self.height = height
        if width is not None: self.width = width
        if size_hint is not None: self.size_hint = size_hint
        if size_hint_y != 1: self.size_hint_y = size_hint_y
        if pos_hint is not None: self.pos_hint = pos_hint
        if not RM.desktop or font_size_force:
            self.font_size = font_size if font_size is not None else RM.fontS * RM.fontScale()
        if RM.bigLanguage: self.font_size = self.font_size * .9
        if RM.specialFont is not None:
            self.font_name = RM.specialFont
        self.padding = padding
        self.text = text

class TitleLabel(MyLabel):
    """ Версия MyLabel для заголовка страницы"""
    def __init__(self, *args, **kwargs):
        super(TitleLabel, self).__init__()
        self.color = RM.pageTitleColor
        self.halign = "center"
        self.valign = "center"
        self.markup = True
        self.font_size = RM.fontS * (1.33 if RM.desktop else (1.1 * RM.fontScale(cap=1.2)))

class MyTextInputCutCopyPaste(Bubble):
    # Internal class used for showing the little bubble popup when
    # copy/cut/paste happen.

    textinput = ObjectProperty(None)
    ''' Holds a reference to the TextInput this Bubble belongs to.
    '''

    but_cut = ObjectProperty(None)
    but_copy = ObjectProperty(None)
    but_paste = ObjectProperty(None)
    but_selectall = ObjectProperty(None)

    matrix = ObjectProperty(None)

    _check_parent_ev = None

    def __init__(self, **kwargs):
        self.mode = 'normal'
        super().__init__(**kwargs)
        self._check_parent_ev = Clock.schedule_interval(self._check_parent, .5)
        self.matrix = self.textinput.get_window_matrix()

        with self.canvas.before:
            Callback(self.update_transform)
            PushMatrix()
            self.transform = Transform()

        with self.canvas.after:
            PopMatrix()

    def update_transform(self, cb):
        m = self.textinput.get_window_matrix()
        if self.matrix != m:
            self.matrix = m
            self.transform.identity()
            self.transform.transform(self.matrix)

    def transform_touch(self, touch):
        matrix = self.matrix.inverse()
        touch.apply_transform_2d(
            lambda x, y: matrix.transform_point(x, y, 0)[:2])

    def on_touch_down(self, touch):
        try:
            touch.push()
            self.transform_touch(touch)
            if self.collide_point(*touch.pos):
                FocusBehavior.ignored_touch.append(touch)
            return super().on_touch_down(touch)
        finally:
            touch.pop()

    def on_touch_up(self, touch):
        try:
            touch.push()
            self.transform_touch(touch)
            for child in self.content.children:
                if ref(child) in touch.grab_list:
                    touch.grab_current = child
                    break
            return super().on_touch_up(touch)
        finally:
            touch.pop()

    def on_textinput(self, instance, value):
        global Clipboard
        if value and not Clipboard and not _is_desktop:
            value._ensure_clipboard()

    def _check_parent(self, dt):
        # this is a prevention to get the Bubble staying on the screen, if the
        # attached textinput is not on the screen anymore.
        parent = self.textinput
        while parent is not None:
            if parent == parent.parent:
                break
            parent = parent.parent
        if parent is None:
            self._check_parent_ev.cancel()
            if self.textinput:
                self.textinput._hide_cut_copy_paste()

    def on_parent(self, instance, value):
        parent = self.textinput
        mode = self.mode

        if parent:
            self.content.clear_widgets()
            if mode == 'paste':
                # show only paste on long touch
                self.but_selectall.opacity = 1
                widget_list = [self.but_selectall, ]
                if not parent.readonly:
                    widget_list.append(self.but_paste)
            elif parent.readonly:
                # show only copy for read only text input
                widget_list = (self.but_copy, )
            else:
                # normal mode
                widget_list = (self.but_cut, self.but_copy, self.but_paste)

            for widget in widget_list:
                self.content.add_widget(widget)

    def do(self, action):
        textinput = self.textinput

        if action == 'cut':
            textinput._cut(textinput.selection_text)
        elif action == 'copy':
            textinput.copy()
        elif action == 'paste':
            textinput.paste()
        elif action == 'selectall':
            textinput.select_all()
            self.mode = ''
            anim = Animation(opacity=0, d=.3)
            anim.bind(on_complete=lambda *args: self.on_parent(self, self.parent))
            anim.start(self.but_selectall)
            return

        self.hide()

    def hide(self):
        parent = self.parent
        if not parent:
            return

        anim = Animation(opacity=0, d=.1)
        anim.bind(on_complete=lambda *args: parent.remove_widget(self))
        anim.start(self)

class MyTextInput(TextInput):
    def __init__(self, multiline=False, size_hint_y=1, size_hint_x=1, hint_text="", pos_hint = {"center_y": .5},
                 text="", disabled=False, input_type="text", width=0, height=None, #mode="below_target",
                 time=False, popup=False, halign="left", valign="center", focus=False, color=None, limit=99999,
                 padding=None, wired_border=True, rounded=False, shrink=False, id=None,
                 specialFont=False, background_color=None, background_disabled_normal=None,
                 font_size=None, font_size_force=False, blockPositivePress=False, *args, **kwargs):
        super(MyTextInput, self).__init__()
        if not RM.desktop or font_size_force:
            self.font_size = font_size if font_size is not None else (RM.fontS * RM.fontScale())
        if RM.specialFont is not None or specialFont: self.font_name = RM.differentFont
        if background_disabled_normal is not None: self.background_disabled_normal = background_disabled_normal
        self.multiline = multiline
        self.id = id
        self.markup = True
        self.limit = limit
        self.halign = halign
        self.valign = valign
        self.size_hint_x = size_hint_x
        self.size_hint_y = size_hint_y
        self.pos_hint = pos_hint
        self.height = height if height is not None else RM.standardTextHeight
        self.background_active = ""
        self.wired_border = wired_border
        self.rounded = rounded
        if padding is not None: self.padding = padding
        else:
            self.padding = (RM.spacing*2, 2) if not RM.desktop else (4, 6)
            if self.height >= RM.standardTextHeight * RM.enlargedTextCo:
                self.padding[1] = self.height * .25
            else:
                self.padding[1] = self.height * .15
        self.width = width
        self.input_type = input_type
        self.text = f"{text}".strip()
        self.disabled = disabled
        self.blockPositivePress = blockPositivePress
        self.hint_text = hint_text
        self.hint_text_color = RM.topButtonColor
        self.use_bubble = True
        self.shrink = shrink
        Window.softinput_mode = "resize" if self.shrink else "below_target"
        self.popup = popup
        self.focus = focus
        self.time = time
        self.write_tab = False
        self.menu = 0
        if RM.mode == "dark":
            self.disabled_foreground_color = [.8, .8, .8]
            self.hint_text_color = RM.topButtonColor
        else:
            self.disabled_foreground_color = [.4, .4, .4]
            self.hint_text_color = [.5, .5, .5]
        self.background_normal = ""
        self.background_disabled_normal = ""
        self.cursor_color = RM.titleColor
        self.cursor_color[3] = .9
        if self.popup:
            self.foreground_color = "white"
            self.height = RM.standardTextHeight * (1 if RM.desktop else 1.1)
        elif color is not None:
            self.foreground_color = self.disabled_foreground_color = color
        else:
            self.foreground_color = "black" if RM.mode == "light" else "white"
        if background_color is not None: self.background_color = background_color
        elif not self.popup:
            self.background_color = RM.textInputBGColor
        else:
            self.cursor_color = RM.titleColorOnBlack
            self.background_color = [.2, .2, .2, 1] # темный фон текста

    def insert_text(self, char, from_undo=False):
        """ Делаем буквы заглавными """
        if len(self.text) >= self.limit: # превышен лимит - показываем предупреждение и выходим
            if not RM.desktop and RM.allowCharWarning:
                RM.log(RM.msg[189] % RM.charLimit, timeout=2)
                RM.allowCharWarning = False
                def __turnToTrue(*args):
                    RM.allowCharWarning = True
                Clock.schedule_once(__turnToTrue, 5)
            return
        elif self.input_type != "text": # цифры и даты
            if f"{RM.button['arrow']} {RM.msg[16]}" in RM.pageTitle.text : # дата
                if char.isnumeric():
                    return super().insert_text(char, from_undo=from_undo)
                elif char == "-":
                    return super().insert_text("-", from_undo=from_undo)
            elif char.isnumeric(): return super().insert_text(char, from_undo=from_undo) # цифры
            elif self.time: # часы - превращаем все символы кроме цифр в двоеточия
                return super().insert_text(":", from_undo=from_undo)
        else: # обычный текст - с капитализацией
            def __capitalize():
                string = self.text[: self.cursor_index()].strip()
                l = len(string) - 1
                if len(string) > 0 and (string[l] == "." or string[l] == "!" or string[l] == "?") or \
                        self.cursor_col == 0:
                    return True # можно
                else: return False # нельзя
            if __capitalize() and RM.language != "ka" and RM.settings[0][11] and not RM.desktop:
                if len(char) == 1: char = char.upper()
                else: char = char[0].upper() + char[1:]
            return super().insert_text(char, from_undo=from_undo)

    def on_text_validate(self):
        if not self.popup and not self.blockPositivePress:
            RM.positivePressed(instance=self)

    def on_focus(self, instance=None, value=None):

        if not value: # сохранение некоторых видов данных в полях ввода при простом дефокусе

            if self.id == "regular": # обычный счетчик: изучения, квартиры и т .д.
                if self.text.strip() == "":
                    self.text = "0"
                if RM.displayed.form == "rep" and self == RM.studies.input: # сохранение изучений
                    RM.rep.studies = int(self.text)
                    RM.rep.saveReport(message=RM.rep.getLogEntry("studies"), log=False)

            elif self.id == "hours": # счетчик часов
                if self.text.strip() == "":
                    self.text = "0:00"
                elif not ":" in self.text:
                    self.text += ":00"
                try:
                    float = ut.timeHHMMToFloat(self.text)
                    self.text = ut.timeFloatToHHMM(float)
                    if self == RM.hours.input:
                        RM.rep.hours = ut.timeHHMMToFloat(self.text)
                        RM.rep.saveReport(message=RM.rep.getLogEntry("hours"), log=False)
                    elif self == RM.credit.input:
                        RM.rep.credit = ut.timeHHMMToFloat(self.text)
                        RM.rep.saveReport(message=RM.rep.getLogEntry("credit"), log=False)
                except:
                    # проверка на правильность ввода времени, иначе показывается ошибка,
                    # а значение не сохраняется
                    RM.popup(message=RM.msg[46])

            elif self.id == "serviceTag": # добавление описания служения
                RM.serviceTag = instance.text.strip()
                self.focus = False

            elif RM.displayed.form == "set":  # настройки
                if RM.msg[52] in RM.settingsPanel.current_tab.text and len(RM.popups) == 0: # лимит часов
                    RM.settings[0][3] = int(instance.text)
                    RM.analyticsMessageCached = None
                elif RM.msg[55] in RM.settingsPanel.current_tab.text: # блокнот
                    RM.resources[0][0] = RM.inputBoxEntry.text.strip()
                RM.save()

            elif RM.displayed.form == "rep" and self == RM.repBox: # правка отчета прошлого месяца на странице отчета
                RM.rep.lastMonth = RM.repBox.text
                RM.rep.saveReport(mute=True)

            elif RM.firstCallPopup and RM.phoneInputOnPopup: # сохранение телефона на плашке первого посещения
                RM.flat.editPhone(RM.quickPhone.text)
                RM.save()
                if RM.porch.clearCache("т") or RM.porch.clearCache("с"): RM.porchView(instance=instance)
                else: RM.clickedInstance.update(RM.flat)

        if platform == "android":
            self.keyboard_mode = "managed"
        elif RM.desktop:
            return

        if value:  # вызов клавиатуры
            Clock.schedule_once(self.create_keyboard, .01)
            if self.shrink: # ручной механизм поднятия экрана над клавиатурой
                def __shrinkWidgets(*args):
                    RM.globalFrame.size_hint_y = None
                    RM.globalFrame.height = Window.height - RM.keyboardHeight() - RM.standardTextHeight
                    RM.globalFrame.remove_widget(RM.boxFooter)
                    RM.boxHeader.size_hint_y = 0
                    RM.titleBox.size_hint_y = 0
                Clock.schedule_once(__shrinkWidgets, .1)
        else:
            self.hide_keyboard()
            self.keyboard_mode = "auto"
            if self.shrink:
                RM.boxHeader.size_hint_y = RM.titleSizeHintY
                RM.titleBox.size_hint_y = RM.tableSizeHintY
                RM.globalFrame.size_hint_y = 1
                if RM.boxFooter not in RM.globalFrame.children: RM.globalFrame.add_widget(RM.boxFooter)

    def keyboard_on_key_up(self, window=None, keycode=None):
        """ Реагирование на ввод в реальном времени в зависимости от формы """
        if RM.displayed.form == "rep" and RM.msg[49] in RM.reportPanel.current_tab.text: # служебный год
            RM.analyticsMessageCached = None
            RM.recalcServiceYear(allowSave=True)
        elif RM.firstCallPopup and RM.phoneInputOnPopup: # плашка первого посещения, активация кнопки телефона при вводе номера
            if RM.quickPhone.text != RM.flat.phone:
                RM.savePhoneBtn.text = RM.button["check"]
                RM.savePhoneBtn.disabled = False
            else:
                RM.savePhoneBtn.text = ""
                RM.savePhoneBtn.disabled = True
            if RM.quickPhone.text != "":
                RM.quickPhoneCallButton.text = RM.button['phone-square']
                RM.quickPhoneCallButton.disabled = False
            else:
                RM.quickPhoneCallButton.text = ""
                RM.quickPhoneCallButton.disabled = True

    def _show_cut_copy_paste(self, pos, win, parent_changed=False, mode='', pos_in_window=False, *l):
        """ Show a bubble with cut copy and paste buttons """
        def __do(*args):
            if not self.use_bubble:
                return

            bubble = self._bubble
            if bubble is None:
                self._bubble = bubble = MyTextInputCutCopyPaste(textinput=self)
                self.fbind('parent', self._show_cut_copy_paste, pos, win, True)

                def hide_(*args):
                    return self._hide_cut_copy_paste(win)

                self.bind(
                    focus=hide_,
                    cursor_pos=hide_,
                )
            else:
                win.remove_widget(bubble)
                if not self.parent:
                    return
            if parent_changed:
                return

            # Search the position from the touch to the window
            lh, ls = self.line_height, self.line_spacing

            x, y = pos
            t_pos = (x, y) if pos_in_window else self.to_window(x, y)
            bubble_size = bubble.size
            bubble_hw = bubble_size[0] / 2.
            win_size = win.size
            bubble_pos = (t_pos[0], t_pos[1] + inch(.25))

            if (bubble_pos[0] - bubble_hw) < 0:
                # bubble beyond left of window
                if bubble_pos[1] > (win_size[1] - bubble_size[1]):
                    # bubble above window height
                    bubble_pos = (bubble_hw, (t_pos[1]) - (lh + ls + inch(.25)))
                    bubble.arrow_pos = 'top_left'
                else:
                    bubble_pos = (bubble_hw, bubble_pos[1])
                    bubble.arrow_pos = 'bottom_left'
            elif (bubble_pos[0] + bubble_hw) > win_size[0]:
                # bubble beyond right of window
                if bubble_pos[1] > (win_size[1] - bubble_size[1]):
                    # bubble above window height
                    bubble_pos = (
                        win_size[0] - bubble_hw,
                        (t_pos[1]) - (lh + ls + inch(.25))
                    )
                    bubble.arrow_pos = 'top_right'
                else:
                    bubble_pos = (win_size[0] - bubble_hw, bubble_pos[1])
                    bubble.arrow_pos = 'bottom_right'
            else:
                if bubble_pos[1] > (win_size[1] - bubble_size[1]):
                    # bubble above window height
                    bubble_pos = (
                        bubble_pos[0],
                        (t_pos[1]) - (lh + ls + inch(.25))
                    )
                    bubble.arrow_pos = 'top_mid'
                else:
                    bubble.arrow_pos = 'bottom_mid'

            bubble_pos = self.to_widget(*bubble_pos, relative=True)
            bubble.center_x = bubble_pos[0]
            if bubble.arrow_pos[0] == 't':
                bubble.top = bubble_pos[1]
            else:
                bubble.y = bubble_pos[1]
            bubble.mode = mode
            Animation.cancel_all(bubble)
            bubble.opacity = 0
            win.add_widget(bubble, canvas='after')
            Animation(opacity=1, d=.1).start(bubble)
        if RM.desktop: __do()
        else: Clock.schedule_once(__do, .3)

    def create_keyboard(self, *args):
        self.show_keyboard()

    def remove_focus_decorator(function):
        def wrapper(self, touch):
            if not self.collide_point(*touch.pos): self.focus = False
            function(self, touch)
        return wrapper

    @remove_focus_decorator
    def on_touch_down(self, touch):
        super().on_touch_down(touch)

class FloorView(DragBehavior, GridLayout):
    """ Сетка подъезда """
    def __init__(self, porch, instance=None, *args, **kwargs):
        super(FloorView, self).__init__()
        try:
            if instance.text.lower() == RM.button['yes']: updated = True # нажата кнопка "Сохранить" на форме квартир
            else: updated = False
        except: updated = False
        self.porch = porch
        size = RM.standardTextHeightUncorrected * (RM.settings[0][8] ** 0.5) # размер кнопки квартиры на сетке
        self.row_default_height = size
        self.col_default_width = size
        self.cols_minimum = {0: RM.floorLabelWidth}
        self.cols = self.porch.columns + 1
        self.rows = self.porch.rows
        self.row_force_default = True
        self.col_force_default = True
        self.spacing = RM.spacing * (2 if RM.desktop else 1.5)
        self.padding = RM.padding, RM.padding*2, RM.padding*2, RM.padding*2
        self.GS = [ # Grid Size - реальный размер сетки подъезда
            (size+self.spacing[0]*1.8) * (self.cols-1) + RM.floorLabelWidth,
            (size + self.spacing[0]*1.4) * self.rows
        ]
        self.oversized = True if self.GS[0] > RM.mainList.size[0] or self.GS[1] > RM.mainList.size[1] else False
        o1 = 0 if RM.orientation == "v" else RM.horizontalOffset/2
        o2 = .351 if RM.orientation == "v" else .365
        self.centerPos = [Window.size[0] / 2 - self.GS[0] / 2 - o1, 0 - Window.size[1] * o2 + self.GS[1] / 2]

        if self.porch.floorview is None and updated: # первичное создание подъезда или обновление параметров существующего
            if self.oversized: # форсируем заполняющий режим, если слишком большой подъезд
                self.pos = [0, 0] # 0,0 - верхний левый угол mainList - для RelativeLayout
                self.porch.pos[0] = False
            else: # подъезд не слишком большой - ставим в центр
                self.pos = self.centerPos
                self.porch.pos[0] = True
        elif self.porch.pos[0]: # заход в уже существующий подъезд
            if self.oversized: # если подъезд перестал влезать, заполняем
                self.pos = [0, 0]
                self.porch.pos[0] = False
            else:
                self.pos = self.porch.pos[1] if self.porch.pos[1] != [0, 0] else self.centerPos
                self.porch.pos[0] = True
        else: # повторный заход в подъезд в том же сеансе, режим заполнения
            self.pos = [0, 0]
            self.porch.pos[0] = False

        if self.porch.pos[0]: # можно таскать
            self.drag_distance = 30
            self.drag_timeout = 250
        else: # заполняющий режим - нельзя таскать
            self.drag_distance = 9999
            self.drag_timeout = 0

        if self.porch.pos[0] and self.pos != self.centerPos and RM.resources[0][1][6] == 0:
            # при первом перемещении показываем подсказку
            RM.popup(title=RM.msg[247], message=RM.msg[13] % RM.button["adjust"])
            RM.resources[0][1][6] = 1
            RM.save()

class TTab(TabbedPanelHeader):
    """ Вкладки панелей """
    def __init__(self, text=""):
        super(TTab, self).__init__()
        if not RM.desktop: self.font_size = RM.fontXS * RM.fontScale(cap=1.2)
        if RM.specialFont is not None: self.font_name = RM.specialFont
        self.markup = True
        self.defaultText = text
        self.background_normal = "void.png"
        self.background_down = RM.tabColors[1]

class TopButton(Button):
    """ Кнопки поиска и настроек """
    def __init__(self, text="", size_hint_x=None, halign="center"):
        super(TopButton, self).__init__()
        if RM.specialFont is not None: self.font_name = RM.specialFont
        self.text = text
        self.halign = halign
        self.valign = "center"
        self.font_size = RM.fontXL * (.9 if RM.desktop else .77)
        self.markup = True
        self.size_hint_x = 1 if size_hint_x is None else size_hint_x
        self.pos_hint = {"center_y": .5}
        self.background_normal = ""
        self.background_down = ""

class SettingsButton(Button):
    """ Кнопка с тремя точками"""
    def __init__(self, id):
        super(SettingsButton, self).__init__()
        self.id = id
        self.text = RM.button['ellipsis'] if id is not None else ""
        self.size_hint_x = RM.ellipsisWidth
        self.valign = "bottom" if not RM.displayed.form == "houseView" else "center"
        self.font_size = (RM.fontXL * 1.15 * RM.fontScale(cap=1.2)) if not RM.desktop else RM.fontXXL
        self.markup = True
        self.background_normal = ""
        self.background_down = ""
        if self.id is None: self.disabled = True

    def on_release(self):
        def __press(*args):
            RM.detailsPressed(instance=self, id=self.id)
        Clock.schedule_once(__press, 0)

class Timer(Button):
    """ Виджет таймера """
    def __init__(self):
        super(Timer, self).__init__()
        self.diameter = [1.5, 1.2] # размер при обычном и нажатом состоянии таймера
        self.defaultSize = RM.fontL * 1.1# if not RM.desktop else RM.fontL * 1.3
        self.font_size = self.defaultSize * self.diameter[0]
        self.markup = True
        self.background_normal = ""
        self.background_down = ""

    def on_press(self):
        self.font_size = self.defaultSize * self.diameter[1]
        Clock.schedule_once(self.step2, 0.05)

    def step2(self, *args):
        self.font_size = self.defaultSize * self.diameter[0]

    def on_release(self):
        RM.timerPressed()

    def updateIcon(self):
        if RM.rep.startTime == 0:       self.stop()
        elif RM.rep.getPauseDur() != 0: self.pause()
        else:                           self.unpause()

    def stop(self):
        """ Остановка таймера """
        self.text = icon("icon-play-circle")
        self.color = RM.timerOffColor

    def pause(self):
        """ Постановка таймера на паузу """
        self.text = icon("icon-pause-circle")
        self.color = RM.timerOffColor
        RM.timerText.color = RM.disabledColor

    def unpause(self):
        """ Снятие таймера с паузы """
        self.text = icon("icon-pause-circle-o")  # снято с паузы, время идет
        self.color = RM.titleColor
        RM.timerText.color = RM.timerTextColorOn

class RetroButton(Button):
    """ Трехмерная кнопка в стиле Kivy """
    def __init__(self, text="", size_hint_x=1, size_hint_y=1, size=None, disabled=False, font_name=None, height=None,
                 width=None, pos_hint=None, background_normal=None, color=None, font_size=None, alpha=None, pos=None,
                 force_font_size=False, background_down=None, background_color=None, halign="center", valign="center"):
        super(RetroButton, self).__init__()
        self.size_hint_x = size_hint_x
        self.size_hint_y = size_hint_y
        if size is not None: self.size = size
        self.disabled = disabled
        if font_name is not None: self.font_name = font_name
        if not RM.desktop or force_font_size:
            self.font_size = RM.fontXS * RM.fontScale(cap=1.2) if font_size is None else font_size
        if RM.specialFont is not None: self.font_name = RM.specialFont
        self.background_color = background_color if background_color is not None else RM.blackTint
        if height is not None: self.height = height
        if width is not None: self.width = width
        self.text = text
        if color is not None: self.color = color
        if pos_hint is not None: self.pos_hint = pos_hint
        if pos is not None: self.pos = pos
        if background_normal is not None: self.background_normal = background_normal
        if background_down is not None: self.background_down = background_down
        self.markup = True
        self.halign = halign
        self.valign = valign
        if alpha is not None: self.background_color[3] = alpha

    def hide(self):
        self.text = ""
        self.disabled = True

    def unhide(self):
        self.disabled = False

class TableButton(Button):
    """ Кнопки в шапке таблицы и ниже на некоторых формах """
    def __init__(self, text="", disabled=False, size_hint_x=1):
        super(TableButton, self).__init__()
        if not RM.desktop: self.font_size = RM.fontXS * RM.fontScale(cap=1.2)
        if RM.specialFont is not None: self.font_name = RM.specialFont
        self.text = text.strip()
        self.markup = True
        self.size_hint_x = size_hint_x
        self.disabled = disabled
        self.disabled_color = RM.topButtonColor if RM.mode == "light" else "darkgray"
        self.background_normal = ""
        self.background_disabled_normal = ""
        self.background_down = ""

class TerTypeButton(Button):
    """ Кнопка выбора типа участка (одиночная) """
    def __init__(self, type, on=False):
        super(TerTypeButton, self).__init__()
        self.on = on
        if not RM.desktop: self.font_size = RM.fontXS * RM.fontScale(cap=1.2)
        if RM.specialFont is not None: self.font_name = RM.specialFont
        self.markup = True
        if RM.theme != "3D":
            self.background_normal = ""
            self.background_disabled_normal = ""
            self.background_down = ""
        self.type = type
        self.halign = "center"
        self.valign = "center"
        self.padding = RM.padding, 0
        size = RM.fontXL if RM.language != "hy" else RM.fontM
        color = get_hex_from_color(RM.scrollIconColor) # цвет иконки в неактивном состоянии
        color2 = get_hex_from_color(RM.standardTextColor) # цвет текста в неактивном состоянии

        if self.type == "condo":
            text = RM.msg[231].replace("#", "\n")
            self.defaultTextOff = f"[size={size}]{icon('icon-building')}[/size]\n\n{text}"
            self.defaultTextOn = f"[color={color}][size={size}]{icon('icon-building')}[/size][/color]\n\n[color={color2}]{text}[/color]"
        elif self.type == "private":
            text = RM.msg[232].replace("#", "\n")
            self.defaultTextOff = f"[size={size}]{icon('icon-map')}[/size]\n\n{text}"
            self.defaultTextOn = f"[color={color}][size={size}]{icon('icon-map')}[/size][/color]\n\n[color={color2}]{text}[/color]"
        elif self.type == "list":
            text = RM.msg[233].replace("#", "\n")
            self.defaultTextOff = f"[size={size}]{icon('icon-list-ul')}[/size]\n\n{text}"
            self.defaultTextOn = f"[color={color}][size={size}]{icon('icon-list-ul')}[/size][/color]\n\n[color={color2}]{text}[/color]"
        self.update(on)

    def update(self, on):
        self.on = on
        size = RM.fontM
        if not self.on: # обновление радиокнопки
            colorOff = RM.linkColor # цвет кнопки в неактивном состоянии
            self.button = f"[size={size}][color={get_hex_from_color(colorOff)}]{RM.button['dot-off']}[/color][/size]"
            self.text = f"{self.defaultTextOn}\n\n{self.button}"
        else:
            colorOn = RM.linkColor if RM.mode == "light" else RM.titleColor # # цвет иконки в активном состоянии
            self.button = f"[size={size}][color={get_hex_from_color(colorOn)}]{RM.button['dot'] if self.on else RM.button['dot-off']}[/color][/size]"
            self.text = f"{self.defaultTextOff}\n\n{self.button}"

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            for widget in self.parent.children:
                widget.on = False
            self.on = True
            return True

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.click()
            return True

    def click(self):
        for widget in self.parent.children:
            if not "Label" in str(widget): widget.update(False)
        if self.type == "condo": hint = RM.msg[70] # обновление текста подсказки
        elif self.type == "private": hint = RM.msg[166]
        elif self.type == "list":
            string = ""
            for char in RM.msg[70]:
                string += char
                if char == ":" or char == ".": break
            hint = f"{string} A1"
        RM.inputBoxEntry.hint_text = hint
        self.update(True)

class FontCheckBox(Button):
    """ Галочка из кнопки и шрифтовой иконки """
    def __init__(self, text="", active=False, size_hint=(1, 1), pos_hint=None, width=0, height=0, icon="check",
                 color=None, padding=[0,0], button_color=None, font_size=None, setting=None,
                 force_font_size=False, button_size=None, halign="center", valign="center", *args, **kwargs):
        super(FontCheckBox, self).__init__()
        self.text = text
        self.background_normal = ""
        self.background_down = ""
        self.background_color = RM.globalBGColor
        self.background_disabled_normal = ""
        self.active = active
        self.value = active # только для считывания состояния
        self.halign = halign
        self.valign = valign
        self.padding = padding
        self.button_color = button_color
        self.size_hint = size_hint
        self.icon = icon
        if pos_hint is not None: self.pos_hint = pos_hint
        self.width = width
        self.height = height
        if not RM.desktop or force_font_size:
            if font_size is not None: self.font_size = font_size
        if RM.specialFont is not None: self.font_name = RM.specialFont
        self.button_size = button_size if button_size is not None else self.font_size
        self.markup = True
        self.color = RM.standardTextColor if color is None else color
        self.defaultText = self.text
        self.setting = setting
        self.update()

    def update(self):
        if self.icon == "check":
            icon_on = icon('icon-check-square')
            icon_off = icon('icon-square-o')
        elif self.icon == "toggle":
            icon_on = icon('icon-toggle-on')
            icon_off = icon('icon-toggle-off')
        if not self.active:
            colorOff = RM.linkColor
            self.button = f"[size={int(self.button_size)}][color={get_hex_from_color(colorOff)}][b]{icon_off}[/b][/color][/size]"
            self.value = True
        else:
            colorOn = RM.linkColor if self.button_color is None else self.button_color
            self.button = f"[size={int(self.button_size)}][color={get_hex_from_color(colorOn)}][b]{icon_on if self.active else icon_off}[/b][/color][/size]"
            self.value = False
        self.text = f"{self.button}  {self.defaultText}" if self.text != "" else self.button

    def on_release(self):
        self.active = False if self.active else True
        self.update()

        if RM.displayed.form == "set":  # Сохранение настроек через переключатели
            if self.setting == RM.msg[40]:     # таймер
                RM.settings[0][22] = self.active
                RM.updateSettings()
            elif self.setting == RM.msg[129]:  # служение по телефону
                RM.settings[0][20] = self.active
            elif self.setting == RM.msg[130]:  # уведомление при таймере
                RM.settings[0][0] = self.active
            elif RM.msg[206] in self.setting:  # нет дома
                RM.settings[0][13] = self.active
            elif self.setting == RM.msg[128]:  # кредит часов
                RM.settings[0][2] = self.active
            elif self.setting == RM.msg[87]:   # новое предложение с заглавной
                RM.settings[0][11] = self.active
            elif self.setting == RM.msg[164]:  # запоминать положение окна
                RM.settings[0][12] = self.active
            RM.save()

        elif RM.displayed.form == "repLog": # галочка в журнале отчета
            RM.repLogCheck = self.active
            RM.updateList(self, progress=True)

class FloatButton(Button):
    """ Кнопка для быстрой прокрутки списка вниз """
    def __init__(self, text, size, pos=None, font_size=None, **kwargs):
        super(FloatButton, self).__init__()
        self.markup = True
        self.font_name = RM.differentFont
        self.text = text
        self.size = size
        self.size_hint = None, None
        if pos is not None: self.pos = pos
        if font_size is not None: self.font_size = font_size
        self.halign = "center"
        self.valign = "center"

class RoundColorButton(Button):
    def __init__(self, color, side=None, pos=None, size_hint=(None, None), text="", pos_hint=None):
        super(RoundColorButton, self).__init__()
        if pos is not None: self.pos = pos
        if pos_hint is not None: self.pos_hint = pos_hint
        self.text = text
        self.color = color
        self.size_hint = size_hint
        if side is not None: self.size = side, side
        self.background_normal = ""
        self.background_down = ""

class ProgressButton(Button):
    def __init__(self):
        super(ProgressButton, self).__init__()

class RoundButton(Button):
    """ Круглая кнопка """
    def __init__(self, text="", size_hint_x=1, size_hint_y=1, size=None, disabled=False, font_name=None,
                 font_size=None, rounded=False, height=None, pos_hint=None, **kwargs):
        super(RoundButton, self).__init__()
        if not RM.desktop:
            self.font_size = RM.fontXS * RM.fontScale(cap=1.2) if font_size is None else font_size
        if RM.bigLanguage: self.font_size = self.font_size * .9
        if font_name is not None: self.font_name = font_name
        if size is not None: self.size = size
        if height is not None: self.height = height
        if pos_hint is not None: self.pos_hint = pos_hint
        self.disabled = disabled
        self.text = text
        self.rounded = rounded
        if RM.specialFont is not None: self.font_name = RM.specialFont
        self.size_hint_x = size_hint_x
        self.size_hint_y = size_hint_y
        self.markup = True
        self.background_normal = ""
        self.background_down = ""
        self.halign = self.valign = "center"
        self.padding = RM.padding, RM.padding

class RoundButtonClassic(Button):
    """ Круглая кнопка из предыдущих версий, без стиля в kv, не мигает при нажатии """

    def __init__(self, text="", size_hint_x=1, size_hint_y=1, text_size=(None, None), halign="center",
                 font_name=None, padding=None, disabled=False,
                 valign="center", size=None, font_size=None, background_normal="", color=None, background_color=None,
                 markup=True, background_down="", **kwargs):
        super(RoundButtonClassic, self).__init__()
        if not RM.desktop: self.font_size = font_size if font_size is not None else RM.fontS
        if RM.specialFont is not None: self.font_name = RM.specialFont
        if font_name is not None: self.font_name = font_name
        self.markup = markup
        self.padding = padding if padding is not None else (RM.padding, RM.padding)
        self.text = text
        self.disabled = disabled
        self.size_hint_x = size_hint_x
        self.size_hint_y = size_hint_y
        self.size = size if size is not None else Window.size
        self.halign = halign
        self.valign = valign
        self.text_size = text_size
        self.background_normal = ""
        self.color = color if color is not None else RM.tableColor
        self.background_down = background_down
        if background_color is not None: self.background_color = background_color

        if RM.theme != "3D":
            self.background_normal = background_normal
            self.color = RM.tableColor if color is None else color
            self.background_color[3] = 0
            with self.canvas.before:
                self.shape_color = Color(rgba=[self.background_color[0], self.background_color[1],
                                               self.background_color[2], 1])
                self.shape = SmoothRoundedRectangle(pos=self.pos, size=self.size, radius=RM.getRadius(instance=self)[1])
                self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def on_press(self, *args):
        if RM.theme != "3D":
            with self.canvas.before:
                self.shape_color = Color(rgba=self.background_color)
                self.shape = SmoothRoundedRectangle(pos=self.pos, size=self.size, radius=RM.getRadius(instance=self)[1])
                self.bind(pos=self.update_shape, size=self.update_shape)

class PopupButton(Button):
    """ Кнопка на всплывающем окне """
    def __init__(self, text="", height=None, font_name=None, pos_hint=None, disabled=False, cap=True,
                 font_size=None, size_hint_x=None, size_hint_y=None, forceSize=False, **kwargs):
        super(PopupButton, self).__init__()
        if not RM.desktop or forceSize:
            self.font_size = (RM.fontS * .9 * RM.fontScale(cap=1.2)) if font_size is None else font_size
        if RM.specialFont is not None: self.font_name = RM.specialFont
        if font_name is not None: self.font_name = font_name
        self.markup = True
        self.padding = RM.padding
        self.halign = "center"
        self.valign = "center"
        self.size_hint_y = size_hint_y
        self.disabled = disabled
        if size_hint_x is not None: self.size_hint_x = size_hint_x
        self.height = RM.standardTextHeight * 1.2 if height is None else height
        self.text = text.upper() if cap and RM.language != "ka" and "icomoon.ttf" not in text else text
        self.background_down = ""
        self.background_normal = ""
        if pos_hint is not None: self.pos_hint = pos_hint

class PopupButtonGray(PopupButton):
    """ Кнопка на всплывающем окне, совпадающая по цвету с текстовым полем ввода """
    def __init__(self, text, height=None, size_hint_x=None, size_hint_y=None, disabled=False, **kwargs):
        super(PopupButtonGray, self).__init__()
        self.text = text
        if size_hint_x is not None: self.size_hint_x = size_hint_x
        if size_hint_y is not None: self.size_hint_y = size_hint_y
        if height is not None: self.height = height
        self.disabled = disabled
        self.background_disabled_normal = ""

class FirstCallButton(Button):
    """ Кнопки на плашке первого посещения, базовый класс """
    def __init__(self, text=""):
        super(FirstCallButton, self).__init__()
        self.text = text
        if not RM.desktop: self.font_size = RM.fontS * RM.fontScale(cap=1.2)
        if RM.specialFont is not None: self.font_name = RM.specialFont
        self.markup = True
        self.halign = "center"
        self.background_down = ""
        self.background_normal = ""

class FirstCallButton1(FirstCallButton):
    """ Кнопка нет дома """
    def __init__(self, **kwargs):
        super(FirstCallButton1, self).__init__()
        self.text = RM.button['lock']

class FirstCallButton2(FirstCallButton):
    """ Кнопка запись """
    def __init__(self, **kwargs):
        super(FirstCallButton2, self).__init__()
        self.text = RM.button['record']

class FirstCallButton3(FirstCallButton):
    """ Кнопка отказ """
    def __init__(self, **kwargs):
        super(FirstCallButton3, self).__init__()
        self.text = RM.button['reject']

class FloorLabel(Label):
    """ Номер этажа """
    def __init__(self, flat, width, font_size):
        super(FloorLabel, self).__init__()
        self.text = flat # в данном случае это просто номер этажа
        self.size_hint = [1, 1]
        self.width = width
        self.height = RM.standardTextHeight * RM.settings[0][8] * RM.fontScale(cap=1.2)
        self.font_size = font_size
        self.halign = "center"
        self.valign = "center"
        self.color = RM.standardTextColor
        self.text_size = self.height * RM.fontScale(cap=1.2), None

class FlatButton(Button):
    """ Кнопка квартиры (обычная или скрытая) – базовый класс """
    def __init__(self, flat, size_hint_y=1, height=0, id=0, recBox=None):
        super(FlatButton, self).__init__()
        self.markup = True
        self.flat = flat
        self.background_normal = ""
        self.background_down = ""
        self.markup = True
        self.padding = RM.padding, 0
        self.recBox = recBox
        self.size_hint_y = size_hint_y
        self.height = height
        self.id = id
        self.flat.buttonID = self
        self.halign = "center"

    def update(self, flat):
        """ Обновление отрисовки кнопки в режиме сетки без ее перемонтировки - либо при создании,
        либо при удалении/восстановлении квартиры """
        self.flat = flat
        if RM.porch.floors():
            if not RM.desktop: self.font_size = RM.flatSizeInGrid
            gap = ("\n" if not RM.porch.pos[0] and RM.screenRatio > RM.flatSizeRatio else " ") if flat.emoji != "" else ""
            number = flat.number
            self.text = f"{number}{gap}{flat.emoji}"
        else:
            name = flat.getName()
            gap = " " if name != "" else ""
            number = f"[b]{flat.number}[/b] {name}"
            self.text = f"{number}{gap}{flat.emoji}"
            if self.recBox is not None: self.updateRecord()
            self.halign = "center" if RM.settings[0][10] < 2 else "left"
            self.valign = "center" if RM.settings[0][10] < 2 else "top"
            if not RM.desktop:
                if RM.settings[0][10] == 1:     self.font_size = RM.flatSizeInList
                elif RM.settings[0][10] == 2:   self.font_size = RM.fontXS * RM.fontScale(cap=1.2)
                elif RM.settings[0][10] >= 3:   self.font_size = RM.fontXXS * RM.fontScale(cap=1.2)
        if self.number != flat.number: self.number = flat.number
        if self.status != flat.status: self.status = flat.status
        if self.color2 != flat.color2: self.color2 = flat.color2
        if "." in flat.number and RM.porch.floors(): self.text = icon('icon-plus-circle')

    def updateRecord(self):
        """ Обновление записей под кнопкой в режиме списка """
        if RM.settings[0][10] <= 2 or (RM.orientation == "h" and RM.settings[0][10] == 3):
            if self.flat.phone != "":
                myicon = RM.button["phone-thin"]
                phone = f"[color={RM.recordGray}]{myicon}[/color]\u00A0{self.flat.phone}\u00A0\u00A0"
            else: phone = ""
            if self.flat.note != "":
                myicon = RM.button["note"]
                if RM.msg[206].lower() in self.flat.note[:30]:
                    limit = self.flat.note.index("\n") if "\n" in self.flat.note else len(self.flat.note)
                else: limit = RM.defaultLimit
                note = f"[color={RM.recordGray}]{myicon}[/color]\u00A0[i]{self.flat.note[:limit]}[/i]\u00A0\u00A0"
                if "\n" in note: note = note[: note.index("\n")] + "  "
            else: note = ""
            if len(self.flat.records) > 0:
                myicon = RM.button["chat"]
                rec = self.flat.records[0].title.replace("\n", " ")
                record = f"[color={RM.recordGray}]{myicon}[/color]\u00A0{rec}"
            else: record = ""
            text = phone + note + record
        else: text = ""
        if len(self.recBox.children) == 1: self.recBox.add_widget(FlatFooterLabel(text))
        label = self.recBox.children[0]
        if label.text != text: label.text = text
        self.recBox.height = RM.height1 * (1 if label.text == "" else 1.85)

    def on_release(self,):
        if self.flat is not None: self.flat.buttonID = self
        if icon('icon-plus-circle') in self.text:
            RM.porch.restoreFlat(instance=self)
            RM.save()
            RM.porchView(update=False, instance=self)
        else:
            RM.scrollClick(instance=self)

class FlatButtonSquare(FlatButton):
    """ Кнопка квартиры в режиме сетки """
    def __init__(self, flat):
        super(FlatButtonSquare, self).__init__(flat=flat)
        self.update(flat)

class FlatFooterLabel(Label):
    """ Записи под квартирой в режиме списка """
    def __init__(self, text, *args, **kwargs):
        super(FlatFooterLabel, self).__init__()
        self.text = text
        self.markup = True
        self.color = RM.standardTextColor
        self.halign = "left"
        self.valign = "top"
        self.size_hint = .98, 1
        self.pos_hint = {"right": 1}
        self.font_size = (RM.fontXS * RM.fontScale(cap=1.2)) if not RM.desktop else RM.fontS
        if RM.specialFont is not None: self.font_name = RM.specialFont

class PopupNoAnimation(Popup):
    """ Попап, в котором отключена анимация при закрытии """
    def __init__(self, **kwargs):
        super(PopupNoAnimation, self).__init__(**kwargs)
        try:
            if RM.specialFont is not None: self.title_font = RM.specialFont
        except: pass

    def open(self, *_args, **kwargs):
        if self._is_open: return
        self._window = Window
        self._is_open = True
        self.dispatch('on_pre_open')
        Window.add_widget(self)
        Window.bind(on_resize=self._align_center, on_keyboard=self._handle_keyboard)
        self.center = (Window.center[0] + (0 if RM.orientation == "v" else RM.horizontalOffset/2),
                       Window.center[1])
        self.fbind('center', self.center)
        self.fbind('size', self.center)
        ani = Animation(_anim_alpha=1, d=0)
        ani.bind(on_complete=lambda *_args: self.dispatch('on_open'))
        ani.start(self)

    def dismiss(self, *largs, **kwargs):
        if self._window is None: return
        if self.dispatch('on_dismiss'):
            if not kwargs.get('force', False): return
        self._anim_alpha = 0
        self._real_remove_widget()

class SortListButton(Button):
    """ Пункт выпадающего списка """
    def __init__(self, text="", size_hint_y=None, font_name=None):
        super(SortListButton, self).__init__()
        self.markup = True
        self.size_hint_y = size_hint_y
        self.height = RM.standardTextHeightUncorrected * 1.4 if not RM.desktop else 40
        if not RM.desktop: self.font_size = RM.fontXS * RM.fontScale(cap=1.2)
        if font_name is not None: self.font_name = font_name
        elif RM.specialFont is not None: self.font_name = RM.specialFont
        self.halign = "center"
        self.valign = "center"
        self.text = text
        self.background_normal = ""
        self.disabled_color = RM.topButtonColor if RM.mode == "light" else "darkgray"
        if RM.theme != "3D": self.background_disabled_normal = ""
        self.background_down = ""

class ScrollButton(Button):
    """ Пункты всех списков кроме квартир """
    def __init__(self, id, text, height, valign="center", size_hint_y=1):
        super(ScrollButton, self).__init__()
        self.id = id # номер пункта, который передается элементу скролла и соответствует displayed.options
        self.text = text
        self.height = height
        self.halign = "left"
        self.valign = valign
        self.padding = (RM.padding*5, 0)
        self.markup = True
        self.size_hint_y = size_hint_y
        self.footers = []
        self.pos_hint = {"center_x": .5}
        if not RM.desktop:
            self.font_size = int(RM.fontM*.95 * RM.fontScale()) if RM.displayed.form == "ter" else int(RM.fontS * RM.fontScale())
        if RM.specialFont is not None: self.font_name = RM.specialFont
        if RM.theme != "3D":
            self.background_normal = ""
            self.background_down = ""
        else:
            self.background_color = [.7,.7,.7]

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.state = "down"
            for f in self.footers: f.state = "down"
            RM.scrollClick(instance=self)

    def on_touch_up(self, touch):
        self.state = "normal"

class FooterButton(Button):
    """ Вкладки под пунктами списка с индикаторами """
    def __init__(self, text, parentIndex):
        super(FooterButton, self).__init__()
        self.spacing = RM.spacing
        self.text = text
        self.markup = True
        if RM.specialFont is not None: self.font_name = RM.specialFont
        self.parentIndex = parentIndex
        self.background_down = ""
        self.background_normal = ""
        self.valign = "center"
        self.halign = "left" if icon('icon-home') in text and RM.displayed.form == "con" else "center"
        self.font_size = (RM.fontS if RM.desktop else RM.fontXXS*.9) * RM.fontScale(cap=1.2)

    def on_release_(self):
        RM.btn[self.parentIndex].state = "down"
        RM.btn[self.parentIndex].on_release()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            RM.btn[self.parentIndex].state = "down"
            for f in RM.btn[self.parentIndex].footers: f.state = "down"
            RM.scrollClick(instance=RM.btn[self.parentIndex])

class RecordButton(Button):
    """ Кнопка с записью посещения на экране квартиры """
    def __init__(self, text, id):
        super(RecordButton, self).__init__()
        self.text = text
        self.markup = True
        self.halign = "left"
        self.valign = "top"
        self.id = id
        if RM.theme == "3D": self.background_color = RM.blackTint
        else:
            self.background_down = ""
            self.background_normal = ""
        if not RM.desktop: self.font_size = RM.fontS * RM.fontScale()
        self.padding = RM.padding * 4, RM.padding * 4.5
        self.spacing = RM.spacing
        self.pos_hint = {"right": 1}
        self.size_hint_x = .86

    def on_release(self):
        RM.scrollClick(instance=RM.btn[self.id])

class Counter(AnchorLayout):
    """ Виджет счетчика """
    def __init__(self, type="int", text="0", disabled=False, width=None,
                 picker=None, # определяет тип счетчика: None или текстовая строка от окон добавления времени
                 ):
        super(Counter, self).__init__()
        self.anchor_x = "center"
        self.anchor_y = "center"

        box = BoxLayout(orientation="vertical", size_hint=(None, None),
                        spacing=RM.spacing if RM.theme != "3D" else 0,
                        width=RM.standardTextWidth * 2.3 if width is None else width,
                        height=RM.standardTextHeight * (2.2 if RM.orientation == "v" else 1.6))

        self.input = MyTextInput(id="regular" if picker is None else "hours",
                                 text=text, disabled=disabled, multiline=False, # ввод
                                 halign="center", time=True if picker is not None else False, size_hint=(1, None),
                                 font_size=RM.fontBigEntry, height=RM.standardTextHeight, input_type="number")

        box.add_widget(self.input)

        buttonBox = BoxLayout(size_hint_y=1 if RM.orientation=="v" else .6,  # второй бокс для кнопок
                              spacing=RM.spacing if RM.theme != "3D" else 0)
        box.add_widget(buttonBox)

        if RM.theme != "3D": self.btnDown = RoundButton(text=icon("icon-minus"), disabled=disabled) # кнопка вниз
        else: self.btnDown = RetroButton(text=icon("icon-minus"), disabled=disabled)

        def __countDown(instance=None):
            try:
                if type != "time":
                    if int(self.input.text) > 0: self.input.text = str(int(self.input.text) - 1)
                else:
                    hours = self.input.text[: self.input.text.index(":")]
                    if int(hours) < 1: self.input.text = "0:00"
                    else:
                        minutes = self.input.text[self.input.text.index(":") + 1:]
                        self.input.text = "%d:%s" % (int(hours) - 1, minutes)
            except: pass

        self.btnDown.bind(on_release=__countDown)
        buttonBox.add_widget(self.btnDown)

        if RM.theme != "3D": self.btnUp = RoundButton(text=icon("icon-plus"), disabled=disabled) # кнопка вверх
        else: self.btnUp = RetroButton(text=icon("icon-plus"), disabled=disabled)

        def __plusPress(self):
            if picker == RM.msg[108] or picker == RM.msg[109]:
                RM.popupForm = "showTimePicker"
                RM.popup(title=picker)
        self.btnUp.bind(on_release=__plusPress)

        def __countUp(instance=None):
            if type != "time": self.input.text = str(int(self.input.text) + 1)
            elif picker == RM.msg[108]: self.input.text = ut.timeFloatToHHMM(RM.rep.hours)
            elif picker == RM.msg[109]: self.input.text = ut.timeFloatToHHMM(RM.rep.credit)
        self.btnUp.bind(on_release=__countUp)
        buttonBox.add_widget(self.btnUp)

        self.add_widget(box)

    def get(self):
        return self.input.text

    def update(self, update):
        self.input.text = update

class ColorStatusButton(Button):
    """ Кнопка выбора цвета """
    def __init__(self, status="", text=""):
        super(ColorStatusButton, self).__init__()
        self.size_hint_max_y = .5
        self.side = (RM.mainList.size[0] - RM.padding * 2 - RM.spacing * 14.5) / 7
        self.size_hint = [None, None]
        self.height = self.side if RM.orientation == "v" else RM.standardTextHeight
        self.width = self.side
        self.text = text
        self.status = status
        self.markup = True
        self.background_normal = ""
        if RM.theme != "3D":
            self.background_color = RM.roundButtonBGColor
        else:
            self.background_down = ""
            self.background_color = RM.getColorForStatus(self.status)

    def on_release(self):
        if self.status != "": self.text = RM.button["dot"]
        def __click(*args):
            if self.status == "1" and RM.resources[0][1][5] == 0:
                RM.popup(title=RM.msg[247], message=RM.msg[82])
                RM.resources[0][1][5] = 1
            if len(RM.flat.records) == 0:
                if RM.multipleBoxEntries[0].text.strip() != "":
                    RM.flat.updateName(RM.multipleBoxEntries[0].text.strip())
                if RM.multipleBoxEntries[1].text.strip() != "":
                    RM.flat.addRecord(RM.multipleBoxEntries[1].text.strip())
            for i in ["0", "1", "2", "3", "4", "5", ""]:
                if self.status == "":
                    self.text = ""
                    RM.popup("resetFlatToGray", message=RM.msg[193], options=[RM.button["yes"], RM.button["no"]])
                    return False
                elif self.status == i:
                    RM.flat.status = i
                    if len(RM.stack) > 0: del RM.stack[0]
                    break
            RM.house.statsCached = None
            RM.save()
            if RM.searchEntryPoint: RM.find(instance=True)
            else: RM.porchView(instance=self)
        Clock.schedule_once(__click, 0)

class MainMenuButton(TouchRippleBehavior, Button):
    """ Три главные кнопки внизу экрана """
    def __init__(self, text, **kwargs):
        super(MainMenuButton, self).__init__()
        self.markup = True
        self.height = 0
        self.pos_hint = {"center_y": .5}
        if not RM.desktop:
            self.iconFont = int(RM.fontL)
            if not RM.bigLanguage: self.font_size = RM.fontXS * .8 * RM.fontScale()
            else: self.font_size = RM.fontXS * .8
        else:
            self.iconFont = int(RM.fontXL * 1.1)
            if RM.bigLanguage and RM.orientation == "h":
                self.font_size = RM.fontXXS*.9
            else: self.font_size = RM.fontS
        if RM.specialFont is not None: self.font_name = RM.specialFont
        self.text = text
        self.iconTer1 = 'icon-map'
        self.iconTer1ru = 'icon-building'
        self.iconTer2 = 'icon-map-o'
        self.iconTer2ru = 'icon-building-o'
        self.iconCon1 = 'icon-address-book'
        self.iconCon2 = 'icon-address-book-o'
        self.iconRep1 = 'icon-file-text'
        self.iconRep2 = 'icon-file-text-o'
        self.valign = self.halign = "center"
        self.size_hint = (1, 1)
        self.markup = True
        self.background_normal = ""
        self.background_down = ""
        self.ripple_duration_out = .15
        self.ripple_fade_from_alpha = 1 if RM.mode == "light" else .3
        self.ripple_fade_to_alpha = 0

    def activate(self):
        col = get_hex_from_color(RM.mainMenuActivated)
        if RM.msg[2] in self.text:
            self.text = f"[color={col}][size={self.iconFont}]{icon(self.iconTer1ru)}[/size]\n{RM.msg[2]}[/color]" if RM.language == "ru" or RM.language == "uk" \
                else f"[color={col}][size={self.iconFont}]{icon(self.iconTer1)}[/size]\n{RM.msg[2]}[/color]"
        elif RM.msg[3] in self.text: self.text = f"[color={col}][size={self.iconFont}]{icon(self.iconCon1)}[/size]\n{RM.msg[3]}[/color]"
        elif RM.msg[4] in self.text: self.text = f"[color={col}][size={self.iconFont}]{icon(self.iconRep1)}[/size]\n{RM.msg[4]}[/color]"

    def deactivate(self):
        col = get_hex_from_color(RM.mainMenuButtonColor)
        if RM.msg[2] in self.text:
            self.text = f"[color={col}][size={self.iconFont}]{icon(self.iconTer2ru)}[/size][/color]\n{RM.msg[2]}" if RM.language == "ru" \
                else f"[color={col}][size={self.iconFont}]{icon(self.iconTer2)}[/size]\n{RM.msg[2]}[/color]"
        elif RM.msg[3] in self.text: self.text = f"[color={col}][size={self.iconFont}]{icon(self.iconCon2)}[/size]\n{RM.msg[3]}[/color]"
        elif RM.msg[4] in self.text: self.text = f"[color={col}][size={self.iconFont}]{icon(self.iconRep2)}[/size]\n{RM.msg[4]}[/color]"

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.ripple_show(touch)
            return True

    def on_touch_up(self, touch=None):
        if self.collide_point(*touch.pos):
            if RM.msg[2] in self.text: RM.terPressed(self)
            elif RM.msg[3] in self.text: RM.conPressed(self)
            elif RM.msg[4] in self.text: RM.repPressed(self)
            self.ripple_fade()
            RM.updateMainMenuButtons()
            return True

class RejectColorSelectButton(AnchorLayout):
    """ Виджет из трех кнопок в настройках для выбора цвета отказа """
    def __init__(self):
        super(RejectColorSelectButton, self).__init__()
        if RM.settings[0][18] == "4":
            text1 = RM.button["dot"]
            text2 = ""
            text3 = ""
        elif RM.settings[0][18] == "5":
            text1 = ""
            text2 = ""
            text3 = RM.button["dot"]
        else:
            text1 = ""
            text2 = RM.button["dot"]
            text3 = ""
        self.b1 = RoundButtonClassic(text=text1, color="white", background_color=RM.getColorForStatus("4"))
        self.b2 = RoundButtonClassic(text=text2, color="white", background_color=RM.getColorForStatus("0"))
        self.b3 = RoundButtonClassic(text=text3, color="white", background_color=RM.getColorForStatus("5"))
        self.b1.bind(on_press=self.change)
        self.b2.bind(on_press=self.change)
        self.b3.bind(on_press=self.change)
        self.anchor_x = "center"
        self.anchor_y = "center"
        box = BoxLayout(spacing=RM.spacing * (2 if RM.desktop else 1), size_hint=(1, RM.settingButtonHintY))
        self.add_widget(box)
        box.add_widget(self.b1)
        box.add_widget(self.b2)
        box.add_widget(self.b3)

    def change(self, instance):
        self.b1.text = ""
        self.b2.text = ""
        self.b3.text = ""
        instance.text = RM.button["dot"]
        if instance is self.b1:   RM.settings[0][18] = "4"
        elif instance is self.b2: RM.settings[0][18] = "0"
        else:                     RM.settings[0][18] = "5"
        RM.save()

class DatePicker(BoxLayout):
    """ Виджет календаря для выбора даты взятия участка """
    def __init__(self, *args, **kwargs):
        super(DatePicker, self).__init__(**kwargs)
        self.date = datetime.datetime.strptime(RM.multipleBoxEntries[1].text, "%Y-%m-%d")
        self.orientation = "vertical"
        self.month_names = (RM.msg[259], RM.msg[263], RM.msg[265], RM.msg[267], RM.msg[269], RM.msg[271],
                            RM.msg[273], RM.msg[275], RM.msg[277], RM.msg[279], RM.msg[281], RM.msg[261])
        if "month_names" in kwargs:
            self.month_names = kwargs['month_names']
        self.header = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), padding=(RM.padding, 0, RM.padding, RM.padding*5))
        self.body = GridLayout(cols = 7)
        self.add_widget(self.header)
        self.add_widget(self.body)
        self.populate_body()
        self.populate_header()

    def populate_header(self, *args, **kwargs):
        self.header.clear_widgets()
        k, r, bg = .3, 0.7, [.22, .22, .22, .9]
        if RM.theme != "3D":
            previous_month = PopupButton(text=RM.button["chevron-left"], color="white", size_hint_x=k,
                                         background_color=bg)
            next_month = PopupButton(text=RM.button["chevron-right"], color="white", size_hint_x=k,
                                     background_color=bg)
        else:
            previous_month = RetroButton(text=RM.button["chevron-left"], size_hint_x=k,
                                         color = RM.mainMenuButtonColor)
            next_month = RetroButton(text=RM.button["chevron-right"], size_hint_x=k,
                                     color=RM.mainMenuButtonColor)
        previous_month.bind(on_release=partial(self.move_previous_month))
        next_month.bind(on_release=partial(self.move_next_month))
        month_year_text = self.month_names[self.date.month -1] + ' ' + str(self.date.year)
        current_month = MyLabel(text=f"[b]{month_year_text}[/b]", markup=True, color=[.95,.95,.95])
        self.header.add_widget(previous_month)
        self.header.add_widget(current_month)
        self.header.add_widget(next_month)

    def populate_body(self, *args, **kwargs):
        self.body.clear_widgets()
        self.date_cursor = datetime.date(self.date.year, self.date.month, 1)
        for filler in range(self.date_cursor.isoweekday()-1):
            self.body.add_widget(MyLabel(text=""))
        while self.date_cursor.month == self.date.month:
            date_label = Button(text = str(self.date_cursor.day), background_normal="",
                                background_down="", background_color=RM.popupBackgroundColor)
            date_label.bind(on_press=partial(self.set_date, day=self.date_cursor.day))
            date_label.bind(on_release=self.pick)
            if self.date.day == self.date_cursor.day:
                date_label.background_color = RM.titleColor
                date_label.background_color[3] = .5
            self.body.add_widget(date_label)
            self.date_cursor += datetime.timedelta(days=1)

    def pick(self, instance=None):
        def __do(*args):
            RM.dismissTopPopup()
            RM.multipleBoxEntries[1].text = str(self.date)
        Clock.schedule_once(__do, 0)

    def set_date(self, *args, **kwargs):
        self.date = datetime.date(self.date.year, self.date.month, kwargs['day'])
        self.populate_body()
        self.populate_header()

    def move_next_month(self, *args, **kwargs):
        if self.date.month == 12:
            self.date = datetime.date(self.date.year + 1, 1, self.date.day)
        else:
            try: self.date = datetime.date(self.date.year, self.date.month + 1, self.date.day)
            except: self.date = datetime.date(self.date.year, self.date.month + 1, self.date.day - 1)
        self.populate_header()
        self.populate_body()

    def move_previous_month(self, *args, **kwargs):
        if self.date.month == 1:
            self.date = datetime.date(self.date.year - 1, 12, self.date.day)
        else:
            try: self.date = datetime.date(self.date.year, self.date.month -1, self.date.day)
            except: self.date = datetime.date(self.date.year, self.date.month + 1, self.date.day - 1)
        self.populate_header()
        self.populate_body()

# Корневой класс приложения

class RMApp(App):
    def build(self):
        if platform == "android":
            request_permissions(["com.google.android.gms.permission.AD_ID"])
            temp = SharedStorage().get_cache_dir() # очистка SharedStorage при запуске
            if temp and os.path.exists(temp): shutil.rmtree(temp)

        self.userPath = app_storage_path() if platform == "android" else "" # местоположение рабочей папки программы
        self.dataFile = "data.jsn"
        self.backupFolderLocation = self.userPath + "backup/"
        self.differentFont = "DejaVuSans.ttf" # специальный шрифт для некоторых языков
        self.languages = {
            # список всех установленных языков, очередность должна совпадать с порядком столбцов,
            # key должен совпадать с принятой в Android локалью, value – с msg[1] для всех языков,
            # font - шрифт, которым выводится этот язык
            "en": ["English", None], # key: [value, font]
            "es": ["español", None],
            "ru": ["русский", None],
            "uk": ["українська", None],
            "sr": ["srpski", None],
            "tr": ["Türkçe", None],
            "ka": ["ქართული", self.differentFont],
            "hy": ["Հայերեն", self.differentFont],
        }
        self.interface = AnchorLayout( # форма высшего уровня для ручного поднятия клавиатуры
            anchor_x="center", anchor_y="top")
        self.houses, self.settings, self.resources = self.initializeDB()
        self.load(allowSave=False)
        self.today = time.strftime("%d", time.localtime())
        self.setParameters()
        self.noDataFileActions()
        self.setTheme()
        self.displayed = DisplayedList()
        self.createInterface()
        self.updateTimer()
        self.backupRestore(delete=True, silent=True)
        self.update()
        self.rep.checkNewMonth()
        self.rep.optimizeReportLog()
        Window.bind(on_touch_move=self.window_touch_move)
        Clock.schedule_interval(self.checkDate, 60)
        Clock.schedule_once(self.terPressed, 0)

        self.save(backup=True)
        return self.interface

    def noDataFileActions(self):
        """ Выполнение некоторых действий в зависимости от наличия файла данных """
        if os.path.exists(self.userPath + self.dataFile):
            self.dprint("Поиск файла данных: найден.")
        else:
            self.dprint("Поиск файла данных: НЕ найден.")
            if self.language == "ru": # в русском языке принудительно включаем кнопку «Нет дома»
                self.settings[0][13] = 1
            if not self.desktop and self.resources[0][1][8] == 0: # интересует версия для ПК?
                self.resources[0][1][8] = 1
                def __ask(*args):
                    self.popup(popupForm="windows", message=self.msg[107],
                               options=[self.button["yes"], self.button["no"]])
                Clock.schedule_once(__ask, 60)
            self.save()

    # Подготовка переменных

    def setParameters(self, reload=False):
        # Определение платформы
        self.desktop = True if platform == "win" or platform == "linux" or platform == "macosx" else False
        if Mobmode: self.desktop = False # переопределение через аргумент (для IDE)
        self.platform = platform
        self.DL = None
        if self.settings[0][6] in self.languages.keys():
            self.language = self.settings[0][6]
        else: # определение языка устройства при первом запуске, либо по умолчанию английский
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
                try:    DL = os.environ['LANG'][0:2]
                except: DL = "en"
            else: DL = "en"
            if DL == "ru" or DL == "be" or DL == "kk": self.language = "ru"
            elif DL == "sr" or DL == "bs" or DL == "hr": self.language = "sr"
            elif DL == "es": self.language = "es"
            elif DL == "uk": self.language = "uk"
            elif DL == "ka": self.language = "ka"
            elif DL == "hy": self.language = "hy"
            elif DL == "tr": self.language = "tr"
            else: self.language = "en"
            self.settings[0][6] = self.language
        try:
            with open(f"{self.language}.lang", mode="r", encoding="utf-8") as file: # загрузка языкового файла
                self.msg = file.read().splitlines()
            self.msg.insert(0, "")
        except:
            from tkinter import messagebox
            messagebox.showerror(
                title="Error",
                message="Не найден языковой файл! Переустановите приложение.\n\nLanguage file not found! Please re-install the app.")
            self.stop()

        Clock.unschedule(self.updateTimer)
        self.updater = Clock.schedule_interval(self.updateTimer, 1) if self.settings[0][22] else None
        self.col = ":" if self.language != "hy" else "." # для армянского языка меняем двоеточие на точку
        self.bigLanguage = True if self.language == "hy" or self.language == "ka" else False
        self.textContextMenuSize = ('150sp', '60sp') if self.language == "en" else ('270sp', '60sp') # размер контекстного меню текста в зависимости от языка
        self.specialFont = self.languages[self.language][1]
        self.openedFile = None # файл данных для открытия с устройства
        self.createFirstHouse = False
        self.deleteOnFloor = False
        self.standardTextHeight = (Window.size[1] * .038 * self.fontScale()) if not self.desktop else 35
        self.standardTextWidth = self.standardTextHeight * 1.3
        self.standardBarWidth = self.standardTextWidth * .6
        self.enlargedTextCo = 1.2 if not self.desktop else 1  # увеличенная текстовая строка на некоторых окнах
        self.ellipsisWidth = .07  # ширина кнопки с тремя точками либо пустого виджета вместо нее, справа и слева
        self.orientationPrev = ""
        self.emojiPopup = None # форма для иконок
        self.enterOnButton = None # нужно для правильного выхода из настроек контакта/квартиры
        self.analyticsMessageCached = None # кэш текста с вычислениями служебного года
        self.invisiblePorchName = "1-segment territory" # название сегмента в списочном участке, которое отключает сегменты
        self.listTypePorchName = "1-segment territory list type" # аналогично, но также превращает иконку участка в список
        self.FCP = PopupNoAnimation(title="") # попап первого посещения
        self.floatButtonAlpha = .8  # прозрачность висячих кнопок
        self.horizontalOffset = 80 # ширина левой боковой полосы на горизонтальной ориентации на компьютере
        self.titleSizeHintY = .11  # ширина полосы заголовка
        self.tableSizeHintY = .09  # ширина полосы верхних табличных кнопок
        self.bottomButtonsSizeHintY = .095  # .12 # ширина полосы центральной кнопки
        self.mainButtonsSizeHintY = .09  # ширина полосы 3 главных кнопок
        self.descrColWidth = .38  # ширина левого столбца таблицы (подписи полей), но кроме настроек
        if self.settings[0][21] != "Google" and self.settings[0][21] != "Yandex" and self.settings[0][21] != "Яндекс"\
                and self.settings[0][21] != "2GIS" and self.settings[0][21] != "2ГИС":
            self.settings[0][21] = self.msg[316]
        self.maps = [
            self.msg[316],
            "Google",
            "Яндекс" if self.language == "ru" or self.language == "uk" else "Yandex",
            "2ГИС" if self.language == "ru" or self.language == "uk" else "2GIS"
        ]

        if not reload:  # при мягкой перезагрузке все, что ниже, не перезагружается (сохраняется)
            self.contactsEntryPoint = self.searchEntryPoint = self.popupEntryPoint = 0 # вход в разные списки
            self.stack = []
            self.restore = 0
            self.blockFirstCall = 0
            self.house = self.porch = self.flat = self.record = self.clickedBtnIndex = None
            EventLoop.window.bind(on_keyboard=self.hook_keyboard)
            Window.fullscreen = False # размеры и визуальные элементы
            self.spacing = self.thickness()[0] * 2
            self.padding = self.thickness()[0] * 2.5
            self.serviceTag = ""
            self.repLogCheck = False
            self.charLimit = 30 # лимит символов на кнопках
            self.allowCharWarning = True
            self.dueWarnMessageShow = True
            self.defaultKeyboardHeight = Window.size[1]*.4
            self.popups = []  # стек попапов, которые могут открываться один над другим
            self.сharLimit = int(30 / RM.fontScale()) if not RM.desktop else int(Window.size[0] / 13)
            self.defaultLimit = int(self.сharLimit / RM.fontScale())  # лимит обрезки строк в записях под квартирами
            self.fontXXL =  int(Window.size[1] / 25) # размеры шрифтов
            self.fontXL =   int(Window.size[1] / 30)
            self.fontL =    int(Window.size[1] / 35)
            self.fontM =    int(Window.size[1] / 40)
            self.fontS =    int(Window.size[1] / 45)
            self.fontXS =   int(Window.size[1] / 50)
            self.fontXXS =  int(Window.size[1] / 55)
            self.fontBigEntry = int(Window.size[1] / 41 * self.fontScale())  # шрифт для увеличенных полей ввода
            self.flatSizeInList = self.fontM * .9 * self.fontScale()  # размер шрифта квартир в режиме списка
            self.tablePCFontSize = self.fontM

            if self.platform == "macosx" or Devmode or Mobmode:
                # В режиме разработчика задаем размер окна принудительно (а также на Mac OS при первом запуске,
                # где горизонтальная ориентация не оптимизирована)
                k = .38
                Window.size = (1120 * k, 2340 * k)
                Window.top = 80
                Window.left = 600

            # Действия в зависимости от платформы

            if self.desktop:
                from kivy.config import Config
                Config.set('input', 'mouse', 'mouse, disable_multitouch')
                Config.write()
                self.title = 'Rocket Ministry'
                Window.icon = "icon.png"
                self.icon = "icon.png"
                if not Devmode and self.settings[0][12]:
                    try: # сначала смотрим положение и размер окна в файле win.ini, если он есть
                        with open("win.ini", mode="r") as file: lines = file.readlines()
                        Window.size = ( int(lines[0]), int(lines[1]) ) # (800, 600)
                        if platform != "linux": # на Линуксе окно все время сдвигается вниз, поэтому пока позиционирование отключено
                            Window.top = int(lines[2])
                            Window.left = int(lines[3])
                    except: pass
                def __dropFile(*args):
                    self.importDB(file=args[1].decode())
                Window.bind(on_drop_file=__dropFile)
                def __close(*args):
                    self.cacheFreeModeGridPosition()
                    self.save(export=True)
                    self.dprint("Выход из программы.")
                    self.checkOrientation(width=args[0].size[0], height=args[0].size[1])
                Window.bind(on_request_close=__close, on_resize=self.checkOrientation)
            elif platform == "android":#else:
                try: plyer.orientation.set_portrait()
                except: pass

        self.standardTextHeightUncorrected = (Window.size[1] * .038) if not self.desktop else 30
        self.floorLabelWidth = self.standardTextHeightUncorrected / 2
        self.rep = Report()  # инициализация отчета

        if os.path.exists("icomoon_updated.ttf"): # шрифты с иконками
            if os.path.exists("icomoon.ttf"): os.remove("icomoon.ttf")
            os.rename("icomoon_updated.ttf", "icomoon.ttf") # если было обновление, сначала заменяем файл
            self.dprint("Найден и переименован загруженный файл icomoon.ttf.")

        register('default_font', 'icomoon.ttf', 'icomoon.fontd')

    # Первичное создание интерфейса

    def setTheme(self):
        """ Назначение темы и цветов """
        self.themes = {
            "3D":           "3D",
            self.msg[300]:  "dark",
            self.msg[301]:  "gray",
            self.msg[302]:  "morning",
            self.msg[303]:  "green",
            self.msg[304]:  "teal",
            self.msg[305]:  "purple",
            self.msg[306]:  "sepia"
        }

        self.theme = self.settings[0][5] if isinstance(self.settings[0][5], str) else "sepia"

        if self.settings[0][5] == "":  # тема не указана - выставляем с нуля
            if platform == "android":
                from kvdroid.tools.darkmode import dark_mode
                if dark_mode(): self.theme = self.settings[0][5] = "gray"
                else: self.theme = self.settings[0][5] = "sepia"
            else: self.theme = self.settings[0][5] = "sepia"

        if not Devmode and self.desktop:  # пытаемся получить тему из файла на ПК
            self.themeOld = self.theme
            try:
                with open("theme.ini", mode="r") as file: self.theme = file.readlines()[0]
            except:
                self.dprint("Не удалось прочитать файл theme.ini.")
                self.themeOverriden = False
            else:
                self.dprint("Тема переопределена из файла theme.ini.")
                self.themeOverriden = True
        else: self.themeOverriden = False

        ck = .9 # коэффициент блеклости иконки на пункте списка
        k = .82

        # Светлые темы
        self.mode = "light"
        self.globalBGColor = [.95, .95, .95, 0]
        self.linkColor = self.wiredButtonColor = self.timerOffColor = [.15, .33, .45, 1]
        self.pageTitleColor = [.19, .63, .52, 1]
        self.titleColor = self.mainMenuActivated = [0, .5,  .8,  1]
        self.topButtonColor = [.73, .73, .73, 1]  # поиск, настройки и кнопки счетчиков
        self.topButtonColorDarkened = [.65, .65, .65, 1]  # более темная версия
        self.standardTextColor = [.2, .2, .2]
        self.activatedColor = [0, .15, .35, .9]
        self.buttonBackgroundColor = [.88, .88, .88, 1]
        self.sortButtonBackgroundColor = [.9, .9, .9, .95]
        self.scrollButtonBackgroundColor = [1, 1, 1, 1]
        self.roundButtonColorPressed = [self.scrollButtonBackgroundColor[0] * k, self.scrollButtonBackgroundColor[1] * k,
                                        self.scrollButtonBackgroundColor[2] * k, 1]
        self.lightGrayFlat = [.6, .6, .6, 1]  # квартира без посещения
        self.darkGrayFlat = [.38, .38, .38, 1]  # квартира "нет дома"
        self.floatButtonBGColor = [.85, .85, .85, self.floatButtonAlpha]
        self.recordGray = get_hex_from_color(self.topButtonColor)
        self.sortButtonBackgroundColorPressed = self.roundButtonColorPressed
        self.interestColor = get_hex_from_color(self.getColorForStatus("1"))  # должен соответствовать зеленому статусу или чуть светлее
        self.saveColor = "008E85"
        self.popupButtonColor = [.9, .9, .9, 1]
        self.popupBackgroundColor = [.16, .16, .16, 1]
        self.popupBGColorPressed = [1, 1, 1, .05]
        self.disabledColor = get_hex_from_color(self.topButtonColor)
        self.roundButtonBGColor = [1, 1, 1, 0]
        self.mainMenuButtonBackgroundColor = [.95,.95,.95,.25]
        self.mainMenuButtonColor = [.51, .5, .5]
        self.tabColors = [self.linkColor, "tab_background_default.png"]

        if self.theme == "sepia":  # Сепия
            self.scrollIconColor = [self.titleColor[0] * ck, self.titleColor[1] * ck, self.titleColor[2] * ck, .7]
            self.standardTextColor = [.22, .2, .19]
            self.topButtonColor[0] += 0.01
            self.topButtonColor[2] -= 0.01
            self.floatButtonBGColor[0] += 0.01
            self.floatButtonBGColor[2] -= 0.01
            self.disabledColor = get_hex_from_color(self.topButtonColor)
            self.buttonBackgroundColor[0]   += 0.01
            self.buttonBackgroundColor[2]   -= 0.01
            self.roundButtonColorPressed[0] += 0.02
            self.roundButtonColorPressed[2] -= 0.02
            self.sortButtonBackgroundColor[0] += 0.01
            self.sortButtonBackgroundColor[2] -= 0.01

        elif self.theme == "purple":  # Пурпур
            self.globalBGColor = [.94, .94, .94, 0]
            self.mainMenuButtonColor = [.31, .31, .31, 1]
            self.mainMenuButtonBackgroundColor = [0.55, 0.55, 0.55, .25]
            self.roundButtonColorPressed[1] -= 0.02
            self.roundButtonColorPressed[2] += 0.02
            self.roundButtonColorPressed1 = self.roundButtonColorPressed + [0]
            self.roundButtonColorPressed2 = self.roundButtonColorPressed + [1]
            self.scrollIconColor = [.2, .45, .71, .8]  # дублирование цвета светлой темы JWL
            self.mainMenuActivated = self.titleColor = [.36, .24, .53, 1]
            self.pageTitleColor = [.5, .38, .67, 1]
            self.lightGrayFlat = [.6, .6, .6, 1]
            self.darkGrayFlat = [.43, .43, .43, 1]
            self.tabColors = [self.linkColor, "tab_background_purple.png"]

        elif self.theme == "teal":  # Бирюза
            self.globalBGColor = [.94, .95, .96, 0]
            self.scrollIconColor = [self.titleColor[0] * ck, self.titleColor[1] * ck, self.titleColor[2] * ck, .7]
            self.mainMenuActivated = self.titleColor
            self.pageTitleColor = [0, .6, .73, 1]
            self.mainMenuButtonColor = [.43, .48, .51, 1]
            self.mainMenuButtonBackgroundColor = [.65, .75, .85, .25]
            self.roundButtonColorPressed[0] -= 0.04
            self.roundButtonColorPressed[2] += 0.04

        elif self.theme == "green":  # Эко
            self.titleColor = self.pageTitleColor = self.mainMenuActivated = [.09, .65, .58, 1]
            self.scrollIconColor = [self.titleColor[0] * ck, self.titleColor[1] * ck, self.titleColor[2] * ck, .7]
            self.timerOffColor = [.1, .3, .3, .8]
            self.mainMenuButtonColor = [.48, .5, .48, 1]
            self.roundButtonColorPressed[0] -= 0.03
            self.roundButtonColorPressed[1] += 0.02
            self.roundButtonColorPressed[2] += 0.01
            self.saveColor = get_hex_from_color(self.titleColor)
            self.tabColors = [self.linkColor, "tab_background_green.png"]

        else:  # Темные темы
            self.mode = "dark"
            self.globalBGColor = [0, 0, 0, 0]
            self.mainMenuButtonBackgroundColor = [0, 0, 0, .25]
            self.scrollButtonBackgroundColor = [.14, .14, .14, 1]
            self.buttonBackgroundColor = [.15, .15, .15, 1]
            self.roundButtonColorPressed = self.sortButtonBackgroundColorPressed = [.2, .2, .22, 1]
            self.roundButtonColorPressed2 = [.97, .97, 1, .2]
            self.sortButtonBackgroundColor = [.18, .18, .18, .95]
            self.lightGrayFlat = [.53, .53, .53, 1]
            self.darkGrayFlat = [.31, .31, .31, 1]
            self.floatButtonBGColor = copy(self.sortButtonBackgroundColor)
            self.mainMenuButtonColor = self.timerOffColor = self.topButtonColor
            self.standardTextColor = [.9, .9, .9, 1]
            self.popupButtonColor = [.25, .25, .25, 1]
            self.pageTitleColor = self.titleColor = self.mainMenuActivated = [.3, .87, 1, 1]
            self.scrollIconColor = [.93, .93, .88, .85]
            self.linkColor = [.85, .95, .96, 1]
            self.wiredButtonColor = self.topButtonColor
            self.recordGray = get_hex_from_color(self.standardTextColor)
            self.interestColor = get_hex_from_color(self.getColorForStatus("1"))
            self.saveColor = "00E7C8"
            self.disabledColor = "4C4C4C"
            self.tabColors = [self.linkColor, "tab_background_night.png"]

            if self.theme == "morning":  # Утро
                self.globalBGColor = [.07, .07, .07, 0]
                self.linkColor = [.96, .96, .96, 1]
                self.scrollButtonBackgroundColor = [.16, .16, .16, 1]
                self.sortButtonBackgroundColor = [.21, .21, .21, .95]
                self.mainMenuButtonBackgroundColor = [.2, .2, .2, .6]
                self.roundButtonColorPressed1 = self.roundButtonColorPressed + [0]
                self.roundButtonColorPressed2 = [1, 1, 1, .25]
                self.mainMenuActivated = self.titleColor = [.76, .65, .89, 1]
                self.pageTitleColor = [.4, .8, .67, 1]
                self.scrollIconColor = [.62, .73, .89, 1]  # дублирование цвета темной темы JWL
                self.tabColors = [self.linkColor, "tab_background_purple_light.png"]

            elif self.theme == "gray":  # Вечер
                self.globalBGColor = [.08, .08, .08, 0]
                self.darkGrayFlat = [.4, .4, .4, 1]
                self.scrollButtonBackgroundColor = [.16, .16, .16, 1]
                self.sortButtonBackgroundColor = [.2, .21, .22, .95]
                self.buttonBackgroundColor = [.05, .2, .35, 1]#[.01, .27, .44, 1] red color
                self.roundButtonColorPressed = [0, .37, .54, 1]
                self.roundButtonColorPressed2 = [.7, .8, .9, .23]
                self.sortButtonBackgroundColorPressed = [.25,.26,.27, 1]
                self.mainMenuButtonBackgroundColor = [.17, .17, .17, .6]
                self.titleColor = self.mainMenuActivated = [.76, .86, .99, 1]
                self.pageTitleColor = [.4, .8, .67, 1]
                self.scrollIconColor = [self.titleColor[0] * ck, self.titleColor[1] * ck, self.titleColor[2] * ck, .85]
                self.saveColor = "00E79E"
                self.disabledColor = get_hex_from_color(self.darkGrayFlat)
                self.linkColor = [.97, .97, .97, 1]
                self.tabColors = [self.linkColor, "tab_background_gray.png"]

            elif self.theme == "3D":  # 3D
                self.globalBGColor = [.15, .15, .15, 1]
                self.titleColor = self.mainMenuActivated = [0, 1, .9, 1]
                self.pageTitleColor = [1, .99, .41, 1]#[0, .95, 1, 1]
                self.scrollIconColor = [self.titleColor[0] * ck, self.titleColor[1] * ck, self.titleColor[2] * ck, .85]
                self.linkColor = self.mainMenuButtonColor = self.timerOffColor = [.97, 1, .97, 1]
                self.mainMenuBGColor = [.5, .5, .5, 1]
                self.scrollButtonBackgroundColor = [1, 1, 1, 1]
                self.sortButtonBackgroundColor = [.2, .2, .2, .95]
                self.sortButtonBackgroundColorPressed = [.4, .42, .42, 1]
                self.roundButtonColorPressed2 = [0, .8, .8, 1]
                self.darkGrayFlat = [.4, .4, .4, 1]
                self.floatButtonBGColor = [.4, .4, .4, self.floatButtonAlpha]
                self.blackTint = [.54, .56, .57]
                self.roundButtonBGColor = [1, 1, 1, 1]
                self.interestColor = get_hex_from_color(self.titleColor)
                self.saveColor = get_hex_from_color(self.titleColor)
                self.disabledColor = get_hex_from_color(self.darkGrayFlat)
                self.tabColors = [self.linkColor, "tab_background_3d.png"]

        self.tableColor = self.tabColors[0] = [self.linkColor[0], self.linkColor[1], self.linkColor[2], .85]
        if self.theme == "purple": self.titleColorOnBlack = [.76, .65, .89]
        elif self.theme == "gray": self.titleColorOnBlack = [.63, .78, .99]
        else: self.titleColorOnBlack = [self.titleColor[0], self.titleColor[1], self.titleColor[2]]
        self.textInputColor = self.standardTextColor
        self.textInputBGColor = 0, 0, 0, 0
        self.timerOffColor[3] = .9
        self.floatButtonBGColor[3] = .78
        Window.clearcolor = self.globalBGColor
        self.mainMenuButtonColor2 = get_hex_from_color(self.mainMenuButtonColor)
        self.titleColor2 = get_hex_from_color(self.titleColor)
        self.RoundButtonColor = get_hex_from_color(self.linkColor)
        self.scrollColor = get_hex_from_color(self.scrollIconColor)
        self.timerTextColorOn = [self.standardTextColor[0], self.standardTextColor[1], self.standardTextColor[2], .9]
        self.textBorderColorActive = self.scrollIconColor
        self.textBorderColorInactive = self.buttonBackgroundColor if self.mode == "light" else self.sortButtonBackgroundColor
        self.color2List = [] # список цветов для вторичного цвета
        for i in range(4): self.color2List.append(self.getColor2(i))

        # Иконки для кнопок

        self.listIconSize = self.fontXL
        self.FCPIconSize = self.fontM
        self.tableIconSize = int(self.fontS * 1.05 * self.fontScale(cap=1.2)) if not self.desktop else int(self.fontL)
        self.tableIconSizeL = int(self.tableIconSize * 1.2)  # вариант чуть побольше
        br = '\n' if self.settings[0][13] else "  "

        self.button = {
            # иконки элементов списка
            "building": f" [size={self.listIconSize}][color={self.scrollColor}]{icon('icon-building')}[/color][/size] ",
            "porch":    f" [size={self.listIconSize}][color={self.scrollColor}]{icon('icon-sign-in')}[/color][/size] ",
            "porch_inv":f" [size={self.listIconSize}][color={get_hex_from_color([0,0,0,0])}]{icon('icon-sign-in')}[/color][/size] ",
            "pin":      f" [size={self.listIconSize}][color={self.scrollColor}]{icon('icon-road')}[/color][/size] ",
            "map":      f" [size={self.listIconSize}][color={self.scrollColor}]{icon('icon-map')}[/color][/size] ",
            "list-ter": f" [size={self.listIconSize}][color={self.scrollColor}]{icon('icon-list-ul')}[/color][/size] ",
            "entry":    f" [size={self.listIconSize}][color={self.scrollColor}]{icon('icon-comments')}[/color][/size] ",
            "plus-1":   f" [size={self.listIconSize}][color={self.scrollColor}]{icon('icon-plus')}[/color][/size]",
            "home":     f" [size={self.listIconSize}][color={self.scrollColor}]{icon('icon-home')}[/color][/size] ",

            # центральная кнопка
            "plus":     f"{icon('icon-plus-circle', size=self.tableIconSize)}",
            "edit":     f"{icon('icon-cog', size=self.tableIconSize)}",
            "search2":  f"{icon('icon-binoculars', size=self.tableIconSize)}",
            "save":     f"[b][color={self.saveColor}]{icon('icon-check-circle', size=self.tableIconSize)} {self.msg[5]}[/color][/b]",

            # плашка первого посещения
            "lock":   f"[size={self.FCPIconSize}]{icon('icon-lock')}[/size]{br}{self.msg[206]}",    # нет дома
            "record": f"[size={self.FCPIconSize}]{icon('icon-pencil')}[/size]{br}{self.msg[163]}",  # запись
            "reject": f"[size={self.FCPIconSize}]{icon('icon-ban')}[/size]{br}{self.msg[207]}",     # отказ

            # иконки для TableButton
            "back":     icon("icon-arrow-left2", size=self.tableIconSize),  # верхние # IcoMoon Free
            "sort":  f"{icon('icon-sort', size=self.tableIconSize)} {self.msg[71]}",
            "user":     icon("icon-user", size=self.tableIconSize),
            "help":     icon("icon-life-bouy", size=self.tableIconSize),
            "log":      icon("icon-history", size=self.tableIconSize),
            "adjust":   icon("icon-adjust1", size=self.tableIconSize),  # нижние # Material Icons
            "resize":   icon("icon-expand", size=self.tableIconSize),
            "flist":    icon("icon-align-justify", size=self.tableIconSize),
            "fgrid":    icon('icon-swipe', size=self.tableIconSize),  # Material Icons
            "phone":    icon('icon-phone', size=self.tableIconSize),
            "phone0":   icon('icon-phone', color=self.disabledColor, size=self.tableIconSize),
            "nav":      icon("icon-map-marker", size=self.tableIconSize),
            "nav0":     icon('icon-map-marker', color=self.disabledColor, size=self.tableIconSize),
            "1":        icon("icon-number1", size=self.tableIconSize),
            "2":        icon("icon-number2", size=self.tableIconSize),
            "3":        icon("icon-number3", size=self.tableIconSize),
            "4":        icon("icon-number4", size=self.tableIconSize),

            # экран данных
            "floppy":   icon("icon-floppy-o", size=self.tableIconSize),
            "open":     icon("icon-folder-open", size=self.tableIconSize),
            "restore":  icon("icon-upload", size=self.tableIconSize),
            "trash":    icon("icon-trash", size=self.tableIconSize),

            "building0":icon("icon-building"),
            "floppy2":  icon("icon-floppy-o"),
            "check":    icon("icon-check"),
            "details":  icon("icon-pencil"),
            "search":   icon("icon-search"),
            "dot":      icon("icon-dot-circle-o"),
            "dot-off":  icon("icon-circle-o"),
            "menu":     icon("icon-bars"),
            "calendar": icon("icon-calendar"),
            "worked":   icon("icon-check"),
            "ellipsis": icon("icon-more_vert"), # Material icons
            "contact":  icon("icon-user"), # отличается от user тем, что не прописан размер
            "phone-square": icon("icon-phone-square"),
            "phone-thin": icon("icon-phone"),
            "shrink":   icon('icon-scissors'),
            "list":     icon("icon-file-text"),
            "bin":   f"{icon('icon-trash')}\n{self.msg[173]}",
            "note":     icon("icon-sticky-note"),
            "header":   icon("icon-sticky-note"), # то же, что note, только для списков
            "chat":     icon("icon-comments"),
            "info":     icon('icon-info-circle'),
            "highlight":icon('icon-info-circle'),
            "share":    icon("icon-share-alt"),
            "export":   icon("icon-cloud-upload"),
            "import":   icon("icon-cloud-download"),
            "arrow":    icon("icon-caret-right"),
            "caret-up": icon("icon-caret-up"),
            "caret-down": icon("icon-caret-down"),
            "chevron-up": icon("icon-chevron-up"),
            "chevron-down": icon("icon-chevron-down"),
            "chevron-left": icon("icon-chevron-left"),
            "chevron-right": icon("icon-chevron-right"),
            "warn":     icon("icon-warning"),
            "male":     icon("icon-male", size=self.tableIconSize),
            "female":   icon("icon-female", size=self.tableIconSize),
            "yes":      self.msg[297].lower(),
            "no":       self.msg[298].lower(),
            "cancel":   self.msg[190].lower(),
            "wait":     icon("icon-spinner3"), # IcoMoon
            "link":    f"[color={self.titleColor2}]{icon('icon-external-link-square')}[/color]",
            "add_emoji":icon("icon-add_photo_alternate"), # Material icons
            "":         ""
        }

        self.emoji = {"check": "\u2611"} # галочка для отчета

        # Иконки и смайлики для квартир. Смайлики - IconMoon, все остальные - Material Icons

        self.icons = [
            icon('icon-grin'),
            icon('icon-smile'),
            icon('icon-cool'),
            icon('icon-tongue'),
            icon('icon-hipster'),
            icon('icon-shocked'),
            icon('icon-wondering'),
            icon('icon-neutral'),
            icon('icon-baffled'),
            icon('icon-sleepy'),
            icon('icon-confused'),
            icon('icon-sad'),
            icon('icon-crying'),
            icon('icon-angry'),
            icon('icon-frustrated'),
            icon('icon-star_outline'),
            icon('icon-star_half'),
            icon('icon-star1'),
            icon('icon-bookmark1'),
            icon('icon-warning1'),
            icon('icon-remove_circle_outline'),
            icon('icon-menu_book'),
            icon('icon-create'),
            icon('icon-message'),
            icon('icon-mark_chat_read'),
            icon('icon-videocam'),
            icon('icon-remove_red_eye'),
            icon('icon-access_time'),
            icon('icon-mail_outline'),
            icon('icon-alternate_email'),
            icon('icon-phone1'),
            icon('icon-phone_locked'),
            icon('icon-phone_disabled'),
            icon('icon-notifications_off'),
            icon('icon-volume_off'),
            icon('icon-location_off'),
            icon('icon-hourglass_disabled'),
            icon('icon-no_cell'),
            icon('icon-check1'),
            icon('icon-clear'),
            icon('icon-pets'),
            icon('icon-format_paint'),
            icon('icon-vpn_key'),
            icon('icon-sensor_door'),
            icon('icon-https'),
            icon('icon-device_thermostat'),
            icon('icon-repeat1'),
            icon('icon-fast_forward'),
            icon('icon-accessible_forward'),
            icon('icon-child_care'),
            icon('icon-child_friendly'),
            icon('icon-flag1'),
            icon('icon-bolt1'),
            icon('icon-send1'),
            icon('icon-directions_car'),
            icon('icon-rocket'),
            icon('icon-person_add_alt_1'),
            icon('icon-medical_services'),
            icon('icon-shield1'),
            icon('icon-favorite'),
            icon('icon-date_range'),
            icon('icon-pending_actions'),
            icon('icon-delete'),
            icon('icon-brightness_low'),
            icon('icon-bedtime'),
            icon('icon-stop_circle'),
            ""
        ]

    def createInterface(self):
        """ Создание основных элементов """
        self.globalFrame = BoxLayout(orientation="vertical")
        self.boxHeader = BoxLayout(spacing=self.spacing, padding=(0, 2))

        self.positive = Button()

        # Таймер

        TimerAndSetSizeHint = .22
        self.timerBox = BoxLayout(size_hint_x=TimerAndSetSizeHint, spacing=self.spacing, padding=(self.padding, 0))
        self.timer = Timer()
        self.timerBox.add_widget(self.timer)
        self.timerText = Label(halign="left", valign="center", pos_hint={"center_y": .5}, markup=True,
                               color=self.timerTextColorOn, width=self.standardTextWidth)
        if not self.desktop: self.timerText.font_size = self.fontXS * self.fontScale()
        def __click(instance, value):
            if value == "timerPress": self.timerPressed()
        self.timerText.bind(on_ref_press=__click)
        self.timerBox.add_widget(self.timerText)

        # Заголовок таблицы

        self.headBox = BoxLayout(size_hint_x=1-TimerAndSetSizeHint*2, spacing=self.spacing)
        self.pageTitle = TitleLabel()
        self.pageTitle.bind(on_ref_press=self.titlePressed)
        self.headBox.add_widget(self.pageTitle)

        # Поиск и настройки

        self.setBox = BoxLayout(size_hint_x=TimerAndSetSizeHint, spacing=self.spacing, padding=(self.padding, 0))
        self.searchButton = TopButton(text=self.button["search"], size_hint_x=.1)
        self.searchButton.bind(on_release=self.searchPressed)
        self.settingsButton = TopButton(text=self.button["menu"], size_hint_x=.1)
        self.settingsButton.bind(on_release=self.settingsPressed)

        if self.settings[0][22]: # если есть таймер
            self.boxHeader.add_widget(self.timerBox)
            self.setBox.add_widget(self.searchButton)
            self.setBox.add_widget(self.settingsButton)
            self.boxHeader.add_widget(self.headBox)
            self.boxHeader.add_widget(self.setBox)
        else:
            self.boxHeader.add_widget(self.settingsButton)
            self.boxHeader.add_widget(self.headBox)
            self.boxHeader.add_widget(self.searchButton)

        self.globalFrame.add_widget(self.boxHeader)

        self.boxCenter = BoxLayout()
        self.mainBox = BoxLayout()
        self.boxCenter.add_widget(self.mainBox)
        self.listarea = BoxLayout(orientation="vertical")
        self.mainBox.add_widget(self.listarea)

        # Верхние кнопки таблицы

        self.titleBox = BoxLayout(size_hint_y=self.tableSizeHintY, padding=(self.padding, self.padding*2),
                                  spacing=self.spacing)
        self.listarea.add_widget(self.titleBox)
        self.tbWidth = [.25, .5, .25] # значения ширины кнопок таблицы
        if self.theme != "3D": self.backButton = TableButton(text=self.button["back"], disabled=True)

        else: self.backButton = RetroButton(text=self.button["back"], disabled=True)
        self.backButton.bind(on_release=self.backPressed)
        self.titleBox.add_widget(self.backButton)

        self.dropSortMenu = DropDown()
        if self.theme != "3D": self.sortButton = TableButton(disabled=True)
        else: self.sortButton = RetroButton(disabled=True)
        self.titleBox.add_widget(self.sortButton)
        self.sortButton.bind(on_press=self.sortPressed)

        if self.theme != "3D": self.detailsButton = TableButton(disabled=True)
        else: self.detailsButton = RetroButton(disabled=True)

        self.detailsButton.bind(on_release=self.detailsPressed)
        self.titleBox.add_widget(self.detailsButton)

        self.backButton.size_hint_x = self.tbWidth[0]
        self.sortButton.size_hint_x = self.tbWidth[1]
        self.detailsButton.size_hint_x = self.tbWidth[2]

        # Главный список

        self.mainList = BoxLayout(orientation="vertical", spacing=self.spacing)
        AL = AnchorLayout(anchor_x="center", anchor_y="top")
        AL.add_widget(self.mainList)
        self.listarea.add_widget(AL)

        self.floatView = RelativeLayout() # дополнительный контейнер для сетки подъезда

        # Нижние кнопки таблицы

        self.bottomButtons = BoxLayout(size_hint_y=self.bottomButtonsSizeHintY,
                                       spacing=self.spacing*3, padding=self.padding*2)
        if self.theme != "3D": self.navButton = TableButton(disabled=True, size_hint_x=.2)
        else: self.navButton = RetroButton(disabled=True, size_hint_x=.2)
        self.bottomButtons.add_widget(self.navButton)
        self.navButton.bind(on_release=self.navPressed)

        self.positive = RoundButton(rounded=True) if self.theme != "3D" else RetroButton()
        self.positive.bind(on_release=self.positivePressed)
        self.bottomButtons.add_widget(self.positive)

        if self.theme != "3D": self.neutral = TableButton(disabled=True, size_hint_x=.2)
        else: self.neutral = RetroButton(disabled=True, size_hint_x=.2)

        self.neutral.bind(on_release=self.neutralPressed)
        self.bottomButtons.add_widget(self.neutral)

        self.floaterBox = FloatLayout(size_hint=(0, 0)) # контейнер для парящих кнопок на некоторых формах
        self.boxCenter.add_widget(self.floaterBox)

        self.globalFrame.add_widget(self.boxCenter)

        if not self.desktop:
            self.interface.add_widget(self.globalFrame)
        else: # в настольном режиме создаем дополнительные фреймы, чтобы отобразить главные кнопки сбоку
            self.desktopModeFrame = AnchorLayout(anchor_x="center", anchor_y="center")
            self.horizontalGrid = GridLayout(rows=1, cols=2)
            self.horizontalGrid.add_widget(self.desktopModeFrame)
            self.horizontalGrid.add_widget(self.globalFrame)
            self.interface.add_widget(self.horizontalGrid)

        Clock.schedule_once(self.checkOrientation, 0)

    # Основные действия с центральным списком

    def updateList(self, instance, progress=False):
        """ Заполнение главного списка элементами """
        form = self.displayed.form

        def __continue(*args):
            tableButtonClicked = True if "TableButton" in str(instance) or "RetroButton" in str(instance) else False
            self.stack = list(dict.fromkeys(self.stack))
            self.mainList.clear_widgets()
            self.mainList.padding = 0
            self.popupEntryPoint = 0
            self.firstCallPopup = False
            self.sortButton.disabled = True
            self.allowDelayOnUpdateList = True

            # Считываем содержимое Feed/displayed

            self.pageTitle.text = f"[ref=title]{self.displayed.title}[/ref]" if "View" in form \
                else self.displayed.title

            if self.displayed.positive != "":
                if form != "repLog": self.restorePositiveButton()
                self.positive.disabled = False
                self.positive.text = self.displayed.positive
                self.positive.color = self.linkColor
            else:
                self.positive.text = ""
                self.positive.disabled = True

            if self.displayed.neutral != "":
                self.neutral.disabled = False
                self.neutral.text = self.displayed.neutral
            else:
                self.neutral.text = ""
                self.neutral.disabled = True
            if self.neutral.text == self.button['phone'] and self.flat.phone == "":
                self.neutral.text = self.button['phone0']
                self.neutral.disabled = True

            if self.displayed.sort is not None:
                self.sortButton.disabled = False
                self.sortButton.text = self.displayed.sort
            else:
                self.sortButton.text = ""
                self.sortButton.disabled = True

            if self.displayed.details is not None:
                self.detailsButton.disabled = False
                self.detailsButton.text = self.displayed.details
            else:
                self.detailsButton.text = ""
                self.detailsButton.disabled = True

            if self.displayed.nav == self.button["nav0"]:
                self.navButton.disabled = True
                self.navButton.text = self.displayed.nav
            elif self.displayed.nav is not None:
                self.navButton.disabled = False
                self.navButton.text = self.displayed.nav
            else:
                self.navButton.text = ""
                self.navButton.disabled = True

            self.backButton.disabled = True if not self.displayed.back else False

            allowMainList = True

            if self.displayed.tip is not None:
                if len(self.displayed.tip) == 2:
                    if self.displayed.tip[0] is not None:
                        self.mainList.add_widget(
                            self.tip(text=self.displayed.tip[0], icon=self.displayed.tip[1], hint_y=1)
                        )
                    if self.displayed.tip[1] == "header":
                        self.mainList.padding = 0, self.padding*2, 0, 0
                else:
                    self.mainList.add_widget(self.tip(self.displayed.tip))
                    allowMainList = False

            # Настройки списка (кроме подъезда в сетке)

            self.btn = []  # массив кнопок для списка
            self.height1 = self.standardTextHeight * 2 / self.fontScale()  # высота кнопки списка
            self.scrollWidget = MainScroll()
            self.scrollWidget.bind(minimum_height=self.scrollWidget.setter('height'))
            self.scroll = ScrollView(size=self.mainList.size, scroll_type=['content'])
            rad = self.getRadius(90)[0]  # радиус закругления подсветки списка в участках и контактах
            if self.desktop:
                self.height1 = self.height1 * (.8 if form == "ter" or form == "con" else .6)

            if self.createFirstHouse: # запись "создайте дом(а)" для пустого сегмента
                self.createFirstHouse = False
                self.floaterBox.clear_widgets()
                box1 = BoxLayout(orientation="vertical", size_hint_y=None, height=self.height1*1.05)
                self.scrollRadius = [rad,]
                box1.add_widget(ScrollButton(
                    id=None, height=box1.height,
                    text=f"{RM.button['plus-1']}{RM.button['home']} {RM.msg[12]}"))
                self.scroll.add_widget(self.scrollWidget)
                self.scrollWidget.add_widget(box1)
                self.mainList.add_widget(self.scroll)

            # Вид подъезда с этажами (сеткой)

            elif form == "porchView" and self.porch.floors():
                self.floatView.clear_widgets()
                self.screenRatio = self.mainList.size[1] / self.mainList.size[0] # соотношение сторон mainList
                self.flatSizeRatio = RM.porch.rows/RM.porch.columns
                if self.porch.columns >= 15 or self.porch.rows >= 30:
                    rad = 9999
                    self.flatSizeInGrid = self.fontXXS * self.fontScale(cap=1.2)
                elif self.porch.columns >= 10 or self.porch.rows >= 20:
                    rad = 250
                    self.flatSizeInGrid = self.fontXS * self.fontScale(cap=1.2)
                else:
                    rad = 150
                    self.flatSizeInGrid = self.fontS * self.fontScale(cap=1.2)

                self.flatButtonRadius = \
                    [0 if self.theme == "3D" else (Window.size[0] * Window.size[1]) / (Window.size[0] * rad), ]
                floorFontSize = self.fontS * (1 if self.desktop else .8) * self.fontScale(cap=1.4)
                if self.porch.floorview is None: # первичная генерация сетки
                    self.porch.floorview = FloorView(porch=self.porch, instance=instance)
                    for flat in self.displayed.options:
                        if "object" in str(flat): # показ квартиры
                            self.porch.floorview.add_widget(FlatButtonSquare(flat))
                        else: # показ цифры этажа
                            self.porch.floorview.add_widget(FloorLabel(flat=flat, width=self.floorLabelWidth,
                                                                       font_size=floorFontSize))
                else: # только обновление
                    self.porch.floorview.__init__(porch=self.porch, instance=instance)
                    if not tableButtonClicked and self.flat is not None:
                        self.flat.buttonID.update(self.flat) # перерисовка одной квартиры
                    else:
                        for b in self.porch.floorview.children:
                            if "FlatButtonSquare" in str(b): b.update(flat=b.flat) # ... или всего подъезда
                            else:
                                b.size_hint_x = 1
                                b.font_size = floorFontSize
                                b.width = self.floorLabelWidth

                if self.porch.pos[0]: # монтаж - свободный режим
                    self.mainList.add_widget(self.floatView)
                    self.floatView.add_widget(self.porch.floorview)

                else: # ... заполняющий режим
                    self.mainList.add_widget(self.porch.floorview)

                    self.porch.floorview.row_force_default = False
                    self.porch.floorview.col_force_default = False
                    self.porch.floorview.col_default_width = 0
                    self.porch.floorview.row_default_height = 0
                    self.porch.floorview.padding = self.padding, 0, self.padding*2, 0
                    self.neutral.text = self.button["resize"]
                    for widget in self.porch.floorview.children:
                        if "app.FloorLabel" in str(widget):
                            widget.size_hint_x = None
                            widget.font_size = floorFontSize * 1.1
                            widget.width = self.floorLabelWidth * 1.1 * self.fontScale(cap=1.2)

                self.floaterBox.clear_widgets()
                self.window_touch_move(tip=False)

            # Все списки

            else:
                self.scrollRadius = [rad, ]
                valign = "center"
                if form == "ter": self.scrollRadius = [rad, ] if len(self.houses) == 0 else [rad, rad, 0, 0]
                elif form == "con": self.scrollRadius = [rad, rad, 0, 0]
                elif form == "houseView":
                    due = self.house.due()
                    self.scrollRadius = [rad, ]
                    if due and self.dueWarnMessageShow:
                        self.mainList.add_widget(self.tip(icon="warn"))
                elif form == "porchView":
                    self.height1 *= .9 # высота списка квартир чуть меньше обычного
                    if self.invisiblePorchName in self.porch.title and due and self.dueWarnMessageShow:
                        if due and self.dueWarnMessageShow:
                            self.mainList.add_widget(self.tip(icon="warn"))
                elif form == "repLog":
                    #self.scrollRadius = [rad, rad, 0, 0]
                    self.height1 *= (1.1 * self.fontScale())
                    valign = "top"
                height = self.height1

                self.flatButtonRadius = \
                    [0 if self.theme == "3D" else (Window.size[0] * Window.size[1]) / (Window.size[0] * 170), ]
                if form != "porchView" or self.porch.scrollview is None:
                    for i in range(len(self.displayed.options)):
                        label = self.displayed.options[i]
                        if form == "porchView": flat = label

                        # Добавление пункта списка

                        if (form == "ter" and len(self.houses)>0) or form == "con" \
                                or form == "houseView":#or form == "repLog":
                            addEllipsis = True # флаг, что нужно добавить три точки настроек
                            box = GridLayout(rows=2, cols=3, height=height, size_hint_y=None)
                            sideMargin = .03
                            box.add_widget(Widget(size_hint=(sideMargin, 0)))
                        else:
                            addEllipsis = False
                            box = BoxLayout(orientation="vertical", height=height, size_hint_y=None)

                        if form != "porchView":
                            # вид для всех списков, кроме подъезда - без фона (а также кнопки "Создайте дом")

                            if form == "repLog": # форматирование элементов и обработка фильтра по галочке
                                if not self.repLogCheck or self.getLog(i)[2] != "":
                                    color1 = get_hex_from_color(self.lightGrayFlat)
                                    color2 = get_hex_from_color(self.standardTextColor)
                                    color3 = self.RoundButtonColor if self.mode == "light" else self.titleColor2
                                    time, body, tag = self.getLog(i)
                                    div1 = "  " if body != "" else ""
                                    if tag != "": # подпись есть
                                        tag2 = f"[color={color3}][b]{tag}[/b][/color]"
                                        div2 = "  "
                                    else:
                                        tag2 = ""
                                        div2 = ""
                                    font = self.fontXS if self.desktop else int(self.fontXXS * self.fontScale(cap=1.2))
                                    label = f"[color={color1}][size={font}]{time}[/size][/color]{div1}[color={color2}]{body}[/color]{div2}{tag2}"  # подпись
                                else:
                                    label = ""

                            if label != "": self.btn.append(ScrollButton(id=i, text=label, height=height))

                        else: # вид для списка подъезда - с фоном и закругленными квадратиками
                            if not "." in flat.number or self.house.type == "private":
                                self.btn.append(FlatButton(id=i, height=height, recBox=box, flat=flat,
                                                           size_hint_y=None))
                            else:
                                self.btn.append(EmptyButton(height=0))
                                continue

                        if label != "":
                            last = len(self.btn) - 1  # адресация кнопки, которая обрабатывается в данный момент
                            button = self.btn[last]
                            box.add_widget(button)

                        if addEllipsis: # добавляем три точки (или пустое место - определяется через id)
                            box.add_widget(SettingsButton(
                                id=None if self.msg[6] in label or self.msg[213] in label else i))
                            self.scrollWidget.padding = RM.padding * 2, RM.padding * 2,\
                                                        0 if self.desktop else 1, RM.padding * 2
                            box.add_widget(Widget(size_hint=(0, 0)))

                        if self.displayed.footer != []: # индикаторы-футеры, если они есть
                            footer = self.displayed.footer
                            self.scrollWidget.spacing = self.spacing * 8
                            box.height = height * 1.32
                            footerGrid = GridLayout(rows=1, cols=len(footer[i]), size_hint_y=None,
                                                    pos_hint={"center_x": .5}, size_hint_x=.96, height=height*.36)
                            if label != "":
                                if form == "con":# or form == "repLog":
                                    footerGrid.cols_minimum = {1: button.size[0] * .7}
                                elif form == "ter":
                                    footerGrid.cols_minimum = { # поджимаем футеры справа и слева
                                        0: button.size[0] * .1,
                                        1: button.size[0] * .2,
                                        2: button.size[0] * .2,
                                        3: button.size[0] * .2,
                                        4: button.size[0] * .2,
                                        5: button.size[0] * .1
                                    }
                                count = 0
                                for b in range(len(footer[i])):
                                    if form == "ter" and self.fontScale() <= 1: limit = 5
                                    elif form == "ter": limit = 3
                                    else: limit = len(footer[i])-1
                                    if count == 0: self.footerRadius = [0, 0, 0, rad * 1.1]
                                    elif count < limit: self.footerRadius = [0, ]
                                    else: self.footerRadius = [0, 0, rad * 1.1, 0]
                                    button.footers.append(FooterButton(text=str(footer[i][b]), parentIndex=i))
                                    count += 1
                                    footerGrid.add_widget(button.footers[len(button.footers)-1])
                                box.add_widget(footerGrid)

                        elif form == "flatView" and len(self.flat.records) > 0: # запись посещения
                            box.add_widget(RecordButton(text=label[label.index("|")+1:].replace("\n", " "), id=i))
                            button.text = button.text[: button.text.index("|")]
                            button.valign = "center"
                            button.size_hint_y = None
                            button.height = height * 1.05
                            min = button.height + self.standardTextHeight * 1.6
                            max = button.height + self.standardTextHeight * (4 if self.orientation == "v" else 5)
                            box.height = max if i == 0 else min
                            box.spacing = self.spacing

                        if label != "": self.scrollWidget.add_widget(box)

                    for step in range(4 if form == "porchView" else 1):
                        self.btn.append(EmptyButton(height))
                        self.scrollWidget.add_widget(self.btn[len(self.btn) - 1])

                if allowMainList: # главный список не монтируется при некоторых видах примечаний (note)
                    if form != "porchView":
                        self.scroll.add_widget(self.scrollWidget)
                        self.mainList.add_widget(self.scroll)
                    else:
                        if self.porch.scrollview is None:
                            self.scroll.add_widget(self.scrollWidget)
                            self.porch.scrollview = self.scroll
                            self.porch.btn = self.btn
                            self.flat = None
                            self.updateList(instance=instance) # повторный вызов, где список уже на scrollview, дальше манипуляции там
                            return
                        else:
                            grid = self.porch.scrollview.children[0]  # адресация таблицы, уже замонтированной на porch
                            if form == "repLog": grid.cols = 1
                            elif self.orientation == "h" and form != "porchView": grid.cols = 2
                            else: grid.cols = self.settings[0][10]
                            self.mainList.add_widget(self.porch.scrollview)
                            if (not tableButtonClicked and self.flat is not None and self.flat.buttonID is not None \
                                    and self.porch.flatsLayout != "с" and self.porch.flatsLayout != "с2"
                                    and self.porch.flatsLayout != "т" and self.porch.flatsLayout != "д"
                                    and self.porch.flatsLayout != "з" and self.porch.flatsLayout != "и"):
                                # при возврате из квартиры перерисовываем только квартиру, но если позволяет сортировка
                                self.flat.buttonID.update(self.flat)
                            else:
                                for b in grid.children: # перерисовка всего списка в остальных случаях
                                    for widget in b.children:
                                        if "FlatButton" in str(widget):
                                            widget.update(flat=widget.flat)
                                            break

                if form != "porchView" or self.porch.scrollview is not None:

                    self.floaterBox.clear_widgets()  # очистка плавающих элементов

                    if form == "ter" or form == "con" or form == "flatView": # лимиты для прокрутки
                        self.listLimit = 7
                    elif form == "porchView":
                        self.listLimit = 10 * self.settings[0][10]
                        self.btn = self.porch.btn
                        self.scroll = self.porch.scrollview
                    else:
                        self.listLimit = 8

                    if form == "repLog":
                        footer = BoxLayout(size_hint_y=None, # галочка для подписей
                                           height=self.standardTextHeight * 1.5)
                        check = FontCheckBox(text=self.msg[335], active=self.repLogCheck)
                        footer.add_widget(check)
                        self.mainList.add_widget(footer)
                        self.mainList.add_widget(self.bottomButtons) # создание новой записи
                        self.positive.text = f"{self.button['plus']} {self.msg[331]}"
                        self.positive.disabled = False
                        self.bottomButtons.size_hint_y = self.bottomButtonsSizeHintY * \
                                                         (1.1 if self.orientation == "v" else 1.38)

                    # прокручиваем до выбранного элемента, если получается
                    if self.displayed.jump is not None and self.displayed.jump < len(self.btn)\
                            and len(self.btn) > self.listLimit:
                        self.scroll.scroll_to(widget=self.btn[self.displayed.jump],
                                              padding=self.mainList.size[1] * .3, animate=False)

                    if form != "ter" and form != "con" and form != "houseView":
                        self.scroll.scroll_type = ['bars', 'content']
                        self.scroll.bar_width = self.standardBarWidth

                        if len(self.btn) > self.listLimit:  # кнопки прокрутки списка вниз и вверх
                            btnSize = self.standardTextHeightUncorrected * 1.7, self.standardTextHeightUncorrected * 1.7
                            fBox = BoxLayout(orientation="vertical", spacing=self.spacing if self.theme != "3D" else 0,
                                             size_hint=(None, None), pos=[Window.size[0] - btnSize[0] - self.padding,
                                                                          self.mainList.size[1]*.32])
                            if self.theme != "3D":
                                scrollselfUp = FloatButton(text=self.button["chevron-up"], size=btnSize)
                                scrollselfDown = FloatButton(text=self.button["chevron-down"], size=btnSize)
                            else:
                                scrollselfUp = RetroButton(text=self.button["chevron-up"], width=btnSize[0],
                                                           height=btnSize[1], alpha=self.floatButtonAlpha,
                                                           size_hint_x=None, size_hint_y=None, halign="center",
                                                           valign="center")
                                scrollselfDown = RetroButton(text=self.button["chevron-down"], width=btnSize[0],
                                                             height=btnSize[1], alpha=self.floatButtonAlpha,
                                                             size_hint_x=None, size_hint_y=None, halign="center",
                                                             valign="center")
                            def __scrollClick(instance):
                                if self.button["chevron-down"] in instance.text:
                                    self.scroll.scroll_to(self.btn[len(self.btn)-1])
                                else:
                                    def __getTopButton():
                                        for bt in self.btn:
                                            if not "EmptyButton" in str(bt): break
                                        return bt
                                    self.scroll.scroll_to(__getTopButton())
                            scrollselfUp.bind(on_release=__scrollClick)
                            scrollselfDown.bind(on_release=__scrollClick)
                            fBox.add_widget(scrollselfUp)
                            fBox.add_widget(scrollselfDown)
                            self.floaterBox.add_widget(fBox)

        if progress and self.allowDelayOnUpdateList:
            self.showProgress()
            Clock.schedule_once(__continue, 0)
        else: __continue()

    def scrollClick(self, instance, delay=True):
        """ Действия, которые совершаются на указанных списках по нажатию на пункт списка """

        def __click(*args): # действие выполняется с запаздыванием, чтобы отобразилась анимация на кнопке
            self.clickedBtn = instance
            self.clickedBtnIndex = instance.id
            if self.msg[6] in instance.text: # "создать подъезд"
                text = instance.text[len(self.msg[6])+70 : ] # число символов во фразе msg[6] + 4 на форматирование
                #print(text) # должно выглядеть: 1[/i]
                if "[/i]" in text: text = text[ : text.index("[")]
                newPorch = self.house.addPorch(text.strip())
                self.save()
                self.houseView(instance=instance, jump=self.house.porches.index(newPorch))
                return
            elif self.msg[11] in instance.text or self.msg[12] in instance.text or self.msg[213] in instance.text: # "создайте"
                self.positivePressed(instant=True)
                return

            if self.displayed.form == "porchView" or self.displayed.form == "con":
                self.contactsEntryPoint = 0
                self.searchEntryPoint = 0

            if self.displayed.form == "ter":
                self.house = self.houses[instance.id]
                self.houseView(instance=instance)

            elif self.displayed.form == "houseView":
                self.porch = self.house.porches[instance.id]
                self.flat = None
                self.porchView(instance=instance)

            elif self.displayed.form == "porchView":
                self.flat = instance.flat
                self.flatView(call=False, instance=instance)

            elif self.displayed.form == "flatView": # режим редактирования записей
                self.record = self.flat.records[instance.id]
                self.recordView(instance=instance) # вход в запись посещения

            elif self.displayed.form == "con": # контакты
                if len(self.allcontacts) > 0:
                    selection = instance.id
                    h = self.allcontacts[selection][7][0]  # получаем дом, подъезд и квартиру выбранного контакта
                    p = self.allcontacts[selection][7][1]
                    f = self.allcontacts[selection][7][2]
                    if self.allcontacts[selection][8] != "virtual": self.house = self.houses[h]
                    else: self.house = self.resources[1][h] # заменяем дом на ресурсы для отдельных контактов
                    self.porch = self.house.porches[p]
                    self.flat = self.porch.flats[f]
                    self.contactsEntryPoint = 1
                    self.searchEntryPoint = 0
                    self.flatView(instance=instance)

            elif self.displayed.form == "search": # поиск
                if not self.msg[8] in instance.text:
                    selection = instance.id
                    h = self.searchResults[selection][0][0]  # получаем номера дома, подъезда и квартиры
                    p = self.searchResults[selection][0][1]
                    f = self.searchResults[selection][0][2]
                    if self.searchResults[selection][1] != "virtual": self.house = self.houses[h] # regular contacts
                    else: self.house = self.resources[1][h]
                    self.porch = self.house.porches[p]
                    self.flat = self.porch.flats[f]
                    self.searchEntryPoint = 1
                    self.contactsEntryPoint = 0
                    self.flatView(instance=instance)

            elif self.displayed.form == "repLog": # журнал служения
                self.logEntryView(instance.id)

        if delay: Clock.schedule_once(__click, 0)
        else: __click()

    def titlePressed(self, instance, value):
        """ Нажатие на заголовок экрана """
        if value == "report" and self.settings[0][3] > 0:
            self.popup(title=self.msg[247], message=self.msg[202])

    def detailsPressed(self, instance=None, id=0):
        """ Нажата кнопка настроек рядом с заголовком (редактирование данного объекта) """
        self.func = self.detailsPressed
        if self.confirmNonSave(instance): return

        if self.displayed.form == "ter":  # детали участка
            self.displayed.form = "houseDetails"
            self.house = self.houses[id]
            self.dest = self.house.title
            self.createMultipleInputBox(
                title=f"[b]{self.house.title}[/b] {self.button['arrow']} {self.msg[16]}",
                options=[self.msg[14], self.msg[17], self.msg[18]],
                defaults=[self.house.title, self.house.date, self.house.note],
                multilines=[False, False, True],
                disabled=[False, False, False],
                nav=self.button['nav'],
                sort=""
            )
            if self.house.type != "condo": # вручную убираем кнопку навигации, если участок не многоквартирный
                self.navButton.disabled = True
                self.navButton.text = ""

        elif self.displayed.form == "houseView": # детали подъезда
            self.displayed.form = "porchDetails"
            self.porch = self.house.porches[id]
            settings = self.msg[20] if self.house.type == "private" else self.msg[19]
            options = [settings, self.msg[18]]
            defaults = [self.porch.title, self.porch.note]
            self.createMultipleInputBox(
                title=f"[b]{self.house.getPorchType()[1]} {self.porch.title}[/b] {self.button['arrow']} {self.msg[16]}",
                options=options,
                defaults=defaults,
                sort="",
                nav=self.button['nav'],
                multilines=[False, True],
                disabled=[False, False]
            )

        elif (self.displayed.form == "porchView" or self.displayed.form == "createNewFlat") \
                and self.house.type == "condo": # кнопка переключения подъездов
            self.cacheFreeModeGridPosition()

        elif self.displayed.form == "con" or self.displayed.form == "flatView" or self.displayed.form == "noteForFlat" or \
            self.displayed.form == "createNewRecord" or self.displayed.form == "recordView": # детали квартиры
            if self.displayed.form == "con": # если детали вызываются по трем точкам из списка контактов
                h = self.allcontacts[id][7][0]
                p = self.allcontacts[id][7][1]
                f = self.allcontacts[id][7][2]
                self.house = self.houses[h] if self.allcontacts[id][8] != "virtual" else self.resources[1][h]
                self.porch = self.house.porches[p]
                self.flat = self.porch.flats[f]
                self.contactsEntryPoint = 1
                self.searchEntryPoint = 0
                self.generateFlatTitle()
            self.displayed.form = "flatDetails"
            address = self.msg[15] if self.house.type == "virtual" else self.msg[14]
            porch = self.house.getPorchType()[1] + (":" if self.language != "hy" else ".")
            if self.language != "ka": porch = porch[0].upper() + porch[1:]
            name = self.msg[21] + (":" if self.language != "hy" else ".")
            number = self.msg[24] if self.house.type == "condo" else (self.msg[15] if self.house.listType() else self.msg[25])
            addressDisabled = False if self.house.type == "virtual" else True
            porchDisabled = False if self.house.type == "virtual" else True
            numberDisabled = True if self.flat.number == "virtual" else False
            self.enterOnButton = instance
            self.createMultipleInputBox(
                title=f"{self.flatTitle} {self.button['arrow']} {self.msg[204].lower()}",
                options=[name, self.msg[23], address, porch, number, self.msg[18]],
                defaults=[self.flat.getName(), self.flat.phone, self.house.title, self.porch.title, self.flat.number, self.flat.note],
                multilines=[False, False, False, False, False, True],
                disabled=[False, False, addressDisabled, porchDisabled, numberDisabled, False],
                neutral=self.button["phone"] if self.flat.phone == "" else self.button["phone-square"],
                nav=self.button['nav0'] if self.flat.number == "virtual" and self.house.title == "" else self.button['nav'],
                sort="",
                details=f"{self.button['user']} {self.msg[204]}"
            )
            self.detailsButton.disabled = True

        elif self.displayed.form == "rep": # журнал отчета
            if instance == self.detailsButton: self.entryID = None
            options = []
            footer = []
            color = self.RoundButtonColor if self.mode == "light" else self.titleColor2
            for l in range(len(self.resources[2])):
                time, body, tag = self.getLog(l)
                options.append(self.resources[2][l])#body)
                """footer.append([
                    time,
                    f"[color={color}]{tag}[/color]"
                ])"""
            self.displayed.update(
                title=f"[b]{self.msg[10]}[/b]",
                options=options,
                form="repLog",
                #footer=footer,
                tip=self.msg[240] % self.rep.reportLogLimit if len(options) == 0 else None,
                jump=self.entryID
            )
            self.updateList(instance=instance, progress=True)

        elif self.displayed.form == "set": # Помощь
            if self.language == "ru" or self.language == "uk":
                webbrowser.open("https://github.com/antorix/rocket-ministry/wiki/ru")
            else:
                webbrowser.open("https://github.com/antorix/rocket-ministry/wiki")

    def backPressed(self, instance=None):
        """ Нажата кнопка «назад» """
        self.dismissTopPopup(all=True)
        if len(self.stack) > 0: del self.stack[0]
        form = self.displayed.form
        stack = self.stack[0] if len(self.stack) > 0 else ""

        if "createNew" in form or form == "logEntryView": # формы создания нового элемента при шаге назад сохраняют свой текст
            if form == "createNewFlat" and self.house.type == "condo":
                pass # создание квартир – пропускаем, в них свой механизм
            elif self.inputBoxEntry.text.strip() != "" or form == "logEntryView":
                self.positivePressed(instant=True)
                return
            elif form == "createNewLog":
                self.repPressed(jumpToLog=True)
                return
        elif ("flatView" in form and len(self.flat.records) == 0) or "recordView" in form or "Details" in form:
            if "Settings" in str(self.enterOnButton):
                self.enterOnButton = None
                self.positivePressed(instant=True)
                self.backPressed()
            else:
                self.positivePressed(instant=True)
            return

        if form == "repLog":    self.repPressed()
        elif stack == "ter":    self.terPressed(instance=instance)
        elif stack == "con":    self.conPressed(instance=instance)
        elif stack == "rep":    self.repPressed(instance=instance)
        elif stack == "search": self.find(instance=instance)
        elif stack == "houseView":
            self.cacheFreeModeGridPosition()
            if self.house.noSegment(): self.terPressed(instance=instance)
            else: self.houseView(instance=instance)
        elif stack == "porchView" or self.blockFirstCall == 1 or self.msg[162] in self.pageTitle.text:
            self.porchView(instance=instance)
        elif stack == "flatView": self.flatView(instance=instance)
        elif len(self.stack) == 0:  self.terPressed()
        self.updateMainMenuButtons()

    def sortPressed(self, instance=None):
        self.dropSortMenu.clear_widgets()
        self.dropSortMenu.bind(on_select=lambda instance, x: setattr(self.sortButton, 'text', x))
        self.sortButton.bind(on_release=self.dropSortMenu.open)
        def __dismiss(*args):
            if self.theme != "3D":
                self.sortButton.background_color = self.globalBGColor
        self.dropSortMenu.bind(on_dismiss=__dismiss)
        if self.displayed.form == "ter": # меню сортировки участков
            sortTypes = [
                "[u][b]"+self.msg[29]+"[/u][/b]" if self.settings[0][19] == "н" else self.msg[29], # название
                "[u][b]" + self.msg[51] + "[/u][/b]" if self.settings[0][19] == "т" else self.msg[51], # тип
                "[u][b]"+self.msg[38]+"[/u][/b]" if self.settings[0][19] == "р" else self.msg[38], # размер
                "[u][b]"+self.msg[31]+"[/u][/b]" if self.settings[0][19] == "и" else self.msg[31], # интерес
                "[u][b]"+self.msg[30]+"[/u][/b]" if self.settings[0][19] == "д" else self.msg[30], # дата взятия
                "[u][b]"+self.msg[230]+"[/u][/b]" if self.settings[0][19] == "в" else self.msg[230], # дата посл. посещения
               f"[u][b]{self.msg[32]}[/u][/b] {self.button['caret-down']}" if self.settings[0][19] == "п" else\
               f"{self.msg[32]} {self.button['caret-down']}",     # обработка
               f"[u][b]{self.msg[32]}[/u][/b] {self.button['caret-up']}" if self.settings[0][19] == "о" else\
               f"{self.msg[32]} {self.button['caret-up']}"        # обработка назад

            ]
            for i in range(len(sortTypes)):
                btn = SortListButton(text=sortTypes[i])
                def __resortHouses(instance):
                    if instance.text == sortTypes[0]:   self.settings[0][19] = "н"
                    elif instance.text == sortTypes[1]: self.settings[0][19] = "т"
                    elif instance.text == sortTypes[2]: self.settings[0][19] = "р"
                    elif instance.text == sortTypes[3]: self.settings[0][19] = "и"
                    elif instance.text == sortTypes[4]: self.settings[0][19] = "д"
                    elif instance.text == sortTypes[5]: self.settings[0][19] = "в"
                    elif instance.text == sortTypes[6]: self.settings[0][19] = "п"
                    elif instance.text == sortTypes[7]: self.settings[0][19] = "о"
                    self.terPressed()
                    self.dropSortMenu.dismiss()
                btn.bind(on_release=__resortHouses)
                self.dropSortMenu.add_widget(btn)

        if self.displayed.form == "houseView": # меню сортировки подъездов
            sortTypes = [
                "[u][b]"+self.msg[29]+"[/u][/b]" if self.house.porchesLayout == "н" or self.house.porchesLayout == "а" else\
                    self.msg[29], # название
                "[u][b]"+self.msg[230]+"[/u][/b]" if self.house.porchesLayout == "п" else\
                    self.msg[230], # посл. посещение
                f"[u][b]{self.msg[38]}[/u][/b] {self.button['caret-down']}" if self.house.porchesLayout == "р" else\
                    f"{self.msg[38]} {self.button['caret-down']}",     # размер вниз
                f"[u][b]{self.msg[38]}[/u][/b] {self.button['caret-up']}" if self.house.porchesLayout == "о" else\
                    f"{self.msg[38]} {self.button['caret-up']}"        # обработка размер вверх
            ]
            for i in range(len(sortTypes)):
                btn = SortListButton(text=sortTypes[i])
                def __resortPorches(instance):
                    if instance.text == sortTypes[0]:   self.house.porchesLayout = "н"
                    elif instance.text == sortTypes[1]: self.house.porchesLayout = "п"
                    elif instance.text == sortTypes[2]: self.house.porchesLayout = "р"
                    elif instance.text == sortTypes[3]: self.house.porchesLayout = "о"
                    self.houseView()
                    self.dropSortMenu.dismiss()
                btn.bind(on_release=__resortPorches)
                self.dropSortMenu.add_widget(btn)

        elif self.displayed.form == "porchView":
            self.porch.flatsNonFloorLayoutTemp = None
            if not self.porch.floors(): # меню сортировки квартир в подъезде
                button1 = self.msg[33] if self.house.listType() else self.msg[34]
                sortTypes = [
                    f"[u][b]{button1}[/u][/b] {self.button['caret-down']}" if self.porch.flatsLayout == "н" else \
                    f"{button1} {self.button['caret-down']}", # номер
                    f"[u][b]{button1}[/u][/b] {self.button['caret-up']}" if self.porch.flatsLayout == "о" else \
                    f"{button1} {self.button['caret-up']}",   # номер обратно
                    f"[u][b]{self.msg[36]} 1[/u][/b]" if self.porch.flatsLayout == "с" else f"{self.msg[36]} 1", # цвет
                    f"[u][b]{self.msg[36]} 2[/u][/b]" if self.porch.flatsLayout == "с2" else f"{self.msg[36]} 2", # цвет2
                     "[u][b]"+self.msg[230]+"[/u][/b]" if self.porch.flatsLayout == "д" else self.msg[230], # дата посл. посещения
                     "[u][b]"+self.msg[37]+"[/u][/b]" if self.porch.flatsLayout == "з" else self.msg[37], # заметка
                     "[u][b]"+self.msg[35]+"[/u][/b]" if self.porch.flatsLayout == "т" else self.msg[35],  # телефон
                     "[u][b]"+self.msg[220]+"[/u][/b]" if self.porch.flatsLayout == "и" else self.msg[220]  # иконка
                ]
                for i in range(len(sortTypes)):
                    btn = SortListButton(text=sortTypes[i])
                    def __resortFlats(instance):
                        self.porch.scrollview = None
                        if instance.text == sortTypes[0]:   self.porch.flatsLayout = "н"
                        elif instance.text == sortTypes[1]: self.porch.flatsLayout = "о"
                        elif instance.text == sortTypes[2]: self.porch.flatsLayout = "с"
                        elif instance.text == sortTypes[3]: self.porch.flatsLayout = "с2"
                        elif instance.text == sortTypes[4]: self.porch.flatsLayout = "д"
                        elif instance.text == sortTypes[5]: self.porch.flatsLayout = "з"
                        elif instance.text == sortTypes[6]: self.porch.flatsLayout = "т"
                        elif instance.text == sortTypes[7]: self.porch.flatsLayout = "и"
                        self.porchView(instance=instance)
                        self.dropSortMenu.dismiss()
                    btn.bind(on_release=__resortFlats)
                    self.dropSortMenu.add_widget(btn)

        elif self.displayed.form == "con": # меню сортировки контактов
            sortTypes = [
                "[u][b]"+self.msg[21]+"[/u][/b]" if self.settings[0][4] == "и" else self.msg[21], # имя
                "[u][b]"+self.msg[33]+"[/u][/b]" if self.settings[0][4] == "а" else self.msg[33], # адрес
                "[u][b]"+self.msg[230]+"[/u][/b]" if self.settings[0][4] == "д" else self.msg[230], # дата последнего посещения
                "[u][b]"+self.msg[220]+"[/u][/b]" if self.settings[0][4] == "э" else self.msg[220]  # иконка
            ]
            for i in range(len(sortTypes)):
                btn = SortListButton(text=sortTypes[i])
                def __resortCons(instance):
                    if instance.text == sortTypes[0]:   self.settings[0][4] = "и"
                    elif instance.text == sortTypes[1]: self.settings[0][4] = "а"
                    elif instance.text == sortTypes[2]: self.settings[0][4] = "д"
                    elif instance.text == sortTypes[3]: self.settings[0][4] = "э"
                    self.conPressed(instance=instance)
                    self.dropSortMenu.dismiss()
                btn.bind(on_release=__resortCons)
                self.dropSortMenu.add_widget(btn)

    def maleButtonPressed(self, instance):
        """ Быстрый выбор пола и возраста (для мужчин) """
        self.maleMenu.clear_widgets()
        for age in ["<18", "18", "25", "30", "35", "40", "45", "50", "55", "60", "65", "70", "75", "80", "80+"]:
            btn = SortListButton(text=age)
            def __select(instance):
                self.multipleBoxEntries[self.row].text = f"{self.msg[85]}{instance.text} "
                self.maleMenu.dismiss()
            btn.bind(on_release=__select)
            self.maleMenu.add_widget(btn)
        self.maleMenu.bind(on_select=lambda instance, x: setattr(self.maleButton, 'text', x))
        self.maleButton.bind(on_release=self.maleMenu.open)

    def femaleButtonPressed(self, instance):
        """ Быстрый выбор пола и возраста (для женщин) """
        self.femaleMenu.clear_widgets()
        for age in ["<18", "18", "25", "30", "35", "40", "45", "50", "55", "60", "65", "70", "75", "80", "80+"]:
            btn = SortListButton(text=age)
            def __select(instance):
                self.multipleBoxEntries[self.row].text = f"{self.msg[86]}{instance.text} "
                self.femaleMenu.dismiss()
            btn.bind(on_release=__select)
            self.femaleMenu.add_widget(btn)
        self.femaleMenu.bind(on_select=lambda instance, x: setattr(self.femaleButton, 'text', x))
        self.femaleButton.bind(on_release=self.femaleMenu.open)

    # Таймер

    def updateTimer(self, *args):
        """ Обновление таймера """
        endTime = (
                          int( time.strftime("%H", time.localtime()) ) * 3600 + \
                          int( time.strftime("%M", time.localtime()) ) * 60 + \
                          int( time.strftime("%S", time.localtime()) )
                  )
        pause = self.rep.getPauseDur()
        updated = (endTime - self.rep.startTime - pause) / 3600
        self.time2 = updated if updated >= 0 else (updated + 24)
        if self.settings[2][6] > 0:
            if ":" in self.timerText.text:
                mytime = ut.timeFloatToHHMM(self.time2)
                mytime2 = mytime[: mytime.index(":")]
                mytime3 = mytime[mytime.index(":") + 1:]
                self.timerText.text = f"[ref=timerPress]{mytime2} {mytime3}[/ref]" if pause == 0 \
                    else f"[ref=timerPress]{mytime2}:{mytime3}[/ref]"
            else: self.timerText.text = f"[ref=timerPress]{ut.timeFloatToHHMM(self.time2)}[/ref]"
        else: self.timerText.text = ""

        self.timer.updateIcon()

    def timerPressed(self, activate=False, instance=None):
        if not activate and self.timer.text == icon("icon-play-circle"): # клик по остановленному таймеру
            self.popup("timerPressed", title=self.msg[40], message=self.msg[219],
                       options=[self.button["yes"], self.button["no"]])

        else: # нажатие при работающем таймере, в том числе на паузе
            if self.resources[0][1][2] == 0:
                self.popup(title=self.msg[247], message=self.msg[184])
                self.resources[0][1][2] = 1
            self.timer.unpause()
            result = self.rep.toggleTimer()
            if result > 0: # всплывающее окно с выбором: пауза или завершение
                self.popup("timerOff", message="123", title=self.msg[40])
            else: # запуск таймера - первичный или после паузы
                pass # что-нибудь

    # Действия главных кнопок

    def navPressed(self, instance=None):
        """ Кнопка слева от позитивной """
        if self.displayed.form == "porchView":
            if self.porch.floors(): # центровка подъезда на центр или верхний левый угол
                self.porch.floorview.pos = [0, 0] if self.porch.floorview.oversized else self.porch.floorview.centerPos
                self.window_touch_move(tip=False)
            elif len(self.porch.flats) > 0: # переключение кол-ва колонок
                def __continue(*args):
                    if self.settings[0][10] == 1:   self.settings[0][10] = 2
                    elif self.settings[0][10] == 2: self.settings[0][10] = 3
                    elif self.settings[0][10] == 3: self.settings[0][10] = 4
                    elif self.settings[0][10] == 4: self.settings[0][10] = 1
                    if self.porch.scrollview is None: self.updateList(instance=instance)
                    for b in self.porch.scrollview.children[0].children:
                        for widget in b.children:
                            if "FlatButton" in str(widget):
                                widget.update(flat=widget.flat)
                                break
                    self.porchView(instance=instance)
                self.showProgress()
                Clock.schedule_once(__continue, 0)

        elif self.dest is not None: # Навигация до участка/контакта
            try:
                if self.settings[0][21] == "Yandex" or self.settings[0][21] == "Яндекс":
                    address = f"yandexmaps://maps.yandex.ru/maps/?mode=search&text={self.dest}"
                elif self.settings[0][21] == "2GIS" or self.settings[0][21] == "2ГИС":
                    address = f"dgis://2gis.ru/search/{self.dest}"
                elif self.settings[0][21] == "Google":
                    address = f"google.navigation:q={self.dest}"
                else: # по умолчанию
                    address = f"geo:0,0?q={self.dest}"
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                intent = Intent(Intent.ACTION_VIEW, Uri.parse(address))
                mActivity.startActivity(intent)
            except:
                if self.settings[0][21] == "Yandex" or self.settings[0][21] == "Яндекс":
                    webbrowser.open(f"https://yandex.ru/maps/?mode=search&text={self.dest}")
                elif self.settings[0][21] == "2GIS" or self.settings[0][21] == "2ГИС":
                    webbrowser.open(f"https://2gis.ru/search/{self.dest}")
                else:#elif self.settings[0][21] == "Google":
                    webbrowser.open(f"http://maps.google.com/?q={self.dest}")

    def positivePressed(self, instance=None, instant=False, value=None, default=""):
        """ Что выполняет центральная кнопка в зависимости от экрана """
        global Rounded

        # Поиск

        def __press(*args):
            if self.msg[146] in self.pageTitle.text:
                input = self.inputBoxEntry.text.lower().strip()

                if input == "report000":
                    self.rep.checkNewMonth(forceDebug=True)

                elif input == "@": # экспорт в облако с выбором приложения
                    self.share(email=True, create_chooser=True)

                elif input == "%": # экспорт в облако без выбора приложения
                    self.share(email=True, create_chooser=False)

                elif input == "^": # проверка обновлений
                    self.update(forced=True)

                elif input == "#": # импорт через буфер обмена
                    self.save(backup=True)
                    self.load(clipboard=Clipboard.paste().strip())

                elif input != "":
                    self.searchQuery = input
                    self.find(instance=instance)

            # Форма создания квартир/домов

            elif self.displayed.form == "porchView":
                def __linkPressed(instance, *args):
                    self.popup(popupForm="addList", instance=instance)

                if self.house.type == "condo": # многоквартирный дом
                    self.displayed.form = "createNewFlat"
                    self.clearTable()
                    self.positive.text = self.button["save"]
                    if len(self.porch.flats) > 0: self.stack.insert(0, self.stack[0])
                    self.mainList.clear_widgets()
                    grid = GridLayout(rows=3, cols=2, col_force_default = True, padding=self.padding, # основная сетка
                                      size_hint_y = .4 if self.orientation=="v" else .6)
                    if self.orientation=="v": # ширина колонок основной таблицы
                        grid.cols_minimum = {0: self.mainList.size[0] * .4, 1: self.mainList.size[0] * .55}
                    else:
                        grid.cols_minimum = {0: self.mainList.size[0] * .3, 1: self.mainList.size[0] * .4}
                        grid.pos_hint={"center_x": .65}
                    align = "center"
                    if len(self.porch.flats) == 0: # определяем номер первой и последней квартир, сначала если это первый подъезд:
                        if len(self.house.porches) == 1: # если это первый подъезд дома, пытаемся загрузить параметры из настроек:
                            try: # попытка загрузить первичные параметры этажей из настроек
                                firstflat, lastflat, floors = self.settings[0][9]
                            except:
                                firstflat, lastflat, floors = "1", "20", "5"
                        else:
                            firstflat, lastflat, floors = "1", "20", "5"
                        selectedPorch = self.house.porches.index(self.porch)
                        if selectedPorch > 0:
                            prevFirst, prevLast, floors = self.house.porches[selectedPorch - 1].getFirstAndLastNumbers()
                            prevRange = int(prevLast) - int(prevFirst)
                            firstflat = str(int(prevLast) + 1)
                            lastflat = str(int(prevLast) + 1 + prevRange)
                    else: # если уже есть предыдущие подъезды:
                        firstflat, lastflat, floors = self.porch.getFirstAndLastNumbers()
                    grid.add_widget(MyLabel(text=self.msg[58], halign=align, valign=align)) # квартир
                    flatsRangeA = AnchorLayout()
                    flatsRangeForm = BoxLayout(height=self.standardTextHeight*1.1, size_hint_y=None)

                    if self.msg[59] != "": flatsRangeForm.add_widget(MyLabel(text=self.msg[59], size_hint_x=None,
                                                                             halign=align, valign=align)) # с
                    a1 = AnchorLayout(anchor_x="center", anchor_y="center")
                    self.flatRangeStart = MyTextInput(text=firstflat, multiline=False, font_size=self.fontBigEntry,
                                                      halign="center", input_type="number")
                    a1.add_widget(self.flatRangeStart)
                    flatsRangeForm.add_widget(a1)
                    flatsRangeForm.add_widget(MyLabel(text=self.msg[60],  size_hint_x=None, halign=align, valign=align)) # по
                    a2 = AnchorLayout(anchor_x="left", anchor_y="center")
                    self.flatRangeEnd = MyTextInput(text=lastflat, multiline=False, font_size=self.fontBigEntry,
                                                    halign="center", input_type="number")
                    a2.add_widget(self.flatRangeEnd)
                    flatsRangeForm.add_widget(a2)
                    flatsRangeA.add_widget(flatsRangeForm)
                    grid.add_widget(flatsRangeA)
                    grid.add_widget(MyLabel(text=self.msg[61], halign=align, valign=align)) # этажей
                    self.floors = Counter(text=floors)
                    grid.add_widget(self.floors)
                    grid.add_widget(MyLabel(text=f"{self.msg[62]}\n{self.msg[63]}", halign=align, valign=align)) # 1-й этаж
                    self.floor1 = Counter(text=str(self.porch.floor1))
                    grid.add_widget(self.floor1)
                    self.mainList.add_widget(grid)
                    self.mainList.add_widget(self.tip(icon="link", text=self.msg[249], hint_y=.05, func=__linkPressed))

                    if len(self.porch.flats) == 0:
                        self.mainList.add_widget(self.tip(text=self.msg[312] % f"[b]{self.msg[5]}[/b]", hint_y=.09))
                    else:
                        self.mainList.add_widget(self.tip(text=self.msg[311]+"\n", hint_y=.09))

                elif self.house.listType(): # участок-список
                    self.popup("addList")

                else: # универсальный участок
                    self.displayed.form = "createNewFlat"
                    self.clearTable()
                    def handleCheckbox(instance):
                        value = instance.value
                        if value:
                            self.inputBoxText.text = self.msg[167]
                            filled = self.inputBoxEntry.text
                            self.textbox.remove_widget(self.inputBoxEntry)
                            self.inputBoxEntry = MyTextInput(text=filled, hint_text=self.msg[59], multiline=self.multiline,
                                                             height=self.standardTextHeight*self.enlargedTextCo,
                                                             rounded=True, size_hint_x=Window.size[0]/2,
                                                             size_hint_y=None, pos_hint=self.pos_hint, input_type="number")
                            self.textbox.add_widget(self.inputBoxEntry)
                            self.inputBoxEntry2 = MyTextInput(hint_text=self.msg[60], multiline=self.multiline,
                                                              height=self.standardTextHeight*self.enlargedTextCo,
                                                              input_type="number", size_hint_x=Window.size[0]/2,
                                                              rounded=True, size_hint_y=None, pos_hint=self.pos_hint)
                            self.inputBoxEntry.halign = self.inputBoxEntry2.halign ="center"
                            self.inputBoxEntry.height *= self.enlargedTextCo
                            self.inputBoxEntry2.height *= self.enlargedTextCo
                            if not self.desktop:
                                self.inputBoxEntry.font_size = self.inputBoxEntry2.font_size = self.fontBigEntry
                            self.textbox.add_widget(self.inputBoxEntry2)
                        else:
                            self.inputBoxText.text = self.msg[64]
                            self.textbox.remove_widget(self.inputBoxEntry2)
                            self.inputBoxEntry.hint_text = self.hint
                            self.inputBoxEntry.input_type = "text"
                    self.createInputBox(
                        title=None,# не меняется
                        message=self.msg[64],
                        checkbox=self.msg[65],
                        handleCheckbox=handleCheckbox,
                        active=False,
                        positive=self.button["save"],
                        hint=self.msg[66],
                        link=[self.msg[307], __linkPressed]
                    )

            # Формы добавления

            elif self.displayed.form == "ter": # добавление участка
                self.detailsButton.disabled = True
                self.displayed.form = "createNewHouse"
                self.terTypeSelector = BoxLayout(orientation="horizontal", padding=(self.padding*4, 0),
                                                 spacing=0 if self.theme != "3D" else self.spacing)
                if self.language == "ru" or self.language == "uk":
                    b1 = TerTypeButton("condo", on=True if self.settings[0][7] == "condo" else False)
                    b2 = TerTypeButton("private", on=True if self.settings[0][7] == "private" else False)
                    b3 = TerTypeButton("list", on=True if self.settings[0][7] == "list" else False)
                else:
                    b1 = TerTypeButton("private", on=True if self.settings[0][7] == "private" else False)
                    b2 = TerTypeButton("condo", on=True if self.settings[0][7] == "condo" else False)
                    b3 = TerTypeButton("list", on=True if self.settings[0][7] == "list" else False)
                self.terTypeSelector.add_widget(b1)
                self.terTypeSelector.add_widget(b2)
                self.terTypeSelector.add_widget(b3)
                if self.settings[0][7] == "condo": hint = self.msg[70] # обновление текста подсказки
                elif self.settings[0][7] == "private": hint = self.msg[166]
                elif self.settings[0][7] == "list":
                    string = ""
                    for char in self.msg[70]:
                        string += char
                        if char == ":" or char == ".": break
                    hint = f"{string} A1"
                else:
                    hint = self.msg[70] if self.language == "ru" or self.language == "uk" else self.msg[166]
                memoBox = AnchorLayout(anchor_x="right", anchor_y="center")
                self.memorize = FontCheckBox(
                    text=self.msg[68], button_size=self.fontM, padding=(self.padding*2, 0),
                    button_color=self.linkColor if self.mode == "light" else self.titleColor,
                    size_hint=(None, None), halign="right", valign="center",
                    active=True if self.settings[0][7] is not None and self.settings[0][7] != 0 else False,
                    height=memoBox.height, width=self.mainList.size[0])
                def __checkbox_click(instance):
                    if not instance.value: self.settings[0][7] = None
                self.memorize.bind(on_press=__checkbox_click)
                memoBox.add_widget(self.memorize)
                self.createInputBox(
                    title=f"[b]{self.msg[67]}[/b]",
                    embed=self.terTypeSelector,
                    embed2=memoBox,
                    message=self.msg[165],
                    default=default,
                    sort="",
                    limit=self.charLimit,
                    hint=hint
                )

            elif self.displayed.form == "houseView": # добавление подъезда
                self.displayed.form = "createNewPorch"
                if self.house.type == "condo":
                    message = self.msg[72]
                    hint = self.msg[73]
                    tip = self.msg[74]
                    checkbox = None
                else:
                    message = self.msg[75]
                    hint = ""
                    checkbox = self.msg[48] if len(self.house.porches) == 0 else None
                    tip = ""
                def __handleCheckbox(instance):
                    value = instance.value
                    if value:
                        self.inputBoxEntry.disabled = True
                        self.inputBoxEntry.hint_text = ""
                    else:
                        self.inputBoxEntry.disabled = False
                        self.inputBoxEntry.hint_text = hint
                self.createInputBox(
                    title=f"[b]{self.house.title}[/b] {self.button['arrow']} {self.msg[77 if self.house.type == 'condo' else 78].lower()}",
                    message=message,
                    hint=hint,
                    sort="",
                    checkbox=checkbox,
                    handleCheckbox=__handleCheckbox,
                    active=False,
                    limit=self.charLimit,
                    tip=tip
                )

            elif self.displayed.form == "con": # добавление контакта
                self.detailsButton.disabled = True
                self.displayed.form = "createNewCon"
                self.createInputBox(
                    title=f"[b]{self.msg[79]}[/b]",
                    message=self.msg[80],
                    multiline=False,
                    sort="",
                    limit=self.charLimit,
                    tip=self.msg[81]
                )

            elif self.displayed.form == "flatView": # добавление посещения
                self.house.statsCached = None
                if len(self.flat.records) > 0:
                    self.displayed.form = "createNewRecord" # добавление нового посещения в существующем контакте
                    self.createInputBox(
                        title=f"{self.flatTitle} {self.button['arrow']} {self.msg[161].lower()}",
                        message=self.msg[125],
                        multiline=True,
                        details=f"{self.button['user']} {self.msg[204]}",
                        neutral=self.button["phone"] if self.flat.phone == "" else self.button["phone-square"]
                    )
                else: # сохранение первого посещения и выход в подъезд
                    newName = self.multipleBoxEntries[0].text.strip()
                    if newName != "" or self.house.type != "virtual":
                        self.flat.updateName(newName)
                    if self.multipleBoxEntries[1].text.strip() != "":
                        self.flat.addRecord(self.multipleBoxEntries[1].text.strip())
                    self.flat.updateStatus()
                    self.save()
                    for entry in self.multipleBoxEntries: entry.text = ""
                    if self.contactsEntryPoint: self.conPressed(instance=instance)
                    elif self.searchEntryPoint: self.find()
                    else: self.porchView(instance=instance)

            elif self.displayed.form == "createNewRecord":  # добавление новой записи посещения (повторное)
                self.displayed.form = "flatView"
                self.house.statsCached = None
                record = self.inputBoxEntry.text.strip()
                self.flat.addRecord(record)
                self.save()
                self.flatView(instance=instance)

            elif self.displayed.form == "repLog": # добавление записи журнала
                self.detailsButton.disabled = True
                self.displayed.form = "createNewLog"
                self.createInputBox(
                    title=f"[b]{self.msg[332]}[/b]",
                    message=f"{self.msg[333]}{self.col}",
                    multiline=False,
                    sort="",
                    limit=self.charLimit,
                    tip=self.msg[334]
                )

            # Формы сохранения

            elif self.displayed.form == "createNewHouse":  # сохранение нового участка
                self.displayed.form = "ter"
                newTer = self.inputBoxEntry.text.strip()
                for widget in self.terTypeSelector.children:
                    if not "Label" in str(widget):
                        if widget.on:
                            condo = widget.type
                            break
                else:
                    self.popup(title=self.msg[203], message=self.msg[234])
                    self.displayed.form = "createNewHouse"
                    return
                if newTer == "": newTer = f"{self.msg[137]} {len(self.houses)+1}"
                if self.language == "ka": self.addHouse(self.houses, newTer, condo)
                else: self.addHouse(self.houses, newTer, condo)
                self.settings[0][7] = condo if self.memorize.active else None
                self.save()
                self.terPressed()

            elif self.displayed.form == "createNewPorch":  # сохранение нового подъезда
                self.displayed.form = "houseView"
                newPorch = self.inputBoxEntry.text.strip()
                if self.house.type == "private" and len(self.house.porches) == 0 and self.checkbox.active:
                    newPorch = self.invisiblePorchName
                elif newPorch == "": newPorch = str(self.house.getLastPorchNumber())
                self.house.addPorch(newPorch, self.house.getPorchType()[0])
                self.save()
                self.houseView()

            elif self.displayed.form == "createNewFlat":  # сохранение новых квартир
                if self.house.type == "condo":  # многоквартирный подъезд
                    self.popupForm = "updatePorch"
                    if len(self.porch.flats) > 0:
                        self.popup(title=self.msg[203], message=self.msg[229], # "Обновить параметры подъезда?"
                                   options=[self.button["yes"], self.button["no"]])
                    else:
                        self.popupPressed(instance=Button(text=self.button["yes"]))
                else: # сохранение домов в сегменте универсального участка
                    self.porch.scrollview = self.house.statsCached= None
                    start = self.decommify(self.inputBoxEntry.text)
                    if not self.checkbox.active:
                        self.porch.addFlat(start)
                        self.save()
                        self.porchView(instance=instance)
                    else:
                        finish = self.inputBoxEntry2.text.strip()
                        try:
                            if int(start) > int(finish): 5/0
                            self.porch.addFlats(int(start), int(finish))
                        except:
                            self.popup(title=self.msg[203], message=self.msg[91])
                            return
                        else:
                            self.save()
                            self.porchView(instance=instance)

            elif self.displayed.form == "recordView": # сохранение уже существующей записи посещения
                self.displayed.form = "flatView"
                self.flat.editRecord(self.record, self.inputBoxEntry.text.strip())
                self.house.statsCached = None
                self.save()
                self.flatView(instance=instance)

            elif self.displayed.form == "createNewCon": # сохранение нового контакта
                self.displayed.form = "con"
                name = self.decommify(self.inputBoxEntry.text)
                if name == "": name = f"{self.msg[158]} {len(self.resources[1])+1}"
                self.addHouse(self.resources[1], "", "virtual")  # создается новый виртуальный дом
                self.resources[1][len(self.resources[1]) - 1].addPorch(input="", type="virtual")
                self.resources[1][len(self.resources[1]) - 1].porches[0].addFlat(name, virtual=True)
                self.resources[1][len(self.resources[1]) - 1].porches[0].flats[0].status = "1"
                self.save()
                self.conPressed(instance=instance)

            elif self.displayed.form == "createNewLog":  # сохранение новой записи журнала
                self.displayed.form = "repLog"
                entry = self.inputBoxEntry.text.strip()
                date = time.strftime("%d.%m", time.localtime()) + "." + \
                       str(int(time.strftime("%Y", time.localtime())) - 2000)
                time2 = time.strftime("%H:%M:%S", time.localtime())
                div = "|" if entry != "" else ""
                self.resources[2].insert(0, f"\n{date} {time2}  {div}{entry}".strip())
                self.save()
                self.repPressed(jumpToLog=True)

            elif self.displayed.form == "logEntryView":  # сохранение существующей записи журнала
                self.displayed.form = "repLog"
                new = self.inputBoxEntry.text.strip()
                body = f"  {self.entryBody}" if self.entryBody != "" else ""
                div = "|" if new != "" else ""
                self.resources[2][self.entryID] = f"\n{self.entryDate}{body}{div}{new}"
                self.save()
                self.repPressed(jumpToLog=True)

            # Детали

            elif self.displayed.form == "houseDetails": # детали участка
                self.displayed.form = "houseView"
                self.house.note = self.multipleBoxEntries[2].text.strip()
                newTitle = self.multipleBoxEntries[0].text.strip()
                if newTitle == "": newTitle = self.house.title
                self.house.title = newTitle
                newDate = self.multipleBoxEntries[1].text.strip()
                if ut.checkDate(newDate):
                    self.house.date = newDate
                    self.house.dueCached = None
                    self.save()
                    self.terPressed()
                else:
                    self.save()
                    self.displayed.form = "ter"
                    self.detailsPressed() # при ошибочном вводе даты вручную перезаходим в настройки
                    self.popup(message=self.msg[92])
                    return

            elif self.displayed.form == "porchDetails": # детали подъезда
                self.displayed.form = "porchView"
                self.porch.note = self.multipleBoxEntries[1].text.strip()
                newTitle = self.multipleBoxEntries[0].text.strip() # попытка изменить название подъезда - сначала проверяем, что нет дублей
                if newTitle == "": newTitle = self.porch.title
                self.porch.title = newTitle
                self.save()
                self.houseView()

            elif self.displayed.form == "flatDetails": # детали квартиры/контакта
                self.displayed.form = "flatView"
                self.house.statsCached = None
                newName = self.multipleBoxEntries[0].text.strip() # имя
                if newName != "" or self.house.type != "virtual": self.flat.updateName(newName)
                self.flat.editPhone(self.multipleBoxEntries[1].text) # телефон
                if self.house.type == "virtual": # адрес
                    self.house.title = self.multipleBoxEntries[2].text.strip()
                self.porch.title = self.multipleBoxEntries[3].text.strip() # подъезд
                if self.house.type == "virtual":
                    newNumber = self.multipleBoxEntries[4].text.strip() # номер/адрес
                elif len(self.multipleBoxEntries[4].text) > 0 and self.multipleBoxEntries[4].text.strip()[0] != "-"\
                        and self.multipleBoxEntries[4].text.strip()[0] != "+" and self.multipleBoxEntries[4].text.strip()[0] != ".":
                    if self.house.type == "condo" and self.multipleBoxEntries[4].text.strip()[0] == "0":
                        return # в многокв. домах квартира не должна начинаться с 0
                    else: newNumber = self.multipleBoxEntries[4].text.strip()
                else:
                    self.detailsPressed()
                    return
                self.flat.editNote(self.multipleBoxEntries[5].text)  # заметка
                # проверяем, чтобы не было точек и запятых
                if ("." in self.multipleBoxEntries[4].text.strip() and self.house.type == "condo") \
                        or "," in self.multipleBoxEntries[4].text.strip():
                    self.popup(message=self.msg[89 if self.house.type == "condo" else 90])
                else: # все корректно, сохраняем
                    if newNumber != self.flat.number:
                        self.flat.updateTitle(newNumber)
                        self.porch.floorview = self.porch.scrollview = None # при смене номера обнуляем все представления
                    self.save()
                    if self.popupEntryPoint: self.porchView(instance=instance)
                    else:
                        if "Settings" in str(self.enterOnButton):
                            self.conPressed(instance=instance)
                        else:
                            self.flatView(instance=instance)

        if instant: # мгновенный вызов без запаздывания
            __press()
            return True
        else:
            Clock.schedule_once(__press, 0)
            return True

    def neutralPressed(self, instance=None):
        if self.displayed.form == "porchView":
            if self.resources[0][1][3] == 0: # три режима подъезда
                self.popup(title=self.msg[247],
                           message=(self.msg[171] % (self.button["fgrid"], self.button["resize"], self.button["flist"])).replace("#", "\n\n   "))
                self.resources[0][1][3] = 1
            if self.porch.floors(): # этажи активированы в настройках подъезда
                if self.porch.pos[0] is True: # если свободный режим - включаем заполняющий
                    self.porch.pos[0] = False
                    if self.porch.floorview is not None: self.porch.pos[1] = copy(self.porch.floorview.pos)
                    self.porchView(instance=instance)
                elif self.porch.pos[0] is False: # если заполняющий режим - включаем список
                    if self.porch.flatsNonFloorLayoutTemp is not None:
                        self.porch.flatsLayout = self.porch.flatsNonFloorLayoutTemp
                    else: self.porch.flatsLayout = "н"
                    self.porchView(instance=instance)
            else: # если список - включаем свободный режим (если позволяет размер, иначе автоматически включается заполняющий)
                self.porch.pos[0] = True
                if self.porch.floorview is not None: self.porch.floorview.pos = self.porch.pos[1]
                self.porch.flatsLayout = self.porch.type[7:] # определение этажей по цифре в типе подъезда
                if self.porch.flatsLayout == "":
                    self.popup(message=self.msg[94] % self.msg[155])
                self.porchView(instance=instance)
            self.save()

        elif self.button["phone"] in instance.text or self.button["phone-square"] in instance.text:
            self.phoneCall(instance=instance)

    # Действия других кнопок

    def terPressed(self, instance=None, updateStack=True):
        self.func = self.terPressed
        if self.confirmNonSave(instance): return
        elif "MainMenuButton" in str(instance): self.house = None # сброс перемотки списка
        self.cacheFreeModeGridPosition()
        self.contactsEntryPoint = 0
        self.searchEntryPoint = 0

        if self.settings[0][19] == "д":  # first sort - by date
            self.houses.sort(key=lambda x: x.date, reverse=False)
        elif self.settings[0][19] == "р":  # by size
            for house in self.houses:
                house.size = house.getHouseStats()[3]
            self.houses.sort(key=lambda x: x.size, reverse=True)
        elif self.settings[0][19] == "н":  # alphabetic by title
            self.houses.sort(key=lambda x: x.title, reverse=False)
        elif self.settings[0][19] == "и":  # by number of interested persons
            for house in self.houses:
                house.interest = house.getHouseStats()[1]
            self.houses.sort(key=lambda x: x.interest, reverse=True)
        elif self.settings[0][19] == "п":  # by progress
            for house in self.houses:
                house.progress = house.getHouseStats()[2]
            self.houses.sort(key=lambda x: x.progress, reverse=False)
        elif self.settings[0][19] == "о":  # by progress reversed
            for house in self.houses:
                house.progress = house.getHouseStats()[2]
            self.houses.sort(key=lambda x: x.progress, reverse=True)
        elif self.settings[0][19] == "т":  # by type
            self.houses.sort(key=lambda x: x.sort())
        elif self.settings[0][19] == "в":  # by last visit
            for house in self.houses:
                house.progress = house.getHouseStats()[4]
            self.houses.sort(key=lambda x: x.progress, reverse=False)

        housesList = []
        footer = []
        for i in range(len(self.houses)):
            stats = self.houses[i].getHouseStats()
            due = self.houses[i].due()
            if self.houses[i].listType():
                listIcon = self.button['list-ter']
            else:
                listIcon = self.button['building'] if self.houses[i].type == "condo" else self.button['map']
            housesList.append(f"{listIcon} [b]{self.houses[i].title}[/b]")
            shortenedDate = ut.shortenDate(self.houses[i].date)
            dateDue = f"[color=F4CA16]{self.button['warn']}[/color]"
            interested = f"[b]{(stats[1])}[/b]" if int(stats[1]) > 0 else str((int(stats[1])))
            intIcon = self.button['contact'] if int(stats[1]) != 0 else icon("icon-user-o")
            footer.append([
                f"{icon('icon-home')} {stats[3]}", # кол-во квартир
                f"[color={self.interestColor}]{intIcon} {interested}[/color]", # интересующиеся
                f"{self.button['calendar'] if not due else dateDue} {str(shortenedDate)}", # дата
                f"{self.button['worked']} {int(stats[2] * 100)}%" # обработка
                ])
            if self.fontScale() <= 1:
                footer[i].insert(0, "")
                footer[i].append("")
        buildingIcon = self.button['building'] if RM.language == "ru" or RM.language == "uk" else self.button['map']
        housesList.append(f"{self.button['plus-1']}{buildingIcon} {self.msg[95]}") if len(housesList) == 0 else None

        self.displayed.update( # display list of houses and options
            title=f"[b]{self.msg[2]}[/b] ({len(self.houses)})",
            message=self.msg[97],
            options=housesList,
            footer=footer,
            form="ter",
            sort=self.button['sort'] if len(self.houses) > 0 else None,
            positive=f"{self.button['plus']} {self.msg[98]}",
            back=False,
            tip=[self.resources[0][0], "header"] if self.resources[0][0] != "" else None,
            jump=self.houses.index(self.house) if self.house is not None and self.house in self.houses else None
        )
        if updateStack: self.stack = ["ter"]
        self.updateList(instance=instance, progress=False)

        if len(self.houses) == 0 and self.orientation == "v": # слегка анимируем запись "Создайте первый участок"
            self.mainList.padding = (0, self.padding * 5, 0, Window.size[1] * .3)
            self.scroll.scroll_to(widget=self.btn[0], animate=True)

        self.updateMainMenuButtons()
        self.buttonTer.activate()

        def __getTBH(*args):
            self.TBH = self.titleBox.height # запись высоты titlebox, чтобы она не прыгала при скрытии центральной кнопки
        Clock.schedule_once(__getTBH, 0)

    def conPressed(self, instance=None):
        if instance is not None:
            self.func = self.conPressed
            if self.confirmNonSave(instance): return
            elif "MainMenuButton" in str(instance): self.clickedBtnIndex = None
        self.buttonCon.activate()
        self.contactsEntryPoint = 1
        self.searchEntryPoint = 0
        self.cacheFreeModeGridPosition()
        self.allcontacts = self.getContacts()
        options = []
        footer = []

        # Sort
        if   self.settings[0][4] == "и": self.allcontacts.sort(key=lambda x: x[0]) # by name
        elif self.settings[0][4] == "а": self.allcontacts.sort(key=lambda x: x[2]) # by address
        elif self.settings[0][4] == "д": self.allcontacts.sort(key=lambda x: x[5]) # by date
        elif self.settings[0][4] == "э": self.allcontacts.sort(key=lambda x: self.icons.index(x[1])) # by icon

        for i in range(len(self.allcontacts)):

            if self.allcontacts[i][3] == "virtual": self.allcontacts[i][3] = ""
            if self.allcontacts[i][15] != "condo" and self.allcontacts[i][15] != "virtual":
                porch = self.allcontacts[i][12]
                gap = ", "
            else: porch = gap = ""

            if self.allcontacts[i][15] == "virtual": # отдельный контакт
                addr = self.allcontacts[i][2] # адрес дома
            elif self.allcontacts[i][15] == "condo": # многоквартирный
                addr = self.allcontacts[i][2] # адрес дома
            elif self.allcontacts[i][6]: # бессегментный участок
                if self.allcontacts[i][14]: # listType(): True
                    addr = gap = porch = ""
                else:
                    addr = self.allcontacts[i][2] # бессегментный, но не списочный
                    porch = ""
            elif self.allcontacts[i][15] == "private": # частный и сегментный
                addr = self.allcontacts[i][12] # street (porch) name
                porch = ""
                gap = ", "
            else:
                addr = ""
                gap = ""

            hyphen = "–" if "подъезд" in self.allcontacts[i][8] else ""
            address = f" {addr}{gap}{porch}{hyphen}{self.allcontacts[i][3]}"\
                if self.allcontacts[i][2] != "" else ""
            listIcon = f"[color={get_hex_from_color(self.getColorForStatus('1'))}]{self.button['contact']}[/color]"
            options.append(f"[size={self.listIconSize}]{listIcon}[/size] {self.allcontacts[i][0]} {self.allcontacts[i][1]}")
            footer.append([
                f"{self.button['chat']} {self.allcontacts[i][4]}" if self.allcontacts[i][4] is not None else "",
                "" if address == "" else f"{icon('icon-home')} {address}"
            ])

        self.displayed.update(
            form="con",
            title=f"[b]{self.msg[3]}[/b] ({len(self.allcontacts)})",
            message=self.msg[96],
            options=options,
            footer=footer,
            sort=self.button['sort'] if len(options) > 0 else None,
            positive=f"{self.button['plus']} {self.msg[100]}",
            jump=self.clickedBtnIndex if self.clickedBtnIndex is not None else None,
            tip=self.msg[99] % self.msg[100] if len(options) == 0 else None
        )
        self.stack = ['con', 'ter']
        self.updateList(instance=instance, progress=False)
        self.updateMainMenuButtons()

    def repPressed(self, instance=None, jumpToPrevMonth=False, jumpToLog=False):
        self.func = self.repPressed
        if self.confirmNonSave(instance): return
        self.buttonRep.activate()
        self.clearTable()
        self.neutral.disabled = True
        self.neutral.text = ""
        self.sortButton.disabled = True
        self.sortButton.text = ""
        self.displayed.form = "rep"
        self.stack.insert(0, self.displayed.form)
        self.stack = list(dict.fromkeys(self.stack))
        self.mainList.clear_widgets()
        self.hidePositiveButton()

        if jumpToLog:
            self.detailsPressed()
            return

        self.detailsButton.text = f"{self.button['log']} {self.msg[101]}"
        self.detailsButton.disabled = False
        hours = self.rep.getCurrentHours()[2]
        info = f" {self.button['info']}" if hours != "" else ""
        self.pageTitle.text = f"[b][ref=report]{self.msg[4]}[/b]{hours}{info}[/ref]"
        self.reportPanel = TabbedPanel(background_color=self.globalBGColor, background_image="")

        # Первая вкладка: отчет прошлого месяца

        tab2 = TTab(text=self.monthName()[2])
        report2 = AnchorLayout(anchor_x="center", anchor_y="center")
        hint = "" if self.rep.lastMonth != "" else self.msg[111]
        box = BoxLayout(orientation="vertical", size_hint=(None, None), width=self.standardTextHeight*8,
                        spacing=self.spacing, height=self.standardTextHeight*7)
        self.repBox = MyTextInput(text=self.rep.lastMonth, hint_text=hint, multiline=True, specialFont=True)

        if self.theme != "3D":
            btnSend = RoundButton(text=f"{self.button['share']} {self.msg[110]} ", size_hint_x=1, size_hint_y=None,
                                  size=(0, self.standardTextHeightUncorrected * 1.3))
        else:
            btnSend = RetroButton(text=f"{self.button['share']} {self.msg[110]}", size_hint_x=1, size_hint_y=None,
                                  height=self.standardTextHeightUncorrected * 1.3)
        btnSend.bind(on_release=self.sendLastMonthReport)
        report2.add_widget(box)
        box.add_widget(self.repBox)
        box.add_widget(btnSend)
        tab2.content = report2
        self.reportPanel.add_widget(tab2)
        self.reportPanel.do_default_tab = False

        # Вторая вкладка: текущий месяц

        tab1 = TTab(text=self.monthName()[0])
        text_size = [(Window.size[0] * .4), None]
        g = GridLayout(rows=3, cols=1)

        levelsSizeY = [ # доли трех секций экрана по высоте
            .32 if not self.settings[0][2] else .2,
            .46 if not self.settings[0][2] else .68,
            .22 if not self.settings[0][2] else .12
        ]

        sendBox = AnchorLayout(anchor_x="center", anchor_y="center", pos_hint={"center_x": .5}, # секция с кнопкой отправки
                               size_hint=(1, levelsSizeY[0]))

        if self.theme != "3D":
            send = RoundButton(text=f"{self.button['share']} {self.msg[110]}", size_hint_y=None,
                               size_hint_x=.4 if self.orientation == "v" else .2,
                               size=(0, self.standardTextHeightUncorrected * 1.3))
        else:
            send = RetroButton(text=f"{self.button['share']} {self.msg[110]}", size_hint_y=None,
                               size_hint_x=.4 if self.orientation == "v" else .2,
                               size=(0, self.standardTextHeightUncorrected * 1.3))
        def __sendCurrentMonthReport(*args):
            if not self.desktop:
                plyer.email.send(subject=self.msg[4], text=self.rep.getCurrentMonthReport(), create_chooser=True)
            else:
                Clipboard.copy(self.rep.getCurrentMonthReport())
                self.popup(message=self.msg[133])
        send.bind(on_release=__sendCurrentMonthReport)
        sendBox.add_widget(send)
        g.add_widget(sendBox)

        a = AnchorLayout(anchor_x="center", anchor_y="center", # основная секция отчета
                         size_hint_y = levelsSizeY[1])
        report = GridLayout(cols=2, rows=4, spacing=self.spacing)
        if self.orientation == "h":
            report.size_hint_x = .5
            text_size[0] *= .6
        else:
            report.size_hint_x = .7 * self.fontScale(cap=1.2)
            text_size[0] *= .8 * self.fontScale(cap=1.2)

        report.add_widget(MyLabel(text=self.msg[103], halign="center", valign="center", # изучения
                                  text_size=text_size, color=self.standardTextColor, markup=True))
        self.studies = Counter(text = str(self.rep.studies))
        def __saveStudies(instance):
            """ Сохранение параметра в отчет по нажатию на кнопки счетчика """
            if icon("icon-minus") in instance.text and int(self.studies.input.text) > 0:
                self.rep.studies = int(self.studies.input.text)-1
                self.rep.saveReport(message=self.rep.getLogEntry("-1 study"), log=False)
            elif icon("icon-plus") in instance.text:
                self.rep.studies = int(self.studies.input.text)+1
                self.rep.saveReport(message=self.rep.getLogEntry("+1 study"), log=False)
        self.studies.btnDown.bind(on_release=__saveStudies)
        self.studies.btnUp.bind(on_release=__saveStudies)
        report.add_widget(self.studies)

        report.add_widget(MyLabel(text=self.msg[104], halign="center", valign="center", # часы
                                  text_size=text_size, color=self.standardTextColor, markup=True))
        self.hours = Counter(picker=self.msg[108], type="time", text=ut.timeFloatToHHMM(self.rep.hours))
        def __saveHours(instance):
            """ Сохранение параметра в отчет по нажатию на кнопки счетчика """
            if icon("icon-minus") in instance.text:
                try:
                    if ut.timeHHMMToFloat(self.hours.input.text) >= 1:
                        self.rep.hours = ut.timeHHMMToFloat(self.hours.input.text)-1
                        self.rep.saveReport(message=self.rep.getLogEntry("hours"), log=False)
                    elif ut.timeHHMMToFloat(self.hours.input.text) > 0:
                        self.rep.hours = 0
                        self.rep.saveReport(message=self.rep.getLogEntry("hours"), log=False)
                except: self.popup(message=self.msg[46])
        self.hours.btnDown.bind(on_release=__saveHours)
        report.add_widget(self.hours)

        if self.settings[0][2]: # кредит
            self.creditLabel = MyLabel(text=self.msg[105] % self.rep.getCurrentHours()[0], markup=True,
                                       halign="center", valign="center", text_size = text_size, color=self.standardTextColor)
            report.add_widget(self.creditLabel)
            self.credit = Counter(picker=self.msg[109], type="time", text=ut.timeFloatToHHMM(self.rep.credit))
            def __saveCredit(instance):
                """ Сохранение параметра в отчет по нажатию на кнопки счетчика """
                if icon("icon-minus") in instance.text:
                    try:
                        if ut.timeHHMMToFloat(self.credit.input.text) >= 1:
                            self.rep.credit = ut.timeHHMMToFloat(self.credit.input.text)-1
                            self.rep.saveReport(message=self.rep.getLogEntry("credit"), log=False)
                        elif ut.timeHHMMToFloat(self.credit.input.text) > 0:
                            self.rep.credit = 0
                            self.rep.saveReport(message=self.rep.getLogEntry("credit"), log=False)
                    except: self.popup(message=self.msg[46])
            self.credit.btnDown.bind(on_release=__saveCredit)
            report.add_widget(self.credit)

        g.add_widget(a)

        g.add_widget(Widget(size_hint_y=levelsSizeY[2])) # секция для забивки пустой ячейки внизу

        a.add_widget(report)
        tab1.content = g
        self.reportPanel.add_widget(tab1)

        # Третья вкладка: служебный год

        self.months = []
        if self.settings[0][3] > 0:
            tab3 = TTab(text=self.msg[49])
            x, y, k, row_force_default = (.5, .9, 1, False) if self.orientation == "v" else (.3, 1, .8, True)
            width = self.standardTextWidth
            height = self.standardTextHeight

            report3 = AnchorLayout(anchor_x="center", anchor_y="center")
            b3 = BoxLayout(spacing=self.spacing, padding=self.padding)
            mGrid = GridLayout(rows=12, cols=2, size_hint=(x, y), spacing=self.spacing*2, col_default_width=width,
                                pos_hint={"center_y": .5})

            for i, month in zip(range(12),
                                [self.msg[112], self.msg[113], self.msg[114], self.msg[115], self.msg[116],
                                 self.msg[117], self.msg[118], self.msg[119], self.msg[120], self.msg[121],
                                 self.msg[122], self.msg[123]]): # месяцы года

                mGrid.add_widget(MyLabel(text=month, halign="center", valign="center", width=width, height=height,
                                         text_size=(width, height), pos_hint={"center_y": .5},
                                         color=self.standardTextColor))
                text = str(self.settings[4][i]) if self.settings[4][i] is not None else ""
                font_size = self.fontXS * self.fontScale() if not self.desktop else Window.size[1] / 45
                if self.desktop and font_size > 15: font_size = 15
                if text == "": BGcolor = self.sortButtonBackgroundColor
                elif int(text) < self.settings[0][3]:
                    BGcolor = self.getColorForStatus("5")
                elif int(text) == self.settings[0][3]:
                    if self.theme != "green" and self.theme != "3D": BGcolor = self.titleColor
                    else: BGcolor = self.getColorForStatus("0")
                else:
                    if self.theme == "green" or self.theme == "3D": BGcolor = self.titleColor
                    else: BGcolor = self.getColorForStatus("1")
                monthAmount = MyTextInput(
                    text=text, multiline=False, input_type="number", width=self.standardTextWidth * 1.1,
                    font_size=font_size, background_color=[BGcolor[0], BGcolor[1], BGcolor[2], .4],
                    font_size_force=True, halign="center", valign="center", wired_border=False, size_hint_x=None,
                    size_hint_y=1, height=(height * 1.33 / self.fontScale())
                )
                if self.orientation == "h": monthAmount.padding = (0, 4)
                self.months.append(monthAmount)
                mGrid.add_widget(self.months[i])
                self.analyticsMessage = MyLabel(
                    text=str(self.analyticsMessageCached), markup=True, color=self.standardTextColor, valign="center",
                    text_size=(Window.size[0] / 2, self.mainList.size[1]), height=self.mainList.size[1],
                    font_size=self.fontXS * self.fontScale(cap=1.2), width=Window.size[0] / 2,
                    pos_hint={"center_y": .5}
                )
            b3.add_widget(mGrid)
            b3.add_widget(self.analyticsMessage)
            self.recalcServiceYear(allowSave=False)
            report3.add_widget(b3)
            tab3.content = report3
            self.reportPanel.add_widget(tab3)

        self.mainList.add_widget(self.reportPanel)

        if jumpToPrevMonth: Clock.schedule_once(lambda dt: self.reportPanel.switch_to(tab2), 0)
        else: Clock.schedule_once(lambda dt: self.reportPanel.switch_to(tab1), 0)

        if self.resources[0][1][9] == 0 and self.settings[0][3] == 0: # вы пионер?
            self.resources[0][1][9] = 1
            self.save()
            self.popup("pioneerNorm", message=self.msg[7], options=[self.button["yes"], self.button["no"]])

        self.checkDate()

    def settingsPressed(self, instance=None):
        """ Настройки """

        def __continue(*args):
            self.func = self.settingsPressed
            if self.confirmNonSave(instance): return
            self.displayed.form = "set"
            self.stack = list(dict.fromkeys(self.stack))
            self.updateMainMenuButtons(deactivateAll=True)
            self.clearTable()
            self.mainList.clear_widgets()
            box = BoxLayout(orientation="vertical")
            self.settingsPanel = TabbedPanel(background_color=self.globalBGColor, background_image="")
            self.createMultipleInputBox(
                form=box,
                title="",
                options=[
                    self.msg[124],        # норма часов
                    "<>" + self.msg[127], # цвет отказа
                    "{}" + self.msg[40],  # таймер
                    "{}" + self.msg[130], # уведомление при таймере
                    "{}" + self.msg[129], # служение по телефону
                    "{}" + self.msg[205] % self.msg[206], # нет дома
                    "{}" + self.msg[128], # кредит часов
                    "{}" + (self.msg[87] if not self.desktop else self.msg[164]), # новое предложение с заглавной / запоминать положение окна
                   f"[]{icon('icon-language')} {self.msg[131]}", # язык  = togglebutton
                    "[]" + self.msg[241], # размер кнопки
                    "[]" + self.msg[315], # карты
                    "[]" + self.msg[168]  # тема
                ],
                defaults=[
                    self.settings[0][3],   # норма часов
                    self.settings[0][18],  # цвет отказа
                    self.settings[0][22],  # таймер
                    self.settings[0][0],   # уведомление при таймере
                    self.settings[0][20],  # служение по телефону
                    self.settings[0][13],  # нет дома
                    self.settings[0][2],   # кредит часов
                    self.settings[0][11] if not self.desktop else self.settings[0][12], # новое предложение с заглавной / запоминать положение окна
                    self.settings[0][6],   # язык
                    self.settings[0][21],  # карты
                    self.settings[0][8],   # размер кнопки
                    self.settings[0][5],   # тема
                ],
                multilines=[False, False, False, False, False, False, False, False, False, False, False, False]
            )

            """ Также заняты настройки:
            self.settings[0][1] - позиция подъезда в окне
            self.settings[0][4] - сортировка контактов
            self.settings[0][7] - запомненный тип участка при создании
            self.settings[0][9] - значения первой и последней квартиры и количества этажей в новом подъезде
            self.settings[0][10] - кол-во колонок в таблице квартир                
            """

            # Первая вкладка: настройки

            tab1 = TTab(text=self.msg[52])
            tab1.content = box
            self.settingsPanel.add_widget(tab1)

            # Вторая вкладка: работа с данными

            tab2 = TTab(text=self.msg[54])
            g = GridLayout(rows=5, cols=2, spacing=self.spacing, padding=(self.padding*2, 0))
            sp, cap = self.spacing, 1.2 if self.language != "hy" else 1
            ratio0 = .57 if self.orientation == "v" else .75
            ratio1 = .43 if self.orientation == "v" else .25
            size_hint_y = 1
            padding = (0, self.padding*3)
            g.cols_minimum = {0: (self.mainList.size[0]-self.padding*4-self.spacing*4)*ratio0,
                              1: (self.mainList.size[0]-self.padding*4-self.spacing*4)*ratio1}
            text_size = [g.cols_minimum[0]-self.padding*5, None]

            exportBox = BoxLayout(orientation="vertical", padding=padding, spacing=sp) # Сохранить
            if self.theme != "3D":
                exportEmail = RoundButton(text = f"{self.button['floppy']}\n{self.msg[5]}", size_hint_y=size_hint_y)
            else:
                exportEmail = RetroButton(text=f"{self.button['floppy']}\n{self.msg[5]}", size_hint_y=size_hint_y)
            def __export(instance):
                self.share(file=True)
            exportEmail.bind(on_release=__export)
            g.add_widget(MyLabel(text=self.msg[318], text_size=text_size, valign="top", halign="center",
                                 font_size=self.fontXS * self.fontScale(cap=cap)))
            exportBox.add_widget(exportEmail)
            g.add_widget(exportBox)

            openFileBox = BoxLayout(orientation="vertical", padding=padding, spacing=sp) # Открыть
            if self.theme != "3D":
                openFile = RoundButton(text=f"{self.button['open']}\n{self.msg[134]}", size_hint_y=size_hint_y)
            else:
                openFile = RetroButton(text=f"{self.button['open']}\n{self.msg[134]}", size_hint_y=size_hint_y)
            def __open(instance):
                if self.desktop:
                    from tkinter import filedialog
                    file = filedialog.askopenfilename()
                    if file != "" and len(file) > 0: self.importDB(file=file)
                elif platform == "android":
                    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
                    Chooser(self.chooser_callback).choose_content("text/*")
            openFile.bind(on_release=__open)
            g.add_widget(MyLabel(text=self.msg[317], text_size=text_size, halign="center",
                                 font_size=self.fontXS * self.fontScale(cap=cap)))
            openFileBox.add_widget(openFile)
            g.add_widget(openFileBox)

            restoreBox = BoxLayout(orientation="vertical", padding=padding, spacing=sp) # Восстановление
            if self.theme != "3D":
                restoreBtn = RoundButton(text=f"{self.button['restore']}\n{self.msg[135]}", size_hint_y=size_hint_y)
            else:
                restoreBtn = RetroButton(text=f"{self.button['restore']}\n{self.msg[135]}", size_hint_y=size_hint_y)
            def __restore(instance):
                self.popup("restoreBackup")
            restoreBtn.bind(on_release=__restore)
            g.add_widget(MyLabel(text=self.msg[319], text_size=text_size, halign="center",
                                 font_size=self.fontXS * self.fontScale(cap=cap)))
            restoreBox.add_widget(restoreBtn)
            g.add_widget(restoreBox)

            clearBox = BoxLayout(orientation="vertical", padding=padding, spacing=sp) # Очистка
            if self.theme != "3D":
                clearBtn = RoundButton(text=f"{self.button['trash']}\n{self.msg[136]}", size_hint_y=size_hint_y)
            else:
                clearBtn = RetroButton(text=f"{self.button['trash']}\n{self.msg[136]}", size_hint_y=size_hint_y)
            def __clear(instance):
                self.popup("clearData", message=self.msg[138], options=[self.button["yes"], self.button["no"]])
            clearBtn.bind(on_release=__clear)
            g.add_widget(MyLabel(text=self.msg[320], text_size=text_size, font_size=self.fontXS * self.fontScale(cap=cap),
                                 halign="center"))
            clearBox.add_widget(clearBtn)
            g.add_widget(clearBox)

            tab2.content = g
            self.settingsPanel.add_widget(tab2)

            # Третья вкладка: блокнот

            tab4 = TTab(text=self.msg[55])
            a4 = AnchorLayout(anchor_x="center", anchor_y="center")

            self.backButton.disabled = False
            self.detailsButton.text = ""
            self.detailsButton.disabled = True
            self.createInputBox(
                form=a4,
                default=self.resources[0][0],
                multiline=True,
                details=f"{self.button['help']} {self.msg[144]}",
                hint=self.msg[145]
            )
            tab4.content = a4
            self.settingsPanel.add_widget(tab4)

            # Четвертая вкладка: о программе

            tab3 = TTab(text=self.msg[139])
            a = AnchorLayout(anchor_x="center", anchor_y="center")
            linkColor = get_hex_from_color(self.linkColor)

            if platform == "android":
                from kvdroid.tools.deviceinfo import device_info
                if device_info("manufacturer").lower() == "huawei":
                    store = [ # текст и адрес ссылки на магазин (AppGallery)
                        f"\n\n{self.msg[218]}\n[ref=store][color={linkColor}]{icon('icon-huawei')} [u]Huawei AppGallery[/u][/color][/ref]",
                        "https://appgallery.huawei.com/app/C107628637"
                    ]
                else:
                    store = [ # (Play Store)
                        f"\n\n{self.msg[218]}\n[ref=store][color={linkColor}]{icon('icon-googleplay')} [u]{'Google Play Маркет' if self.language == 'ru' else 'Google Play Store'}[/u][/color][/ref]",
                        "https://play.google.com/store/apps/details?id=org.rocketministry"
                    ]
            else:
                store = "", ""

            aboutBtn = MyLabel(text=
                               f"[color={self.titleColor2}][b]Rocket Ministry {Version}[/b][/color]\n\n" + \
                               f"[i]{self.msg[140]}[/i]\n\n" + \
                               f"{self.msg[141]}\n[ref=web][color={linkColor}]{icon('icon-github')} [u]Github[/u][/color][/ref]\n\n" + \
                               f"{self.msg[142]}\n[ref=email][color={linkColor}]{icon('icon-envelope')} [u]inoblogger@gmail.com[/u][/color][/ref]" + \
                               store[0] + \
                               f"\n\n[i][size={12 if self.desktop else 23}]Kivy v{__version__}[/size][/i]",
                               markup=True, halign="center", valign="center", color=self.standardTextColor,
                               text_size=[self.mainList.size[0] * .8, None]
            )

            def __click(instance, value):
                if value == "web":
                    if self.language == "ru":   webbrowser.open("https://github.com/antorix/rocket-ministry/wiki/ru")
                    else:                       webbrowser.open("https://github.com/antorix/rocket-ministry/")
                elif value == "email":          webbrowser.open("mailto:inoblogger@gmail.com?subject=Rocket Ministry")
                elif value == "store":          webbrowser.open(store[1])
            aboutBtn.bind(on_ref_press=__click)

            a.add_widget(aboutBtn)
            tab3.content = a
            self.settingsPanel.add_widget(tab3)
            self.settingsPanel.do_default_tab = False
            self.mainList.add_widget(self.settingsPanel)
            self.checkDate()
            self.hidePositiveButton()

        self.showProgress()
        Clock.schedule_once(__continue, 0)

    def phoneCall(self, instance):
        """ Телефонный звонок """
        if "PopupButton" in str(instance):
            tempFlat = self.flat
            self.house.statsCached = None
            self.flat.editPhone(self.quickPhone.text)
            self.save()
            self.quickPhone.keyboard_on_key_up()
            if self.porch.clearCache("т") or self.porch.clearCache("с"): self.porchView(instance=instance)
            else: self.clickedInstance.update(self.flat)
            self.flat = tempFlat
        if platform == "android":
            try: plyer.call.makecall(tel=self.flat.phone)
            except: request_permissions([Permission.CALL_PHONE])
        elif self.desktop:
            Clipboard.copy(self.flat.phone)
            self.popup(message=self.msg[28] % self.flat.phone)

    def chooser_callback(self, uri_list):
        """ Копируем файл, выбранный пользователем, в Private Storage """
        for uri in uri_list:
            self.openedFile = SharedStorage().copy_from_shared(uri)
        self.loadShared()

    def generateFlatTitle(self):
        """ Создаем flatTitle (для унификации - может вызываться из разных мест) """
        number = "" if self.flat.number == "virtual" else self.flat.number
        flatPrefix = f"{self.msg[214]} " if "подъезд" in self.porch.type else ""
        self.flatTitle = f"[b]{flatPrefix}{number}[/b] {self.flat.getName()}".strip()
        self.flatTitleNoFormatting = f"{flatPrefix}{number} {self.flat.getName()}".strip()

    def updateSettings(self):
        """ Перезагрузка интерфейса после сохранения некоторых настроек """
        self.restart("soft")
        if not self.settings[0][22]: self.rep.modify(")")
        for house in self.houses:
            for porch in house.porches: porch.scrollview = porch.floorview = None
        Clock.schedule_once(self.settingsPressed, 0)

    def searchPressed(self, instance=None):
        """ Нажата кнопка поиск """
        self.func = self.searchPressed
        if self.confirmNonSave(instance): return
        self.clearTable()
        self.displayed.form = "search"
        self.createInputBox(
            title=f"[b]{self.msg[146]}[/b]",
            message=self.msg[147],
            multiline=False,
            positive=f"{self.button['search2']} [b]{self.msg[148]}[/b]",
            details="",
            tip=self.msg[323],
            focus=True
        )
        self.updateMainMenuButtons(deactivateAll=True)

    def find(self, instance=None):
        """ Выдача результатов поиска """
        self.contactsEntryPoint = 0
        allContacts = self.getContacts(forSearch=True)
        self.searchResults = []
        for con in allContacts: # start search in flats/contacts
            found = False
            if self.searchQuery in con[2].lower() or self.searchQuery in con[2].lower() or self.searchQuery in \
                    con[3].lower() or self.searchQuery in con[8].lower() or self.searchQuery in \
                    con[10].lower() or self.searchQuery in con[11].lower() or self.searchQuery in \
                    con[12].lower() or self.searchQuery in con[13].lower() or\
                    self.searchQuery in con[9].lower():
                found = True

            if con[8] != "virtual":
                for r in range(len(self.houses[con[7][0]].porches[con[7][1]].flats[
                                       con[7][2]].records)):  # in records in flats
                    if self.searchQuery in self.houses[con[7][0]].porches[con[7][1]].flats[
                        con[7][2]].records[r].title.lower():
                        found = True
                    if self.searchQuery in self.houses[con[7][0]].porches[con[7][1]].flats[
                        con[7][2]].records[r].date.lower():
                        found = True
            else:
                for r in range(len(self.resources[1][con[7][0]].porches[0].flats[0].records)): # in records in contacts
                    if self.searchQuery in self.resources[1][con[7][0]].porches[0].flats[0].records[
                        r].title.lower():
                        found = True
                    if self.searchQuery in self.resources[1][con[7][0]].porches[0].flats[0].records[
                        r].date.lower():
                        found = True

            if found: self.searchResults.append([con[7], con[8], con[2]])

        options = []
        for res, i in zip(self.searchResults, range(len(self.searchResults))):  # save results
            number = "%d) " % (i + 1)
            if res[1] != "virtual":  # for regular flats
                if self.houses[res[0][0]].getPorchType()[0] == "подъезд":
                    options.append(
                        f"%s%s–%s" % (number, self.houses[res[0][0]].title,
                                      self.houses[res[0][0]].porches[res[0][1]].flats[res[0][2]].title))
                else:
                    porch = self.houses[res[0][0]].porches[res[0][1]].title
                    porchLabel = f"{porch}, " if not self.invisiblePorchName in porch else ""
                    options.append(
                        f"%s%s, %s%s" % (number, self.houses[res[0][0]].title, porchLabel,
                                         self.houses[res[0][0]].porches[res[0][1]].flats[res[0][2]].title)
                    )
            else: # for standalone contacts
                title = "" if self.resources[1][res[0][0]].title=="" else self.resources[1][res[0][0]].title + ", "
                options.append(
                    f"%s%s%s" % (number, title, self.resources[1][res[0][0]].porches[0].flats[0].title))

        if len(options) == 0: options.append(self.msg[149])

        self.displayed.update(
            form="search",
            title=f"[b]{self.msg[150]}[/b]" % self.searchQuery,
            message=self.msg[151],
            options=options,
            jump=self.clickedBtnIndex,
            positive=""
        )
        self.stack.insert(0, "search")
        self.updateList(instance=instance, progress=True)

    # Экраны иерархии участка

    def houseView(self, instance=None, jump=None):
        """ Вид участка - список подъездов """
        if "virtual" in self.house.type: # страховка от захода в виртуальный дом
            if self.contactsEntryPoint: self.conPressed(instance=instance)
            elif self.searchEntryPoint: self.find(instance=instance)
            return
        elif self.house.noSegment(): # от захода в подъезд бессегментного участка
            self.porch = self.house.porches[0]
            self.porchView(instance=instance)
            return
        self.updateMainMenuButtons()
        note = self.house.note if self.house.note != "" else None
        self.mainListsize1 = self.mainList.size[1]
        self.dest = self.house.title

        self.displayed.update(
            form="houseView",
            title=f"[b]{self.house.title}[/b]",
            nav=self.button['nav'] if self.house.type == "condo" else None,
            options=self.house.showPorches(),
            sort=self.button["sort"] if len(self.house.porches) > 0 else None,
            positive=f"{self.button['plus']} {self.msg[77 if self.house.type == 'condo' else 78]}",
            jump=self.house.porches.index(self.porch) if jump is None and self.porch is not None and \
                                                         self.porch in self.house.porches else jump,
            tip=[note, "header"]
        )
        self.stack = ['houseView', 'ter']
        self.updateList(instance=instance, progress=True if len(self.house.porches) > 5 and not self.house.due() else False)

    def porchView(self, instance, update=True):
        """ Вид подъезда - список квартир или этажей """
        self.blockFirstCall = 0
        self.exitToPorch = False
        floors = self.porch.floors()
        segment = f" {self.button['arrow']} {self.msg[157]} {self.porch.title}" if "подъезд" in self.porch.type else f" {self.button['arrow']} {self.porch.title}"

        if self.house.type != "condo" or len(self.porch.flats) == 0: neutral = ""
        elif floors: neutral = self.button['fgrid']
        elif not "подъезд" in self.porch.type: neutral = ""
        else: neutral = self.button['flist']

        if floors:
            tip = None
            sort = None
        else:
            note = self.porch.note if not self.house.noSegment() else self.house.note
            tip = [note if note != "" else None, "header"]
            sort = self.button["sort"]

        if not self.house.listType():
            positive = f"{self.button['edit']} {self.msg[155]}" if self.house.type == "condo" else f"{self.button['plus']} {self.msg[156]}"
        else:
            positive = f"{self.button['plus']} {self.msg[188]}"

        self.displayed.update(
            title=f"[b]{self.house.title} {(segment if not self.house.noSegment() else '')}[/b]",
            options=self.porch.showFlats(),
            form="porchView",
            sort=sort if len(self.porch.flats) > 0 else None,
            nav=self.numberToIcon(str(self.settings[0][10])) if not floors and len(self.porch.flats) > 0 else None,
            positive=positive,
            neutral=neutral,
            jump=self.porch.flats.index(self.flat) if self.flat is not None and self.flat in self.porch.flats else None,
            tip=tip
        )
        self.stack = ['porchView', 'houseView', 'ter']

        if len(self.porch.flats) < 20: progress = False # в подъезде показываем прогресс только при перемонтировке виджетов
        elif self.porch.floors() and self.porch.floorview is not None: progress = False
        elif not self.porch.floors() and self.porch.scrollview is not None: progress = False
        else: progress = True

        if update or self.porch.floorview is None: self.updateList(instance=instance, progress=progress)
        # после удаления или восстановления квартиры не перемонтируем всю таблицу, а только обновляем кнопки
        else:
            f = len(self.porch.flats) - 1
            for button in self.porch.floorview.children:
                if "FlatButtonSquare" in str(button):
                    button.update(flat=self.porch.flats[f])
                    f -= 1
        if len(self.porch.flats) == 0 and self.house.type == "condo":
            # если нет квартир, сразу форма создания
            self.positivePressed(instant=True)
        self.updateMainMenuButtons()

    def flatView(self, instance, call=True):
        """ Вид квартиры - список записей посещения """
        self.updateMainMenuButtons()
        self.clickedInstance = instance
        self.cacheFreeModeGridPosition()
        self.generateFlatTitle()

        if self.house.listType(): self.dest = self.flat.number
        elif self.house.type == "private":
            if self.house.noSegment(): self.dest = f"{self.house.title}, {self.flat.number}"
            else: self.dest = f"{self.porch.title}, {self.flat.number}"
        else:
            self.dest = self.house.title
            if self.language == "ru" and \
                    (self.settings[0][21] == "Yandex" or self.settings[0][21] == "Яндекс" or \
                     self.settings[0][21] == "2GIS" or self.settings[0][21] == "2ГИС"):
                # для русского языка и Яндекс/2ГИС добавляем поиск по подъезду
                self.dest += f" {self.msg[212]} {self.porch.title}"

        if self.flat.number == "virtual" or self.contactsEntryPoint: self.flatType = f" {self.msg[158]}"
        elif self.house.type == "condo":
            self.flatType = f" Apart." if self.language == "es" and self.fontScale() > 1.2 else f" {self.msg[159]}"
        else: self.flatType = f" {self.msg[57]}"
        note = self.flat.note if self.flat.note != "" else None
        nav = self.button['nav0'] if self.flat.number == "virtual" and self.house.title == "" else self.button['nav']

        self.displayed.update(
            title=self.flatTitle,
            message=self.msg[160],
            options=self.flat.showRecords(),
            form="flatView",
            details=f"{self.button['user']} {self.msg[204]}",
            nav=nav,
            positive=f"{self.button['plus']} {self.msg[161]}",
            neutral=self.button["phone"] if self.flat.phone == "" else self.button["phone-square"],
            jump=self.flat.records.index(self.record) if self.record is not None and \
                                                         self.record in self.flat.records else None,
            tip=[note, "header"]
        )

        if not call and len(self.flat.records) == 0: # всплывающее окно первого посещения
            self.createFirstCallPopup(instance=instance)

        else:
            self.stack = ["flatView"]
            if self.contactsEntryPoint: self.stack.append("con")
            elif self.searchEntryPoint: self.stack.append("search")
            else: self.stack.append("porchView")
            if len(self.flat.records) == 0: # форма первого посещения
                self.scrollWidget.clear_widgets()
                self.firstCallPopup = False
                self.createMultipleInputBox(
                    title=f"{self.flatTitle} {self.button['arrow']} {self.msg[162]}",
                    options=[self.msg[22], self.msg[125]],
                    defaults=[self.flat.getName(), ""],
                    multilines=[False, True],
                    disabled=[False, False],
                    details=f"{self.button['user']} {self.msg[204]}",
                    neutral=self.button["phone"] if self.flat.phone == "" else self.button["phone-square"],
                    nav=nav,
                    sort="",
                    note=note
                )
            else:
                self.updateList(instance=instance)

            # Кнопки первичного цвета (статуса)

            if self.house.type != "virtual" and not self.contactsEntryPoint and not self.popupEntryPoint:
                if self.resources[0][1][7] == 0 and len(self.flat.records) == 0 and instance is not None: # показываем подсказку о первом посещении
                    self.popup(title=self.msg[247], message=self.msg[228])
                    self.mainList.add_widget(self.tip(icon="info", text=self.msg[106], k=.7, halign="center",
                                                      valign="bottom", hint_y=.15))
                self.colorBtn = []
                self.activateColorButton()
                self.colorBox = BoxLayout(size_hint=(1, .163), spacing=self.spacing*2, padding=self.padding*2)
                self.colorBox.add_widget(self.colorBtn[1])
                self.colorBox.add_widget(self.colorBtn[2])
                self.colorBox.add_widget(self.colorBtn[3])
                self.colorBox.add_widget(self.colorBtn[4])
                self.colorBox.add_widget(self.colorBtn[0])
                self.colorBox.add_widget(self.colorBtn[5])
                self.colorBox.add_widget(self.colorBtn[6])
                self.mainList.add_widget(self.colorBox)
                if len(self.flat.records) == 0:
                    self.colorBox.padding = self.padding * 2
                    self.hidePositiveButton()
                else:
                    self.colorBox.padding = self.padding * 2, self.padding * 2, self.padding * 2, 0

            # Круглые кнопки слева (снизу вверх)

            pos = [self.padding*2 if self.orientation == "v" else self.horizontalOffset + self.padding*2,
                   self.mainList.size[1] * .35 - (0 if self.orientation == "v" else Window.size[1] * .06)]
            if len(self.flat.records) == 0: pos[1] *= .75
            side = self.standardTextHeightUncorrected * 1.5
            gap = self.standardTextHeightUncorrected * 2
            font_size = self.fontXXL * .9 # размер шрифта

            if not self.contactsEntryPoint and not self.searchEntryPoint: # доп. цвет
                if len(self.flat.records) == 0 and self.resources[0][1][7] == 0:
                    pos[1] *= 1.3
                    self.resources[0][1][7] = 1
                    self.save()
                color2Selector = RoundColorButton(color=self.getColor2(self.flat.color2), pos=pos, side=side)
                def __color2Click(instance):
                    current = self.color2List.index(color2Selector.color)
                    if current == len(self.color2List) - 1: current = 0
                    else: current += 1
                    color2Selector.color = self.getColor2(current)
                    self.flat.color2 = current
                    self.save()
                color2Selector.bind(on_release=__color2Click)
                self.floaterBox.add_widget(color2Selector)

            pos2 = pos[0], pos[1] + gap  # смайлик
            emoji = self.flat.emoji if self.flat.emoji != "" else self.button["add_emoji"]

            if self.theme != "3D":
                self.emojiSelector = FloatButton(text=emoji, font_size=font_size, pos=pos2, size=(side, side))
            else:
                self.emojiSelector = RetroButton(text=emoji, width=self.standardTextHeight*1.5, pos=pos2,
                                                 font_size=font_size, height=side, size_hint_x=None, size_hint_y=None,
                                                 color=self.topButtonColor if emoji == self.button["add_emoji"] else self.linkColor,
                                                 alpha=self.floatButtonAlpha, halign="center", valign="center")
            self.emojiSelector.bind(on_release=self.createEmojiPopup)
            self.floaterBox.add_widget(self.emojiSelector)

    def logEntryView(self, id):
        """ Просмотр и редактирование записи журнала """
        self.displayed.form = "logEntryView"
        self.entryID = id
        self.entryDate, self.entryBody, self.entryTag = self.getLog(self.entryID)
        self.createInputBox(
            title=f"[b]{self.entryDate}[/b]",
            message=f"[i]{self.entryBody}[/i]\n\n{self.msg[333]}{self.col}",
            default=self.entryTag,
            tip=self.msg[330],
            multiline=False,
            bin=True if self.entryBody == "" else False
        )

    def activateColorButton(self):
        """ Определяем, какая кнопка выбора цвета в квартире должна иметь точку """
        for i, status in zip(range(7), ["0", "1", "2", "3", "4", "5", ""]):
            self.colorBtn.append(ColorStatusButton(status))
            if status == self.flat.getStatus()[0][1]:
                self.colorBtn[i].text = self.button["dot"]

    def recordView(self, instance=None, focus=False):
        self.displayed.form = "recordView"
        self.createInputBox(
            title = f"{self.flatTitle} {self.button['arrow']} {self.record.date}",
            message = self.msg[125],
            default = self.record.title,
            multiline=True,
            details=f"{self.button['user']} {self.msg[204]}",
            neutral=self.button["phone"] if self.flat.phone == "" else self.button["phone-square"],
            bin=True,
            focus=focus
        )

    # Диалоговые окна

    def createInputBox(self, title="", form=None, message="", default="", hint="", checkbox=None, handleCheckbox=None,
                       active=True, input=True, positive=None, sort=None, details=None, neutral=None, multiline=False,
                       tip=None, embed=None, embed2=None, link=None, limit=99999, focus=False, bin=False):
        """ Форма ввода данных с одним полем """
        if len(self.stack) > 0: self.stack.insert(0, self.stack[0])
        if form is None: form = self.mainList
        form.padding = 0
        form.clear_widgets()
        self.floaterBox.clear_widgets()
        self.removeScrollButtons()
        self.restorePositiveButton()
        self.backButton.disabled = False
        if title is not None: self.pageTitle.text = f"[ref=title]{title}[/ref]"
        self.positive.disabled = False
        self.positive.text = positive if positive is not None else self.button["save"]
        if neutral is not None:
            self.neutral.text = neutral
            self.neutral.disabled = False
            if self.neutral.text == self.button['phone'] and self.flat.phone == "":
                self.neutral.text = self.button['phone0']
                self.neutral.disabled = True
        if sort == "":
            self.sortButton.text = sort
            self.sortButton.disabled = True
        elif sort is not None:
            self.sortButton.text = sort
            self.sortButton.disabled = False
        if details == "":
            self.detailsButton.text = details
            self.detailsButton.disabled = True
        elif details is not None:
            self.detailsButton.text = details
            self.detailsButton.disabled = False

        pos_hint = {"top": 1}
        grid = GridLayout(rows=2, cols=1, spacing=self.spacing,
                          padding=(self.padding*2, self.padding*2, self.padding*2, 0))

        if message != "":
            self.inputBoxText = MyLabel(text=message, valign="center", size_hint_y=.6 * self.fontScale(),
                                        halign="center", font_size = self.fontS * self.fontScale(),
                                        text_size=(Window.size[0]*.9, None))
            grid.add_widget(self.inputBoxText)

        if input:
            textbox = BoxLayout(spacing=self.spacing*2)
            size_hint_y = None if not multiline else .62#1
            self.inputBoxEntry = MyTextInput(multiline=multiline, hint_text=hint, size_hint_y=size_hint_y, limit=limit,
                                             height=self.standardTextHeightUncorrected*self.enlargedTextCo,
                                             rounded=True if not multiline else False, text=default, focus=focus,
                                             pos_hint=pos_hint)
            textbox.add_widget(self.inputBoxEntry)
            grid.add_widget(textbox)

        if checkbox is not None: # если заказана галочка, добавляем
            grid.rows += 1
            if self.displayed.form == "createNewFlat": # чтобы это увидела внешняя функция
                self.textbox = textbox
                self.multiline = multiline
                self.pos_hint = pos_hint
                self.hint = hint
            self.checkbox = FontCheckBox(active=active, text=checkbox, button_size=self.fontM,
                                         font_size=self.fontS * self.fontScale())
            self.checkbox.bind(on_press=handleCheckbox)
            grid.add_widget(self.checkbox)

        if not multiline or checkbox is not None: # увеличиваем шрифт в одиночных полях ввода
            textbox.padding = self.padding * 4, 0
            self.inputBoxEntry.halign = "center"
            if not self.desktop:
                self.inputBoxEntry.height *= self.enlargedTextCo
                self.inputBoxEntry.font_size = self.fontBigEntry

        if tip is not None or link is not None: # добавление подсказки или ссылки (нельзя одновременно)
            extra = self.tip(tip) if tip is not None else self.tip(icon="link", text=link[0], func=link[1])
            grid.rows += 3
            if multiline: grid.add_widget(Widget())
            grid.add_widget(extra)
            grid.add_widget(Widget())

        elif embed is not None: # добавление интеграции (+ второй интеграции, если есть)
            grid.rows += 2
            grid.add_widget(embed)
            grid.add_widget(embed2 if embed2 is not None else Widget())
            self.inputBoxText.size_hint_y = .5

        elif message != "":
            self.inputBoxText.size_hint_y = .2 # поиск и детали посещения
            if checkbox is not None: # добавление домов
                grid.rows += 1
                grid.add_widget(Widget())

        form.add_widget(grid)

        if bin: # прокручивание текста до конца и добавление корзины
            Clock.schedule_once(lambda x: self.inputBoxEntry.do_cursor_movement(action="cursor_pgup", control="cursor_home"), 0)
            lowGrid = GridLayout(cols=3, size_hint=(1, .45))
            form.add_widget(lowGrid)
            pad = self.padding * 4
            a1 = AnchorLayout(anchor_y="center", anchor_x="left", padding=pad)
            a2 = AnchorLayout(anchor_y="center", anchor_x="center", padding=pad)
            a3 = AnchorLayout(anchor_y="center", anchor_x="right", size_hint=(1, 1), padding=pad)
            lowGrid.add_widget(a1)
            lowGrid.add_widget(a2)
            lowGrid.add_widget(a3)
            a3.add_widget(self.bin())
            if multiline: self.inputBoxEntry.size_hint_y = 1

    def removeScrollButtons(self):
        """ Удаляем кнопки прокрутки списка на экране настроек """
        for widget in self.floaterBox.children:
            if "BoxLayout" in str(widget):
                self.floaterBox.remove_widget(widget)
                break

    def createMultipleInputBox(self, form=None, title=None, options=[], defaults=[], multilines=[], disabled=[],
                               sort=None, details=None, note=None, neutral=None, nav=None):
        """ Форма ввода данных с несколькими полями """
        if form is None: form = self.mainList
        form.clear_widgets()
        self.backButton.disabled = False
        self.positive.text = self.button["save"]
        self.positive.disabled = False
        self.detailsButton.disabled = True
        self.firstCallPopup = False
        self.restorePositiveButton()
        self.removeScrollButtons()
        self.floaterBox.clear_widgets()
        if self.displayed.form != "flatDetails": self.floaterBox.clear_widgets()
        self.navButton.disabled = True
        self.navButton.text = ""
        if title is not None: self.pageTitle.text = f"[ref=title]{title}[/ref]"
        if neutral == "":
            self.neutral.text = neutral
            self.neutral.disabled = True
        elif neutral is not None:
            self.neutral.disabled = False
            self.neutral.text = neutral
            if self.neutral.text == self.button['phone'] and self.flat.phone == "":
                self.neutral.text = self.button['phone0']
                self.neutral.disabled = True
        if sort == "":
            self.sortButton.text = sort
            self.sortButton.disabled = True
        elif sort is not None:
            self.sortButton.text = sort
            self.sortButton.disabled = False
        if details is not None:
            self.detailsButton.text = details
            self.detailsButton.disabled = False
        if nav == self.button['nav0']:
            self.navButton.text = nav
            self.navButton.disabled = True
        elif nav is not None:
            self.navButton.text = nav
            self.navButton.disabled = False
        if note is not None:
            if self.displayed.form != "flatView":
                self.mainList.add_widget(self.tip(note, icon="note"))
            else:
                self.mainList.add_widget(self.tip(note, icon="header"))

        grid = GridLayout(rows=len(options), cols=2, pos_hint={"top": 1}, padding=self.padding*2)

        self.multipleBoxLabels = []
        self.multipleBoxEntries = []
        checkbox = False

        if len(disabled) < len(defaults):
            for i in range(len(multilines)):
                disabled.append(False)

        for row, default, multiline, disable in zip(range(len(options)), defaults, multilines, disabled):#, saves):
            if self.displayed.form == "set":
                settings = True
                shrink = False
                if str(options[row]) == self.msg[124]:  # поле ввода
                    text = options[row].strip()
                elif "{}" in str(options[row]):  # галочка
                    text = str(options[row][2:]).strip()
                    checkbox = True
                else:  # выпадающий список
                    text = str(options[row][2:]).strip()
                self.settingButtonHintY = .95
                labelSize_hint = (1, 1)
                entrySize_hint = ((.5 if self.orientation == "v" else .3), 1)
                text_size = (Window.size[0] * 0.66 * .95, None)
                font_size = self.fontXS * self.fontScale(cap=1.2)
                halign = "center"

                if self.desktop and self.msg[130] in text:  # не показываем опцию уведомления, если таймер отключен, а также всегда на ПК
                    timerOK = False
                elif self.msg[130] not in text or (self.msg[130] in text and self.settings[0][22] == 1):
                    timerOK = True
                else: timerOK = False
            else:
                settings = False
                shrink = True if self.displayed.form == "flatView" and not self.contactsEntryPoint and not self.searchEntryPoint else False
                grid.spacing = self.spacing * 2
                y = 1 if multiline else None
                text = options[row].strip()
                labelSize_hint = (self.descrColWidth, y)
                entrySize_hint = (1-self.descrColWidth, y)
                text_size = (Window.size[0] * .95 * self.descrColWidth, None)
                font_size = self.fontS * self.fontScale()
                halign = "left"
                timerOK = True

            if settings: limit = 99999  # задаем лимиты символов
            elif multiline: limit = 99999
            else: limit = self.charLimit

            height = self.standardTextHeight

            # инструкции, какие поля разрешено монтировать, а какие нет
            if self.invisiblePorchName in str(default):  # поле "номер/адрес" для виртуальных контактов
                allowMount = False
            #elif self.msg[87] in text:  # временно отключена опция начала предложения с заглавной буквы
            #    allowMount = False
            elif default != "virtual" and timerOK:  # поле сегмента для участков без сегментов
                allowMount = True
            else:
                allowMount = False

            self.multipleBoxLabels.append(MyLabel(text=text, valign="center", halign="center", size_hint=labelSize_hint,
                                                  markup=True, text_size=[text_size[0], None], pos_hint={"top": 0},
                                                  font_size=font_size, color=self.standardTextColor, height=height))

            if allowMount: grid.add_widget(self.multipleBoxLabels[row])

            textbox = BoxLayout(size_hint=entrySize_hint, height=height)

            if self.msg[127] in str(options[row]): self.multipleBoxEntries.append(RejectColorSelectButton())
            elif self.msg[131] in str(options[row]): self.multipleBoxEntries.append(self.languageSelector())
            elif self.msg[241] in str(options[row]): self.multipleBoxEntries.append(self.buttonSizeSelector())
            elif self.msg[315] in str(options[row]): self.multipleBoxEntries.append(self.mapSelector())
            elif self.msg[168] in str(options[row]): self.multipleBoxEntries.append(self.themeSelector())
            elif checkbox == False:
                input_type = "number" if settings or self.msg[17] in self.multipleBoxLabels[row].text\
                    else "text"
                self.multipleBoxEntries.append(
                    MyTextInput(
                        text=str(default) if default != "virtual" else "", halign=halign, multiline=multiline,
                        size_hint_x=entrySize_hint[0], size_hint_y=entrySize_hint[1] if multiline else None,
                        limit=limit, input_type=input_type, disabled=disable, shrink=shrink,
                        height=(self.standardTextHeight*self.enlargedTextCo) if settings else height
                    )
                )
            else:
                self.multipleBoxEntries.append(
                    FontCheckBox(active=default, size_hint=(entrySize_hint[0], entrySize_hint[1]),
                                 setting=self.multipleBoxLabels[row].text,
                                 icon="toggle", button_size=self.fontXL,
                                 button_color=self.linkColor if self.mode == "light" else self.titleColor))

            if self.displayed.form == "houseDetails" and\
                    self.multipleBoxLabels[row].text == self.msg[17]:  # добавляем кнопку календаря в настройки участка
                if self.theme != "3D":
                    calButton = RoundButton(text=self.button["calendar"],
                                            size_hint_x=.2 if self.orientation == "v" else .1)
                else:
                    calButton = RetroButton(text=self.button["calendar"],
                                            size_hint_x=.2 if self.orientation == "v" else .1)
                calButton.bind(on_release=lambda x: self.popup("showDatePicker"))
                textbox.add_widget(self.multipleBoxEntries[row])
                textbox.add_widget(calButton)
                textbox.spacing = self.spacing
                grid.add_widget(textbox)
            elif allowMount:
                textbox.add_widget(self.multipleBoxEntries[row])
                grid.add_widget(textbox)

            if self.displayed.form == "flatView" and self.multipleBoxLabels[row].text == self.msg[22]:  # добавляем кнопки М и Ж
                if self.desktop:
                    textbox2 = BoxLayout(orientation="vertical", size_hint=entrySize_hint, spacing=self.spacing,
                                         height=height+self.standardTextHeightUncorrected*1.3)
                    mfBox = BoxLayout(spacing=self.spacing, size_hint_x=.5)
                else:
                    textbox2 = BoxLayout(orientation="vertical", size_hint=entrySize_hint, height=height*3)
                    mfBox = BoxLayout(spacing=self.spacing*2, size_hint_x=.5)
                grid.remove_widget(textbox)
                textbox.size_hint = 1, 1
                textbox.padding = 0
                self.multipleBoxEntries[row].height = self.standardTextHeight*self.enlargedTextCo
                self.multipleBoxEntries[row].padding[1] = self.multipleBoxEntries[row].height * .25
                textbox2.add_widget(textbox)
                self.row = row
                self.maleMenu = DropDown()
                if self.theme != "3D":
                    self.maleButton = RoundButton(text=self.button['male'], size_hint_y=1)
                else:
                    self.maleButton = RetroButton(text=self.button['male'],  size_hint_y=1)
                self.maleButton.bind(on_press=self.maleButtonPressed)
                self.femaleMenu = DropDown()
                if self.theme != "3D":
                    self.femaleButton = RoundButton(text=self.button['female'], size_hint_y=1)
                else:
                    self.femaleButton = RetroButton(text=self.button['female'], size_hint_y=1)
                self.femaleButton.bind(on_press=self.femaleButtonPressed)
                mfBox.add_widget(self.maleButton)
                mfBox.add_widget(self.femaleButton)
                textbox2.add_widget(mfBox)
                self.multipleBoxLabels[0].height = textbox2.height
                self.multipleBoxLabels[0].text_size[1] = self.multipleBoxLabels[0].height
                grid.add_widget(textbox2)
                grid.rows += 1
                grid.add_widget(Widget(size_hint=labelSize_hint, height=self.standardTextHeightUncorrected*.4))
                grid.add_widget(Widget(size_hint=entrySize_hint, height=self.standardTextHeightUncorrected*.4))

        form.add_widget(grid)

        if self.displayed.form == "flatView" and len(self.flat.records) == 0:
            grid.padding = (self.padding*2, self.padding*2, self.padding*2, 0)

        elif "Details" in self.displayed.form: # добавление корзины и еще двух ячеек для кнопок
            lowGrid = GridLayout(cols=3, size_hint=(1, .45), pos_hint={"center_x": .5})
            form.add_widget(lowGrid)
            pad = self.padding * 4
            a1 = AnchorLayout(anchor_y="center", anchor_x="left", padding=pad)
            a2 = AnchorLayout(anchor_y="center", anchor_x="center", padding=pad)
            a3 = AnchorLayout(anchor_y="center", anchor_x="right", padding=pad)
            lowGrid.add_widget(a1)
            lowGrid.add_widget(a2)
            lowGrid.add_widget(a3)
            condensedX = .95
            if not "flat" in self.displayed.form: # в участке добавляем кнопку экспорта телефонов
                if self.displayed.form == "houseDetails":
                    if self.settings[0][20]:
                        a1.add_widget(self.exportTer())
                        a2.add_widget(self.exportPhones())
                    else:
                        a2.add_widget(self.exportTer())
                    a3.add_widget(self.bin())
                    lowGrid.size_hint_x = condensedX
                else:
                    a3.add_widget(self.bin())
            else:
                if self.contactsEntryPoint:
                    a2.add_widget(self.bin(f"{self.button['share']}\n{self.msg[76]}"))
                    a3.add_widget(self.bin())
                    lowGrid.size_hint_x = condensedX
                elif self.searchEntryPoint:
                    a3.add_widget(self.bin())
                elif self.house.type == "private":
                    a3.add_widget(self.bin())
                elif self.displayed.form == "flatDetails" and self.porch.floors():
                    a2.add_widget(self.bin(f"{self.button['shrink']}\n{self.msg[217]}"))
                    a3.add_widget(self.bin())
                    lowGrid.size_hint_x = condensedX
                elif not self.porch.floors():
                    a3.add_widget(self.bin())
                else:
                    a3.add_widget(self.bin())

    # Генераторы интерфейсных элементов

    def languageSelector(self):
        """ Выбор языка для настроек """
        a = AnchorLayout()
        self.dropLangMenu = DropDown()
        options = list(self.languages.values())
        for option in options:
            btn = SortListButton(font_name=self.differentFont, text=option[0])
            def __saveLanguage(instance):
                self.dropLangMenu.select(instance.text)
                for i in range(len(self.languages)):  # язык
                    if list(self.languages.values())[i][0] in self.languageButton.text:
                        self.settings[0][6] = list(self.languages.keys())[i]
                        break
                self.save()
                self.updateSettings()
            btn.bind(on_release=__saveLanguage)
            self.dropLangMenu.add_widget(btn)
        if self.theme != "3D":
            self.languageButton = RoundButton(font_name=self.differentFont, text=self.msg[1], size_hint_x=1,
                                              font_size=self.fontXS*self.fontScale(cap=1.2),
                                              size_hint_y=self.settingButtonHintY)
        else:
            self.languageButton = RetroButton(font_name=self.differentFont, text=self.msg[1], size_hint_x=1,
                                              font_size=self.fontXS*self.fontScale(cap=1.2),
                                              size_hint_y=self.settingButtonHintY)
        self.dropLangMenu.bind(on_select=lambda instance, x: setattr(self.languageButton, 'text', x))
        self.languageButton.bind(on_release=self.dropLangMenu.open)
        a.add_widget(self.languageButton)
        return a

    def buttonSizeSelector(self):
        """ Выбор размера кнопок квартир """
        a = AnchorLayout()
        self.dropBSMenu = DropDown()
        for size in range(1, 11):
            btn = SortListButton(text=str(size))
            def __saveSize(instance):
                self.dropBSMenu.select(instance.text)
                self.settings[0][8] = int(instance.text)
                self.save()
            btn.bind(on_release=__saveSize)
            self.dropBSMenu.add_widget(btn)
        if self.theme != "3D":
            self.BSButton = RoundButton(text=str(self.settings[0][8]), size_hint_x=1,
                                        font_size=self.fontXS*self.fontScale(cap=1.2),
                                        size_hint_y=self.settingButtonHintY)
        else:
            self.BSButton = RetroButton(text=str(self.settings[0][8]), size_hint_x=1,
                                        font_size=self.fontXS*self.fontScale(cap=1.2),
                                        size_hint_y=self.settingButtonHintY)
        self.dropBSMenu.bind(on_select=lambda instance, x: setattr(self.BSButton, 'text', x))
        self.BSButton.bind(on_release=self.dropBSMenu.open)
        a.add_widget(self.BSButton)
        return a

    def mapSelector(self):
        """ Выбор карт """
        a = AnchorLayout()
        self.dropMapsMenu = DropDown()
        for map in self.maps:
            btn = SortListButton(text=map)
            def __saveMaps(instance):
                self.dropMapsMenu.select(instance.text)
                self.settings[0][21] = instance.text
                self.save()
            btn.bind(on_release=__saveMaps)
            self.dropMapsMenu.add_widget(btn)
        if len(str(self.settings[0][21]))<3: self.settings[0][21] = "Google"
        if self.theme != "3D":
            self.mapsButton = RoundButton(text=self.settings[0][21], size_hint_x=1,
                                          font_size=self.fontXS*self.fontScale(cap=1.2),
                                          size_hint_y=self.settingButtonHintY)
        else:
            self.mapsButton = RetroButton(text=self.settings[0][21], size_hint_x=1,
                                          font_size=self.fontXS*self.fontScale(cap=1.2),
                                          size_hint_y=self.settingButtonHintY)
        self.dropMapsMenu.bind(on_select=lambda instance, x: setattr(self.mapsButton, 'text', x))
        self.mapsButton.bind(on_release=self.dropMapsMenu.open)
        a.add_widget(self.mapsButton)
        return a

    def themeSelector(self):
        """ Выбор темы для настроек """
        a = AnchorLayout()
        self.dropThemeMenu = DropDown()
        try: currentTheme = list({i for i in self.themes if self.themes[i] == self.theme})[0]
        except: currentTheme = self.msg[306]
        if self.themeOverriden: currentTheme = list({i for i in self.themes if self.themes[i] == self.themeOld})[0]
        options = list(self.themes.keys())
        for option in options:
            btn = SortListButton(text=option)
            def __saveTheme(instance):
                self.dropThemeMenu.select(instance.text)
                self.settings[0][5] = self.themes[instance.text]
                self.save()
                self.updateSettings()
            btn.bind(on_release=__saveTheme)
            self.dropThemeMenu.add_widget(btn)
        if self.theme != "3D":
            self.themeButton = RoundButton(text=currentTheme, size_hint_x=1,
                                           font_size=self.fontXS*self.fontScale(cap=1.2),
                                           size_hint_y=self.settingButtonHintY)
        else:
            self.themeButton = RetroButton(text=currentTheme, size_hint_x=1,
                                           font_size=self.fontXS*self.fontScale(cap=1.2),
                                           size_hint_y=self.settingButtonHintY)
        self.dropThemeMenu.bind(on_select=lambda instance, x: setattr(self.themeButton, 'text', x))
        self.themeButton.bind(on_release=self.dropThemeMenu.open)
        a.add_widget(self.themeButton)
        return a

    def exportTer(self):
        """ Кнопка экспорта участка """
        text = f"{self.button['floppy2']} {self.msg[153]}".replace(" ", "\n")
        w = h = self.mainList.size[0] * .25 if not self.desktop else 90 # размер (сторона квадрата)
        if self.language == "tr":
            w *= 1.1
            h *= 1.1
        if self.theme != "3D":
            btn = RoundButton(text=text, size_hint_x=None, size_hint_y=None, size=(w, h))
        else:
            btn = RetroButton(text=text, size_hint_x=None, size_hint_y=None, size=(w, h))
        def __exportTer(instance):
            for porch in self.house.porches: porch.scrollview = porch.floorview = None
            self.share(file=True, ter=self.house)
        btn.bind(on_release=__exportTer)
        return btn

    def exportPhones(self, includeWithoutNumbers=None):
        """ Кнопка экспорта телефонов участка либо обработка ее нажатия """
        if includeWithoutNumbers is None: # пользователь еще не ответил, создаем выпадающее меню
            text = f"{self.button['share']} {self.msg[154]}".replace(" ", "\n")
            w = h = self.mainList.size[0] * .25 if not self.desktop else 90 # размер (сторона квадрата)
            if self.language == "tr":
                w *= 1.1
                h *= 1.1
            if self.theme != "3D":
                btn = RoundButton(text=text, size_hint_x=None, size_hint_y=None, size=(w, h))
            else:
                btn = RetroButton(text=text, size_hint_x=None, size_hint_y=None, size=(w, h))
            def __exportPhones(instance):
                self.popup("includeWithoutNumbers", message=self.msg[172],
                           options=[self.button["yes"], self.button["no"]])
            btn.bind(on_release=__exportPhones)
            return btn

        else: # пользователь ответил на вопрос, экспортируем
            string = self.msg[314] % self.house.title + ":\n\n"
            flats = []
            for porch in self.house.porches:
                for flat in porch.flats:
                    if includeWithoutNumbers and (not "." in flat.number or self.house.type == "private"):
                        flats.append(flat)
                    elif not includeWithoutNumbers and flat.phone != "": flats.append(flat)
            if len(flats) == 0: self.popup(message=self.msg[313])
            else:
                try:    flats.sort(key=lambda x: float(x.number))
                except: flats.sort(key=lambda x: ut.numberize(x.title))
                for flat in flats:
                    string += f"{flat.number}. {flat.phone}\n"
                if not self.desktop:
                    plyer.email.send(subject=self.msg[314] % "", text=string, create_chooser=True)
                else:
                    Clipboard.copy(string)
                    self.popup(message=self.msg[133])

    def bin(self, text=None):
        """ Корзина на текстовых формах """
        w = h = self.mainList.size[0] * .25 if not self.desktop else 90 # размер (сторона квадрата)
        if self.language == "tr":
            w *= 1.1
            h *= 1.1
        if text is None: text = self.button['bin']
        if self.theme != "3D":
            btn = RoundButton(text=text, size_hint_x=None, size_hint_y=None, size=(w, h))
        else:
            btn = RetroButton(text=text, size_hint_x=None, size_hint_y=None, size=(w, h))
        if self.displayed.form == "flatDetails" and text == self.button['bin']:
            btn.bind(on_release=self.deleteFlatInCondo) # только для квартир - отключение поэтажного вида с одновременным удалением
        elif self.button['share'] in text:
            btn.bind(on_release=self.exportContact) # только для квартир - отключение поэтажного вида с одновременным удалением
        else:
            btn.bind(on_release=self.deletePressed)
        return btn

    def exportContact(self, instance):
        """ Экспорт данных контакта """
        saveResult = self.positivePressed(instant=True, instance=instance)
        self.detailsPressed(instance=instance)
        if saveResult: # делаем экспорт только после успешного сохранения
            con = self.flat
            porchLabel = f"{(self.msg[212][0].upper() + self.msg[212][1:]) if self.language != 'ka' else self.msg[212]}{':' if self.language != 'hy' else '.'}"
            numberOrPorch = f" – {con.number}" if con.number != "virtual" else f"\n{porchLabel} {self.porch.title}"
            string = f"{con.getName()}\n{self.msg[23]} {con.phone}\n{self.msg[15]} {self.house.title}{numberOrPorch}\n{self.msg[18]} {con.note}\n{self.msg[160]}\n"
            for record in con.records:
                string += f"\n{record.date}{':' if self.language != 'hy' else '.'}\n"
                string += f"{record.title}\n"
            if not self.desktop:
                plyer.email.send(subject=con.getName(), text=string, create_chooser=True)
            else:
                Clipboard.copy(string)
                self.popup(message=self.msg[133])

    def tip(self, text="", icon="info", halign="left", valign="top", k=.8, hint_y=None, func=None):
        """ Подсказка """
        background_color = None
        font_size = self.fontXS * self.fontScale(cap=1.2)
        textColor = get_hex_from_color(self.standardTextColor)
        textHeight = None

        if icon == "warn":
            color = "F4CA16"  # желтый
            background_color = [.96, .95, .78] if self.mode == "light" else [.37, .32, .11]
            size_hint_y = hint_y if hint_y is not None else 0.19 * self.fontScale(cap=1.2)
            size_hint_y *= self.fontScale()
            if self.bigLanguage: size_hint_y *= 1.25
            k = .95
        elif icon == "info":
            color = self.titleColor2
            size_hint_y = hint_y if hint_y is not None else 1#0.5
            size_hint_y *= self.fontScale()
        elif icon == "note": # заметка на страницах ввода
            color = self.titleColor2
            size_hint_y = (.15 if self.orientation == "h" else .07) if self.desktop else None
            textHeight = self.standardTextHeight
            halign = "center"
        elif icon == "header": # заметка над списком
            color = get_hex_from_color(self.scrollIconColor)
            size_hint_y = None
            padding = self.padding * 9 if self.displayed.form != "flatView" else 0, 0
            halign = "center" if self.displayed.form == "flatView" else "left"
            valign = "top"
            font_size *= .97
        else:#elif icon == "link":
            color = get_hex_from_color(self.linkColor)
            size_hint_y = hint_y if hint_y is not None else 0.5
            size_hint_y *= self.fontScale()
            text = f"[u][color={color}][ref=link]{text}[/ref][/color][/u]"

        if text == "" and icon != "warn": # если получен пустой текст, вместо подсказки ставим пустой виджет
            tip = Widget(size_hint_y=size_hint_y)
        elif icon == "warn":
            if not self.desktop:
                size1 = int(self.fontXS * self.fontScale(cap=1.2))
                size2 = int(self.fontXXS * self.fontScale(cap=1.2))
                text = f"[color={color}]{self.button[icon]}[/color] [size={size1}]{self.msg[152]}[/size]\n[size={size2}][u]{self.msg[41]}[/u][/size]"
            else: # для ПК просто убираем размеры
                text = f"[color={color}]{self.button[icon]}[/color] {self.msg[152]}\n[u]{self.msg[41]}[/u]"
            tip = TipButton(text=text, size_hint_x=.98, size_hint_y=size_hint_y, halign=halign,
                            valign="center", text_size=[self.mainList.size[0] * k, None],
                            background_color=background_color)
            tip.bind(on_release=self.hideDueWarnMessage)
        elif icon == "header":
            tip = TipButton(text=f"[color={color}]{self.button[icon]}[/color] [color={textColor}][i]{text}[/i][/color]",
                            padding=padding, height=self.standardTextHeight, size_hint_y=size_hint_y,
                            font_size=font_size, halign=halign, valign=valign, background_color=background_color)
        else:
            tip = MyLabel(text=f"[ref=note][color={color}]{self.button[icon]}[/color] {text}[/ref]",
                          text_size=[self.mainList.size[0] * k, textHeight], size_hint_y=size_hint_y,
                          font_size=font_size, markup=True, halign=halign, valign=valign)

        if icon == "link": tip.bind(on_ref_press=func)

        return tip

    def hideDueWarnMessage(self, instance):
        """ Скрытие предупреждения о просроченном участке до перезапуска программы """
        self.mainList.remove_widget(instance)
        self.dueWarnMessageShow = False

    def createFirstCallPopup(self, instance):
        """ Попап первого посещения """
        if self.flat is None: return
        self.displayed.form = "porchView"
        self.FCP.title = self.flat.number
        self.FCP.separator_color = [0,0,0,0]
        self.firstCallPopup = True
        self.phoneInputOnPopup = True if self.settings[0][20] == 1 else False
        size_hint = [.85, .57] if self.orientation == "v" else [.42, .7]
        size_hint[1] *= self.fontScale(cap=1.2)
        contentMain = BoxLayout(orientation="vertical", spacing = self.spacing * 2)
        self.FCP.content = contentMain
        SH = 1 # size_hint_x для всех элементов на окне
        PH = {"center_x": .5}
        pad0 = self.padding * 4

        content = GridLayout(rows=1, cols=2, size_hint_x=SH, pos_hint=PH, padding=(pad0, 0))
        content2 = GridLayout(rows=1, cols=1, size_hint_x=SH, pos_hint=PH, padding=(pad0, 0))
        self.buttonsGrid = GridLayout(rows=0, pos_hint={"right": 1}, padding=(pad0, 0))

        self.buttonsGrid.cols = 0
        font_size = self.fontS * 1.1 * RM.fontScale(cap=1.2)  # общие параметры для маленьких кнопок
        size = self.standardTextHeight * .85, self.standardTextHeight

        self.buttonsGrid.cols += 1 # кнопка телефона 1
        self.quickPhoneCallButton = PopupButton(form=self.popupForm, font_size=font_size, size_hint_x=None,
                                                disabled=False if self.phoneInputOnPopup else True,
                                                size_hint_y=None, size=size)
        self.quickPhoneCallButton.bind(on_release=self.phoneCall)
        self.buttonsGrid.add_widget(self.quickPhoneCallButton)

        shrink = PopupButton( # кнопка удаления или урезания (универсальная)
            text=self.button['shrink'] if self.porch.floors() else self.button['trash'],
            form=self.popupForm, font_size=font_size, size_hint_x=None, size_hint_y=None, size=size)
        def __shrink(instance):
            self.blockFirstCall = 1
            self.deletePressed(forced=True)

        shrink.bind(on_release=__shrink)
        self.buttonsGrid.cols += 1
        self.buttonsGrid.add_widget(shrink)

        if self.porch.floors():  # кнопка удаления на подъезде
            floorDelete = PopupButton(text=self.button['trash'], form=self.popupForm, font_size=font_size,
                                      size_hint_x=None, size_hint_y=None, size=size)
            floorDelete.bind(on_release=self.deleteFlatInCondo)
            self.buttonsGrid.cols += 1
            self.buttonsGrid.add_widget(floorDelete)

        details = PopupButton(text=self.button['contact'], size_hint_x=None,  # кнопка настроек
                              form=self.popupForm, font_size=font_size, size_hint_y=None, size=size)
        def __details(instance):
            if self.phoneInputOnPopup: self.flat.editPhone(self.quickPhone.text)
            self.FCP.dismiss()
            self.popupEntryPoint = 1
            self.blockFirstCall = 1
            self.flatView(instance=instance)
            self.detailsPressed()
        details.bind(on_release=__details)
        self.buttonsGrid.cols += 1
        self.buttonsGrid.add_widget(details)
        self.buttonsGrid.height = details.height + self.padding*2
        self.buttonsGrid.size_hint = self.buttonsGrid.cols * .175, None
        contentMain.add_widget(self.buttonsGrid)

        if self.phoneInputOnPopup:  # поле ввода телефона
            self.keyboardCloseTime = .1
            size_hint[1] = size_hint[1] * 1.08
            content.padding =  pad0, pad0, pad0, 0
            content2.padding = pad0, 0, pad0, pad0
            phoneBox = BoxLayout(orientation="horizontal", padding=(pad0, 0), size_hint=(SH, None), pos_hint=PH,
                                 height=self.standardTextHeight)
            self.quickPhone = MyTextInput(hint_text=self.msg[35], size_hint_y=1,
                                          text=self.flat.phone, popup=True, multiline=False,
                                          wired_border=False, input_type="number" if not self.desktop else "text")
            phoneBox.add_widget(self.quickPhone)
            if self.quickPhone.text != "":
                self.quickPhoneCallButton.text = self.button['phone-square']
                self.quickPhoneCallButton.disabled = False
            else:
                self.quickPhoneCallButton.text = ""
                self.quickPhoneCallButton.disabled = True

            self.savePhoneBtn = PopupButtonGray(text="", size_hint_y=1, size_hint_x=.12, disabled=True)
            phoneBox.add_widget(self.savePhoneBtn)
            contentMain.add_widget(phoneBox)

            def __savePhone(instance):
                self.flat.editPhone(self.quickPhone.text)
                self.save()
                self.quickPhone.keyboard_on_key_up()
                self.FCP.dismiss()
                if self.porch.clearCache("т") or self.porch.clearCache("с"): self.porchView(instance=instance)
                else: self.clickedInstance.update(self.flat)
            self.quickPhone.bind(on_text_validate=__savePhone)
            self.savePhoneBtn.bind(on_release=__savePhone)

        r = self.getRadius(120)[0]
        self.FCRadius = [  # first call radius – значения радиусов для всех кнопок плашки первого посещения
            [r, 0, 0, 0],  # нет дома
            [0, r, 0, 0],  # запись с нет дома
            [r, r, 0, 0],  # запись без нет дома
            [0, 0, r, r]   # отказ
        ]

        if self.settings[0][13] == 1:
            content.spacing = self.spacing
            firstCallBox = BoxLayout(orientation="vertical") # кнопка нет дома
            if self.theme == "3D": firstCallBox.spacing = 0
            elif self.desktop: firstCallBox.spacing = 1
            else: firstCallBox.spacing = self.spacing
            if self.theme != "3D":
                firstCallNotAtHome = FirstCallButton1()
            else:
                firstCallNotAtHome = RetroButton(text=RM.button['lock'], color="lightgray")

            def __notAtHome(instance=None):
                if not self.resources[0][1][4] and self.language == "ru":
                    self.popup(title=self.msg[247], message="Кнопку «Нет дома» можно отключить в настройках!")
                    self.resources[0][1][4] = 1
                self.house.statsCached= None
                date = time.strftime("%d", time.localtime())
                month = self.monthName()[5]
                timeCur = time.strftime("%H:%M", time.localtime())
                newNote = f"{date} {month} {timeCur} {self.msg[206].lower()}\n" + self.flat.note
                self.flat.editNote(newNote)
                self.save()
                self.FCP.dismiss()
                if self.porch.clearCache("з") or self.porch.clearCache("с"): self.porchView(instance=instance)
                else: self.clickedInstance.update(self.flat)
            firstCallNotAtHome.bind(on_release=__notAtHome)
            firstCallBox.add_widget(firstCallNotAtHome)
            content.add_widget(firstCallBox)

        if self.theme != "3D": # кнопка запись
            firstCallBtnCall = FirstCallButton2()
        else:
            firstCallBtnCall = RetroButton(text=RM.button['record'], color=self.titleColor)
        def __firstCall(instance):
            if self.phoneInputOnPopup: self.flat.editPhone(self.quickPhone.text)
            self.flatView(call=True, instance=instance)
            self.FCP.dismiss()
        firstCallBtnCall.bind(on_release=__firstCall)
        content.add_widget(firstCallBtnCall)
        if self.theme != "3D":
            firstCallBtnReject = FirstCallButton3()
        else:
            firstCallBtnReject = RetroButton(text=RM.button['reject'],
                                             color=self.getColorForStatus(self.settings[0][18]))

        def __quickReject(instance): # кнопка отказ
            self.house.statsCached = None
            self.flat.addRecord(self.msg[207][0].lower() + self.msg[207][1:])
            self.flat.status = self.settings[0][18]  # "0"
            self.save()
            self.FCP.dismiss()
            if self.porch.clearCache("с") or self.porch.clearCache("д"): self.porchView(instance=instance)
            else: self.clickedInstance.update(self.flat)
        firstCallBtnReject.bind(on_release=__quickReject)
        content2.add_widget(firstCallBtnReject)
        contentMain.add_widget(content)
        contentMain.add_widget(content2)

        side = self.standardTextHeight * 1.1 # кнопки вторичных цветов внизу
        pos_hint = {"center_y": .5}
        c2box = BoxLayout(size_hint=(SH, None), pos_hint=PH, padding=(pad0, 0), spacing=self.spacing * 4,
                          height=side * (1.7 if not self.phoneInputOnPopup else 1.2))
        def __clickOnColor2(instance):
            color2 = 0 if instance.color == [.2, .2, .2, 1] else self.color2List.index(instance.color)
            self.flat.color2 = color2
            self.save()
            self.FCP.dismiss()
            if self.porch.clearCache("с2"): self.porchView(instance=instance)
            else: self.clickedInstance.update(self.flat)
        cb = []
        for c in range(4):
            cb.append(RoundColorButton(color=self.getColor2(c), side=side, pos_hint=pos_hint))
            c2box.add_widget(cb[len(cb)-1])
            cb[len(cb)-1].bind(on_release=__clickOnColor2)
        contentMain.add_widget(c2box)

        self.buttonClose = PopupButton(text=self.msg[190], height=self.standardTextHeight * 1.5) # кнопка отмена
        self.buttonClose.bind(on_release=self.FCP.dismiss)
        contentMain.add_widget(self.buttonClose)
        self.FCP.size_hint = size_hint

        try: self.FCP.open()
        except:
            self.dprint("Не могу открыть попап, перезагружаю данные.") # проблема возникает при смене размера окна только на ПК
            self.FCP.dismiss()
            self.restart("soft")
            self.porch.scrollview = self.porch.floorview = None
            self.porchView(instance=instance)

    def createEmojiPopup(self, instance=None, *args):
        """ Создание и (или) запуск окна выбора иконок. Создается только один раз за работу программы """
        if self.emojiPopup is None:
            content = BoxLayout(orientation="vertical")
            def __emojiClick(instance):
                self.flat.emoji = instance.text
                self.save()
                self.emojiSelector.text = self.flat.emoji if self.flat.emoji != "" else self.button["add_emoji"]
                self.emojiPopup.dismiss()
                if self.theme == "3D":
                    self.emojiSelector.color = self.topButtonColor if self.emojiSelector.text == self.button["add_emoji"] else self.linkColor
            self.emojiGrid = GridLayout(padding=(0, self.padding * 2), spacing=self.spacing)
            if self.orientation == "v":
                size_hint = .88, .85
                self.emojiGrid.cols = 6
                self.emojiGrid.rows = 11
            else:
                size_hint = .8, .8
                self.emojiGrid.cols = 11
                self.emojiGrid.rows = 6
            for e in range(len(self.icons)-1):
                button = PopupButton(text=self.icons[e], size_hint_y=1, font_size=self.fontXXL, forceSize=True)
                button.bind(on_release=__emojiClick)
                self.emojiGrid.add_widget(button)
            buttonClose = PopupButton(text=self.msg[190])
            buttonClose.bind(on_release=lambda x: __emojiClick(instance=Button(text="")))
            content.add_widget(self.emojiGrid)
            content.add_widget(buttonClose)
            self.emojiPopup = PopupNoAnimation(title=self.msg[220], content=content, size_hint=size_hint,
                                               separator_color=self.titleColorOnBlack)
        for button in self.emojiGrid.children:
            button.color = self.titleColorOnBlack if button.text == self.flat.emoji else "lightgray"

        try: self.emojiPopup.open()
        except:
            self.dprint("Не могу открыть попап, перезагружаю данные.") # проблема возникает при смене размера окна только на ПК
            self.emojiPopup.dismiss()
            self.restart("soft")
            self.floaterBox.clear_widgets()
            self.flatView(instance=instance)

    # Обработка контактов

    def retrieve(self, containers, h, p, f, contacts):
        """ Retrieve and append contact list """

        cont = containers[h]
        lastRecordDate = cont.porches[p].flats[f].records[0].date if len(cont.porches[p].flats[f].records) > 0 else None
        if cont.porches[p].flats[f].lastVisit == 0: cont.porches[p].flats[f].lastVisit = 0
        contacts.append([  # create list with one person per line with values:
            cont.porches[p].flats[f].getName(),  # 0 contact name
            cont.porches[p].flats[f].emoji,  # 1 emoji
            cont.title,  # 2 house title
            cont.porches[p].flats[f].number,  # 3 flat number
            lastRecordDate,  # 4 дата последней встречи - отображаемая, record.date
            cont.porches[p].flats[f].lastVisit, # 5 дата последней встречи - абсолютная, Flat.lastVisit
            True if self.invisiblePorchName in cont.porches[p].title else False,  # 6 бессегментный участок или нет
            [h, p, f],  # 7 reference to flat
            cont.porches[p].type,  # 8 porch type ("virtual" as key for standalone contacts)
            cont.porches[p].flats[f].phone,  # 9 phone number

            # Used only for search function:
            cont.porches[p].flats[f].title,  # 10 flat title
            cont.porches[p].flats[f].note,  # 11 flat note
            cont.porches[p].title,  # 12 porch name
            cont.note,  # 13 house note

            cont.listType() if cont.type != "virtual" else False,  # 14 listType или нет

            # Used for checking house type:

            cont.type,  # 15 house type ("virtual" as key for standalone contacts)

            ""  # не используется
        ])
        return contacts

    def decommify(self, string):
        """ Замена запятых на точки с запятой в строке """
        if "," in string: result = string.replace(",", ";")
        else: result = string
        return result.strip()

    def getContacts(self, forSearch=False):
        """ Returns list of all contacts """
        contacts = []
        for h in range(len(self.houses)):
            for p in range(len(self.houses[h].porches)):
                for f in range(len(self.houses[h].porches[p].flats)):
                    flat = self.houses[h].porches[p].flats[f]
                    if not forSearch:  # поиск для списка контактов - только светло-зеленые жильцы и все отдельные контакты
                        if flat.status == "1" or flat.number == "virtual":
                            self.retrieve(self.houses, h, p, f, contacts)
                    else:  # поиск для поиска - все контакты вне зависимости от статуса
                        if not "." in flat.number or self.houses[h].type == "private":
                            self.retrieve(self.houses, h, p, f, contacts)
        for h in range(len(self.resources[1])):
            self.retrieve(self.resources[1], h, 0, 0, contacts)  # отдельные контакты - все
        return contacts

    # Различная визуализация

    def getColorForStatus(self, status=99):
        """ Возвращает цвет по полученному символу статуса """
        if self.theme == "purple" or self.theme == "morning":
            if status == "?":   return self.darkGrayFlat  # темно-серый
            elif status == "0": return [.29, .44, .69,1]  # синий
            elif status == "1": return [.16, .69, .29, 1] # зеленый
            elif status == "2": return [.29, .4, .19, 1]  # темно-зеленый
            elif status == "3": return [.48, .34, .65, 1] # фиолетовый
            elif status == "4": return [.77, .52, .19, 1] # оранжевый
            elif status == "5": return [.58, .16, .15, 1] # красный
            else:               return self.lightGrayFlat
        else:
            if status == "?":   return self.darkGrayFlat  # темно-серый
            elif status == "0": return [0, .54, .73, 1]   # синий
            elif status == "1": return [0, .7, .46, 1]    # зеленый
            elif status == "2": return [.30, .50, .46, 1] # темно-зеленый
            elif status == "3": return [.53, .37, .76, 1] # фиолетовый
            elif status == "4": return [.73, .63, .33, 1] # желтый | светло-коричневый
            elif status == "5": return [.75, .29, .22, 1] # красный
            else:               return self.lightGrayFlat

    def getColorForStatusPressed(self, status):
        """ Возвращает цвет кнопки статуса в нажатом состоянии """
        color = self.getColorForStatus(status)
        k = .8
        return color[0]*k, color[1]*k, color[2]*k, 1

    def getColorForReject(self):
        """ Цвет для кнопки отказа """
        color = self.getColorForStatus(self.settings[0][18])
        if self.mode == "light":
            return color
        else:
            return [color[0]*.95, color[1]*.95, color[2]*.95, .97]

    def getColor2(self, color2, flat=None):
        """ Возвращает значение вторичного цвета (кружочка) """
        alpha = .9
        if   color2 == 1: return [.25, .9, .99, alpha]  # голубой
        elif color2 == 2:
            yellowDefault = [.91, .87, .47, alpha]
            if flat is not None:
                if flat.status == "4":
                    return [.93, .88, .51, alpha] # желтый на желтом
                else:
                    return yellowDefault # желтый на остальных
            return yellowDefault # желтый
        elif color2 == 3:
            redDefault = [1, .45, .5, alpha]
            if flat is not None:
                if flat.status == "4" and self.theme != "purple" and self.theme != "morning":
                    return [1, .42, .53, alpha] # красный на желтом на НЕ пурпурных темах
                elif flat.status == "4":
                    return [1, .4, .45, alpha] # красный на желтом на пурпурных темах
                elif flat.status == "5":
                    return [1, .5, .55, alpha] # красный на красном
                else:
                    return redDefault # красный на остальных
            else:
                return redDefault # красный на остальных
        else:             return [0, 0, 0, 0]

    def keyboardHeight(self, *args):
        """ Возвращает высоту клавиатуры в str """
        if platform == "android":
            activity.getWindow().getDecorView().getWindowVisibleDisplayFrame(rect)
            rect.top = 0
            height = activity.getWindowManager().getDefaultDisplay().getHeight() - (rect.bottom - rect.top)
            if height > 300: self.defaultKeyboardHeight = height
            else: height = self.defaultKeyboardHeight
            return height
        else:
            return self.defaultKeyboardHeight

    def cacheFreeModeGridPosition(self):
        """ Сохранение позиции сетки подъезда в свободном режиме при уходе с экрана """
        if self.porch is not None and self.porch.floorview is not None and self.porch.pos[0]:
            self.porch.pos[1] = copy(self.porch.floorview.pos)

    def window_touch_move(self, tip=True, touch=None):
        """ Регистрация перетаскивания по экрану """
        # рисуем кнопку сброса позиции подъезда в свободном перемещении
        if self.porch is not None and self.porch.floorview is not None \
            and self.displayed.form == "porchView" and self.porch.floors() and self.porch.pos[0]:
            if (self.porch.floorview.oversized and self.porch.floorview.pos != [0, 0]) \
                or (not self.porch.floorview.oversized and self.porch.floorview.pos != self.porch.floorview.centerPos):
                self.navButton.text = self.button["adjust"]
                self.navButton.disabled = False
            else:
                self.navButton.text = ""
                self.navButton.disabled = True

    def clearTable(self):
        """ Очистка верхних кнопок таблицы для некоторых форм """
        self.backButton.disabled = False
        self.sortButton.disabled = True
        self.sortButton.text = ""
        self.neutral.disabled = True
        self.neutral.text = ""
        self.navButton.disabled = True
        self.navButton.text = ""
        self.mainList.padding = 0
        if self.bottomButtons in self.mainList.children:
            self.mainList.remove_widget(self.bottomButtons)
        self.restorePositiveButton()
        self.cacheFreeModeGridPosition()
        self.floaterBox.clear_widgets()

    def showProgress(self):
        """ Показывает кнопку с символом ожидания """
        self.floaterBox.add_widget(ProgressButton())

    def checkOrientation(self, window=None, width=None, height=None):
        """ Выполняется при каждом масштабировании окна, проверяет ориентацию, и если она горизонтальная, адаптация интерфейса """

        if Window.size[0] <= Window.size[1]:
            self.orientation = "v"
            self.globalFrame.padding = 0
            if self.orientation != self.orientationPrev: self.drawMainButtons()
            self.orientationPrev = self.orientation
            self.boxHeader.size_hint_y = self.titleSizeHintY
            self.titleBox.size_hint_y = self.tableSizeHintY
            self.boxFooter.size_hint_y = self.mainButtonsSizeHintY
            self.positive.size_hint_x=.5
            self.bottomButtons.size_hint_y = self.bottomButtonsSizeHintY
        else:
            self.orientation = "h"
            if self.theme == "morning" or self.theme == "purple":
                self.globalFrame.padding = (self.padding * 5, 0, 0, 0)
            if self.orientation != self.orientationPrev: self.drawMainButtons()
            self.orientationPrev = self.orientation
            self.boxHeader.size_hint_y = self.titleSizeHintY * 1.2
            self.titleBox.size_hint_y = self.tableSizeHintY * 1.2
            self.boxFooter.size_hint_y = .6
            self.positive.size_hint_x = .2
            self.bottomButtons.size_hint_y = self.bottomButtonsSizeHintY * 1.2

        if self.desktop and not Devmode:
            try:
                with open("win.ini", "w") as file:
                    file.write(str(width)+"\n")
                    file.write(str(height)+"\n")
                    file.write(str(Window.top)+"\n")
                    file.write(str(Window.left))
            except: pass

    def drawMainButtons(self):
        """ Отрисовка кнопок меню в зависимости от ориентации экрана при смене ориентации """

        while 1:
            if len(self.globalFrame.children) < 3: # если кнопок нет (при старте или смене ориентации), создаем их
                self.boxFooter = BoxLayout()
                self.buttonTer = MainMenuButton(text=self.msg[2]) # Участки
                self.buttonCon = MainMenuButton(text=self.msg[3]) # Контакты
                self.buttonRep = MainMenuButton(text=self.msg[4]) # Отчет
                if self.orientation == "v": # вертикальная ориентация
                    self.boxFooter.orientation = "horizontal"
                    self.boxFooter.padding = 0
                    if self.desktop:
                        self.desktopModeFrame.clear_widgets()
                        self.desktopModeFrame.size_hint_x = 0
                    self.globalFrame.add_widget(self.boxFooter)

                else: # горизонтальная ориентация
                    self.boxFooter.orientation = "vertical"
                    self.boxFooter.padding = (0, 0, 0, self.padding * 3)
                    if self.desktop:
                        self.desktopModeFrame.size_hint_x = None
                        self.desktopModeFrame.width = self.horizontalOffset
                        self.desktopModeFrame.add_widget(self.boxFooter)
                self.boxFooter.add_widget(self.buttonTer)
                self.boxFooter.add_widget(self.buttonCon)
                self.boxFooter.add_widget(self.buttonRep)
                break

            else: # если кнопки есть, удаляем их
                self.globalFrame.remove_widget(self.boxFooter)
                self.boxFooter.clear_widgets()

        self.updateMainMenuButtons()
        self.floaterBox.clear_widgets()

    def updateMainMenuButtons(self, deactivateAll=False):
        """ Обновляет статус трех главных кнопок """
        if deactivateAll:
            self.buttonRep.deactivate()
            self.buttonTer.deactivate()
            self.buttonCon.deactivate()
        elif self.displayed.form == "rep":
            self.buttonRep.activate()
            self.buttonTer.deactivate()
            self.buttonCon.deactivate()
        elif self.displayed.form == "con" or self.contactsEntryPoint:
            self.buttonCon.activate()
            self.buttonTer.deactivate()
            self.buttonRep.deactivate()
        elif self.displayed.form == "ter" or self.displayed.form == "createNewFlat" or "view" in self.displayed.form.lower():
            self.buttonTer.activate()
            self.buttonCon.deactivate()
            self.buttonRep.deactivate()
        else:
            self.buttonRep.deactivate()
            self.buttonTer.deactivate()
            self.buttonCon.deactivate()

    def hidePositiveButton(self):
        """ Скрытие центральной кнопки """
        self.positive.text = self.navButton.text = self.neutral.text = ""
        self.listarea.remove_widget(self.bottomButtons)
        self.titleBox.size_hint_y = None
        self.titleBox.height = self.TBH

    def restorePositiveButton(self):
        """ Восстановление центральной кнопки """
        if self.bottomButtons not in self.listarea.children:
            self.listarea.add_widget(self.bottomButtons)
        self.titleBox.size_hint_y = self.tableSizeHintY
        self.checkOrientation()

    def getRadius(self, rad=100, instance=None):
        """ Коэффициент закругления овальных кнопок. Больше - СЛАБЕЕ закругление """
        # Некоторые используемые значения:
        # 37 - центральная кнопка и закругленное поле ввода
        # 100 - большинство кнопок (по умолчанию)
        # 200 - незакругленное поле ввода
        # 250 - почти квадратные кнопки (некоторые)
        # instance - кнопка, которая рисуется на момент вызова функции
        if instance is not None:
            if "MyTextInput" in str(instance):  # строка ввода более закругленная на формах InputBox
                rad = 37 if instance.rounded else 200
            elif instance.text == icon('icon-minus') or instance.text == icon('icon-plus') \
                or instance.text == f"{self.button['share']} {self.msg[110]} " \
                or instance.text == self.button['calendar'] or instance.text == self.button['male'] \
                or instance.text == self.button['female']: # уменьшаем радиус для некоторых видов кнопок
                rad = 250

        if self.theme == "3D" or \
                (self.platform == "win" and "MyTextInput" in str(instance)):
            buttonRadius = 0 # на 3D все квадратное, на Windows - поля ввода
        else:
            buttonRadius = (Window.size[0] * Window.size[1]) / (Window.size[0] * rad)

        radius = [buttonRadius,]
        return buttonRadius, radius

    def thickness(self):
        """ Выдает толщину линии независимо от разрешения экрана, соответствующую проволочной версии RM.positive.
         На компьютере всегда 1 пиксел """
        density = int(self.density())
        mirrorDensity = density     # просто повтор разрешения (ниже)
        if self.desktop:
            extremeThinLine = 1     # максимально тонкая линия, которую можно нормально отрисовать на устройстве
        else:
            extremeThinLine = (density / 2) if (density / 2) >= 1.3 else 1.3
        return mirrorDensity, extremeThinLine

    def density(self):
        """ Получает плотность экрана в dpi """
        if platform == 'android':
            Hardware = autoclass('org.renpy.android.Hardware')
            return Hardware.metrics.scaledDensity
        elif platform == 'ios':
            import ios
            return ios.get_scale() * 0.75
        elif platform == 'macosx':
            from kivy.base import EventLoop
            EventLoop.ensure_window()
            return EventLoop.window.dpi / 96.
        else:
            return 1.0

    def fontScale(self, cap=999.9):
        """ Возвращает размер шрифта на Android:
        маленький = 0.85
        обычный = 1.0
        большой = 1.149
        очень крупный = 1.299
        огромный = 1.45 """
        if platform == "android":
            scale = mActivity.getResources().getConfiguration().fontScale
            if scale > cap: scale = cap
        else: scale = 1
        return scale

    def numberToIcon(self, number):
        """ Преобразует цифру в иконку с цифрой """
        if number == "2": return icon('icon-number2')
        elif number == "3": return icon('icon-number3')
        elif number == "4": return icon('icon-number4')
        else: return icon('icon-number1')

    # Вспомогательные функции

    def log(self, message="", title="Rocket Ministry", timeout=2, forceNotify=False):
        """ Displaying and logging to file important system messages """
        if Devmode: self.dprint(f"[LOG] {message}")
        elif not self.desktop and not forceNotify:
            plyer.notification.notify(toast=True, message=message)
        else:
            icon = "" if not self.desktop else "icon.ico"
            try: plyer.notification.notify(app_name="Rocket Ministry", title=title, app_icon=icon,
                                           ticker="Rocket Ministry", message=message, timeout=timeout)
            except: plyer.notification.notify(toast=True, message=message)

    def addHouse(self, houses, input, type=True):
        """ Adding new house """
        if type == True: type = "condo"
        elif type == False: type = "private"
        createInvisiblePorch = True if type == "list" else False
        if type == "list": type = "private"
        houses.append(House(title=input.strip(), type=type))
        if createInvisiblePorch: # добавляем первый невидимый подъезд для списочного участка
            last = len(houses)-1
            houses[last].addPorch(input=RM.listTypePorchName, type="сегмент")

    def recalcServiceYear(self, allowSave=True):
        """ Подсчет статистики служебного года """
        if self.analyticsMessageCached is None:
            for i in range(12):
                month = self.months[i]
                month.text = month.text.strip()
                if month.text.isnumeric():
                    self.settings[4][i] = int(month.text)
                    if int(month.text) < self.settings[0][3]:
                        month.background_color = self.getColorForStatus("5")
                    elif int(month.text) == self.settings[0][3]:
                        if self.theme != "green" and self.theme != "3D": month.background_color = self.titleColor
                        else: month.background_color = self.getColorForStatus("0")
                    else:
                        if self.theme == "green" or self.theme == "3D": month.background_color = self.titleColor
                        else: month.background_color = self.getColorForStatus("1")
                    month.background_color[3] = 0.4
                else:
                    self.settings[4][i] = None
                    month.background_color = self.sortButtonBackgroundColor
            hourSum = 0.0  # total sum of hours
            monthNumber = 0  # months entered
            for i in range(len(self.settings[4])):
                if self.settings[4][i] is not None:
                    hourSum += self.settings[4][i]
                    monthNumber += 1
            yearNorm = float(self.settings[0][3]) * 12  # other stats
            gap = (12 - monthNumber) * float(self.settings[0][3]) - (yearNorm - hourSum)
            average = (yearNorm - hourSum) / (12 - monthNumber) if monthNumber != 12 else (yearNorm - hourSum)
            if gap >= 0:
                gapEmo = icon("icon-smile-o")
                gapWord = self.msg[174]
            elif gap < 0:
                gapEmo = icon("icon-frown-o")
                gapWord = self.msg[175]
            else:
                gapEmo = gapWord = ""
            br = "" if Window.size[1]<=600 or self.fontScale() > 1.2 or self.bigLanguage else "\n"
            self.analyticsMessage.text = f"[b]{self.msg[176]}[/b]\n\n" + \
                                         f"{self.msg[177]}{self.col} [b]%d[/b]\n{br}" % monthNumber + \
                                         f"{self.msg[178]}{self.col} [b]%d[/b]\n{br}" % hourSum + \
                                         f"{self.msg[179]}¹{self.col} [b]%d[/b]\n{br}" % yearNorm + \
                                         f"{self.msg[180]}{self.col} [b]%d[/b]\n{br}" % (yearNorm - hourSum) + \
                                         f"%s{self.col} [b]%d[/b] %s\n{br}" % (gapWord, abs(gap), gapEmo) + \
                                         f"{self.msg[181]}²{self.col} [b]%0.f[/b]\n{br}" % average + \
                                         "____\n" + \
                                         f"¹ {self.msg[182]}\n" + \
                                         f"² {self.msg[183]}"
            self.analyticsMessageCached = self.analyticsMessage.text
            if allowSave: self.save()

    def sendLastMonthReport(self, instance=None):
        """ Отправка отчета прошлого месяца """
        if not self.desktop:
            plyer.email.send(subject=self.msg[4], text=self.rep.lastMonth, create_chooser=True)
        else:
            Clipboard.copy(self.rep.lastMonth)
            self.popup(message=self.msg[133])

    def deleteFlatInCondo(self, *args):
        """ Удаление квартиры в многоквартирном доме """
        self.deleteOnFloor = True
        if self.flat.is_empty() and self.flat.status == "" and self.flat.color2 == 0 and self.flat.emoji == "":
            self.deletePressed()
        else:
            self.popup(popupForm = "confirmDeleteFlat",
                       title=f"{self.msg[199]}: {self.flatTitleNoFormatting}", message=self.msg[198],
                       options=[self.button["yes"], self.button["no"]])

    def deletePressed(self, instance=None, forced=False):
        """ Действие при нажатии на кнопку с корзиной на форме любых деталей """
        if self.displayed.form == "houseDetails": # удаление участка
            self.popup("confirmDeleteHouse", title=f"{self.msg[194]}: {self.house.title}", message=self.msg[195],
                       options=[self.button["yes"], self.button["no"]])

        elif self.displayed.form == "porchDetails": # удаление подъезда
            title = self.msg[196] if self.house.type == "condo" else self.msg[197]
            self.popup("confirmDeletePorch", title=f"{title}: {self.porch.title}", message=self.msg[198],
                       options=[self.button["yes"], self.button["no"]])

        elif self.displayed.form == "flatDetails" or self.displayed.form == "flatView" \
                or self.displayed.form == "porchView" or forced: # удаление квартиры
            self.popupForm = "confirmDeleteFlat"
            if self.contactsEntryPoint or self.searchEntryPoint or ((self.flat.status != "" or self.flat.color2 != 0 or self.flat.emoji != "") and not self.porch.floors()):
                self.popup(title=f"{self.msg[199]}: {self.flatTitleNoFormatting}", message=self.msg[198], # Вы уверены?
                           options=[self.button["yes"], self.button["no"]])
            else:
                self.popupPressed(instance=Button(text=self.button["yes"]))

        elif self.displayed.form == "recordView": # удаление записи посещения
            self.popup("confirmDeleteRecord", title=self.msg[200],
                       message=f"{self.msg[201]} {self.record.date}?",
                       options=[self.button["yes"], self.button["no"]])

        elif self.displayed.form == "logEntryView": # удаление записи журнала
            self.popup("confirmDeleteLogEntry", title=f"{self.msg[201]} {self.entryDate}?", message=self.msg[198],
                       options=[self.button["yes"], self.button["no"]])

        elif self.displayed.form == "noteForFlat":
            self.flat.note = ""
            self.save()
            self.flatView(instance=instance)

        elif self.displayed.form == "noteForPorch":
            self.porch.note = ""
            self.save()
            self.porchView(instance=instance)

        elif self.displayed.form == "noteForHouse":
            self.house.note = ""
            self.save()
            self.houseView(instance=instance)

    def confirmNonSave(self, instance):
        """ Проверяет, есть ли несохраненные данные в форме первого посещения """
        if "RoundButton" in str(instance) or (self.contactsEntryPoint and "MyTextInput" in str(instance)):
            return False # для предотвращения ложных срабатываний в разделе контактов
        try:
            if self.displayed.form != "flatView" or self.msg[162] not in self.pageTitle.text:
                return False
            len(self.multipleBoxEntries) # для генерации ошибки
        except: return False
        else:
            if self.multipleBoxEntries[0].text.strip() == self.flat.getName() and self.multipleBoxEntries[1].text.strip() == "":
                return False
            else:
                self.popup("nonSave", message=self.msg[239], options=[self.button["yes"], self.button["no"]])
                return True

    def popupPressed(self, instance=None):
        """ Действия при нажатии на кнопки всплывающего окна self.popup """
        self.dismissTopPopup()

        if self.popupForm == "windows":
            self.dismissTopPopup(all=True)
            if self.button["yes"] in instance.text.lower():
                if self.language == "ru":
                    webbrowser.open("https://github.com/antorix/rocket-ministry/wiki/ru#windows")
                else:
                    webbrowser.open("https://github.com/antorix/rocket-ministry/wiki#windows")

        elif self.popupForm == "clearData":
            if self.button["yes"] in instance.text.lower():
                self.clearDB()
                self.removeFiles()
                if platform == "android":
                    temp = SharedStorage().get_cache_dir()
                    if temp and os.path.exists(temp): shutil.rmtree(temp)
                self.log(self.msg[192])
                self.restart("soft")
                self.terPressed(instance=instance)

        elif self.popupForm == "restoreRequest":
            if self.button["yes"] in instance.text.lower():
                result = self.backupRestore(restoreNumber=self.fileToRestore, allowSave=False)
                self.dismissTopPopup()
                if result == False:
                    self.popup(title=self.msg[44], message=self.msg[45])
                else:
                    self.save()
                    self.restart("soft")
                    self.terPressed(instance=instance)
                    self.popup(title=self.msg[44], message=self.msg[258] % self.fileDates[self.fileToRestore])

        elif self.popupForm == "newMonth":
            self.repPressed()

        elif self.popupForm == "nonSave":
            if self.button["yes"] in instance.text.lower():
                self.multipleBoxEntries[0].text = self.flat.getName()
                self.multipleBoxEntries[1].text = ""
                self.func()
            else:
                self.floaterBox.clear_widgets()

        elif self.popupForm == "updatePorch":
            if self.button["yes"] in instance.text.lower():
                self.porch.floorview = self.porch.scrollview = self.house.statsCached = None
                self.displayed.form = "porchView"
                self.porch.deleteHiddenFlats()
                try:
                    start = int(self.flatRangeStart.text.strip())
                    finish = int(self.flatRangeEnd.text.strip())
                    floors = int(self.floors.get())
                    f1 = int(self.floor1.get())
                    if start > finish or start < 0 or floors < 1:  #
                        5 / 0  # создаем ошибку
                except:
                    self.popup(message=self.msg[88])
                    self.positivePressed(instant=True)
                else:
                    self.porch.flatsLayout = "н" # удаляем квартиры до и после заданного диапазона
                    newFlats = []
                    for flat in self.porch.flats:
                        num = ut.numberize(flat.number)
                        if num >= start and num <= finish:
                            newFlats.append(flat)
                    del self.porch.flats[:]
                    self.porch.flats = newFlats
                    self.porch.addFlats(start, finish, floors)
                    self.porch.adjustFloors(floors)
                    self.porch.floor1 = f1
                    if len(self.house.porches) == 1:  # если это первое создание квартир в доме, выгружаем параметры в настройку
                        self.settings[0][9] = start, finish, floors
                    self.save()
                    self.porch.flatsLayout = str(self.porch.rows)
                    self.porchView(instance=instance)

            elif self.exitToPorch:
                self.porchView(instance=instance)
                self.dismissTopPopup(all=True)

        elif self.popupForm == "confirmDeleteRecord":
            if self.button["yes"] in instance.text.lower():
                self.house.statsCached = None
                self.flat.deleteRecord(self.record)
                self.save()
                self.flatView(instance=instance)

        elif self.popupForm == "confirmDeleteLogEntry":
            if self.button["yes"] in instance.text.lower():
                del self.resources[2][self.entryID]
                self.save()
                self.repPressed(jumpToLog=True)

        elif self.popupForm == "confirmDeleteFlat":
            if self.button["yes"] in instance.text.lower():
                self.porch.scrollview = self.house.statsCached = None
                if self.house.type == "virtual":  # удаление виртуального контакта
                    virtualHouse = self.resources[1].index(self.house)
                    del self.resources[1][virtualHouse]
                    if self.contactsEntryPoint: self.conPressed(instance=instance)
                    elif self.searchEntryPoint: self.find()
                elif self.contactsEntryPoint:  # удаление из контактов - простое очищение
                    self.flat.wipe()
                    self.conPressed(instance=instance)
                elif self.searchEntryPoint:  # удаление из поиска - простое очищение
                    self.flat.wipe()
                    self.find()
                elif self.house.type == "condo":
                    if self.deleteOnFloor: # полное удаление квартиры на сетке подъезда, а также на списке из настроек
                        self.deleteOnFloor = False
                        self.flat.number = "%.1f" % (ut.numberize(self.flat.number) + .5)
                        self.flat.wipe()
                        self.FCP.dismiss()
                        self.porchView(instance=instance,
                                       update=True if self.displayed.form == "flatDetails" else False)
                    else: # показ вопроса: удалить квартиру в этой позиции?
                        if self.resources[0][1][0] == 0 and self.porch.floors():
                            self.popup("confirmShrinkFloor", title=self.msg[203], message=self.msg[216],
                                       checkboxText=self.msg[170], options=[self.button["yes"], self.button["no"]])
                            return
                        else:
                            if not self.porch.floors(): # полное удаление квартиры на списке подъезда (не из настроек)
                                self.flat.number = "%.1f" % (ut.numberize(self.flat.number) + .5)
                                self.flat.wipe()
                                self.FCP.dismiss()
                                self.porchView(instance=instance)
                            else: # удаление позиции на сетке подъезда
                                blockDelete = self.porch.deleteFlat(self.flat)
                                if blockDelete != True:
                                    if self.displayed.form != "flatDetails": # не из настроек
                                        self.porchView(instance=instance, update=False)
                                        self.FCP.dismiss(all=True)
                                    else: # из настроек
                                        selected = self.house.porches.index(self.porch)
                                        self.allowDelayOnUpdateList = False
                                        self.porchView(instance=instance, update=False)
                                        self.backPressed()
                                        self.scrollClick(instance=self.btn[selected], delay=False) # не элегантно, но пока работает

                else: # обычное удаление в сегменте
                    self.FCP.dismiss(all=True)
                    self.porch.deleteFlat(self.flat)
                    self.porchView(instance=instance)
                self.save()
                self.updateMainMenuButtons()
            else:
                self.deleteOnFloor = False

        elif self.popupForm == "confirmShrinkFloor":
            if self.popupCheckbox.active: self.resources[0][1][0] = 1
            if self.button["yes"] in instance.text.lower():
                self.FCP.dismiss()
                self.house.statsCached = None
                self.porch.deleteFlat(self.flat)
                self.save()
                if self.displayed.form == "flatDetails": self.porch.floorview = None
                self.porchView(instance=instance, update=True if self.displayed.form == "flatDetails" \
                                                                 or not self.porch.floors() else False)
        elif self.popupForm == "confirmDeletePorch":
            if self.button["yes"] in instance.text.lower():
                self.house.statsCached = None
                self.house.deletePorch(self.porch)
                self.save()
                self.houseView(instance=instance)

        elif self.popupForm == "confirmDeleteHouse":
            if self.button["yes"] in instance.text.lower():
                for porch in self.house.porches:
                    for flat in porch.flats:
                        if flat.status == "1":
                            if flat.getName() == "": flat.updateName("?")
                            flat.clone(toStandalone=True, title=self.house.title)
                del self.houses[self.houses.index(self.house)]
                self.save()
                self.terPressed(instance=instance)

        elif self.popupForm == "pioneerNorm":
            if self.button["yes"] in instance.text.lower():
                self.settings[0][3] = 50
                self.save()
                self.repPressed()

        elif self.popupForm == "restart":
            if self.button["yes"] in instance.text.lower():
                self.restart()

        elif self.popupForm == "resetFlatToGray":
            if self.button["yes"] in instance.text.lower():
                self.house.statsCached = None
                if len(self.stack) > 0: del self.stack[0]
                self.flat.wipe()
                if self.contactsEntryPoint:  self.conPressed(instance=instance)
                elif self.searchEntryPoint:  self.find(instance=True)
                else:                        self.porchView(instance=instance)
                self.save()
            else:
                self.colorBtn[6].text = ""
                self.activateColorButton()

        elif self.popupForm == "submitReport":
            if self.button["no"] in instance.text.lower():
                self.buttonTer.deactivate()
                self.repPressed(jumpToPrevMonth=True)
                Clock.schedule_once(self.sendLastMonthReport, 0.3)

        elif self.popupForm == "includeWithoutNumbers":
            self.exportPhones(includeWithoutNumbers = True if instance.text.lower() == self.button["yes"] else False)

        elif self.popupForm == "timerPressed":
            if self.button["yes"] in instance.text.lower(): # первичный запуск таймера после подтверждения
                self.timerPressed(activate=True)
                if self.displayed.form == "rep": self.repPressed()
                elif self.displayed.form == "repLog": self.repPressed(jumpToLog=True)

        self.popupForm = ""

    def popup(self, popupForm="", message="", options=None, firstCall=False, title=None, checkboxText=None,
              dismiss=True, instance=None, *args):
        """ Всплывающее окно """

        # Специальный попап для первого посещения

        if options is None: options = ["Close"]
        if title is None: title = self.msg[203]
        separator = True
        if popupForm != "": self.popupForm = popupForm
        if options == ["Close"]: options = [self.msg[39]]
        size_hint = [.85, .6] if self.orientation == "v" else [.6, .85]
        auto_dismiss = dismiss

        # Добавление времени в отчет

        if self.popupForm == "showTimePicker":
            self.popupForm = ""
            size_hint[1] *= 1.1
            separator = False
            contentMain = BoxLayout(orientation="vertical", spacing=self.spacing*2)
            from circulartimepicker import CircularTimePicker

            tag = MyTextInput(id="serviceTag", text=self.serviceTag, # описание служения
                              hint_text=RM.msg[329], multiline=False, wired_border=False,
                              popup=True, size_hint_y=None, height=self.standardTextHeight)
            contentMain.add_widget(tag)

            picker = CircularTimePicker() # часы
            self.pickedTime = "00:00"
            def __setTime(instance, time):
                self.pickedTime = time
            picker.bind(time=__setTime)
            contentMain.add_widget(picker)
            save = PopupButton(text=self.msg[188], pos_hint={"bottom": 1})  # кнопка сохранения

            def __closeTimePicker(instance):
                self.dismissTopPopup()
                time2 = str(self.pickedTime)[:5] # время, выбранное на пикере (HH:MM)
                if title == self.msg[108]:
                    time1 = self.hours.get()  # исходное время на счетчике (HH:MM)
                    if self.pickedTime != "00:00":
                        self.time3 = ut.sumHHMM([time1, time2]) # сумма исходного и добавленного времени (HH:MM)
                        self.rep.modify(f"ч{time2}")
                        self.hours.update(self.time3)
                        hours = self.rep.getCurrentHours()[2]
                        info = f" {self.button['info']}" if hours != "" else ""
                        self.pageTitle.text = f"[b][ref=report]{self.msg[4]}[/b]{hours}{info}[/ref]"
                        if self.settings[0][2]: self.creditLabel.text = self.msg[105] % self.rep.getCurrentHours()[0]
                elif title == self.msg[109]:
                    time1 = self.credit.get()  # исходное время на счетчике (HH:MM)
                    if self.pickedTime != "00:00":
                        self.time3 = ut.sumHHMM([time1, time2])  # сумма двух времен в HH:MM
                        self.rep.modify(f"к{time2}")
                        self.credit.update(self.time3)
                        hours = self.rep.getCurrentHours()[2]
                        info = f" {self.button['info']}" if hours != "" else ""
                        self.pageTitle.text = f"[b][ref=report]{self.msg[4]}[/b]{hours}{info}[/ref]"
                        self.creditLabel.text = self.msg[105] % self.rep.getCurrentHours()[0]
            save.bind(on_release=__closeTimePicker)

            box = BoxLayout(size_hint_y=None)
            box.add_widget(save)
            box.add_widget(Widget(size_hint_x=.2))
            self.buttonClose = PopupButton(text=self.msg[190])
            self.buttonClose.bind(on_release=self.popupPressed)
            box.add_widget(self.buttonClose)
            contentMain.add_widget(box)

        # Выбор даты

        elif self.popupForm == "showDatePicker":
            self.popupForm = ""
            separator = False
            title = ""
            contentMain = BoxLayout(orientation="vertical", spacing=self.spacing*2)
            self.datePicked = DatePicker(padding=(0, 0, 0, self.padding*7))
            contentMain.add_widget(self.datePicked)
            self.buttonClose = PopupButton(text=self.msg[190], pos_hint={"bottom": 1})
            self.buttonClose.bind(on_release=self.popupPressed)
            contentMain.add_widget(self.buttonClose)

        # Добавление списка квартир

        elif self.popupForm == "addList":
            title = self.msg[191] if not self.house.listType() else self.msg[233].replace("#", " ")
            if self.orientation == "v": size_hint[1] *= self.fontScale()
            width = self.mainList.width * size_hint[0] * .9
            contentMain = BoxLayout(orientation="vertical")
            btnSave = PopupButton(
                text=f"{self.button['plus']} {self.msg[188].upper() if self.language != 'ka' else self.msg[188]}"
            )
            bBox = AnchorLayout(anchor_y="center", size_hint_y=None, height=btnSave.height*1.3)
            bBox.add_widget(btnSave)
            contentMain.add_widget(bBox)
            text = MyTextInput(hint_text=self.msg[185] if self.house.type == "condo" else self.msg[309],
                               wired_border=False, popup=True, multiline=True, shrink=False)
            contentMain.add_widget(text)
            if self.theme != "3D":
                btnPaste = PopupButtonGray(text=f"{icon('icon-paste')} {self.msg[186]}", size=(width, bBox.height))
            else:
                btnPaste = RetroButton(text=f"{icon('icon-paste')} {self.msg[186]}", size_hint_x=1, size_hint_y=None,
                                       width=width, height=bBox.height)
            def __paste(instance):
                text.text += Clipboard.paste()
            btnPaste.bind(on_release=__paste)
            contentMain.add_widget(btnPaste)
            description = MyLabel(text=self.msg[187] if self.house.type == "condo" else self.msg[245],
                                  text_size=(width, None), font_size=self.fontXS * self.fontScale(),
                                  valign="center", color=[.95, .95, .95])
            contentMain.add_widget(description)
            def __save(instance):
                self.porch.floorview = self.house.statsCached = None
                flats = text.text.strip()
                if flats != "":
                    newstr = ""
                    for char in flats:
                        if char == "\n": newstr += ","
                        elif self.house.type == "condo" and char == ".": newstr += ";"
                        else: newstr += char
                    if self.house.type == "private":
                        flats = [x for x in newstr.split(',')]
                    else:
                        flats = []
                        for x in newstr.split(','):
                            flats.append(x)
                    showWarning = False
                    for flat in flats:
                        try:
                            if self.house.type == "condo" and int(flat[0]) == 0: 5/0
                            else: pass
                        except: showWarning = True
                        else: self.porch.addFlat(f"{flat}")
                    self.dismissTopPopup(all=True)
                    if showWarning:
                        self.popup(title=self.msg[203], message=self.msg[250])
                        if len(self.porch.flats) == 0:
                            return
                    self.porch.scrollview = None
                    if self.house.type == "condo":
                        tempLayout = self.porch.flatsLayout
                        tempType = self.porch.type
                        if tempLayout == "н" and tempType[7:].isnumeric():
                            self.porch.adjustFloors(int(tempType[7:]))
                            self.porch.flatsLayout = "н"
                        else:
                            self.porch.adjustFloors()
                        self.porchView(instance=instance)
                        self.exitToPorch = True
                        if not showWarning:
                            self.positivePressed(instant=True)
                            self.positivePressed(instant=True)
                    else:
                        self.porchView(instance=instance)
                    self.save()
            btnSave.bind(on_release=__save)
            btnClose = PopupButton(text=self.msg[190])
            btnClose.bind(on_release=self.popupPressed)
            contentMain.add_widget(btnClose)
            self.popupForm = ""

        # Восстановление резервных копий

        elif self.popupForm == "restoreBackup":
            self.popupForm = ""
            title = self.msg[44]
            if self.orientation == "v": size_hint[1] *= self.fontScale()
            contentMain = BoxLayout(orientation="vertical", pos_hint={"top": 1})
            contentMain.add_widget(Label(text=self.msg[102], color=[.95, .95, .95], halign="left", valign="center",
                                         height=self.standardTextHeight*1.5, size_hint=(1, None),
                                         text_size=(self.mainList.width*size_hint[0]*.9, self.standardTextHeight*1.5)))

            self.fileDates = [] # собираем файлы резервных копий
            try:
                files = [f for f in os.listdir(self.backupFolderLocation) if os.path.isfile(os.path.join(self.backupFolderLocation, f))]
                files.sort(reverse=True)
            except:
                self.popup(title=self.msg[135], message=self.msg[257]) # файлов нет, выходим
                return

            for file in files:
                self.fileDates.append(str("{:%d.%m.%Y, %H:%M:%S}".format(
                    datetime.datetime.strptime(time.ctime((os.path.getmtime(self.backupFolderLocation + file))),
                                               "%a %b %d %H:%M:%S %Y"))) + f" ({os.path.getsize(self.backupFolderLocation + file)} B)")
            def __clickOnFile(instance): # обработка клика по файлу
                def __do(*args):
                    for i in range(len(files)):
                        if str("{:%d.%m.%Y, %H:%M:%S}".format(
                            datetime.datetime.strptime(time.ctime((os.path.getmtime(self.backupFolderLocation + files[i]))),
                                                       "%a %b %d %H:%M:%S %Y"))) in instance.text:
                            break
                    self.fileToRestore = i
                    self.popup("restoreRequest", title=self.msg[44], message=self.msg[45] % self.fileDates[i],
                               options=[self.button["yes"], self.button["no"]])
                Clock.schedule_once(__do, .05)

            btn = [] # раскладываем кнопки
            self.backups = ScrollView(size=(self.mainList.size[0] * .9, self.mainList.size[1] * .9),
                                     bar_width=self.standardBarWidth, scroll_type=['bars', 'content'])
            gridList = GridLayout(cols=1, size_hint_y=None, spacing=self.spacing * 2, padding=self.padding)
            gridList.bind(minimum_height=gridList.setter('height'))
            for i in range(len(self.fileDates)):
                if self.theme != "3D":
                    button = PopupButtonGray(text=self.fileDates[i], size_hint_y=None,
                                             height = self.standardTextHeight * 1.5,
                                             font_size=self.fontS * self.fontScale())
                else:
                    button = RetroButton(text=self.fileDates[i], size_hint_y=None, height=self.standardTextHeight * 1.5)
                btn.append(button)
                gridList.add_widget(btn[i])
                btn[i].bind(on_release=__clickOnFile)
            gridList.add_widget(Widget(height=self.standardTextHeight, size_hint_y=None))
            self.backups.add_widget(gridList)
            contentMain.add_widget(self.backups)
            grid = GridLayout(rows=2, cols=1, size_hint_y=None) # добавляем кнопку "Отмена"
            self.confirmButtonPositive = PopupButton(text=options[0], pos_hint={"bottom": 1})
            self.confirmButtonPositive.bind(on_release=lambda x=True: self.dismissTopPopup(all=x))
            grid.add_widget(Widget())
            grid.add_widget(self.confirmButtonPositive)
            contentMain.add_widget(grid)

        # Окно остановки таймера или паузы

        elif self.popupForm == "timerOff":
            self.popupForm = ""
            size_hint = (.93, .4 * self.fontScale(cap=1.2)) if self.orientation == "v" else (.6, .6)
            size = int(self.fontXXL * 1.3)
            contentMain = BoxLayout(orientation="vertical")
            a1 = AnchorLayout(size_hint_y=.2, anchor_x="center", anchor_y="center")
            contentMain.add_widget(a1)
            contentMain.add_widget(Widget(size_hint_y=None, height=self.standardTextHeight))
            tag = MyTextInput(id="serviceTag", text=self.serviceTag, hint_text=RM.msg[329], multiline=False,
                              wired_border=False, popup=True, size_hint_y=None, height=self.standardTextHeight)
            a1.add_widget(tag)
            grid = GridLayout(rows=1, cols=3, size_hint_y=.6, padding=self.padding, spacing=self.spacing)
            contentMain.add_widget(grid)

            button = RM.msg[324].replace("#", "\n")

            if self.theme != "3D":
                btn1 = PopupButton(text=f"[size={size}]{icon('icon-pause-circle')}[/size]\n\n{button}",
                                size_hint_y=1, cap=False)
            else:
                btn1 = RetroButton(text=f"[size={size}]{icon('icon-pause-circle')}[/size]\n\n{button}",
                                   size_hint_y=1)
            grid.add_widget(btn1)
            def __pauseTimer(instance):
                self.rep.modify("-")
                self.timer.pause()
                Clock.unschedule(self.updater)
                self.updater = Clock.schedule_interval(self.updateTimer, 1) if self.settings[0][22] else None
                self.dismissTopPopup()
            btn1.bind(on_release=__pauseTimer)

            button = RM.msg[325].replace("#", "\n")

            if self.theme != "3D":
                btn2 = PopupButton(text=f"[size={size}]{icon('icon-stop-circle')}[/size]\n\n{button}",
                                   size_hint_y=1, cap=False)
            else:
                btn2 = RetroButton(text=f"[size={size}]{icon('icon-stop-circle')}[/size]\n\n{button}",
                                   size_hint_y=1)
            grid.add_widget(btn2)
            def __stopHours(instance):
                self.rep.modify(")")
                self.timer.stop()
                if self.displayed.form == "rep": self.repPressed()
                elif self.displayed.form == "repLog": self.repPressed(jumpToLog=True)
                self.dismissTopPopup()
            btn2.bind(on_release=__stopHours)

            if self.settings[0][2]:
                button = RM.msg[326].replace("#", "\n")
                if self.theme != "3D":
                    btn3 = PopupButton(text=f"[size={size}]{icon('icon-stop-circle')}[/size]\n\n{button}",
                                       size_hint_y=1, cap=False)
                else:
                    btn3 = RetroButton(text=f"[size={size}]{icon('icon-stop-circle')}[/size]\n\n{button}",
                                       size_hint_y=1)
                grid.add_widget(btn3)
                def __stopCredit(instance):
                    self.rep.modify("$")
                    self.timer.stop()
                    if self.displayed.form == "rep": self.repPressed()
                    elif self.displayed.form == "repLog": self.repPressed(jumpToLog=True)
                    self.dismissTopPopup()
                btn3.bind(on_release=__stopCredit)

            box = BoxLayout(size_hint_y=.2) # отмена
            self.confirmButtonPositive = PopupButton(text=options[0])
            self.confirmButtonPositive.bind(on_release=self.popupPressed)
            box.add_widget(self.confirmButtonPositive)
            contentMain.add_widget(box)

        # Стандартное информационное окно либо запрос да/нет

        else:
            size_hint = (.93, .17 * (self.fontScale()*2)) if self.orientation == "v" else (.6, .5)
            text_size = Window.size[0] * size_hint[0] * .92, None
            contentMain = BoxLayout(orientation="vertical")
            if checkboxText is not None: contentMain.add_widget(Widget())
            label = MyLabel(text=message, halign="left", valign="center", text_size=text_size,
                            font_size=self.fontXS*self.fontScale(cap=1.3),
                            color=[.95, .95, .95])
            contentMain.add_widget(label)

            if checkboxText is not None: # задана галочка
                self.popupCheckbox = FontCheckBox(text=checkboxText, halign="right", valign="bottom",
                                                  size_hint=(1, None), color="lightgray", button_color=self.titleColorOnBlack,
                                                  height=self.standardTextHeight,
                                                  font_size=self.fontXS*self.fontScale(cap=1.2))
                contentMain.add_widget(Widget(size_hint_y=.2))
                contentMain.add_widget(self.popupCheckbox)
                contentMain.add_widget(Widget(size_hint_y=.4))

            if len(options) > 0: # заданы кнопки
                box = BoxLayout(size_hint_y=None)
                self.confirmButtonPositive = PopupButton(text=options[0])
                self.confirmButtonPositive.bind(on_release=self.popupPressed)
                box.add_widget(self.confirmButtonPositive)
                if len(options) > 1: # если кнопок несколько
                    auto_dismiss = False
                    box.add_widget(Widget(size_hint_x=.2))
                    self.confirmButtonNegative = PopupButton(text=options[1])
                    self.confirmButtonNegative.bind(on_release=self.popupPressed)
                    box.add_widget(self.confirmButtonNegative)
                contentMain.add_widget(box)

        self.popups.insert(
            0,
            PopupNoAnimation(title=title, content=contentMain, size_hint=size_hint, auto_dismiss=auto_dismiss,
                             separator_color=self.titleColorOnBlack if separator else [0, 0, 0, 0])
        )

        if firstCall:
            def __gotoPorch(instance):
                self.displayed.form = "porchView"
                self.displayed.options = self.porch.showFlats()
            self.popups[0].bind(on_dismiss=__gotoPorch)
            self.popupForm = ""
        Clock.schedule_once(self.popups[0].open, 0)

    def dismissTopPopup(self, all=False, *args):
        """ Закрывает и удаляет самый верхний попап в стеке """
        if len(self.popups) == 0:
            return
        elif not all:
            self.popups[0].dismiss()
            del self.popups[0]
        else: # закрываем и удаляем вообще все попапы
            for popup in self.popups:
                popup.dismiss()
            del self.popups[:]

    def loadLanguages(self):
        """ Загружает csv-файл с языками, если есть """
        import csv
        import glob
        languages = []
        for l in self.languages.keys(): languages.append([])
        dir = "c:\\Users\\antor\\Downloads\\" if os.name == "nt" else "/home/antorix/Загрузки/"
        filenames = glob.glob(dir + "Rocket Ministry localization sheet*.csv")
        def __generate(file, col):
            with open(file, "w", encoding="utf-8") as f:
                for row in languages[col]:
                    f.write(row + "\n")
        try:
            with open(filenames[0], newline='', encoding="utf8") as csvfile:
                file = csv.reader(csvfile)
                for row in file:
                    for col in range(len(languages)):
                        languages[col].append(row[col].strip())
        except:
            self.dprint("CSV-файл с локализациями не найден.")
        else:
            self.dprint("CSV-файл с локализациями найден, обновляю языковые файлы.")
            with open("lpath.ini", encoding='utf-8', mode="r") as f: lpath = f.read()
            for i in range(len(self.languages.keys())):
                __generate(f"{list(self.languages.keys())[i]}.lang", i) # в Linux с относительным путем
            for zippath in glob.iglob(os.path.join(dir, '*.csv')):
                os.remove(zippath)

    def update(self, forced=False):
        """ Проверяем новую версию и при наличии обновляем программу с GitHub """
        if not forced and (not self.desktop or Devmode): return  # мобильная версия не проверяет обновления, а также в режиме разработчика
        else: self.dprint("Проверяем обновления настольной версии.")

        def __update(threadName, delay):
            try:  # подключаемся к GitHub
                for line in requests.get("https://raw.githubusercontent.com/antorix/rocket-ministry/master/version"):
                    newVersion = line.decode('utf-8').strip()
            except:
                self.dprint("Не удалось подключиться к серверу.")
            else:  # успешно подключились
                self.dprint(f"Версия на сайте: {newVersion}")
                today = str(datetime.datetime.strptime(time.strftime('%Y-%m-%d'), "%Y-%m-%d"))
                today = today[0: today.index(" ")]
                self.settings[1] = today
                if newVersion > Version:
                    Clock.schedule_once(lambda x: self.popup(message=self.msg[310], dismiss=False), 5)
                    self.dprint("Найдена новая версия, скачиваем.")
                    response = requests.get("https://github.com/antorix/rocket-ministry/archive/refs/heads/master.zip")
                    import tempfile
                    import zipfile
                    file = tempfile.TemporaryFile()
                    file.write(response.content)
                    fzip = zipfile.ZipFile(file)
                    fzip.extractall("")
                    file.close()
                    downloadedFolder = "rocket-ministry-master"
                    for file_name in os.listdir(downloadedFolder):
                        source = downloadedFolder + "/" + file_name
                        destination = file_name
                        if os.path.isfile(source):
                            if not "icomoon.ttf" in source: shutil.move(source, destination)
                            else: shutil.move(source, "icomoon_updated.ttf")
                    shutil.rmtree(downloadedFolder)
                elif forced:
                    Clock.schedule_once(lambda x: self.popup(message="Обновлений нет."), 1)
                else: self.dprint("Обновлений нет.")
        _thread.start_new_thread(__update, ("Thread-Update", 0,))

    def monthName(self, monthCode=None, monthNum=None):
        """ Returns names of current and last months in lower and upper cases """
        if monthCode is not None:   month = monthCode
        elif monthNum is not None:
            if monthNum == 1:   month = "Jan"
            elif monthNum == 2: month = "Feb"
            elif monthNum == 3: month = "Mar"
            elif monthNum == 4: month = "Apr"
            elif monthNum == 5: month = "May"
            elif monthNum == 6: month = "Jun"
            elif monthNum == 7: month = "Jul"
            elif monthNum == 8: month = "Aug"
            elif monthNum == 9: month = "Sep"
            elif monthNum == 10:month = "Oct"
            elif monthNum == 11:month = "Nov"
            elif monthNum == 12:month = "Dec"
        else:                   month = time.strftime("%b", time.localtime())

        if month == "Jan":
            curMonthUp = self.msg[259]
            curMonthLow = self.msg[260]
            lastMonthUp = self.msg[261]
            lastMonthLow = self.msg[262]
            lastMonthEn = "Dec"
            curMonthRuShort = self.msg[283]
            monthNum = 1
            lastTheoMonthNum = 4
            curTheoMonthNum = 5
        elif month == "Feb":
            curMonthUp = self.msg[263]
            curMonthLow = self.msg[264]
            lastMonthUp = self.msg[259]
            lastMonthLow = self.msg[260]
            lastMonthEn = "Jan"
            curMonthRuShort = self.msg[284]
            monthNum = 2
            lastTheoMonthNum = 5
            curTheoMonthNum = 6
        elif month == "Mar":
            curMonthUp = self.msg[265]
            curMonthLow = self.msg[266]
            lastMonthUp = self.msg[263]
            lastMonthLow = self.msg[264]
            lastMonthEn = "Feb"
            curMonthRuShort = self.msg[285]
            monthNum = 3
            lastTheoMonthNum = 6
            curTheoMonthNum = 7
        elif month == "Apr":
            curMonthUp = self.msg[267]
            curMonthLow = self.msg[268]
            lastMonthUp = self.msg[265]
            lastMonthLow = self.msg[266]
            lastMonthEn = "Mar"
            curMonthRuShort = self.msg[286]
            monthNum = 4
            lastTheoMonthNum = 7
            curTheoMonthNum = 8
        elif month == "May":
            curMonthUp = self.msg[269]
            curMonthLow = self.msg[270]
            lastMonthUp = self.msg[267]
            lastMonthLow = self.msg[268]
            lastMonthEn = "Apr"
            curMonthRuShort = self.msg[287]
            monthNum = 5
            lastTheoMonthNum = 8
            curTheoMonthNum = 9
        elif month == "Jun":
            curMonthUp = self.msg[271]
            curMonthLow = self.msg[272]
            lastMonthUp = self.msg[269]
            lastMonthLow = self.msg[270]
            lastMonthEn = "May"
            curMonthRuShort = self.msg[288]
            monthNum = 6
            lastTheoMonthNum = 9
            curTheoMonthNum = 10
        elif month == "Jul":
            curMonthUp = self.msg[273]
            curMonthLow = self.msg[274]
            lastMonthUp = self.msg[271]
            lastMonthLow = self.msg[272]
            lastMonthEn = "Jun"
            curMonthRuShort = self.msg[289]
            monthNum = 7
            lastTheoMonthNum = 10
            curTheoMonthNum = 11
        elif month == "Aug":
            curMonthUp = self.msg[275]
            curMonthLow = self.msg[276]
            lastMonthUp = self.msg[273]
            lastMonthLow = self.msg[274]
            lastMonthEn = "Jul"
            curMonthRuShort = self.msg[290]
            monthNum = 8
            lastTheoMonthNum = 11
            curTheoMonthNum = 12
        elif month == "Sep":
            curMonthUp = self.msg[277]
            curMonthLow = self.msg[278]
            lastMonthUp = self.msg[275]
            lastMonthLow = self.msg[276]
            lastMonthEn = "Aug"
            curMonthRuShort = self.msg[291]
            monthNum = 9
            lastTheoMonthNum = 12
            curTheoMonthNum = 1
        elif month == "Oct":
            curMonthUp = self.msg[279]
            curMonthLow = self.msg[280]
            lastMonthUp = self.msg[277]
            lastMonthLow = self.msg[278]
            lastMonthEn = "Sep"
            curMonthRuShort = self.msg[292]
            monthNum = 10
            lastTheoMonthNum = 1
            curTheoMonthNum = 2
        elif month == "Nov":
            curMonthUp = self.msg[281]
            curMonthLow = self.msg[282]
            lastMonthUp = self.msg[279]
            lastMonthLow = self.msg[280]
            lastMonthEn = "Oct"
            curMonthRuShort = self.msg[293]
            monthNum = 11
            lastTheoMonthNum = 2
            curTheoMonthNum = 3
        else:  # Dec
            curMonthUp = self.msg[261]
            curMonthLow = self.msg[262]
            lastMonthUp = self.msg[281]
            lastMonthLow = self.msg[282]
            lastMonthEn = "Nov"
            curMonthRuShort = self.msg[294]
            monthNum = 12
            lastTheoMonthNum = 3
            curTheoMonthNum = 4

        return curMonthUp, curMonthLow, lastMonthUp, lastMonthLow, lastMonthEn,\
               curMonthRuShort, monthNum, lastTheoMonthNum, curTheoMonthNum

    def getLog(self, id):
        """ Получает номер на элемент записи журнала и возвращает отдельные его элементы в виде строк """
        entry = self.resources[2][id]
        time = entry[:18].strip() # время
        if "|" in entry:
            body = entry[20: entry.index("|")].strip() # основная запись
            tag = entry[entry.index("|") + 1:].strip() # подпись
        else:
            body = entry[20:].strip()  # основная запись
            tag = ""
        return [time, body, tag]

    def checkDate(self, *args):
        """ Проверка сегодняшней даты. Если она изменилась, делаем резервную копию, обнуляется house.due и проверяется отчет """
        if self.today == time.strftime('%d', time.localtime()):
            self.dprint("Дата не изменилась.")
        else:
            self.dprint("Изменилась дата.")
            self.rep.checkNewMonth()
            for house in self.houses: house.dueCached = None
            self.save(backup=True)
            self.today = time.strftime("%d", time.localtime())

    def dprint(self, text):
        """ Вывод отладочной информации в режиме разработчика """
        if Devmode: print(text)

    # Системные функции

    def on_pause(self):
        """ На паузе приложения """
        self.cacheFreeModeGridPosition()
        if self.porch is not None: self.porch.scrollview = None
        # перезагружаем кеш списка подъезда для решения бага, когда после возврата из паузы весь подъезд пропадает
        self.checkDate()
        self.save(verify=True)
        return True

    @mainthread
    def loadShared(self):
        """ Получение загруженного файла на Android """
        if self.openedFile is not None:
            self.importDB(file=self.openedFile)
            self.openedFile = None
        return True

    def restart(self, mode="hard"):
        """ Перезапуск либо перерисовка """
        if mode == "soft": # простая перерисовка интерфейса
            self.interface.clear_widgets()
            self.noDataFileActions()
            self.setParameters(reload=True)
            self.setTheme()
            self.createInterface()
            Clock.schedule_once(lambda x: self.terPressed(instance=self.settingsButton, updateStack=False), 0)
        else: # полная перезагрузка приложения
            if platform == "android":
                from kvdroid.tools import restart_app
                restart_app()
            elif self.desktop:
                self.stop()
                from os import startfile
                startfile("main.py" if not Devmode else "rm_dev.bat")
            else:
                self.stop() # просто выход, в крайнем случае

    def hook_keyboard(self, window, key, *largs):
        """ Обрабатывает кнопку "назад" на мобильных устройствах и Esc на ПК """
        if key == 27:
            if not self.backButton.disabled: # если можно нажать на "назад"
                Clock.schedule_once(lambda x: self.backPressed(instance=self.backButton), 0)

            # "Назад" нажать нельзя:

            elif platform == "android":
                if self.displayed.form == "ter":
                    self.dismissTopPopup(all=True)
                    self.save()
                    activity.moveTaskToBack(True)
            elif not self.desktop:
                self.save()
                self.stop()
            else:
                self.dismissTopPopup(all=True)

            return True

    # Работа с базой данных

    def initializeDB(self):
        """ Возвращает исходные значения houses, settings, resources """
        return [], \
               [
                   [1, 5, 0, 0, "и", "", "", None, 5, 0, 1, 1, 1, 0, "", 1, 0, "", "5", "д", 1, "sepia", 1], # program settings
                   "",  # дата последнего обновления    settings[1]
                   # report:                            settings[2]
                   [0.0, # [0] hours                    settings[2][0…]
                    0.0, # [1] credit
                    0,   # [2] placements
                    0,   # [3] videos
                    0,   # [4] returns,
                    0,   # [5] studies,
                    0,   # [6] startTime
                    0,   # [7] endTime
                    0.0, # [8] reportTime
                    0, # [9] pauseTime
                    "",  # [10] note
                    0,   # [11] to remind submit report (0: already submitted) - не используется с 2.0
                    ""   # [12] отчет прошлого месяца
                    ],
                   time.strftime("%b", time.localtime()),  # month of last save: settings[3]
                   [None, None, None, None, None, None, None, None, None, None, None, None]  # service year: settings[4]
               ], \
               [
                   ["",  # resources[0][0] = notepad
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # resources[0][1] = флаги о подсказках (когда показана, ставим 1)
                    ],
                   # resources[0][1][0] - показана подсказка про уменьшение этажа
                   # resources[0][1][1] - показана подсказка про масштабирование подъезда
                   # resources[0][1][2] - показана подсказка про таймер
                   # resources[0][1][3] - показана подсказка про переключение вида подъезда
                   # resources[0][1][4] - показана подсказка про кнопку «Нет дома»
                   # resources[0][1][5] - показана подсказка про первого интересующегося
                   # resources[0][1][6] - показана подсказка про возвращение подъезда в исходное положение
                   # resources[0][1][7] - показана подсказка про экран первого посещения
                   # resources[0][1][8] - показана подсказка про версию для Windows/Linux
                   # resources[0][1][9] - показан запрос про месячную норму

                   [],  # standalone contacts   resources[1]
                   [],  # report log            resources[2]
               ]

    def load(self, DataFile=None, allowSave=True, forced=False, clipboard=None, silent=False):
        """ Loading houses and settings from JSON file """
        if Devmode: self.loadLanguages()
        if DataFile is None: DataFile = self.dataFile
        self.popupForm = ""
        self.error = None  # отладочный флаг
        self.dprint("Загружаю буфер.")

        # Замена data.jsn файлом с телефона - недокументированная функция, только на русском языке

        if platform == "win" and os.path.exists("import.ini"):
            with open("import.ini", encoding='utf-8', mode="r") as f: importPath = f.read()
            if os.path.exists(importPath + "Данные Rocket Ministry.txt"):
                os.remove(self.userPath + "data.jsn")
                shutil.move(importPath + "Данные Rocket Ministry.txt", os.path.abspath(os.getcwd()))
                os.rename("Данные Rocket Ministry.txt", "data.jsn")
                plyer.notification.notify(app_name="Rocket Ministry", title="Rocket Ministry", app_icon="icon.ico",
                                          ticker="Rocket Ministry", message="Импортирован файл с телефона!", timeout=3)

        # Начинаем загрузку, сначала получаем буфер

        buffer = []

        if clipboard is not None:  # импорт из буфера обмена недокументированным способом через строку поиска
            self.dprint("Смотрим буфер обмена.")
            clipboard = str(clipboard).strip()
            try:
                clipboard = clipboard[clipboard.index("[\"Rocket Ministry"):]
                with open("data.jsn", "w") as file: file.write(clipboard)
                self.dprint("База данных перезаписана из буфера обмена, перезагружаемся!")
            except: return False
            else:
                self.restart()

        if forced:  # импорт по запросу с конкретным файлом
            try:
                with open(DataFile, "r") as file: buffer = json.load(file)
                self.dprint("Буфер получен из импортированного файла.")
            except:
                if not silent: self.popup(message=self.msg[244])
                return False

        else:  # обычная загрузка
            if os.path.exists(self.userPath + DataFile):
                try:
                    with open(self.userPath + DataFile, "r") as file: buffer = json.load(file)
                except:
                    message = "Файл данных найден, но поврежден. Пытаюсь восстановить резервную копию."
                    self.dprint(message)
                    self.error = message
                    if self.backupRestore(restoreNumber=0, allowSave=allowSave):
                        self.dprint("База восстановлена из резервной копии 1.")
                        return True
                    else: self.dprint("Не удалось восстановить непустую резервную копию (ее нет?).")
                else: self.dprint("Буфер получен из файла data.jsn в стандартном местоположении.")
            else:
                message = "Файл данных не найден, пытаюсь восстановить резервную копию."
                self.dprint(message)
                self.error = message
                if self.backupRestore(restoreNumber=0, allowSave=allowSave):
                    self.dprint("База восстановлена из резервной копии 2.")
                    return True
                else: self.dprint("Не удалось восстановить последнюю резервную копию (ее нет?).")

        # Буфер получен, читаем из него

        if len(buffer) == 0: self.dprint("Создаю новую базу.")

        elif "Rocket Ministry application data file." in buffer[0]:
            singleTer = 1 if "Single territory export" in buffer[0] else 0
            self.dprint("База определена, контрольная строка совпадает.")
            del buffer[0]
            result = self.loadOutput(buffer, singleTer) # ЗАГРУЗКА ИЗ БУФЕРА, RESULT УКАЗЫВАЕТ НА УСПЕХ/НЕУСПЕХ
            if not result:
                message = "Ошибка загрузки из буфера."
                self.dprint(message)
                self.error = message
                if self.backupRestore(restoreNumber=0, allowSave=allowSave):
                    self.dprint("База восстановлена из резервной копии 3.")
                    return True
            else:
                message = "База успешно загружена."
                self.dprint(message)
                return True
        else:
            message = "База получена, но контрольная строка в файле не совпадает."
            self.dprint(message)
            self.error = message
            if clipboard is None and not forced:
                self.dprint("Восстанавливаю резервную копию.")
                if self.backupRestore(restoreNumber=0):
                    self.dprint("База восстановлена из резервной копии 4.")
                    return True

    def importDB(self, file, instance=None):
        """ Импорт данных из буфера обмена либо файла """
        self.save()
        self.dprint("Пытаюсь загрузить базу из файла.")
        success = self.load(forced=True, DataFile=file, silent=True) # сначала пытаемся загрузить файл
        if not success: self.popup(message=self.msg[208])
        else:
            self.save()
            self.restart("soft")
            self.terPressed()
            Clock.schedule_once(lambda x: self.popup(message=self.msg[209]), 0.2)

    def backupRestore(self, silent=True, allowSave=True, delete=False, restoreNumber=None):
        """ Восстановление файла из резервной копии """
        try:
            files = [f for f in os.listdir(self.backupFolderLocation) if \
                     os.path.isfile(os.path.join(self.backupFolderLocation, f))]
        except:
            self.dprint("Не найдена папка резервных копий.")
            return

        fileDates = []
        for i in range(len(files)):
            fileDates.append(str("{:%d.%m.%Y, %H:%M:%S}".format(
                datetime.datetime.strptime(time.ctime((os.path.getmtime(self.backupFolderLocation + files[i]))),
                                           "%a %b %d %H:%M:%S %Y"))))

        if restoreNumber is not None:  # восстановление файла по номеру
            files.sort(reverse=True)
            fileDates.sort(reverse=True)
            try: self.load(forced=True, allowSave=allowSave, DataFile=self.backupFolderLocation + files[restoreNumber])
            except:
                message = f"Не удалось восстановить резервную копию № {restoreNumber}: {files[restoreNumber]}"
                self.dprint(message)
                if not silent:
                    try: self.popup(message=message)
                    except: self.error = message
                return False
            else:
                message = f"Успешно восстановлена резервная копия № {restoreNumber}: {files[restoreNumber]}"
                self.dprint(message)
                if not silent:
                    try: self.popup(message=message)
                    except: self.error = message
                return fileDates[restoreNumber]  # в случае успеха возвращает дату и время восстановленной копии

        # Если выбран режим удаления лишних копий

        elif delete == True and not Devmode:
            def __cut(*args):
                files.sort()
                self.dprint("Урезаем резервные копии до лимита.")
                limit = 9 # -1, потому что сразу после обрезки создается новая резервная копия на старте
                if len(files) > limit:  # лимит превышен, удаляем
                    extra = len(files) - limit
                    for i in range(extra):
                        self.dprint(f"Удаляю лишний резервный файл: {files[i]}")
                        os.remove(self.backupFolderLocation + files[i])
            if self.desktop: _thread.start_new_thread(__cut, ("Thread-Cut", 1,))
            else: __cut()

    def save(self, backup=False, silent=True, export=False, verify=False):
        """ Saving database to JSON file """
        output = self.getOutput()

        # Сначала резервируем

        if backup:
            self.dprint(f"Резервирование. Размер output: {len(str(output))}")
            if not os.path.exists(self.backupFolderLocation):
                try: os.makedirs(self.backupFolderLocation)
                except IOError:
                    if not silent: self.log(self.msg[248])
                    return
            savedTime = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
            bkFile = f"{self.backupFolderLocation}data_{savedTime}.jsn"
            for count in range(1, 6):
                try:
                    with open(bkFile, "w") as newbkfile: json.dump(output, newbkfile)
                    with open(bkFile, "r") as newbkfile: buffer = json.load(newbkfile) # проверка созданнного файла
                    self.dprint(f"Размер buffer: {len(str(buffer))}")
                    if len(str(output)) == len(str(buffer)):
                        self.dprint("buffer совпадает c output: резервирование успешно!")
                        if not silent: Clock.schedule_once(lambda x: self.popup(message=self.msg[56]), .1)
                        break
                    else:
                        self.dprint("buffer НЕ совпадает c output: резервирование не успешно, повторяем...")
                        time.sleep(.1*count)
                except: pass
            else:
                message = f"Не удалось создать корректную резервную копию после {count} попыток! Удаляем файл {bkFile} и перезагружаемся..."
                self.dprint(message)
                os.remove(bkFile)
                self.restart()

        # Сохраняем
        for count in range(1, 6):
            try:
                with open(self.userPath + self.dataFile, "w") as file: json.dump(output, file)
            except:
                message1 = f"Ошибка записи базы! "
                if count < 5: message2 = f"Делаем попытку № {count}..."
                elif not backup: message2 = f"Не получилось сохранить после {count} попыток!"
                self.dprint(message1 + message2)
                time.sleep(.01)
            else:
                if not verify:
                    self.dprint("База успешно сохранена.")
                    break
                else: # если сохранение с проверкой записи
                    verified = False
                    with open(self.userPath + self.dataFile, "r") as file: buffer = json.load(file)
                    message1 = f"Проверка сохраненного файла.\nРазмер output: {len(str(output))}. Размер buffer: {len(str(buffer))}.\n"
                    if len(str(output)) == len(str(buffer)):
                        message2 = "Успешно!"
                        verified = True
                        self.dprint(message1 + message2)
                    else: message2 = f"Ошибка! Пробуем еще раз, попытка № {count}..."
                    self.dprint(message1 + message2)
                    if verified: break
                    else: time.sleep(0.1)
        else:
            message =  f"Не удалось корректно сохранить базу после {count} попыток!"
            message +=  "\nПроверки не было. Запускаю проверку через 5 секунд" if not verify else\
                        "\nПроверка была. Запускаю резервирование через 10 секунд."
            self.dprint(message)
            if not verify: Clock.schedule_once(lambda x: self.save(verify=True), 5)  # если не было проверки, запускаем повторно с проверкой
            else: Clock.schedule_once(lambda x: self.save(backup=True), 10)  # если была проверка и не помогла, запускаем резервирование

        # Экспорт в файл на ПК, если найден файл sync.ini, где прописан путь

        if export and not Devmode and os.path.exists("sync.ini"):
            self.dprint("Найден sync.ini, экспортируем.")
            try:
                with open("sync.ini", encoding='utf-8', mode="r") as f: filename = f.read()
                with open(filename, "w") as file: json.dump(output, file)
            except: self.dprint("Ошибка записи в файл.")

    def getOutput(self, ter=None):
        """ Возвращает строку со всеми данными программы, которые затем либо сохраняются локально, либо экспортируются"""
        if ter is None: # экспорт всей базы
            output = ["Rocket Ministry application data file. Do NOT edit manually!"] + [self.settings] + \
                     [[self.resources[0], [self.resources[1][i].export() for i in range(len(self.resources[1]))], self.resources[2]]]
            for house in self.houses:
                output.append(house.export())
        else: # экспорт одного участка
            output = ["Rocket Ministry application data file. Do NOT edit manually! Single territory export."] + [self.settings] + \
                     [[self.resources[0], [self.resources[1][i].export() for i in range(len(self.resources[1]))], self.resources[2]]]
            output.append(ter.export())
        return output

    def houseRetrieve(self, containers, housesNumber, h):
        """ Retrieves houses from JSON buffer into objects """
        for a in range(housesNumber):
            self.addHouse(containers, h[a][0], h[a][4])  # creating house and writing its title and type
            cont = containers[a]
            cont.porchesLayout = h[a][1]
            cont.date = h[a][2]
            cont.note = h[a][3]
            porches = h[a][5]
            for b in range(len(porches)):
                cont.porches.append(
                    Porch(title=porches[b][0], pos=porches[b][1], flatsLayout=porches[b][2],
                          floor1=porches[b][3], note=porches[b][4], type=porches[b][5]))
                flats = porches[b][6]
                for c in range(len(flats)):

                    if len(flats[c]) == 7:  # добавление новых данных в версии 2.13.000
                        flats[c].insert(6, 0) # вторичный цвет
                        flats[c].insert(7, "") # смайлик
                        flats[c].insert(8, []) # пустой список на будущее

                    currentPorch = cont.porches[len(cont.porches)-1] # текущий подъезд
                    cont.porches[b].flats.append(
                        Flat(title=flats[c][0], note=flats[c][1], number=flats[c][2], status=flats[c][3],
                             phone=flats[c][4], lastVisit=flats[c][5], color2=flats[c][6], porchRef=currentPorch,
                             emoji=flats[c][7], extra=flats[c][8]))
                    records = flats[c][9]
                    for d in range(len(records)):
                        cont.porches[b].flats[c].records.append(Record(date=records[d][0], title=records[d][1]))

    def loadOutput(self, buffer, singleTer):
        """ Загружает данные из буфера """
        try:
            if singleTer: # загрузка только одного участка, который добавляется к уже существующей базе
                a = len(self.houses)
                self.addHouse(self.houses, buffer[2][0], buffer[2][4])  # creating house and writing its title and type
                house = self.houses[a]
                house.porchesLayout = buffer[2][1]
                house.date = buffer[2][2]
                house.note = buffer[2][3]
                porches = buffer[2][5]
                for b in range(len(porches)):
                    house.porches.append(
                        Porch(title=porches[b][0], pos=porches[b][1], flatsLayout=porches[b][2],
                              floor1=porches[b][3], note=porches[b][4], type=porches[b][5]))
                    flats = porches[b][6]
                    for c in range(len(flats)):

                        if len(flats[c]) == 7:  # добавление новых данных в версии 2.13.000
                            flats[c].insert(6, 0)  # вторичный цвет
                            flats[c].insert(7, "")  # смайлик
                            flats[c].insert(8, [])  # пустой список на будущее

                        currentPorch = house.porches[len(house.porches)-1] # текущий подъезд
                        house.porches[b].flats.append(
                            Flat(title=flats[c][0], note=flats[c][1], number=flats[c][2], status=flats[c][3],
                                 phone=flats[c][4], lastVisit=flats[c][5], color2=flats[c][6], porchRef=currentPorch,
                                 emoji=flats[c][7], extra=flats[c][8]))
                        records = flats[c][9]
                        for d in range(len(records)):
                            house.porches[b].flats[c].records.append(
                                Record(date=records[d][0], title=records[d][1]))

            else: # загрузка и обновление базы целиком
                self.clearDB()

                self.settings[0] = buffer[0][0]  # загружаем настройки
                self.settings[1] = buffer[0][1]
                self.settings[2] = buffer[0][2]
                self.settings[3] = buffer[0][3]
                self.settings[4] = buffer[0][4]
                if len(self.settings[0]) == 22: self.settings[0].append(1)

                self.resources[0] = buffer[1][0]  # загружаем блокнот

                self.resources[1] = []  # загружаем отдельные контакты
                virHousesNumber = int(len(buffer[1][1]))
                hr = []
                for s in range(virHousesNumber):
                    hr.append(buffer[1][1][s])
                self.houseRetrieve(self.resources[1], virHousesNumber, hr)

                self.resources[2] = buffer[1][2]  # загружаем журнал отчета

                housesNumber = int(len(buffer)) - 2  # загружаем участки
                h = []
                for s in range(2, housesNumber + 2):
                    h.append(buffer[s])
                self.houseRetrieve(self.houses, housesNumber, h)

                # Конвертации данных устаревших версий

                if len(self.resources[0]) == 0: # конвертация заметок блокнота версии 1.x
                    self.resources[0].append("")
                elif len(self.resources[0]) > 1 and isinstance(self.resources[0][1], str):
                    notes = ""
                    for note in self.resources[0]:
                        notes += note + "\n"
                    del self.resources[0][:]
                    self.resources[0].append(notes)

                if len(self.resources[0]) == 1:
                    self.resources[0].append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # добавляем для новой версии новый массив

                if self.settings[0][5] == "default": # конвертация темы "сепия" старой версии в новую
                    self.settings[0][5] = "sepia"

                if "." in str(self.settings[0][8]): self.settings[0][8] = 5

                if self.settings[0][10] == 0: self.settings[0][10] = 1 # кол-во колонок

        except: return False
        else:   return True

    def clearDB(self, silent=True):
        """ Очистка базы данных """
        self.houses.clear()
        self.settings.clear()
        self.resources.clear()
        self.settings[:] = self.initializeDB()[1][:]
        self.resources[:] = self.initializeDB()[2][:]
        if not silent: self.log(self.msg[242])

    def removeFiles(self, keepDatafile=False):
        """ Удаление базы данных и резервной папки """
        if os.path.exists(self.userPath + self.dataFile) and not keepDatafile: os.remove(self.userPath + self.dataFile)
        if os.path.exists(self.backupFolderLocation): shutil.rmtree(self.backupFolderLocation)

    def share(self, silent=False, clipboard=False, email=False, folder=None, file=False, ter=None, create_chooser=True):
        """ Sharing database """
        output = self.getOutput(ter=ter)
        buffer = json.dumps(output)

        if clipboard: # копируем базу в буфер обмена - нигде не используется, но возможно
            try:
                s = str(buffer)
                Clipboard.copy(s)
            except: return

        elif email: # экспорт в сообщении
            if not self.desktop:
                plyer.email.send(subject=self.msg[251] if ter is None else ter.title,
                                 text=str(buffer), create_chooser=create_chooser)
            else: # на компьютере просто кладем в буфер обмена
                Clipboard.copy(str(buffer))
                self.popup(message=self.msg[133])

        elif file: # экспорт в локальный файл на устройстве
            if self.desktop:
                try:
                    from tkinter import filedialog
                    folder = filedialog.askdirectory()
                    if folder == "" or len(folder) == 0: return # пользователь отменил экспорт
                    filename = folder + f"/{self.msg[251] if ter is None else ter.title}.txt"
                    with open(filename, "w") as file: json.dump(output, file)
                except:
                    self.dprint("Экспорт в файл не удался.")
                    if folder != "": self.popup(message=self.msg[308])
                else: self.popup(message=self.msg[252] % filename)

            elif platform == "android":
                filename = os.path.join(
                    SharedStorage().get_cache_dir(),
                    f"{self.msg[251] if ter is None else ter.title}.txt")
                with open(filename, "w") as file: json.dump(output, file)
                shared_file = SharedStorage().copy_to_shared(private_file=filename) # копируем в папку "Документы" на телефоне
                self.popup(message=self.msg[253])

        elif not Devmode and folder is not None: # экспорт в файл
            try:
                with open(folder + "/data.jsn", "w") as file: json.dump(output, file)
            except: self.popup(message=self.msg[132])
            else:   self.popup(message=self.msg[254] % folder + "/data.jsn")

        else:
            try:
                with open(os.path.expanduser("~") + "/data_backup.jsn", "w") as file: json.dump(output, file)
                path = os.path.expanduser("~")
            except:
                if not silent: self.popup(message=self.msg[255])
            else:
                if not silent: self.popup(message=self.msg[256] % path)


RM = RMApp()

if __name__ == "__main__":
    RM.run()
