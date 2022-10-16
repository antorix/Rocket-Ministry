#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import io2
import dialogs
import set
import reports
import house_op
from icons import icon
import homepage

class House():
    
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
                if self.porches[a].flats[b].status !=  "": visited += 1
                if self.porches[a].flats[b].status == "1": interest += 1
        return [visited, interest]
    
    def getTipIcon(self):
        """ Выдает подсказку [0] и иконку [1] при создании участка или изменении названия """

        if self.type == "private":
            return "Введите название участка – улицу, квартал и т. д., например:\nЛесная\nЛесная/Радужная/Сосновая", icon("cottage")
        elif self.type == "office":
            return "Введите название либо адрес объекта, например:\nТЦ «Радуга»\nПушкина, 20", icon("office")
        elif self.type == "phone":
            return "Введите название участка – список номеров или произвольно, например:\n353-2000 – 353-2200\nМои телефоны", icon("phone2")
        else:
            return "Введите улицу и номер дома, например:\nПушкина, 30", icon("house")

    def getPorchType(self):
        """ Выдает название типа подъезда [0], иконку подъезда [1] и существительное
        типа контакта в родительном падеже [2] исходя из типа дома """
        if self.type == "private":
            return "сегмент", icon("flag"), "квартир" # напр. "сортировка квартир"
        elif self.type == "office":
            return "отдел", icon("door"), "сотрудников"
        elif self.type == "phone":
            return "диапазон", icon("phone3"), "номеров"
        else:
            return "подъезд", icon("porch"), "квартир"

    def sortPorches(self):
        if self.porchesLayout=="н": # numeric by number
            self.porches.sort(key=lambda x: float(x.title), reverse=False)
        if self.porchesLayout=="а": # alphabetic by title
            self.porches.sort(key=lambda x: x.title, reverse=False)

    def showPorches(self):
        list = []

        self.sortPorches()

        for i in range(len(self.porches)):
            if self.porches[i].note != "":
                note = " %s %s " % (icon("pin"), self.porches[i].note)
            else:
                note = ""
            list.append(self.getPorchType()[1] + " %s %s %s" % (self.porches[i].title, self.porches[i].showStatus(), note))

        if len(list) == 0:
            list.append("Создайте %s внутри участка" % self.getPorchType()[0])

        if io2.settings[0][1]==True or io2.Mode == "text":
            list.append("%s Новый %s" % (icon("plus"), self.getPorchType()[0]))  # создание нового участка
            list.append(icon("preferences") + " Детали")

        return list
        
    def addPorch(self, input="", type="condo"):
        self.porches.append(self.Porch()) 
        self.porches[len(self.porches)-1].title = input.strip()
        self.porches[len(self.porches)-1].type = type
        
    def rename(self, input):
        self.title = input[3:].upper()
        
    def export(self):
        return [
            self.title,
            self.porchesLayout,
            self.date,
            self.note,
            self.type,
            [self.porches[i].export() for i in range(len(self.porches))]
        ]
            
    class Porch():
        
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
            if io2.settings[0][21]==False:
                return ""
            result="?"
            for i in range(len(house_op.getPorchStatuses()[0])):
                if self.status==house_op.getPorchStatuses()[0][i] or self.status==house_op.getPorchStatuses()[1][i]:
                    if io2.settings[0][1]==False and io2.Mode=="sl4a":
                        result=house_op.getPorchStatuses()[0][i]
                    else:
                        result=house_op.getPorchStatuses()[1][i]
            return result

        def deleteFlat(self, ind):
            answer=True
            if len(self.flats[ind].records)!=0 or self.flats[ind].getName()!="": # проверка, что квартира не пустая
                answer = dialogs.dialogConfirm(
                    title=icon(
                        "cut") + " Удалить «%s»?" % self.flats[ind].number,
                        message="Внутри есть данные! Вы уверены?"
                    )
            if answer==True:
                io2.log("«%s» удален" % self.flats[ind].number)
                del self.flats[ind]
                return "deleted"

        def sortFlats(self, forceNumerical=False):
            if self.flatsLayout == "н" or forceNumerical==True: # numeric by number
                self.flats.sort(key=lambda x: float(x.number))
            elif self.flatsLayout == "о": # numeric by number reversed
                self.flats.sort(key=lambda x: float(x.number), reverse=True)
            elif self.flatsLayout=="а": # numeric-alphabetic by number
                self.flats.sort(key=lambda x: x.getNumericalNumber())
            elif self.flatsLayout=="с": # alphabetic by status character
                self.flats.sort(key=lambda x: float(x.number))
                self.flats.sort(key=lambda x: x.getStatus()[1])
            elif self.flatsLayout=="т": # by phone number
                self.flats.sort(key=lambda x: float(x.number))
                self.flats.sort(key=lambda x: x.phone, reverse=True)
            elif set.ifInt(self.flatsLayout)==True: # floors view with reversed numeric order
                #try:
                a = len(self.flats)/int(self.flatsLayout)
                if not a.is_integer(): return 1 # stop=1
                self.flats.sort(key=lambda x: float(x.getNumericalNumber()))

                # Reversing order in rows to straight
                rows = int(self.flatsLayout)
                columns = int(len(self.flats) / rows)

                row=[i for i in range(rows)]
                i=0
                for r in range(rows):
                    row[r]=self.flats[i:i+columns]
                    i += columns
                row = row[::-1]
                del self.flats [:]
                for r in range(rows): self.flats += row[r]
                #except:
                #    print("error")
                #    self.flatsLayout="н"
            return 0

        def autoFloorArrange(self, silent=False):
            """ Подсчитывает и предлагает разбивку по этажам после каждого создания квартир, возвращает список раскладок """
            fnumber = len(self.flats)
            options = []
            if fnumber>=6:
                for i in range(2, fnumber + 1):
                    if fnumber % i == 0:
                        options.append(str(i))
                if len(options)>1:
                    del options[len(options)-1]
                    if silent==False: # в тихом режиме только считаем, но не показываем список
                        choice=dialogs.dialogList(
                            title="Сколько этажей в подъезде?",
                            positive=None,
                            negative="Этажи не нужны",
                            options=options)
                        if homepage.menuProcess(choice) == True:
                            return
                        if choice==None:
                            return
                        elif set.ifInt(choice) == True:
                            result = int(options[int(choice)])
                            self.flatsLayout = result
                            self.sortFlats()
            if len(options)>1:
                return True
            else:
                return False

        def showFlats(self, floor=0):
            """ Вывод квартир для вида подъезда """

            def showGrid():
                """ Вывод подъезда в классическом текстовом окне """
                message = "«+1» – добавить новую квартиру.\n«+1-50» – добавить диапазон.\n«*» – детали.\n\n"
                i = 0
                for r in range(rows):
                    if self.flatsLayout!="н" and self.flatsLayout!="а" and self.flatsLayout!="с": # display floor number
                        message += "%2d│ " % (rows-r+self.floor1-1)
                    for c in range(columns):
                        if c < len(self.flats):
                            message += "%3s%s " % (self.flats[i].number, self.flats[i].getStatus(forceText=forceText)[0])
                            i+=1
                    if rows-r != 1:
                        message += "\n"
                return message

            def showListOfFlats(floor=None):
                """Вывод подъезда в графическом режиме списком квартир """

                options=[]
                i = 0
                if floor==None: # выводится весь подъезд
                    for flat in self.flats:  # выводим квартиры
                        options.append(self.flats[i].addFlatTolist())
                        i+=1
                    if len(options) == 0:
                        if self.type=="отдел":
                            options.append("Создайте одного или нескольких сотрудников (с нумерацией)")
                        elif self.type=="сегмент":
                            options.append("Создайте один или несколько домов (квартир)")
                        elif self.type=="диапазон":
                            options.append("Создайте один или несколько телефонных номеров")
                        else:
                            options.append("Создайте одну или несколько квартир")
                    if io2.settings[0][1]==True or io2.Mode == "text":
                        options.append(icon("plus") + " Добавить")
                        options.append(icon("preferences") + " Детали")
                elif floor>0: # выводится список запрошенного этажа
                    rows = int(self.flatsLayout)
                    columns = int(len(self.flats) / rows)
                    for r in range(rows):
                        for c in range(columns):
                            if rows-r == floor:
                                options.append(self.flats[i].addFlatTolist())
                            i += 1
                    if io2.settings[0][1] == True or io2.Mode == "text":
                        if floor<rows:
                            options.append(icon("up") + " Вверх")
                        if floor>1:
                            options.append(icon("down") + " Вниз")

                return options

            def showListOfFloors():
                """Вывод подъезда в графическом режиме в виде списка этажей (автоматически, если включена поэтажная сортировка)"""
                options=[]
                i=0
                try:
                    for r in range(rows):
                        floorNumber = "%2d│ " % (rows - r + self.floor1 - 1)
                        flat = ""
                        for c in range(columns):
                            flat += "%s%s " % (self.flats[i].number, self.flats[i].getStatus(forceText=forceText)[0])
                            i += 1
                        options.append(floorNumber + flat)
                    if io2.settings[0][1] == True or io2.Mode == "text":  # добавляем кнопки
                        options.append(icon("plus") + " Добавить")
                        options.append(icon("preferences") + " Детали")
                except:
                    return None
                return options

            # Сначала сортируем квартиры

            stop = self.sortFlats()
            if set.ifInt(self.flatsLayout)==False: # если любая сортировка кроме поэтажной
                rows = 1
                columns = 999
            elif stop==1: # включена поэтажная сортировка
                io2.log("Ошибка поэтажной раскладки, измените кол-во квартир или этажей")
                rows = 1
                columns = 999
                try:
                    self.flatsLayout = "н"
                    self.sortFlats()
                except:
                    self.flatsLayout = "а"
                    self.sortFlats()
            else:
                rows = int(self.flatsLayout)
                columns = int(len(self.flats) / rows)

            # Вывод квартир - определяем режим, затем вызываем соответствующую функцию

            forceText = False

            if io2.settings[0][1]==1 or io2.Mode=="text":  # показываем подъезд в режиме сетки
                return showGrid()

            if floor!=0: # если получен конкретный этаж, функция вывода списка всего подъезда выдает список только одного этажа
                return showListOfFlats(floor=floor)

            if set.ifInt(self.flatsLayout)==True: # показываем подъезд в графическом режиме, если включена поэтажная сортировка
                result = showListOfFloors() # полным списком
                if result==None:
                    flats = showListOfFlats()
                    return flats # поэтажная сортировка не сработала, переключение на обычный список
                else:
                    return result
            else: # поэтажная сортировка отключена
                flats = showListOfFlats()
                return flats
        
        def addFlat(self, input, silent=False, virtual=False, forceStatusUpdate=False):
            """Создает квартиру и возвращает ссылку на нее (объект)"""
            input=input.strip()
            self.flats.append(self.Flat())
            last = len(self.flats)-1 # number of modified flat is the last appended
            record = self.flats[last].setFlat(input, virtual)
            createdFlat = last
            delete = False

            if record != "": # add record at once (if any)
                self.flats[last].addRecord(record, forceStatusUpdate=forceStatusUpdate)
            
            # Check if flat with such number already exists, it is deleted
            
            for i in range(last): 
                if self.flats[i].number == self.flats[last].number: # flat with identical number (i) found
                    if len(self.flats[i].records)==0 and self.flats[i].status=="" and self.flats[i].getName()=="":
                        delete=True # no tenant and no records, delete silently
                    else:
                        if silent==True:
                            delete=True
                        elif dialogs.dialogConfirm(
                            icon("cut") + " Перезапись «%s»" % self.flats[i].number, "Внутри есть данные! Точно перезаписать?"
                        ) == True:
                            delete=True # user approves deletion
                        else:
                            del self.flats[last] # user reconsidered, delete the newly created empty flat
                            createdFlat = -1
                    break
                    
            if delete==True: # deletion
                del self.flats[i]
                createdFlat = last-1

            return self.flats[createdFlat]
            
        def addFlats(self, input):
            s=f=0
            success=True

            for i in range(len(input)):
                if input[i]=="-":
                    s=i
                if input[i]=="/" or input[i]=="[":
                    f=i
            try:
                start = int(input[1:s])
            except:
                io2.log("Ошибка массового ввода, проверьте номера")
                start=success=0 # ошибочный ввод из-за дефиса не в том месте

            try:
                if f==0:
                    end = int(input[s+1:])
                else:
                    end = int(input[s+1:f])
            except:
                end=success=0 # ошибочный ввод из-за дефиса не в том месте

            if success==True and start<=end:
                for i in range(start, end+1):
                    self.addFlat("+%s" % (str(i)))
                if f!=0:
                    self.flatsLayout = input[f+1:]
            else:
                io2.log("Ошибка массового ввода, проверьте номера")
                success=0

            return success

        def autoreject(self, flat=None, choice=None):
            """ Автоматическое проставление отказа в существующую или новую квартиру"""

            flatFound = False
            if flat==None: # квартира не дана - ищем по номеру (choice)
                for i in range(len(self.flats)):  # ищем номер квартиры
                    if choice[1:] == self.flats[i].number:
                        selectedFlat = i
                        flatFound = True
                        flat = self.flats[selectedFlat]
                        break
            else:
                flatFound = True

            if flatFound==True:
                if len(flat.records) == 0 and flat.getName()=="":
                    flat.addRecord("отказ")  # квартира пустая - ставим автоотказ сразу
                    flat.status="0"
                elif dialogs.dialogConfirm(  # в квартире есть данные - переспрашиваем
                    icon("cut") + " Перезапись «%s»" % flat.number,
                    "Внутри есть данные! Точно перезаписать?"
                    ) == True:
                    flat.addRecord("отказ")
                    flat.status = "0"
                    io2.log("В «%s» добавлен отказ" % flat.title)
            else: # квартира с указанным номером не найдена - создаем новую
                self.addFlat(choice)
                self.flats[len(self.flats) - 1].addRecord("отказ")
                self.flats[len(self.flats) - 1].status = "0"
                io2.log("Создан номер «%s» с отказом" % self.flats[len(self.flats) - 1].title)

        def export(self):
            return [
                self.title,
                self.status,
                self.flatsLayout,
                self.floor1,
                self.note,
                self.type,
                [self.flats[i].export() for i in range(len(self.flats))]
            ]

        class Flat():
            
            def __init__(self):
                self.title = "" # пример title: "20, Василий 30 лет"
                self.note = ""
                self.number = "virtual" # у адресных жильцов автоматически создается из первых символов title до запятой: "20";
                                        # у виртуальных автоматически присваивается "virtual", а обычного номера нет
                self.status = "" # automatically generated from last symbol of last record
                self.phone = ""
                self.meeting = ""
                self.records = [] # list of Record instances, initially empty

            def getNumericalNumber(self):
                """ Преобразование номера из строки в число, возвращает 0, если не удалось"""
                output=""                
                for char in self.number:
                    if set.ifInt(char)==True:
                        output+=char
                try:
                    return int(output)
                except:
                    return 0

            def addFlatTolist(self, forceText=False):
                """ Функция для форматированного показа строки в режимах списков подъезда (полный и поэтажный) """
                line=""
                if self.note != "":
                    note = ("%s%s" % (icon("pin"), self.note))
                else:
                    note = ""
                line += " %s %s %s %s" % (self.number, self.getStatus(forceText=forceText)[0], self.getName(), note)
                return line

            def getName(self):
                """ Генерирует имя жильца из заголовка квартиры """
                if "," in self.title:
                    return self.title[self.title.index(",") + 1:].strip()
                elif set.ifInt(self.title)==True: # один номер
                    return ""
                elif set.ifInt(self.title)==False: # что-то помимо номера, но не запятая
                    return self.title
                else:
                    return ""

            def showRecords(self):
                options = []

                if len(self.records)==0:
                    options.append("Создайте первую запись в журнале посещений")
                else:
                    for i in range(len(self.records)): # добавляем записи разговоров
                        options.append(icon("mic") + " %s: %s" % (self.records[i].date, self.records[i].title))

                if io2.Mode == "text" or io2.settings[0][1]==True:
                    options.append(icon("plus") + " Новое посещение")  # positive button on Android

                if io2.Mode == "text":
                    options.append(icon("preferences") + " Детали")  # positive button on Android
                neutral = icon("preferences") + " Детали"

                return neutral, options

            def addRecord(self, input, forceStatusUpdate=False):
                self.records.insert(0, self.Record())
                self.records[0].title = input
                if len(self.records)==1: # если создана первая запись, то вне зависимости от настроек ставится временный статус "?"
                    self.status="?"
                
                date = time.strftime("%d", time.localtime())
                month = reports.monthName()[5]
                timeCur = time.strftime("%H:%M", time.localtime())
                
                self.records[0].date = "%s %s %s" % (date, month, timeCur)

                if io2.settings[0][9]==1 or forceStatusUpdate==True:
                    if len(input)>0:
                        self.status = self.records[0].title[len(input)-1] # status set to last character of last record
                    else:
                        self.status=""

                if len(self.records)>1 and io2.settings[0][7]==1:
                    reports.report("==п")

                return len(self.records)-1

            def editRecord(self, f, input):
                self.records[f].title = input
                if io2.settings[0][9]==1:
                    self.updateStatus()

            def deleteRecord(self, f):
                del self.records[f]
                if io2.settings[0][9]==1 or (len(self.records)==0 and self.getName()==""):
                    self.updateStatus()
                io2.log("Запись посещения удалена")

            def updateStatus(self):
                """ Обновление статуса квартиры после любой операции """

                if len(self.records) == 0 and self.getName()=="":  # нет ни жильца, ни записей
                    self.status = ""
                elif len(self.records) > 0:  # есть хотя бы одна запись
                    if self.records[0].title=="": # если запись пустая
                        self.status = "?"
                    else:
                        self.status = self.records[0].title[ len(self.records[0].title) - 1 ]  # статус по последней букве последней записи
                else:
                    self.status = "?"

            def updateName(self, choice, forceStatusUpdate=False):
                """ Получаем только имя и соответственно обновляем заголовок"""
                if choice=="":
                    self.title = self.number
                elif self.number=="virtual":
                    self.title=choice
                else:
                    self.title = self.number + ", " + choice
                if io2.settings[0][9]==1 or forceStatusUpdate==True or (len(self.records)==0 and self.getName()==""):
                    self.updateStatus()

            def setFlat(self, input="", virtual=False):
                """ Определяет и прописывает корректные title и number, возвращает запись посещения.
                 Используется при любом создании и правке любых контактов, адресных и отдельных!
                 Input подается начиная с "+". """
                result=""
                if "." in input and not "," in input: # lone "."
                    if virtual==False:
                        self.title = self.number = input[1:input.index(".")].strip()
                    result = input[input.index(".")+1:].strip()
                elif not "." in input and not "," in input: # ввод одного номера или контакта
                    if virtual==False:
                        self.title = self.number = input[1:].strip()
                    else:
                        self.title = input[1:].strip()
                elif "," in input and not "." in input:
                    self.number = input[1:input.index(",")]
                    self.title = input[1:].strip()
                elif "." in input and "," in input: # if both present in right order, correctly return record
                    if input.index(",") < input.index("."): # , .
                        self.title = input[1:input.index(".")].strip()
                        self.number = input[1:input.index(",")]
                    else: # . ,
                        if virtual==False:
                            self.title = self.number = input[1:input.index(".")].strip()
                    result = input[input.index(".")+1:].strip()

                if virtual==True:
                    self.number = "virtual"

                self.updateStatus()
                return result

            def getStatus(self, forceText=False):
                """ Возвращает иконку и сортировочное значение статуса на основе цифры """

                if self.status == "0":
                    string = icon("reject", forceText)
                    value = 7 # value нужно для сортировки квартир по статусу
                elif self.status == "1":
                    string = icon("interest", forceText)
                    value = 0
                elif self.status == "2":
                    string = icon("green", forceText)
                    value = 1
                elif self.status == "3":
                    string = icon("purple", forceText)
                    value = 2
                elif self.status == "4":
                    string = icon("brown", forceText)
                    value = 3
                elif self.status == "5":
                    string = icon("danger", forceText)
                    value = 6
                elif self.status == "":
                    string = icon("void", forceText)
                    value = 5
                else:
                    string = icon("question", forceText)
                    value = 4

                return string, value

            def copyToStandalone(self, title):
                """ Копирование квартиры в отдельный контакт """
                from io2 import resources
                from house_cl import House
                from copy import deepcopy
                if "," in self.title:
                    tempFlatNumber = self.title[0: self.title.index(",")]
                else:
                    tempFlatNumber = self.title
                resources[1].append(House())  # create house address
                newVirtualHouse = resources[1][len(resources[1]) - 1]
                newVirtualHouse.addPorch("virtual")  # create virtual porch
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
                return newContact.getName()

            def export(self):
                return [
                    self.title,
                    self.note,
                    self.number,
                    self.status,
                    self.phone,
                    self.meeting,
                    [self.records[i].export() for i in range(len(self.records))]
                ]

            class Record():

                def __init__(self):
                    self.date = ""
                    self.title = ""
                    
                def showContent(self):
                    message = self.title
                    if self.note != "":
                        message += "\n\n%s %s" % (self.note, icon("pin"))
                    return
                    message
                    
                def export(self):
                    return [
                        self.date,
                        self.title
                    ]
