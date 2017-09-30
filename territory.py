#!/usr/bin/python
# -*- coding: utf-8 -*-

import house_op
from icons import icon
import set
import sys
import io2
import dialogs
import reports
import console
import contacts

def terView(houses, settings, resources):
    """ Territory  screen """
    
    if "--textconsole" in sys.argv: pureText=True
    else: pureText=False
    
    while 1:
        house_op.sortHouses(houses, settings, resources)

        housesList = [icon("plus", settings[0][4]) + " " + icon("globe", settings[0][4])]        
        
        for i in range(len(houses)): # check houses statistics
            if houses[i].getHouseStats()[0] > 0: visited = "%s %s" % (icon("mark", settings[0][4]), str(houses[i].getHouseStats()[0]))
            else: visited=""
            if houses[i].getHouseStats()[1] > 0: interested = "%s %s" % (icon("smile", settings[0][4]), str(houses[i].getHouseStats()[1]))
            else: interested=""
            if houses[i].note != "": note = "%s %s" % (icon("pin", settings[0][4]), houses[i].note)
            else: note=""
            
            if houses[i].type=="condo": houseIcon = icon("house", settings[0][4]) # get icon for condo or cottage
            elif houses[i].type=="private": houseIcon = icon("cottage", settings[0][4])
            elif houses[i].type=="office": houseIcon = icon("office", settings[0][4])
            
            else: houseIcon = icon("globe", settings[0][4])
            
            if io2.osName=="android":
                housesList.append("%s %s\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0%s  %s %s  %s" % (
                    houseIcon, houses[i].title,
                    house_op.shortenDate(houses[i].date), visited, interested, note)
                )
            else:
                housesList.append("%s %-25s %-5s  %-2s %-2s %s" % (
                    houseIcon, houses[i].title, house_op.shortenDate(houses[i].date), visited, interested, note
                )
            )
        
        if io2.osName!="android":
            if io2.Textmode==False: housesList.append(icon("console", settings[0][4]) + " Консоль") # positive button on Android
            housesList.append(icon("sort", settings[0][4]) + " Сортировка") # neutral button on Android
        
        if settings[0][5]==1:
            consoleStatus = icon("console", settings[0][4]) + " Консоль"
            buttonStatus = True
        else:
            consoleStatus = ""
            buttonStatus = False
        
        try:
            choice = dialogs.dialogList( # display list of houses and options
                title = icon("globe", settings[0][4]) + " Участки (%d) %s" % (len(houses), reports.getTimerIcon(settings[2][6], settings)), # houses sorting type, timer icon
                message = "Выберите участок или создайте новый:",
                options = housesList,
                form = "terView",
                cancel = "Назад",
                neutral = icon("sort", settings[0][4]) + " Сорт.",
                neutralButton = True,
                positiveButton = buttonStatus,
                positive = consoleStatus,
                houses = houses
        )
        except ValueError:
            io2.log("Ошибка вывода")
            return
        console.process(choice, houses, settings, resources)
        choice2=""
        
        try:            
            if choice==None: break
            
            elif choice=="neutral": # territory settings
                set.terSort(houses, settings, resources)
                
            elif choice == "positive": # console
                if console.dialog(houses, settings, resources)==True: return houses, settings, resources, True
                    
            elif choice==0:
                type = set.pickHouseType(houses=houses, selectedHouse=None, settings=settings, resources=resources)
                
                if type=="condo":
                    houseIcon = icon("house", settings[0][4], pureText=pureText)
                    message = "Введите улицу и номер дома, например:\nПушкина, 30"
                elif type=="private":
                    houseIcon = icon("cottage", settings[0][4], pureText=pureText)
                    message = "Введите улицу, например:\nЛесная"
                elif type=="office":
                    houseIcon = icon("office", settings[0][4], pureText=pureText)
                    message = "Введите название либо адрес объекта, например:\nТЦ «Радуга»\nПушкина, 20"
                else: continue
                
                choice2 = dialogs.dialog(houseIcon + " Новый участок " + reports.getTimerIcon(settings[2][6], settings), message)
                console.process(choice2, houses, settings, resources)                
                if choice2 != None:
                    house_op.addHouse(houses, choice2, type) 
                    io2.log("Создан участок «%s»" % choice2.upper())
                    io2.save(houses, settings, resources)
                    houseView(len(houses)-1, houses, settings) # go to house             
                
                
            else:
                if houseView(choice-1, houses, settings, resources)==True: return True # go to house 
                
        except: continue
                
def houseView(selectedHouse, houses, settings, resources, jump=""):
    """ House screen, list (blue house) """    
    
    #if "--textconsole" in sys.argv: pureText=True
    #else: pureText=False
    
    while 1:
        houses[selectedHouse].sortPorches()        
        
        if houses[selectedHouse].type=="condo": porchIcon = icon("porch", settings[0][4], pureText=io2.Textmode)
        elif houses[selectedHouse].type=="private": porchIcon = icon("flag", settings[0][4], pureText=io2.Textmode)
        elif houses[selectedHouse].type=="office": porchIcon = icon("door", settings[0][4], pureText=io2.Textmode)
        
        porchesList = [icon("plus", settings[0][4]) + " " + porchIcon]
        
        for i in range(len(houses[selectedHouse].porches)):
            if houses[selectedHouse].porches[i].note != "": note = " %s %s " % (icon("pin", settings[0][4]), houses[selectedHouse].porches[i].note)
            else: note=""
            porchesList.append(porchIcon + " %s %s" % (houses[selectedHouse].porches[i].title, note))
        
        if io2.osName!="android":
            porchesList.append(icon("preferences", settings[0][4]) + " Участок") # positive button on Android
            if io2.Textmode==False: porchesList.append(icon("console", settings[0][4]) + " Консоль") # neutral button on Android
        
        if settings[0][5]==1:
            consoleStatus = icon("console", settings[0][4]) + " Консоль"
            buttonStatus = True
        else:
            consoleStatus = ""
            buttonStatus = False
        
        if houses[selectedHouse].note !="": noteTitle = icon("pin", settings[0][4]) + " " + houses[selectedHouse].note
        else: noteTitle=""
        
        if houses[selectedHouse].type=="condo": houseIcon = icon("house", settings[0][4])            
        elif houses[selectedHouse].type=="private": houseIcon = icon("cottage", settings[0][4])  
        elif houses[selectedHouse].type=="office": houseIcon = icon("office", settings[0][4])  
        
        try:
            choice = dialogs.dialogList( # display list of porches and options
                form = "houseView",
                title = houseIcon + " %s %s %s" % (houses[selectedHouse].title, noteTitle, reports.getTimerIcon(settings[2][6], settings)),
                options = porchesList,
                cancel = "Назад",
                neutral = icon("preferences", settings[0][4]) + " Участок",
                neutralButton = True,
                positive = consoleStatus,
                positiveButton = buttonStatus,
                houses = houses,
                selectedHouse = selectedHouse)
        except:
            io2.log("Ошибка вывода")
            return
        console.process(choice, houses, settings, resources)
        choice2=""
        
        #try:
        if choice==None: break
        
        elif choice=="neutral": # house settings
            if set.houseSettings(houses, selectedHouse, settings, resources) == "deleted": break # exit to territory screen if house was deleted
                
        elif choice=="positive": # console
            if console.dialog(houses, settings, resources)==True: return True
        
        elif choice==0: # new porch
            if houses[selectedHouse].type=="condo":
                type=" подъезд "
                message="Введите заголовок подъезда (обычно просто номер):"
            elif houses[selectedHouse].type=="private":
                message="Введите название сегмента внутри участка. Это может быть группа домов, часть квартала, четная/нечетная сторона и т.п. Можно создать единственный сегмент с любым названием и даже без него:"    
                type=" сегмент "
            elif houses[selectedHouse].type=="office":
                message="Введите название офиса или организации, например:\nПродуктовый магазин\nОфис 15"    
                type=" офис "
                
            choice2 = dialogs.dialog(porchIcon + " Новый" + type + reports.getTimerIcon(settings[2][6], settings), message)
            console.process(choice2, houses, settings, resources)
            if choice2 != None:
                if choice2[0]=="+": choice2=choice2[1:]
                houses[selectedHouse].addPorch(choice2)
                io2.save(houses, settings, resources)
        
        elif porchView(selectedHouse, choice-1, houses, settings, resources)==True: return True # go to porch
                        
        #except: continue

def porchView(selectedHouse, selectedPorch, houses, settings, resources):
    """ Porch screen, console (yellow house) """
    
    message=default=""
    
    while 1:
        choice=""
        # Display dialog
        
        if houses[selectedHouse].porches[selectedPorch].note != "": noteTitle = icon("pin", settings[0][4]) + " " + houses[selectedHouse].porches[selectedPorch].note      
        else: noteTitle=""        
        
        if houses[selectedHouse].type=="condo": porchIcon = icon("porch", settings[0][4], pureText=io2.Textmode)
        elif houses[selectedHouse].type=="private": porchIcon = icon("flag", settings[0][4], pureText=io2.Textmode)
        elif houses[selectedHouse].type=="office": porchIcon = icon("door", settings[0][4], pureText=io2.Textmode)
        
        title = porchIcon + " %s (%s) %s %s" % (houses[selectedHouse].porches[selectedPorch].title, houses[selectedHouse].title, noteTitle, reports.getTimerIcon(settings[2][6], settings))
        message = houses[selectedHouse].porches[selectedPorch].showFlats(houses[selectedHouse].type, settings)
        
        if houses[selectedHouse].type=="condo": neutral = icon("preferences", settings[0][4]) + " Подъезд"        
        elif houses[selectedHouse].type=="private": neutral = icon("preferences", settings[0][4]) + " Сегмент"        
        elif houses[selectedHouse].type=="office": neutral = icon("preferences", settings[0][4]) + " Офис"        
        
        try:
            choice = dialogs.dialog(title, message, default=default, neutral=neutral, neutralButton=True)
        except:
            houses[selectedHouse].porches[selectedPorch].flatsLayout = "а"
            io2.log("Ошибка вывода, смена сортировки на алфавитную")
            try: choice = dialogs.dialog(title, message, default=default, neutral=neutral, neutralButton=True)
            except:
                io2.log("Ошибка вывода")
                return
        
        try:  
            if choice == None: break
            
            elif choice == "neutral" or choice == "!": # porch settings
                if set.porchSettings(houses, selectedHouse, selectedPorch, settings, resources)=="deleted": break
            
            elif choice=="": # enter last flat
                if len(houses[selectedHouse].porches[selectedPorch].flats)!=0:                    
                    if flatView(selectedHouse, selectedPorch, len(houses[selectedHouse].porches[selectedPorch].flats)-1, houses, settings, resources)==True: return True
                
            elif choice[0] == "+" and "-" in choice: # mass add flats
                added = houses[selectedHouse].porches[selectedPorch].addFlats(choice, settings)
                if added[2]!=0: io2.log("Нельзя добавить последовательность с убыванием номеров")
                else: io2.save(houses, settings, resources)
                default=""
                
            elif choice[0] == "+" and "-" not in choice and len(choice)>1: # add new flat (and enter)                
                if "++" in choice: continue # ++ not allowed (can crush system)
                createdFlat, record, enter = houses[selectedHouse].porches[selectedPorch].addFlat(choice, settings)
                io2.save(houses, settings, resources)
                if enter==1:
                    if flatView(selectedHouse, selectedPorch, createdFlat, houses, settings, resources)==True: return True
                default=""
                
            elif choice[0]== "[": houses[selectedHouse].porches[selectedPorch].flatsLayout = choice[1:] # change flats layout
            
            #elif choice[0]== "-":
            
            elif (choice[0]=="*" or choice[0]=="×") and len(choice)>1: # «автоотказ»
                selectedFlat = -1
                flatFound = False
                for i in range(len(houses[selectedHouse].porches[selectedPorch].flats)): # get selected flat's number
                    if choice[1:] == houses[selectedHouse].porches[selectedPorch].flats[i].number:
                        selectedFlat = i
                        houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].addRecord("автоотказ 0")
                        flatFound = True
                        break
                if flatFound == False:
                    selectedFlat = houses[selectedHouse].porches[selectedPorch].addFlat(choice, settings)[2]
                    houses[selectedHouse].                                      porches[selectedPorch].flats[len(houses[selectedHouse].porches[selectedPorch].flats)-1].addRecord("автоотказ 0")
                    io2.log("В «%s» добавлен автоотказ" % houses[selectedHouse].porches[selectedPorch].flats[len(houses[selectedHouse].porches[selectedPorch].flats)-1].title)
                else:
                    io2.log("В «%s» добавлен автоотказ" % houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].title)
                io2.save(houses, settings, resources)
            
            else: # go to flat view 
                for i in range(len(houses[selectedHouse].porches[selectedPorch].flats)): # get selected flat's number
                    if choice == houses[selectedHouse].porches[selectedPorch].flats[i].number:
                        if flatView(selectedHouse, selectedPorch, i, houses, settings, resources)==True: return True
                        break
                        
            # Global console        
            if choice != "":
                try:
                    result = console.process(choice, houses, settings, resources, houseTitle=houses[selectedHouse].title)
                    if result[1]==True: return True
                    elif result[0]==True: continue  # block further execution if blocking command is passed                
                except: continue
            elif io2.Textmode==True: console.process(choice, houses, settings, resources)
            
        except: continue
        

def flatView(selectedHouse, selectedPorch, selectedFlat, houses, settings, resources, virtual=False):
    """ Flat screen, list (silhouette) """
    
    if "--textconsole" in sys.argv: pureText=True
    else: pureText=False
    
    housesOrig=houses
    if virtual==True: houses=resources[1] # redefine houses if contact is virtual, but keep original for other operations
    
    while 1:
        
        # Prepare title
        
        if contacts.checkDate(houses[selectedHouse].porches[selectedPorch].flats[selectedFlat])[0] != "": appointment = icon("calendar", settings[0][4])
        else: appointment = ""
        
        if contacts.checkPhone(houses[selectedHouse].porches[selectedPorch].flats[selectedFlat]) != "zzz": phone = icon("phone", settings[0][4])
        else: phone = ""
        
        if contacts.checkEmail(houses[selectedHouse].porches[selectedPorch].flats[selectedFlat]) != "zzz": email = icon("export", settings[0][4])
        else: email = ""
        
        if settings[0][5]==1:
            consoleStatus = icon("console", settings[0][4]) + " Консоль"
            buttonStatus = True
        else:
            consoleStatus = ""
            buttonStatus = False
        
        options = houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].showRecords(settings)
        
        if houses[selectedHouse].type=="office":
            if io2.osName!="android": options.append(icon("preferences", settings[0][4])+ " Сотрудник") # positive button on Android
            neutral = icon("preferences", settings[0][4]) + " Сотрудник"
        elif virtual==True: 
            if io2.osName!="android": options.append(icon("preferences", settings[0][4])+ " Контакт") # positive button on Android
            neutral = icon("preferences", settings[0][4]) + " Контакт"
        else:
            if io2.osName!="android": options.append(icon("preferences", settings[0][4])+ " Квартира")
            neutral = icon("preferences", settings[0][4]) + " Квартира"
        
        if houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].note=="": # where to show note depending on OS
           noteTitle = ""
           noteMessage = ""
        elif houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].note!="" and io2.osName=="android":
            noteTitle = icon("pin", settings[0][4]) + " " + houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].note
            noteMessage = ""
        elif houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].note!="" and io2.osName!="android":
            noteTitle = ""
            noteMessage = icon("pin", settings[0][4]) + " " + houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].note + "\n\n"

        if io2.osName!="android" and io2.Textmode==False: options.append(icon("console", settings[0][4]) + " Консоль") # neutral button on Android
            
        # Display dialog
        
        try:
            choice = dialogs.dialogList(
            title = icon("contact", settings[0][4]) + " %s %s %s %s %s %s  %s" % (
                set.getStatus(houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].status, settings, type=1)[0],
                houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].title,
                appointment,
                phone,
                email,
                noteTitle,
                reports.getTimerIcon(settings[2][6], settings)
            ),
            options=options,
            form="flatView",
            message = "%sВыберите запись посещения или создайте новое:" % noteMessage,
            neutral = neutral,
            neutralButton = True,
            positive = consoleStatus,
            positiveButton = buttonStatus) 
        except:
            io2.log("Ошибка вывода")
            return   
        console.process(choice, housesOrig, settings, resources)
        choice2=""
        
        try:
            if choice==None: break
            
            elif choice=="neutral": # flat settings
                if set.flatSettings(housesOrig, selectedHouse, selectedPorch, selectedFlat, settings, resources, virtual)=="deleted": break
                
            elif choice=="positive": # console
                if console.dialog(housesOrig, settings, resources)==True: return True
            
            elif choice==0: # new record
                while 1:
                    if default=="": default=settings[0][12]
                    choice2 = dialogs.dialog(icon("tablet", settings[0][4], pureText=pureText) + " Новая запись посещения " + reports.getTimerIcon(settings[2][6], settings), default=default)
                    console.process(choice2, housesOrig, settings, resources)
                    if choice2 != None:                        
                        houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].addRecord(choice2)
                        if len(houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].records)>1 and settings[0][7]==1: # auto writing return visit
                            reports.report(houses, settings, resources, choice="%п")
                        if houses[selectedHouse].porches[selectedPorch].title!="virtual": io2.save(houses, settings, resources)                    
                    break
                if settings[0][9]==1: break
            
            elif contacts.ifInt(choice)==True: # edit record             
                options2 = [icon("edit", settings[0][4]) + " Править", icon("cut", settings[0][4]) + " Удалить"]
                choice2 = dialogs.dialogList(title=icon("tablet", settings[0][4]) + " Запись посещения " + reports.getTimerIcon(settings[2][6], settings),
                    options=options2, message="Что делать с записью?", form="noteEdit")
                    
                if contacts.ifInt(choice2)==True: result2 = options2[choice2]
                else: result2 = choice2
                
                if result2==None: continue                    
                elif "Править" in result2: # edit
                    choice3 = dialogs.dialog(icon("tablet", settings[0][4], pureText=pureText) + " Правка записи " + reports.getTimerIcon(settings[2][6], settings), default = houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].records[int(choice)-1].title)
                    console.process(choice3, housesOrig, settings, resources)
                    if choice3 != None:
                        houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].records[int(choice)-1].title = choice3
                        houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].status = \
                            houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].records[int(choice)-1].title[len(choice3[:])-1] # status set to last character of last record
                    
                elif "Удалить" in result2: # delete record                    
                    del houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].records[int(choice)-1]
                    #io2.log("Запись удалена")                                        
                    if len(houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].records)==0:
                        houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].status = ""
                    else: houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].status =\
                        houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].records[len(houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].records)-1].title[len(houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].records[len(houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].records)-1].title[1:])]
                if houses[selectedHouse].porches[selectedPorch].title!="virtual": io2.save(houses, settings, resources)                    
                else: continue
                
        except: continue
