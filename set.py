#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import io2
from io2 import houses, settings
import dialogs
import webbrowser
import time
import house_op
from icons import icon

def houseSettings(selectedHouse):
    """ House settings """

    house=houses[selectedHouse]

    while 1:
        options = [
            icon("baloon") + " Название участка",
            icon("pin") + " Заметка участка",
            icon("date") + " Дата взятия",
            house.getTipIcon()[1] + " Изменить тип",
            icon("map") + " Маршрут",
            icon("cut") + " Удалить участок",
        ]
        choice = dialogs.dialogList(
            title = house.title,
            message = "Выберите настройку:",
            options = options,
            form="houseSettings",
            negative = "Назад")

        if choice==None:
            break
        else:
            result = options[choice]

        if "Название" in result: # edit house
        
            choice2 = dialogs.dialogText(
                title=icon("baloon") + " Название участка",
                message=house.getTipIcon()[0],
                default = house.title
            )
            if choice2 != None:
                house.title = choice2.upper()
                io2.save()
                
        elif "Заметка" in result: # house note
            choice2 = dialogs.dialogText(
                icon("pin") + " Заметка участка",
                default=house.note
            )
            if choice2 != None:
                house.note = choice2
                io2.save()
        
        elif "Удалить" in result: # delete house
            interest=[] # считаем все квартиры со статусом 1
            for p in range(len(house.porches)):
                for f in range(len(house.porches[p].flats)):
                    if house.porches[p].flats[f].status=="1":
                        interest.append([p, f])
            message="Перед удалением участка его желательно сдать."
            if len(interest)>0:
                message += " Также в участке есть %d интересующихся. Они будут скопированы в отдельные контакты." % len(interest)
            message += "\n\nУдаляем?"
            answer=dialogs.dialogConfirm(
                title = icon("cut") + "Удаление %s" % house.title,
                message=message
            )
            if answer==True:
                if len(interest)>0:
                    for int in interest:
                        flat = house.porches[int[0]].flats[int[1]]
                        flat.copyToStandalone(house.title)
                del houses[selectedHouse]
                io2.save()
                return "deleted"
                
        elif "Дата взятия" in result: # edit date
            year = house.date[0:4]
            month = (house.date[5:7])
            day = (house.date[8:10])
            date = dialogs.dialogPickDate(title = icon("date") + " Дата взятия участка",
                    year=year, month=month, day=day
            )
            if date!=None:
                house.date = date
                io2.save()

        elif "Изменить тип" in result:
            house_op.pickHouseType(house) # house type
            io2.save()
                
        elif "Маршрут" in result:
            map(house.title) # map
                
    return "" # exit

def porchSettings(house, selectedPorch):
    """ Porch settings """

    porch = house.porches[selectedPorch]
    
    while 1:
        options = [
            icon("baloon") + " Название %sа" % porch.type,
            icon("sort") + " Сортировка " + house.getPorchType()[2],
            icon("pin") + " Заметка %sа" % porch.type,
            icon("intercom") + " Режим домофона",
            icon("map") + " Маршрут",
            icon("cut") + " Удалить %s" % porch.type,
        ]

        if settings[0][21]==1:
            options.insert(2, icon("status") + " Статус обработки")

        if ifInt(porch.flatsLayout)==True:
            options.insert(2, icon("porch") + " Номер первого этажа")
        
        choice = dialogs.dialogList(
            title = porch.title,
            message = "Выберите настройку:",
            form = "porchSettings",
            options = options)

        if choice == None:
            break
        else:
            result = options[choice]
        
        if "Название" in result: # edit porch title
        
            if house.type=="condo":
                message = "Введите заголовок подъезда (обычно просто номер):"
            elif house.type=="private":
                message = "Введите название сегмента внутри участка. Это может быть группа домов, часть квартала, четная/нечетная сторона и т.п. Можно создать единственный сегмент с любым названием и даже без него:"
            elif house.type=="office":
                message = "Введите название офиса или организации, например:\nПродуктовый магазин\nОфис 15"
            elif house.type=="phone":
                message = "Введите название участка или диапазон номеров, например:\n231-100 – 213-500"
        
            choice2 = dialogs.dialogText(
                title = icon("baloon") + " Название %sа" % porch.type,
                message=message,
                default = porch.title
            )
            if choice2 != None:
                porch.title = choice2.strip()
                io2.save()
            else:
                continue

        elif "Статус" in result:  # set status of porch
            while 1:
                for i in range(len(house_op.getPorchStatuses()[0])):
                    if porch.status==house_op.getPorchStatuses()[0][i] or\
                       porch.status==house_op.getPorchStatuses()[1][i]:
                        selected=i

                if io2.settings[0][1]==False and io2.Mode=="sl4a":
                    options=house_op.getPorchStatuses()[0]
                else:
                    options = house_op.getPorchStatuses()[1]

                choice2 = dialogs.dialogRadio(
                    title=icon("sort") + " Статус " + porch.status,
                    message="Выберите статус:",
                    options=options,
                    selected=selected
                )
                if choice2 != None:
                    porch.status = choice2
                    io2.save()
                break

        elif "Сортировка" in result: # flats sorting
            if ifInt(porch.flatsLayout)==True:
                floors = ": " + str(porch.flatsLayout)
            else: floors=""

            options=[
                "По этажам",
                "По номеру",
                "По номеру обратная",
                "По статусу",
                "По телефону"
            ]
            if ifInt(porch.flatsLayout)==True:
                selected=0
            elif porch.flatsLayout=="н":
                selected=1
            elif porch.flatsLayout=="о":
                selected=2
            elif porch.flatsLayout=="с":
                selected=3
            elif porch.flatsLayout=="т":
                selected=4
            else:
                selected=0

            choice3 = dialogs.dialogRadio(
                title=icon("sort") + " Сортировка " + house.getPorchType()[2],
                message="Выберите тип сортировки:",
                options=options,
                selected=selected
            )
            if choice3==None:
                continue
            elif choice3 == "По этажам":
                if porch.autoFloorArrange(silent=True) == False:
                    dialogs.dialogInfo("Сортировка", "Поэтажное представление невозможно при данном числе квартир!")
                else:
                    porch.autoFloorArrange()
                    io2.save()
            elif choice3 == "По номеру":
                porch.flatsLayout="н"
                io2.save()
            elif choice3 == "По номеру обратная":
                porch.flatsLayout="о"
                io2.save()
            elif choice3=="По статусу":
                porch.flatsLayout="с"
                io2.save()
            elif choice3=="По телефону":
                porch.flatsLayout="т"
                io2.save()
            
        elif "Заметка" in result: # porch note
            choice2 = dialogs.dialogText(
                icon("pin") + " Заметка %sа" % porch.type,
                default=porch.note
            )
            if choice2 != None:
                porch.note = choice2
                io2.save()
                
        elif "Удалить" in result: # delete porch
            answer = dialogs.dialogConfirm(
                title = icon("cut") + " Удалить " + porch.title,
                message = "Вы уверены?"
            )
            if answer== True:
                del house.porches[selectedPorch]
                io2.save()
                return "deleted"

        elif "Номер первого этажа" in result:
            message="Укажите этаж, с которого будет начинаться нумерация этажей:"
            if ifInt(porch.floor1)==False:
                default="1"
            else:
                default = str(porch.floor1)
            while 1:
                number=dialogs.dialogText(
                    title=icon("porch") + " Первый этаж",
                    default=default,
                    message=message
                )
                if number==None:
                    break
                elif ifInt(number)==True and int(number)>0:
                    porch.floor1=int(number)
                    io2.save()
                    break
                else:
                    message="Требуется целое положительное число:"
                    default=number

        elif "Режим домофона" in result:
            list=[]
            porch.sortFlats(forceNumerical=True) # временно сортируем по номеру
            for flat in porch.flats:
                list.append(flat.addFlatTolist())

            dialogs.dialogChecklist(
                title=icon("intercom") + " Режим домофона",
                options=list,
                positive=False,
                negative="Назад"
            )
            porch.sortFlats() # возвращаем исходную сортировку

        elif "Маршрут" in result:
            map(house.title) # map

def flatSettings(flat, house, virtual=False):

    while 1:

        options = [
            icon("baloon") + " Имя",
            flat.getStatus()[0] + " Статус",
            icon("phone") + " Телефон",
            icon("pin") + " Заметка",
            icon("appointment") + " Встреча"
        ]
        if virtual==True:
            options.insert(1, icon("house") + " Адрес")
        else:
            options.append(icon("star") + " В отдельный контакт")
        
        phone = flat.phone
        if io2.Mode=="sl4a":
            if phone != "":
                if virtual==False:
                    options.insert(3, icon("phone") + " Набрать номер")
                else:
                    options.insert(4, icon("smartphone") + " Набрать номер")
                #options.insert(5, icon("phone") + " SMS")
                #options.append(icon("mail") + " Сообщение")
        options.append(icon("map") + " Маршрут")
        options.append(icon("cut") + " Удалить")

        if flat.number == "virtual":  # прячем номера отдельных контактов
            number = ""
        else:
            number = flat.number

        choice = dialogs.dialogList(
            title = "%s %s" % (number, flat.getName()),
            message = "Выберите действие:",
            form = "flatSettings",
            options = options)

        if choice == None:
            break
        else:
            result = options[choice]

        if "Имя" in result: # edit
            mychoice = dialogs.dialogText(
                icon("baloon") + " Контакт",
                message="Введите имя контакта:",
                default = flat.getName()
            )
            if mychoice==None:
                continue
            elif len(mychoice)==0:
                if virtual==True:
                    continue
                else:
                    flat.updateName("")
            elif len(mychoice)>0 and mychoice[0]!="," and mychoice[0]!="."\
                    and mychoice!="!" and mychoice[0]!="+": # правка name
                flat.updateName(mychoice)
                io2.save()
                continue

        elif "Статус" in result:
            if flat.status=="0":
                selected=0
            elif flat.status=="1":
                selected=1
            elif flat.status=="2":
                selected=2
            elif flat.status=="3":
                selected=3
            elif flat.status=="4":
                selected=4
            elif flat.status=="5":
                selected=5
            else:
                selected = 0

            options=[
                icon("reject") + " Отказ",
                icon("interest") + " Интерес",
                icon("green") + " Зеленый",
                icon("purple") + " Фиолетовый",
                icon("brown") + " Коричневый",
                icon("danger") + " Красный"
            ]
            status = dialogs.dialogRadio(title="Статус контакта", options=options, selected=selected)
            if status!=None:
                for i in range(len(options)):
                    if status == options[i]:
                        flat.status=str(i)
                io2.save()

        elif "Телефон" in result:
            newPhone = setPhone(flat.phone)
            if newPhone!=None:
                flat.phone = newPhone
                io2.save()

        elif "Встреча" in result:
            flat.meeting = setMeeting(flat.meeting)
            if flat.meeting!="":
                io2.log("Назначена встреча на %s!" % house_op.shortenDate(flat.meeting))
                io2.save()
                
        elif "Заметка" in result:
            choice2 = dialogs.dialogText(
                icon("pin") + " Заметка контакта",
                default = flat.note
            )
            if choice2 != None:
                flat.note = choice2
                io2.save()
                
        elif "Удалить" in result:
            return "deleted" # if "deleted" from settings menu, exit to porch
                
        elif "Адрес" in result: # edit address of standalone contact
            while 1:
                address = dialogs.dialogText(
                    title=icon("house") + " Адрес",
                    message = "Введите полный адрес:",
                    default = house.title
                )
                if address != None:
                    house.title = address.upper()
                    io2.save()
                break
                
        elif "В отдельный контакт" in result:
            name = flat.copyToStandalone(house.title)
            io2.save()
            io2.log("Создан отдельный контакт %s" % name)
            
        elif "Email" in result: # Email
            if io2.Mode=="sl4a":
                try:
                    from androidhelper import Android
                    Android().sendEmail(email,"","",attachmentUri=None) # email on Android
                except IOError:
                    io2.log("Не удалось отправить письмо!")
                else:
                    io2.consoleReturn()
            else:
                webbrowser.open("mailto:%s" % email) # email on Windows/Linux

        elif "Набрать номер" in result: # phone call, Android-only
            if io2.Mode=="sl4a":
                from androidhelper import Android
                myphone=Android()
                myphone.setClipboard(phone)
                io2.log("Номер скопирован в буфер обмена")
                #myphone.phoneCallNumber(phone)
                myphone.phoneDialNumber(phone)
                time.sleep(3)
            
        elif "SMS" in result: # SMS, Android-only
            if io2.Mode=="sl4a":
                text = dialogs.dialogText(
                    title=icon("call") + " SMS на %s" % phone,
                    message="Введите текст SMS"
                )
                if text==None or "cancelled" in text:
                    continue
                from androidhelper import Android
                Android().smsSend(destinationAddress=phone, text=text)
                io2.log("SMS на номер %s отправлено" % phone)
                
        elif "Сообщение" in result: # Email
            if io2.Mode=="sl4a":
                try:
                    from androidhelper import Android
                    Android().setClipboard(phone)
                    Android().sendEmail(phone,phone,phone,attachmentUri=None) # message on Android
                except IOError:
                    io2.log("Не удалось отправить сообщение!")
                else:
                    io2.consoleReturn()
   
        elif "Маршрут" in result:
            map(flat.title) # map

def ifInt(char):
    """ Checks if value is integer """
    try: int(char) + 1
    except: return False
    else: return True

def map(houseTitle=""):
    if io2.Mode == "sl4a":
        try:
            from androidhelper import Android
            phone = Android()
            phone.viewMap(houseTitle)
            os.system("clear")
        except:
            io2.log("Не удалось выполнить поиск на карте")
        else:
            io2.consoleReturn()
    else:
        webbrowser.open("https://yandex.ru/maps/?text=%s" % houseTitle)

def setPhone(phone=""):
    message="Введите номер"
    default=phone
    while 1:
        phone = dialogs.dialogText(
            title=icon("date") + " Номер телефона",
            message=message,
            default=default,
            neutralButton=True
        )
        if phone==None:
            return None
        elif phone.strip() == "":
            return ""
        else:
            phone=phone.strip()
        if ifInt(phone)==True:
            return phone
        elif phone[0]=="+":
            if ifInt(phone[1:]) == True:
                return phone
        else:
            message="Допустимы только цифры и знак «+» в начале"
            default=phone
            continue

def setMeeting(meeting=""):
    if meeting == "":
        year = int(time.strftime("%Y", time.localtime()))
        month = int(time.strftime("%m", time.localtime()))
        day = int(time.strftime("%d", time.localtime()))
    else:
        year = int(meeting[0:4])
        month = int(meeting[5:7])
        day = int(meeting[8:10])
    date = dialogs.dialogPickDate(
        title=icon("date") + " Назначение встречи с контактом",
        year=year,
        month=month,
        day=day
    )
    if date == None or date.strip()=="":
        return ""
    else:
        return date
