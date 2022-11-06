#!/usr/bin/python
# -*- coding: utf-8 -*-

import io2
import reports
import dialogs
import house_op
import territory
import time
import string
import set
from icons import icon
import homepage

def checkDate(flat):
    """ Returns appointment dates in two types """

    if flat.meeting!="":
        year = str(flat.meeting[2:4])
        month = str(flat.meeting[5:7])
        day = str(flat.meeting[8:10])
        regularDate = day + "." + month + "." + year
        sortableDate = year + month + day
    else:
        regularDate = ""
        sortableDate = 999999

    return regularDate, sortableDate

def checkEmail(flat):
    """ Returns email """
    
    email="zzz"
    
    for a in range(len(flat.records)):
        title = flat.records[a].title
        if "@" in title:
            at = title.index("@")
            
            if " " in title[:at]: # if space before @
                for i in range(len(title[:at])):
                    if title[i]==" ": start = i # count closest space to @ from left
                before = title[start:at]
            else:
                start = 0
                before = title[:at]
            
            if " " in title[at:]: # if space after @
                for i in range(len(title[at:])):
                    if title[at+i]==" ": # count closest space to @ on the right 
                        end = at+i
                        after = title[at:end]
                        break
            else:
                end = len(title)
                after = title[at:]
            
            if title[end-1]=="." or title[end-1]=="," or title[end-1]=="!" or title[end-1]=="?" or title[end-1]==":" or title[end-1]==";":
               after = after[:len(after)-1]
                        
            after[len(after)-1].translate(string.punctuation)            
            email = before + after            
            email = email.strip()
    
    return email

def getContactsAmount(date=0):
    """ Just count contact amount """
    
    c=0
    datedFlats=[]
    today = str( str(int(time.strftime("%Y", time.localtime()))-2000) + time.strftime("%m%d", time.localtime()) )
    for h in range(len(io2.houses)):
        for p in range(len(io2.houses[h].porches)):
            for f in range(len(io2.houses[h].porches[p].flats)):
                if date==1: # check appointment date
                    dateApp = checkDate(io2.houses[h].porches[p].flats[f])[1]
                    if dateApp!=999999 and dateApp == today:
                        #datedFlats.append(dateApp) # check if matches with today's date
                        datedFlats.append(io2.houses[h].porches[p].flats[f])  # check if matches with today's date
                if io2.houses[h].porches[p].flats[f].status != "" and io2.houses[h].porches[p].flats[f].status != "0"\
                        and io2.houses[h].porches[p].flats[f].getName()!="" and not "." in io2.houses[h].porches[p].flats[f].number:
                    c+=1

    for h in range(len(io2.resources[1])):
        c+=1
        if date==1: # check appointment date
            dateApp = checkDate(io2.resources[1][h].porches[0].flats[0])[1]
            if dateApp!=999999 and dateApp == today:
                #datedFlats.append(dateApp) # check if matches with today's date
                datedFlats.append(io2.resources[1][h].porches[0].flats[0])  # check if matches with today's date
            
    return c, datedFlats
    
def retrieve(containers, h, p, f, contacts):
    """ Retrieve and append contact list """
    
    name = containers[h].porches[p].flats[f].getName()
    if containers[h].type=="virtual":
        number = ""
    else:
        number = containers[h].porches[p].flats[f].number

    if len( containers[h].porches[p].flats[f].records )>0:
        lastRecordDate = containers[h].porches[p].flats[f].records[len(containers[h].porches[p].flats[f].records)-1].date
    else:
        lastRecordDate=""

    contacts.append([# create list with one person per line with values:
        name,                                                                                           # 0 contact name
        containers[h].porches[p].flats[f].getStatus()[0],                                               # 1 status
        containers[h].title,                                                                            # 2 house title
        number,                                                                                         # 3 flat number
        lastRecordDate,                                                                                 # 4 last record date
        checkDate(containers[h].porches[p].flats[f])[0],                                                # 5 appointment date as proper date string
        checkDate(containers[h].porches[p].flats[f])[1],                                                # 6 appointment date as sortable int
        [h, p, f],                                                                                      # 7 reference to flat
        containers[h].porches[p].type,                                                                  # 8 porch type ("virtual" as key for standalone contacts)
        containers[h].porches[p].flats[f].phone,                                                        # 9 phone number
        
        # Used only for search function:
        
        containers[h].porches[p].flats[f].title,                                                        # 10 flat title
        containers[h].porches[p].flats[f].note,                                                         # 11 flat note
        containers[h].porches[p].title,                                                                 # 12 porch type
        containers[h].note,                                                                             # 13 house note        
        
        # Used for emailing contacts:
        
        checkEmail(containers[h].porches[p].flats[f]),                                                  # 14 email

        # Used for checking house type:

        containers[h].type,                                                                             # 15 house type
        containers[h].porches[p].flats[f].getStatus()[1],                                               # 16 sortable status ("value")
        ])
        
    return contacts

def getContacts(forSearch=False):
    """ Returns list of all contacts (house contacts: with records and status other than 0 and 9 """
    
    contacts=[]    
    for h in range(len(io2.houses)):
        for p in range(len(io2.houses[h].porches)):
            for f in range(len(io2.houses[h].porches[p].flats)):
                if forSearch==False: # поиск для списка контактов - только актуальные жильцы
                    if io2.houses[h].porches[p].flats[f].status != "" and io2.houses[h].porches[p].flats[f].status != "0" \
                            and io2.houses[h].porches[p].flats[f].getName()!="" and not "." in io2.houses[h].porches[p].flats[f].number:
                        retrieve(io2.houses, h, p, f, contacts)
                else: # поиск для поиска - все контакты вне зависимости от статуса
                    if not "." in io2.houses[h].porches[p].flats[f].number:
                        retrieve(io2.houses, h, p, f, contacts)

    for h in range(len(io2.resources[1])):
        retrieve(io2.resources[1], h, 0, 0, contacts) # отдельные контакты - все

    return contacts

def showContacts():
    """ Show sorted list of contacts """

    choice=""
    while 1:
        contacts = getContacts()
        options = []
        
        # Sort
        if io2.settings[0][4]=="в":
            contacts.sort(key=lambda x: str(x[6]))  # by appointment date
        elif io2.settings[0][4]=="и":
            contacts.sort(key=lambda x: x[0])  # by name
        elif io2.settings[0][4]=="с":
            contacts.sort(key=lambda x: x[16]) # by status
        elif io2.settings[0][4]=="п":
            contacts.sort(key=lambda x: x[4])  # by last record date
        elif io2.settings[0][4]=="а":
            contacts.sort(key=lambda x: x[2])  # by address
        elif io2.settings[0][4]=="т":
            contacts.sort(key=lambda x: x[9])  # by phone number

        #if io2.Mode=="sl4a":
        #    gap = " "
        #else:
        #    gap="\t"

        for i in range(len(contacts)):

            if contacts[i][15]!="condo" and contacts[i][15]!="virtual":
                porch = contacts[i][12] + ", "
                gap = ", "
            else:
                porch=gap=""
            if io2.Mode != "sl4a" and contacts[i][1] == "\u2716":
                contacts[i][1]="x"
            if contacts[i][15] == "condo":
                myicon = icon("house")
            elif contacts[i][15] == "office":
                myicon = icon("office")
            elif contacts[i][15] == "private":
                myicon = icon("cottage")
            elif contacts[i][15] == "phone":
                myicon = icon("phone2")
            else:
                myicon=icon("star")

            if contacts[i][5] != "":
                appointment = "%s%s " % (icon("appointment", simplified=False), contacts[i][5][0:5]) # appointment
            else:
                appointment=""
            if contacts[i][9] != "":
                phone = "%s%s " % ("т.", contacts[i][9]) # phone
            else:
                phone=""
            if contacts[i][8]=="подъезд":
                hyphen="-"
            else:
                hyphen=""
            if contacts[i][2]!="":
                address = "(%s%s%s%s%s) " % (contacts[i][2], gap, porch, hyphen, contacts[i][3])
            else:
                address=""
            if contacts[i][11]!="":
                note = icon("pin", simplified=False) + contacts[i][11]
            else:
                note = ""

            options.append(
                myicon + " %s %s %s%s%s%s" % (
                    contacts[i][1],
                    contacts[i][0],
                    address,
                    appointment,
                    phone,
                    note,
                )
            )

        if len(options) == 0:
            options.append("Здесь будут отображаться жильцы со всех участков и отдельные контакты, созданные вами")

        # Display dialog

        if choice!="positive":
            choice = dialogs.dialogList(
                form = "showContacts",
                title = icon("contacts") + " Контакты " + reports.getTimerIcon(io2.settings[2][6]),
                message = "Список контактов:",
                options = options,
                positive=icon("plus", simplified=False),
                neutral = icon("sort", simplified=False) + " Сорт."
            )
        if homepage.menuProcess(choice)==True:
            continue
        elif choice==None:
            break
        elif choice == "neutral":  # sorting
            options = [
                "По дате назначенной встречи",
                "По имени",
                "По статусу",
                "По адресу",
                "По дате последнего посещения",
                "По номеру телефона"
            ]
            if io2.settings[0][4] == "и":
                selected = 1
            elif io2.settings[0][4] == "с":
                selected = 2
            elif io2.settings[0][4] == "а":
                selected = 3
            elif io2.settings[0][4] == "п":
                selected = 4
            elif io2.settings[0][4] == "т":
                selected = 5
            else:
                selected = 0

            choice2 = dialogs.dialogRadio(
                title=icon("sort", simplified=False) + " Сортировка контактов",
                options=options,
                selected=selected
            )
            if choice2 == None:
                continue
            elif choice2 == "По имени":
                io2.settings[0][4] = "и"
            elif choice2 == "По статусу":
                io2.settings[0][4] = "с"
            elif choice2 == "По адресу":
                io2.settings[0][4] = "а"
            elif choice2 == "По дате последнего посещения":
                io2.settings[0][4] = "п"
            elif choice2 == "По номеру телефона":
                io2.settings[0][4] = "т"
            else:
                io2.settings[0][4] = "в"
            io2.save()

        elif choice == "positive":  # добавление нового контакта
            default = choice = ""
            newContact = dialogs.dialogText(
                icon("contact") + " Новый контакт",
                default=default,
                message="Введите имя:"
            )
            if newContact == None or newContact == "":
                continue
            else:
                house_op.addHouse(io2.resources[1], "", "virtual") # создается новый виртуальный дом
                io2.resources[1][len(io2.resources[1]) - 1].addPorch(input="virtual", type="virtual")
                io2.resources[1][len(io2.resources[1]) - 1].porches[0].addFlat("+" + newContact, virtual=True)
                io2.resources[1][len(io2.resources[1]) - 1].porches[0].flats[0].status = "1"
                io2.log("Создан контакт %s" % io2.resources[1][len(io2.resources[1]) - 1].porches[0].flats[0].getName())
                io2.save()

        elif set.ifInt(choice) == True:
            if "Здесь будут отображаться" in options[choice]:
                choice="positive"
            else:
                h = contacts[choice][7][0]  # получаем номера дома, подъезда и квартиры
                p = contacts[choice][7][1]
                f = contacts[choice][7][2]
                if contacts[choice][8] != "virtual":  # смотрим контакт на участке
                    if set.ifInt(io2.houses[h].porches[p].flatsLayout)==True:
                        allowDelete = False # нельзя удалить контакт, если он в доме с поэтажной сортировкой
                    else:
                        allowDelete = True
                    exit = territory.flatView(flat=io2.houses[h].porches[p].flats[f], house=io2.houses[h], allowDelete=allowDelete)
                    if exit == "deleted":
                        io2.houses[h].porches[p].deleteFlat(f)
                        io2.save()
                    elif exit == "createdRecord" and io2.settings[0][9] == 0:
                        set.flatSettings(flat=io2.houses[h].porches[p].flats[f], house=io2.houses[h], jumpToStatus=True)
                    continue
                else:
                    exit = territory.flatView(flat=io2.resources[1][h].porches[0].flats[0], house=io2.resources[1][h], virtual=True)
                    if exit == "deleted":
                        io2.log("Контакт %s удален" % io2.resources[1][h].porches[0].flats[0].getName())
                        del io2.resources[1][h]
                        io2.save()
                    elif exit == "createdRecord" and io2.settings[0][9] == 0:
                        set.flatSettings(flat=io2.resources[1][h].porches[0].flats[0], house=io2.resources[1][h], jumpToStatus=True)
                    continue

        else:
            continue
