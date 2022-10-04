#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
from icons import icon
import set
import io2
from io2 import houses
from io2 import settings
import house_op
import dialogs
import contacts
import reports

def terView():
    """ Список участков """

    choice=""
    while 1:
        if choice!="positive":
            choice = dialogs.dialogList( # display list of houses and options
                title = icon("globe") + " Участки " + reports.getTimerIcon(settings[2][6]), # houses sorting type, timer icon
                message = "Выберите участок или создайте новый:",
                options = house_op.showHouses(),
                form = "terView",
                negative = "Назад",
                positiveButton=True,
                positive = icon("plus"),
                neutralButton=True,
                neutral = icon("sort") + " Сорт."
            )
        if choice==None:
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
            type = house_op.pickHouseType()
            if type=="condo":
                houseIcon = icon("house")
                message = "Введите улицу и номер дома, например:\nПушкина, 30"
            elif type=="private":
                houseIcon = icon("cottage")
                message = "Введите улицу или район, например:\nЛесная\nЮжная часть"
            elif type=="office":
                houseIcon = icon("office")
                message = "Введите название либо адрес объекта, например:\nТЦ «Радуга»\nПушкина, 20"
            elif type=="phone":
                houseIcon = icon("phone")
                message = "Введите список номеров, например:\n231-000 – 231-499"
            else: continue

            choice2 = dialogs.dialogText(houseIcon + " Новый участок", message)
            if choice2 != None:
                house_op.addHouse(houses, choice2, type)
                io2.log("Создан участок «%s»" % choice2.upper())
        else:
            continue

def houseView(selectedHouse):
    """ Вид участка - список подъездов """

    house = houses[selectedHouse]

    choice = ""
    while 1:
        if house.note !="":
            noteTitle = icon("pin") + " " + house.note
        else:
            noteTitle=""
        if house.type=="condo":
            houseIcon = icon("house")
        elif house.type=="private":
            houseIcon = icon("cottage")
        elif house.type == "phone":
            houseIcon = icon("phone")
        else:
            houseIcon = icon("house")

        if choice!="positive":
            choice = dialogs.dialogList(
                form = "houseView",
                title = houseIcon + " %s ⇨ подъезды %s" % (house.title, reports.getTimerIcon(settings[2][6])),
                options = house.showPorches(),
                negative = "Назад",
                positiveButton=True,
                positive=icon("plus"),
                neutralButton=True,
                neutral = icon("preferences") + " Детали"
            )

        if choice==None:
            break
        elif choice=="neutral": # Детали
            if set.houseSettings(selectedHouse) == "deleted":
                break  # если участок был удален, выход на список участков
            else:
                continue
        elif choice=="positive": # новый подъезд
            choice=""
            if house.type=="private":
                message="Введите название сегмента внутри участка. Это может быть группа домов, часть квартала, четная/нечетная сторона и т.п. Можно создать единственный сегмент с любым названием и даже без него:"
                type="сегмент"
            elif house.type=="office":
                message="Введите название отдела внутри организации, например:\nКасса\nАдминистрация\nОхрана"
                type="отдел"
            elif house.type=="phone":
                message="Введите диапазон номеров, например:\n100–200"
                type="диапазон"
            else:
                message = "Введите заголовок подъезда (обычно просто номер):"
                type = "подъезд"
            if house.type == "condo":
                porchIcon = icon("porch")
            elif house.type == "private":
                porchIcon = icon("flag")
            elif house.type == "office":
                porchIcon = icon("door")
            elif house.type == "phone":
                porchIcon = icon("flag")
            else:
                porchIcon = icon("porch")

            choice2 = dialogs.dialogText(
                title= porchIcon + " Новый %s" % type,
                message = message
            )
            if choice2 != None:
                if choice2=="+":
                    choice2=choice2[1:]
                house.addPorch(choice2, type)
        elif set.ifInt(choice) == True:
            if "Создайте" in house.showPorches()[choice]:
                choice="positive"
            elif porchView(house, choice) == True:
                return True
        else:
            continue

def porchView(house, selectedPorch):
    """ Вид поодъезда, список квартир или этажей """

    porch = house.porches[selectedPorch]

    messageFailedInput = "Не сработало, попробуйте еще раз"

    def firstCallMenu(flat):
        """ Меню, которое выводится при первом заходе в квартиру"""

        options = [
            icon("interest")    + " Записать посещение",
            icon("reject")      + " Отказ и выход",
            icon("preferences") + " Детали",
        ]
        if settings[0][10]==1:
            options.insert(2, icon("rocket") + " Умная строка")

        choice = dialogs.dialogList(
            title="%s ⇨ первое посещение" % flat.number,
            options=options,
            form="firstCallMenu"
        )
        if choice == None:
            return
        elif set.ifInt(choice) == True:
            result = options[choice]
        else:
            return

        if "Отказ" in result:
            porch.autoreject(flat=flat)

        elif "Записать посещение" in result:
            name = dialogs.dialogText(
                title="%s Ввод данных о первом посещении" % icon("mic"),
                message="Имя и (или) описание человека:"
            )
            if name == None:
                return
            else:
                flat.updateName(name)
                record = dialogs.dialogText(
                    title="%s Ввод данных о первом посещении" % icon("mic"),
                    message="Описание разговора:"
                )
                if record==None:
                    return
                else:
                    flat.addRecord(record)
                    choices = dialogs.dialogChecklist(
                        title="%s Что еще сделать?" % icon("mic"),
                        message="Что сделать после посещения?",
                        negative="ОК",
                        options=[
                            icon("interest") + " Установить статус «интерес» ",
                            icon("placements") + " Добавить публикацию",
                            icon("video") + " Добавить видео",
                            icon("phone2") + " Записать телефон",
                            icon("appointment") + " Назначить встречу"
                        ]
                    )
                    if choices!=None:
                        checked = ' '.join(choices)
                        if "Установить статус" in checked:  # интерес
                            flat.updateStatus(status="1")
                        if "Добавить публикацию" in checked: # публикация
                            reports.report(choice="{{б}")
                        if "Добавить видео" in checked: # видео
                            reports.report(choice="{{в}")
                        if "Записать телефон" in checked:  # телефон
                            flat.phone = set.setPhone()
                        if "Назначить встречу" in checked:  # встреча
                            flat.meeting = set.setMeeting()
            io2.save()

        elif "Умная строка" in result:
            notebookOriginalSize = len(io2.resources[0])
            input = dialogs.dialogText(
                title="%s Умная строка" % icon("rocket"),
                neutralButton=True,
                neutral="%s Справка" % icon("help"),
                message="Нажмите на справку для подсказки по этой функции"
            )
            if input==None:
                pass
            elif input=="neutral":
                dialogs.dialogHelp(
                    title="%s Умная строка" % icon("rocket"),
                    message="«Умная строка» – это самый мощный и быстрый способ добавления нового посещения, а также работы с отчетами!\n\n" +
                            "Введите любой текст без точки, и он превратится в заметку квартиры.\n\n" + \
                            "Введите текст с точкой – будет записано имя жильца.\n\n" + \
                            "Если после точки продолжить ввод текста, к имени жильца будет добавлена запись посещения.\n\n" +
                            "Если в конце записи (как последний символ) поставить цифру от 0 до 4 – это статус квартиры. 0 – отказ, 1 – интерес, 2 – зеленый, 3 – фиолетовый, 4 – красный.\n\n" + \
                            "Если в тексте посещения использовать сочетания =б, =в, =ч, =п, =и – в отчет добавится соответственно публикация, видео, час времени, повторное посещение или изучение.\n\n"+ \
                            "(Для публикации также можно использовать =ж и =к).\n\n"+\
                            "Если последним символом строки будет плюс (+), то посещение не будет записано, но вместо этого вся строка занесется в блокнот (доступен с главной страницы приложения) с указанием адреса дома и номера квартиры.\n\n"+\
                            "Если вы не пользуетесь умной строкой, ее можно отключить в настройках.\n\n"+\
                            "Пример умной строки:\n\n"+\
                            "Алексей 30. Показали Отк. 21:4, оставили =буклет о Цар. 1"

                )
            elif "." not in input:
                flat.note = input
            elif "." in input:
                porch.addFlat(
                    input = "+%s, %s" % (flat.number, input), # классическая нотация
                    forceStatusUpdate=True
                )
            if notebookOriginalSize < len(io2.resources[0]): # определено добавление заметки, добавляем к ней адрес и время
                createdNote = io2.resources[0][ len(io2.resources[0])-1 ]
                date = time.strftime("%d", time.localtime())
                month = reports.monthName()[5]
                timeCur = time.strftime("%H:%M", time.localtime())
                io2.resources[0][ len(io2.resources[0])-1 ] = "%s-%s, %s %s %s: %s" % (house.title, flat.number, date, month, timeCur, createdNote)
            io2.save()

        elif "Детали" in result:
            if set.flatSettings(flat, house)=="deleted":
                return "deleted"

    def findFlatByNumber(number):
        """ Находит и открывает квартиру по номеру квартиры в данном подъезде,
        иначе возвращает False (кроме случая удаления этой квартиры) """
        number = number.strip()
        found=False
        try:
            if set.ifInt(number)!=True:
                number = number[0 : number.index(" ")].strip()
        except:
            pass
        else:
            for i in range(len(porch.flats)):
                if number == porch.flats[i].number:
                    found = True
                    if len(porch.flats[i].records)==0 and porch.flats[i].getName()=="" and porch.flats[i].status=="": # если первый раз, запускаем меню первого посещения
                        exit = firstCallMenu(porch.flats[i])
                        if exit == "deleted":
                            porch.deleteFlat(i)
                            return "deleted"
                        break
                    else: # если есть записи посещений, заходим напрямую
                        exit = flatView(porch.flats[i], house)
                        if exit == "deleted":
                            porch.deleteFlat(i)
                            return "deleted"
                        break
        return found

    default = choice = ""
    while 1: # Показываем весь подъезд

        if house.type=="condo":
            porchIcon = icon("porch")
        elif house.type=="private":
            porchIcon = icon("flag")
        elif house.type=="office":
            porchIcon = icon("door")
        elif house.type=="phone":
            porchIcon = icon("flag")

        # Режим сетки отключен, показываем стандартно

        if settings[0][5] == 0:

            if choice!="positive":
                options = porch.showFlats()
                choice = dialogs.dialogList(
                    title=porchIcon + "Подъезд %s %s" % (porch.title, reports.getTimerIcon(settings[2][6])),
                    options=options,
                    form="porchViewGUIList",
                    positiveButton=True,
                    positive=icon("plus"),
                    neutralButton=True,
                    neutral=icon("preferences") + " Детали"
                )
            if choice==None:
                return
            elif set.ifInt(choice)==True: # определяем, выбран этаж или квартира
                if "Создайте" in options[choice]:
                    choice = "positive"
                    continue
                elif options[choice][2]=="│": # этаж - выходим из этого цикла и переходим на один ниже
                    floorNumber = int(options[choice][0:2])
                    choice = ""
                else:
                    findFlatByNumber(options[choice]) # квартира - показываем и повторяем цикл
                    choice = ""
                    continue
            elif choice=="neutral":
                if set.porchSettings(house, selectedPorch) == "deleted":
                    return
                continue
            elif choice=="positive":
                addFlat = dialogs.dialogText(
                    title="Добавление новых квартир",
                    default=default,
                    message="Введите один номер (напр. 1) или диапазон через дефис (напр. 1–50)"
                )
                if addFlat == None:  # нажата Отмена/Назад
                    choice = default = ""
                    continue
                elif addFlat == "":  # нажат Ввод с пустой строкой - будет ошибка
                    io2.log(messageFailedInput)
                    continue
                elif set.ifInt(addFlat) == True and not "-" in addFlat: # добавляем одиночную квартиру, требуется целое число
                    porch.addFlat("+"+addFlat)
                    if settings[0][20] == True:
                        porch.autoFloorArrange()
                    choice = default = ""
                    continue
                elif set.ifInt(addFlat[0]) == True and "-" in addFlat: # массовое добавление квартир
                    porch.addFlats("+"+addFlat)
                    if settings[0][20] == True:
                        porch.autoFloorArrange()
                    choice = default = ""
                    continue
                else:
                    default=addFlat
                    io2.log(messageFailedInput)
                    continue
            else:
                continue

            while 1: # Показываем этаж

                rows = int(porch.flatsLayout)
                if (floorNumber - porch.floor1 + 1) < rows:
                    neutralButton = True
                    neutral = "↑"
                else:
                    neutralButton = False
                    neutral = ""
                if (floorNumber - porch.floor1 + 1) > 1:
                    positiveButton = True
                    positive = "↓"
                else:
                    positiveButton = False
                    positive = ""
                options = porch.showFlats(floor=floorNumber - porch.floor1 + 1)
                choice = dialogs.dialogList(
                    title="Этаж %d" % floorNumber,
                    options=options,
                    form="porchViewGUIOneFloor",
                    positiveButton=positiveButton,
                    positive=positive,
                    neutralButton=neutralButton,
                    neutral=neutral
                )
                if choice==None:
                    break
                elif set.ifInt(choice) == True: # находим и открываем квартиру
                    if findFlatByNumber(options[choice])=="deleted":
                        break
                elif choice == "neutral": # этаж вверх
                    floorNumber += 1
                elif choice =="positive": # этаж вниз
                    floorNumber -=1
                else:
                    continue

        # Режим сетки включен - классический вид

        else:
            choice = dialogs.dialogText(
                title=porchIcon + "%s (%s) %s %s" % (porch.title,
                                                     house.title,
                                                     house.note,
                                                     reports.getTimerIcon(settings[2][6])),
                message=porch.showFlats(),
                default=default,
                neutralButton=True,
                neutral=icon("preferences") + " Детали"
            )
            if choice==None:
                break
            elif len(choice)==0:
                continue
            elif choice == "neutral" or choice == "\\":
                choice = default = ""
                if set.porchSettings(house, selectedPorch) == "deleted":
                    return
            elif choice[0] == "+":  # добавление квартир(ы) разными способами
                if len(choice) == 1:
                    io2.log("Чтобы добавить квартиру, введите номер!")
                    choice = default = ""
                elif set.ifInt(choice[1]) == True and "-" not in choice:  # add new flat (and enter)
                    porch.addFlat(choice)
                    default = choice = ""
                elif set.ifInt(choice[1]) == True and "-" in choice:  # mass add flats
                    porch.addFlats(choice)
                    default = choice = ""
            elif choice[0] == "[":
                porch.flatsLayout = choice[1:]  # change flats layout
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
                        default = choice = ""
                        break
            elif choice[0] == "0" and len(choice) > 1:  # «автоотказ»
                porch.autoreject(choice=choice)
                default = choice = ""
            else:  # go to flat view
                result = findFlatByNumber(choice)
                if result=="deleted":
                    porch.deleteFlat(i)
                elif result==False:
                    io2.log(messageFailedInput)
                    default=choice

def flatView(flat, house, virtual=False):
    """ Flat screen, list (silhouette) """

    choice=""
    while 1:
        # Prepare title
        
        if flat.meeting!="":
            appointment = icon("appointment")
        else:
            appointment = ""

        if flat.phone != "":
            phone = icon("phone2")
        else:
            phone = ""

        if contacts.checkEmail(flat) != "zzz":
            email = icon("export")
        else:
            email = ""
        
        if flat.note!="":
            noteTitle = icon("pin") + " " + flat.note
        else:
            noteTitle=""

        neutral, options = flat.showRecords()

        # Display dialog

        if flat.number=="virtual": # прячем номера отдельных контактов
            number=""
        else:
            number=flat.number
        if choice!="positive":
            choice = dialogs.dialogList(
                title = icon("contact") + " %s %s %s %s %s %s %s  %s" % (
                    flat.getStatus()[0],
                    number,
                    flat.getName(),
                    appointment,
                    phone,
                    email,
                    noteTitle,
                    reports.getTimerIcon(settings[2][6])
                ),
                message = "Выберите запись посещения или создайте новую:",
                options=options,
                form="flatView",
                positiveButton=True,
                positive=icon("plus"),
                neutralButton = True,
                neutral = neutral
            )
        if choice==None:
            break

        elif choice=="neutral" or choice=="\\":
            if set.flatSettings(flat, house, virtual)=="deleted":
                return "deleted"

        elif choice=="positive": # new record
            default=settings[0][12]
            choice2 = dialogs.dialogText(
                title = icon("mic") + " Новая запись посещения",
                message = "О чем говорили?",
                default=default,
                largeText=True
            )
            if choice2 == None or choice2 == "":
                choice = ""
                continue
            else:
                flat.addRecord(choice2.strip())
                choice=""
                continue
                #if settings[0][9]==1:
                #    break
                #else:
                #    continue
        elif set.ifInt(choice)==True:
            if "Создайте" in options[choice]:
                choice = "positive"
                continue

            elif int(choice) <= len(flat.records): # edit record
                options2 = [icon("edit") + " Править", icon("cut") + " Удалить"]
                choice2 = dialogs.dialogList(
                    title=icon("mic") + " Запись посещения",
                    options=options2,
                    message="Что делать с записью?",
                    form="noteEdit"
                )
                if choice2==None:
                    continue
                else:
                    result2=options2[choice2]

                if "Править" in result2: # edit
                    choice3 = dialogs.dialogText(
                        icon("mic") + " Правка записи",
                        default = flat.records[int(choice)].title,
                        largeText=True
                    )
                    if choice3==None:
                        continue
                    else:
                        flat.editRecord(int(choice), choice3)

                elif "Удалить" in result2: # delete record
                    flat.deleteRecord(int(choice))

        else:
            continue

