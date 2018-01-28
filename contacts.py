#!/usr/bin/python
# -*- coding: utf-8 -*-

import io2
import reports
import dialogs
import house_cl
import console
import territory
import time
import sys
import set
import string
from icons import icon

def ifInt(char):
    """ Checks if value is integer """
    
    try: int(char) + 1
    except: return False
    else: return True

def checkDate(flat):
    """ Returns appointment dates in two types """
    
    regularDate=""
    sortableDate=999999
    
    for a in range(len(flat.records)):
        title = flat.records[a].title + "       "
        for i in range(len(title)):
            if not "+" in title[i-1] and ifInt(title[i-1])==False and ifInt(title[i])==True and ifInt(title[i+1])==True and ifInt(title[i+2])==True and ifInt(title[i+3])==True and ifInt(title[i+4])==True and ifInt(title[i+5])==True and ifInt(title[i+6])==False:
                regularDate = ''.join( [ title[i], title[i+1], ".", title[i+2], title[i+3], ".", title[i+4], title[i+5] ] )
                sortableDate = ''.join( [ title[i+4], title[i+5], title[i+2], title[i+3], title[i], title[i+1] ] )
                sortableDate = int(sortableDate)
                
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

def checkPhone(flat):
    """ Returns phone number """
    
    phone = "zzz"
    
    for a in range(len(flat.records)):
        title = flat.records[a].title + "            "
        for i in range(len(title)):
            
            if "+" in title[i] and ifInt(title[i+1])==True and ifInt(title[i+2])==True and ifInt(title[i+3])==True and ifInt(title[i+4])==True and ifInt(title[i+5])==True and ifInt(title[i+6])==True and ifInt(title[i+7])==True and ifInt(title[i+8])==True and ifInt(title[i+9])==True and ifInt(title[i+10])==True and ifInt(title[i+10])==True and ifInt(title[i+11])==True and ifInt(title[i+11])==True:
                
                if ifInt(title[i+11])==True: t11=title[i+11]
                else: t11 = ""
                
                if ifInt(title[i+12])==True: t12=title[i+12]
                else: t12 = ""
                
                phone = ''.join( [ title[i], title[i+1], title[i+2], title[i+3], title[i+4], title[i+5], title[i+6], title[i+7], title[i+8], title[i+9], title[i+10], t11, t12 ] )
                
    return phone

def getContactsAmount(houses, resources, date=0):
    """ Just count contact amount """
    
    c=0
    datedFlats=[]
    
    for h in range(len(houses)):
        for p in range(len(houses[h].porches)):
            for f in range(len(houses[h].porches[p].flats)):
                if len(houses[h].porches[p].flats[f].records) > 0 and houses[h].porches[p].flats[f].status != "0" and houses[h].porches[p].flats[f].status != "9":
                    c+=1
                if date==1: # check appointment date
                    dateApp = checkDate(houses[h].porches[p].flats[f])[1]
                    if dateApp!=999999 and dateApp == int( str(int(time.strftime("%Y", time.localtime()))-2000) + time.strftime("%m%d", time.localtime()) ): datedFlats.append(dateApp) # check if matches with today's date                  
                    
    for h in range(len(resources[1])):
        #if len(resources[1][h].porches[0].flats[0].records) > 0:
        c+=1
        if date==1: # check appointment date
            dateApp = checkDate(resources[1][h].porches[0].flats[0])[1]
            if dateApp!=999999 and dateApp == int( str(int(time.strftime("%Y", time.localtime()))-2000) + time.strftime("%m%d", time.localtime()) ): datedFlats.append(dateApp) # check if matches with today's date
            
    return c, datedFlats
    
def retrieve(houses, h, p, f, contacts, settings):
    """ Retrieve and append contact list """
    
    title = houses[h].porches[p].flats[f].title
    if "," in title: # divide name and number
        title = title[title.index(",")+1:] 
        number = houses[h].porches[p].flats[f].title[:houses[h].porches[p].flats[f].title.index(",")]                    
    else: number = title
        
    if title[0]==" ": title = title[1:]
    if houses[h].title=="": houses[h].title="(БЕЗ АДРЕСА)"
    
    if len( houses[h].porches[p].flats[f].records )>0:
        lastRecordDate = houses[h].porches[p].flats[f].records[len(houses[h].porches[p].flats[f].records)-1].date
    else:
        lastRecordDate=""
    
    contacts.append([# create list with one person per line with values:
        title,                                                                                      # 0 contact name
        set.getStatus(houses[h].porches[p].flats[f].status, settings, type=1)[0],                   # 1 status
        houses[h].title,                                                                            # 2 house title 
        number,                                                                                     # 3 flat number        
        lastRecordDate,                                                                             # 4 last record date        
        checkDate(houses[h].porches[p].flats[f])[0],                                                # 5 appointment date as proper date string
        checkDate(houses[h].porches[p].flats[f])[1],                                                # 6 appointment date as sortable int
        [h, p, f],                                                                                  # 7 reference to flat
        houses[h].porches[p].title,                                                                 # 8 porch title ("virtual" as key for standalone contacts)
        checkPhone(houses[h].porches[p].flats[f]),                                                  # 9 phone number
        
        # Used only for search function:
        
        houses[h].porches[p].flats[f].title,                                                        # 10 flat title
        houses[h].porches[p].flats[f].note,                                                         # 11 flat note
        houses[h].porches[p].note,                                                                  # 12 porch note
        houses[h].note,                                                                             # 13 house note        
        
        # Used for emailing contacts:
        
        checkEmail(houses[h].porches[p].flats[f]),                                                  # 14 email

        # Used for checking house type:

        houses[h].type,                                                                             # 15 house type        
        
        set.getStatus(houses[h].porches[p].flats[f].status, settings, type=1)[1],                   # 16 sortable status ("value")
        
        ])
        
    return contacts

def getContacts(houses, settings, resources):
    """ Returns list of all contacts (house contacts: with records and status other than 0 and 9 """
    
    contacts=[]    
    for h in range(len(houses)):
        for p in range(len(houses[h].porches)):
            for f in range(len(houses[h].porches[p].flats)):
                if len(houses[h].porches[p].flats[f].records) > 0 and houses[h].porches[p].flats[f].status != "0" and houses[h].porches[p].flats[f].status != "9":
                    retrieve(houses, h, p, f, contacts, settings)                    
    for h in range(len(resources[1])):
        retrieve(resources[1], h, 0, 0, contacts, settings)
    
    return contacts

def showContacts(houses, settings, resources):
    """ Show sorted list of contacts """
    
    if "--textconsole" in sys.argv: pureText=True
    else: pureText=False
    
    while 1:
        contacts = getContacts(houses, settings, resources)
        options = [icon("plus", settings[0][4]) + " " + icon("contact", settings[0][4])]        
        
        # Sort
        if settings[0][10]=="в": contacts.sort(key=lambda contacts: contacts[6]) # by appointment date
        elif settings[0][10]=="и": contacts.sort(key=lambda contacts: contacts[0]) # by name
        elif settings[0][10]=="с": contacts.sort(key=lambda contacts: contacts[16]) # by status
        elif settings[0][10]=="з": contacts.sort(key=lambda contacts: contacts[4]) # by last record date
        elif settings[0][10]=="а": contacts.sort(key=lambda contacts: contacts[2]) # by address
        elif settings[0][10]=="т": contacts.sort(key=lambda contacts: contacts[9]) # by phone number        
        elif settings[0][10]=="э": contacts.sort(key=lambda contacts: contacts[14]) # by email
        
        if io2.osName=="android": gap = "      "
        else: gap=" "
        
        for i in range(len(contacts)):
            
            if contacts[i][1] == "":
                if io2.osName == "android":
                    contacts[i][1] = "\u00A0\u00A0\u00A0\u00A0\u00A0" # spaces
                else:
                    contacts[i][1] = " "
            elif contacts[i][1] == "?" and io2.osName == "android":
                contacts[i][1] = "?\u00A0\u00A0"
            
            if contacts[i][5] != "": appointment = "\n%s%s %s" % (gap, icon("appointment", settings[0][4]), contacts[i][5]) # appointment
            else: appointment=""            
            
            if contacts[i][9] != "zzz": phone = "\n%s%s %s" % (gap, icon("phone", settings[0][4]), contacts[i][9]) # phone
            else: phone=""
            
            if contacts[i][14] != "zzz": email = "\n%s%s %s" % (gap, icon("export", settings[0][4]), contacts[i][14]) # email
            else: email=""

            if contacts[i][15]=="office": porch = contacts[i][8] + ", "
            else: porch=""            
                        
            if io2.osName != "android" and contacts[i][1] == "\u2716": contacts[i][1]="x"
            
            options.append(icon("contact", settings[0][4]) + " %s %s\n %s%s, %s%s%s%s%s" % (contacts[i][1], contacts[i][0], gap, contacts[i][2], porch, contacts[i][3], appointment, phone, email) )
        
        if io2.osName != "android":
            if io2.Textmode==False: options.append(icon("console", settings[0][4]) + " Консоль") # positive button on Android
            options.append(icon("sort", settings[0][4]) + " Сортировка") # neutral button on Android
            
        if settings[0][5]==1:
                consoleStatus = icon("console", settings[0][4]) + " Консоль"
                buttonStatus = True
        else:
            consoleStatus = ""
            buttonStatus = False
        
        # Display dialog
        #try:
        choice = dialogs.dialogList(
        form = "showContacts",
        title = icon("contacts", settings[0][4]) + " Контакты (%d) %s " % (len(contacts), reports.getTimerIcon(settings[2][6], settings)), # houses sorting type, timer icon
        message = "Выберите контакт:",
        options = options,
        neutralButton = True,
        neutral = icon("sort", settings[0][4]) + " Сорт.",
        positiveButton = buttonStatus,
        positive = consoleStatus)
        #except:
        #    io2.log("Ошибка вывода")
        #    return
        
        if ifInt(choice)==True: result = options[choice]
        else: result = choice 
        
        if result==None: break # exit
        
        elif result=="positive": # console
            if console.dialog(houses, settings, resources)==True: return True
                
        elif result=="neutral": # sorting 
            options=[
                "По дате назначенной встречи",
                "По имени",
                "По статусу",
                #"По дате посл. записи",
                "По адресу",
                "По номеру телефона",
                "По email"
            ]
            
            if      settings[0][10]=="и": selected=1
            elif    settings[0][10]=="с": selected=2
            elif    settings[0][10]=="з": selected=3
            elif    settings[0][10]=="а": selected=4
            elif    settings[0][10]=="т": selected=5
            elif    settings[0][10]=="э": selected=6
            else:   selected=0
            
            choice2 = dialogs.dialogRadio(
                title = icon("sort", settings[0][4]) + " Сортировка контактов " + reports.getTimerIcon(settings[2][6], settings),
                options=options,
                selected=selected)
            console.process(choice2, houses, settings, resources)
        
            if choice2==None: continue
            elif ifInt(choice2[0])==True: result2 = options[choice2[0]]
            else: result2 = choice2
            
            if result2=="По дате назначенной встречи": settings[0][10]="в"
            elif result2=="По имени": settings[0][10]="и"
            elif result2=="По статусу": settings[0][10]="с"
            elif result2=="По дате посл. записи": settings[0][10]="з"
            elif result2=="По адресу": settings[0][10]="а"
            elif result2=="По номеру телефона": settings[0][10]="т"
            elif result2=="По email": settings[0][10]="э"
            
        elif choice=="delete":
            if contacts[choice-1][8] != "virtual":
                if territory.flatView(contacts[choice-1][7][0], contacts[choice-1][7][1], contacts[choice-1][7][2], houses, settings, resources, delete=True)==True: return True # go to flat         
            else:
                exit = territory.flatView(contacts[choice-1][7][0], 0, 0, houses, settings, resources, virtual=True, delete=True)
                io2.save(houses, settings, resources)
                if exit==1: return True # go to flat     
            
        elif icon("plus", settings[0][4]) in result[0]: # add new standalone contact        
            default=""
            newContact=""
            while newContact != None:
                newContact = dialogs.dialog( 
                    icon("contact", settings[0][4], pureText=pureText) + " Новый контакт " + reports.getTimerIcon(settings[2][6], settings),
                    default=default, 
                    message = "Введите имя (напр. Иван) либо номер квартиры с описанием контакта через запятую, например:\n3,Иван Иванович 50"
                )
                console.process(newContact, houses, settings, resources)
                if newContact != None:                    
                        default=newContact 
                        default2=""
                        address=""
                else: break
                        
                while address != None:
                    address = dialogs.dialog( 
                        title = icon("contact", settings[0][4], pureText=pureText) + " Новый контакт " + reports.getTimerIcon(settings[2][6], settings),
                        message = "Введите адрес дома (без номера квартиры) или оставьте поле пустым",
                        default=default2
                    )
                    console.process(address, houses, settings, resources)
                    if address != None:
                        resources[1].append(house_cl.House()) # create house address
                        resources[1][len(resources[1])-1].title = address.upper() 
                        resources[1][len(resources[1])-1].type = "condo"
                        resources[1][len(resources[1])-1].addPorch("virtual") # create virtual porch                        
                        resources[1][len(resources[1])-1].porches[0].addFlat("+" + newContact, settings, virtual=True) # create flat
                        newContact=None
                    io2.save(houses, settings, resources)
                    break            
        else:
            console.process(choice, houses, settings, resources)
            try:            
                if contacts[choice-1][8] != "virtual":
                    if territory.flatView(contacts[choice-1][7][0], contacts[choice-1][7][1], contacts[choice-1][7][2], houses, settings, resources)==True: return True # go to flat         
                else:
                    exit = territory.flatView(contacts[choice-1][7][0], 0, 0, houses, settings, resources, virtual=True)
                    io2.save(houses, settings, resources)
                    if exit==1: return True # go to flat
            except: continue
