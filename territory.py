#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
from icons import icon
import set
import io2
import homepage
import house_op
import house_cl
import dialogs
import reports

GridMode = 0
MessageOnAdd = "Введите один номер (напр. 1) или диапазон номеров через дефис или пробел (напр. 1 50):"

def terView(start=False):
    """ Список участков """

    if io2.Simplified==0: # отладочные действия
        #print(len(io2.resources[2]))
        #import tkinter as tk
        #form = tk.Toplevel()
        #porchView(io2.houses[0], 0)
        pass

    choice=""
    while 1:

        if choice!="positive":
            choice = dialogs.dialogList( # display list of houses and options
                title = icon("globe") + " Участки " + reports.getTimerIcon(io2.settings[2][6]), # houses sorting type, timer icon
                message = "Список участков:",
                options = house_op.showHouses(),
                form = "terView",
                negative = "Назад",
                positive = icon("plus", simplified=False),
                neutral = icon("sort", simplified=False) + " Сорт."
            )
        if homepage.menuProcess(choice) == True:
            continue
        elif choice==None:
            break
        elif set.ifInt(choice) == True:
            if "Создайте" in house_op.showHouses()[choice]:
                choice="positive"
            elif houseView(choice) == True: # выбор участка
                return True
        elif choice=="neutral": # сортировка
            house_op.terSort()
        elif choice=="positive": # новый участок
            choice=""
            created=False
            while created!=True:
                type = house_op.pickHouseType()
                if type==None:
                    break
                house_op.addHouse(io2.houses, "", type) # создается временный дом
                temphouse = io2.houses[len(io2.houses)-1]
                message = temphouse.getTipIcon()[0]
                while 1:
                    choice2 = dialogs.dialogText(
                        title = temphouse.getTipIcon()[1] + " Новый участок",
                        message = message,
                        height = 5
                    )
                    del io2.houses [len(io2.houses)-1] # удаляется временный дом
                    if choice2==None:
                        break
                    else:
                        for house in io2.houses:
                            if choice2.upper().strip() == house.title.upper().strip():
                                message = "Уже есть участок с таким названием, выберите другое!"
                                break
                        else:
                            house_op.addHouse(io2.houses, choice2, type)
                            io2.log("Создан участок «%s»" % choice2.upper())
                            io2.save()
                            created=True
                            break
        else:
            continue

def houseView(selectedHouse):
    """ Вид участка - список подъездов """

    house = io2.houses[selectedHouse]

    choice = ""
    while 1:
        if house.type=="condo":
            houseIcon = icon("house")
        elif house.type=="private":
            houseIcon = icon("cottage")
        elif house.type == "phone":
            houseIcon = icon("phone2")
        else:
            houseIcon = icon("house")

        if choice!="positive":

            choice = dialogs.dialogList(
                form = "houseView",
                title = houseIcon + " %s ⇨ %sы %s" % (house.title, house.getPorchType()[0], reports.getTimerIcon(io2.settings[2][6])),
                message = "Список %sов:" % house.getPorchType()[0],
                options = house.showPorches(),
                negative = "Назад",
                positive=icon("plus", simplified=False),
                neutral = icon("preferences", simplified=False) + " Детали"
            )

        if homepage.menuProcess(choice) == True:
            continue
        elif choice==None:
            break
        elif choice=="neutral": # Детали
            if set.houseSettings(selectedHouse) == "deleted":
                break  # если участок был удален, выход на список участков
            else:
                continue
        elif choice=="positive": # новый подъезд
            choice=""
            if house.type=="private":
                message="Введите название сегмента внутри участка. Это может быть улица, группа домов, часть квартала или просто номер:"
            elif house.type=="office":
                message="Введите название отдела внутри организации, например:\nТорговый зал\nАдминистрация\nОхрана"
            elif house.type=="phone":
                message="Введите диапазон номеров, например «100–199». Можно не создавать диапазоны и сделать единственный раздел под цифрой 1."
            else:
                message = "Введите заголовок подъезда (обычно просто номер):"
            while 1:
                choice2 = dialogs.dialogText(
                    title= house.getPorchType()[1] + " Новый %s" % house.getPorchType()[0],
                    message = message,
                    height = 5
                )
                if choice2 == None:
                    break
                else:
                    for porch in house.porches:
                        if choice2.strip() == porch.title:
                            message = "Уже есть %s с таким названием, выберите другое!" % house.getPorchType()[0]
                            break
                    else:
                        if choice2 == "+":
                            choice2 = choice2[1:]
                        house.addPorch(choice2, house.getPorchType()[0])
                        io2.save()
                        break

        elif set.ifInt(choice) == True:
            if "Создайте" in house.showPorches()[choice]:
                choice="positive"
            elif porchView(house, choice) == True:
                return True
        else:
            continue

def porchView(house, selectedPorch):
    """ Вид поодъезда - список квартир или этажей """

    global MessageOnAdd
    porch = house.porches[selectedPorch]
    messageFailedInput = "Не сработало, попробуйте еще раз."
    porchMessage = "\n"#"Список %s, сортировка %s:" % (house.getPorchType()[2], porch.getSortType())
    default = choice = ""
    selected=0
    if set.ifInt(porch.flatsLayout) == True:
        messageOnAdd = house_cl.MessageOfProhibitedFlatCreation1 % porch.getPreviouslyDeletedFlats()
    else:
        messageOnAdd = MessageOnAdd
    while 1: # Показываем весь подъезд
        # Стандартный списочный вид

        if io2.settings[0][1]==0 and io2.Mode!="text" and GridMode==0:

            if choice!="positive":
                options = porch.showFlats()
                choice = dialogs.dialogList(
                    title=house.getPorchType()[1] + " %s %s " % (porch.title, reports.getTimerIcon(io2.settings[2][6])),
                    message = porchMessage,
                    options=options,
                    form="porchViewGUIList",
                    positive=icon("plus", simplified=False),
                    neutral=icon("preferences", simplified=False) + " Детали",
                    selected=selected
                )
            menu = homepage.menuProcess(choice)
            if menu == "phone":
                set.porchSettings(house, selectedPorch, jumpToPhone=True)
            elif menu == True:
                continue
            elif choice==None:
                return
            elif set.ifInt(choice)==True: # определяем, выбран этаж или квартира
                if "Создайте" in options[choice]:
                    choice = "positive"
                    continue
                elif len(options[choice])>1 and options[choice][2]=="│": # выбран этаж - выходим из этого цикла и переходим на один ниже
                    floorNumber = int(options[choice][0:2])
                    for i in range(len(options)):
                        if str(floorNumber).strip() == options[i][0:2].strip():
                            selected = i
                            break
                    choice = ""
                else:
                    findFlatByNumber(house, porch, options[choice]) # квартира - показываем и повторяем цикл
                    for i in range(len(options)):
                        if options[i].strip() == options[choice].strip():
                            selected = i
                            break
                    choice = ""
                    continue
            elif choice=="neutral":
                if set.porchSettings(house, selectedPorch) == "deleted":
                    return
                continue
            elif choice=="positive":
                addFlat = dialogs.dialogText(
                    title=icon("plus", simplified=False) + " Добавление " + house.getPorchType()[2],
                    default=default,
                    message=messageOnAdd
                )
                if addFlat == None:  # нажата Отмена/Назад
                    choice = default = ""
                    messageOnAdd = MessageOnAdd
                    continue
                elif addFlat == "":  # нажат Ввод с пустой строкой - будет ошибка
                    io2.log(messageFailedInput)
                    continue
                elif not "-" in addFlat and not " " in addFlat: # добавляем одиночную квартиру, требуется целое число
                    if porch.type == "подъезд" and set.ifInt(addFlat) == False:
                        default = addFlat
                        messageOnAdd = "В многоквартирном доме номера квартир могут содержать только цифры!"
                        continue
                    else:
                        porch.addFlat("+"+addFlat)
                        choice = default = ""
                        io2.save()
                        messageOnAdd = MessageOnAdd
                        continue
                elif set.ifInt(addFlat[0]) == True and ("-" in addFlat or " " in addFlat): # массовое добавление квартир
                    porch.addFlats("+"+addFlat)
                    choice = default = ""
                    io2.save()
                    messageOnAdd = MessageOnAdd
                    continue
                else:
                    default=addFlat
                    messageOnAdd = messageFailedInput
                    continue
            else:
                continue

            selected2=0
            while 1: # Показываем этаж

                try:
                    rows = int(porch.flatsLayout)
                except:
                    porch.flatsLayout="н"
                    break
                if (floorNumber - porch.floor1 + 1) < rows:
                    neutral = "↑"
                else:
                    neutral = None
                if (floorNumber - porch.floor1 + 1) > 1:
                    positive = "↓"
                else:
                    positive = None
                options = porch.showFlats(floor=floorNumber - porch.floor1 + 1)
                choice = dialogs.dialogList(
                    title="Этаж %d" % floorNumber,
                    message = "Список этажей:",
                    options=options,
                    form="porchViewGUIOneFloor",
                    selected=selected2,
                    positive=positive,
                    neutral=neutral
                )
                if homepage.menuProcess(choice) == True:
                    continue
                elif choice=="x":
                    continue
                elif choice==None:
                    break
                elif choice == "neutral" and neutral != None: # этаж вверх
                    floorNumber += 1
                elif choice =="positive" and positive != None: # этаж вниз
                    floorNumber -=1
                elif choice!="neutral" and choice!="positive" and int(choice) == len(options)-1: # удаляем первую квартиру на этаже
                    try:
                        flatNumber = findFlatByNumber(house, porch, options[0], onlyGetNumber=True)
                        porch.deleteFlat(flatNumber)
                        io2.save()
                        selected2 = int(choice)-1
                    except:
                        continue
                elif set.ifInt(choice) == True: # находим и открываем квартиру
                    if findFlatByNumber(house, porch, options[choice])=="deleted":
                        break
                    for i in range(len(options)):
                        if options[i].strip() == options[choice].strip():
                            selected2 = i
                            break
                else:
                    continue

        # Текстовое представление подъезда

        else:
            choice = dialogs.dialogText(
                title=house.getPorchType()[1] + "%s (%s) %s %s" % (porch.title,
                                                     house.title,
                                                     house.note,
                                                     reports.getTimerIcon(io2.settings[2][6])),
                message = porch.showFlats(),
                form="porchText",
                height=porch.showFlats(countFloors=True),
                mono=True,
                default=default,
                neutral=icon("preferences", simplified=False) + " Детали"
            )
            if choice==None or choice=="":
                break
            elif len(choice)==0:
                continue
            elif choice == "neutral" or choice == "*":
                choice = default = ""
                if set.porchSettings(house, selectedPorch) == "deleted":
                    return
            elif choice[0] == "+":  # добавление квартир(ы) разными способами
                if len(choice) == 1:
                    io2.log("Чтобы добавить квартиру, введите + с номером!")
                    choice = default = ""
                elif set.ifInt(choice[1]) == True and "-" not in choice:  # add new flat (and enter)
                    porch.addFlat(choice)
                    io2.save()
                    default = choice = ""
                elif set.ifInt(choice[1]) == True and "-" in choice:  # mass add flats
                    porch.addFlats(choice)
                    io2.save()
                    default = choice = ""
            elif choice[0] == "[":
                if set.ifInt(choice[1:])==True:
                    porch.deleteHiddenFlats()
                    porch.forceFloors(floors=choice[1:])
                else:
                    porch.flatsLayout = choice[1:]
                default = choice = ""
                io2.save()
            elif choice[0] == "{":
                try:
                    house.porch.floor1 = int(choice[1:])  # change first floor
                    io2.save()
                    default = choice = ""
                except:
                    pass
            elif choice[0] == "-" or choice[0] == "–":  # delete flat
                for i in range(
                        len(porch.flats)):  # get selected flat's number
                    if choice[1:] == porch.flats[i].number:
                        porch.deleteFlat(i)
                        io2.save()
                        default = choice = ""
                        break
            elif choice[0] == "0" and len(choice) > 1:  # «автоотказ»
                porch.autoreject(choice=choice)
                io2.save()
                default = choice = ""
            else:  # go to flat view
                result = findFlatByNumber(house, porch, choice)
                if result=="deleted":
                    porch.deleteFlat(i)
                    io2.save()
                elif result==False:
                    io2.log(messageFailedInput)
                    default=choice

def flatView(flat, house=None, virtual=False, allowDelete=True):
    """ Вид квартиры - список записей посещения """

    choice = exit = ""
    while 1:
        # Prepare title

        if flat.meeting!="":
            appointment = " " + icon("appointment") + " "
        else:
            appointment = " "

        if flat.phone != "":
            phone = icon("phone") + " "
        else:
            phone = " "
        
        if flat.note!="":
            noteTitle = icon("pin") + flat.note + " "
        else:
            noteTitle=" "

        neutral, options = flat.showRecords()

        if io2.Mode=="easygui" and io2.settings[0][1]==0: # убираем иконки на ПК
            for i in range(len(options)):
                options[i] = options[i][2:]

        # Display dialog

        if flat.number=="virtual": # прячем номера отдельных контактов
            number=" "
        else:
            number=flat.number + " "
        if choice!="positive":
            choice = dialogs.dialogList(
                title = "%s %s%s%s%s%s %s" % (
                    flat.getStatus()[0],
                    number,
                    flat.getName(),
                    appointment,
                    phone,
                    noteTitle,
                    reports.getTimerIcon(io2.settings[2][6])
                ),
                message="Список посещений:",
                options=options,
                form="flatView",
                positive=icon("plus", simplified=False),
                neutral = neutral
            )
        if homepage.menuProcess(choice) == True:
            continue
        elif choice==None:
            break
        elif choice=="neutral" or choice=="*":
            if set.flatSettings(flat, house, virtual, allowDelete=allowDelete)=="deleted":
                exit = "deleted"
                break
        elif choice=="positive": # new record
            choice2 = dialogs.dialogText(
                title = icon("mic", simplified=False) + " Новая запись посещения",
                message = "О чем говорили?",
                largeText=True,
                positive="Сохранить",
                negative="Отмена"
            )
            if choice2 == None or choice2=="":
                choice = ""
                continue
            else:
                recordsInitial = len(flat.records)
                flat.addRecord(choice2.strip())
                io2.save()
                if len(flat.records) > recordsInitial:
                    exit = "createdRecord"
                choice=""
                continue
        elif set.ifInt(choice)==True:
            if "Создайте" in options[choice]:
                choice = "positive"
                continue
            elif int(choice) <= len(flat.records): # edit record
                options2 = [icon("edit") + " Править", icon("cut") + " Удалить"]
                if io2.Mode == "easygui" and io2.settings[0][1] == 0:  # убираем иконки на ПК
                    for i in range(len(options2)):
                        options2[i] = options2[i][2:]
                choice2 = dialogs.dialogList(
                    title=icon("mic", simplified=False) + " Запись посещения",
                    options=options2,
                    message="Что делать с записью?",
                    form="noteEdit"
                )
                if homepage.menuProcess(choice2)==True:
                    continue
                if choice2=="x":
                    continue
                elif choice2==None or choice2=="":
                    continue
                else:
                    result2=options2[choice2]

                if "Править" in result2: # edit
                    choice3 = dialogs.dialogText(
                        title=icon("mic", simplified=False) + " Правка записи",
                        default = flat.records[int(choice)].title,
                        largeText=True,
                        positive="Сохранить",
                        negative="Отмена"
                    )
                    if choice3==None:
                        continue
                    else:
                        flat.editRecord(int(choice), choice3)
                        io2.save()

                elif "Удалить" in result2: # delete record
                    flat.deleteRecord(int(choice))
                    io2.save()
            else:
                homepage.menuProcess(choice)
                continue
        else:
            continue
    return exit

def findFlatByNumber(house, porch, number, onlyGetNumber=False):
    """ Находит и открывает квартиру по номеру квартиры в данном подъезде,
    иначе возвращает False (кроме случая удаления этой квартиры) """

    def firstCallMenu(flat):
        """ Меню, которое выводится при первом заходе в квартиру"""

        options = [icon("mic", simplified=False) +            " Посещение"]
        if io2.settings[0][20]==1 and set.PhoneMode==True:
            if flat.phone!="":
                phone = ": %s" % flat.phone
            else:
                phone = ""
            options.append(icon("phone2", simplified=False) +  " Телефон%s" % phone)
        if io2.settings[0][13] == 1:
            options.append(icon("lock", simplified=False) +   " Нет дома")
        options.append(icon("reject", simplified=False) +     " Отказ")
        if io2.settings[0][18] == 1:
            options.append(icon("unreachable", simplified=False) + " Невозможно попасть")
        if io2.settings[0][10] == 1:
            options.append(icon("rocket", simplified=False) + " Умная строка")
        options.append(icon("preferences", simplified=False)+ " Детали")

        if (io2.Mode == "text" or io2.settings[0][1]) and flat.note!="":
            noteForConsole = "(%s)" % flat.note
        else:
            noteForConsole=""

        if io2.Mode == "easygui" and io2.settings[0][1] == 0:  # убираем иконки на ПК
            for i in range(len(options)):
                options[i] = options[i][2:]

        if set.PhoneMode==False or flat.phone!="":
            choice = dialogs.dialogList(
                title="%s ⇨ первое посещение %s" % (flat.number, noteForConsole),
                options=options,
                message="Список действий при первом посещении:",
                form="firstCallMenu"
            )
            if homepage.menuProcess(choice) == True:
                return
            elif choice == None:
                return
            elif set.ifInt(choice) == True:
                result = options[choice]
            else:
                return
        else:
            result="Телефон"

        if "Телефон" in result:
            if set.PhoneMode==True:
                flatNumber=flat.number
            else:
                flatNumber=""
            newPhone = set.setPhone(flat.phone, flatNumber=flatNumber)
            if newPhone != None:
                flat.phone = newPhone
                io2.save()

        elif "Отказ" in result:
            porch.autoreject(flat=flat)
            io2.save()

        elif "Нет дома" in result:
            porch.addFlat(input="+%s.нет дома" % flat.number, forceStatusUpdate=True)
            io2.save()

        elif "Невозможно попасть" in result:
            if flat.note != "":
                flat.note += "| 🚫"# + icon("unreachable", simplified=False)
            else:
                flat.note = " 🚫"# + icon("unreachable", simplified=False)
            io2.save()

        elif "Посещение" in result:
            name = dialogs.dialogText(
                title="%s Ввод данных о первом посещении" % icon("mic", simplified=False),
                message="Имя и (или) описание человека:"
            )
            if name == None:
                return
            else:
                flat.updateName(name, forceStatusUpdate=True)
                io2.save()
                record = dialogs.dialogText(
                    title="%s Ввод данных о первом посещении" % icon("mic", simplified=False),
                    message="Описание разговора:"
                )
                if record == None:
                    return
                else:
                    flat.addRecord(record)
                    io2.save()
                    if io2.Mode=="text" or io2.settings[0][1]==1:
                        flat.status = "1"
                        io2.save()
                    else:
                        options = [
                            icon("interest") + " Установить статус «интерес» ",
                            icon("placements") + " Добавить публикацию",
                            icon("video") + " Добавить видео",
                            icon("phone") + " Записать телефон",
                            icon("appointment") + " Назначить встречу"
                        ]
                        if io2.Mode == "easygui" and io2.settings[0][1] == 0:  # убираем иконки на ПК
                            for i in range(len(options)):
                                options[i] = options[i][2:]
                        choices = dialogs.dialogChecklist(
                        title="%s Что еще сделать?" % icon("mic", simplified=False),
                        message="Что сделать после посещения?",
                        options=options,
                        selected = [0, 0, 0, 0, 0],
                        negative=None
                    )
                        if choices != None:
                            checked = ' '.join(choices)
                            if "Установить статус" in checked:  # интерес
                                flat.status = "1"
                            if "Добавить публикацию" in checked:  # публикация
                                reports.report(choice="==б")
                            if "Добавить видео" in checked:  # видео
                                reports.report(choice="==в")
                            if "Записать телефон" in checked:  # телефон
                                flat.phone = set.setPhone()
                            if "Назначить встречу" in checked:  # встреча
                                flat.meeting = set.setMeeting()
                            io2.save()

        elif "Умная строка" in result:
            notebookOriginalSize = len(io2.resources[0])
            input = dialogs.dialogText(
                title="%s Умная строка" % icon("rocket"),
                neutral="%s Справка" % icon("info"),
                message="Нажмите на справку для подсказки по этой функции."
            )
            if input == None:
                pass
            elif input == "neutral" or input == "*" or input == "справка" or input == "help":
                dialogs.dialogInfo(
                    largeText=True,
                    title="%s Умная строка" % icon("rocket"),
                    message="«Умная строка» – это самый мощный и быстрый способ добавления нового посещения, а также ввода данных в отчет!\n\n" +
                            "Введите любой текст без точки, и он превратится в заметку квартиры.\n\n" + \
                            "Введите текст с точкой – это будет имя жильца.\n\n" + \
                            "Если после точки продолжить ввод текста, к имени жильца добавится запись посещения.\n\n" +
                            "Если в конце записи (как последний символ) поставить цифру от 0 до 5 – это статус квартиры. 0 – отказ, 1 – интерес, 2 – зеленый, 3 – фиолетовый, 4 – коричневый, 5 – красный.\n\n" + \
                            "Если в тексте посещения использовать сочетания =б, =в, =ч, =п, =и – в отчет добавится соответственно публикация, видео, час времени, повторное посещение или изучение.\n\n" + \
                            "(Для публикации также можно использовать =ж и =к).\n\n" + \
                            "Если последним символом строки будет плюс (+), то посещение не будет записано, но вместо этого вся строка занесется в блокнот (доступен с главной страницы приложения) с указанием адреса дома и номера квартиры.\n\n" + \
                            "Примеры умной строки:\n\n" + \
                            "Алексей 30. Показали Отк. 21:4, оставили =буклет о Цар. 2\n\n" + \
                            "ж60. Показали =в, начато =и 1\n\n" + \
                            "Если вы не пользуетесь умной строкой, ее можно отключить в настройках.",
                    positive="OK",
                    negative=None
                )
            elif "." not in input:
                flat.note = input
            elif "." in input:
                porch.addFlat(
                    input="+%s, %s" % (flat.number, input),  # классическая нотация
                    forceStatusUpdate=True
                )
            if notebookOriginalSize < len(
                    io2.resources[0]):  # определено добавление заметки, добавляем к ней адрес и время
                createdNote = io2.resources[0][len(io2.resources[0]) - 1]
                date = time.strftime("%d", time.localtime())
                month = reports.monthName()[5]
                timeCur = time.strftime("%H:%M", time.localtime())
                io2.resources[0][len(io2.resources[0]) - 1] = "%s-%s, %s %s %s: %s" % (
                house.title, flat.number, date, month, timeCur, createdNote)
            io2.save()

        elif "Детали" in result:
            if set.flatSettings(flat, house, allowDelete=allowDelete) == "deleted":
                return "deleted"

        elif "Удалить" in result:
            return "deleted"

    if set.ifInt(porch.flatsLayout)==True:
        allowDelete = False
    else:
        allowDelete = True

    found=False
    """try:
        if set.ifInt(number)!=True:
            number = number[0 : number.index(" ")].strip()
    except:
        pass
    else:"""

    try:
        number = number[0: number.index(" ")].strip()
    except:
        number = number.strip()
    for i in range(len(porch.flats)):
        if number == porch.flats[i].number:
            found = True
            if onlyGetNumber == True:
                return i # только возвращаем номер и выходим

            if len(porch.flats[i].records)==0 and porch.flats[i].getName()=="": # если первый раз, запускаем меню первого посещения
                exit = firstCallMenu(porch.flats[i])
                if exit == "deleted":
                    porch.deleteFlat(i)
                    io2.save()
                    return "deleted"
                break
            else: # если есть записи посещений, заходим напрямую
                exit = flatView(porch.flats[i], house, allowDelete=allowDelete)
                if exit == "deleted":
                    porch.deleteFlat(i)
                    io2.save()
                    return "deleted"
                elif exit == "createdRecord" and io2.settings[0][9]==0:
                    set.flatSettings(porch.flats[i], jumpToStatus=True)
                break
    return found