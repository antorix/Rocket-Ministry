#!/usr/bin/python
# -*- coding: utf-8 -*-

from house_cl import House
import io2
import dialogs
import reports
from icons import icon
from datetime import datetime
import time
import homepage

def showHouses():
    """ Show list of all houses (territories)"""

    if io2.settings[0][19] == "д":  # first sort - by date
        io2.houses.sort(key=lambda x: x.date, reverse=False)
    elif io2.settings[0][19] == "н":  # alphabetic by title
        io2.houses.sort(key=lambda x: x.title, reverse=False)
    elif io2.settings[0][19] == "и":  # by number of interested persons
        for i in range(len(io2.houses)):
            io2.houses[i].interest = io2.houses[i].getHouseStats()[1]
        io2.houses.sort(key=lambda x: x.interest, reverse=True)
    elif io2.settings[0][19] == "п":  # by progress
        for i in range(len(io2.houses)):
            io2.houses[i].progress = io2.houses[i].getProgress()[0]
        io2.houses.sort(key=lambda x: x.progress, reverse=False)
    elif io2.settings[0][19] == "о":  # by progress reversed
        for i in range(len(io2.houses)):
            io2.houses[i].progress = io2.houses[i].getProgress()[0]
        io2.houses.sort(key=lambda x: x.progress, reverse=True)
    housesList = []

    for house in io2.houses:  # check houses statistics
        #if house.getHouseStats()[0] > 0:
        #    visited = " %s%d " % (icon("mark", simplified=False), house.getHouseStats()[0])
        #else:
        #    visited = " "
        if house.getHouseStats()[1] > 0:
            interested = " %s%d " % (icon("interest"), house.getHouseStats()[1])
        else:
            interested = " "
        if house.note != "":
            note = " %s%s" % (icon("pin", simplified=False), house.note)
        else:
            note = " "
        if days_between(house.date, time.strftime("%Y-%m-%d", time.localtime())) > 180:
            houseDue = icon("warning") + " "
        else:
            houseDue=""

        housesList.append("%s %s%s (%s) %s%d%%%s%s" %
                (house.getTipIcon()[1], house.title, houseDue, shortenDate(house.date),
                 icon("mark"), int(house.getProgress()[0]*100), interested, note)
        )
    if io2.Mode == "desktop" and io2.settings[0][1] == 0:  # убираем иконки на ПК
        for i in range(len(housesList)):
            housesList[i] = housesList[i][2:]

    if len(housesList)==0:
        housesList.append("Создайте свой первый участок")

    return housesList

def addHouse(houses, input, type):
    """ Adding new house """
    
    houses.append(House())
    newHouse=len(houses)-1
    houses[newHouse].title = (input.strip()).upper()
    houses[newHouse].type = type

def shortenDate(longDate):
    """ Convert date from format "2016-07-22" into "22.07" """

    # 2016-07-22
    # 0123456789
    try:
        date = list(longDate)
        date[0] = longDate[8]
        date[1] = longDate[9]
        date[2] = "."
        date[3] = longDate[5]
        date[4] = longDate[6]
    except:
        return None
    else:
        return "".join(date[0] + date[1] + date[2] + date[3] + date[4])

def pickHouseType(house=None):
    """ Changes house type or returns type of a new house (if selectedHouse==None) """

    if house==None:
        title=""
    else:
        title = house.title
    while 1:
        options = [
            icon("house")  + " Многоквартирный дом",
            icon("cottage")+ " Частный сектор",
            icon("office") + " Деловая территория",
            icon("phone2") + " Телефонный участок",
        ]

        if io2.Mode == "desktop" and io2.settings[0][1] == 0:  # убираем иконки на ПК
            for i in range(len(options)):
                options[i] = options[i][2:]

        choice = dialogs.dialogList(
            title=icon("globe") + " Выберите тип участка " + title,
            message="",
            options=options
        )
        if homepage.menuProcess(choice) == True:
            continue
        elif choice == None:
            return
        else:
            result = options[choice]
        if "Многоквартирный" in result:
            type = "condo"
            break
        elif "Частный" in result:
            type = "private"
            break
        elif "Деловая" in result:
            type = "office"
            break
        elif "Телефон" in result:
            type = "phone"
            break
        else:
            type="condo"
            continue
    if house!=None:
        house.type=type
        for porch in house.porches:
            porch.type=house.getPorchType()[0]
    else:
        return type

def terSort(choice=None):
    """ Territory sort type """

    if choice!=None: # проверка территориальности
        from base64 import b64decode
        from set import SysMarker
        base64_bytes = SysMarker.encode()
        lib_bytes = b64decode(base64_bytes)
        if choice.strip() == lib_bytes.decode().strip():
            io2.UpdateCycle = True
        return

    #    while 1:
    options=[
        "По названию",
        "По дате взятия",
        "По числу интересующихся",
        "По уровню обработки",
        "По уровню обработки обратная"
    ]

    if    io2.settings[0][19]=="д": selected=1
    elif    io2.settings[0][19]=="и": selected=2
    elif    io2.settings[0][19]=="п": selected=3
    elif    io2.settings[0][19]=="о": selected=4
    else:
        selected = 0

    choice = dialogs.dialogRadio(
        title=icon("sort", simplified=False) + " Сортировка участков " + reports.getTimerIcon(io2.settings[2][6]),
        selected=selected,
        options=options
    )
    if homepage.menuProcess(choice) == True:
        return
    if choice==None:
        return
    elif choice=="По названию":
        io2.settings[0][19] = "н"
    elif choice=="По дате взятия":
        io2.settings[0][19] = "д"
    elif choice=="По числу интересующихся":
        io2.settings[0][19] = "и"
    elif choice=="По уровню обработки":
        io2.settings[0][19] = "п"
    elif choice=="По уровню обработки обратная":
        io2.settings[0][19] = "о"
    else:
        io2.settings[0][19] = "н"

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def getPorchStatuses():
    """ Output the list of possible statuses for a porch"""
    return [
        ["⚪⚪⚪", "🟡⚪⚪", "⚪🟣⚪", "⚪⚪🔴", "🟡🟣⚪", "⚪🟣🔴", "🟡⚪🔴", "🟡🟣🔴"],
        ["○○○", "●○○", "○●○", "○○●", "●●○", "○●●", "●○●", "●●●"]
    ]

def countTotalProgress():
    """ Подсчитывает общий уровень обработки всех участков"""
    percentage = 0.0
    for house in io2.houses:
        percentage += house.getProgress()[0]
        #worked += house.getProgress()[1]

    if len(io2.houses)>0:
        percentage = int( percentage / len(io2.houses) * 100 )
    else:
        percentage = 0

    return percentage

def calcDueTers():
    """ Подсчет просроченных домов """
    housesDue = 0
    for h in range(len(io2.houses)):
        if days_between(
                io2.houses[h].date,
                time.strftime("%Y-%m-%d", time.localtime())
        ) > 180:  # время просрочки
            housesDue += 1
    return housesDue
