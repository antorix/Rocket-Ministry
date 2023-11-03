#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import argv
Devmode = 1 if "dev" in argv else 0

Version = "2.10.001"

"""
* Исправлен баг, при котором программа падала при выборе турецкого языка.
* Мелкие исправления и оптимизации.
"""

import utils as ut
import time
import os
import json
import shutil
import datetime
import _thread
import webbrowser
from functools import partial
from random import random
from copy import copy, deepcopy
from iconfonts import icon
from iconfonts import register

try:
    from kivy.app import App
    import plyer
    import requests
except:
    if Devmode: print("Модуль kivy, plyer или requests не найден, устанавливаю.")
    from subprocess import check_call
    from sys import executable
    check_call([executable, '-m', 'pip', 'install', 'kivy==2.1.0'])
    check_call([executable, '-m', 'pip', 'install', 'plyer'])
    check_call([executable, '-m', 'pip', 'install', 'requests'])
    from kivy.app import App
    import plyer
    import requests

from kivy import platform
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
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
from kivy.clock import Clock
from kivy.uix.slider import Slider
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_hex_from_color

if platform == "android":
    from android.permissions import request_permissions, Permission
    import kvdroid
    from kvdroid import activity
    from kvdroid.jclass.android import Rect
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    mActivity = PythonActivity.mActivity
    from android.storage import app_storage_path

elif platform == "win" and not Devmode: # убираем консоль
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Классы объектов участка

class House(object):
    """ Класс участка """
    def __init__(self):
        self.title = ""
        self.porchesLayout = "а"
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        self.note = ""
        self.type = ""
        self.porches = []

    def getHouseStats(self):
        """ Подсчет, сколько в доме посещенных и интересующихся """
        visited = interest = totalFlats = 0
        for porch in self.porches:
            for flat in porch.flats:
                if not "." in str(flat.number): totalFlats += 1
                if len(flat.records) > 0: visited += 1
                if flat.status == "1": interest += 1
        ratio = visited / totalFlats if totalFlats != 0 else 0
        return visited, interest, ratio, totalFlats

    def getPorchType(self):
        """ Выдает название подъезда своего типа (всегда именительный падеж), [0] для программы и [1] для пользователя """
        if self.type == "private": return "сегмент", RM.msg[211]
        else: return "подъезд", RM.msg[212]

    def due(self):
        """ Определяет, что участок просрочен """
        d1 = datetime.datetime.strptime(self.date, "%Y-%m-%d")
        d2 = datetime.datetime.strptime(time.strftime("%Y-%m-%d", time.localtime()), "%Y-%m-%d")
        days_between = abs((d2 - d1).days)
        if days_between > 122: return True
        else: return False

    def showPorches(self):

        def __getFlatsRange(porch):
            """ Выдает диапазон квартир в подъезде многоквартирного дома """
            range = ""
            alpha = False
            list = []
            for flat in porch.flats:
                if not "." in flat.number:
                    try: list.append(int(flat.number))
                    except:
                        alpha = True
                        list.append(flat.number)
            if not alpha: list.sort()
            if len(list) == 1:
                range = f" {RM.msg[214]} [i]{list[0]}[/i]"
            elif len(list) > 1:
                last = len(list) - 1
                range = f" {RM.msg[214]} [i]{list[0]}–{list[last]}[/i]"
            return range

        list = []
        self.porches.sort(key=lambda x: ut.numberize(x.title), reverse=False)
        porchString = RM.msg[212][0].upper() + RM.msg[212][1:] if RM.language != "ka" else RM.msg[212]
        for porch in self.porches:
            listIcon = f"{RM.button['porch']} {porchString}" if self.type == "condo" else RM.button['pin']
            list.append(f"{listIcon} [b]{porch.title}[/b] {__getFlatsRange(porch)}")
        if self.type != "condo" and len(list) == 0:
            list.append(f"{RM.button['plus-1']}{RM.button['pin']} {RM.msg[213] % self.getPorchType()[1]}")
        if self.type == "condo":
            if len(list) == 0: number = 1
            else:
                last = len(self.porches)-1
                number = int(self.porches[last].title) + 1 if self.porches[last].title.isnumeric() else None
            if number != None: list.append(f"[i]{RM.msg[6]} {number}[/i]")
        return list

    def addPorch(self, input="", type="подъезд"):
        self.porches.append(Porch())
        self.porches[len(self.porches)-1].title = input.strip()
        self.porches[len(self.porches)-1].type = type

    def deletePorch(self, selectedPorch):
        del self.porches[selectedPorch]

    def rename(self, input):
        self.title = input[3:].upper()

    def export(self):
        return [
            self.title,
            self.porchesLayout,
            self.date,
            self.note,
            self.type,
            [porch.export() for porch in self.porches]
        ]

class Porch(object):
    """ Класс подъезда """
    def __init__(self):
        self.title = ""
        self.status = ""
        self.flatsLayout = "н"
        self.floor1 = 1 # number of first floor
        self.note = ""
        self.flats = [] # list of Flat instances, initially empty
        self.type = ""
        self.flatsNonFloorLayoutTemp = None # несохраняемая переменная
        self.alpha = False

    def shrinkFloor(self, selectedFlat):
        """ Определяет самую левую квартиру этажа и отправляет ее на удаление, чтобы уменьшить этаж """
        all = self.showFlats()
        number = self.flats[selectedFlat].number # отображаемый номер кликнутой квартиры
        for i in range(len(all)):
            if not isinstance(all[i], str) and all[i].number == number:
                index = i # индекс кликнутой квартиры в сетке выдачи (options)
                break
        while 1:
            try:
                if isinstance(all[index-1], str) or "." in all[index-1].number:
                    number = all[index].number # отображаемый номер первой квартиры на этом этаже
                    break
                else:
                    index -= 1
            except:
                RM.popup(message="Unknown error")
                return
        for i in range(len(self.flats)):
            if self.flats[i].number == number:
                if self.checkLastFlatBug(number):
                    self.deleteFlat(i)
                break

    def checkLastFlatBug(self, number):
        """ Проверяет баг на удаление последней квартиры на этаже, если выше нет хотя бы одной квартиры """
        matrix = self.porchAsMatrix()
        floor = self.getFloorOfFlat(number, matrix)
        up = self.flatNumberOnFloor(floor+1, matrix)
        this = self.flatNumberOnFloor(floor, matrix)
        if this == 1 and (self.columns - up) > 0:
            if RM.language == "ru" or RM.language == "uk": error = "Нельзя удалить последнюю квартиру на этаже, если на этаже выше удалена хотя бы одна квартира. Чтобы избежать этой проблемы, удаляйте квартиры снизу вверх. Вы можете пересобрать подъезд и начать заново."
            else: error = "Sorry, you cannot delete the last remaining flat on a floor if one floor up has at least one deleted flat as well. To avoid this problem, delete flats from bottom to top. You can regenerage the entrance and start from scratch."
            RM.popup(message=error)
            return False
        else: return True

    def getFloorOfFlat(self, number, matrix=None):
        """ Возвращает номер этажа, на котором находится квартира с полученным номером (этаж фактический) """
        if matrix == None: matrix = self.porchAsMatrix()
        for row in range(0, self.rows):
            for col in range(0, self.columns):
                if int(matrix[row][col]) == int(number): return row+1

    def flatNumberOnFloor(self, floor, matrix=None):
        """ Считает, сколько квартир на этаже с полученным номером """
        if matrix == None: matrix = self.porchAsMatrix()
        try: floorList = matrix[floor-1]
        except: return 999999
        else:
            count = 0
            for number in floorList:
                if not "." in str(number): count += 1
            return count

    def porchAsMatrix(self):
        """ Преобразует список квартир подъезда из простого одномерного массива в двумерный,
        в котором количество строк и столбцов соответствуют виду подъезда """
        list = self.showFlats()
        matrix = []
        count = 0
        for row in range(self.rows):
            matrix.insert(0, [])
            for col in range(self.columns+1):
                if not isinstance(list[count], str):
                    value = list[count].number
                    if not "." in value: matrix[0].append(int(value))
                    else: matrix[0].append(float(value))
                count+=1
        return matrix

    def deleteFlat(self, ind):
        """ Удаление квартиры - переводит на сдвиг (если подъезд) или простое удаление (если не подъезд) """
        if "подъезд" in self.type and self.floors(): # если подъезд c сеткой, делаем сдвиг
            deletedFlat = self.flats[ind]
            flatsLayoutOriginal = self.flatsLayout # определяем, нет ли в конце списка квартиры с записями, которую нельзя сдвигать
            self.flatsLayout = "о"
            self.sortFlats()
            for flat in self.flats:
                if not "." in flat.number:
                    status = flat.status
                    break
            self.flatsLayout = flatsLayoutOriginal
            self.sortFlats()

            if status != "": RM.popup(message=RM.msg[215] % RM.msg[155]) # больше нельзя уменьшать этажи

            else:
                deletedFlatClone = deepcopy(deletedFlat)
                deletedFlat.hide() # скрываем удаленную квартиру

                self.flatsLayout = "н"
                self.sortFlats() # временно сортируем по номеру

                porch2 = deepcopy(self.flats) # создаем клон подъезда и очищаем исходный подъезд
                for flat in self.flats:
                    flat.wipe()

                for flat in self.flats: # понижаем номера всех квартир
                    if float(flat.number) >= float(deletedFlat.number):
                        flat.number = str(float(flat.number) - 1)
                        if float(flat.number).is_integer(): flat.number = flat.number[0: flat.number.index(".")]
                        flat.title = flat.number + ", " + flat.getName() if flat.getName() != "" else flat.number

                for flat1 in self.flats: # возвращаем исходные квартиры подъезда с данными
                    for flat2 in porch2:
                        if flat1.number == flat2.number and flat2.status != "":
                            flat1.clone(flat2)

                for flat in self.flats: # восстанавливаем на новом месте квартиры с содержимым
                    if flat.number == deletedFlatClone.number:
                        flat.clone(deletedFlatClone)
                        break

                self.flatsLayout = flatsLayoutOriginal # возвращаем исходную сортировку
                self.sortFlats()
                if RM.resources[0][1][8] == 0:
                    RM.popup(title=RM.msg[247], message=RM.msg[230] % RM.msg[155])
                    RM.resources[0][1][8] = 1

        else: del self.flats[ind] # если не подъезд или нет сетки, простое удаление

    def getFirstAndLastNumbers(self):
        """ Возвращает первый и последний номера в подъезде и кол-во этажей """
        numbers = []
        for flat in self.flats:
            if flat.number.isnumeric(): numbers.append(int(flat.number))
        numbers.sort()
        try:
            first = str(numbers[0])
            last = str(numbers[len(numbers) - 1])
            floors = self.type[7:]
            if floors == "": floors = "1"
        except:
            try:
                first, last, floors = RM.settings[0][9]
            except:
                first = "1"
                last = "20"
                floors = "5"
        return first, last, floors

    def sortFlats(self):
        """ Сортировка квартир """
        if self.flatsLayout == "н":  # numeric by number
            self.flatsNonFloorLayoutTemp = self.flatsLayout
            self.flats.sort(key=lambda x: ut.numberize(x.title))

        elif self.flatsLayout == "о": # numeric by number reversed
            self.flatsNonFloorLayoutTemp = self.flatsLayout
            self.flats.sort(key=lambda x: ut.numberize(x.title), reverse=True)

        elif self.flatsLayout=="с": # alphabetic by status character
            self.flatsNonFloorLayoutTemp = self.flatsLayout
            self.flats.sort(key=lambda x: ut.numberize(x.title))
            self.flats.sort(key=lambda x: x.getStatus()[1])

        elif self.flatsLayout=="т": # by phone number
            self.flatsNonFloorLayoutTemp = self.flatsLayout
            self.flats.sort(key=lambda x: ut.numberize(x.title))
            self.flats.sort(key=lambda x: x.phone, reverse=True)

        elif self.flatsLayout=="з": # by note
            self.flatsNonFloorLayoutTemp = self.flatsLayout
            self.flats.sort(key=lambda x: ut.numberize(x.title))
            self.flats.sort(key=lambda x: x.note, reverse=True)

        if str(self.flatsLayout).isnumeric(): # сортировка по этажам
            try:
                self.flats.sort(key=lambda x: float(x.number))
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
            except:
                self.flatsLayout = "н"
                self.flatsNonFloorLayoutTemp = self.flatsLayout

    def floors(self):
        """ Возвращает True, если в подъезде включен поэтажный вид """
        try:
            if self.flatsLayout.isnumeric(): return True
            else: return False
        except: return False

    def deleteHiddenFlats(self):
        """ Удаление скрытых квартир """
        while 1:
            for i in range(len(self.flats)):
                if "." in self.flats[i].number:
                    del self.flats[i]
                    break
            else: break

    def forceFloors(self, floors=None):
        """ Создаем любое заказанное количество этажей """
        self.deleteHiddenFlats()
        if floors==None: floors = self.rows
        self.flatsLayout="н"
        self.sortFlats()
        warn = False
        extraFlats = 0
        while 1:
            a = len(self.flats) / floors
            if not a.is_integer(): # собрать этажность не удалось, добавляем одну квартиру и пробуем снова
                warn=True
                try: lastNumber = int( self.flats[ len(self.flats)-1 ].number) + 1
                except: return
                self.addFlat("%d" % lastNumber)
                extraFlats += 1
                continue
            else:
                self.flatsLayout = floors
                self.rows = floors
                self.sortFlats()
                if warn: RM.popup(message="\n" + RM.msg[216] % (extraFlats, RM.button['shrink']))
                break

    def showFlats(self, sort=False):
        """ Вывод квартир для вида подъезда """
        if sort: self.sortFlats() # сортируем, если нужно

        self.rows = 1
        self.columns = 999
        try:
            if self.flatsLayout.isnumeric(): # определяем тип сортировки
                self.rows = int(self.flatsLayout)
                self.columns = int(len(self.flats) / self.rows)
        except: pass

        options = []
        self.alpha = False

        try:
            if self.flatsLayout.isnumeric(): # вывод многоквартирного подъезда в табличной раскладке
                i = 0
                for r in range(self.rows):
                    #options.append("%2d│ " % (self.rows - r + self.floor1 - 1))
                    options.append(str(self.rows - r + self.floor1 - 1))
                    for c in range(self.columns):
                        #options.append(f"{self.flats[i].getStatus()[0]}{self.flats[i].number}")
                        options.append(self.flats[i])
                        i += 1
            else: # вывод подъезда/сегмента простым списком
                for flat in self.flats:
                    if not "." in flat.number and not flat.number.isnumeric():
                        self.alpha = True
                    if flat.addFlatTolist() != "":
                        options.append(flat.addFlatTolist())
        except:
            for flat in self.flats:
                if flat.addFlatTolist() != "": options.append(flat.addFlatTolist())
        if len(options) == 0 and self.type == "сегмент":
            options.append(f"{RM.button['plus-1']}{RM.button['home']} {RM.msg[12]}")
        return options

    def addFlat(self, input, forcedDelete=False, silent=False, virtual=False):
        """ Создает квартиру """
        input=input.strip()
        if input == "": return None
        self.flats.append(Flat())
        last = len(self.flats)-1
        if not virtual:
            self.flats[last].title = self.flats[last].number = input.strip()  # ***
        else:
            self.flats[last].title = input.strip()
            self.flats[last].number = "virtual"

        if "подъезд" in self.type: # Check if flat with such number already exists, it is deleted (only on grid)
            delete = False
            for i in range(last):
                if self.flats[i].number == self.flats[last].number: # flat with identical number (i) found
                    if self.flats[i].status=="": delete=True # no tenant and no records, delete silently
                    else:
                        if forcedDelete: delete=True
                        else: del self.flats[last] # delete the newly created empty flat
                    break
            if delete: del self.flats[i]

    def addFlats(self, input):
        """ Массовое создание квартир через дефис или пробел (внутренний синтаксис) """
        s=f=0
        success=True
        floors=None
        if str(self.flatsLayout).isnumeric(): self.flatsLayout = "н"
        for i in range(len(input)):
            if input[i]=="-":
                s=i
            if input[i]=="[":
                f=i
                floors = input[f+1:] # извлекаем кол-во этажей из цифры после [
        try: start = int(input[0:s])
        except: start=success=0 # ошибочный ввод из-за дефиса не в том месте
        try:    end = int(input[s+1:]) if f == 0 else int(input[s+1:f])
        except: end=success=0 # ошибочный ввод из-за дефиса не в том месте
        if success:
            for i in range(start, end+1):
                self.addFlat("%s" % (str(i)), silent=True)
            if f!=0: self.flatsLayout = input[f+1:]
        else: success=0
        if "подъезд" in self.type:
            if floors == None: floors = self.rows
            self.forceFloors(int(floors)) # для форсированного задания этажей
        return success

    def export(self):
        return [
            self.title,
            self.status,
            self.flatsLayout,
            self.floor1,
            self.note,
            self.type,
            [flat.export() for flat in self.flats]
        ]

class Flat(object):
    """ Класс квартиры/контакта"""
    def __init__(self):
        self.title = "" # объединенный заголовок квартиры, например: "20, Василий 30 лет"
        self.note = ""  # заметка
        self.number = "virtual" # у адресных жильцов автоматически создается из первых символов title до запятой: "20" (в примере выше);
                                # у виртуальных автоматически присваивается "virtual", а обычного номера нет
        self.status = "" # статус, формируется динамически
        self.phone = "" # телефон
        self.lastVisit = 0 # дата последней встречи в абсолютных секундах (формат time.time())
        self.records = [] # список записей посещений
        self.porchRef = None # указатель на подъезд, в котором находится квартира. Не сохраняется

    def addFlatTolist(self):
        """ Функция для форматированного показа строки в списке подъезда """
        line=""
        if 1:#not "." in self.number:
            name = "" if self.getName() == "" else self.getName().strip()
            line += f"{self.getStatus()[0]} [b]{self.number}[/b] {name}"
        return line

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

    def wipe(self, silent=True):
        """ Полностью очищает квартиру, оставляя только номер """
        del self.records[:]
        self.status = self.note = self.phone = self.lastVisit = ""
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
            try: porch = self.porchRef.title if "подъезд" in self.porchRef.type else ""
            except: porch = ""
            newVirtualHouse.addPorch(input=porch, type="virtual") # create virtual porch
            newVirtualHouse.porches[0].addFlat(self.getName(), virtual=True) # create flat
            newContact = newVirtualHouse.porches[0].flats[0]
            newContact.title = newContact.getName()
            newVirtualHouse.title = "%s-%s" % (title, tempFlatNumber)
            newVirtualHouse.type = "virtual"
            newContact.number = "virtual"
            newContact.records = copy(self.records)
            newContact.note = copy(self.note)
            newContact.status = copy(self.status)
            newContact.phone = copy(self.phone)
            newContact.lastVisit = copy(self.lastVisit)
            return newContact.getName()

    def showRecords(self):
        options = []
        if len(self.records)==0: options.append(RM.msg[220])
        else:
            for i in range(len(self.records)): # добавляем записи разговоров
                if i == 0: # самая последняя (верхняя) запись
                    options.append(f"{RM.button['entry']} [b]{self.records[i].date}[/b][i]{self.records[i].title}[/i]")
                else: # остальные записи
                    options.append(f"{RM.button['entry']} [b]{self.records[i].date}[/b]")
        return options

    def addRecord(self, input):
        self.records.insert(0, Record())
        self.records[0].title = input
        if len(self.records)==1 and self.status == "" and self.number != "virtual": # при первой записи ставим статус ?
            self.status="?"
        date = time.strftime("%d", time.localtime())
        if date[0] == "0": date = date[1:]
        month = RM.monthName()[5]
        timeCur = time.strftime("%H:%M", time.localtime())
        self.records[0].date = "%s %s %s" % (date, month, timeCur)        
        self.lastVisit = time.time()
        return len(self.records)-1

    def editRecord(self, ind, input):
        self.records[ind].title = input
        self.updateStatus()

    def deleteRecord(self, f):
        del self.records[f]
        self.updateStatus()

    def is_empty(self):
        """ Проверяет, что в квартире нет никаких данных """
        if len(self.records) == 0 and self.getName() == "" and self.note == "" and self.phone == "":
            return True
        else: return False

    def updateStatus(self):
        """ Обновление статуса квартиры после любой операции """
        if self.is_empty() and self.status == "?":
            self.status = ""
        elif not self.is_empty() and self.status == "":
            self.status = "?"

    def updateName(self, choice):
        """ Получаем только имя и соответственно обновляем заголовок """
        if choice=="": self.title = self.number
        elif self.number=="virtual": self.title=choice
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

    def hide(self):
        """ Делает квартиру невидимой, не меняя этажность подъезда, путем добавления дробной части к номеру """
        self.number = str ( float(self.number) + random() )

    def getStatus(self):
        """ Возвращает иконку и сортировочное значение статуса в int """
        if self.status == "0":
            string = "{0}"
            value = 6 # value нужно для сортировки квартир по статусу
        elif self.status == "1":
            string = "{1}"
            value = 0
        elif self.status == "2":
            string = "{2}"
            value = 1
        elif self.status == "3":
            string = "{3}"
            value = 2
        elif self.status == "4":
            string = "{4}"
            value = 3
        elif self.status == "?":
            string = "{?}"
            value = 10
        elif self.status == "5":
            string = "{5}"
            value = 7
        else:
            string = "{ }"
            value = 9
        return string, value

    def export(self):
        return [
            self.title,
            self.note,
            self.number,
            self.status,
            self.phone,
            self.lastVisit,
            [record.export() for record in self.records]
        ]

class Record(object):
    """ Класс записи посещения """
    def __init__(self):
        self.date = ""
        self.title = ""

    def export(self):
        return [self.date, self.title]

# Класс отчета

class Report(object):
    def __init__(self):
        self.hours = RM.settings[2][0]
        self.credit = RM.settings[2][1]
        self.placements = RM.settings[2][2]
        self.videos = RM.settings[2][3]
        self.returns = RM.settings[2][4]
        self.studies = RM.settings[2][5]
        self.startTime = RM.settings[2][6]
        self.endTime = RM.settings[2][7]
        self.reportTime = RM.settings[2][8]
        self.difTime = RM.settings[2][9]
        self.note = RM.settings[2][10]
        self.reminder = RM.settings[2][11]
        self.lastMonth = RM.settings[2][12]
        self.reportLogLimit = 200

    def saveReport(self, message="", mute=False, save=True, notify=False):
        """ Выгрузка данных из класса в настройки, сохранение и оповещение """
        RM.settings[2] = [
            self.hours,
            self.credit,
            self.placements,
            self.videos,
            self.returns,
            self.studies,
            self.startTime,
            self.endTime,
            self.reportTime,
            self.difTime,
            self.note,
            self.reminder,
            self.lastMonth
        ]
        if not mute:
            RM.log(message, notify=notify)
            date = time.strftime("%d.%m", time.localtime()) + "." + str(int(time.strftime("%Y", time.localtime())) - 2000)
            time2 = time.strftime("%H:%M:%S", time.localtime())
            RM.resources[2].insert(0, f"\n{date} {time2}: {message}")
        if save: RM.save(silent=True)

    def checkNewMonth(self, forceDebug=False):
        ut.dprint(Devmode, "Определяем начало нового месяца.")
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
            forceHours = True if RM.settings[0][2] == 1 and self.credit >= 1 else False
            self.lastMonth = f"{RM.msg[223]}\n" % RM.monthName()[3] + \
                             (service if self.hours < 1 and not forceHours else \
                             f"{RM.msg[104]}{RM.col} %s\n" % ut.timeFloatToHHMM(self.hours)[
                                                     0: ut.timeFloatToHHMM(self.hours).index(":")]) + \
                             f"{RM.msg[103]}{RM.col} %d\n" % self.studies
            if credit != "": self.lastMonth += f"{RM.msg[224]}{RM.col} %s" % credit

            # Clear service year in October
            if int(time.strftime("%m", time.localtime())) == 10:
                RM.settings[4] = [None, None, None, None, None, None, None, None, None, None, None, None]

            # Save last month hour+credit into service year
            RM.settings[4][RM.monthName()[7] - 1] = self.hours + self.credit

            self.clear(rolloverHours, rolloverCredit)
            RM.settings[3] = time.strftime("%b", time.localtime())
            self.reminder = 1
            self.saveReport(mute=True)
            if saveTimer != 0: # если при окончании месяца работает таймер, принудительно выключаем его
                self.startTime = saveTimer
                Clock.schedule_once(RM.timerPressed, 0.1)

    def toggleTimer(self):
        result = 0
        if not self.startTime: self.modify("(")
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
        self.difTime = 0.0
        self.note = ""
        self.reminder = 1

    def modify(self, input=" "):
        """ Modifying report on external commands using internal syntax """
        if input == "(":  # start timer
            self.startTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
                time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
            self.saveReport(RM.msg[225], notify = True if RM.settings[0][0] == 1 else False)

        elif input == ")": # остановка таймера
            if self.startTime > 0:
                self.endTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
                    time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
                self.reportTime = (self.endTime - self.startTime) / 3600
                if self.reportTime < 0: self.reportTime += 24  # if timer worked after 0:00
                self.hours += self.reportTime
                self.startTime = 0
                self.saveReport(RM.msg[226] % ut.timeFloatToHHMM(self.reportTime), save=False)
                self.reportTime = 0.0
                self.saveReport(mute=True, save=True) # после выключения секундомера делаем резервную копию принудительно

        elif input == "$": # остановка таймера с кредитом
            if self.startTime > 0:
                self.endTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
                    time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
                self.reportTime = (self.endTime - self.startTime) / 3600
                if self.reportTime < 0: self.reportTime += 24 # if timer worked after 0:00
                self.credit += self.reportTime
                self.startTime = 0
                self.saveReport(RM.msg[227] % ut.timeFloatToHHMM(self.reportTime), save=False)
                self.reportTime = 0.0
                self.saveReport(mute=True, save=True) # после выключения секундомера делаем резервную копию принудительно

        elif "ч" in input or "к" in input or "и" in input:
            if input[0] == "ч": # часы
                if input == "ч":
                    self.hours += 1
                    self.saveReport(RM.msg[231])
                else:
                    self.hours = ut.timeHHMMToFloat(RM.time3)
                    self.saveReport(RM.msg[232] % input[1:])
            elif input[0] == "к": # кредит
                if input == "к":
                    self.credit += 1
                    self.saveReport(RM.msg[233])
                else:
                    self.credit = ut.timeHHMMToFloat(RM.time3)
                    self.saveReport(RM.msg[234] % input[1:])
            elif input == "и": # изучения
                self.studies += 1
                self.saveReport(RM.msg[241])
        self.checkNewMonth()

    def optimizeReportLog(self):
        def __optimize(*args):
            ut.dprint(Devmode, "Оптимизируем размер журнала отчета.")
            if len(RM.resources[2]) > self.reportLogLimit:
                extra = len(RM.resources[2]) - self.reportLogLimit
                for i in range(extra):
                    del RM.resources[2][len(RM.resources[2]) - 1]
        _thread.start_new_thread(__optimize, ("Thread-Optimize", .1,))

    def getCurrentMonthReport(self):
        """ Выдает отчет текущего месяца """
        if RM.settings[0][2]:
            credit = f"{RM.msg[222]} {ut.timeFloatToHHMM(self.credit)[0: ut.timeFloatToHHMM(self.credit).index(':')]}\n"  # whether save credit to file
        else: credit = ""
        service = f"{RM.msg[42]}{':' if RM.language != 'hy' else '.'} {RM.emoji['check']}\n" # служение было
        forceHours = True if RM.settings[0][2] == 1 and self.credit >= 1 else False
        result= f"{RM.msg[223]}\n" % RM.monthName()[1] + \
                (service if self.hours < 1 and not forceHours else \
                f"{RM.msg[104]}{RM.col} %s\n" % ut.timeFloatToHHMM(self.hours)[
                                                 0: ut.timeFloatToHHMM(self.hours).index(":")]) + \
                f"{RM.msg[103]}{RM.col} %d\n" % self.studies
        if credit != "": result += f"{RM.msg[224]}{RM.col} %s" % credit
        return result

# Классы интерфейса

class DisplayedList(object):
    """ Класс, описывающий содержимое и параметры списка, выводимого на RM.mainList """
    def __init__(self):
        self.update()

    def update(self, message="", title="", form="", options=[], sort=None, details=None, resize=None,
               footer=[], positive="", neutral="", tip=None, back=True):
        self.message = message
        self.title = title
        self.form = form
        self.options = options
        self.positive = positive
        self.neutral = neutral
        self.sort = sort
        self.details = details
        self.resize = resize
        self.footer = footer,
        self.back = back
        self.tip = tip

class TipButton(Button):
    """ Заметки и предупреждения (невидимые кнопки) """
    def __init__(self, text="", size_hint_y=1, font_size=None, text_size=[0, 0], color=None, background_color=None,
                 font_size_force=False, halign="left", *args, **kwargs):
        super(TipButton, self).__init__()
        self.text = text
        self.size_hint_y = size_hint_y
        if RM.specialFont != None: self.font_name = RM.specialFont
        if not RM.desktop or font_size_force:
            self.font_size = font_size if font_size != None else RM.fontS * RM.fontScale()
        if RM.bigLanguage: self.font_size = self.font_size * .9
        self.markup = True
        self.text_size = text_size
        self.background_normal = ""
        self.background_down = ""
        self.halign = halign
        self.valign = "center"
        self.padding = (RM.padding*3, RM.padding)
        self.pos_hint = {"center_x": .5}
        self.color = RM.standardTextColor
        if color != None: self.color = color
        self.background_color = background_color if background_color != None else RM.globalBGColor

class MyLabel(Label):
    def __init__(self, text="", markup=None, color=None, halign=None, valign=None, text_size=None, size_hint=None,
                 size_hint_y=1, font_size_force=False,
                 height=None, width=None, pos_hint=None, font_size=None, *args, **kwargs):
        super(MyLabel, self).__init__()
        if markup != None: self.markup = markup
        self.color = color if color != None else RM.standardTextColor
        if halign != None: self.halign = halign
        if valign != None: self.valign = valign
        if text_size != None: self.text_size = text_size
        if height != None: self.height = height
        if width != None: self.width = width
        if size_hint != None: self.size_hint = size_hint
        if size_hint_y != 1: self.size_hint_y = size_hint_y
        if pos_hint != None: self.pos_hint = pos_hint
        if not RM.desktop or font_size_force:
            self.font_size = font_size if font_size != None else RM.fontS * RM.fontScale()
        if RM.bigLanguage: self.font_size = self.font_size * .9
        if RM.specialFont != None:
            self.font_name = RM.specialFont
        self.text = text

class MyTextInput(TextInput):
    def __init__(self, multiline=False, size_hint_y=1, size_hint_x=1, hint_text="", pos_hint = {"center_y": .5},
                 text="", disabled=False, input_type="text", width=0, height=None, mode="resize", time=False,
                 popup=False, halign="left", valign="center", focus=False, color=None, background_color=None, limit=99999,
                 specialFont=False,
                 font_size=None, font_size_force=False, shrink=True, blockPositivePress=False, *args, **kwargs):
        super(MyTextInput, self).__init__()
        if not RM.desktop or font_size_force:
            self.font_size = font_size if font_size != None else (RM.fontS * RM.fontScale())
        if RM.specialFont != None or specialFont: self.font_name = RM.differentFont
        self.multiline = multiline
        self.markup = True
        self.limit = limit
        self.halign = halign
        self.valign = valign
        self.shrink = shrink
        self.size_hint_x = size_hint_x
        self.size_hint_y = size_hint_y
        self.pos_hint = pos_hint
        self.height = height if height != None else RM.standardTextHeight
        self.width = width
        self.input_type = input_type
        self.text = u"%s" % text
        self.disabled = disabled
        self.blockPositivePress = blockPositivePress
        self.foreground_color = RM.textInputColor
        self.background_color = RM.textInputBGColor
        self.hint_text = hint_text
        self.hint_text_color = RM.topButtonColor
        self.use_bubble = True
        self.mode = mode
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
        if RM.theme != "3D":
            self.background_normal = ""
            self.background_disabled_normal = ""

        self.cursor_color = RM.titleColor
        self.cursor_color[3] = .9

        if color != None:
            self.foreground_color = self.disabled_foreground_color = color
        else:
            self.foreground_color = "black" if RM.mode=="light" else "white"

        if background_color != None: self.background_color = background_color

    def insert_text(self, char, from_undo=False):
        """ Делаем буквы заглавными """
        if len(self.text) >= self.limit:
            if not RM.desktop and RM.allowCharWarning:
                RM.log(RM.msg[91] % RM.charLimit, timeout=2)
                RM.allowCharWarning = False
                def __turnToTrue(*args):
                    RM.allowCharWarning = True
                Clock.schedule_once(__turnToTrue, 5)
            return
        if self.input_type != "text":
            if f"{RM.button['arrow']} {RM.msg[16]}" in RM.pageTitle.text : # дата
                if char.isnumeric():
                    return super().insert_text(char, from_undo=from_undo)
                elif char == "-":
                    return super().insert_text("-", from_undo=from_undo)
            elif char.isnumeric(): return super().insert_text(char, from_undo=from_undo) # цифры
            elif self.time: # часы - превращаем все символы кроме цифр в двоеточия
                return super().insert_text(":", from_undo=from_undo)
        else:
            def __capitalize():
                string = self.text[: self.cursor_index()].strip()
                l = len(string) - 1
                if len(string) > 0 and (string[l] == "." or string[l] == "!" or string[l] == "?") or self.cursor_col == 0:
                    return True # можно
                else: return False # нельзя
            if __capitalize() and RM.language != "ka" and RM.settings[0][11] and not RM.desktop:
                if len(char) == 1: char = char.upper()
                else: char = char[0].upper() + char[1:]
            return super().insert_text(char, from_undo=from_undo)

    def on_text_validate(self):
        if not self.popup and not self.blockPositivePress: RM.positivePressed(instance=self)

    def on_focus(self, instance=None, value=None):
        if platform == "android":
            self.keyboard_mode = "managed"
            Window.softinput_mode = self.mode
        elif RM.desktop:
            return

        if value:  # вызов клавиатуры
            Clock.schedule_once(self.create_keyboard, .05)
            if not self.multiline or self.mode == "pan" or not self.shrink: return
            else:
                def __shrinkWidgets(*args):
                    RM.globalFrame.size_hint_y = None
                    RM.globalFrame.height = Window.height - RM.keyboardHeight() - RM.standardTextHeight
                    RM.globalFrame.remove_widget(RM.boxFooter)
                    RM.boxHeader.size_hint_y = 0
                    RM.titleBox.size_hint_y = 0
                    RM.bottomButtons.size_hint_y = RM.bottomButtonsSizeHintY * 1.5
                Clock.schedule_once(__shrinkWidgets, .07)

        else:
            self.hide_keyboard()
            self.keyboard_mode = "auto"
            if self.shrink:
                RM.boxHeader.size_hint_y = RM.titleSizeHintY
                RM.titleBox.size_hint_y = RM.tableSizeHintY
                RM.globalFrame.size_hint_y = 1
                RM.bottomButtons.size_hint_y = RM.bottomButtonsSizeHintY
                if RM.boxFooter not in RM.globalFrame.children: RM.globalFrame.add_widget(RM.boxFooter)

    def on_touch_down (self, instance, touch):
        print(1)
        if touch.button == 'right':
            print("right mouse clicked")

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

class MyCheckBox(CheckBox):
    """ Галочки """
    def __init__(self, active=False, size_hint=(1, 1), pos_hint=None, *args, **kwargs):
        super(MyCheckBox, self).__init__()
        self.active = active
        self.size_hint = size_hint
        if pos_hint != None: self.pos_hint = pos_hint
        self.background_checkbox_down = "checkbox_down.png"
        self.background_checkbox_normal = "checkbox_normal.png"

class TTab(TabbedPanelHeader):
    """ Вкладки панелей """
    def __init__(self, text=""):
        super(TTab, self).__init__()
        if not RM.desktop and RM.fontScale() > 1: self.font_size = RM.fontS
        if RM.specialFont != None: self.font_name = RM.specialFont
        self.text = text
        self.background_normal = "void.png"
        self.color, self.background_down = RM.tabColors

class TopButton(Button):
    """ Кнопки поиска и настроек """
    def __init__(self, text="", size_hint_x=None):
        super(TopButton, self).__init__()
        if RM.specialFont != None: self.font_name = RM.specialFont
        self.text = text
        self.font_size = RM.fontXL * (.85 if RM.desktop else .79)
        self.markup=True
        self.size_hint_x = 1 if size_hint_x==None else size_hint_x
        self.size_hint_y = None
        self.pos_hint = {"center_y": .5}
        self.color = RM.topButtonColor
        self.background_color = RM.globalBGColor
        self.background_normal = ""
        self.background_down = "" if RM.theme == "dark" else RM.buttonPressedBG

    def on_press(self):
        RM.buttonFlash(instance=self)
        if RM.mode=="dark" and self.background_color != RM.tableBGColor:
            self.background_color = RM.buttonPressedOnDark
            Clock.schedule_once(self.restoreBlackBG, RM.onClickFlash)

    def restoreBlackBG(self, *args):
        self.background_color = RM.globalBGColor

class FooterButton(Button):
    """ Вкладки под пунктами списка с индикаторами """
    def __init__(self, text="", parentIndex=None, **kwargs):
        super(FooterButton, self).__init__()
        self.spacing = RM.spacing
        self.text = text
        self.markup = True
        self.parentIndex = parentIndex
        self.background_color = RM.scrollButtonBackgroundColor if RM.theme != "3D" else RM.globalBGColor
        self.background_down = ""
        self.background_normal = ""
        self.valign = "top"
        self.font_size = (RM.fontS if RM.desktop else RM.fontXXS*.9) * RM.fontScale()
        self.color = get_hex_from_color(
            [
                RM.linkColor[0],
                RM.linkColor[1],
                RM.linkColor[2],
                .9
            ] if RM.mode == "light" else RM.standardTextColor)

    def on_press_(self):
        RM.btn[self.parentIndex].background_normal = RM.buttonPressedBG

    def on_release(self):
        if self.parentIndex != None: RM.btn[self.parentIndex].on_release()

class TableButton(Button):
    """ Кнопки в шапке таблицы и ниже на некоторых формах """
    def __init__(self, text="", size_hint_x=1, size_hint_y=1, height=0, width=0, background_color=None,
                 text_size=(None, None),
                 form=None, color=None, pos_hint=None, size=None, disabled=False, font_name=None, **kwargs):
        super(TableButton, self).__init__()
        if not RM.desktop: self.font_size = RM.fontS
        if RM.specialFont != None: self.font_name = RM.specialFont
        if font_name != None: self.font_name = font_name
        self.text = text.strip()
        self.markup = True
        self.size_hint_x = size_hint_x
        self.size_hint_y = size_hint_y
        self.padding = (RM.padding, RM.padding)
        self.text_size = text_size
        self.height = height
        self.width = width
        self.halign = "center"
        self.disabled = disabled
        if form == "firstCall":
            self.height *= 1.6
            self.width *= 1.7
        if size != None: self.size = size
        self.pos_hint = pos_hint if pos_hint != None else {"center_y": .5}
        self.default_background_color = RM.tableBGColor if background_color == None else background_color
        if RM.theme == "3D" or RM.desktop:
            self.color = RM.mainMenuButtonColor
            self.background_color = RM.scrollButtonBackgroundSecondaryColor
            if RM.desktop and RM.theme != "3D":
                if color != None: self.color = color
                else: self.color = RM.tableColor
                self.background_normal = ""
                self.background_color = self.default_background_color if background_color == None else background_color
                self.background_down = RM.buttonPressedBG
                self.background_disabled_normal = ""
                self.background_disabled_down = ""
        else:
            if color != None: self.color = color
            else: self.color = RM.tableColor
            self.background_normal = ""
            self.background_color = self.default_background_color
            if RM.theme == "dark" or RM.theme == "gray":
                self.background_down = ""
            else: self.background_down = RM.buttonPressedBG
            self.background_disabled_normal = ""

    def on_press(self):
        if RM.theme != "3D":# and self.default_background_color != RM.tableBGColor:
            RM.buttonFlash(instance=self)
            if (RM.mode == "dark" and RM.theme != "3D") and \
                    (self.background_color != RM.tableBGColor or RM.button["target"] in self.text):
                self.background_color = RM.buttonPressedOnDark
                Clock.schedule_once(self.restoreBlackBG, RM.onClickFlash)

    def restoreBlackBG(self, *args):
        self.background_color = self.default_background_color

class RButton(Button):
    """ Круглая кнопка """
    def __init__(self, text="", size_hint_x=1, size_hint_y=1, text_size=(None, None), halign="center",
                 height=0, font_name=None,
                 valign="center", size=Window.size, font_size=None, background_normal="", color=None, background_color=None,
                 markup=True, background_down="", onPopup=False, quickFlash=False, radiusK = 1, **kwargs):
        super(RButton, self).__init__()
        if not RM.desktop: self.font_size = font_size if font_size != None else RM.fontS
        if RM.specialFont != None: self.font_name = RM.specialFont
        if font_name != None: self.font_name = font_name
        self.markup = markup
        self.padding = (RM.padding, RM.padding)
        self.text = text
        self.size_hint_x = size_hint_x
        self.size_hint_y = size_hint_y
        self.height = (RM.standardTextHeight / RM.fontScale()) if height != 0 else height
        self.size = size
        self.halign = halign
        self.valign = valign
        self.text_size = text_size
        self.radius = [RM.buttonRadius * radiusK]
        self.popupBackgroundColor = [.22, .22, .22, .9]
        self.k = .5 if quickFlash == True else 1
        if self.text == RM.button['lock']:
            self.radius = [RM.buttonRadius * radiusK, 0, 0, 0] # нет дома
        elif self.text == RM.button['record']: # подгонка радиуса под кнопки первого посещения
            if RM.settings[0][13]: # если есть кнопка "нет дома"
                self.radius = [0, RM.buttonRadius * radiusK, 0, 0] # отказ
            else:
                self.radius = [RM.buttonRadius * radiusK, RM.buttonRadius * radiusK, 0, 0] # отказ
        if self.text == RM.button['reject']: # подгонка радиуса под кнопки первого посещения
            self.radius = [0, 0, RM.buttonRadius * radiusK, RM.buttonRadius * radiusK] # отказ
            if RM.theme == "3D" and not RM.desktop and color == RM.getColorForStatus("4"):
                k=1.7
                color = [color[0]*k, color[1]*k, color[2]*k, 1] # немного высветляем коричневый цвет на серой кнопке

        if RM.theme != "3D" and not RM.desktop:
            self.background_down = background_down
            if onPopup: self.background_color = self.popupBackgroundColor
            elif background_color == None: self.background_color = RM.tableBGColor
            else: self.background_color = background_color
            self.background_normal = background_normal
            self.origColor = RM.tableColor if color == None else color
            self.color = self.origColor
            self.background_color[3] = 0

            with self.canvas.before:
                self.shape_color = Color(rgba=[self.background_color[0], self.background_color[1],
                                               self.background_color[2], 1])
                self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
                self.bind(pos=self.update_shape, size=self.update_shape)

        elif RM.theme != "3D" and RM.desktop:
            if RM.theme == "purple" and background_color == None:
                self.color = RM.tableColor
            else:
                self.color = color if color != None else RM.tableColor
            if RM.theme != "3D": self.background_normal = ""
            if background_color != None:
                self.background_color = background_color
            elif onPopup and RM.theme != "3D":
                self.background_color = self.popupBackgroundColor
            elif RM.theme == "3D":
                self.background_color = RM.buttonTint
            else:
                self.background_color = RM.tableBGColor
            self.background_down = RM.buttonPressedBG

        else: # тема 3D
            self.background_color = RM.buttonTint
            if color != None: self.color = color
            else: self.color = RM.tableColor
            if background_color != None and background_color != RM.buttonTint:
                self.background_normal = ""
                self.background_color = background_color

        if onPopup:
            self.size_hint = (1, None)
            self.height = RM.standardTextHeight * 1.3 / RM.fontScale()
            self.color = self.origColor = RM.popupButtonColor

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def on_press(self, *args):
        RM.buttonFlash(instance=self)
        if RM.theme != "3D" and not RM.desktop:
            if RM.titleBox.size_hint_y != 0: # не должно срабатывать, когда кнопка "Сохранить" на поднятой клавиатуре
                with self.canvas.before:
                    self.shape_color = Color(rgba=[self.background_color[0]*RM.onClickColK,
                                                   self.background_color[1]*RM.onClickColK,
                                                   self.background_color[2]*RM.onClickColK, 1])
                    self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
                    self.bind(pos=self.update_shape, size=self.update_shape)
            self.color = RM.titleColor# if RM.theme != "purple" else RM.linkColor
            Clock.schedule_once(self.restoreColor, RM.onClickFlash * self.k)

    def restoreColor(self, *args):
        if RM.titleBox.size_hint_y != 0 and RM.theme != "3D" and not RM.desktop:
            with self.canvas.before:
                self.shape_color = Color(rgba=[self.background_color[0], self.background_color[1],
                                               self.background_color[2], 1])
                self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
                self.bind(pos=self.update_shape, size=self.update_shape)
        if RM.theme != "3D" and not RM.desktop: self.color = self.origColor

class PopupNoAnimation(Popup):
    """ Попап, в котором отключена анимация при закрытии """
    def __init__(self, **kwargs):
        super(PopupNoAnimation, self).__init__(**kwargs)
        if RM.specialFont != None: self.title_font = RM.specialFont

    def open(self, *_args, **kwargs):
        if self._is_open: return
        self._window = Window
        self._is_open = True
        self.dispatch('on_pre_open')
        Window.add_widget(self)
        Window.bind(on_resize=self._align_center,
                    on_keyboard=self._handle_keyboard)
        self.center = (Window.center[0] / RM.SR, Window.center[1])#Window.center
        self.fbind('center', self.center)#_align_center)
        self.fbind('size', self.center)#_align_center)
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
    def __init__(self, text, font_name=None):
        super(SortListButton, self).__init__()
        self.markup = True
        self.size_hint_y = None
        self.height = Window.size[1] * .038 * 1.6 if not RM.desktop else 45
        if RM.theme == "default" or RM.theme == "green":
            k=.98
            self.bk_color = [RM.textInputBGColor[0]*k, RM.textInputBGColor[1]*k, RM.textInputBGColor[2]*k, RM.textInputBGColor[3]]
        else:
            self.bk_color = RM.textInputBGColor
        self.background_color = self.bk_color
        self.background_normal = ""
        self.background_down = RM.buttonPressedBG
        self.color = RM.tableColor
        if RM.fontScale() > 1: self.font_size = RM.fontS
        if font_name != None: self.font_name = font_name
        elif RM.specialFont != None: self.font_name = RM.specialFont
        self.text = text

    def on_press(self):
        RM.buttonFlash(instance=self)
        Clock.schedule_once(self.restoreColor, RM.onClickFlash)

    def restoreColor(self, *args):
        self.background_color = self.bk_color

class ScrollButton(Button):
    """ Пункты всех списков кроме квадратиков квартир в поэтажном режиме """
    def __init__(self, text="", height=0, valign="center", text_size=None, size_hint_x=1, size_hint_y=None, parentIndex=None):
        super(ScrollButton, self).__init__()
        self.size_hint_x = size_hint_x
        if size_hint_y != None: self.size_hint_y = size_hint_y
        self.height = height
        self.halign = "left"
        self.valign = valign
        self.markup = True
        if not RM.desktop: self.font_size = RM.fontM*.9 * RM.fontScale()
        self.parentIndex = parentIndex
        k = .9 if RM.orientation == 'v' else .95
        self.text_size = ((Window.size[0] * k)*RM.SR, None) if text_size == None else text_size
        if RM.specialFont != None: self.font_name = RM.specialFont
        self.originalColor = RM.linkColor
        if RM.theme != "3D":
            self.background_normal = ""
            self.background_color = RM.scrollButtonBackgroundColor
        else:
            self.background_color = RM.buttonTint
        if self.originalColor != "": self.color = self.originalColor
        if RM.theme != "3D": self.background_down = RM.buttonPressedBG
        self.text = text
        if parentIndex != None: self.background_color = [.92, .92, .92]

    """def on_touch_down(self, touch):# widget, touch, *args):
        self.menu = BoxLayout(
            size_hint=(None, None),
            orientation='vertical',
            center=touch.pos)
        self.menu.add_widget(Button(text='a'))
        self.menu.add_widget(Button(text='b'))
        close = Button(text='close')
        close.bind(on_release=self.close_menu)
        self.menu.add_widget(close)
        RM.mainList.add_widget(self.menu)

    def close_menu(self, instance):
        RM.mainList.remove_widget(self.menu)

    def on_touch_up(self, touch):
        self.delete_clock(widget=self.root, touch=touch)

    def delete_clock(self, widget, touch, *args):
        Clock.unschedule(touch.ud['event'])
        #RM.btn[0].on_release()
        #RM.detailsPressed()
        #self.menu(touch)

    def menu(self, touch, *args):
        print(3)
        RM.btn[0].on_release()
        return
        menu = BoxLayout(
                size_hint=(None, None),
                orientation='vertical',
                center=touch.pos)
        menu.add_widget(Button(text='a'))
        menu.add_widget(Button(text='b'))
        close = Button(text='close')
        close.bind(on_release=partial(self.close_menu, menu))
        menu.add_widget(close)
        self.root.add_widget(menu)
        #self.root.run()

    def close_menu(self, widget, *args):
        self.root.remove_widget(widget)"""

    def on_press(self):
        if self.parentIndex == None:
            if "dark" in RM.theme:
                self.background_color = [RM.buttonPressedOnDark[0]/2, RM.buttonPressedOnDark[1]/2, RM.buttonPressedOnDark[2]/2]
                Clock.schedule_once(self.restoreBlackBG, RM.onClickFlash)
        else: RM.btn[self.parentIndex].on_press()

    def restoreBlackBG(self, *args):
        self.background_color = RM.scrollButtonBackgroundColor

    def on_release(self):
        if self.parentIndex == None: RM.clickOnList(instance=self)
        else: RM.btn[self.parentIndex].on_release()

class FlatButton(Button):
    """ Кнопка квартиры """
    def __init__(self, text="", status="", size_hint_x=1, size_hint_y=1, width=0, height=0, pos_hint={"top": 0},
                 grid=False, **kwargs):
        super(FlatButton, self).__init__()
        if RM.specialFont != None: self.font_name = RM.specialFont
        self.text = text
        self.markup = True
        self.halign = "center"
        self.valign = "middle"
        self.pos_hint = pos_hint
        self.text_size = ((Window.size[0]*.95)*RM.SR, height)
        self.size_hint_x = size_hint_x
        self.size_hint_y = size_hint_y
        if not RM.desktop:
            if not grid:
                if RM.fontScale() > 1.3:
                    self.font_size = RM.fontL
                else:
                    self.font_size = RM.fontM * RM.fontScale()
            elif RM.fontScale() < 1.2:
                self.font_size = RM.fontS * RM.fontScale()
            else:
                self.font_size = RM.fontS
        self.origWidth = width
        self.origHeight = height
        self.width = self.origWidth
        self.height = self.origHeight
        self.background_normal = ""
        self.background_down = RM.buttonPressedBG
        self.background_color = RM.getColorForStatus(status)
        self.radius = [RM.buttonRadius/4]
        if RM.desktop: self.radius = [RM.buttonRadius/4 * RM.desktopRadK]

        if RM.theme != "3D" and not RM.desktop:
            self.background_color[3] = 0
            if RM.msg[11] in text:
                self.background_color = RM.scrollButtonBackgroundColor
                self.color = RM.linkColor
                self.halign = "left"
            with self.canvas.before:
                self.shape_color = Color(rgba=[self.background_color[0], self.background_color[1], self.background_color[2], 1])
                self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
                self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def on_press(self):
        if RM.theme != "3D" and not RM.desktop:
            with self.canvas.before:
                self.shape_color = Color(rgba=[self.background_color[0]*RM.onClickColK, self.background_color[1]*RM.onClickColK,
                                               self.background_color[2]*RM.onClickColK, 1])
                self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
                self.bind(pos=self.update_shape, size=self.update_shape)
            Clock.schedule_once(self.restoreColor, RM.onClickFlash)

    def restoreColor(self, *args):
        with self.canvas.before:
            self.shape_color = Color(rgba=[self.background_color[0], self.background_color[1], self.background_color[2], 1])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            self.bind(pos=self.update_shape, size=self.update_shape)

    def on_release(self):
        RM.clickOnList(instance=self)

    def colorize(self, *args):
        self.background_color = RM.getColorForStatus(RM.flat.status)
        if RM.theme != "3D" and not RM.desktop:
            self.background_color[3] = 0
            with self.canvas.before:
                self.shape_color = Color(
                    rgba=[self.background_color[0], self.background_color[1], self.background_color[2], 1])
                self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
                self.bind(pos=self.update_shape, size=self.update_shape)

class CounterButton(Button):
    """ Кнопка на счетчиках """
    def __init__(self, mode, disabled=False):
        super(CounterButton, self).__init__()
        self.mode = mode
        self.size_hint = (1, 1)
        self.text = icon("icon-minus-1") if mode == "minus" else icon("icon-plus-1")
        self.markup = True
        self.disabled = disabled
        self.font_size = RM.fontM * RM.fontScale()
        self.color = RM.tableColor
        self.color[3] = .8
        if RM.theme != "3D":
            self.background_color = RM.tableBGColor
            self.background_normal = ""
            self.background_down = RM.buttonPressedBG
    def on_release(self):
        if self.mode == RM.msg[108] or self.mode == RM.msg[109]:
            RM.popupForm = "showTimePicker"
            RM.popup(title=self.mode)
        else: RM.counterChanged = True

class Counter(AnchorLayout):
    """ Виджет счетчика """
    def __init__(self, type="int", text="0", disabled=False, picker=None, width=None,
                 mode="resize", focus=False):
        super(Counter, self).__init__()
        self.anchor_x = "center"
        self.anchor_y = "center"

        box = BoxLayout(orientation="vertical", size_hint=(None, None),
                        spacing=RM.spacing if RM.theme != "3D" else 0,
                        width=RM.standardTextWidth * 2.3 if width == None else width,
                        height=RM.standardTextHeight * (2.2 if RM.orientation == "v" else 1.4))

        self.input = MyTextInput(text=text, focus=focus, disabled=disabled, multiline=False, # ввод
                                 halign="center", time = True if picker != None else False, size_hint=(1, None),
                                 font_size=RM.fontBigEntry,
                                 height=RM.standardTextHeight, input_type="number", mode=mode)
        def focus(instance, value):
            RM.counterChanged = True
            if ":" in self.input.text: RM.counterTimeChanged = True
            if self.input.text.isnumeric() and int(self.input.text) < 0: self.input.text = "0"
            else:
                try:
                    if self.input.text[0] == "-": self.input.text = self.input.text[1:]
                except: pass
            if not value:
                if self.input.text.strip() == "":
                    self.input.text = "0" if picker == None else "0:00"
                elif picker != None and not ":" in self.input.text: self.input.text += ":00"
        self.input.bind(focus=focus)
        self.input.bind(on_text_validate=RM.positivePressed)
        box.add_widget(self.input)

        buttonBox = BoxLayout(size_hint_y=1 if RM.orientation=="v" else .5,  # второй бокс для кнопок
                              spacing=RM.spacing if RM.theme != "3D" else 0)
        box.add_widget(buttonBox)

        btnDown = CounterButton("minus", disabled=disabled)  # кнопка вниз

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
                    RM.counterTimeChanged = RM.counterChanged = True
            except:
                pass

        btnDown.bind(on_release=__countDown)
        buttonBox.add_widget(btnDown)

        btnUp = CounterButton("plus" if picker == None else picker, disabled=disabled) # кнопка вверх
        def __countUp(instance=None):
            if type != "time": self.input.text = str(int(self.input.text) + 1)
        btnUp.bind(on_release=__countUp)
        buttonBox.add_widget(btnUp)

        self.add_widget(box)

    def get(self):
        return self.input.text

    def update(self, update):
        self.input.text = update

class Timer(Button):
    """ Виджет таймера """
    def __init__(self):
        super(Timer, self).__init__()
        self.pos_hint = {"center_y": .5}
        self.diameter = [1.5, 1.3] # размер при обычном и нажатом состоянии таймера
        self.font_size = RM.fontXL * self.diameter[0]
        self.markup = True
        self.halign = "left"
        self.background_color = RM.globalBGColor
        self.background_normal = ""
        self.originalColor = self.color
        self.background_down = "" if RM.theme == "dark" else RM.buttonPressedBG

    def on_press(self):
        self.font_size = RM.fontXL * self.diameter[1]
        Clock.schedule_once(self.step2, RM.onClickFlash)
        if RM.mode=="dark" and self.background_color != RM.tableBGColor:
            self.background_color = RM.buttonPressedOnDark
            Clock.schedule_once(self.restoreBlackBG, RM.onClickFlash)

    def restoreBlackBG(self, *args):
        self.background_color = RM.globalBGColor

    def step2(self, *args):
        self.font_size = RM.fontXL * self.diameter[0]

    def on_release(self):
        RM.timerPressed()

    def on(self):
        """ Включение таймера """
        self.text = icon("icon-stop-circle")
        self.color = RM.titleColor

    def off(self):
        """ Выключение таймера """
        self.text = icon("icon-play-circled-1")
        self.color = RM.timerOffColor

class ColorStatusButton(Button):
    """ Кнопка выбора цвета """
    def __init__(self, status="", text=""):
        super(ColorStatusButton, self).__init__()
        self.size_hint_max_y = .5
        self.side = (RM.mainList.size[0] - RM.padding * 2 - RM.spacing * 14.5) / 7
        self.size_hint = (None, None)
        self.height = self.side if RM.orientation == "v" else RM.standardTextHeight
        self.width = self.side
        self.text = text
        self.status = status
        self.markup = True
        self.background_normal = ""
        self.background_color = RM.getColorForStatus(self.status)

        self.radius = [RM.buttonRadius / 4]
        if RM.desktop: self.radius = [RM.buttonRadius/4 * RM.desktopRadK]

        if RM.theme != "3D" and not RM.desktop:
            self.background_color[3] = 0
            with self.canvas.before:
                self.shape_color = Color(rgba=[RM.getColorForStatus(self.status)[0], RM.getColorForStatus(self.status)[1],
                                               RM.getColorForStatus(self.status)[2], 1])
                self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
                self.bind(pos=self.update_shape, size=self.update_shape)
        else:
            self.background_down = RM.buttonPressedBG

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def on_press(self, *args):
        for button in RM.colorBtn: button.text = ""
        self.text = RM.button["dot"]
        if RM.theme != "3D":
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
        if self.status == "1" and RM.resources[0][1][5] == 0:
            RM.popup(title=RM.msg[247], message=RM.msg[82])
            RM.resources[0][1][5] = 1
            RM.save()
        RM.colorBtnPressed(color=self.status)

class MainMenuButton(Button):
    """ Три главные кнопки внизу экрана """
    def __init__(self, text):
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
        if RM.specialFont != None: self.font_name = RM.specialFont
        self.text = text

        self.iconTer1 = 'icon-map'
        self.iconTer1ru = 'icon-building-filled'
        self.iconTer2 = 'icon-map-o'
        self.iconTer2ru = 'icon-building'
        self.iconCon1 = 'icon-address-book-1'
        self.iconCon2 = 'icon-address-book-o'
        self.iconRep1 = 'icon-doc-text-inv'
        self.iconRep2 = 'icon-doc-text'

        self.valign = self.halign = "center"
        self.size_hint = (1, 1)
        self.markup = True
        if RM.theme == "purple":
            self.background_color = RM.tableBGColor
        elif RM.theme == "morning":
            self.background_color = RM.mainMenuBGColor
        else:
            self.background_color = RM.globalBGColor
        if RM.theme != "3d":
            self.background_down = RM.buttonPressedBG
            self.background_normal = ""
        self.color = RM.mainMenuButtonColor

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

    def on_press(self):
        if RM.mode=="dark" and self.background_color != RM.tableBGColor and RM.theme != "morning" and RM.theme != "gray":
            self.background_color = RM.buttonPressedOnDark
            Clock.schedule_once(self.restoreBlackBG, RM.onClickFlash)

    def restoreBlackBG(self, *args):
        self.background_color = RM.globalBGColor if RM.theme != "morning" else RM.scrollButtonBackgroundColor

    def on_release(self):
        RM.updateMainMenuButtons()

    def hide(self):
        self.background_color = RM.globalBGColor

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
        k = .3
        if RM.desktop: k = k * RM.desktopRadK
        self.b1 = RButton(text=text1, markup=True, background_color=RM.getColorForStatus("4"), background_normal="",
                    color="white", background_down = RM.buttonPressedBG, radiusK=k)
        self.b2 = RButton(text=text2, markup=True, background_color=RM.getColorForStatus("0"), background_normal="",
                    color = "white", background_down = RM.buttonPressedBG, radiusK=k)
        self.b3 = RButton(text=text3, markup=True, background_color=RM.getColorForStatus("5"), background_normal="",
                    color = "white", background_down = RM.buttonPressedBG, radiusK=k)
        self.b1.bind(on_press=self.change)
        self.b2.bind(on_press=self.change)
        self.b3.bind(on_press=self.change)
        self.anchor_x = "center"
        self.anchor_y = "center"
        box = BoxLayout(spacing = RM.spacing, size_hint = (1, .7))
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
        if self.b1.text == RM.button["dot"]: return "4"
        elif self.b2.text == RM.button["dot"]: return "0"
        else: return "5"

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
        self.header = BoxLayout(orientation = 'horizontal', size_hint = (1, 0.2), padding=RM.padding*3)
        self.body = GridLayout(cols = 7)
        self.add_widget(self.header)
        self.add_widget(self.body)
        self.populate_body()
        self.populate_header()

    def populate_header(self, *args, **kwargs):
        self.header.clear_widgets()
        k, r, bg =.4, 0.7, [.22, .22, .22, .9]
        if RM.theme != "3D":
            previous_month = RButton(text = icon("icon-left-open"), radiusK=r, color="white",
                                     size_hint_x=k, background_color=bg)
            next_month = RButton(text=icon("icon-right-open"), radiusK=r, color="white",
                                 size_hint_x=k, background_color=bg)
        else:
            previous_month = Button(text = icon("icon-left-open"), markup=True, size_hint_x=k,
                                    color = RM.mainMenuButtonColor,
                                    background_color = RM.buttonTint)
            next_month = Button(text=icon("icon-right-open"), markup=True, size_hint_x=k,
                                color=RM.mainMenuButtonColor,
                                background_color=RM.buttonTint)
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
                                background_down = RM.buttonPressedBG,
                                background_color=RM.popupBackgroundColor)
            date_label.bind(on_press=partial(self.set_date, day=self.date_cursor.day))
            date_label.bind(on_release=self.pick)
            if self.date.day == self.date_cursor.day:
                date_label.background_color = RM.titleColor
                date_label.background_color[3] = .5
            self.body.add_widget(date_label)
            self.date_cursor += datetime.timedelta(days = 1)

    def pick(self, instance=None):
        def do(*args):
            RM.dismissTopPopup()#RM.mypopup.dismiss()
            RM.multipleBoxEntries[1].text = str(self.date)
        Clock.schedule_once(do, RM.onClickFlash)

    def set_date(self, *args, **kwargs):
        self.date = datetime.date(self.date.year, self.date.month, kwargs['day'])
        self.populate_body()
        self.populate_header()

    def move_next_month(self, *args, **kwargs):
        if self.date.month == 12:
            self.date = datetime.date(self.date.year + 1, 1, self.date.day)
        else:
            self.date = datetime.date(self.date.year, self.date.month + 1, self.date.day)
        self.populate_header()
        self.populate_body()

    def move_previous_month(self, *args, **kwargs):
        if self.date.month == 1:
            self.date = datetime.date(self.date.year - 1, 12, self.date.day)
        else:
            self.date = datetime.date(self.date.year, self.date.month -1, self.date.day)
        self.populate_header()
        self.populate_body()

# Корневой класс приложения

class RMApp(App):
    def build(self):
        if platform == "android": request_permissions([Permission.INTERNET, "com.google.android.gms.permission.AD_ID"])

        self.userPath = app_storage_path() if platform == "android" else ""

        ### Перенос данных из старого местоположения на Android в новое
        if platform == "android" and os.path.exists("../data.jsn"):
            shutil.move("../data.jsn", self.userPath + "data.jsn")
            try: shutil.rmtree("../backup")
            except: pass

        self.backupFolderLocation = self.userPath + "backup/"
        self.dataFile = "data.jsn"
        self.lastTimeBackedUp =   int(time.strftime("%H", time.localtime())) * 3600 \
                                + int(time.strftime("%M", time.localtime())) * 60 \
                                + int(time.strftime("%S", time.localtime()))
        self.differentFont = "DejaVuSans.ttf" # специальный шрифт для некоторых языков
        self.languages = {
            # список всех установленных языков, очередность должна совпадать с порядком столбцов,
            # key должен совпадать с принятой в Android локалью, value – с msg[1] для всех языков
            "en": ["English", None], # key: value
            "es": ["español", None],
            "ru": ["русский", None],
            "uk": ["українська", None],
            #"sr": ["srpski", None],
            "tr": ["Türkçe", None],
            "ka": ["ქართული", self.differentFont],
            "hy": ["Հայերեն", self.differentFont],
        }

        self.houses, self.settings, self.resources = self.initializeDB()
        self.load(allowSave=False)
        self.setParameters()
        self.setTheme()
        self.interface = AnchorLayout(anchor_x="center", anchor_y="top") # форма высшего уровня, поднимается над клавиатурой
        self.displayed = DisplayedList()
        self.createInterface()
        self.terPressed()
        self.updateTimer()
        self.backupRestore(delete=True, silent=True)
        if self.update(): self.popup(message=self.msg[310], dismiss=False)
        self.rep.checkNewMonth()
        self.rep.optimizeReportLog()
        self.save(backup=True)
        Clock.schedule_interval(self.updateTimer, 1)

        self.root = FloatLayout()

        return self.interface

    # Подготовка переменных

    def setParameters(self, reload=False):
        # Определение платформы
        self.desktop = True if platform == "win" or platform == "linux" or platform == "macosx" else False
        #self.desktop = False
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

        self.col = ":" if self.language != "hy" else "" # для армянского языка убираем двоеточия в разделе отчета
        self.textContextMenuSize = ('150sp', '50sp') if self.language == "en" else ('250sp', '50sp') # размер контекстного меню текста в зависимости от языка
        self.specialFont = self.languages[self.language][1]
        self.standardTextHeight = (Window.size[1] * .038 * self.fontScale()) if not self.desktop else 35
        self.standardTextHeightUncorrected = Window.size[1] * .038 # то же, что выше, но без коррекции на размер шрифта
        self.standardTextWidth = self.standardTextHeight * 1.3
        self.standardBarWidth = self.standardTextHeight
        self.standardTextWidth = self.standardTextHeight * 1.3
        self.standardRButtonRadius = .4
        self.orientationPrev = ""
        self.horizontalShrinkRatio = .15 # ширина левой боковой полосы на горизонтальной ориентации
        self.titleSizeHintY = .1  # ширина полосы заголовка
        self.tableSizeHintY = .1  # ширина полосы верхних табличных кнопок
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
        self.rep = Report() # инициализация отчета

        register('default_font', 'fontello.ttf', 'fontello.fontd')  # шрифты с иконками

        if not reload:  # при мягкой перезагрузке все, что ниже, не перезагружается (сохраняется)
            self.contactsEntryPoint = self.searchEntryPoint = self.popupEntryPoint = 0 # различные переменные
            self.stack = []
            self.showSlider = False
            self.restore = 0
            self.blockFirstCall = 0
            self.importHelp = 0
            EventLoop.window.bind(on_keyboard=self.hook_keyboard)
            Window.fullscreen = False # размеры и визуальные элементы
            self.spacing = Window.size[1]/400
            self.padding = Window.size[1]/300
            self.charLimit = 30 # лимит символов на кнопках
            self.allowCharWarning = True
            self.defaultKeyboardHeight = Window.size[1]*.4
            self.clickedBtnIndex = 0
            self.popups = []  # стек попапов, которые могут открываться один над другим
            self.listOnScreenLimit = 8 # кол-во пунктов списка, после которого будет прокручивание до этого пункта
            self.onClickColK  = .9 # коэффициент затемнения фона кнопки при клике
            self.onClickFlash = .1 # время появления теневого эффекта на кнопках
            self.backupTimeoutBeforeDelete = .02 # время задержки перед удалением, чтобы прошло резервирование
            self.buttonPressedBG = "button_background.png"
            self.fontXXL =  int(Window.size[1] / 25) # размеры шрифтов
            self.fontXL =   int(Window.size[1] / 30)
            self.fontL =    int(Window.size[1] / 35)
            self.fontM =    int(Window.size[1] / 40)
            self.fontS =    int(Window.size[1] / 45)
            self.fontXS =   int(Window.size[1] / 50)
            self.fontXXS =  int(Window.size[1] / 55)
            self.fontBigEntry = int(Window.size[1] / 41 * self.fontScale())  # шрифт для увеличенных полей ввода
            self.bigLanguage = True if self.language == "hy" or self.language == "ka" else False

            if Devmode:
                k = .4
                Window.size = (1120 * k, 2340 * k)
                Window.top = 80
                Window.left = 600

            # Действия в зависимости от платформы

            if self.desktop:
                from kivy.config import Config
                Config.set('input', 'mouse', 'mouse, disable_multitouch')
                #Config.set('input', 'mouse', 'mouse, enable_multitouch')
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
                    self.save(export=True)
                    ut.dprint(Devmode, "Выход из программы.")
                    self.checkOrientation(width=args[0].size[0], height=args[0].size[1])
                Window.bind(on_request_close=__close)
                Window.bind(on_resize=self.checkOrientation)

            else:
                try: plyer.orientation.set_portrait()
                except: pass

        rad = 37 # коэффициент закругления овальных кнопок, которое рассчитывается с учетом размера экрана
        self.buttonRadius = (Window.size[0] * Window.size[1]) / (Window.size[0] * rad)
        self.desktopRadK = 1.8 # коэффициент усиления радиуса для некоторых кнопок на ПК

    # Создание интерфейса

    def createInterface(self):
        """ Создание основных элементов """

        self.globalFrame = BoxLayout(orientation="vertical")
        self.boxHeader = BoxLayout(spacing=self.spacing, padding=self.padding)

        # Таймер

        TimerAndSetSizeHint = .21 if not self.desktop else None
        self.timerBox = BoxLayout(size_hint_x=TimerAndSetSizeHint, spacing=self.spacing, padding=(self.padding, 0))
        self.timer = Timer()
        self.timerBox.add_widget(self.timer)
        self.timerText = Label(halign="left", valign="center", pos_hint={"center_y": .5},
                               color=[self.standardTextColor[0], self.standardTextColor[1], self.standardTextColor[2], .9],
                               width=self.standardTextWidth, markup=True)
        if not self.desktop: self.timerText.font_size = self.fontXS * self.fontScale()
        self.timerBox.add_widget(self.timerText)

        # Заголовок таблицы

        self.headBox = BoxLayout(size_hint_x=.5, spacing=self.spacing)
        self.pageTitle = MyLabel(text="", font_size=self.fontL if self.desktop else self.fontS,
                                 color=self.titleColor, halign="center", valign="center", markup=True)

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
            self.pageTitle.text_size = (Window.size[0] * .4, None)
        else:
            self.boxHeader.add_widget(self.settingsButton)
            self.boxHeader.add_widget(self.headBox)
            self.boxHeader.add_widget(self.searchButton)
            self.pageTitle.text_size = (Window.size[0] * .7, None)

        self.globalFrame.add_widget(self.boxHeader)

        self.boxCenter = BoxLayout()
        self.mainBox = BoxLayout()
        self.boxCenter.add_widget(self.mainBox)
        self.listarea = BoxLayout(orientation="vertical")
        self.mainBox.add_widget(self.listarea)

        # Верхние кнопки таблицы

        self.titleBox = BoxLayout(size_hint_y=self.tableSizeHintY, padding=self.padding)
        self.listarea.add_widget(self.titleBox)
        tbWidth = [.29, .31, .1, .3] # значения ширины кнопок таблицы
        self.backButton = TableButton(text=self.button["back"], size_hint_x=tbWidth[0], disabled=True, background_color=self.globalBGColor)
        self.backButton.bind(on_release=self.backPressed)
        self.titleBox.add_widget(self.backButton)

        self.dropSortMenu = DropDown()
        self.sortButton = TableButton(size_hint_x=tbWidth[1], disabled=True, background_color=self.globalBGColor)
        self.titleBox.add_widget(self.sortButton)
        self.sortButton.bind(on_press=self.sortPressed)

        self.resizeButton = TableButton(size_hint_x=tbWidth[2], disabled=True, background_color=self.globalBGColor)
        self.titleBox.add_widget(self.resizeButton)
        self.resizeButton.bind(on_release=self.resizePressed)

        self.detailsButton = TableButton(size_hint_x=tbWidth[3], disabled=True, background_color=self.globalBGColor)
        self.detailsButton.bind(on_release=self.detailsPressed)
        self.titleBox.add_widget(self.detailsButton)

        if self.desktop: # на компьютере отменяем прозрачность верхних кнопок, чтобы убрать полосатость
            self.backButton.background_color[3] = self.sortButton.background_color[3] = \
                self.resizeButton.background_color[3] = self.detailsButton.background_color[3] = 1

        # Главный список

        self.mainList = BoxLayout(orientation="vertical", spacing=self.spacing)
        AL = AnchorLayout(anchor_x="center", anchor_y="top")
        AL.add_widget(self.mainList)
        self.listarea.add_widget(AL)

        # Слайдер и джойстик выбора позиции

        self.sliderBox = BoxLayout()
        value = self.settings[0][8]
        image = self.sliderImage
        self.slider = Slider(pos=(0, Window.size[1] * .75), orientation='horizontal', min=0.4, max=2,
                             padding=0, value=value, cursor_image=image)
        self.sliderBox.add_widget(self.slider)
        self.posSelector = GridLayout(rows=3, cols=3, size_hint=(None, None), padding=self.padding,
                                      size=(Window.size[0]/2.5, Window.size[1]/3.5))
        buttons = []
        for i in [1,2,3,4,5,6,7,8,9]:
            buttons.append(TableButton(text=self.button["dot"]))
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
            if   i == 1: buttons[len(buttons)-1].bind  (on_release=__click1)
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

        self.bottomButtons = BoxLayout(size_hint_y = self.bottomButtonsSizeHintY, spacing=self.spacing,
                                       padding = self.padding * 2)
        self.listarea.add_widget(self.bottomButtons)
        self.navButton = TableButton(text=self.button['nav'], disabled=True, background_color=self.globalBGColor,
                                     size_hint_x=.2)
        self.bottomButtons.add_widget(self.navButton)
        self.navButton.bind(on_release=self.navPressed)

        self.positive = RButton(background_color=self.positiveButtonBGColor, color=self.tableColor, radiusK=.7,
                                font_size=self.fontS)

        self.positive.bind(on_release=self.positivePressed)
        self.bottomButtons.add_widget(self.positive)

        self.neutral = TableButton(background_color=self.globalBGColor, disabled=True, size_hint_x=.2)
        self.neutral.bind(on_release=self.neutralPressed)
        self.bottomButtons.add_widget(self.neutral)

        #self.negative = TableButton(text="123",background_color=self.globalBGColor, size_hint_x=.20)
        #self.negative.bind(on_release=self.backPressed)
        #self.bottomButtons.add_widget(self.negative)

        self.globalFrame.add_widget(self.boxCenter)

        if not self.desktop:
            self.interface.add_widget(self.globalFrame)
        else: # в настольном режиме создаем дополнительные фреймы, чтобы отобразить главные кнопки сбоку
            self.desktopModeFrame = AnchorLayout(anchor_x="center", anchor_y="center")
            self.horizontalGrid = GridLayout(rows=1,cols=2)
            self.horizontalGrid.add_widget(self.desktopModeFrame)
            self.horizontalGrid.add_widget(self.globalFrame)
            self.interface.add_widget(self.horizontalGrid)

        self.checkOrientation()

    def setTheme(self):
        self.themes = {
            "3D":           "3D",
            self.msg[300]:  "dark",
            self.msg[301]:  "gray",
            self.msg[302]:  "morning",
            self.msg[303]:  "sepia",
            self.msg[304]:  "green",
            self.msg[305]:  "teal",
            self.msg[306]:  "purple",
            self.msg[307]:  "default"
        }

        self.themeDefault = [ [.93,.93,.93,.9], [.15, .33, .45, 1], [.18, .65, .83, 1] ] # фон таблицы, кнопки таблицы и title

        self.theme = self.settings[0][5] if isinstance(self.settings[0][5], str) else "default"

        if self.settings[0][5] == "": # определяем тему при первом запуске
            if platform == "android":
                from kvdroid.tools.darkmode import dark_mode
                if dark_mode() == True: self.theme = self.settings[0][5] = "gray"
                else: self.theme = self.settings[0][5] = "default"
            else: self.theme = self.settings[0][5] = "default"

        if Devmode == 0 and self.desktop: # пытаемся получить тему из файла на ПК
            self.themeOld = self.theme
            try:
                with open("theme.ini", mode="r") as file: self.theme = file.readlines()[0]
            except:
                ut.dprint(Devmode, "Не удалось прочитать файл theme.ini.")
                self.themeOverriden = False
            else:
                ut.dprint(Devmode, "Тема переопределена из файла theme.ini.")
                self.themeOverriden = True
        else: self.themeOverriden = False

        self.topButtonColor = [.73, .73, .73, 1] # "lightgray" # поиск, настройки и кнопки счетчиков
        ck = .9
        self.popupButtonColor = [.97, .97, .97]

        if self.theme == "dark" or self.theme == "morning": # темная тема
            self.mode = "dark"
            self.globalBGColor = [0, 0, 0, .5] #self.themeDark # фон программы
            self.buttonPressedOnDark = [.3, .3, .3, 1]  # цвет в темных темах, определяющий засветление фона кнопки
            self.scrollButtonBackgroundColor = [.14, .14, .15]  # фон пунктов списка
            self.tableBGColor = self.positiveButtonBGColor = [.18, .18, .19]  # цвет фона кнопок таблицы
            self.textInputBGColor = [.26, .26, .27, .95]
            self.textInputColor = [1, 1, 1]  # шрифт ввода текста в поля
            self.mainMenuButtonColor = [.95, .95, .95] # три главные кнопки неактивные
            self.iconColor = get_hex_from_color([.5, .5, .5]) # цвет иконки участка
            self.standardTextColor = [.9, .9, .9, 1] # основной текст всех шрифтов
            self.titleColor = self.mainMenuActivated = [.3, .82, 1, 1] # неон - цвет нажатой кнопки и заголовка
            self.scrollIconColor = [self.titleColor[0] * ck, self.titleColor[1] * ck, self.titleColor[2] * ck, .6] # иконка списка
            self.popupBackgroundColor = [.16, .16, .16, 1] # фон всплывающего окна
            self.linkColor = self.tableColor = [.95, .95, .96, 1] # цвет текста на плашках таблицы и кнопках главного меню
            self.lightGrayFlat = [.4, .4, .4, 1]
            self.darkGrayFlat = [.26, .26, .26, 1] # квартира "нет дома"
            self.createNewPorchButton = [.2, .2, .2, 1] # пункт списка создания нового подъезда
            self.interestColor = get_hex_from_color(self.getColorForStatus("1")) # "00BC7F" # "00CA94" # должен соответствовать зеленому статусу или чуть светлее
            self.timerOffColor = self.linkColor
            self.saveColor = "00E7C8"
            self.disabledColor = "4C4C4C"
            self.tabColors = [self.linkColor, "tab_background_teal.png"] # основной цвет вкладки и фон
            self.sliderImage = "slider_cursor.png"

            if self.theme == "morning": # Утро
                self.mainMenuButtonColor = self.timerOffColor = self.topButtonColor
                self.linkColor = self.tableColor = [.97, .97, .97, 1]
                self.mainMenuBGColor = self.tableBGColor =[.16, .16, .16]
                self.scrollButtonBackgroundColor = [.17, .17, .17]
                self.textInputBGColor = [.26, .26, .26, .95]
                self.positiveButtonBGColor = [.22, .22, .22]
                self.titleColor = self.mainMenuActivated = [.76, .65, .89]
                self.scrollIconColor = [.62, .73, .89]
                self.tabColors = [self.linkColor, "tab_background_purple_light.png"]
                self.sliderImage = "slider_cursor_mono.png"

        else: # "default"
            self.mode = "light"
            self.globalBGColor = [1,1,1,.5]
            self.linkColor = self.tableColor = self.mainMenuButtonColor = self.themeDefault[1]
            self.standardTextColor = [.13, .13, .13, 1]
            self.textInputColor = [0, 0, 0]
            self.mainMenuActivated = self.titleColor = [0,.47,.75]
            self.activatedColor = [0, .15, .35, .9]
            self.tableBGColor = self.positiveButtonBGColor = self.themeDefault[0]
            self.iconColor = get_hex_from_color([.5, .5, .5])
            self.scrollIconColor = [self.titleColor[0] * ck, self.titleColor[1] * ck, self.titleColor[2] * ck, .6]
            self.popupBackgroundColor = [.16, .16, .16]
            self.scrollButtonBackgroundColor = [.97,.97,.97]
            self.lightGrayFlat = [.6, .6, .6, 1]
            self.darkGrayFlat = [.43,.43,.43,1]
            self.createNewPorchButton = "dimgray"
            self.textInputBGColor = [.97, .97, .97, .95]
            self.interestColor = get_hex_from_color(self.getColorForStatus("1"))
            self.saveColor = "008E85"
            self.timerOffColor = self.themeDefault[1]
            self.disabledColor = get_hex_from_color(self.topButtonColor)
            self.tabColors = [self.linkColor, "tab_background_blue.png"]
            self.sliderImage = "slider_cursor.png"

            if self.theme == "purple": # Пурпур
                self.globalBGColor = [.95, .95, .95, .5]
                self.linkColor = [.29, .43, .65, 1]
                self.mainMenuButtonColor = self.timerOffColor = [.35, .33, .33, 1]
                self.scrollButtonBackgroundColor = [1,1,1]
                self.titleColor = self.tableColor = self.mainMenuActivated = [.36, .24, .53, 1]
                self.scrollIconColor = [self.titleColor[0] * ck, self.titleColor[1] * ck, self.titleColor[2] * ck, .6]
                self.textInputBGColor = [.99, .99, .99, .95]
                self.tableBGColor = [0.83, 0.83, 0.83, 1]
                self.positiveButtonBGColor = [0.86, 0.86, 0.86, 1]
                self.saveColor = "008E61"
                self.tabColors = [self.linkColor, "tab_background_purple.png"]
                self.sliderImage = "slider_cursor_mono.png"

            elif self.theme == "teal": # Бирюза
                self.titleColor = self.mainMenuActivated = self.themeDefault[2]
                self.scrollIconColor = [self.titleColor[0] * ck, self.titleColor[1] * ck, self.titleColor[2] * ck, .6]
                self.scrollButtonBackgroundColor = [.95, .96, .97]
                self.positiveButtonBGColor = self.tableBGColor = [.92,.94,.95,.9]
                self.tabColors = [self.linkColor, "tab_background_teal.png"]

            elif self.theme == "green": # Эко
                self.titleColor = self.mainMenuActivated = [.09, .65, .58, 1]
                self.scrollIconColor = [self.titleColor[0] * ck, self.titleColor[1] * ck, self.titleColor[2] * ck, .6]
                self.mainMenuButtonColor = self.timerOffColor = [.1, .3, .3, .8]
                self.tableBGColor = self.positiveButtonBGColor = [0.92, 0.94, 0.92, .9]
                self.iconColor = get_hex_from_color([.49, .51, .49])
                self.saveColor = get_hex_from_color(self.titleColor)
                self.tabColors = [self.linkColor, "tab_background_green.png"]
                self.sliderImage = "slider_cursor_mono.png"

            elif self.theme == "sepia":  # Сепия
                self.mainMenuButtonColor = [.28, .25, .3, .8]
                self.scrollButtonBackgroundColor = [.98, .97, .96]
                self.standardTextColor = self.textInputColor = [.21, .2, .2]
                self.tableBGColor = [.94, .93, .92, .9]

            elif self.theme == "gray": # Вечер
                self.mode = "dark"
                self.globalBGColor = [.12, .12, .12, .5]
                self.darkGrayFlat = [.4, .4, .4, 1]
                self.buttonPressedOnDark = [.4, .4, .4, 1]  # цвет в темных темах, определяющий засветление фона кнопки
                self.scrollButtonBackgroundColor = [.22, .22, .22]
                self.textInputBGColor = [.28, .28, .29, .95]
                self.positiveButtonBGColor = self.tableBGColor = [.01, .27, .44]
                self.titleColor = self.mainMenuActivated = [.76, .86, .99, 1]
                self.scrollIconColor = [self.titleColor[0] * ck, self.titleColor[1] * ck, self.titleColor[2] * ck, .6]
                self.mainMenuButtonColor = self.timerOffColor = self.topButtonColor
                self.standardTextColor = [.9, .9, .9, 1]
                self.textInputColor = [1, 1, 1]
                self.iconColor = get_hex_from_color([.6, .6, .6])
                self.saveColor = "00E79E"
                self.disabledColor = get_hex_from_color(self.darkGrayFlat)
                self.linkColor = self.tableColor = [.98, .98, 1]
                self.tabColors = [self.linkColor, "tab_background_gray.png"]
                self.sliderImage = "slider_cursor_mono.png"

            elif self.theme == "3D": # 3D
                self.mode = "dark"
                self.buttonTint = self.positiveButtonBGColor = [.8, .8, .8]
                self.globalBGColor = [.12, .12, .12, 1]
                self.buttonPressedOnDark = [.4, .4, .4, 1] # цвет в темных темах, определяющий засветление фона кнопки
                self.iconColor = get_hex_from_color([.6, .6, .6])
                self.titleColor = self.mainMenuActivated = [0, 1, .9, 1]#.95, .81, 1]
                self.scrollIconColor = [self.titleColor[0] * ck, self.titleColor[1] * ck, self.titleColor[2] * ck, .6]
                self.linkColor = self.mainMenuButtonColor = self.tableColor = self.timerOffColor = [.97, 1, .97, 1]
                self.textInputBGColor = [.42, .42, .42, .95]
                self.standardTextColor = [.9, .9, .9]
                self.textInputColor = [1, 1, 1]
                self.interestColor = get_hex_from_color(self.titleColor)
                self.saveColor = get_hex_from_color(self.titleColor)
                self.disabledColor = get_hex_from_color(self.darkGrayFlat)
                self.tabColors = [self.linkColor, "tab_background_3d.png"]
                self.bottomButtonsSizeHintY = .11
                self.sliderImage = "slider_cursor_mono.png"

        self.mainMenuButtonColor2 = get_hex_from_color(self.mainMenuButtonColor)
        self.titleColor2 = get_hex_from_color(self.titleColor)
        self.timerOffColor[3] = .9
        if self.theme == "purple": self.positiveButtonColor = get_hex_from_color(self.linkColor)
        elif self.theme == "morning": self.positiveButtonColor = get_hex_from_color(self.scrollIconColor)
        else: self.positiveButtonColor = self.titleColor2
        self.scrollColor = get_hex_from_color(self.scrollIconColor)
        k = .98 if self.mode == "light" else .8
        self.scrollButtonBackgroundSecondaryColor = [
            self.scrollButtonBackgroundColor[0] * k,
            self.scrollButtonBackgroundColor[1] * k,
            self.scrollButtonBackgroundColor[2] * k
        ]

        Window.clearcolor = self.globalBGColor

        # Иконки для кнопок

        if self.theme == "purple" or self.theme == "green": colNN = get_hex_from_color(self.tableColor)
        else: colNN = None
        self.button = {
            "building": f" [color={self.scrollColor}][b]{icon('icon-building-filled')}[/b][/color]", # центральный список
            "porch":    f" [color={self.scrollColor}]{icon('icon-login')}[/color]",
            "pin":      f" [color={self.scrollColor}]{icon('icon-pin')}[/color]",
            "map":      f" [color={self.scrollColor}]{icon('icon-map')}[/color]",
            "entry":    f" [color={self.scrollColor}]{icon('icon-chat')}[/color]",
            "plus-1":   f" [color={self.scrollColor}][b]{icon('icon-plus-1')}[/b][/color]",
            "home":     f" [color={self.scrollColor}][b]{icon('icon-home-1')}[/b][/color]",

            "plus":     f"[b][color={self.positiveButtonColor}]{icon('icon-plus-squared-alt')}[/color][/b]", # центральная кнопка
            "edit":     f"[b][color={self.positiveButtonColor}]{icon('icon-edit-1')}[/color][/b]",
            "search2":  f"[b][color={self.positiveButtonColor}]{icon('icon-search-circled')}[/color][/b]",
            "top":      f"[b][color={self.positiveButtonColor}]{icon('icon-up-open')}[/color][/b] {self.msg[143]}",
            "save":     f"[b][color={self.saveColor}]{icon('icon-ok-circled')} {self.msg[5]}[/b][/color]",
            "add":      f"[b][color={self.saveColor}]{icon('icon-ok-circled')} {self.msg[188]}[/b][/color]",

            "ok":       icon("icon-ok-1") + " OK",
            "back":     icon("icon-left-2"),
            "details":  icon("icon-pencil-1"),
            "search":   icon("icon-search-1"),
            "dot":      icon("icon-dot-circled"),
            "menu":     icon("icon-menu"),
            "floppy":   icon("icon-floppy"),
            "calendar": icon("icon-calendar-1"),
            "worked":   icon("icon-arrows-cw-1"),
            "cog":      icon("icon-cog-1"),
            "contact":  icon("icon-user-plus"),
            "phone1":   icon("icon-phone-1"),
            "resize":   icon("icon-resize-full-alt-2"),
            "sort":     icon("icon-sort-alt-up"),
            "target":   icon("icon-target-1"),
            "shrink":f"{icon('icon-scissors')} {self.msg[169]}",
            "list":     icon("icon-doc-text-inv"),
            "bin":   f"{icon('icon-trash-1')}\n{self.msg[173]}",
            "note":     icon("icon-sticky-note"),
            "chat":     icon("icon-chat"),
            "log":      icon("icon-history"),
            "info":     icon('icon-info-circled'),
            "share":    icon("icon-share-squared"),
            "export":   icon("icon-upload-cloud"),
            "import":   icon("icon-download-cloud"),
            "open":     icon("icon-folder-open"),
            "restore":  icon("icon-upload-1"),
            "wipe":     icon("icon-trash-1"),
            "help":     icon("icon-help-circled"),
            "arrow":    icon("icon-right-dir"),
            "nav":      icon("icon-location-circled", color=colNN),
            "flist":    icon("icon-align-justify", color=colNN),
            "fgrid":    icon("icon-th-large", color=colNN),
            "phone":    icon("icon-phone-circled", color=colNN),
            "phone0":   icon("icon-phone-circled", color=self.disabledColor),
            "lock":  f"{icon('icon-lock-1')}\n[b]{self.msg[206]}[/b]",
            "record":f"{icon('icon-pencil-1')}\n[b]{self.msg[163]}[/b]",
            "reject":f"{icon('icon-block-1')}\n[b]{self.msg[207]}[/b]",
            "warn":     icon("icon-attention"),
            "up":       icon("icon-up-1"),
            "down":     icon("icon-down-1"),
            "user":     icon("icon-user-1"),
            "yes":      self.msg[297],
            "no":       self.msg[298],
            "cancel":   self.msg[190],
            "link":    icon("icon-link-ext"),
            "":         ""
        }

        self.emoji = {
            "check":    "\u2611" # галочка
        }

    # Основные действия с центральным списком

    def updateList(self):
        """Заполнение главного списка элементами"""

        try:
            self.stack = list(dict.fromkeys(self.stack))
            self.mainList.clear_widgets()
            self.popupEntryPoint = 0
            if not self.showSlider: self.sortButton.disabled = True
            self.navButton.disabled = True
            self.navButton.text = ""

            # Считываем содержимое Feed/displayed

            self.pageTitle.text = f"[ref=title]{self.displayed.title}[/ref]" if "View" in self.displayed.form \
                else self.displayed.title

            #from kvdroid.tools.lang import device_lang
            #DL = device_lang()
            #self.pageTitle.text = str(DL)

            if self.displayed.positive != "":
                self.positive.disabled = False
                self.positive.text = f"[b]{self.displayed.positive}[/b]"
                self.positive.color = self.tableColor
            else:
                self.positive.text = ""
                self.positive.disabled = True

            if self.displayed.neutral != "":
                self.neutral.disabled = False
                self.neutral.text = self.displayed.neutral
                if self.neutral.text == self.button['phone'] and self.flat.phone == "":
                    self.neutral.text = self.button['phone0']
                    self.neutral.disabled = True
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

            self.backButton.disabled = True if not self.displayed.back else False

            if self.displayed.tip != None:
                if len(self.displayed.tip) == 2:
                    if self.displayed.tip[0] != None:
                        self.mainList.add_widget(self.tip(text=self.displayed.tip[0], icon=self.displayed.tip[1]))
                else:
                    self.mainList.add_widget(self.tip(self.displayed.tip))

            if "View" in self.displayed.form:
                self.navButton.disabled = False
                self.navButton.text = self.button['nav']

            footer = self.displayed.footer[0]

            # Обычный список (этажей нет)

            floorK = 1 if self.desktop else .8 # коэффициент размера цифры этажа

            if self.displayed.form != "porchView" or \
                    (self.displayed.form == "porchView" and not self.porch.floors()):
                height1 = self.standardTextHeight * 2 / self.fontScale()
                if self.desktop: height1 = height1 * .7
                height = height1
                self.scrollWidget = GridLayout(cols=1, spacing=self.spacing*1.5, padding=self.padding*2,
                                               size_hint_y=None)
                self.scrollWidget.bind(minimum_height=self.scrollWidget.setter('height'))
                self.scroll = ScrollView(size=(self.mainList.size[0]*.9, self.mainList.size[1]*.9),
                                         bar_width=self.standardBarWidth, scroll_type=['bars', 'content'])
                self.btn = []

                for i in range(len(self.displayed.options)):
                    label = self.displayed.options[i]
                    marker = f"[size=0][color={get_hex_from_color([0,0,0,0])}]{i}[/color][/size]"
                    if (self.displayed.form == "porchView" or self.displayed.form == "con") and "{" in label:
                        status = label[label.index("{") + 1: label.index("}")]  # определение статуса по цифре
                        label = label[3:] # удаление статуса из строки
                    else:
                        status = ""

                    addPhone = addNote = addRecord = False
                    valign = "center"
                    if self.displayed.form == "porchView" and len(self.porch.flats) > 0:
                        flat = self.porch.flats[i]
                        if len(flat.records) > 0: addRecord = True
                        if flat.phone != "": addPhone = True
                        if flat.note != "": addNote = True
                    elif self.displayed.form == "flatView":
                        height = height1
                        valign = "top"

                    # Добавление пункта списка

                    if self.msg[8] in label or self.displayed.form == "repLog":
                        # отдельный механизм добавления записей журнала отчета + ничего не найдено в поиске
                        self.btn.append(MyLabel(text=label.strip(), color=self.standardTextColor, halign="left",
                                                           valign="top", size_hint_y=None, height=height1, markup=True,
                                                            text_size=(Window.size[0]*self.SR-self.standardTextHeight, height1)))
                        self.scrollWidget.add_widget(self.btn[i])

                    else: # стандартное добавление

                        gap = 1.05 # зазор между квартирами в списке
                        box = BoxLayout(orientation="vertical", size_hint_y=None)

                        if self.displayed.form != "porchView" or self.button['plus-1'] in self.displayed.options[0]:
                            # вид для всех списков, кроме подъезда - без фона (а также кнопки "Создайте дом")
                            self.btn.append(ScrollButton(text=marker+label.strip(), height=height*2, valign=valign))

                        else: # вид для списка подъезда - с фоном и закругленными квадратиками
                            if not "." in label:
                                self.scrollWidget.spacing = (self.spacing, 0)
                                self.btn.append(FlatButton(text=marker+label.strip(), height=height, status=status,
                                                           size_hint_y=None))
                            else:
                                continue

                        last = len(self.btn)-1
                        box.add_widget(self.btn[last])

                        if addRecord or addPhone or addNote: # если есть запись посещения, телефон или заметка, добавляем снизу
                            gray = get_hex_from_color(self.topButtonColor if self.mode=="light" else self.standardTextColor)
                            if flat.phone != "":
                                myicon = self.button["phone1"]
                                phone = f"[color={gray}]{myicon}[/color]\u00A0{flat.phone}\u00A0\u00A0"
                            else:
                                phone = ""
                            if flat.note != "":
                                myicon = self.button["note"]
                                if self.msg[206].lower() in flat.note[:30]: # если в заметке есть "нет дома", обрезаем заметку по это слово
                                    limit = flat.note.index("\n") if "\n" in flat.note else len(flat.note)
                                else: # иначе обрезаем по размеру шрифта в системе
                                    сharLimit = int(30 / self.fontScale()) if not self.desktop else int(Window.size[0] / 13)
                                    limit = int(сharLimit/self.fontScale())
                                note = f"[color={gray}]{myicon}[/color]\u00A0{flat.note[:limit]}\u00A0\u00A0"
                                if "\n" in note: note = note[ : note.index("\n")] + "  "
                            else:
                                note = ""
                            if len(flat.records) > 0:
                                myicon = self.button["chat"]
                                record = f"[color={gray}]{myicon}[/color]\u00A0{flat.records[0].title}"
                            else:
                                record = ""
                            text = phone + note + record
                            box.add_widget(MyLabel(
                                text=text, markup=True, color=self.standardTextColor, halign="left", valign="top",
                                size_hint_y=None, height=height1*self.fontScale(),
                                text_size = (Window.size[0]*self.SR-self.standardTextHeight, height1)))
                            box.height = height * gap + height1*self.fontScale()
                        else:
                            box.height = height * gap

                        if footer != []: # создаем индикаторы-футеры, если они есть
                            self.scrollWidget.spacing = self.spacing * 10
                            box.height = height * 1.32 * gap
                            footerGrid = GridLayout(rows=1, cols=len(footer[i]), size_hint_y=None, height=height/3)
                            for button in range(len(footer[i])):
                                footerGrid.add_widget(FooterButton(text=str(footer[i][button]), parentIndex=i))
                            box.add_widget(footerGrid)

                        elif self.displayed.form == "houseView":
                            if "[/i]" in label.strip() and self.msg[6] in label.strip():
                                self.btn[i].background_color = self.scrollButtonBackgroundSecondaryColor

                        elif self.displayed.form == "flatView" and len(self.flat.records[0].title)>0 and\
                                self.flat.records[0].title in label and "[i]" in self.btn[len(self.btn) - 1].text:
                            # увеличиваем первую запись, если она есть
                            button = self.btn[len(self.btn) - 1]
                            co = (len(self.flat.records[0].title) + 175) / 2150
                            if co > .3: co = .3
                            lastRec = MyTextInput(text=self.flat.records[0].title, size_hint_y=None, multiline=True,
                                                  color=self.standardTextColor, background_color=self.globalBGColor,
                                                  disabled=True, height=Window.size[1]*co)
                            button.text = button.text[: button.text.index("[i]")]
                            button.valign = "center"
                            button.size_hint_y = None
                            button.height = height * 1.05
                            box.add_widget(lastRec)
                            box.height = Window.size[1] * co + button.height

                        self.scrollWidget.add_widget(box)

                self.scrollWidget.add_widget(Button(size_hint_y=None, # пустая кнопка для решения бага последней записи
                                                    height=height, halign="center", valign="center",
                                                    text_size=(Window.size[0]-15, height-10), background_normal="",
                                                    background_color=self.globalBGColor, background_down=""))
                self.scroll.add_widget(self.scrollWidget)
                self.mainList.add_widget(self.scroll)

            # Вид подъезда с этажами

            elif self.settings[0][7] == 1: # поэтажная раскладка с масштабированием
                spacing = self.spacing * 2
                self.floorview = GridLayout(cols=self.porch.columns+1, rows=self.porch.rows, spacing=spacing,
                                            padding=(self.padding*2, 0))
                for i in range(len(self.displayed.options)):
                    flat = self.displayed.options[i]
                    try:  # показ цифры этажа
                        self.floorview.add_widget(Label(text=flat, halign="right", color=self.standardTextColor,
                                                        width=self.standardTextHeight/3,
                                                        size_hint_x=None, font_size=self.fontXS*floorK))
                    except:
                        if "." in flat.number: self.floorview.add_widget(Widget())
                        else:
                            self.floorview.add_widget(FlatButton(text=flat.number, status=flat.status, size_hint_y=0,
                                                                 grid=True))
                self.sliderToggle()
                self.mainList.add_widget(self.floorview)

            else: # без масштабирования

                if self.settings[0][8] != 0: # расчеты расстояний и зазоров
                    size = self.standardTextHeight * self.settings[0][8] * 1.5
                else:
                    size = self.standardTextHeight
                noScaleSpacing = self.spacing * 2
                floorLabelWidth = size / 6
                diffX = self.mainList.size[0] - (size * self.porch.columns + size/4) - (noScaleSpacing * self.porch.columns)
                diffY = self.mainListsize1 - (size * self.porch.rows) - (noScaleSpacing * self.porch.rows)

                # Определение центровки

                if self.settings[0][1] == 1:    self.noScalePadding = [0, 0, diffX, diffY / 2]  # влево вверху
                elif self.settings[0][1] == 2:  self.noScalePadding = [diffX / 2, 0, diffX / 2, diffY]  # по центру вверху
                elif self.settings[0][1] == 3:  self.noScalePadding = [diffX, 0, diffY, 0]  # справа вверху
                elif self.settings[0][1] == 4:  self.noScalePadding = [0, diffY / 2, diffX, diffY / 2] # влево по центру
                elif self.settings[0][1] == 6:  self.noScalePadding = [diffX, diffY / 2, 0, diffY / 2]  # справа по центру
                elif self.settings[0][1] == 7:  self.noScalePadding = [0, diffY, diffX, 0 / 2]  # влево внизу
                elif self.settings[0][1] == 8:  self.noScalePadding = [diffX/2, diffY, 0, diffX/2]  # снизу по центру
                elif self.settings[0][1] == 9:  self.noScalePadding = [diffX, diffY, 0, 0]  # справа снизу
                else:                           self.noScalePadding = [diffX / 2, diffY / 2, diffX / 2, diffY / 2]  # по центру

                if self.noScalePadding[0] < 0 or self.noScalePadding[1] < 0 or self.noScalePadding[2] < 0 or self.noScalePadding[3] < 0: # если слишком большой подъезд, включаем масштабирование
                    self.settings[0][7] = 1
                    self.porchView()
                    return

                BL = BoxLayout()
                self.floorview = GridLayout(row_force_default=True, row_default_height=size, # отрисовка
                                            col_force_default=True, col_default_width=size,
                                            cols_minimum={0: floorLabelWidth},
                                            cols=self.porch.columns + 1,
                                            rows=self.porch.rows, spacing=noScaleSpacing, padding=self.noScalePadding)

                for i in range(len(self.displayed.options)):
                    flat = self.displayed.options[i]
                    try: # показ цифры этажа
                        self.floorview.add_widget(Label(text=flat, halign="right", valign="center", width=floorLabelWidth,
                                                        font_size=self.fontXS*floorK, height=size, size_hint=(None, None),
                                                        color=self.standardTextColor))
                    except:
                        if "." in flat.number: self.floorview.add_widget(Widget())
                        else:
                            self.floorview.add_widget(FlatButton(text=flat.number, status=flat.status, width=size,
                                                                 height=size, grid=True, size_hint_x=None, size_hint_y=None))
                BL.add_widget(self.floorview)
                self.mainList.add_widget(BL)
                self.sliderToggle()

        except: # в случае ошибки пытаемся восстановить последнюю резервную копию
            if self.restore < 10:
                ut.dprint(Devmode, f"Файл базы данных поврежден, пытаюсь восстановить резервную копию {self.restore}.")
                result = self.backupRestore(restoreNumber=self.restore, allowSave=False)
                if result != False:
                    ut.dprint(Devmode, "Резервная копия восстановлена.")
                    self.restore += 1
                    self.restart("soft")
                    self.save(backup=False)
                    self.updateList()
                else:
                    ut.dprint(Devmode, "Резервных копий больше нет.")
                    self.restore = 10
            else:
                self.popup("emergencyExport", title=self.msg[9], message=self.msg[10])

    def sliderToggle(self, mode=""):
        self.settings[0][7] = 0
        if mode == "off": self.showSlider = False
        if self.showSlider and not self.sliderBox in self.boxHeader.children:
            self.boxHeader.clear_widgets()
            self.boxHeader.add_widget(self.sliderBox)
            if self.orientation == "v": self.boxFooter.add_widget(self.posSelector)
            else: self.bottomButtons.add_widget(self.posSelector)
        if not self.showSlider and self.sliderBox in self.boxHeader.children:
            self.boxHeader.remove_widget(self.sliderBox)
            if self.orientation == "v": self.boxFooter.remove_widget(self.posSelector)
            else: self.bottomButtons.remove_widget(self.posSelector)
            if self.settings[0][22]: # если есть таймер
                self.boxHeader.add_widget(self.timerBox)
                self.boxHeader.add_widget(self.headBox)
                self.boxHeader.add_widget(self.setBox)
            else: # если нет таймера
                self.boxHeader.add_widget(self.settingsButton)
                self.boxHeader.add_widget(self.headBox)
                self.boxHeader.add_widget(self.searchButton)

    def sliderGet(self, x, y):
        self.settings[0][8] = self.slider.value
        self.porchView()

    def clickOnList(self, instance):
        """ Действия, которые совершаются на указанных списках по нажатию на пункт списка """
        def __do(*args): # действие всегда выполняется с запаздыванием, чтобы отобразилась анимация на кнопке
            if self.msg[6] in instance.text: # "создать подъезд"
                text = instance.text[len(self.msg[6])+45 : ] # число символов во фразе msg[6] + 45 (на форматирование)
                #print(text) # должно выглядеть: 1[/i]
                if "[/i]" in text: text = text[ : text.index("[")]
                self.house.addPorch(text.strip())
                self.save()
                self.houseView(instance=instance)
                return
            elif self.msg[11] in instance.text or self.msg[12] in instance.text: # "создайте"
                self.positivePressed()
                return

            if "[size=0]" in instance.text:
                markerPos = instance.text[ instance.text.index("color=#00000000")+16 : instance.text.index("[/color]")]
                self.choice = self.clickedBtnIndex = int(markerPos)

            if self.displayed.form == "porchView" or self.displayed.form == "con":
                if self.showSlider:
                    self.showSlider = False
                    self.sliderToggle()
                self.contactsEntryPoint = 0
                self.searchEntryPoint = 0

            if self.displayed.form == "ter":
                self.house = self.houses[self.choice]
                self.selectedHouse = self.choice
                self.houseView(instance=instance)

            elif self.displayed.form == "houseView":
                self.porch = self.house.porches[self.choice]
                self.selectedPorch = self.choice
                self.porchView(instance=instance)

            elif self.displayed.form == "porchView":
                if self.porch.floors():
                    try: number = instance.text[instance.text.index("[b]") + 3: instance.text.index("[/b]")].strip()
                    except: number = instance.text.strip()
                    for i in range(len(self.porch.flats)):
                        if number == self.porch.flats[i].number:
                            self.flat = self.porch.flats[i]
                            self.selectedFlat = i
                            break
                else:
                    self.flat = self.porch.flats[self.choice]
                    for i in range(len(self.porch.flats)):
                        if self.flat.number == self.porch.flats[i].number:
                            self.selectedFlat = i
                            break
                self.flatView(call=False, instance=instance)

            elif self.displayed.form == "flatView": # режим редактирования записей
                self.selectedRecord = self.choice
                try: self.record = self.flat.records[self.selectedRecord]
                except: return # для защиты от ошибки при нажатии 2 пальцами
                else: self.recordView(instance=instance) # вход в запись посещения

            elif self.displayed.form == "con": # контакты
                self.selectedCon = self.choice
                h = self.allcontacts[self.selectedCon][7][0]  # получаем дом, подъезд и квартиру выбранного контакта
                p = self.allcontacts[self.selectedCon][7][1]
                f = self.allcontacts[self.selectedCon][7][2]
                if self.allcontacts[self.selectedCon][8] != "virtual": self.house = self.houses[h]
                else: self.house = self.resources[1][h] # заменяем дом на ресурсы для отдельных контактов
                self.selectedHouse = h
                self.porch = self.house.porches[p]
                self.selectedPorch = p
                self.flat = self.porch.flats[f]
                self.selectedFlat = f
                self.contactsEntryPoint = 1
                self.searchEntryPoint = 0
                self.flatView(instance=instance)

            elif self.displayed.form == "search": # поиск
                self.selectedCon = self.choice
                h = self.searchResults[self.selectedCon][0][0]  # получаем номера дома, подъезда и квартиры
                p = self.searchResults[self.selectedCon][0][1]
                f = self.searchResults[self.selectedCon][0][2]
                if self.searchResults[self.selectedCon][1] != "virtual": self.house = self.houses[h] # regular contacts
                else: self.house = self.resources[1][h]
                self.selectedHouse = h
                self.porch = self.house.porches[p]
                self.selectedPorch = p
                self.flat = self.porch.flats[f]
                self.selectedFlat = f
                self.searchEntryPoint = 1
                self.contactsEntryPoint = 0
                self.flatView(instance=instance)

        Clock.schedule_once(__do, 0)

    def titlePressed(self, instance, value):
        """ Нажатие на заголовок экрана """
        def __edit(*args):
            try:
                if value == "title":
                    self.multipleBoxEntries[0].focus = True
                elif value == "note":
                    if self.msg[152] in instance.text: self.multipleBoxEntries[1].focus = True
                    else:
                        for i in range(len(self.multipleBoxEntries)):
                            if self.multipleBoxLabels[i].text == self.msg[18]:
                                self.multipleBoxEntries[i].focus = True
                                break
            except: pass

        if value == "title":
            self.detailsPressed()
            Clock.schedule_once(__edit, .3)
        elif value == "report" and self.settings[0][3] > 0:
            self.popup(title=self.msg[247], message=self.msg[202])
        elif value == "note":
            self.detailsPressed()
            Clock.schedule_once(__edit, .3)

    def detailsPressed(self, instance=None):
        """ Нажата кнопка настроек рядом с заголовком (редактирование данного объекта) """
        self.func = self.detailsPressed
        if self.confirmNonSave(): return

        self.showSlider = False
        self.sliderToggle()
        if self.displayed.form == "houseView" or self.displayed.form == "noteForHouse" or \
            self.displayed.form == "createNewPorch":  # детали участка
            self.displayed.form = "houseDetails"
            self.createMultipleInputBox(
                title=f"{self.house.title} {self.button['arrow']} {self.msg[16]}",
                options=[self.msg[14], self.msg[17], self.msg[18]],
                defaults=[self.house.title, self.house.date, self.house.note],
                multilines=[False, False, True],
                disabled=[False, False, False]
            )

        elif self.displayed.form == "porchView" or self.displayed.form == "noteForPorch" or \
            self.displayed.form == "createNewFlat": # детали подъезда
            self.displayed.form = "porchDetails"
            settings = self.msg[20] if self.house.type == "private" else self.msg[19]
            options = [settings, self.msg[18]]
            defaults = [self.porch.title, self.porch.note]
            self.createMultipleInputBox(
                title=f"{self.house.getPorchType()[1]} {self.porch.title} {self.button['arrow']} {self.msg[16]}",
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
            address = self.msg[15] if self.house.type == "virtual" else self.msg[14]
            porch = self.house.getPorchType()[1] + (":" if self.language != "hy" else ".")
            if self.language != "ka": porch = porch[0].upper() + porch[1:]
            number = self.msg[24] if self.house.type == "condo" else self.msg[25]
            addressDisabled = False if self.house.type == "virtual" else True
            porchDisabled = False if self.house.type == "virtual" else True
            numberDisabled = True if self.porch.floors() or self.flat.number == "virtual" else False
            self.createMultipleInputBox(
                title=self.flatTitle + f" {self.button['arrow']} {self.msg[16]}",
                options=[self.msg[22], self.msg[23], address, porch, number, self.msg[18]],
                defaults=[self.flat.getName(), self.flat.phone, self.house.title, self.porch.title, self.flat.number, self.flat.note],
                multilines=[False, False, False, False, False, True],
                disabled=[False, False, addressDisabled, porchDisabled, numberDisabled, False],
                neutral=self.button["phone"]
            )

        elif self.displayed.form == "rep": # журнал отчета
            options=[]
            for line in self.resources[2]:
                options.append(line)
            tip = self.msg[240] % self.rep.reportLogLimit if len(options) == 0 else None
            self.displayed.update(
                title=self.msg[26],
                options=options,
                form="repLog",
                positive=self.button["top"],
                tip=tip
            )
            if instance != None: self.stack.insert(0, self.displayed.form)
            self.updateList()

        elif self.displayed.form == "set": # Помощь
            if self.language == "ru" or self.language == "uk":
                webbrowser.open("https://github.com/antorix/Rocket-Ministry/wiki/ru")
            else:
                webbrowser.open("https://github.com/antorix/Rocket-Ministry/wiki")

    def backPressed(self, instance=None):
        """ Нажата кнопка «назад» """
        self.func = self.backPressed
        if self.confirmNonSave(): return
        if len(self.stack) > 0: del self.stack[0]
        if self.displayed.form == "repLog": self.repPressed()
        elif len(self.stack) > 0:
            if self.stack[0] == "ter": self.terPressed()
            elif self.stack[0] == "con": self.conPressed()
            elif self.stack[0] == "search": self.find()
            elif self.stack[0] == "houseView":
                self.showSlider = False
                self.sliderToggle()
                self.houseView()
            elif self.stack[0] == "porchView" or self.blockFirstCall == 1 or self.msg[162] in self.pageTitle.text:
                self.porchView()
            elif self.stack[0] == "flatView": self.flatView()
        self.updateMainMenuButtons()

    def resizePressed(self, instance=None):
        """ Нажата кнопка слайдера """
        if self.resources[0][1][1] == 0:
            self.resources[0][1][1] = 1
            self.save()
            self.popup(title=self.msg[247], message=self.msg[27] % self.button['resize'])
        if self.showSlider:
            self.showSlider = False
            self.save()
        else:
            self.showSlider = True
        self.porchView()
        self.sliderToggle("on")

    def sortPressed(self, instance=None):
        self.dropSortMenu.clear_widgets()
        if self.displayed.form == "ter": # меню сортировки участков
            sortTypes = [
                "[u]"+self.msg[29]+"[/u]" if self.settings[0][19] == "н" else self.msg[29], # название
                "[u]"+self.msg[38]+"[/u]" if self.settings[0][19] == "р" else self.msg[38], # размер
                "[u]"+self.msg[31]+"[/u]" if self.settings[0][19] == "и" else self.msg[31], # интерес
                "[u]"+self.msg[30]+"[/u]" if self.settings[0][19] == "д" else self.msg[30], # дата
                f"[u]{self.msg[32]}[/u] {self.button['down']}" if self.settings[0][19] == "п" else\
                    f"{self.msg[32]} {self.button['down']}", # обработка
                f"[u]{self.msg[32]}[/u] {self.button['up']}" if self.settings[0][19] == "о" else\
                    f"{self.msg[32]} {self.button['up']}"# обработка назад
            ]

            for i in range(len(sortTypes)):
                btn = SortListButton(text=sortTypes[i])
                def __resortHouses(instance=None):
                    if instance.text == sortTypes[0]:   self.settings[0][19] = "н"
                    elif instance.text == sortTypes[1]: self.settings[0][19] = "р"
                    elif instance.text == sortTypes[2]: self.settings[0][19] = "и"
                    elif instance.text == sortTypes[3]: self.settings[0][19] = "д"
                    elif instance.text == sortTypes[4]: self.settings[0][19] = "п"
                    elif instance.text == sortTypes[5]: self.settings[0][19] = "о"
                    self.save()
                    self.terPressed()
                    self.dropSortMenu.dismiss()
                btn.bind(on_release=__resortHouses)
                self.dropSortMenu.add_widget(btn)
            self.dropSortMenu.bind(on_select=lambda instance, x: setattr(self.sortButton, 'text', x))
            self.sortButton.bind(on_release=self.dropSortMenu.open)

        elif self.displayed.form == "porchView":
            self.porch.flatsNonFloorLayoutTemp = None
            if not self.porch.floors(): # меню сортировки квартир в подъезде
                sortTypes = [
                    f"[u]{self.msg[34]}[/u] {self.button['down']}" if self.porch.flatsLayout == "н" else\
                        f"{self.msg[34]} {self.button['down']}", # номер
                    f"[u]{self.msg[34]}[/u] {self.button['up']}" if self.porch.flatsLayout == "о" else\
                        f"{self.msg[34]} {self.button['up']}", # номер обратно
                    "[u]"+self.msg[36]+"[/u]" if self.porch.flatsLayout == "с" else self.msg[36], # статус
                    "[u]"+self.msg[37]+"[/u]" if self.porch.flatsLayout == "з" else self.msg[37], # заметка
                    "[u]"+self.msg[35]+"[/u]" if self.porch.flatsLayout == "т" else self.msg[35]  # телефон
                ]
                for i in range(len(sortTypes)):
                    btn = SortListButton(text=sortTypes[i])
                    def __resortFlats(instance=None):
                        if instance.text == sortTypes[0]:   self.porch.flatsLayout = "н"
                        elif instance.text == sortTypes[1]: self.porch.flatsLayout = "о"
                        elif instance.text == sortTypes[2]: self.porch.flatsLayout = "с"
                        elif instance.text == sortTypes[3]: self.porch.flatsLayout = "з"
                        elif instance.text == sortTypes[4]: self.porch.flatsLayout = "т"
                        self.save()
                        self.porchView(sortFlats=True, scroll_to=0)
                        self.dropSortMenu.dismiss()
                    btn.bind(on_release=__resortFlats)
                    self.dropSortMenu.add_widget(btn)
                self.dropSortMenu.bind(on_select=lambda instance, x: setattr(self.sortButton, 'text', x))
                self.sortButton.bind(on_release=self.dropSortMenu.open)

        elif self.displayed.form == "con": # меню сортировки контактов
            sortTypes = [
                "[u]"+self.msg[21]+"[/u]" if self.settings[0][4] == "и" else self.msg[21], # имя
                "[u]"+self.msg[33]+"[/u]" if self.settings[0][4] == "а" else self.msg[33], # адрес
                #"[u]"+self.msg[30]+"[/u]" if self.settings[0][4] == "д" else self.msg[30] # дата последней встречи
            ]
            for i in range(len(sortTypes)):
                btn = SortListButton(text=sortTypes[i])
                def __resortCons(instance=None):
                    if instance.text == sortTypes[0]:   self.settings[0][4] = "и"
                    elif instance.text == sortTypes[1]: self.settings[0][4] = "а"
                    #elif instance.text == sortTypes[2]: self.settings[0][4] = "д"
                    #elif instance.text == sortTypes[3]: self.settings[0][4] = "з"
                    self.save()
                    self.conPressed()
                    self.dropSortMenu.dismiss()
                btn.bind(on_release=__resortCons)
                self.dropSortMenu.add_widget(btn)
            self.dropSortMenu.bind(on_select=lambda instance, x: setattr(self.sortButton, 'text', x))
            self.sortButton.bind(on_release=self.dropSortMenu.open)

        elif self.displayed.form == "createNewFlat": # кнопка "Список" на форме создания квартир
            self.popup("addList")

    def clearTable(self):
        """ Очистка верхних кнопок таблицы для некоторых форм """
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
        endTime = int( time.strftime("%H", time.localtime()) ) * 3600 + \
                  int( time.strftime("%M", time.localtime()) ) * 60 + \
                  int( time.strftime("%S", time.localtime()) )
        updated = (endTime - self.settings[2][6]) / 3600
        self.time2 = updated if updated >= 0 else (updated + 24)
        if self.settings[2][6] > 0:
            if ":" in self.timerText.text:
                mytime = ut.timeFloatToHHMM(self.time2)
                mytime2 = mytime[: mytime.index(":")]
                mytime3 = mytime[mytime.index(":") + 1:]
                mytime4 = f"{mytime2} {mytime3}"
                self.timerText.text = mytime4
            else: self.timerText.text = ut.timeFloatToHHMM(self.time2)
        else: self.timerText.text = ""
        self.timer.on() if self.timerText.text != "" else self.timer.off()

    def timerPressed(self, mode="press", instance=None):
        if mode == "press" and self.timer.text == icon("icon-play-circled-1"): # первоначальный лик
            self.popup("timerPressed", title=self.msg[40], message=self.msg[219], options=[self.button["yes"], self.button["no"]])

        else: # вызов с положительного ответа в диалоге
            if self.resources[0][1][2] == 0:
                self.popup(title=self.msg[247], message=self.msg[217])
                self.resources[0][1][2] = 1
                self.save()
            self.updateTimer()
            result = self.rep.toggleTimer()
            if result == 1:
                self.rep.modify(")") # кредит выключен, записываем время служения сразу
                if self.displayed.form == "rep":
                    self.repPressed()
            elif result == 2: # кредит включен, сначала спрашиваем, что записать
                self.popup("timerType", title=self.msg[40], message=self.msg[41], options=[self.msg[42], self.msg[43]])

    # Действия главных кнопок positive, neutral

    def navPressed(self, instance=None):
        """ Навигация до участка/контакта """
        dest = self.house.title if self.house.type == "condo" else f"{self.house.title} {self.porch.title}"
        if "virtual" in dest: dest = dest.replace("virtual", "")

        """try:# попытка реализовать через plyer, пока не работает
            from plyer import maps
            maps.search(dest)
            #maps.route("Пушкина 32", self.house.title)
        except:
            #webbrowser.open(f"https://www.google.com/maps/place/{dest}")
            #webbrowser.open(f"https://yandex.ru/maps/?mode=search&text={dest}")            
        return"""

        try:
            if self.settings[0][21] == "Yandex" or self.settings[0][21] == "Яндекс":
                address = f"yandexmaps://maps.yandex.ru/maps/?mode=search&text={dest}"
            elif self.settings[0][21] == "2GIS" or self.settings[0][21] == "2ГИС":
                address = f"dgis://2gis.ru/search/{dest}"
            elif self.settings[0][21] == "Google":
                address = f"google.navigation:q={dest}"
            else:
                address = f"geo:0,0?q={dest}"

            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(address))
            mActivity.startActivity(intent)

        except:
            if self.settings[0][21] == "Yandex" or self.settings[0][21] == "Яндекс":
                webbrowser.open(f"https://yandex.ru/maps/?mode=search&text={dest}")
            elif self.settings[0][21] == "2GIS" or self.settings[0][21] == "2ГИС":
                webbrowser.open(f"https://2gis.ru/search/{dest}")
            else:#elif self.settings[0][21] == "Google":
                webbrowser.open(f"http://maps.google.com/?q={dest}")

    def positivePressed(self, instance=None, value=None, default=""):
        """ Что выполняет центральная кнопка в зависимости от экрана """
        self.showSlider = False
        self.sliderToggle()

        # Поиск

        def __press(*args):
            if self.msg[146] in self.pageTitle.text:
                input = self.inputBoxEntry.text.lower().strip()

                if input == "report000":
                    self.rep.checkNewMonth(forceDebug=True)

                elif input == "file000":
                    def __handleSelection(selection):
                        if len(selection) > 0:
                            file = selection[0]
                            self.pageTitle.text = file
                            self.importDB(file=file)
                    plyer.filechooser.open_file(on_selection=__handleSelection)

                elif input == "export000":
                    self.share(email=True) if not self.desktop else self.share(file=True)

                elif input == "clone000":
                    self.flat.clone(title=self.house.title, toStandalone=True)

                elif input != "":
                    self.searchQuery = input
                    self.find(instance=instance)

            elif self.msg[84] in self.positive.text: # Новый поиск
                self.searchPressed()

            # Отчет

            elif self.displayed.form == "rep":
                self.save()
                time.sleep(self.backupTimeoutBeforeDelete)
                self.rep.checkNewMonth()
                if self.reportPanel.current_tab.text == self.monthName()[0]:
                    success = 1
                    change = 0
                    try:
                        temp = ut.timeHHMMToFloat(self.hours.get().strip())
                        if temp == None: # если конвертация не удалась, создаем ошибку
                            5/0
                    except: success = 0
                    else:
                        if temp != self.rep.hours and self.counterTimeChanged: change = 1
                        temp_hours = temp

                    try:
                        if self.settings[0][2]==1:
                            temp = ut.timeHHMMToFloat(self.credit.get().strip())
                            if temp == None: 5/0
                        else: temp = 0
                    except: success = 0
                    else:
                        if self.settings[0][2] == 1:
                            if temp != self.rep.credit and self.counterTimeChanged: change = 1
                            temp_credit = temp

                    try: temp = int(self.studies.get().strip())
                    except: success = 0
                    else:
                        if temp != self.rep.studies: change = 1
                        temp_studies = temp

                    if success == 0: self.popup(message=self.msg[46])

                    elif success and change and self.counterChanged:
                        self.rep.hours = temp_hours
                        self.rep.studies = temp_studies
                        if self.settings[0][2] == 1:
                            self.rep.credit = temp_credit
                            credit = f"{self.msg[47]}, " % ut.timeFloatToHHMM(self.rep.credit)
                        else:
                            credit = ""
                        self.rep.saveReport(
                            message=self.msg[48] % (
                                ut.timeFloatToHHMM(self.rep.hours),
                                credit,
                                self.rep.studies
                            )
                        )
                        self.pageTitle.text = f"[b][ref=report]{self.msg[4]}{self.rep.getCurrentHours()[2]}[/ref][/b]"
                        if self.settings[0][2] == 1:
                            self.creditLabel.text = self.msg[105] % self.rep.getCurrentHours()[0]

                    self.counterChanged = self.counterTimeChanged = False

                elif self.reportPanel.current_tab.text == self.msg[49]: self.recalcServiceYear(allowSave=True)

                else: self.editLastMonthReport(value=0)

            elif self.button["top"] in self.positive.text and len(self.btn) > 0:
                self.scroll.scroll_to(widget=self.btn[0], padding=0, animate=False)

            # Настройки

            elif self.displayed.form == "set":
                self.save()
                time.sleep(self.backupTimeoutBeforeDelete)
                self.saveSettings()

            # Форма создания квартир/домов

            elif self.displayed.form == "porchView":
                self.save()
                time.sleep(self.backupTimeoutBeforeDelete)
                self.clearTable()
                self.displayed.form = "createNewFlat"
                self.positive.text = self.button["save"]
                self.sortButton.text = f"{self.button['list']} {self.msg[191]}"
                self.sortButton.disabled = False

                if self.house.type == "condo": # многоквартирный дом
                    if len(self.porch.flats) > 0: self.stack.insert(0, self.stack[0])
                    self.mainList.clear_widgets()
                    grid = GridLayout(rows=3, cols=2, col_force_default = True, padding=self.padding, # основная сетка
                                      size_hint_y = .4 if self.orientation=="v" else .6)
                    if self.orientation=="v": # ширина колонок основной таблицы
                        grid.cols_minimum = {0: self.mainList.size[0] * .4, 1: self.mainList.size[0] * .55}
                    else:
                        grid.cols_minimum = {0: self.mainList.size[0]*self.SR * .3, 1: self.mainList.size[0]*self.SR * .4}
                        grid.pos_hint={"center_x": .65}
                    align = "center"
                    if self.porch.alpha: self.mainList.add_widget(self.tip(icon="warn", hint_y=.08, text=self.msg[326]))
                    if len(self.porch.flats)==0: # определяем номер первой и последней квартир, сначала если это первый подъезд:
                        if len(self.house.porches)==1: # если это первый подъезд дома, пытаемся загрузить параметры из настроек:
                            try: # попытка загрузить первичные параметры этажей из настроек
                                firstflat, lastflat, floors = self.settings[0][9]
                            except:
                                firstflat, lastflat, floors = "1", "20", "5"
                        else:
                            firstflat, lastflat, floors = "1", "20", "5"
                        if self.selectedPorch > 0:
                            prevFirst, prevLast, floors = self.house.porches[self.selectedPorch - 1].getFirstAndLastNumbers()
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
                    self.floors = Counter(text=floors if not self.porch.alpha else "",
                                          disabled=False if not self.porch.alpha else True)
                    grid.add_widget(self.floors)
                    grid.add_widget(MyLabel(text=f"{self.msg[62]}\n{self.msg[63]}", halign=align, valign=align)) # 1-й этаж
                    self.floor1 = Counter(text=str(self.porch.floor1) if not self.porch.alpha else "", mode="pan",
                                          disabled=False if not self.porch.alpha else True)
                    grid.add_widget(self.floor1)
                    self.mainList.add_widget(grid)
                    def __linkPressed(instance, *args):
                        self.buttonFlash(instance)
                        self.popup("addList")
                    self.mainList.add_widget(self.tip(icon="link", text=self.msg[325], hint_y=.09, func=__linkPressed))
                    if len(self.porch.flats) == 0:
                        self.mainList.add_widget(self.tip(text=self.msg[312] % f"[b]{self.msg[5]}[/b]", hint_y=.09))
                    else:
                        self.mainList.add_widget(self.tip(text=self.msg[311]+"\n", hint_y=.09))

                else: # универсальный участок
                    self.createInputBox(
                        title=None,# не меняется
                        message=self.msg[64],
                        checkbox=self.msg[65],
                        active=False,
                        positive=self.button["add"],
                        hint=self.msg[66],
                        tip=""
                    )

            # Формы добавления

            elif self.displayed.form == "ter": # добавление участка
                self.detailsButton.disabled = True
                self.displayed.form = "createNewHouse"
                if self.language == "ru" or self.language == "uk":
                    active = True
                    hint = self.msg[70]
                    self.ruTerHint = " / У1"
                    ruList = " Снимите галочку, если участок другого типа или нужно ввести произвольный список адресов (в одном доме или разных)." \
                        if self.language == "ru" else ""
                else:
                    active = False
                    hint = self.msg[166]
                    self.ruTerHint = ""
                    ruList = ""
                self.createInputBox(
                    title=self.msg[67],
                    checkbox=self.msg[68],
                    active=active,
                    message=self.msg[165],
                    default=default,
                    sort="",
                    hint=hint,
                    limit=self.charLimit,
                    tip=self.msg[71] + ruList
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
                    title=f"{self.house.title} {self.button['arrow']} {self.msg[78].lower()} {self.house.getPorchType()[1]}",
                    message=message,
                    hint=hint,
                    limit=self.charLimit,
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
                    limit=self.charLimit,
                    tip=self.msg[81]
                )

            elif self.displayed.form == "flatView": # добавление посещения
                if len(self.flat.records) > 0:
                    self.displayed.form = "createNewRecord" # добавление нового посещения в существующем контакте
                    self.createInputBox(
                        title=f"{self.flatTitle} {self.button['arrow']} {self.msg[161].lower()}",
                        message=self.msg[83],
                        multiline=True,
                        details=self.button["cog"] + self.flatType,
                        neutral=self.button["phone"]
                    )
                else: # сохранение первого посещения и выход в подъезд
                    newName = self.multipleBoxEntries[0].text.strip()
                    if newName != "" or self.house.type != "virtual":
                        self.flat.updateName(newName)
                    if self.multipleBoxEntries[1].text.strip() != "":
                        self.flat.addRecord(self.multipleBoxEntries[1].text.strip())
                    self.flat.updateStatus()
                    if self.contactsEntryPoint: self.conPressed()
                    elif self.searchEntryPoint: self.find()
                    else: self.porchView()
                    for entry in self.multipleBoxEntries: entry.text = ""
                    self.save()

            elif self.displayed.form == "createNewRecord": # добавление новой записи посещения (повторное)
                self.displayed.form = "flatView"
                record = self.inputBoxEntry.text.strip()
                self.flat.addRecord(record)
                self.save()
                self.flatView()

            # Формы сохранения

            elif self.displayed.form == "createNewHouse":  # сохранение нового участка
                self.displayed.form = "ter"
                newTer = self.inputBoxEntry.text.strip()
                condo = self.checkbox.active
                if newTer == "": newTer = f"{self.msg[137]} {len(self.houses)+1}"
                if self.language == "ka": self.addHouse(self.houses, newTer, condo, forceUpper=False)
                else: self.addHouse(self.houses, newTer, condo, forceUpper=True)
                self.save()
                self.terPressed()

            elif self.displayed.form == "createNewPorch": # сохранение нового подъезда
                self.displayed.form = "houseView"
                newPorch = self.inputBoxEntry.text.strip()
                if newPorch == "": newPorch = str(len(self.house.porches)+1)
                self.house.addPorch(newPorch, self.house.getPorchType()[0])
                self.save()
                self.houseView()

            elif self.displayed.form == "createNewFlat": # сохранение новых квартир
                self.displayed.form = "porchView"
                if self.house.type == "condo": # многоквартирный подъезд
                    try:
                        start = int(self.flatRangeStart.text.strip())
                        finish = int(self.flatRangeEnd.text.strip())
                        floors = int(self.floors.get()) if not self.porch.alpha else 1
                        f1 = int(self.floor1.get()) if not self.porch.alpha else 1
                        if start > finish or floors < 1: 5 / 0 # создаем ошибку
                    except:
                        self.popup(message = self.msg[88])
                        self.positivePressed()
                    else:
                        self.porch.deleteHiddenFlats()
                        numbers = []
                        alNumbers = []
                        for flat in self.porch.flats:
                            if not flat.number.isnumeric(): # проверяем на наличие букв в номерах
                                alNumbers.append(flat.number)
                            elif int(flat.number) < int(start): numbers.append(flat.number)
                        for number in numbers: # удаляем квартиры до и после заданного диапазона
                            for i in range(len(self.porch.flats)):
                                if self.porch.flats[i].number == number:
                                    del self.porch.flats[i]
                                    break
                        del numbers[:]
                        for flat in self.porch.flats:
                            if not flat.number.isnumeric(): continue
                            elif int(flat.number) > int(finish): numbers.append(flat.number)
                        for number in numbers:
                            for i in range(len(self.porch.flats)):
                                if self.porch.flats[i].number == number:
                                    del self.porch.flats[i]
                                    break
                        self.porch.addFlats("%d-%d[%d" % (start, finish, floors))
                        if len(alNumbers) == 0:
                            self.porch.flatsLayout = str(floors)
                        self.porch.floor1 = f1
                        if len(self.house.porches) == 1:  # если это первое создание квартир в доме, выгружаем параметры в настройку
                            self.settings[0][9] = start, finish, floors
                        self.save()
                    self.porchView()

                else: # сохранение домов в сегменте универсального участка
                    addFlat = self.inputBoxEntry.text.strip()
                    if not self.checkbox.active:
                        if not "." in addFlat and not "," in addFlat:
                            self.porch.addFlat(addFlat)
                            self.save()
                            self.porchView()
                        else:
                            self.popup(message=self.msg[89])
                            self.porchView()
                            self.positivePressed()
                    else:
                        addFlat2 = self.inputBoxEntry2.text.strip()
                        try:
                            if int(addFlat) > int(addFlat2): 5/0
                            self.porch.addFlats("%d-%d" % (int(addFlat), int(addFlat2)))
                        except:
                            self.popup(message=self.msg[90])
                            def __repeat(*args):
                                self.porchView()
                                self.positivePressed()
                                self.checkbox.active = True
                            Clock.schedule_once(__repeat, 0.5)
                        else:
                            self.porchView()
                            self.save()
                    if 0:#len(self.btn) >= self.listOnScreenLimit:
                        last = len(self.btn)-1
                        self.scroll.scroll_to(widget=self.btn[last], padding=0, animate=False)
                        self.clickedBtnIndex = last

            elif self.displayed.form == "recordView": # сохранение уже существующей записи посещения
                self.displayed.form = "flatView"
                self.flat.editRecord(self.selectedRecord, self.inputBoxEntry.text.strip())
                self.save()
                self.flatView()

            elif self.displayed.form == "createNewCon": # сохранение нового контакта
                self.displayed.form = "con"
                name = self.inputBoxEntry.text.strip()
                if name == "": name = f"{self.msg[158]} {len(self.resources[1])+1}"
                self.addHouse(self.resources[1], "", "virtual")  # создается новый виртуальный дом
                self.resources[1][len(self.resources[1]) - 1].addPorch(input="", type="virtual")
                self.resources[1][len(self.resources[1]) - 1].porches[0].addFlat(name, virtual=True)
                self.resources[1][len(self.resources[1]) - 1].porches[0].flats[0].status = "1"
                self.save()
                self.conPressed()

            # Детали

            elif self.displayed.form == "houseDetails": # детали участка
                self.displayed.form = "houseView"
                self.house.note = self.multipleBoxEntries[2].text.strip()
                if self.language == "ka": # для грузинского без заглавных букв
                    newTitle = self.multipleBoxEntries[0].text.strip()  # попытка изменить адрес - сначала проверяем, что нет дублей
                else:
                    newTitle = self.multipleBoxEntries[0].text.upper().strip()
                if newTitle == "": newTitle = self.house.title
                self.house.title = newTitle
                self.save()
                self.houseView()
                newDate = self.multipleBoxEntries[1].text.strip()
                if ut.checkDate(newDate):
                    self.house.date = newDate
                    self.save()
                    self.houseView()
                else:
                    self.detailsPressed()
                    self.popup(message=self.msg[92])
                    return

            elif self.displayed.form == "porchDetails": # детали подъезда
                self.displayed.form = "porchView"
                self.porch.note = self.multipleBoxEntries[1].text.strip()
                newTitle = self.multipleBoxEntries[0].text.strip() # попытка изменить название подъезда - сначала проверяем, что нет дублей
                if newTitle == "": newTitle = self.porch.title
                self.porch.title = newTitle
                self.save()
                self.porchView()

            elif self.displayed.form == "flatDetails": # детали квартиры/контакта
                success = True
                allow = True
                self.displayed.form = "flatView"
                newName = self.multipleBoxEntries[0].text.strip() # имя
                if newName != "" or self.house.type != "virtual": self.flat.updateName(newName)
                self.flat.editPhone(self.multipleBoxEntries[1].text) # телефон
                if self.house.type == "virtual": # адрес
                    if self.language == "ka": # для грузинского без заглавных букв
                        self.house.title = self.multipleBoxEntries[2].text.strip()
                    else:
                        self.house.title = self.multipleBoxEntries[2].text.upper().strip()
                self.porch.title = self.multipleBoxEntries[3].text.strip() # подъезд
                if self.house.type == "virtual":
                    newNumber = self.multipleBoxEntries[4].text.strip() # номер/адрес
                elif len(self.multipleBoxEntries[4].text) > 0 and self.multipleBoxEntries[4].text.strip()[0] != "0" and self.multipleBoxEntries[4].text.strip()[0] != "-"\
                        and self.multipleBoxEntries[4].text.strip()[0] != "+" and self.multipleBoxEntries[4].text.strip()[0] != ".":
                    newNumber = self.multipleBoxEntries[4].text.strip()
                else:
                    self.detailsPressed()
                    return
                self.flat.editNote(self.multipleBoxEntries[5].text)  # заметка
                if self.house.type == "condo": # в подъезде проверяем, чтобы не было дублей номеров
                    for i in range(len(self.porch.flats)):
                        if self.porch.flats[i].number == newNumber and i != self.selectedFlat:
                            allow = False
                            break
                if allow:
                    self.flat.updateTitle(newNumber)
                    if self.porch.floors():
                        self.porch.sortFlats()
                        if self.porch.alpha: self.porch.flatsLayout = "н"
                        self.porch.sortFlats()
                else:
                    success = False
                    self.detailsPressed()
                    self.multipleBoxEntries[4].text = newNumber
                    self.popup(message=self.msg[93]) # такой номер уже существует
                if success:
                    self.save()
                    if not self.popupEntryPoint:
                        self.flatView()
                    else:
                        self.popupEntryPoint = 0
                        self.porchView(sortFlats=True,# if allow and self.porch.floors() else False,
                                       scroll_to=False if allow and self.porch.floors() else 0)

        Clock.schedule_once(__press, 0)

    def neutralPressed(self, instance=None, value=None):
        self.showSlider = False
        self.sliderToggle()
        if self.displayed.form == "porchView":
            if self.resources[0][1][3] == 0:
                self.popup(title=self.msg[247], message=self.msg[171])
                self.resources[0][1][3] = 1
                self.save()
            if self.porch.floors():
                if self.porch.flatsNonFloorLayoutTemp != None:
                    self.porch.flatsLayout = self.porch.flatsNonFloorLayoutTemp
                else: self.porch.flatsLayout = "н"
            else:
                if not self.porch.alpha: self.porch.flatsLayout = self.porch.type[7:] # определение этажей по цифре в типе подъезда
                if self.porch.flatsLayout == "" or self.porch.alpha: self.popup(message=self.msg[94] % self.msg[155])
            self.save()
            self.porchView(sortFlats=True)

        elif self.button["phone"] in instance.text:
            if platform == "android": request_permissions([Permission.CALL_PHONE])
            try: plyer.call.makecall(tel=self.flat.phone)
            except:
                if self.desktop and self.flat.phone.strip() != "":
                    Clipboard.copy(self.flat.phone)
                    self.popup(message=self.msg[28] % self.flat.phone)

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
        elif self.displayed.form == "ter" or "view" in self.displayed.form.lower():
            self.buttonTer.activate()
            self.buttonCon.deactivate()
            self.buttonRep.deactivate()
        else:
            self.buttonRep.deactivate()
            self.buttonTer.deactivate()
            self.buttonCon.deactivate()

    # Действия других кнопок

    def terPressed(self, instance=""):
        self.func = self.terPressed
        if self.confirmNonSave(): return
        self.buttonTer.activate()
        self.contactsEntryPoint = 0
        self.searchEntryPoint = 0

        if self.settings[0][19] == "д":  # first sort - by date
            self.houses.sort(key=lambda x: x.date, reverse=False)
        elif self.settings[0][19] == "р":  # by size
            for i in range(len(self.houses)):
                self.houses[i].size = self.houses[i].getHouseStats()[3]
            self.houses.sort(key=lambda x: x.size, reverse=True)
        elif self.settings[0][19] == "н":  # alphabetic by title
            self.houses.sort(key=lambda x: x.title, reverse=False)
        elif self.settings[0][19] == "и":  # by number of interested persons
            for i in range(len(self.houses)):
                self.houses[i].interest = self.houses[i].getHouseStats()[1]
            self.houses.sort(key=lambda x: x.interest, reverse=True)
        elif self.settings[0][19] == "п":  # by progress
            for i in range(len(self.houses)):
                self.houses[i].progress = self.houses[i].getHouseStats()[2]
            self.houses.sort(key=lambda x: x.progress, reverse=False)
        elif self.settings[0][19] == "о":  # by progress reversed
            for i in range(len(self.houses)):
                self.houses[i].progress = self.houses[i].getHouseStats()[2]
            self.houses.sort(key=lambda x: x.progress, reverse=True)

        housesList = []
        footer = []
        for i in range(len(self.houses)):  # check houses statistics
            stats = self.houses[i].getHouseStats()
            due = self.houses[i].due()
            listIcon = self.button['building'] if self.houses[i].type == "condo" else self.button['map']
            housesList.append(f"{listIcon} [b]{self.houses[i].title}[/b]")
            shortenedDate = ut.shortenDate(self.houses[i].date)
            dateDue = "" if not due else f"[color=F4CA16] {self.button['warn']}[/color]"
            interested = f"[b]{(stats[1])}[/b]" if int(stats[1]) > 0 else str((int(stats[1])))
            intIcon = self.button['user'] if int(stats[1]) != 0 else icon("icon-user-o")
            footer.append([
                f"{icon('icon-home-1')} {stats[3]}", # кол-во квартир
                f"[color={self.interestColor}]{intIcon} {interested}[/color]",# интересующиеся
                f"{self.button['calendar']} {str(shortenedDate)}{dateDue}",  # дата
                f"{self.button['worked']} {int(stats[2] * 100)}%", # обработка
                ])
            if self.fontScale() <= 1:
                footer[i].insert(0, "")
                footer[i].append("")
            if self.resources[0][1][6] == 0 and int(stats[2] * 100) > 0:
                self.popup(title=self.msg[247], message=self.msg[13])
                self.resources[0][1][6] = 1
                self.save()
        buildingIcon = self.button['building'] if RM.language == "ru" or RM.language == "uk" else self.button['map']
        housesList.append(f"{self.button['plus-1']}{buildingIcon} {self.msg[95]}") if len(housesList) == 0 else None
        self.displayed.update( # display list of houses and options
            title=f"[b]{self.msg[2]} ({len(self.houses)})[/b]",
            message=self.msg[97],
            options=housesList,
            footer=footer,
            form="ter",
            sort=self.button['sort'],
            positive=f"{self.button['plus']} {self.msg[98]}",
            back=False
        )
        if instance != None: self.stack.insert(0, self.displayed.form)
        self.updateList()
        self.updateMainMenuButtons()

    def conPressed(self, instance=None):
        if instance != None:
            self.func = self.conPressed
            if self.confirmNonSave(): return
        self.buttonCon.activate()
        self.contactsEntryPoint = 1
        self.searchEntryPoint = 0
        self.showSlider = False
        self.sliderToggle()
        self.allcontacts = self.getContacts()
        options = []
        footer = []

        # Sort
        if self.settings[0][4] == "и":     self.allcontacts.sort(key=lambda x: x[0]) # by name
        elif self.settings[0][4] == "а":   self.allcontacts.sort(key=lambda x: x[2]) # by address
        elif self.settings[0][4] == "д":   self.allcontacts.sort(key=lambda x: x[5]) # by date

        for i in range(len(self.allcontacts)):
            if self.allcontacts[i][3] == "virtual": self.allcontacts[i][3] = ""
            if self.allcontacts[i][15] != "condo" and self.allcontacts[i][15] != "virtual":
                porch = f"{self.allcontacts[i][12]}, " if self.allcontacts[i][14] else ""
                gap = ", "
            else: porch = gap = ""
            hyphen = "–" if "подъезд" in self.allcontacts[i][8] else ""
            address = f" {self.allcontacts[i][2]}{gap}{porch}{hyphen}{self.allcontacts[i][3]}"\
                if self.allcontacts[i][2] != "" else ""
            #phone = f" {self.allcontacts[i][9]}" if self.allcontacts[i][9] != "" else ""
            #date = f"{self.button['chat']} {self.allcontacts[i][4]}"
            listIcon = f"[color={get_hex_from_color(self.getColorForStatus('1'))}]{self.button['user']}[/color]"
            options.append(f"{self.allcontacts[i][1]}{listIcon} [b]{self.allcontacts[i][0]}[/b]")
            footer.append([
                f"{self.button['chat']} {self.allcontacts[i][4]}" if self.allcontacts[i][4] != None else "",
                "" if address=="" else f"{icon('icon-home-1')} {address}",
                ##"" if phone=="" else f"{icon('icon-phone-1')} {phone}"
            ])

        self.displayed.update(
            form="con",
            title=f"[b]{self.msg[3]} ({len(self.allcontacts)})[b]",
            message=self.msg[96],
            options=options,
            footer=footer,
            sort=self.button['sort'],
            positive=f"{self.button['plus']} {self.msg[100]}",
            back=False,
            tip=self.msg[99] % self.msg[100] if len(options) == 0 else None
        )
        if instance != None: self.stack.insert(0, self.displayed.form)
        self.updateList()

        if len(options) >= self.listOnScreenLimit: # пытаемся всегда вернуться на последний контакт
            index = self.clickedBtnIndex + 1
            if index == len(self.btn): index -= 1
            try: self.scroll.scroll_to(widget=self.btn[index], padding=0, animate=False)
            except: pass

        self.updateMainMenuButtons()

    def repPressed(self, instance=None, jumpToPrevMonth=False):
        self.func = self.repPressed
        if self.confirmNonSave(): return
        self.buttonRep.activate()
        if len(self.stack) > 0: self.stack.insert(0, self.stack[0]) # дублирование последнего шага стека, чтобы предотвратить уход со страницы
        self.clearTable()
        self.counterChanged = False
        self.counterTimeChanged = False
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
        self.pageTitle.text = f"[b][ref=report]{self.msg[4]}{self.rep.getCurrentHours()[2]}[/ref][/b]"

        self.reportPanel = TabbedPanel(background_color=self.globalBGColor, background_image="")
        self.mainList.clear_widgets()

        # Первая вкладка: отчет прошлого месяца

        tab2 = TTab(text=self.monthName()[2])
        report2 = AnchorLayout(anchor_x="center", anchor_y="center")
        hint = "" if self.rep.lastMonth != "" else self.msg[111]
        box = BoxLayout(orientation="vertical", size_hint=(None, None), width=self.standardTextHeight*8,
                        height=self.standardTextHeight*6)
        self.repBox = MyTextInput(text=self.rep.lastMonth, hint_text=hint, multiline=True, specialFont=True)
        self.repBox.bind(focus=self.editLastMonthReport)
        btnSend = TableButton(text=f"\n{self.button['share']} {self.msg[110]}", size_hint_x=1, size_hint_y=None,
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
        text_size = [(Window.size[0] * .4) * self.SR, None]
        g = GridLayout(rows=3, cols=1)

        levelsSizeY = [ # доли трех секций экрана по высоте
            .32 if not self.settings[0][2] else .2,
            .46 if not self.settings[0][2] else .68,
            .22 if not self.settings[0][2] else .12
        ]

        sendBox = AnchorLayout(anchor_x="center", anchor_y="center", pos_hint={"center_x": .5}, # секция с кнопкой отправки
                               size_hint=(1, levelsSizeY[0]))
        send = RButton(text=f"{self.button['share']} {self.msg[110]}", size_hint_y=None,
                       size_hint_x=.4 if self.orientation == "v" else .2, radiusK=self.standardRButtonRadius,
                       size=(0, self.standardTextHeightUncorrected * 1.3), pos_hint={"center_x": .5})
        def __sendCurrentMonthReport(*args):
            plyer.email.send(subject=self.msg[4], text=self.rep.getCurrentMonthReport(), create_chooser=True)
        send.bind(on_release=__sendCurrentMonthReport)
        sendBox.add_widget(send)
        g.add_widget(sendBox)

        a = AnchorLayout(anchor_x="center", anchor_y="center", # основная секция отчета
                         size_hint_y = levelsSizeY[1])
        report = GridLayout(cols=2, rows=4, spacing=self.spacing)
        if self.orientation == "h":
            report.size_hint_x = .6
            text_size[0] *= .7
        report.add_widget(MyLabel(text=self.msg[104], halign="center", valign="center", text_size = text_size,
                                  color=self.standardTextColor, markup=True))
        self.hours = Counter(picker=self.msg[108], type="time", text=ut.timeFloatToHHMM(self.rep.hours))
        report.add_widget(self.hours)
        if self.settings[0][2]==1:
            self.creditLabel = MyLabel(text=self.msg[105] % self.rep.getCurrentHours()[0], markup=True,
                                       halign="center", valign="center", text_size = text_size, color=self.standardTextColor)
            report.add_widget(self.creditLabel)
            self.credit = Counter(picker=self.msg[109], type="time",
                                  text=ut.timeFloatToHHMM(self.rep.credit), mode="pan")
            report.add_widget(self.credit)
        report.add_widget(MyLabel(text=self.msg[103], halign="center", valign="center", text_size = text_size,
                                  color=self.standardTextColor, markup=True))
        self.studies = Counter(text = str(self.rep.studies), mode="pan")
        report.add_widget(self.studies)
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
                text = str(self.settings[4][i]) if self.settings[4][i] != None else ""
                mode = "" if i<6 else "pan"
                monthAmount = MyTextInput(text=text, multiline=False, input_type="number", width=self.standardTextWidth * 1.1,
                                          font_size=self.fontXS*self.fontScale() if not self.desktop else Window.size[1]/45,
                                          font_size_force=True, halign="center", valign="center", mode=mode,
                                          size_hint_x=None, size_hint_y=1, height=height)
                self.months.append(monthAmount)
                mGrid.add_widget(self.months[i])
                self.analyticsMessage = MyLabel(markup=True, color=self.standardTextColor, valign="center",
                                              text_size=(Window.size[0]*self.SR / 2, self.mainList.size[1]),
                                              height=self.mainList.size[1],
                                              width=Window.size[0]*self.SR / 2, pos_hint={"center_y": .5})
                self.months[i].bind(focus=self.recalcServiceYear)

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

    def settingsPressed(self, instance=None):
        """ Настройки """
        self.func = self.settingsPressed
        if self.confirmNonSave(): return
        self.displayed.form = "set"
        self.updateMainMenuButtons(deactivateAll=True)
        self.clearTable()
        self.mainList.clear_widgets()
        box = BoxLayout(orientation="vertical")
        self.settingsPanel = TabbedPanel(background_color=self.globalBGColor, background_image="")
        self.createMultipleInputBox(
            form=box,
            title="",
            options=[
                self.msg[124], # норма часов
                "{}" + self.msg[40],  # таймер
                "{}" + self.msg[130],  # уведомление при таймере
                "{}" + self.msg[125] % self.msg[206], # нет дома {} = вместо строки ввода должна быть галочка
                "<>" + self.msg[127], # выбор цвета отказа
                "{}" + self.msg[128], # кредит часов
                "{}" + self.msg[129], # быстрый ввод телефона
                "{}" + (self.msg[86] if not self.desktop else self.msg[164]), # новое предложение с заглавной / запоминать положение окна
               f"[]{icon('icon-language')} {self.msg[131]}", # язык () = togglebutton
                "[]" + self.msg[315], # карты ()
                "[]" + self.msg[168]  # тема ()
            ],
            defaults=[
                self.settings[0][3],   # норма часов
                self.settings[0][22],  # таймер
                self.settings[0][0],   # уведомление при запуске таймера
                self.settings[0][13],  # нет дома
                self.settings[0][18],  # цвет отказа
                self.settings[0][2],   # кредит часов
                self.settings[0][20],  # показывать телефон
                self.settings[0][11] if not self.desktop else self.settings[0][12], # новое предложение с заглавной / запоминать положение окна
                self.settings[0][6],   # язык
                self.settings[0][21],  # карты
                self.settings[0][5],   # тема
            ],
            multilines=[False, False, False, False, False, False, False, False, False, False, False]
        )

        """ Также заняты настройки:
        self.settings[0][1] - позиция подъезда в окне
        self.settings[0][4] - сортировка контактов
        self.settings[0][5] - тема интерфейса
        self.settings[0][7] - масштабирование подъезда
        self.settings[0][8] - значение слайдера
        self.settings[0][9] - значения первой и последней квартиры и количества этажей в новом подъезде
        self.settings[0][21] - карты
        self.settings[0][22] - таймер                
        """

        # Первая вкладка: настройки

        tab1 = TTab(text=self.msg[52])
        tab1.content = box
        self.settingsPanel.add_widget(tab1)

        # Вторая вкладка: работа с данными

        tab2 = TTab(text=self.msg[54])
        g = GridLayout(rows=4, cols=2, spacing=self.spacing*4, padding=self.padding*2)
        radiusK = .2
        ratioV = .55 if self.orientation == "v" else .75
        ratioH = .45 if self.orientation == "v" else .25
        g.cols_minimum = {0: (self.mainList.size[0]*self.SR-self.padding*4-self.spacing*4)*ratioV,
                          1: (self.mainList.size[0]*self.SR-self.padding*4-self.spacing*4)*ratioH}
        text_size = [g.cols_minimum[0]-self.padding*3, None]

        sp = self.spacing*3
        exportBox = BoxLayout(orientation="vertical", spacing=sp)
        exportEmail = RButton(text = f"{self.button['export' if not self.desktop else 'floppy']} {self.msg[132]}",
                              size_hint_y=.5, radiusK=radiusK)

        def __export(instance):
            self.share(email=True) if not self.desktop else self.share(file=True)
        exportEmail.bind(on_release=__export)
        g.add_widget(MyLabel(text=self.msg[318] if not self.desktop else self.msg[322], text_size=text_size,
                             valign="top", font_size=self.fontS))
        exportBox.add_widget(Widget(size_hint_y=.25))
        exportBox.add_widget(exportEmail)
        exportBox.add_widget(Widget(size_hint_y=.25))
        g.add_widget(exportBox)

        importBtnDefaultText = f"{self.button['import']} {self.msg[133]}"
        importBtn = RButton(text=importBtnDefaultText, radiusK=radiusK,
                            size_hint_y=.5, text_size=[g.cols_minimum[1]-self.padding*3, None])
        importBox = BoxLayout(orientation="vertical", spacing=sp)#self.spacing*3)
        g.add_widget(MyLabel(text=self.msg[324], text_size=text_size, font_size=self.fontS))
        g.add_widget(importBox)
        if self.orientation == "v": importBox.add_widget(Widget(size_hint_y=.12))
        importBox.add_widget(importBtn)
        self.importEntry = MyTextInput(hint_text=self.msg[323], multiline=False, font_size=self.fontXXS,
                                       size_hint_y=.25 if self.orientation == "v" else .5,
                                       blockPositivePress=True, font_size_force=True, shrink=False)
        def __import(*args):
            def __do(*args):
                self.importDB(link=self.importEntry.text)
                importBtn.color = self.tableColor
                importBtn.text = importBtnDefaultText
            importBtn.color = self.titleColor if self.theme != "purple" else self.linkColor
            importBtn.text = f"{icon('icon-hourglass-3')} {self.msg[210]}"
            Clock.schedule_once(__do, .1)

        def __insertAndImport(*args):
            self.importEntry.text = Clipboard.paste().strip()
            Clock.schedule_once(__import, .1)
        importBtn.bind(on_release=__insertAndImport)
        self.importEntry.bind(on_text_validate=__import)
        importBox.add_widget(self.importEntry)
        if self.orientation == "v": importBox.add_widget(Widget(size_hint_y=.12))

        if self.desktop:
            g.rows += 1
            importFileBox = BoxLayout(orientation="vertical", spacing=sp)
            importFile = RButton(text=f"{self.button['open']} {self.msg[134]}", radiusK=radiusK, size_hint_y=.5)
            def __importFile(instance):
                from tkinter import filedialog
                file = filedialog.askopenfilename()
                if file != "": self.importDB(file=file)
            importFile.bind(on_release=__importFile)
            g.add_widget(MyLabel(text=self.msg[319], text_size=text_size, font_size=self.fontS))
            importFileBox.add_widget(Widget(size_hint_y=.25))
            importFileBox.add_widget(importFile)
            importFileBox.add_widget(Widget(size_hint_y=.25))
            g.add_widget(importFileBox)

        restoreBox = BoxLayout(orientation="vertical", spacing=sp)
        restoreBtn = RButton(text=f"{self.button['restore']} {self.msg[135]}", radiusK=radiusK, size_hint_y=.5)
        def __restore(instance):
            self.popup("restoreBackup")
        restoreBtn.bind(on_release=__restore)
        g.add_widget(MyLabel(text=self.msg[320], text_size=text_size, font_size=self.fontS))
        restoreBox.add_widget(Widget(size_hint_y=.25))
        restoreBox.add_widget(restoreBtn)
        restoreBox.add_widget(Widget(size_hint_y=.25))
        g.add_widget(restoreBox)

        clearBox = BoxLayout(orientation="vertical", spacing=sp)
        clearBtn = RButton(text=f"{self.button['wipe']} {self.msg[136]}", radiusK=radiusK, size_hint_y=.5)
        def __clear(instance):
            self.popup("clearData", message=self.msg[138], options=[self.button["yes"], self.button["no"]])
        clearBtn.bind(on_release=__clear)
        g.add_widget(MyLabel(text=self.msg[321], text_size=text_size, font_size=self.fontS))
        clearBox.add_widget(Widget(size_hint_y=.25))
        clearBox.add_widget(clearBtn)
        clearBox.add_widget(Widget(size_hint_y=.25))
        g.add_widget(clearBox)

        tab2.content = g
        self.settingsPanel.add_widget(tab2)

        # Третья вкладка: блокнот

        tab4 = TTab(text=self.msg[55])
        a4 = AnchorLayout(anchor_x="center", anchor_y="center")

        self.backButton.disabled = False
        self.showSlider = False
        self.detailsButton.text = ""
        self.detailsButton.disabled = True
        self.sliderToggle()
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
        aboutBtn = MyLabel(text=
                           f"[color={self.titleColor2}][b]Rocket Ministry {Version}[/b][/color]\n\n" + \
                           f"{self.msg[140]}\n\n" + \
                           f"{self.msg[141]}\n[ref=web][color={linkColor}]{icon('icon-github')} [u]Github[/u][/color][/ref]\n\n" + \
                           f"{self.msg[142]}\n[ref=email][color={linkColor}]{icon('icon-mail-alt')} [u]inoblogger@gmail.com[/u][/color][/ref]\n\n",
                           markup=True, halign="left", valign="center", color=self.standardTextColor,
                           text_size=[self.mainList.size[0] * .8, None]
        )

        def __click(instance, value):
            if value == "web":
                if self.language == "ru":   webbrowser.open("https://github.com/antorix/Rocket-Ministry/wiki/ru")
                else:                       webbrowser.open("https://github.com/antorix/Rocket-Ministry/")
            elif value == "email":          webbrowser.open("mailto:inoblogger@gmail.com?subject=Rocket Ministry")

        aboutBtn.bind(on_ref_press=__click)
        a.add_widget(aboutBtn)
        tab3.content = a
        self.settingsPanel.add_widget(tab3)
        self.settingsPanel.do_default_tab = False
        self.mainList.add_widget(self.settingsPanel)

    def saveSettings(self, clickOnSave=True):
        if self.settingsPanel.current_tab.text == self.msg[52]:
            if self.settings[0][7] == 1 and not self.multipleBoxEntries[6].active:
                self.slider.value = self.settings[0][8] = 1
                self.showSlider = False
            try:
                self.settings[0][3] = 0 if self.multipleBoxEntries[0].text.strip() == "" \
                    else int(self.multipleBoxEntries[0].text.strip())  # норма часов
            except: pass
            self.settings[0][22] = self.multipleBoxEntries[1].active  # таймер
            self.settings[0][0] = self.multipleBoxEntries[2].active  # уведомление при запуске таймера
            self.settings[0][13] = self.multipleBoxEntries[3].active  # нет дома
            self.settings[0][18] = self.multipleBoxEntries[4].get()  # цвет отказа
            self.settings[0][2] = self.multipleBoxEntries[5].active  # кредит
            self.settings[0][20] = self.multipleBoxEntries[6].active  # показывать телефон
            if not self.desktop:
                self.settings[0][11] = self.multipleBoxEntries[7].active  # новое предложение с заглавной
            else:
                self.settings[0][12] = self.multipleBoxEntries[7].active  # запоминать положение окна
            for i in range(len(self.languages)):  # язык
                if list(self.languages.values())[i][0] in self.languageButton.text:
                    self.settings[0][6] = list(self.languages.keys())[i]
                    break
            self.settings[0][21] = self.mapsButton.text # карты
            self.settings[0][5] = self.themes[self.themeButton.text]  # тема

            if self.settings[0][22] == 0:
                self.settings[2][6] = 0  # принудительно останавливаем таймер, если он отключен
                self.updateTimer()

            self.save()
            self.restart("soft")
            if clickOnSave: Clock.schedule_once(self.settingsPressed, .1)
            self.log(self.msg[53])

        elif self.settingsPanel.current_tab.text == self.msg[54]:
            self.save()
            self.log(self.msg[56])

        elif self.settingsPanel.current_tab.text == self.msg[55]:
            self.resources[0][0] = self.inputBoxEntry.text.strip()
            self.save()

    def searchPressed(self, instance=None):
        """ Нажата кнопка поиск """
        self.func = self.searchPressed
        if self.confirmNonSave(): return
        self.displayed.form = "search"
        self.clearTable()
        self.createInputBox(
            title=f"[b]{self.msg[146]}[/b]",
            message=self.msg[147],
            multiline=False,
            positive=f"{self.button['search2']} [b]{self.msg[148]}[/b]",
            details="",
            focus=True
        )
        self.updateMainMenuButtons(deactivateAll=True)

    def find(self, instance=None):
        self.contactsEntryPoint = 0
        allContacts = self.getContacts(forSearch=True)
        self.searchResults = []
        for i in range(len(allContacts)): # start search in flats/contacts
            found = False
            if self.searchQuery in allContacts[i][2].lower() or self.searchQuery in allContacts[i][2].lower() or self.searchQuery in \
                    allContacts[i][3].lower() or self.searchQuery in allContacts[i][8].lower() or self.searchQuery in \
                    allContacts[i][10].lower() or self.searchQuery in allContacts[i][11].lower() or self.searchQuery in \
                    allContacts[i][12].lower() or self.searchQuery in allContacts[i][13].lower() or\
                    self.searchQuery in allContacts[i][9].lower():
                found = True

            if allContacts[i][8] != "virtual":
                for r in range(len(self.houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[
                                       allContacts[i][7][2]].records)):  # in records in flats
                    if self.searchQuery in self.houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[
                        allContacts[i][7][2]].records[r].title.lower():
                        found = True
                    if self.searchQuery in self.houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[
                        allContacts[i][7][2]].records[r].date.lower():
                        found = True
            else:
                for r in range(len(self.resources[1][allContacts[i][7][0]].porches[0].flats[0].records)): # in records in contacts
                    if self.searchQuery in self.resources[1][allContacts[i][7][0]].porches[0].flats[0].records[
                        r].title.lower():
                        found = True
                    if self.searchQuery in self.resources[1][allContacts[i][7][0]].porches[0].flats[0].records[
                        r].date.lower():
                        found = True

            if found: self.searchResults.append([allContacts[i][7], allContacts[i][8], allContacts[i][2]])

        options = []
        for i in range(len(self.searchResults)):  # save results
            number = "%d) " % (i + 1)
            if self.searchResults[i][1] != "virtual":  # for regular flats
                if self.houses[self.searchResults[i][0][0]].getPorchType()[0] == "подъезд":
                    options.append(f"[b]%s%s-%s[/b]" % (number, self.houses[self.searchResults[i][0][0]].title,
                                             self.houses[self.searchResults[i][0][0]].porches[self.searchResults[i][0][1]].flats[
                                             self.searchResults[i][0][2]].title))
                else:
                    options.append(f"[b]%s%s, %s, %s[/b]" % (number,
                        self.houses[self.searchResults[i][0][0]].title,
                        self.houses[self.searchResults[i][0][0]].porches[self.searchResults[i][0][1]].title,
                        self.houses[self.searchResults[i][0][0]].porches[self.searchResults[i][0][1]].flats[self.searchResults[i][0][2]].title
                        ))

            else: # for standalone contacts
                title = "" if self.resources[1][self.searchResults[i][0][0]].title == "" else \
                    self.resources[1][self.searchResults[i][0][0]].title + ", "
                options.append(f"[b]%s%s%s[/b]" % (number, title,
                    self.resources[1][self.searchResults[i][0][0]].porches[0].flats[0].title))

        if len(options) == 0: options.append(self.msg[149])

        self.displayed.update(
            form="search",
            title=f"{self.msg[150]}" % self.searchQuery,
            message=self.msg[151],
            options=options,
            positive=f" {self.button['search2']} {self.msg[84]}"
        )
        if instance != None: self.stack.insert(0, self.displayed.form)
        self.updateList()

        if len(options) >= self.listOnScreenLimit: # пытаемся всегда вернуться в последний элемент поиска
            index = self.clickedBtnIndex + 1
            if index == len(self.btn): index -= 1
            try: self.scroll.scroll_to(widget=self.btn[index], padding=0, animate=False)
            except: pass

    # Функции по обработке участков

    def houseView(self, instance=None):
        """ Вид участка - список подъездов """
        if "virtual" in self.house.type: # страховка от захода в виртуальный дом
            if self.contactsEntryPoint: self.conPressed()
            elif self.searchEntryPoint: self.find(instance=instance)
            return
        self.updateMainMenuButtons()
        note = self.house.note if self.house.note != "" else None
        self.mainListsize1 = self.mainList.size[1]

        self.displayed.update(
            form="houseView",
            title=f"{self.house.title}",
            options=self.house.showPorches(),
            details=f"{self.button['cog']} {self.msg[137]}",
            positive=f"{self.button['plus']} {self.msg[78]} {self.house.getPorchType()[1]}",
            tip=[note, "note"]
        )
        if instance != None: self.stack.insert(0, self.displayed.form)
        self.updateList()
        if self.house.due(): self.mainList.add_widget(self.tip(text=self.msg[152], icon="warn"))

    def porchView(self, instance=None, sortFlats=True, scroll_to=None):
        """ Вид подъезда - список квартир или этажей """
        if "virtual" in self.porch.type: # страховка от захода в виртуальный подъезд
            if self.contactsEntryPoint: self.conPressed()
            elif self.searchEntryPoint: self.find(instance=instance)
            return
        self.updateMainMenuButtons()
        self.blockFirstCall = 0
        positive = f" {self.msg[155]}" if "подъезд" in self.porch.type else f" {self.msg[156]}"
        segment = f" {self.button['arrow']} {self.msg[157]} {self.porch.title}" if "подъезд" in self.porch.type else f" {self.button['arrow']} {self.porch.title}"
        options = self.porch.showFlats(sort=sortFlats)
        if self.house.type != "condo": neutral = ""
        elif self.porch.floors() and not self.porch.alpha: neutral = self.button['fgrid']
        elif not "подъезд" in self.porch.type: neutral = ""
        else: neutral = self.button['flist']
        note = self.porch.note if self.porch.note != "" else None

        if self.porch.floors() and not self.porch.alpha:
            noteButton = self.button["resize"]
            note = None
            sort = None
        else:
            noteButton = None
            sort = self.button["sort"]

        porchName = f" {self.house.getPorchType()[1]}" if self.language == "ka" \
            else f" {self.house.getPorchType()[1][0].upper()}{self.house.getPorchType()[1][1:]}" # для грузинского без заглавных

        self.displayed.update(
            title=self.house.title+segment,
            options=options,
            form="porchView",
            sort=sort,
            resize=noteButton,
            details=self.button["cog"] + porchName,
            positive=(self.button["edit"] if self.house.type == "condo" else self.button["plus"]) + positive,
            neutral=neutral,
            tip=[note, "note"]
        )
        if instance != None: self.stack.insert(0, self.displayed.form)
        self.updateList()

        if self.house.type == "condo" and len(self.porch.flats) == 0: # если нет квартир, сразу форма создания
            self.positivePressed()
            return

        if scroll_to == "last" and len(self.btn) >= self.listOnScreenLimit: # после сортировки прокручиваем список
            index = len(self.btn)-1
            self.clickedBtnIndex = index
            self.scroll.scroll_to(widget=self.btn[index], padding=0, animate=False)
        elif scroll_to != None and len(self.btn) >= self.listOnScreenLimit:
            self.clickedBtnIndex = scroll_to
            self.scroll.scroll_to(widget=self.btn[scroll_to], padding=0, animate=False)
        elif not self.porch.floors() and len(self.porch.flats) >= self.listOnScreenLimit: # пытаемся вернуться в последнюю квартиру
            index = self.clickedBtnIndex+1
            if index == len(self.btn): index -= 1
            try: self.scroll.scroll_to(widget=self.btn[index], padding=0, animate=False)
            except: pass

    def flatView(self, call=True, instance=None):
        """ Вид квартиры - список записей посещения """
        if "." in str(self.flat.number): return # страховка от случайного захода в удаленную квартиру
        self.updateMainMenuButtons()
        number = " " if self.flat.number == "virtual" else self.flat.number + " " # прячем номера отдельных контактов
        flatPrefix = f"{self.msg[214]} " if "подъезд" in self.porch.type else ""
        self.flatTitle = (flatPrefix + number + self.flat.getName()).strip()
        records = self.flat.showRecords()
        if self.flat.number == "virtual" or self.contactsEntryPoint: self.flatType = f" {self.msg[158]}"
        elif self.house.type == "condo":
            self.flatType = f" Apart." if self.language == "es" and self.fontScale() > 1.2 else f" {self.msg[159]}"
        else: self.flatType = f" {self.msg[57]}"
        note = self.flat.note if self.flat.note != "" else None

        self.displayed.update(
            title=self.flatTitle,
            message=self.msg[160],
            options=records,
            form="flatView",
            details=self.button["cog"] + self.flatType,
            positive=f"{self.button['plus']} {self.msg[161]}",
            neutral=self.button["phone"],
            tip=[note, "note"]
        )
        if not call and len(self.flat.records)==0: # всплывающее окно первого посещения
            self.clickedInstance = instance
            self.popup(firstCall=True)

        else:
            if instance != None or self.popupEntryPoint: self.stack.insert(0, self.displayed.form)
            if len(self.flat.records) == 0:
                if self.resources[0][1][7] == 0 and instance != None:
                    self.popup(title=self.msg[247], message=self.msg[229])
                    self.resources[0][1][7] = 1
                    self.save()
                self.scrollWidget.clear_widgets()
                self.navButton.disabled = False
                self.navButton.text = self.button['nav']

                self.createMultipleInputBox(
                    title=f"{self.flatTitle} {self.button['arrow']} {self.msg[162]}",
                    options=[self.msg[22], self.msg[83]],
                    defaults=[self.flat.getName(), ""],
                    multilines=[False, True],
                    disabled=[False, False],
                    details=self.button["cog"] + self.flatType,
                    neutral=self.button["phone"],
                    resize="",
                    sort="",
                    note=note
                )
                self.stack = list(dict.fromkeys(self.stack))
            else: self.updateList()

            if self.house.type != "virtual" and not self.contactsEntryPoint:
                self.colorBtn = []
                for i, status in zip(range(7), ["0", "1", "2", "3", "4", "5", ""]):
                    self.colorBtn.append(ColorStatusButton(status))
                    if status == self.flat.getStatus()[0][1]:
                        self.colorBtn[i].text = self.button["dot"]
                        self.colorBtn[i].markup = True
                colorBox = BoxLayout(size_hint_y=None, height=self.mainList.size[0]/7,
                                     spacing=self.spacing*2, padding=(self.padding*2, 0, self.padding*2, 0))
                if self.orientation == "h": colorBox.height = self.standardTextHeight
                colorBox.add_widget(self.colorBtn[1])
                colorBox.add_widget(self.colorBtn[2])
                colorBox.add_widget(self.colorBtn[3])
                colorBox.add_widget(self.colorBtn[4])
                colorBox.add_widget(self.colorBtn[0])
                colorBox.add_widget(self.colorBtn[5])
                colorBox.add_widget(self.colorBtn[6])
                self.mainList.add_widget(colorBox)

            if len(records) >= self.listOnScreenLimit: # пытаемся всегда вернуться на последнюю запись посещения
                try: self.scroll.scroll_to(widget=self.btn[self.clickedBtnIndex], padding=0, animate=False)
                except: pass

    def recordView(self, instance=None, focus=False):
        self.displayed.form = "recordView"
        self.createInputBox(
            title = f"{self.flatTitle} {self.button['arrow']} {self.record.date}",
            message = self.msg[83],
            default = self.record.title,
            multiline=True,
            details=self.button["cog"] + self.flatType,
            neutral=self.button["phone"],
            focus=focus
        )

    # Диалоговые окна

    def createInputBox(self, title="", form=None, message="", default="", hint="", checkbox=None, active=True, input=True,
                       positive=None, sort=None, resize=None, details=None, neutral=None, multiline=False, tip=None,
                       limit=99999, focus=False):
        """ Форма ввода данных с одним полем """
        if len(self.stack) > 0: self.stack.insert(0, self.stack[0]) # дублирование последнего шага стека, чтобы предотвратить уход со страницы
        if form == None: form = self.mainList
        form.clear_widgets()
        self.backButton.disabled = False
        if title != None: self.pageTitle.text = f"[ref=title]{title}[/ref]"
        self.positive.disabled = False
        self.positive.text = positive if positive != None else self.button["save"]
        if neutral != None:
            self.neutral.text = neutral
            self.neutral.disabled = False
            if self.neutral.text == self.button['phone'] and self.flat.phone == "":
                self.neutral.text = self.button['phone0']
                self.neutral.disabled = True
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
        grid = GridLayout(rows=2, cols=1, spacing=self.spacing, padding=(self.padding*2, self.padding*2, self.padding*2, 0))

        if message != "":
            self.inputBoxText = MyLabel(text=message, valign="center", size_hint_y=.6 * self.fontScale(),
                                        halign="center",
                                        font_size = self.fontS * self.fontScale(),
                                        text_size = (Window.size[0]*self.SR*.9, None))
            grid.add_widget(self.inputBoxText)

        if input:
            textbox = BoxLayout()
            size_hint_y = None if not multiline else 1
            self.inputBoxEntry = MyTextInput(multiline=multiline, hint_text=hint, size_hint_y=size_hint_y, limit=limit,
                                             text=default, pos_hint=pos_hint, focus=focus)
            textbox.add_widget(self.inputBoxEntry)
            grid.add_widget(textbox)

        if checkbox != None: # если заказана галочка, добавляем
            grid.rows += 1
            gridCB = GridLayout(rows=2, size_hint_y=.5)
            self.checkbox = MyCheckBox(active=active)
            gridCB.add_widget(self.checkbox)

            def __on_checkbox_active(checkbox, value): # что происходит при активированной галочке
                if self.displayed.form == "createNewHouse":
                    if value == 1:
                        self.inputBoxText.text = message
                        self.inputBoxEntry.hint_text = self.msg[70]
                    else:
                        self.inputBoxText.text = self.msg[165]
                        self.inputBoxEntry.hint_text = self.msg[166] + self.ruTerHint
                elif self.displayed.form == "createNewFlat":
                    if value == 1:
                        self.inputBoxText.text = self.msg[167]
                        filled = self.inputBoxEntry.text
                        textbox.remove_widget(self.inputBoxEntry)
                        self.inputBoxEntry = MyTextInput(text=filled, hint_text=self.msg[59], multiline=multiline,
                                                         size_hint_x=Window.size[0]*self.SR/2,
                                                         size_hint_y=None, pos_hint=pos_hint, input_type="number")
                        textbox.add_widget(self.inputBoxEntry)
                        self.inputBoxEntry2 = MyTextInput(hint_text = self.msg[60], multiline=multiline,
                                                          input_type="number", size_hint_x=Window.size[0]*self.SR/2,
                                                          size_hint_y=None, pos_hint=pos_hint)
                        self.inputBoxEntry.halign = self.inputBoxEntry2.halign ="center"
                        if not self.desktop:
                            self.inputBoxEntry.font_size = self.inputBoxEntry2.font_size = self.fontBigEntry
                            self.inputBoxEntry.height *= 1.2
                            self.inputBoxEntry2.height *= 1.2
                        textbox.add_widget(self.inputBoxEntry2)
                    else:
                        self.porchView()
                        self.positivePressed()
            self.checkbox.bind(active=__on_checkbox_active)
            gridCB.add_widget(MyLabel(text=checkbox, color=self.standardTextColor))
            grid.add_widget(gridCB)

        if not multiline or checkbox != None: # увеличиваем шрифт в одиночных полях ввода
            textbox.padding = (self.padding * 4, 0)
            self.inputBoxEntry.halign = "center"
            if not self.desktop:
                self.inputBoxEntry.height *= 1.2
                self.inputBoxEntry.font_size = self.fontBigEntry

        if tip != None: # добавление подсказки
            tipText = self.tip(tip)
            grid.rows += 3
            grid.add_widget(Widget())
            grid.add_widget(tipText)
            grid.add_widget(Widget())
        elif message != "":
            self.inputBoxText.size_hint_y = .2 # поиск и детали посещения
            if checkbox != None: # добавление домов
                grid.rows += 1
                grid.add_widget(Widget())

        form.add_widget(grid)

        if self.displayed.form == "recordView": # прокручивание текста до конца и добавление корзины
            Clock.schedule_once(lambda x: self.inputBoxEntry.do_cursor_movement(action="cursor_pgup", control="cursor_home"), 0)
            self.inputBoxEntry.shrink = False
            form.add_widget(Widget(height=self.standardTextHeight*2 if self.orientation=="v" else self.standardTextHeight/2,
                                   size_hint_y=None))
            binAnchor = AnchorLayout(anchor_y="center", anchor_x="right", pos_hint={"center_x": .5},
                                     size_hint=(1, None), padding=self.padding*6)
            form.add_widget(binAnchor)
            form.add_widget(Widget(height=self.standardTextHeight*2 if self.orientation=="v" else self.standardTextHeight/2,
                                   size_hint_y=None))
            binAnchor.add_widget(self.bin())

    def createMultipleInputBox(self, form=None, title=None, options=[], defaults=[], multilines=[], disabled=[],
                               sort=None, resize=None, details=None, note=None, neutral=None):
        """ Форма ввода данных с несколькими полями """
        if form == None: form = self.mainList
        form.clear_widgets()
        if len(self.stack) > 0: self.stack.insert(0, self.stack[0]) # дублирование последнего шага стека, чтобы предотвратить уход со страницы
        self.backButton.disabled = False
        self.positive.text = self.button["save"]
        self.positive.disabled = False
        self.detailsButton.disabled = True
        self.showSlider = False
        self.sliderToggle()

        if title != None: self.pageTitle.text = f"[ref=title]{title}[/ref]"
        if neutral == "":
            self.neutral.text = neutral
            self.neutral.disabled = True
        elif neutral != None:
            self.neutral.disabled = False
            self.neutral.text = neutral
            if self.neutral.text == self.button['phone'] and self.flat.phone == "":
                self.neutral.text = self.button['phone0']
                self.neutral.disabled = True
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
        if note != None: self.mainList.add_widget(self.tip(note, icon="note"))

        grid = GridLayout(rows=len(options), cols=2, pos_hint={"top": 1}, spacing=self.spacing, padding=self.padding*2)

        self.multipleBoxLabels = []
        self.multipleBoxEntries = []
        checkbox = False

        if len(disabled) < len(defaults):
            for i in range(len(multilines)):
                disabled.append(False)

        for row, default, multiline, disable in zip(range(len(options)), defaults, multilines, disabled):
            if self.displayed.form == "set":
                if str(options[row]) == self.msg[124]:  # поле ввода
                    text = options[row].strip()
                elif "{}" in str(options[row]):  # галочка
                    text = str(options[row][2:]).strip()
                    checkbox = True
                else:  # выпадающий список
                    text = str(options[row][2:]).strip()
                labelSize_hint = (1, 1)
                entrySize_hint = ((.5 if self.orientation == "v" else .3), 1)
                text_size = (Window.size[0]*self.SR * 0.66, None)
                halign = "center"
                if self.desktop and self.msg[130] in text: # не показываем опцию уведомления, если таймер отключен, а также всегда на ПК
                    timerOK = False
                elif self.msg[130] not in text or (self.msg[130] in text and self.settings[0][22] == 1):
                    timerOK = True
                else: timerOK = False
            else:
                y = 1 if multiline else None
                text = options[row].strip()
                labelSize_hint = (self.descrColWidth, y)
                entrySize_hint = (1-self.descrColWidth, y)
                text_size = (Window.size[0]*self.SR*self.descrColWidth, None)
                halign="left"
                timerOK = True

            if self.displayed.form == "set": limit = 99999 # задаем лимиты символов
            elif multiline: limit = 99999
            else: limit = self.charLimit
            height = self.standardTextHeight
            self.multipleBoxLabels.append(MyLabel(text=text, valign="center", halign="center", size_hint=labelSize_hint,
                                                  markup=True, text_size=text_size, font_size=self.fontS,
                                                  color=self.standardTextColor, height=height))

            if default != "virtual" and timerOK: # скрываем поле "номер/подъезд" для виртуальных контактов
                grid.add_widget(self.multipleBoxLabels[row])

            textbox = BoxLayout(size_hint=entrySize_hint, height=height, pos_hint={"center_x": .5},
                                padding=0 if not multiline else (0, self.spacing, 0, 0))

            if self.msg[127] in str(options[row]): self.multipleBoxEntries.append(RejectColorSelectButton())

            elif self.msg[131] in str(options[row]): self.multipleBoxEntries.append(self.languageSelector())

            elif self.msg[315] in str(options[row]): self.multipleBoxEntries.append(self.mapSelector())

            elif self.msg[168] in str(options[row]): self.multipleBoxEntries.append(self.themeSelector())

            elif checkbox == False:
                input_type = "number" if self.displayed.form == "set" or self.msg[17] in self.multipleBoxLabels[row].text\
                    else "text"
                self.multipleBoxEntries.append(MyTextInput(text = str(default) if default != "virtual" else "",
                                                           halign=halign,
                                                           multiline=multiline, size_hint_x=entrySize_hint[0],
                                                           size_hint_y=entrySize_hint[1] if multiline else None,
                                                           limit=limit, input_type = input_type, disabled=disable,
                                                           shrink=True if multiline and self.displayed.form=="flatView" else False,
                                                           pos_hint={"center_x": .5, "center_y": .5}, height=height*.9))

            else: self.multipleBoxEntries.append(MyCheckBox(active=default, size_hint=(entrySize_hint[0], entrySize_hint[1]),
                                                            pos_hint = {"top": 1}, color=self.titleColor))

            if self.displayed.form == "houseDetails" and\
                    self.multipleBoxLabels[row].text == self.msg[17]: # добавляем кнопку календаря в настройки участка
                calButton = TableButton(text=self.button["calendar"], size_hint_y=None, height=height*.9,
                                        size_hint_x=.2 if self.orientation == "v" else .1)
                textbox.spacing = self.spacing
                def calPress(instance): self.popup("showDatePicker")
                calButton.bind(on_release=calPress)
                textbox.add_widget(self.multipleBoxEntries[row])
                textbox.add_widget(calButton)
                grid.add_widget(textbox)
            elif default != "virtual" and timerOK:#and (self.msg[130] not in text and self.settings[0][22] == 0): # скрываем поле "номер/подъезд" для виртуальных контактов
                textbox.add_widget(self.multipleBoxEntries[row])
                grid.add_widget(textbox)
                #if self.msg[130] in text and self.settings[0][22] == 0: # убираем уведомление по таймеру, если сам таймер отключен
                #    textbox.remove_widget(self.multipleBoxEntries[row])
                #    grid.remove_widget(textbox)

        form.add_widget(grid)

        if self.displayed.form == "flatView" and len(self.flat.records)==0:
            grid.padding = (self.padding*2, self.padding*2, self.padding*2, 0)

        elif "Details" in self.displayed.form: # добавление корзины
            form.add_widget(Widget(height=self.standardTextHeight*2 if self.orientation=="v" else self.standardTextHeight/2,
                                   size_hint_y=None))
            lowGrid = GridLayout(cols=3, size_hint=(1, None))
            form.add_widget(lowGrid)
            form.add_widget(Widget(height=self.standardTextHeight*2 if self.orientation=="v" else self.standardTextHeight/2,
                                   size_hint_y=None))
            pad = self.padding * 5
            a1 = AnchorLayout(anchor_y="center", anchor_x="left", padding=pad)
            a2 = AnchorLayout(anchor_y="center", anchor_x="center", padding=pad)
            binAnchor = AnchorLayout(anchor_y="center", anchor_x="right", size_hint=(1, 1), padding=self.padding*6)
            lowGrid.add_widget(a1)
            lowGrid.add_widget(a2)
            lowGrid.add_widget(binAnchor)

            if not "flat" in self.displayed.form: # в участке добавляем кнопку экспорта телефонов
                if self.displayed.form == "houseDetails":
                    a1.add_widget(self.exportTer())
                    a2.add_widget(self.exportPhones())
                    binAnchor.add_widget(self.bin())
                else: binAnchor.add_widget(self.bin())
            else:
                if self.contactsEntryPoint or self.searchEntryPoint: binAnchor.add_widget(self.bin())
                elif self.house.type == "private": binAnchor.add_widget(self.bin())
                elif self.displayed.form == "flatDetails" and "подъезд" in self.porch.type and self.porch.floors():
                    lowGrid.cols=1
                    lowGrid.remove_widget(a1)
                    lowGrid.remove_widget(binAnchor)
                    a2.add_widget(self.bin("уменьшить этаж"))
                elif not self.porch.floors():
                    binAnchor.add_widget(self.bin())
                else: binAnchor.add_widget(self.bin())

    # Генераторы интерфейсных элементов

    def themeSelector(self):
        """ Выбор темы для настроек """
        a = AnchorLayout()
        self.dropThemeMenu = DropDown()
        try: currentTheme = list({i for i in self.themes if self.themes[i] == self.theme})[0]
        except: currentTheme = self.msg[307]
        if self.themeOverriden: currentTheme = list({i for i in self.themes if self.themes[i] == self.themeOld})[0]
        options = list(self.themes.keys())
        for option in options:
            btn = SortListButton(text=option)
            btn.bind(on_release=lambda btn: self.dropThemeMenu.select(btn.text))
            self.dropThemeMenu.add_widget(btn)
        self.themeButton = RButton(text=currentTheme, size_hint_x=1, size_hint_y=.7, radiusK=.2)
        self.dropThemeMenu.bind(on_select=lambda instance, x: setattr(self.themeButton, 'text', x))
        self.themeButton.bind(on_release=self.dropThemeMenu.open)
        a.add_widget(self.themeButton)
        return a

    def languageSelector(self):
        """ Выбор языка для настроек """
        a = AnchorLayout()
        self.dropLangMenu = DropDown()
        options = list(self.languages.values())
        for option in options:
            btn = SortListButton(font_name=self.differentFont, text=option[0])
            btn.bind(on_release=lambda btn: self.dropLangMenu.select(btn.text))
            self.dropLangMenu.add_widget(btn)
        self.languageButton = RButton(font_name=self.differentFont, text=self.msg[1], size_hint_x=1,
                                      size_hint_y=.7, radiusK=.2)
        self.dropLangMenu.bind(on_select=lambda instance, x: setattr(self.languageButton, 'text', x))
        self.languageButton.bind(on_release=self.dropLangMenu.open)
        a.add_widget(self.languageButton)
        return a

    def mapSelector(self):
        """ Выбор карт """
        a = AnchorLayout()
        self.dropMapsMenu = DropDown()
        for map in self.maps:
            btn = SortListButton(text=map)
            btn.bind(on_release=lambda btn: self.dropMapsMenu.select(btn.text))
            self.dropMapsMenu.add_widget(btn)
        if len(str(self.settings[0][21]))<3: self.settings[0][21] = "Google"
        self.mapsButton = RButton(text=self.settings[0][21], size_hint_x=1, size_hint_y=.7, radiusK=.2)
        self.dropMapsMenu.bind(on_select=lambda instance, x: setattr(self.mapsButton, 'text', x))
        self.mapsButton.bind(on_release=self.dropMapsMenu.open)
        a.add_widget(self.mapsButton)
        return a

    def exportTer(self):
        """ Кнопка экспорта участков """
        string = f"{self.button['share']} {self.msg[153]}"
        text = ""
        for char in string:
            if char == " ":
                text += "\n"
            else:
                text += char
        w = h = self.mainList.size[0] * .25 if not self.desktop else 90 # размер (сторона квадрата)
        if self.language == "tr":
            w *= 1.1
            h *= 1.1
        btn = RButton(text=text, size_hint_x=None, size_hint_y=None, radiusK=self.standardRButtonRadius,
                      size=(w, h), text_size=(w, None))
        def __exportTer(instance):
            if not self.desktop: self.share(email=True, ter=self.house)
            else: self.share(file=True, ter=self.house)
        btn.bind(on_release=__exportTer)
        return btn

    def exportPhones(self, includeWithoutNumbers=None):
        """ Кнопка экспорта телефонов участка либо обработка ее нажатия """
        if includeWithoutNumbers == None: # пользователь еще не ответил, создаем выпадающее меню
            string = f"{self.button['share']} {self.msg[154]}"
            text = ""
            for char in string:
                if char == " ": text += "\n"
                else: text += char
            w = h = self.mainList.size[0] * .25 if not self.desktop else 90 # размер (сторона квадрата)
            if self.language == "tr":
                w *= 1.1
                h *= 1.1
            btn = RButton(text=text, size_hint_x=None, size_hint_y=None, radiusK=self.standardRButtonRadius,
                          size=(w, h), text_size=(w, None))

            def __exportPhones(instance):
                self.popup("includeWithoutNumbers", message=self.msg[172], options=[self.button["yes"], self.button["no"]])
            btn.bind(on_release=__exportPhones)
            return btn

        else: # пользователь ответил на вопрос, экспортируем
            string = self.msg[314] % self.house.title + ":\n\n"
            flats = []
            for porch in self.house.porches:
                for flat in porch.flats:
                    if includeWithoutNumbers and not "." in flat.number: flats.append(flat)
                    elif not includeWithoutNumbers and flat.phone != "": flats.append(flat)
            if len(flats) == 0: self.popup(message=self.msg[313])
            else:
                try:    flats.sort(key=lambda x: float(x.number))
                except: flats.sort(key=lambda x: ut.numberize(x.title))
                for flat in flats:
                    string += f"{flat.number}. {flat.phone}\n"
                plyer.email.send(subject=self.msg[314] % "", text=string, create_chooser=True)

    def bin(self, label=None):
        """ Корзина на текстовых формах """
        if label == None: # корзина
            string = self.button['bin']
            text = ""
            w = h = self.mainList.size[0] * .25 if not self.desktop else 90 # размер (сторона квадрата)
            if self.language == "tr":
                w *= 1.1
                h *= 1.1
            for char in string:
                if char == " ": text += "\n"
                else: text += char
        else: # любая другая кнопка, на данный момент только уменьшение этажей
            text = self.button['shrink']
            w = self.mainList.width * (.6 if self.orientation == "v" else .4)
            h = self.standardTextHeight * 1.7
        btn = RButton(text=text, size_hint_x=None, size_hint_y=None, radiusK=self.standardRButtonRadius,
                      size=(w, h), text_size=(w, None))
        btn.bind(on_release=self.deletePressed)
        return btn

    def tip(self, text="", icon="info", hint_y=None, func=None):
        """ Подсказка """
        k = .8
        background_color = None
        if icon == "warn":
            color = "F4CA16" # желтый
            background_color = [.96, .95, .78] if self.mode == "light" else [.37, .32, .11]
            size_hint_y = hint_y if hint_y != None else 0.22
            size_hint_y *= self.fontScale()
            if self.bigLanguage: size_hint_y *= 1.25
            k=.95
            textHeight = None
            halign = "left"
        elif icon == "info":
            color = self.titleColor2
            size_hint_y = hint_y if hint_y != None else 0.5
            size_hint_y *= self.fontScale()
            textHeight = None
            halign = "left"
        elif icon == "note":
            color = self.titleColor2
            size_hint_y = None#0.1
            textHeight = self.standardTextHeight
            halign = "center"
        elif icon == "link":
            color = get_hex_from_color(self.linkColor)
            size_hint_y = hint_y if hint_y != None else 0.5
            size_hint_y *= self.fontScale()
            textHeight = None
            halign = "left"
            text = f"[u][color={color}][ref=link]{text}[/ref][/color][/u]"

        if text == "": # если получен пустой текст, вместо подсказки ставим пустой виджет
            tip = Widget(size_hint_y=size_hint_y)
        else:
            if icon == "warn":
                tip = TipButton(text=f"[ref=note][color={color}]{self.button[icon]}[/color] {text}[/ref]",
                                text_size=[self.mainList.size[0] * k, None],#textHeight],
                                size_hint_y=size_hint_y, font_size=self.fontXS * self.fontScale(),
                                halign=halign, valign="center", background_color = background_color)
            else:
                tip = MyLabel(text=f"[ref=note][color={color}]{self.button[icon]}[/color] {text}[/ref]",
                              text_size=[self.mainList.size[0] * k, textHeight],
                              size_hint_y=size_hint_y, font_size=self.fontXS * self.fontScale(),
                              markup=True, halign=halign, valign="top")
        if icon == "note" or icon == "warn": tip.bind(on_ref_press=self.titlePressed)
        elif icon == "link": tip.bind(on_ref_press=func)
        return tip

    # Функции для контактов

    def retrieve(self, containers, h, p, f, contacts):
        """ Retrieve and append contact list """

        number = "" if containers[h].type == "virtual" else containers[h].porches[p].flats[f].number

        if len(containers[h].porches[p].flats[f].records) > 0:
                lastRecordDate = containers[h].porches[p].flats[f].records[0].date
        else:   lastRecordDate = None#""
        if containers[h].porches[p].flats[f].lastVisit == "": containers[h].porches[p].flats[f].lastVisit = 0
        contacts.append([  # create list with one person per line with values:
            containers[h].porches[p].flats[f].getName(),  # 0 contact name
            containers[h].porches[p].flats[f].getStatus()[0],  # 1 status
            containers[h].title,  # 2 house title
            number,  # 3 flat number
            lastRecordDate,  # 4 дата последней встречи - отображаемая, record.date
            containers[h].porches[p].flats[f].lastVisit, # 5 дата последней встречи - абсолютная, record.lastVisit
            "",  # не используется
            [h, p, f],  # 7 reference to flat
            containers[h].porches[p].type,  # 8 porch type ("virtual" as key for standalone contacts)
            containers[h].porches[p].flats[f].phone,  # 9 phone number

            # Used only for search function:

            containers[h].porches[p].flats[f].title,  # 10 flat title
            containers[h].porches[p].flats[f].note,  # 11 flat note
            containers[h].porches[p].title,  # 12 porch type
            containers[h].note,  # 13 house note
            True if (len(containers[h].porches) > 1 and containers[h].porches[p].type == "сегмент") else False,# 14 True = универсальный участок и несколько сегментов, False = все остальное

            # Used for checking house type:

            containers[h].type,  # 15 house type ("virtual" as key for standalone contacts)
            containers[h].porches[p].flats[f].getStatus()[1],  # 16 sortable status ("value")
        ])
        return contacts

    def getContacts(self, forSearch=False):
        """ Returns list of all contacts """
        contacts = []
        for h in range(len(self.houses)):
            for p in range(len(self.houses[h].porches)):
                for f in range(len(self.houses[h].porches[p].flats)):
                    flat = self.houses[h].porches[p].flats[f]
                    if forSearch == False:  # поиск для списка контактов - только светло-зеленые жильцы и все отдельные контакты
                        if flat.status == "1" or flat.number == "virtual":
                            self.retrieve(self.houses, h, p, f, contacts)
                    else:  # поиск для поиска - все контакты вне зависимости от статуса
                        if not "." in flat.number:
                            self.retrieve(self.houses, h, p, f, contacts)

        for h in range(len(self.resources[1])):
            self.retrieve(self.resources[1], h, 0, 0, contacts)  # отдельные контакты - все

        return contacts

    # Обработка клавиатуры

    def hook_keyboard(self, window, key, *largs):
        """ Обрабатывает кнопку "назад" на мобильных устройствах и Esc на ПК """
        if key == 27:
            if self.backButton.disabled == False:
                self.backPressed()
            elif platform == "android":
                self.save()
                activity.moveTaskToBack(True)
            elif not self.desktop:
                self.save()
                self.stop()
            return True

    def keyboardHeight(self, *args):
        """ Возвращает высоту клавиатуры в str"""
        if platform == "android":
            rect = Rect(instantiate=True)
            activity.getWindow().getDecorView().getWindowVisibleDisplayFrame(rect)
            rect.top = 0
            height = activity.getWindowManager().getDefaultDisplay().getHeight() - (rect.bottom - rect.top)
            if height > 300: self.defaultKeyboardHeight = height
            else: height = self.defaultKeyboardHeight
            return height
        else:
            return self.defaultKeyboardHeight

    # Вспомогательные функции

    def log(self, message="", timeout=2, notify=False):
        """ Displaying and logging to file important system messages """
        if Devmode: print(message)
        elif self.desktop or notify:
            icon = "" if not self.desktop else "icon.ico"
            plyer.notification.notify(app_name="Rocket Ministry", title="Rocket Ministry", app_icon=icon,
                                      ticker="Rocket Ministry", message=message, timeout=timeout)
        else:
            plyer.notification.notify(toast=True, message=message)

    def addHouse(self, houses, input, type=True, forceUpper=False):
        """ Adding new house """
        if type == True: type = "condo"
        elif type == False: type = "private"
        houses.append(House())
        newHouse = len(houses) - 1
        houses[newHouse].title = input.strip() if not forceUpper or self.language == "ge" else (input.strip()).upper()
        houses[newHouse].type = type

    def editLastMonthReport(self, instance=None, value=None):
        """ Правка отчета прошлого месяца на странице отчета """
        if value == 0:
            self.rep.lastMonth = self.repBox.text
            self.rep.saveReport(mute=True)

    def recalcServiceYear(self, instance=None, value=None, allowSave=True):
        """ Подсчет статистики служебного года """
        if value == 1: return
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
                month.background_color = self.textInputBGColor

        hourSum = 0.0  # total sum of hours
        monthNumber = 0  # months entered
        for i in range(len(self.settings[4])):
            if self.settings[4][i] != None:
                hourSum += self.settings[4][i]
                monthNumber += 1
        yearNorm = float(self.settings[0][3]) * 12  # other stats
        gap = (12 - monthNumber) * float(self.settings[0][3]) - (yearNorm - hourSum)
        average = (yearNorm - hourSum) / (12 - monthNumber) if monthNumber != 12 else (yearNorm - hourSum)
        if gap >= 0:
            gapEmo = icon("icon-smile")
            gapWord = self.msg[174]
        elif gap < 0:
            gapEmo = icon("icon-frown")
            gapWord = self.msg[175]
        else:
            gapEmo = ""
        br = "" if Window.size[1]<=600 or self.bigLanguage else "\n"
        if not self.desktop and self.fontScale() > 1: self.analyticsMessage.font_size = self.fontS
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
        if allowSave: self.save()

    def sendLastMonthReport(self, instance=None):
        """ Отправка отчета прошлого месяца """
        plyer.email.send(subject=self.msg[4], text=self.rep.lastMonth, create_chooser=True)

    def colorBtnPressed(self, color):
        """ Нажатие на цветной квадрат статуса """
        if len(self.flat.records) == 0:
            if self.multipleBoxEntries[0].text.strip() != "":
                self.flat.updateName(self.multipleBoxEntries[0].text.strip())
            if self.multipleBoxEntries[1].text.strip() != "":
                self.flat.addRecord(self.multipleBoxEntries[1].text.strip())
        for i in ["0", "1", "2", "3", "4", "5", ""]:
            if color == "":
                self.popup("resetFlatToGray", message=self.msg[193], options=[self.button["yes"], self.button["no"]])
                return
            elif color == i:
                self.flat.status = i
                if len(self.stack) > 0: del self.stack[0]
                break
        self.save()
        if self.searchEntryPoint: self.find(instance=True)
        else: self.porchView()

    def getColorForStatus(self, status=99):
        """ Возвращает цвет по полученному символу статуса """
        if self.theme == "purple" or self.theme == "morning":
            if status == "?":   return [.43, .43, .43, 1] # темно-серый
            elif status == "0": return [.29, .43, .65, 1] # синий
            elif status == "1": return [.16, .69, .29, 1] # зеленый
            elif status == "2": return [.29, .4, .19, 1]  # темно-зеленый
            elif status == "3": return [.48, .34, .65, 1] # фиолетовый
            elif status == "4": return [.77, .52, .19, 1] # оранжевый
            elif status == "5": return [.58, .16, .15, 1] # красный
            else:               return [.6, .6, .6, 1]
        else:
            if status == "?":   return self.darkGrayFlat  # темно-серый
            elif status == "0": return [0, .54, .73, 1]   # синий
            elif status == "1": return [0, .74, .50, 1]   # зеленый
            elif status == "2": return [.30, .50, .46, 1] # темно-зеленый
            elif status == "3": return [.53, .37, .76, 1] # фиолетовый
            elif status == "4": return [.73, .63, .33, 1] # желтый | светло-коричневый
            elif status == "5": return [.81, .24, .17, 1] # красный
            else:               return self.lightGrayFlat

    def deletePressed(self, instance=None, forced=False):
        """ Действие при нажатии на кнопку с корзиной на форме любых деталей """
        if self.displayed.form == "houseDetails": # удаление участка
            self.popup("confirmDeleteHouse", title=f"{self.msg[194]}: {self.house.title}", message=self.msg[195],
                       options=[self.button["yes"], self.button["no"]])

        elif self.displayed.form == "porchDetails": # удаление подъезда
            title = self.msg[196] if self.house.type == "condo" else self.msg[197]
            self.popup("confirmDeletePorch", title=f"{title}: {self.porch.title}", message=self.msg[198],
                       options=[self.button["yes"], self.button["no"]])

        elif self.displayed.form == "flatDetails" or self.displayed.form == "flatView" or forced: # удаление квартиры
            self.popupForm = "confirmDeleteFlat"
            if self.contactsEntryPoint or self.searchEntryPoint or (self.flat.status != "" and not self.porch.floors()):
                self.popup(title=f"{self.msg[199]}: {self.flatTitle}", message=self.msg[198],
                           options=[self.button["yes"], self.button["no"]])
            else:
                self.popupPressed(instance=Button(text=self.button["yes"]))

        elif self.displayed.form == "recordView": # удаление записи посещения
            self.popup("confirmDeleteRecord", title=self.msg[200],
                       message=f"{self.msg[201]} {self.record.date}?",
                       options=[self.button["yes"], self.button["no"]])

        elif self.displayed.form == "noteForFlat":
            self.flat.note = ""
            self.save()
            self.flatView()

        elif self.displayed.form == "noteForPorch":
            self.porch.note = ""
            self.save()
            self.porchView()

        elif self.displayed.form == "noteForHouse":
            self.house.note = ""
            self.save()
            self.houseView()

    def confirmNonSave(self):
        """ Проверяет, есть ли несохраненные данные в форме первого посещения """
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
        if self.popupForm == "timerType":
            self.rep.modify(")" if instance.text == self.msg[42] else "$")
            if self.displayed.form == "rep": self.repPressed()

        elif self.popupForm == "clearData":
            if instance.text == self.button["yes"]:
                self.clearDB()
                self.removeFiles()
                self.log(self.msg[192])
                self.restart("soft")
                self.terPressed()

        elif self.popupForm == "restoreRequest":
            if instance.text == self.button["yes"]:
                result = self.backupRestore(restoreNumber=self.fileToRestore, allowSave=False)
                self.dismissTopPopup()
                if result == False:
                    self.popup(title=self.msg[44], message=self.msg[45])
                else:
                    self.restart("soft")
                    self.terPressed()
                    self.popup(title=self.msg[44], message=self.msg[258] % self.fileDates[self.fileToRestore])

        elif self.popupForm == "newMonth":
            self.repPressed()
            self.resizePressed()

        elif self.popupForm == "nonSave":
            if instance.text == self.button["yes"]:
                self.multipleBoxEntries[0].text = self.flat.getName()
                self.multipleBoxEntries[1].text = ""
                self.func()

        elif self.popupForm == "confirmDeleteRecord":
            if instance.text == self.button["yes"]:
                self.save()
                time.sleep(self.backupTimeoutBeforeDelete)
                self.flat.deleteRecord(self.selectedRecord)
                self.save()
                self.flatView()

        elif self.popupForm == "confirmDeleteFlat":
            if instance.text == self.button["yes"]:
                self.save()
                time.sleep(self.backupTimeoutBeforeDelete)
                if self.house.type == "virtual":
                    del self.resources[1][self.selectedHouse]
                    if self.contactsEntryPoint or self.searchEntryPoint:
                        self.backPressed()
                        self.backPressed()
                elif self.house.type == "condo":
                    if not self.contactsEntryPoint and not self.searchEntryPoint:
                        if self.resources[0][1][0] == 0 and self.porch.floors():
                            self.popup("confirmShrinkFloor", title=self.msg[203], message=self.msg[299],
                                       checkboxText=self.msg[170], options=[self.button["yes"], self.button["no"]])
                            return
                        elif not self.porch.floors():
                            self.porch.deleteFlat(self.selectedFlat)
                            self.porch.type="подъезд"
                            if self.popupEntryPoint: self.porchView()
                            else:
                                self.backPressed()
                                self.backPressed()
                        else:
                            self.porch.shrinkFloor(self.selectedFlat)
                            if self.displayed.form == "flatDetails":
                                if not self.popupEntryPoint: self.backPressed()
                                self.backPressed()
                            else: self.porchView()
                    else:
                        self.flat.wipe()
                        if self.contactsEntryPoint or self.searchEntryPoint:
                            self.backPressed()
                            self.backPressed()
                else:
                    self.porch.deleteFlat(self.selectedFlat)
                    if self.contactsEntryPoint or self.searchEntryPoint:
                        self.backPressed()
                        self.backPressed()
                    elif self.displayed.form == "porchView":
                        self.porchView()
                    else:
                        if not self.popupEntryPoint: self.backPressed()
                        self.backPressed()
                self.save()

        elif self.popupForm == "confirmShrinkFloor":
            if self.popupCheckbox.active: self.resources[0][1][0] = 1
            if instance.text == self.button["yes"]:
                self.porch.shrinkFloor(self.selectedFlat)
                self.porchView()
                self.save()

        elif self.popupForm == "confirmDeletePorch":
            if instance.text == self.button["yes"]:
                self.save()
                time.sleep(self.backupTimeoutBeforeDelete)
                self.house.deletePorch(self.selectedPorch)
                self.save()
                self.houseView()
                self.backPressed()

        elif self.popupForm == "confirmDeleteHouse":
            if instance.text == self.button["yes"]:
                self.save()
                time.sleep(self.backupTimeoutBeforeDelete)
                for porch in self.house.porches:
                    for flat in porch.flats:
                        flat.porchRef = porch
                        if flat.status == "1":
                            if flat.getName() == "": flat.updateName("?")
                            flat.clone(toStandalone=True, title=self.house.title)
                del self.houses[self.selectedHouse]
                self.save()
                self.terPressed()

        elif self.popupForm == "pioneerNorm":
            if instance.text == self.button["yes"]:
                self.settings[0][3] = 50
                self.save()
                self.repPressed()

        elif self.popupForm == "restart":
            if instance.text == self.button["yes"]:
                self.restart()

        elif self.popupForm == "resetFlatToGray":
            if instance.text == self.button["yes"]:
                self.save()
                time.sleep(self.backupTimeoutBeforeDelete)
                if len(self.stack) > 0: del self.stack[0]
                if self.flat.number == "virtual": del self.resources[1][self.selectedHouse]
                else:                             self.flat.wipe()
                if self.contactsEntryPoint:  self.conPressed()
                elif self.searchEntryPoint:  self.find(instance=True)
                else:                             self.porchView()
                self.save()
            else:
                self.colorBtn[6].text = ""
                for i, status in zip(range(7), ["0", "1", "2", "3", "4", "5", ""]):
                    if status == self.flat.getStatus()[0][1]:
                        self.colorBtn[i].text = self.button["dot"]
                        self.colorBtn[i].markup = True

        elif self.popupForm == "submitReport":
            if instance.text == self.button["no"]:
                self.buttonTer.deactivate()
                self.repPressed(jumpToPrevMonth=True)
                Clock.schedule_once(self.sendLastMonthReport, 0.3)

        elif self.popupForm == "includeWithoutNumbers":
            self.exportPhones(includeWithoutNumbers = True if instance.text == self.button["yes"] else False)

        elif self.popupForm == "timerPressed":
            if instance.text == self.button["yes"]: self.timerPressed(mode="activate")

        elif self.importHelp:
            if instance.text == self.button["yes"]:
                if self.language == "ru" or self.language == "uk":
                    webbrowser.open("https://github.com/antorix/Rocket-Ministry/wiki/ru#синхронизация-и-резервирование-данных")
                else:
                    webbrowser.open("https://github.com/antorix/Rocket-Ministry/wiki#data-synchronization-and-backup")
            self.importHelp = 0

        self.popupForm = ""

    def popup(self, popupForm="", message="", options="Close", title=None, firstCall=False, checkboxText=None, dismiss=True):
        """ Всплывающее окно """

        # Специальный попап для первого посещения

        if title == None: title = self.msg[203]
        if popupForm != "": self.popupForm = popupForm
        if options == "Close": options = [self.msg[39]]
        size_hint = [.9, .6] if self.orientation == "v" else [.5, .8]
        auto_dismiss = dismiss
        radiusK = self.standardRButtonRadius

        if firstCall == True:
            self.popupForm = "firstCall"
            radiusK = .6  # степень закругленности кнопок
            title = self.flat.number
            size_hint = [.8, .55] if self.orientation == "v" else [.35, .72]
            contentMain = BoxLayout(orientation="vertical", padding=self.padding)
            content = GridLayout(rows=1, cols=1, padding=self.padding, spacing=self.spacing)
            content2 = GridLayout(rows=1, cols=1, padding=[self.padding, 0, self.padding, self.padding],
                                  spacing=self.spacing)
            spacingK = 3 # коэффициент увеличения кнопки в углу формы
            buttonsGrid = BoxLayout(orientation="horizontal", size_hint=(None, None), height=self.standardTextHeight,
                                    width=self.standardTextHeight*2 + self.spacing * spacingK,
                                    pos_hint={"right": 1, "center": .5}, spacing=self.spacing * spacingK)
            shrink = TableButton(text=icon('icon-scissors') if self.porch.floors() else icon('icon-trash-1'),
                                 form=self.popupForm, size_hint_x=None, size_hint_y=None, color=self.popupButtonColor,
                                 size=(self.standardTextHeight, self.standardTextHeight),
                                 font_size=self.fontS * self.fontScale(),
                                 background_color=self.popupBackgroundColor, pos_hint={"right": 1, "center": .5})
            def __shrink(instance):
                self.dismissTopPopup()
                self.buttonFlash(instance)
                self.popupEntryPoint = 1
                self.blockFirstCall = 1
                self.deletePressed(forced=True)
            shrink.bind(on_release=__shrink)
            buttonsGrid.add_widget(shrink)

            details = TableButton(text=self.button["cog"], size_hint_x=None, size_hint_y=None, # кнопка настроек
                                  font_size=self.fontS * self.fontScale(),
                                  color=self.popupButtonColor, form=self.popupForm,
                                  size=(self.standardTextHeight, self.standardTextHeight),
                                  background_color=self.popupBackgroundColor, pos_hint={"right": 1})
            def __details(instance):
                self.dismissTopPopup()
                self.buttonFlash(instance)
                self.popupEntryPoint = 1
                self.blockFirstCall = 1
                self.flatView()
                del self.stack[0]
                self.detailsPressed()
            details.bind(on_release=__details)
            buttonsGrid.add_widget(details)
            contentMain.add_widget(buttonsGrid)

            if self.settings[0][20] == 1: # если нужно добавить телефон
                self.keyboardCloseTime = .1
                size_hint[1] = size_hint[1] * 1.06
                self.quickPhone = MyTextInput(size_hint_y=None, hint_text = self.msg[35], height=self.standardTextHeight,
                                              focus=True if self.desktop else False,
                                              multiline=False, input_type="text", popup=True)
                contentMain.add_widget(self.quickPhone)
                def __getPhone(instance):
                    self.dismissTopPopup()
                    self.quickPhone.hint_text = self.msg[204]
                    self.popupForm = "quickPhone"
                    self.flat.editPhone(self.quickPhone.text)
                    self.save()
                    if self.porch.floors(): self.clickedInstance.colorize()
                    else: self.porchView()
                    self.quickPhone.text = ""
                self.quickPhone.bind(on_text_validate=__getPhone)

                def __dismiss(instance, value):
                    if value == 0: self.dismissTopPopup()
                if self.desktop: # на компьютере закрываем попап при дефокусе строки поиска
                    self.quickPhone.bind(focus=__dismiss)

            if self.settings[0][13] == 1:  # кнопка нет дома
                content.cols += 1
                colorBG = None if self.theme == "3D" else [.25, .25, .25]
                firstCallNotAtHome = RButton(text=self.button['lock'], color="white",
                                             font_size=self.fontS * self.fontScale(),
                                             quickFlash=True, background_color=colorBG, radiusK=radiusK)
                def __quickNotAtHome(instance):
                    date = time.strftime("%d", time.localtime())
                    month = self.monthName()[5]
                    timeCur = time.strftime("%H:%M:%S", time.localtime())
                    newNote = f"{date} {month} {timeCur} {self.msg[206][0].lower()+self.msg[206][1:]}\n" + self.flat.note
                    self.flat.editNote(newNote)
                    self.save()
                    if self.porch.floors(): self.clickedInstance.colorize()
                    else: self.porchView()
                    self.dismissTopPopup()#.dismiss()
                    if self.resources[0][1][4] == 0:
                        self.popup(title=self.msg[247], message=self.msg[205] % self.msg[206])
                        self.resources[0][1][4] = 1
                        self.save()
                firstCallNotAtHome.bind(on_release=__quickNotAtHome)
                content.add_widget(firstCallNotAtHome)

            if self.theme == "dark" or self.theme == "morning":
                color = self.popupBackgroundColor
                colorBG = self.themeDefault[0]
            elif self.theme == "gray":
                color = self.tableBGColor
                colorBG = self.themeDefault[0]
            elif self.theme == "3D":
                color = self.titleColor
                colorBG = None
            else:
                color = self.tableColor
                colorBG = self.themeDefault[0]

            firstCallBtnCall = RButton(text=self.button['record'], quickFlash=True,# кнопка интерес
                                       font_size=self.fontS * self.fontScale(),
                                       color=color, background_color=colorBG, radiusK=radiusK)
            def __firstCall(instance):
                self.dismissTopPopup()
                self.flatView(call=True, instance=instance)
            firstCallBtnCall.bind(on_release=__firstCall)
            content.add_widget(firstCallBtnCall)

            if self.theme == "3D": # кнопка отказ
                color = [
                    self.getColorForStatus(self.settings[0][18])[0],
                    self.getColorForStatus(self.settings[0][18])[1],
                    self.getColorForStatus(self.settings[0][18])[2]
                ]
                colorBG = None
            else:
                color = "white"
                colorBG = self.getColorForStatus(self.settings[0][18])
            firstCallBtnReject = RButton(text=self.button['reject'], background_color=colorBG,
                                         font_size=self.fontS * self.fontScale(),
                                         color=color, quickFlash=True, radiusK=radiusK)
            def __quickReject(instance):
                self.flat.addRecord(self.msg[207][0].lower() + self.msg[207][1:]) # "отказ"
                self.flat.status = self.settings[0][18]  # "0"
                self.save()
                if self.porch.floors(): self.clickedInstance.colorize()
                else: self.porchView()
                self.dismissTopPopup()
            firstCallBtnReject.bind(on_release=__quickReject)
            content2.add_widget(firstCallBtnReject)

            contentMain.add_widget(content)
            contentMain.add_widget(content2)

            grid = GridLayout(rows=2, cols=1, size_hint_y=None)
            grid.add_widget(Widget())
            self.buttonClose = RButton(text=self.msg[190], onPopup=True, pos_hint={"bottom": 1}, radiusK=radiusK)
            grid.add_widget(self.buttonClose)
            self.buttonClose.bind(on_release=self.popupPressed)
            contentMain.add_widget(grid)

            self.popupForm = ""

        # Выбор времени для отчета

        elif self.popupForm == "showTimePicker":
            self.popupForm = ""
            pickerForm = BoxLayout(orientation="vertical", padding=self.padding, spacing=self.spacing*2)
            from circulartimepicker import CircularTimePicker
            picker = CircularTimePicker() # часы
            self.pickedTime = "00:00"
            def __setTime(instance, time):
                self.pickedTime = time
            picker.bind(time=__setTime)
            pickerForm.add_widget(picker)
            save = RButton(text=self.msg[188], onPopup=True, pos_hint={"bottom": 1}, radiusK=radiusK)  # кнопка сохранения

            def __closeTimePicker(instance):
                self.dismissTopPopup()
                time2 = str(self.pickedTime)[:5] # время, выбранное на пикере (HH:MM)
                if title == self.msg[108]:
                    time1 = self.hours.get()  # исходное время на счетчике (HH:MM)
                    if self.pickedTime != "00:00":
                        try:
                            self.time3 = ut.sumHHMM([time1, time2]) # сумма исходного и добавленного времени (HH:MM)
                            self.rep.modify(f"ч{time2}")
                            self.hours.update(self.time3)
                            self.pageTitle.text = f"[b][ref=report]{self.msg[4]}{self.rep.getCurrentHours()[2]}[/ref][/b]"
                            if self.settings[0][2]: self.creditLabel.text = self.msg[105] % self.rep.getCurrentHours()[0]
                        except: self.popup(message=self.msg[46])
                elif title == self.msg[109]:
                    time1 = self.credit.get()  # исходное время на счетчике (HH:MM)
                    if self.pickedTime != "00:00":
                        try:
                            self.time3 = ut.sumHHMM([time1, time2])  # сумма двух времен в HH:MM
                            self.rep.modify(f"к{time2}")
                            self.credit.update(self.time3)
                            self.pageTitle.text = f"[b][ref=report]{self.msg[4]}{self.rep.getCurrentHours()[2]}[/ref][/b]"
                            self.creditLabel.text = self.msg[105] % self.rep.getCurrentHours()[0]
                        except: self.popup(message=self.msg[46])

            save.bind(on_release=__closeTimePicker)

            grid = GridLayout(rows=1, cols=3, size_hint_y=None)
            grid.cols_minimum = {
                0: grid.width*.45,
                1: grid.width*.1,
                2: grid.width*.45
            }
            grid.add_widget(save)
            grid.add_widget(Widget())
            self.buttonClose = RButton(text=self.msg[190], onPopup=True, radiusK=radiusK)
            self.buttonClose.bind(on_release=self.popupPressed)
            grid.add_widget(self.buttonClose)
            pickerForm.add_widget(grid)

            contentMain = pickerForm

        # Выбор даты

        elif self.popupForm == "showDatePicker":
            self.popupForm = ""
            title=""
            contentMain = BoxLayout(orientation="vertical", padding=self.padding, spacing=self.spacing*2)
            self.datePicked = DatePicker(padding=(0, 0, 0, self.padding*7))
            contentMain.add_widget(self.datePicked)
            self.buttonClose = RButton(text=self.msg[190], onPopup=True, pos_hint={"bottom": 1}, radiusK=radiusK)
            self.buttonClose.bind(on_release=self.popupPressed)
            contentMain.add_widget(self.buttonClose)

        # Добавление списка квартир

        elif self.popupForm == "addList":
            self.popupForm = ""
            title = self.msg[191]
            if self.orientation == "v": size_hint[1] *= self.fontScale()
            width = self.mainList.width * size_hint[0] * .9
            contentMain = BoxLayout(orientation="vertical", spacing=self.spacing, padding=self.padding)
            text = MyTextInput(hint_text=self.msg[185] if self.house.type == "condo" else self.msg[309],
                               multiline=True, shrink=False,
                               focus=True if self.desktop else False)
            contentMain.add_widget(text)
            btnPaste = TableButton(text=f"{icon('icon-paste')} {self.msg[186]}", size_hint_x=1, size_hint_y=None,
                                   width=width, height=self.standardTextHeight * (1.2 if not self.desktop else 1))
            def __paste(instance):
                text.text = Clipboard.paste()
            btnPaste.bind(on_release=__paste)
            contentMain.add_widget(btnPaste)
            warning = f" {self.msg[184]}" if self.house.type == "condo" else f" {self.msg[245]}"
            description = MyLabel(text=self.msg[187] + warning, text_size=(width, None),
                                  font_size=self.fontXS * self.fontScale(),
                                  valign="center", color=[.95, .95, .95])
            contentMain.add_widget(description)
            grid = GridLayout(cols=3, size_hint=(1, None))
            btnSave = RButton(text=self.msg[188], onPopup=True, radiusK=radiusK)

            def __save(instance):
                flats = text.text.strip()
                newstr = ""
                for char in flats:
                    if char == "\n": newstr += ","
                    elif char == ".": newstr += ";"
                    else: newstr += char
                if self.house.type == "private":
                    flats = [x for x in newstr.split(',')]
                else:
                    flats = []
                    for x in newstr.split(','):
                        flats.append(x)
                if self.porch.floors():  # отключение поэтажного вида
                    self.porch.type = "подъезд"
                    self.porch.flatsLayout = "н"
                for flat in flats:
                    self.porch.addFlat(f"{flat}")
                if "подъезд" in self.porch.type: self.porchView(sortFlats=True)
                else: self.porchView()#scroll_to="last")
                self.save()
                self.dismissTopPopup()

            btnSave.bind(on_release=__save)
            btnClose = RButton(text=self.msg[190], onPopup=True, radiusK=radiusK)
            btnClose.bind(on_release=self.popupPressed)
            grid.add_widget(btnSave)
            grid.add_widget(Widget())
            grid.add_widget(btnClose)
            contentMain.add_widget(grid)

        # Восстановление резервных копий

        elif self.popupForm == "restoreBackup":
            self.popupForm = ""
            title = self.msg[44]
            if self.orientation == "v": size_hint[1] *= self.fontScale()
            contentMain = BoxLayout(orientation="vertical", padding=self.padding, pos_hint={"top": 1})
            contentMain.add_widget(Label(text=self.msg[102], color=[.95, .95, .95], halign="left", valign="center",
                                         height=self.standardTextHeight*1.5,
                                         text_size=(self.mainList.width*size_hint[0]/self.SR*.9, self.standardTextHeight*1.5),
                                         size_hint=(1, None)))

            self.fileDates = [] # собираем файлы резервных копий
            try:
                files = [f for f in os.listdir(self.backupFolderLocation) if
                     os.path.isfile(os.path.join(self.backupFolderLocation, f))]
            except:
                self.popup(title=self.msg[135], message=self.msg[257]) # файлов нет, выходим
                return

            files.sort(reverse=True)
            for file in files:
                self.fileDates.append(str("{:%d.%m.%Y, %H:%M:%S}".format(
                    datetime.datetime.strptime(time.ctime((os.path.getmtime(self.backupFolderLocation + file))),
                                               "%a %b %d %H:%M:%S %Y"))))
            def __clickOnFile(instance): # обработка клика по файлу
                for i in range(len(files)):
                    if instance.text == str("{:%d.%m.%Y, %H:%M:%S}".format(
                        datetime.datetime.strptime(time.ctime((os.path.getmtime(self.backupFolderLocation + files[i]))),
                                                   "%a %b %d %H:%M:%S %Y"))):
                        break
                self.fileToRestore = i
                self.popup("restoreRequest", title=self.msg[44], message=self.msg[45] % self.fileDates[i],
                           options=[self.button["yes"], self.button["no"]])

            btn = [] # раскладываем кнопки
            self.backups = ScrollView(size=(self.mainList.size[0] * .9, self.mainList.size[1] * .9),
                                     bar_width=self.standardBarWidth, scroll_type=['bars', 'content'])

            gridList = GridLayout(cols=1, size_hint_y=None, spacing=self.spacing * 2, padding=self.padding)
            gridList.bind(minimum_height=gridList.setter('height'))
            for i in range(len(self.fileDates)):
                button=Button(text=self.fileDates[i], size_hint_y=None, height = self.standardTextHeight * 1.5,
                    color="white", background_color=[.22, .22, .22, .9] if self.theme != "3D" else self.buttonTint)
                def __click(instance):
                    Clock.schedule_once(lambda x: self.buttonFlash(instance=instance), 0.1)
                button.bind(on_press=__click)
                if self.theme != "3D":
                    button.background_down = self.buttonPressedBG
                    button.background_normal=""
                btn.append(button)
                gridList.add_widget(btn[i])
                btn[i].bind(on_release=__clickOnFile)
            gridList.add_widget(Widget(height=self.standardTextHeight, size_hint_y=None))
            self.backups.add_widget(gridList)
            contentMain.add_widget(self.backups)

            grid = GridLayout(rows=2, cols=1, size_hint_y=None) # добавляем кнопку "Отмена"
            self.confirmButtonPositive = RButton(text=options[0], onPopup=True, pos_hint={"bottom": 1}, radiusK=radiusK)

            self.confirmButtonPositive.bind(on_release=lambda x=True: self.dismissTopPopup(all=x))
            grid.add_widget(Widget())
            grid.add_widget(self.confirmButtonPositive)
            contentMain.add_widget(grid)

        # Стандартное информационное окно либо запрос да/нет

        else:
            size_hint = (.9, .2 * (self.fontScale()*2)) if self.orientation == "v" else (.6, .5)
            text_size = (Window.size[0] * size_hint[0] * .92, None)
            contentMain = BoxLayout(orientation="vertical")
            if checkboxText != None: contentMain.add_widget(Widget())
            label = MyLabel(text=message, halign="left", valign="center", text_size=text_size, markup=True,
                            font_size=self.fontXS*self.fontScale(), color=[.95, .95, .95])
            contentMain.add_widget(label)

            if checkboxText != None: # задана галочка
                contentMain.add_widget(Widget())
                CL = BoxLayout()
                self.popupCheckbox = MyCheckBox(size_hint=(.1, 1), halign="right")
                CL.add_widget(self.popupCheckbox)
                CL.add_widget(MyLabel(text="    "+checkboxText, halign="left", valign="center",
                                      color="lightgray", font_size = self.fontXS * .95 * self.fontScale(),
                                      size_hint=(.85, 1), text_size=text_size))
                contentMain.add_widget(CL)

            if len(options) > 0: # заданы кнопки
                grid = GridLayout(rows=1, cols=1, size_hint_y=None, pos_hint={"bottom": 1})
                self.confirmButtonPositive = RButton(text=options[0], onPopup=True, pos_hint={"bottom": 1}, radiusK=radiusK)
                self.confirmButtonPositive.bind(on_release=self.popupPressed)
                if len(options) == 1: # если кнопка одна (закрыть или отмена)
                    grid.rows += 1
                    grid.add_widget(Widget())
                grid.add_widget(self.confirmButtonPositive)
                if len(options) > 1: # если кнопок несколько
                    grid.cols +=2
                    grid.add_widget(Widget())
                    self.confirmButtonNegative = RButton(text=options[1], onPopup=True, radiusK=radiusK)
                    self.confirmButtonNegative.bind(on_release=self.popupPressed)
                    grid.add_widget(self.confirmButtonNegative)
                contentMain.add_widget(grid)

        self.popups.insert(0, PopupNoAnimation(title=title, content=contentMain, size_hint=size_hint,
                                        separator_color=self.titleColor if title != "" and
                                                                           title != self.msg[108] and title != self.msg[109]\
                                                                        else self.popupBackgroundColor,
                                        auto_dismiss=auto_dismiss))

        if firstCall == True:
            def __gotoPorch(instance):
                self.displayed.form = "porchView"
                self.displayed.options = self.porch.showFlats()
            self.popups[0].bind(on_dismiss=__gotoPorch)
            self.popupForm = ""
        Clock.schedule_once(self.popups[0].open, 0)

    def dismissTopPopup(self, all=False, *args):
        """ Закрывает и удаляет самый верхний попап в стеке """
        if len(self.popups) == 0: return
        if not all:
            self.popups[0].dismiss()
            del self.popups[0]
        else: # закрываем и удаляем вообще все попапы
            for popup in self.popups:
                popup.dismiss()
            del self.popups[:]

    def changePorchPos(self, pos):
        """ Центровка подъезда по кнопке на джойстике """
        if self.noScalePadding[0] < 0 or self.noScalePadding[1] < 0: return
        self.settings[0][1] = pos
        self.updateList()

    def loadLanguages(self):
        """ Загружает csv-файл с языками, если есть """
        import csv
        import glob
        languages = []
        for l in self.languages.keys():
            languages.append([])
        dir = "c:\\Users\\antor\\Downloads\\"
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
            ut.dprint(Devmode, "CSV-файл с локализациями не найден.")
        else:
            ut.dprint(Devmode, "CSV-файл с локализациями найден, обновляю языковые файлы.")
            with open("lpath.ini", encoding='utf-8', mode="r") as f: lpath = f.read()
            for i in range(len(self.languages.keys())):
                __generate(f"{lpath}\\{list(self.languages.keys())[i]}.lang", i)
            for zippath in glob.iglob(os.path.join(dir, '*.csv')):
                os.remove(zippath)

    def importDB(self, instance=None, link=None, file=None):
        """ Импорт данных из буфера обмена либо файла """
        self.save(silent=True)
        if file == None:
            ut.dprint(Devmode, "Пытаюсь загрузить базу по ссылке.")
            success = self.load(clipboard=link)
        else:
            ut.dprint(Devmode, "Пытаюсь загрузить базу из файла.")
            success = self.load(forced=True, DataFile=file, silent=True) # сначала пытаемся загрузить текстовый файл
            if success == False: # файл не текстовый, пробуем загрузить Word-файл
                self.popup(message=self.msg[208])
        if success == True:
            self.restart("soft")
            self.terPressed()
            Clock.schedule_once(lambda x: self.popup(message=self.msg[209]), 0.2)
        elif file == None:
            if success == False:
                self.importHelp = 1
                self.popup(message=self.msg[317], options=[self.button["yes"], self.button["no"]])
            else: # тоже неудачно, но другой вид ошибки
                self.popup(message=success)

    def checkOrientation(self, window=None, width=None, height=None):
        """ Выполняется при каждом масштабировании окна, проверяет ориентацию, и если она горизонтальная, адаптация интерфейса """

        if Window.size[0] <= Window.size[1]:
            self.orientation = "v"
            self.SR = 1
            self.globalFrame.padding = 0
            if self.orientation != self.orientationPrev: self.drawMainButtons()
            self.orientationPrev = self.orientation
            self.boxHeader.size_hint_y = self.titleSizeHintY
            self.titleBox.size_hint_y = self.tableSizeHintY
            self.boxFooter.size_hint_y = self.mainButtonsSizeHintY
            self.positive.size_hint_x=.6
            self.bottomButtons.size_hint_y = self.bottomButtonsSizeHintY
        else:
            self.orientation = "h"
            self.SR = 1 - self.horizontalShrinkRatio
            if self.theme == "morning" or self.theme == "purple": self.globalFrame.padding = (self.padding * 5, 0, 0, 0)
            if self.orientation != self.orientationPrev: self.drawMainButtons()
            self.orientationPrev = self.orientation
            self.boxHeader.size_hint_y = self.titleSizeHintY * 1.2
            self.titleBox.size_hint_y = self.tableSizeHintY * 1.2
            self.boxFooter.size_hint_y = .6
            self.positive.size_hint_x = .3
            self.bottomButtons.size_hint_y = self.bottomButtonsSizeHintY * 1.2
        self.pageTitle.text_size = (Window.size[0] * (.4 if self.settings[0][22] else .7), None)

        if self.desktop and not Devmode:
            try:
                with open("win.ini", "w") as file:
                    file.write(str(width)+"\n")
                    file.write(str(height)+"\n")
                    file.write(str(Window.top)+"\n")
                    file.write(str(Window.left))
            except: pass

    def drawMainButtons(self):
        """ Отрисовка кнопок меню по-разному в зависимости от ориентации экрана """

        while 1:
            if len(self.globalFrame.children) < 3: # если кнопок нет (при старте или смене ориентации), создаем их
                self.boxFooter = BoxLayout()
                self.buttonTer = MainMenuButton(text=self.msg[2]) # Участки
                self.buttonTer.bind(on_release=self.terPressed)
                self.buttonCon = MainMenuButton(text=self.msg[3]) # Контакты
                self.buttonCon.bind(on_release=self.conPressed)
                self.buttonRep = MainMenuButton(text=self.msg[4]) # Отчет
                self.buttonRep.bind(on_release=self.repPressed)
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
                        self.desktopModeFrame.size_hint_x = self.horizontalShrinkRatio
                        self.desktopModeFrame.add_widget(self.boxFooter)
                self.boxFooter.add_widget(self.buttonTer)
                self.boxFooter.add_widget(self.buttonCon)
                self.boxFooter.add_widget(self.buttonRep)
                break

            else: # если кнопки есть, удаляем их
                self.globalFrame.remove_widget(self.boxFooter)
                self.boxFooter.clear_widgets()

        self.updateMainMenuButtons()

    def buttonFlash(self, instance=None, timeout=None):
        if self.theme == "3D": return
        if timeout == None: timeout = RM.onClickFlash
        if instance != None:
            color = instance.color
            instance.color = self.titleColor if self.theme != "purple" else self.linkColor
        def __restoreColor(*args):
            if instance != None: instance.color = color
        Clock.schedule_once(__restoreColor, timeout)

    def fontScale(self):
        ''' Возвращает размер шрифта на Android:
        маленький = 0.85
        обычный = 1.0
        большой = 1.149
        очень крупный = 1.299
        огромный = 1.45 '''
        return mActivity.getResources().getConfiguration().fontScale if platform == 'android' else 1

    def restart(self, mode="hard"):
        """ Перезапуск либо перерисовка """
        self.checkOrientation(width=Window.size[0], height=Window.size[1])
        if mode == "soft": # простая перерисовка интерфейса
            self.setParameters(reload=True)
            self.interface.clear_widgets()
            self.setTheme()
            self.createInterface()
        else: # полная перезагрузка приложения
            if platform == "android":
                kvdroid.tools.restart_app()
            elif self.desktop:
                self.stop()
                from os import startfile
                startfile("main.py")
            else:
                self.stop() # просто выход

    def monthName(self, monthCode=None, monthNum=None):
        """ Returns names of current and last months in lower and upper cases """
        if monthCode != None:   month = monthCode
        elif monthNum != None:
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

        return curMonthUp, curMonthLow, lastMonthUp, lastMonthLow, lastMonthEn, curMonthRuShort, monthNum, lastTheoMonthNum, curTheoMonthNum

    # Работа с базой данных

    def initializeDB(self):
        """ Возвращает исходные значения houses, settings, resources """
        import time
        self.initialDBSize = 360 # минимальный размер файла для загрузки
        return [], \
               [
                   [1, 5, 0, 0, "и", "", "", 0, 1.5, 0, 0, 1, 1, 1, "", 1, 0, "", "5", "д", 0, "Default", 1],
                   # program settings
                   "",  # дата последнего обновления settings[1]
                   # report:                       settings[2]
                   [0.0,  # [0] hours         settings[2][0…]
                    0.0,  # [1] credit
                    0,  # [2] placements
                    0,  # [3] videos
                    0,  # [4] returns,
                    0,  # [5] studies,
                    0,  # [6] startTime
                    0,  # [7] endTime
                    0.0,  # [8] reportTime
                    0.0,  # [9] difTime
                    "",  # [10] note
                    0,  # [11] to remind submit report (0: already submitted) - не используется с 2.0
                    ""  # [12] отчет прошлого месяца
                    ],
                   time.strftime("%b", time.localtime()),  # month of last save: settings[3]
                   [None, None, None, None, None, None, None, None, None, None, None, None]  # service year: settings[4]
               ], \
               [
                   ["",  # resources[0][0] = notepad
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # resources[0][1] = флаги о подсказках
                    ],
                   # resources[0][1][0] - показана подсказка про уменьшение этажа (когда показана, ставим 1)
                   # resources[0][1][1] - показана подсказка про масштабирование подъезда
                   # resources[0][1][2] - показана подсказка про таймер
                   # resources[0][1][3] - показана подсказка про переключение вида подъезда
                   # resources[0][1][4] - показана подсказка про кнопку "нет дома"
                   # resources[0][1][5] - показана подсказка про первого интересующегося
                   # resources[0][1][6] - показана подсказка про процент обработки
                   # resources[0][1][7] - показана подсказка про экран первого посещения
                   # resources[0][1][8] - показана подсказка после уменьшения этажа
                   # resources[0][1][9] - показан запрос про месячную норму

                   [],  # standalone contacts   resources[1]
                   [],  # report log            resources[2]
               ]

    def load(self, DataFile=None, allowSave=True, forced=False, clipboard=None, silent=False):
        """ Loading houses and settings from JSON file """
        if Devmode: self.loadLanguages()
        if DataFile == None: DataFile = self.dataFile
        self.popupForm = ""
        if os.path.exists("temp"): os.remove("temp")
        ut.dprint(Devmode, "Загружаю буфер.")

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

        if clipboard != None:  # берем буфер обмена

            badURLError = self.msg[243]
            ut.dprint(Devmode, "Смотрим буфер обмена.")
            clipboard = str(clipboard).strip()

            if "drive.google.com" in clipboard: # получена ссылка на Google Drive
                try:
                    URL = "https://docs.google.com/uc?export=download"
                    id = clipboard[clipboard.index("/d/") + 3: clipboard.index("/view")]
                    session = requests.Session()
                    response = session.get(URL, params={'id': id}, stream=True)
                    with open("temp", "wb") as f:
                        for chunk in response.iter_content(32768):
                            if chunk: f.write(chunk)
                except: return badURLError

            else: # получен чистый текст
                try:
                    clipboard = clipboard[clipboard.index("[\"Rocket Ministry"):]
                    with open("temp", "w") as file: file.write(clipboard)
                    ut.dprint(Devmode, "Содержимое буфера обмена записано во временный файл.")
                except: return False

            try:
                with open("temp", "r") as file: buffer = json.load(file)
                ut.dprint(Devmode, "Буфер получен из буфера обмена.")
            except: return badURLError

        elif forced:  # импорт по запросу с конкретным файлом
            try:
                if ".doc" in DataFile:
                    try: import docx2txt
                    except:
                        check_call([executable, '-m', 'pip', 'install', 'docx2txt'])
                        check_call([executable, '-m', 'pip', 'install', 'plyer'])
                        import docx2txt
                    string = docx2txt.process(DataFile)
                    with open("temp", "w") as file: file.write(string)
                    with open("temp", "r") as file: buffer = json.load(file)
                else:
                    with open(DataFile, "r") as file: buffer = json.load(file)
                ut.dprint(Devmode, "Буфер получен из импортированного файла.")
            except:
                if not silent: self.popup(message=self.msg[244])
                return False

        else:  # обычная загрузка
            if os.path.exists(self.userPath + DataFile):
                size = os.path.getsize(self.userPath + DataFile)  # файл меньше заданного порога не загружаем
                if size < self.initialDBSize:
                    ut.dprint(Devmode, "Файл данных найден, но пустой. Пытаюсь восстановить резервную копию.")
                    if self.backupRestore(restoreWorking=True, allowSave=allowSave) == True:
                        ut.dprint(Devmode, "База восстановлена из резервной копии.")
                        if allowSave:
                            self.save(backup=True) # успешный результат с загрузкой копии и выход
                            ut.dprint(Devmode, "База сохранена с резервированием1.")
                        return True
                    else: ut.dprint(Devmode, "Не удалось восстановить непустую резервную копию (ее нет?).")
                else:
                    try:
                        with open(self.userPath + DataFile, "r") as file: buffer = json.load(file)
                    except:
                        ut.dprint(Devmode, "Файл данных найден, но он поврежден. Пытаюсь восстановить резервную копию.")
                        if self.backupRestore(restoreWorking=True, allowSave=allowSave) == True:
                            ut.dprint(Devmode, "База восстановлена из резервной копии.")
                            if allowSave:
                                self.save(backup=True)  # успешный результат с загрузкой копии и выход
                                ut.dprint(Devmode, "База сохранена с резервированием2.")
                            return True
                        else: ut.dprint(Devmode, "Не удалось восстановить непустую резервную копию (ее нет?).")
                    else: ut.dprint(Devmode, "Буфер получен из файла data.jsn в стандартном местоположении.")
            else:
                ut.dprint(Devmode, "Файл базы данных %s не найден, пытаюсь восстановить резервную копию." % DataFile)
                if self.backupRestore(restoreWorking=True, allowSave=allowSave) == True:
                    ut.dprint(Devmode, "База восстановлена из резервной копии.")
                    if allowSave:
                        self.save(backup=True)  # успешный результат с загрузкой копии и выход
                        ut.dprint(Devmode, "База сохранена с резервированием3.")
                    return True
                else: ut.dprint(Devmode, "Не удалось восстановить непустую резервную копию (ее нет?).")

        # Буфер получен, читаем из него

        try:
            self.save(backup=True)
            if len(buffer) == 0: ut.dprint(Devmode, "Создаю новую базу.")

            elif "Rocket Ministry application data file." in buffer[0]:
                singleTer = 1 if "Single territory export" in buffer[0] else 0
                ut.dprint(Devmode, "База определена, контрольная строка совпадает.")
                del buffer[0]
                result = self.loadOutput(buffer, singleTer) # ЗАГРУЗКА ИЗ БУФЕРА
                if not result:
                    ut.dprint(Devmode, "Ошибка импорта.")
                    self.backupRestore(restoreWorking=True, allowSave=allowSave)
                    ut.dprint(Devmode, "База восстановлена из резервной копии.")
                else:
                    ut.dprint(Devmode, "База успешно загружена.")
                    if allowSave:
                        self.save()  # успешный результат
                        ut.dprint(Devmode, "База сохранена без резервирования.")
                    return True
            else:
                ut.dprint(Devmode, "База получена, но контрольная строка не совпадает.")
                if clipboard == None and not forced:
                    ut.dprint(Devmode, "Восстанавливаю резервную копию.")
                    self.backupRestore(restoreWorking=True)
        except:
            ut.dprint(Devmode, "Ошибка проверки загруженного буфера.")
            return False

    def backupRestore(self, silent=True, allowSave=True, delete=False, restoreNumber=None, restoreWorking=False):
        """ Восстановление файла из резервной копии """

        try:
            files = [f for f in os.listdir(self.backupFolderLocation) if os.path.isfile(os.path.join(self.backupFolderLocation, f))]
        except:
            ut.dprint(Devmode, "Не найдена папка резервных копий.")
            return

        fileDates = []
        for i in range(len(files)):
            fileDates.append(str("{:%d.%m.%Y, %H:%M:%S}".format(
                datetime.datetime.strptime(time.ctime((os.path.getmtime(self.backupFolderLocation + files[i]))),
                                           "%a %b %d %H:%M:%S %Y"))))

        if restoreNumber != None:  # восстановление файла по номеру
            files.sort(reverse=True)
            fileDates.sort(reverse=True)
            try: self.load(forced=True, allowSave=allowSave, DataFile=self.backupFolderLocation + files[restoreNumber])
            except: return False
            else: return fileDates[restoreNumber]  # в случае успеха возвращает дату и время восстановленной копии

        elif restoreWorking:  # восстановление самой последней непустой копии
            files.sort(reverse=True)
            fileDates.sort(reverse=True)
            for i in range(len(files)):
                size = os.path.getsize(self.backupFolderLocation + files[i])
                if size > self.initialDBSize:
                    try:
                        self.load(forced=True, allowSave=allowSave, DataFile=self.backupFolderLocation + files[i])
                    except:
                        ut.dprint(Devmode, "Непустая резервная копия не найдена.")
                        return False
                    else:
                        ut.dprint(Devmode, "Успешно загружена последняя непустая резервная копия.")
                        if not silent: self.popup(message=self.msg[258] % fileDates[i])
                        return True

        # Если выбран режим удаления лишних копий

        elif delete == True:
            def __delete(*args):
                ut.dprint(Devmode, "Обрабатываем резервные копии.")
                limit = 10
                if len(files) > limit:  # лимит превышен, удаляем
                    extra = len(files) - limit
                    for i in range(extra):
                        os.remove(self.backupFolderLocation + files[i])
            _thread.start_new_thread(__delete, ("Thread-Delete", 0,))

    def save(self, backup=False, silent=True, export=False):
        """ Saving database to JSON file """

        def __save(*args):
            output = self.getOutput()

            # Сначала резервируем

            curTime = ut.getCurTime()
            if backup or (curTime - self.lastTimeBackedUp) > 300: # раз в 5 минут:
                if os.path.exists(self.userPath + self.dataFile):
                    if not os.path.exists(self.backupFolderLocation):
                        try: os.makedirs(self.backupFolderLocation)
                        except IOError:
                            if not silent: self.log(self.msg[248])
                            return
                    savedTime = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
                    with open(self.backupFolderLocation + "data_" + savedTime + ".jsn", "w") as newbkfile:
                        json.dump(output, newbkfile)
                        if not silent: self.popup(message=self.msg[249])
                        self.lastTimeBackedUp = curTime
                        ut.dprint(Devmode, "Выполнена резервная копия из self.save.")

            # Сохраняем

            while 1:
                try:
                    with open(self.userPath + self.dataFile, "w") as file: json.dump(output, file)
                except:
                    pass#ut.dprint(Devmode, "Ошибка записи в self.save!")
                else:
                    #ut.dprint(Devmode, "База успешно сохранена из self.save.")
                    if not silent: self.popup(message=self.msg[250])
                    break

            # Экспорт в файл на ПК, если найден файл sync.ini, где прописан путь

            if export and not Devmode and os.path.exists("sync.ini"):
                ut.dprint(Devmode, "Найден sync.ini, экспортируем.")
                try:
                    with open("sync.ini", encoding='utf-8', mode="r") as f: filename = f.read()
                    if ".doc" in filename:  # если в расширении файла есть .doc, создаем Word-файл
                        try:
                            from docx import Document
                        except:
                            from subprocess import check_call
                            from sys import executable
                            check_call([executable, '-m', 'pip', 'install', 'python-docx'])
                            from docx import Document
                        doc = Document()
                        doc.add_paragraph(str(json.dumps(output)))
                        doc.save(filename)
                    else:  # иначе пишем в простой текст
                        with open(filename, "w") as file: json.dump(output, file)
                except: ut.dprint(Devmode, "Ошибка записи в файл.")

        if export: __save()
        else: _thread.start_new_thread(__save, ("Thread-Save", .01,))

    def getOutput(self, ter=None):
        """ Возвращает строку со всеми данными программы, которые затем либо сохраняются локально, либо экспортируются"""
        if ter == None: # экспорт всей базы
            output = ["Rocket Ministry application data file. Do NOT edit manually!"] + [self.settings] + \
                     [[self.resources[0], [self.resources[1][i].export() for i in range(len(self.resources[1]))], self.resources[2]]]
            for house in self.houses:
                output.append(house.export())
        else: # экспорт одного участка
            output = ["Rocket Ministry application data file. Do NOT edit manually! Single territory export."] + [self.settings] + \
                     [[self.resources[0], [self.resources[1][i].export() for i in range(len(self.resources[1]))], self.resources[2]]]
            output.append(ter.export())
        return output

    def update(self):
        """ Проверяем новую версию и при наличии обновляем программу с GitHub """
        result = False

        if not self.desktop: return result  # мобильная версия не проверяет обновления
        else: ut.dprint(Devmode, "Проверяем обновления настольной версии.")

        try:  # подключаемся к GitHub
            for line in requests.get("https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/version"):
                newVersion = line.decode('utf-8').strip()
        except:
            ut.dprint(Devmode, "Не удалось подключиться к серверу.")
            return result
        else:  # успешно подключились, сохраняем сегодняшнюю дату последнего обновления (пока не используется)

            """Version = '2.09.005' # тестирование версий
            print(Version)
            newVersion = '2.10.000'
            print(newVersion)
            if newVersion > Version:
                print("new version found!")
                return True
            else:
                print("no new version found")
                return False"""

            ut.dprint(Devmode, "Версия на сайте: " + newVersion)
            today = str(datetime.datetime.strptime(time.strftime('%Y-%m-%d'), "%Y-%m-%d"))
            today = today[0: today.index(" ")]
            self.settings[1] = today
            self.save()

        if newVersion > Version:
            def __update(threadName, delay):
                ut.dprint(Devmode, "Найдена новая версия, скачиваем.")
                response = requests.get("https://github.com/antorix/Rocket-Ministry/archive/refs/heads/master.zip")
                import tempfile
                import zipfile
                file = tempfile.TemporaryFile()
                file.write(response.content)
                fzip = zipfile.ZipFile(file)
                fzip.extractall("")
                file.close()
                downloadedFolder = "Rocket-Ministry-master"
                for file_name in os.listdir(downloadedFolder):
                    source = downloadedFolder + "/" + file_name
                    destination = file_name
                    if os.path.isfile(source):
                        try: shutil.move(source, destination)
                        except: ut.dprint(Devmode, "Не удалось переместить файл %s." % source)
                os.remove(file)
                shutil.rmtree(downloadedFolder)
            _thread.start_new_thread(__update, ("Thread-Update", 0,))
            result = True
        else: ut.dprint(Devmode, "Обновлений нет.")

        return result

    def houseRetrieve(self, containers, housesNumber, h):
        """ Retrieves houses from JSON buffer into objects """
        for a in range(housesNumber):
            self.addHouse(containers, h[a][0], h[a][4])  # creating house and writing its title and type
            containers[a].porchesLayout = h[a][1]
            containers[a].date = h[a][2]
            containers[a].note = h[a][3]

            porchesNumber = len(h[a][5])  # counting porches
            for b in range(porchesNumber):
                containers[a].addPorch(h[a][5][b][0])  # creating porch and writing its title and layout
                containers[a].porches[b].status = h[a][5][b][1]
                containers[a].porches[b].flatsLayout = h[a][5][b][2]
                containers[a].porches[b].floor1 = h[a][5][b][3]
                containers[a].porches[b].note = h[a][5][b][4]
                containers[a].porches[b].type = h[a][5][b][5]

                flatsNumber = len(h[a][5][b][6])  # counting flats
                for c in range(flatsNumber):
                    containers[a].porches[b].flats.append(Flat())  # creating flat and writing its title
                    containers[a].porches[b].flats[c].title = h[a][5][b][6][c][0]
                    containers[a].porches[b].flats[c].note = h[a][5][b][6][c][1]
                    containers[a].porches[b].flats[c].number = h[a][5][b][6][c][2]
                    containers[a].porches[b].flats[c].status = h[a][5][b][6][c][3]
                    containers[a].porches[b].flats[c].phone = h[a][5][b][6][c][4]
                    containers[a].porches[b].flats[c].lastVisit = h[a][5][b][6][c][5]

                    visitNumber = len(h[a][5][b][6][c][6])  # counting visits
                    for d in range(visitNumber):
                        containers[a].porches[b].flats[c].records.append(Record())
                        containers[a].porches[b].flats[c].records[d].date = h[a][5][b][6][c][6][d][0]
                        containers[a].porches[b].flats[c].records[d].title = h[a][5][b][6][c][6][d][1]

    def loadOutput(self, buffer, singleTer):
        """ Загружает данные из буфера """
        try:
            if singleTer: # загрузка только одного участка, который добавляется к уже существующей базе
                a=len(self.houses)

                self.addHouse(self.houses, buffer[2][0], buffer[2][4])  # creating house and writing its title and type
                self.houses[a].porchesLayout = buffer[2][1]
                self.houses[a].date = buffer[2][2]
                self.houses[a].note = buffer[2][3]
                porchesNumber = len(buffer[2][5])  # counting porches
                for b in range(porchesNumber):
                    self.houses[a].addPorch(buffer[2][5][b][0])  # creating porch and writing its title and layout
                    self.houses[a].porches[b].status = buffer[2][5][b][1]
                    self.houses[a].porches[b].flatsLayout = buffer[2][5][b][2]
                    self.houses[a].porches[b].floor1 = buffer[2][5][b][3]
                    self.houses[a].porches[b].note = buffer[2][5][b][4]
                    self.houses[a].porches[b].type = buffer[2][5][b][5]
                    flatsNumber = len(buffer[2][5][b][6])  # counting flats
                    for c in range(flatsNumber):
                        self.houses[a].porches[b].flats.append(Flat())  # creating flat and writing its title
                        self.houses[a].porches[b].flats[c].title = buffer[2][5][b][6][c][0]
                        self.houses[a].porches[b].flats[c].note = buffer[2][5][b][6][c][1]
                        self.houses[a].porches[b].flats[c].number = buffer[2][5][b][6][c][2]
                        self.houses[a].porches[b].flats[c].status = buffer[2][5][b][6][c][3]
                        self.houses[a].porches[b].flats[c].phone = buffer[2][5][b][6][c][4]
                        self.houses[a].porches[b].flats[c].lastVisit = buffer[2][5][b][6][c][5]
                        visitNumber = len(buffer[2][5][b][6][c][6])  # counting visits
                        for d in range(visitNumber):
                            self.houses[a].porches[b].flats[c].records.append(Record())
                            self.houses[a].porches[b].flats[c].records[d].date = buffer[2][5][b][6][c][6][d][0]
                            self.houses[a].porches[b].flats[c].records[d].title = buffer[2][5][b][6][c][6][d][1]

            else: # загрузка и обновление базы целиком
                self.clearDB()

                self.settings[0] = buffer[0][0]  # загружаем настройки
                self.settings[1] = buffer[0][1]
                self.settings[2] = buffer[0][2]
                self.settings[3] = buffer[0][3]
                self.settings[4] = buffer[0][4]
                if len(self.settings[0]) == 22: self.settings[0].append(1)  # удалить в 2024

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

        except: return False
        else: return True

    def clearDB(self, silent=True):
        """ Очистка базы данных """
        self.houses.clear()
        self.settings.clear()
        self.resources.clear()
        self.settings[:] = self.initializeDB()[1][:]
        self.resources[:] = self.initializeDB()[2][:]
        if not silent: self.log(self.msg[242])

    def removeFiles(self, keepDatafile=False):
        """ Удаление базы данных и резервной папки"""
        if os.path.exists(self.userPath + self.dataFile) and not keepDatafile: os.remove(self.userPath + self.dataFile)
        if os.path.exists(self.backupFolderLocation): shutil.rmtree(self.backupFolderLocation)

    def share(self, silent=False, clipboard=False, email=False, folder=None, file=False, ter=None):
        """ Sharing database """
        output = self.getOutput(ter=ter)
        buffer = json.dumps(output)

        if clipboard: # копируем базу в буфер обмена - не используется
            try:
                s = str(buffer)
                Clipboard.copy(s)
            except: return

        elif email: # экспорт в сообщении
            plyer.email.send(subject=self.msg[251] if ter==None else ter.title, text=str(buffer), create_chooser=True)

        elif file: # экспорт в текстовый файл на компьютере
            try:
                from tkinter import filedialog
                folder = filedialog.askdirectory()
                filename = folder + f"/{self.msg[251] if ter==None else ter.title}.txt"
                with open(filename, "w") as file: json.dump(output, file)
            except:
                ut.dprint(Devmode, "Экспорт в файл не удался.")
                if folder != "": self.popup(message=self.msg[308])
            else: self.popup(message=self.msg[252] % filename)

        elif not Devmode and folder != None: # экспорт в файл
            try:
                with open(folder + "/data.jsn", "w") as file: json.dump(output, file)
            except: self.popup(message=self.msg[253])
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

if __name__ == "__main__": RM.run()
