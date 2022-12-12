#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import utils
from random import random
from copy import deepcopy
import app
from iconfonts import icon

class House(object):
    
    def __init__(self):
        self.title = ""
        self.porchesLayout = "а"
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        self.note = ""
        self.type = ""
        self.porches = []

    def getHouseStats(self):
        """ Finds how many interested (status==1) people in house """
        
        visited=0
        interest=0
        for a in range(len(self.porches)):
            for b in range(len(self.porches[a].flats)):
                if self.porches[a].flats[b].status != "": visited += 1
                if self.porches[a].flats[b].status == "1": interest += 1
        return visited, interest

    def getPorchType(self):
        """ Выдает тип своего подъезда [0],
            существительное типа контакта в родительном падеже единственного числа [1],
            в родительном падеже множественного числа [2],
            в творительном падеже единственного числа [3]
        напр. [1] "детали квартиры" [2] "сортировка домов" / [3] "информация о доме" """
        if self.type == "private":
            return "сегмент", "дома", "домов", "доме"
        elif self.type == "office":
            return "отдел", "сотрудника", "сотрудников", "сотруднике"
        elif self.type == "phone":
            return "диапазон", "номера", "номеров", "номере"
        else:
            return "подъезд", "квартиры", "квартир", "квартире"

    def showPorches(self):
        list = []
        try:
            self.porches.sort(key=lambda x: float(x.title), reverse=False) # сначала пытаемся сортировать по номеру
        except:
            self.porches.sort(key=lambda x: x.title, reverse=False) # если не получается, алфавитно

        for i in range(len(self.porches)):
            if self.porches[i].note != "":
                note = " •" + self.porches[i].note
            else:
                note = ""
            list.append("%s%s" % (self.porches[i].title, self.porches[i].getFlatsRange()))

        if self.type != "condo" and len(list) == 0:
            list.append("Создайте %s участка" % self.getPorchType()[0])

        if self.type == "condo":
            if len(list) == 0:
                number = 1
            else:
                last = len(self.porches)-1
                if utils.ifInt(self.porches[last].title)==True:
                    number = int(self.porches[last].title) + 1
                else:
                    number = None
            if number != None:
                list.append("[i]Создать подъезд %d[/i]" % number)

        return list
        
    def addPorch(self, input="", type="подъезд"):
        self.porches.append(self.Porch())
        self.porches[len(self.porches)-1].title = input.strip()
        self.porches[len(self.porches)-1].type = type

    def rename(self, input):
        self.title = input[3:].upper()

    def getProgress(self):
        """ Выдает показатель обработки участка в виде доли от 0 до 1 [0] и только обработанные квартиры [1]"""
        totalFlats = workedFlats = 0
        for porch in self.porches:
            for flat in porch.flats:
                totalFlats +=1
                if flat.getStatus()[1] != 4 and flat.getStatus()[1] != 5:
                    workedFlats += 1
        if totalFlats != 0:
            return workedFlats / totalFlats, workedFlats
        else:
            return 0, 0
        
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
        
        def __init__(self):
            self.title = ""
            self.status = "⚪⚪⚪" #"000"
            self.flatsLayout = "н"
            self.floor1 = 1 # number of first floor
            self.note = ""
            self.flats = [] # list of Flat instances, initially empty
            self.type = ""

        def showStatus(self):
            """ Выдает статус подъезда в виде графики или цифр в зависимости от режима вывода """
            if utils.settings[0][21]==False:
                return ""
            result="?"
            for i in range(len(utils.getPorchStatuses()[0])):
                if self.status==utils.getPorchStatuses()[0][i] or self.status==utils.getPorchStatuses()[1][i]:
                    if utils.settings[0][1]==False:
                        result=utils.getPorchStatuses()[0][i]
                    else:
                        result=utils.getPorchStatuses()[1][i]
            return result

        def shrinkFloor(self, selectedFlat):
            """ Определяет самую левую квартиру этажа и отправляет ее на удаление, чтобы уменьшить этаж"""

            all = self.showFlats()
            number = self.flats[selectedFlat].number
            for i in range(len(all)):
                if "}" in all[i] and all[i][all[i].index("}") + 1 :] == number:
                    index = i
                    break
            while 1:
                if "│" in all[index-1] or "." in all[index-1]:
                    number = all[index] [all[index].index("}") + 1:] # находим номер первой квартиры на этаже
                    break
                else:
                    index -= 1
            for i in range(len(self.flats)):
                if self.flats[i].number == number:
                    self.deleteFlat(i)
                    break

        def deleteFlat(self, ind):
            answer = True
            restore = False
            if self.flats[ind].status != "":  # проверка, что квартира не пустая
                if not "подъезд" in self.type: # выбрано удаление квартиры на обычном участке
                    answer = True
                else:  # удаление в подъезде с этажами
                    restore = True
            if answer == True:
                if "подъезд" in self.type:
                    result = self.shift(ind, restore=restore)
                    if result == "disableFloors":
                        utils.log("Удалено: %s" % self.flats[ind].title)
                        del self.flats[ind]
                        self.flatsLayout = "н"
                        self.sortFlats()
                else:
                    utils.log("Удалено: %s" % self.flats[ind].title)
                    del self.flats[ind]
                return "deleted"

        def getFlatsRange(self):
            """ Выдает диапазон квартир в подъезде многоквартирного дома"""
            range = ""
            if not "подъезд" in self.type:
                return range

            list = []

            for flat in self.flats:
                if not "." in flat.number:
                    try:
                        list.append(int(flat.number))
                    except:
                        return " –" # в подъезде есть нецифровые номера квартир, выходим
            list.sort()

            if len(list) == 1:
                range = " [i]%s–%s[/i]" % (list[0], list[0])
            elif len(list) > 1:
                last = len(list) - 1
                range = " [i]%s–%s[/i]" % (list[0], list[last])
            return range

        def shift(self, ind, restore=False):
            """ Сдвиг квартир вниз после удаления из этажной раскладки """

            deletedFlat = self.flats[ind]
            result = None

            flatsLayoutOriginal = self.flatsLayout  # определяем, нет ли в конце списка квартиры с записями, которую нельзя сдвигать
            self.flatsLayout = "о"
            self.sortFlats()
            for flat in self.flats:
                if not "." in flat.number:
                    number = flat.number
                    status = flat.status
                    break
            self.flatsLayout = flatsLayoutOriginal
            self.sortFlats()

            if status != "" and deletedFlat.number != number:
                app.MyApp.popup("В этом подъезде больше нельзя сокращать этажи, потому что последняя квартира с записью исчезнет! Но вы можете изменить диапазон квартир или кол-во этажей на экране «Квартиры».")

            else:
                if restore == True:
                    deletedFlatClone = deepcopy(deletedFlat)
                deletedFlat.hide()  # скрываем удаленную квартиру
                result = "deleted"

                self.flatsLayout = "н"
                self.sortFlats()  # временно сортируем по номеру

                porch2 = deepcopy(self.flats)  # создаем клон подъезда и очищаем исходный подъезд
                for flat in self.flats:
                    flat.wipe()

                for flat in self.flats:  # понижаем номера всех квартир
                    if float(flat.number) >= float(deletedFlat.number):
                        flat.number = str(float(flat.number) - 1)
                        if float(flat.number).is_integer() == True:
                            flat.number = flat.number[0: flat.number.index(".")]
                        if flat.getName() != "":
                            flat.title = flat.number + ", " + flat.getName()
                        else:
                            flat.title = flat.number

                for flat1 in self.flats:  # возвращаем исходные квартиры подъезда с данными
                    for flat2 in porch2:
                        if flat1.number == flat2.number and flat2.status != "":
                            flat1.clone(flat2)

                if restore == True:  # если была удалена квартира с содержимым, восстанавливаем ее на новом месте
                    for flat in self.flats:
                        if flat.number == deletedFlatClone.number:
                            flat.clone(deletedFlatClone)
                            break

                self.flatsLayout = flatsLayoutOriginal  # возвращаем исходную сортировку
                self.sortFlats()
            return result

        def getFirstAndLastNumbers(self):
            """Возвращает первый и последний номера в подъезде"""
            numbers = []
            for flat in self.flats:
                if utils.ifInt(flat.number) == True:
                    numbers.append(int(flat.number))
            numbers.sort()
            first = str(numbers[0])
            last = str(numbers[len(numbers) - 1])
            return first, last

        def sortFlats(self):
            """Сортировка квартир"""

            if self.flatsLayout == "н":  # numeric by number
                try:
                    self.flats.sort(key=lambda x: float(x.number))
                except:
                    self.flatsLayout = "а"
                    self.flats.sort(key=lambda x: x.title)

            elif self.flatsLayout == "о": # numeric by number reversed
                try:
                    self.flats.sort(key=lambda x: float(x.number), reverse=True)
                except:
                    self.flatsLayout = "а"
                    self.flats.sort(key=lambda x: x.title, reverse=True)

            elif self.flatsLayout=="с": # alphabetic by status character
                try:
                    self.flats.sort(key=lambda x: float(x.number))
                except:
                    self.flats.sort(key=lambda x: x.title, reverse=True)
                self.flats.sort(key=lambda x: x.getStatus()[1])

            elif self.flatsLayout=="т": # by phone number
                try:
                    self.flats.sort(key=lambda x: float(x.number))
                except:
                    self.flats.sort(key=lambda x: x.title, reverse=True)
                self.flats.sort(key=lambda x: x.phone, reverse=True)

            elif self.flatsLayout=="з": # by note
                self.flats.sort(key=lambda x: x.note, reverse=True)

            if utils.ifInt(self.flatsLayout)==True and "подъезд" in self.type: # сортировка по этажам
                self.flats.sort(key=lambda x: float(x.number))
                self.rows = int(self.flatsLayout)
                self.columns = int(len(self.flats) / self.rows)
                row=[i for i in range(self.rows)]
                i=0
                for r in range(self.rows):
                    row[r]=self.flats[i:i+self.columns]
                    i += self.columns
                row = row[::-1]
                del self.flats [:]
                for r in range(self.rows): self.flats += row[r]
                self.type = "подъезд%d" % self.rows

        def floors(self):
            """ Возвращает True, если в подъезде включен поэтажный вид """
            if utils.ifInt(self.flatsLayout)==True:
                return True
            else:
                return False

        def deleteHiddenFlats(self):
            """Удаление скрытых квартир"""
            while 1: # сначала удаляем скрытые квартиры
                for i in range(len(self.flats)):
                    if "." in self.flats[i].number:
                        del self.flats[i]
                        break
                else:
                    break

        def forceFloors(self, floors=None):
            """ Создаем любое заказанное количество этажей """
            self.deleteHiddenFlats()
            if floors==None:
                floors = self.rows
            self.flatsLayout="н"
            self.sortFlats()
            warn = False
            extraFlats = 0
            while 1:
                a = len(self.flats) / floors
                if not a.is_integer(): # собрать этажность не удалось, добавляем одну квартиру и пробуем снова
                    warn=True
                    try:
                        lastNumber = int( self.flats[ len(self.flats)-1 ].number) + 1
                    except:
                        return
                    self.addFlat("+%d" % lastNumber)
                    extraFlats += 1
                    continue
                else:
                    self.flatsLayout = floors
                    self.rows = floors
                    self.sortFlats()
                    if warn==True:
                        app.MyApp.popup(
                            message="\nЗапрошено нестандартное соотношение квартир и этажей. Пришлось добавить %d квартир(ы), которые вам нужно вручную удалить на нужных этажах. Для этого нажмите на кнопку [b]%s Уменьшить этаж[/b] в деталях квартиры на соответствующем этаже." % (extraFlats, icon("icon-resize-small-1"))
                        )
                    break

        def showFlats(self, countFloors=False):
            """ Вывод квартир для вида подъезда """

            def showListOfFlats():
                """Вывод подъезда в графическом режиме списком квартир (весь дом или один этаж)"""
                options=[]
                i = 0
                for flat in self.flats:  # выводим квартиры
                    if self.flats[i].addFlatTolist() != "":
                        options.append(self.flats[i].addFlatTolist())
                    i+=1
                if len(options) == 0:
                    if self.type=="отдел":
                        options.append("Создайте одного или нескольких сотрудников (используя нумерацию для удобства)")
                    elif self.type=="сегмент":
                        options.append("Создайте один или несколько домов")
                    elif self.type=="диапазон":
                        options.append("Создайте один или несколько телефонных номеров")
                    else:
                        options.append("Создайте квартиры подъезда")
                return options

            def showListOfFloors():
                """Вывод подъезда в подъездной раскладке"""
                options = []
                i = 0
                for r in range(self.rows):
                    options.append("%2d│ " % (self.rows - r + self.floor1 - 1))
                    flat = ""
                    for c in range(self.columns):
                        options.append("%s%s" % (self.flats[i].getStatus()[0], self.flats[i].number))
                        i += 1
                return options

            # Сначала сортируем квартиры

            self.sortFlats()
            if utils.ifInt(self.flatsLayout)==False: # если любая сортировка кроме поэтажной
                self.rows = 1
                self.columns = 999
            else:
                self.rows = int(self.flatsLayout)
                self.columns = int(len(self.flats) / self.rows)

            if countFloors==True:
                return self.rows

            # Вывод квартир - определяем режим, затем вызываем соответствующую функцию

            if utils.ifInt(self.flatsLayout)==True: # показываем подъезд в графическом режиме, если включена поэтажная сортировка
                result = showListOfFloors() # полным списком
                if result==None:
                    flats = showListOfFlats()
                    return flats # поэтажная сортировка не сработала, переключение на обычный список
                else:
                    return result
            else: # поэтажная сортировка отключена
                flats = showListOfFlats()
                return flats

        def getPreviouslyDeletedFlats(self):
            """ Выдает список квартир, ранее удаленных в этом подъезде"""
            numbers=[]
            for flat in reversed(self.flats): # удаляем дубли номеров
                if "." in flat.number:
                    numbers.append(flat.number[ 0 : flat.number.index(".") ])
            numbers = list(dict.fromkeys(numbers))
            mylist = ""
            if len(numbers)==0:
                mylist += " (но их нет)"
            else:
                mylist += " (например, "
                count = 0
                for number in numbers:
                    if count == 0:
                        mylist += "%s" % str(int(number) + 1)
                    else:
                        mylist += ", %s" % str(int(number) + 1)
                    count += 1
                mylist += ")"
            return mylist

        def addFlat(self, input, forcedDelete=False, silent=False, virtual=False):
            """Создает квартиру и возвращает ссылку на нее (экземпляр)"""
            input=input.strip()
            if input == "+":
                return None

            self.flats.append(self.Flat())
            last = len(self.flats)-1

            if virtual == False:
                self.flats[last].title = self.flats[last].number = input[1:].strip()  # ***
            else:
                self.flats[last].title = input[1:].strip()
                self.flats[last].number = "virtual"

            self.flats[last].updateStatus()
            
            createdFlat = last
            delete = False

            # Check if flat with such number already exists, it is deleted

            for i in range(last):
                if self.flats[i].number == self.flats[last].number: # flat with identical number (i) found
                    if self.flats[i].status=="":
                        delete=True # no tenant and no records, delete silently
                    else:
                        if forcedDelete==True:
                            delete=True
                        else:
                            if silent==False:
                                app.MyApp.popup("Контакт с таким номером уже существует, и в нем есть записи!")
                            del self.flats[last] # user reconsidered, delete the newly created empty flat
                            createdFlat = -1
                    break

            if delete==True: # deletion
                del self.flats[i]
                createdFlat = last-1

            return self.flats[createdFlat]
            
        def addFlats(self, input):
            """ Массовое создание квартир через дефис или пробел """
            s=f=0
            success=True
            floors=None

            if utils.ifInt(self.flatsLayout)==True:
                if utils.settings[0][1] == 1:
                    pass
                else:
                    pass
                answer = True
                if answer == True:
                    self.flatsLayout = "н"
                else:
                    return

            for i in range(len(input)):
                if input[i]=="-":
                    s=i
                if input[i]=="[":
                    f=i
                    floors = input[f+1:] # извлекаем кол-во этажей из цифры после [

            try:
                start = int(input[1:s])
            except:
                start=success=0 # ошибочный ввод из-за дефиса не в том месте

            try:
                if f==0:
                    end = int(input[s+1:])
                else:
                    end = int(input[s+1:f])
            except:
                end=success=0 # ошибочный ввод из-за дефиса не в том месте

            if success==True:
                for i in range(start, end+1):
                    self.addFlat("+%s" % (str(i)), silent=True)
                if f!=0:
                    self.flatsLayout = input[f+1:]
            else:
                success=0

            if "подъезд" in self.type:
                if floors == None:
                    floors = self.rows
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
            
            def __init__(self):
                self.title = "" # пример title: "20, Василий 30 лет"
                self.note = ""
                self.number = "virtual" # у адресных жильцов автоматически создается из первых символов title до запятой: "20";
                                        # у виртуальных автоматически присваивается "virtual", а обычного номера нет
                self.status = "" # automatically generated from last symbol of last record
                self.phone = ""
                self.meeting = ""
                self.records = [] # list of Record instances, initially empty

            def addFlatTolist(self, forceText=False):
                """ Функция для форматированного показа строки в режимах списков подъезда (полный и поэтажный) """
                line=""
                if not "." in self.number:
                    if self.phone=="":
                        phone=""
                    else:
                        phone = " т." + self.phone
                    line += "%s %s %s%s [i]%s[/i]" % (self.getStatus()[0],\
                                                self.number, self.getName(), phone, self.note)
                return line

            def getName(self):
                """ Генерирует имя жильца из заголовка квартиры """
                if "," in self.title:
                    return self.title[self.title.index(",") + 1:].strip()
                elif utils.ifInt(self.title)==True: # один номер
                    return ""
                elif utils.ifInt(self.title)==False and self.number=="virtual": # что-то помимо номера, но не запятая
                    return self.title
                else:
                    return ""

            def wipe(self, silent=True):
                """ Полностью очищает квартиру, оставляя только номер """
                del self.records[:]
                self.status = self.note = self.phone = self.meeting = ""
                self.title = self.number
                if self.title == "virtual":
                    self.title = ""

            def clone(self, flat2=None, title="", toStandalone=False):
                # Делает из себя копию полученной квартиры
                if toStandalone==False:
                    self.title = deepcopy(flat2.title)
                    self.number = deepcopy(flat2.number)
                    self.phone = deepcopy(flat2.phone)
                    self.meeting = deepcopy(flat2.meeting)
                    self.status = deepcopy(flat2.status)
                    self.note = deepcopy(flat2.note)
                    for record in flat2.records:
                        self.records.append(deepcopy(record))

                else: # создаем отдельный контакт
                    from utils import resources
                    if "," in self.title:
                        tempFlatNumber = self.title[0: self.title.index(",")]
                    else:
                        tempFlatNumber = self.title
                    resources[1].append(House())  # create house address
                    newVirtualHouse = resources[1][len(resources[1]) - 1]
                    newVirtualHouse.addPorch(type="virtual")  # create virtual porch ***
                    newVirtualHouse.porches[0].addFlat("+" + self.getName(), virtual=True)  # create flat
                    newContact = newVirtualHouse.porches[0].flats[0]
                    newContact.title = newContact.getName()
                    newVirtualHouse.title = "%s-%s" % (title, tempFlatNumber)
                    newVirtualHouse.type = "virtual"
                    newContact.records = deepcopy(self.records)
                    newContact.note = deepcopy(self.note)
                    newContact.status = deepcopy(self.status)
                    newContact.phone = deepcopy(self.phone)
                    newContact.meeting = deepcopy(self.meeting)
                    utils.log("Создан контакт %s" % newContact.getName())
                    return newContact.getName()

            def output(self):
                """ Для тестирования """
                print("*******************")
                print("КОНТАКТ «%s»" % self.title)
                print("-------------------")

            def showRecords(self):
                options = []
                if len(self.records)==0:
                    options.append("Создайте первое посещение")
                else:
                    for i in range(len(self.records)): # добавляем записи разговоров
                        options.append("%s\n[i]%s[/i]" % (self.records[i].date, self.records[i].title))
                return options

            def addRecord(self, input):
                self.records.insert(0, self.Record())
                self.records[0].title = input
                if len(self.records)==1 and self.status == "" and self.number != "virtual": # при первой записи ставим статус ?
                    self.status="?"

                date = time.strftime("%d", time.localtime())
                month = utils.monthName()[5]
                timeCur = time.strftime("%H:%M", time.localtime())
                
                self.records[0].date = "%s %s %s" % (date, month, timeCur)

                self.updateStatus()

                return len(self.records)-1

            def editRecord(self, ind, input):
                self.records[ind].title = input
                self.updateStatus()

            def deleteRecord(self, f):
                del self.records[f]
                self.updateStatus()
                utils.log("Запись посещения удалена")

            def updateStatus(self):
                """ Обновление статуса квартиры после любой операции """
                if len(self.records) == 0 and self.getName()=="" and self.note=="" and self.phone=="":  # нет никаких записей
                    self.status = ""
                elif self.status == "":
                    self.status = "?"

            def updateName(self, choice):
                """ Получаем только имя и соответственно обновляем заголовок """
                if choice=="":
                    self.title = self.number
                elif self.number=="virtual":
                    self.title=choice
                else:
                    self.title = self.number + ", " + choice
                self.updateStatus()

            def updateTitle(self, choice):
                """ Обновляем только заголовок (для немногоквартирных участков) """
                if choice == "":
                    return
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
                """ Делает квартиру невидимой, не меняя этажность подъезда """
                self.number = str ( float(self.number) + random() )
                #self.wipe()

            def getStatus(self):
                """ Возвращает иконку и сортировочное значение статуса на основе цифры """

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
                    value = 4
                elif self.status == "5":
                    string = "{5}"
                    value = 7
                else:
                    string = "{ }"
                    value = 5

                return string, value

            def export(self):
                return [
                    self.title,
                    self.note,
                    self.number,
                    self.status,
                    self.phone,
                    self.meeting,
                    [record.export() for record in self.records]
                ]

            class Record(object):

                def __init__(self):
                    self.date = ""
                    self.title = ""
                    
                def export(self):
                    return self.date, self.title
