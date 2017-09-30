#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import io2
import dialogs
import reports
import house_cl
import webbrowser
import contacts
import console
import time
import sys
import datetime
import territory
import extras
from icons import icon


def tools(houses, settings, resources, jumpToImport=False): # file, former "tools"
    """ Program settings on the start screen """
    
    while 1:
     
        if jumpToImport==True:
            houses, settings, resources = io2.load(url=settings[0][14]) # jump from console
            return houses, settings, resources, True
    
        options =  [
            #icon("jwlibrary", settings[0][4]) + " JW Library",
            #icon("calendar", settings[0][4]) + " Календарь",
            icon("export", settings[0][4]) + " Экспорт",
            icon("import", settings[0][4]) + " Импорт по URL",
            icon("restore", settings[0][4]) + " Восстановление",
            icon("load", settings[0][4]) + " Загрузка",
            icon("save", settings[0][4]) + " Сохранение"
        ]                
                    
        if io2.osName != "android" and io2.Textmode==False: options.append(icon("console", settings[0][4]) + " Консоль ") # positive button on Android
        
        # Determine date & time of last database save
        #if io2.osName=="android": backupPath = io2.AndroidUserPath + "backup/"
        #else: backupPath = "./backup/"
        #lastSave = "Последнее сохранение: {:%d.%m.%Y, %H:%M}".format(datetime.datetime.strptime(time.ctime((os.path.getmtime(backupPath))), "%a %b %d %H:%M:%S %Y"))
        #options.append(lastSave)
        lastSave=None
            
        if settings[0][5]==1:
            consoleStatus = icon("console", settings[0][4]) + " Консоль"
            buttonStatus = True
        else:
            consoleStatus = ""
            buttonStatus = False         
        try:
            choice = dialogs.dialogList( # display list of settings
            form = "tools",
            title = icon("file", settings[0][4]) + " Файл %s " % reports.getTimerIcon(settings[2][6], settings),
            message = "Выберите действие:",
            positiveButton = buttonStatus,
            positive = consoleStatus,
            options = options)
        except:
            io2.log("Ошибка вывода")
            break
        console.process(choice, houses, settings, resources)
        
        if contacts.ifInt(choice)==True: result = options[choice]
        else: result = choice   
        
        if result==None or choice==lastSave: break
        
        elif "positive" in result: # console
            if console.dialog(houses, settings, resources)==True: return houses, settings, resources, True
            
        elif "JW Library" in result: extras.library() # JW Library
        
        elif "Календарь" in result: extras.calendar() # calendar
        
        elif "Сохранение" in result: io2.save(houses, settings, resources, manual=True) # save        
        
        elif "Загрузка" in result:
            houses, settings, resources = io2.load(forced=True) # load            
            io2.save(houses, settings, resources)
        
        elif "Экспорт" in result:
            io2.save(houses, settings, resources)
            io2.share(houses, settings, resources, manual=True, filePick=True) # send
            
        elif "Импорт" in result: houses, settings, resources = io2.load(url=settings[0][14]) # URL download (beta)            
        
        elif "Восстановление" in result: # restore backup

            if io2.osName=="android": backupPath = io2.AndroidUserPath + "backup/"
            else: backupPath = "./backup/"
                
            files = [f for f in os.listdir(backupPath) if os.path.isfile(os.path.join(backupPath, f))]            
            
            fileDates=[]
            for i in range(len(files)): fileDates.append(str("{:%d.%m.%Y, %H:%M}".format(datetime.datetime.strptime(time.ctime((os.path.getmtime(backupPath + files[i]))), "%a %b %d %H:%M:%S %Y"))))
            
            choice2 = dialogs.dialogList(
                title=icon("restore", settings[0][4]) + " Выберите дату и время резервной копии для восстановления " + reports.getTimerIcon(settings[2][6], settings),
                message="Выберите дату и время резервной копии для восстановления:",
                options=fileDates,
                form="restore"
            ) # choose file
            console.process(choice2, houses, settings, resources)
            if choice2==None: continue                        
            try: result = io2.load(UserFile = backupPath + files[choice2]) # load from backup copy
            except: io2.log("Не удалось восстановить данные!")
            else:
                houses, settings, resources = result
                io2.save(houses, settings, resources)
                io2.log("Данные успешно восстановлены из файла " + backupPath + files[choice2])                
            
    return houses, settings, resources, False

def search(houses, settings, resources, query=""):
    """ Search flats/contacts """
    
    if "--textconsole" in sys.argv: pureText=True
    else: pureText=False
    
    while 1:    
        query = dialogs.dialog( # get search query 
            icon("search", settings[0][4], pureText=pureText) + " Поиск " + reports.getTimerIcon(settings[2][6], settings),
            default="", 
            message = "Введите поисковый запрос:"
        )
        if io2.osName=="android":
            from androidhelper import Android
            phone = Android()
            phone.dialogCreateSpinnerProgress(title="Prompt Ministry", message="Ищем", maximum_progress=100)
        console.process(query, houses, settings, resources)
        if query==None: break
        else:
            
            # Valid query, run search
            
            while 1:    
                
                query = query.lower() 
                query = query.strip()
                allContacts = contacts.getContacts(houses, settings, resources)
                list=[]           
                
                for i in range(len(allContacts)): # start search in flats/contacts
                    found=False                
                    if query in allContacts[i][2].lower() or query in allContacts[i][2].lower() or query in allContacts[i][3].lower() or query in allContacts[i][8].lower() or query in allContacts[i][10].lower() or query in allContacts[i][11].lower() or query in allContacts[i][12].lower() or query in allContacts[i][13].lower(): 
                        found=True                
                    
                    if allContacts[i][8]!="virtual":
                        for r in range(len(houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[allContacts[i][7][2]].records)): # in records in flats
                            if query in houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[allContacts[i][7][2]].records[r].title.lower(): 
                                found=True
                            if query in houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[allContacts[i][7][2]].records[r].date.lower(): 
                                found=True
                            if query in houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[allContacts[i][7][2]].records[r].note.lower(): 
                                found=True
                    else:                     
                        for r in range(len(resources[1][allContacts[i][7][0]].porches[0].flats[0].records)): # in records in contacts
                            if query in resources[1][allContacts[i][7][0]].porches[0].flats[0].records[r].title.lower(): 
                                found=True         
                            if query in resources[1][allContacts[i][7][0]].porches[0].flats[0].records[r].date.lower(): 
                                found=True
                            if query in resources[1][allContacts[i][7][0]].porches[0].flats[0].records[r].note.lower(): 
                                found=True
                            
                    if found==True: list.append([allContacts[i][7], allContacts[i][8], allContacts[i][2]])
                        
                options2=[]
                for i in range(len(list)): # save results 
                    if list[i][1] != "virtual": # for regular flats
                        options2.append("%d) %s, %s" % (i+1, houses[list[i][0][0]].title, houses[list[i][0][0]].porches[list[i][0][1]].flats[list[i][0][2]].title) ) 
                    else: # for standalone contacts
                        options2.append("%d) %s, %s" % (i+1, resources[1][list[i][0][0]].title, resources[1][list[i][0][0]].porches[0].flats[0].title )
                    )
                
                if len(options2)==0: options2.append("Ничего не найдено")
                
                if io2.osName=="android":
                    phone.dialogDismiss()        
            
                choice2 = dialogs.dialogList(
                    form="search",
                    title = icon("search", settings[0][4]) +  " Поиск по запросу «%s» %s" % (query, reports.getTimerIcon(settings[2][6], settings)),
                    message = "Результаты:",
                    options=options2
                )
                console.process(choice2, houses, settings, resources)
                
                # Show results
                
                if choice2==None: break
                
                elif options2[0]=="Ничего не найдено":
                    continue
                
                else: # go to flat
                    if list[choice2][1] != "virtual": # regular contacts
                        territory.flatView(list[choice2][0][0], list[choice2][0][1], list[choice2][0][2], houses, settings, resources)
                    else: # standalone contacts
                        territory.flatView(list[choice2][0][0], 0, 0, resources[1], settings, resources)

def status(setting, settings):
    
    if setting!=0: return icon("mark", settings[0][4]) + " "
    else: return "□ "
    
def toggle(setting):
    
    if setting==1: return 0
    else: return 1

def preferences(houses, settings, resources):
    """ Program preferences """
    
    if "--textconsole" in sys.argv: pureText=True
    else: pureText=False
    
    exit=0    
    
    while 1:
        options = []
        if settings[0][14]!="": importURL = "«%s…»" % settings[0][14][:15]
        else: importURL = "нет"            
        
        options.append(status(settings[0][7], settings) + "Автоматически записывать повторные посещения") # settings[0][7]
        options.append(status(settings[0][9], settings) + "Выходить из квартиры после добавления записи") # settings[0][9]
        options.append("▪ Шаблон записи посещения: «%s»" % settings[0][12]) # settings[0][12]
        options.append(status(settings[0][8], settings) + "Напоминать о сдаче отчета") # settings[0][8]
        options.append(status(settings[0][15], settings) + "Переносить минуты отчета на следующий месяц") # settings[0][15]
        options.append(status(settings[0][2], settings) + "Кредит часов") # settings[0][2]
        
        if io2.osName=="android":
            options.append(status(settings[0][0], settings) + "Бесшумный режим при таймере") # settings[0][0]
            options.append(status(settings[0][5], settings) + "Показывать консоль на отдельной кнопке") # settings[0][5]
            options.append(status(settings[0][1], settings) + "Подгонять шрифты под мелкий системный шрифт") # settings[0][1]
        
        options.append(status(settings[0][11], settings) + "Индикатор встреч на сегодня на главной странице") # settings[0][11]
        options.append("▪ Месячная норма: %d" % settings[0][3]) # settings[0][3]
        
        if io2.osName!="linux": options.append(status(settings[0][4], settings) + "Упрощенные значки") # settings[0][4]
        options.append("▪ Число резервных копий: %d" % settings[0][6]) # settings[0][6]                
        #options.append("Сортировка контактов") settings[0][10]       
        options.append("▪ Консольная команда по умолчанию: «%s»" % settings[0][13]) # settings[0][13]
        options.append("▪ URL импорта базы данных: %s" % importURL) # settings[0][14]        
        options.append("▪ Пароль на вход: %s" % settings[0][17]) # settings[0][17]
        
        if io2.osName != "android" and io2.Textmode==False: options.append(icon("console", settings[0][4]) + " Консоль") # positive button on Android
        
        if settings[0][5]==1:
            consoleStatus = icon("console", settings[0][4]) + " Консоль"
            buttonStatus = True
        else:
            consoleStatus = ""
            buttonStatus = False
        
        try:
            choice = dialogs.dialogList( # display list of settings
            form = "preferences",
            title = icon("preferences", settings[0][4]) + " Настройки %s " % reports.getTimerIcon(settings[2][6], settings),
            message = "Выберите настройку:",
            options = options,
            positiveButton = buttonStatus,
            positive = consoleStatus,
            cancel = "Назад")
        except:
            io2.log("Ошибка вывода")
            break
        choice2=""
        console.process(choice, houses, settings, resources)
        
        if contacts.ifInt(choice)==True: result = options[choice]
        else: result = choice
        
        if result==None: break
        
        elif result=="positive": # console
            if console.dialog(houses, settings, resources)==True: return houses, settings, resources, True
            
        elif "Бесшумный режим" in result: settings[0][0] = toggle(settings[0][0])
        
        elif "Подгонять шрифты" in result: settings[0][1] = toggle(settings[0][1])
        
        elif "Кредит часов" in result: settings[0][2] = toggle(settings[0][2])
            
        elif "Месячная норма" in result: 
            while 1:
                choice2 = dialogs.dialog(title = icon("preferences", settings[0][4], pureText=pureText) + " Месячная норма " + reports.getTimerIcon(settings[2][6], settings),
                message="Введите месячную норму часов для подсчета запаса или отставания от нормы по состоянию на текущий день. Чтобы не показывать норму в отчете, введите 0:", default = str(settings[0][3]))
                console.process(choice2, houses, settings, resources)
                try:
                    if choice2!=None:                        
                        if choice2=="": settings[0][3]=0
                        else: settings[0][3] = int(choice2)                        
                        io2.save(houses, settings, resources)
                    else: break
                except:
                    io2.log("Не удалось изменить, попробуйте еще")
                    continue
                else: break
                
        elif "Упрощенные значки" in result: settings[0][4] = toggle(settings[0][4])
                
        elif "Показывать консоль" in result: settings[0][5] = toggle(settings[0][5])
        
        elif "Число резервных копий" in result: # backup copies
            while 1:
                choice2 = dialogs.dialog(title= icon("preferences", settings[0][4], pureText=pureText) + " Число резервных копий " + reports.getTimerIcon(settings[2][6], settings), message="От 0 до 100:", default = str(settings[0][6]))
                console.process(choice2, houses, settings, resources)
                try:
                    if choice2!=None:
                        settings[0][6] = int(choice2)
                        if settings[0][6]>100: settings[0][6]=100
                        elif settings[0][6]<0: settings[0][6]=0
                        io2.save(houses, settings, resources)
                    else: break
                except:
                    io2.log("Не удалось изменить, попробуйте еще")
                    continue
                else: break
             
        elif "Автоматически записывать" in result: settings[0][7] = toggle(settings[0][7])
        
        elif "Напоминать о сдаче" in result: settings[0][8] = toggle(settings[0][8])
        
        elif "Выходить из квартиры" in result: settings[0][9] = toggle(settings[0][9])
        
        elif "Индикатор встреч" in result: settings[0][11] = toggle(settings[0][11])
   
        elif "Шаблон записи" in result:
            choice2 = dialogs.dialog(title= icon("preferences", settings[0][4], pureText=pureText) + " Шаблон записи посещения " + reports.getTimerIcon(settings[2][6], settings), message="Введите текст, который будет автоматически подставляться в новой записи посещения, либо оставьте поле пустым:", default = str(settings[0][12]))
            console.process(choice2, houses, settings, resources)
            if choice2!=None:
                settings[0][12]=choice2
                
        elif "Консольная команда" in result:
            choice2 = dialogs.dialog(title= icon("preferences", settings[0][4], pureText=pureText) + " Консольная команда по умолчанию " + reports.getTimerIcon(settings[2][6], settings), message="Введите команду, которая будет выполняться в консоли путем ввода символа _:", default = str(settings[0][13]))
            console.process(choice2, houses, settings, resources)
            if choice2!=None:
                settings[0][13]=choice2.strip()
                
        elif "URL импорта" in result:
            choice2 = dialogs.dialog(title= icon("preferences", settings[0][4], pureText=pureText) + " URL импорта базы данных " + reports.getTimerIcon(settings[2][6], settings), message="Введите URL-адрес, по которому будет загружаться база данных:", default = settings[0][14])
            console.process(choice2, houses, settings, resources)
            if choice2!=None:
                settings[0][14]=choice2.strip()                
        elif "Переносить минуты" in result: settings[0][15] = toggle(settings[0][15])
        
        elif "Пароль на вход" in result:
            choice2 = dialogs.dialog(title= icon("preferences", settings[0][4], pureText=pureText) + " Пароль на вход " + reports.getTimerIcon(settings[2][6], settings), message="Введите пароль для входа в программу. Если оставить поле пустым, пароль запрашиваться не будет:", default = str(settings[0][17]))
            console.process(choice2, houses, settings, resources)
            if choice2!=None:
                settings[0][17]=choice2
               
        io2.save(houses, settings, resources)            
            
    if exit==1: return True

def terSort(houses, settings, resources):
    """ Territory sort type """

    #    while 1:
    options=[
        "По адресу",
        "По дате взятия",
        "По числу интересующихся",
        "По числу посещений"
    ]
    
    if      settings[1]=="а": selected=0
    elif    settings[1]=="д": selected=1
    elif    settings[1]=="и": selected=2
    elif    settings[1]=="п": selected=3
    
    choice = dialogs.dialogRadio(
        title=icon("sort", settings[0][4]) + " Сортировка участков " + reports.getTimerIcon(settings[2][6], settings),
        selected=selected,
        options=options)
    console.process(choice, houses, settings, resources)
    
    if contacts.ifInt(choice[0])==True: result = options[choice[0]]
    else: result = choice
    
    if result=="По адресу": settings[1] = "а"
    elif result=="По дате взятия": settings[1] = "д"
    elif result=="По числу интересующихся": settings[1] = "и"
    elif result=="По числу посещений": settings[1] = "п"
        
def houseSettings(houses, selectedHouse, settings, resources):
    """ House settings """
    
    if "--textconsole" in sys.argv: pureText=True
    else: pureText=False
    
    while 1:
        options = [
            icon("baloon", settings[0][4]) + " Адрес",
            icon("pin", settings[0][4]) + " Заметка участка",
            icon("date", settings[0][4]) + " Дата взятия",
            icon("cut", settings[0][4]) + " Удалить",
            icon("edit", settings[0][4]) + " Изменить тип",
            icon("globe", settings[0][4]) + " Карта",
            icon("jwlibrary", settings[0][4]) + " JW Library"
        ]        
        
        if houses[selectedHouse].type=="condo": houseIcon = icon("house", settings[0][4])
        elif houses[selectedHouse].type=="private": houseIcon = icon("cottage", settings[0][4])            
        elif houses[selectedHouse].type=="office": houseIcon = icon("office", settings[0][4])            
        
        choice = dialogs.dialogList(
            title = houseIcon + " " + houses[selectedHouse].title + reports.getTimerIcon(settings[2][6], settings),
            message = "Выберите настройку:",
            options = options,
            form="houseSettings",
            cancel = "Назад")
        console.process(choice, houses, settings, resources)
        choice2=""
        
        if contacts.ifInt(choice)==True: result = options[choice]
        else: result = choice
        
        if result==None: break
        
        elif "Адрес" in result: # edit house
            
            if houses[selectedHouse].type=="condo": message = "Введите улицу и номер дома, например:\nПушкина, 30"
            elif houses[selectedHouse].type=="private": message = "Введите улицу, например:\nЛесная"
            elif houses[selectedHouse].type=="office": message = "Введите название либо адрес объекта, например:\nТЦ «Радуга»\nПушкина, 20"
        
            choice2 = dialogs.dialog(title=icon("baloon", settings[0][4], pureText=pureText) + " Адрес " + reports.getTimerIcon(settings[2][6], settings), message=message, default = houses[selectedHouse].title)
            console.process(choice2, houses, settings, resources)
            if choice2 != None:
                houses[selectedHouse].title = choice2.upper()
                io2.save(houses, settings, resources)
                
        elif "Заметка" in result: # house note
            choice2 = dialogs.dialog(icon("pin", settings[0][4], pureText=pureText) + " Заметка участка " + reports.getTimerIcon(settings[2][6], settings), default=houses[selectedHouse].note)
            console.process(choice2, houses, settings, resources)
            if choice2 != None:
                houses[selectedHouse].note = choice2
                io2.save(houses, settings, resources)
        
        elif "Дата взятия" in result: # edit date
            date = dialogs.pickDate(title = icon("date", settings[0][4]) + " Дата взятия участка " + reports.getTimerIcon(settings[2][6], settings),
                    year = int ( houses[selectedHouse].date[0:4]),
                    month = int ( houses[selectedHouse].date[5:7]),
                    day = int ( houses[selectedHouse].date[8:10]),
                    settings=settings,
            )
            console.process(date, houses, settings, resources)
            if date!=None:
                houses[selectedHouse].date = date
                #io2.log("Дата успешно изменена")
                io2.save(houses, settings, resources)
        
        elif "Удалить" in result: # delete house
            answer=dialogs.dialogConfirm(icon("cut", settings[0][4]) + " Удалить участок " + houses[selectedHouse].title + reports.getTimerIcon(settings[2][6], settings), "Вы уверены?")
            #console.process(answer, houses, settings, resources)
            if answer==True:
                #io2.log("Участок удален")
                del houses[selectedHouse]
                io2.save(houses, settings, resources)
                return "deleted"
                
        elif "Изменить тип" in result: pickHouseType(houses, selectedHouse, settings, settings) # house type
                
        elif "Карта" in result: extras.map(houses[selectedHouse].title) # map                          
                
        elif "JW Library" in result: extras.library() # JW Library
                
    return "" # exit
    
def pickHouseType(houses, selectedHouse, settings, resources):
    """ Changes house type or returns type of a new house (if selectedHouse==None) """
    
    if selectedHouse==None: title=""
    else: title = houses[selectedHouse].title        
    
    while 1:
        
        options=[
            icon("house", settings[0][4]) + " Многоквартирный дом",
            icon("cottage", settings[0][4]) + " Частный сектор",
            icon("office", settings[0][4]) + " Деловая территория",
        ]
        choice = dialogs.dialogList(
            title = icon("globe", settings[0][4]) + " Выберите тип участка %s %s" % (title, reports.getTimerIcon(settings[2][6], settings)),
            message="",
            options=options
        )
        console.process(choice, houses, settings, resources)
        
        if contacts.ifInt(choice)==True: result = options[choice]
        else: result = choice
        
        if "Многоквартирный" in result:
            if selectedHouse==None: return "condo"
            else: houses[selectedHouse].type="condo"
        elif "Частный" in result:
            if selectedHouse==None: return "private"
            else: houses[selectedHouse].type="private"
        elif "Деловая" in result:
            if selectedHouse==None: return "office"
            else: houses[selectedHouse].type="office"
        else: continue
        break

def porchSettings(houses, selectedHouse, selectedPorch, settings, resources):
    """ Porch settings """
    
    if "--textconsole" in sys.argv: pureText=True
    else: pureText=False
    
    while 1:
        if houses[selectedHouse].type=="condo":
            type=" подъезда"
            type2=" квартир "
            porchIcon = icon("porch", settings[0][4])
        elif houses[selectedHouse].type=="private":
            type=" сегмента"
            type2=" квартир "
            porchIcon = icon("flag", settings[0][4])
        elif houses[selectedHouse].type=="office":
            type=" офиса"
            type2=" сотрудников "
            porchIcon = icon("door", settings[0][4])
            
        options = [
            icon("baloon", settings[0][4]) + " Название" + type,
            icon("sort", settings[0][4]) + " Сортировка" + type2,
            icon("pin", settings[0][4]) + " Заметка" + type,
            icon("cut", settings[0][4]) + " Удалить",
            icon("help", settings[0][4]) + " Команды",
            icon("globe", settings[0][4]) + " Карта"
        ]
        
        if io2.osName=="android": options.append(icon("jwlibrary", settings[0][4]) + " JW Library")
        
        choice = dialogs.dialogList(
            title = porchIcon + " " + houses[selectedHouse].porches[selectedPorch].title + reports.getTimerIcon(settings[2][6], settings),
            message = "Выберите настройку:",
            form = "porchSettings",
            options = options)
        console.process(choice, houses, settings, resources)
        choice2=""
        
        if contacts.ifInt(choice)==True: result = options[choice]
        else: result = choice
        
        if result == None: break
        
        elif "Название" in result: # edit porch title
        
            if houses[selectedHouse].type=="condo": message = "Введите заголовок подъезда (обычно просто номер):"
            elif houses[selectedHouse].type=="private": message = "Введите название сегмента внутри участка. Это может быть группа домов, часть квартала, четная/нечетная сторона и т.п. Можно создать единственный сегмент с любым названием и даже без него:"
            elif houses[selectedHouse].type=="office": message = "Введите название офиса или организации, например:\nПродуктовый магазин\nОфис 15"
        
            choice2 = dialogs.dialog(icon("baloon", settings[0][4], pureText=pureText) + " Название" + type + reports.getTimerIcon(settings[2][6], settings), message=message, default = houses[selectedHouse].porches[selectedPorch].title)
            console.process(choice2, houses, settings, resources)
            if choice2 != None:
                houses[selectedHouse].porches[selectedPorch].title = choice2.strip()
                io2.save(houses, settings, resources)
            else: continue
            
        elif "Сортировка" in result: # flats sorting
        
            while 1:
                
                if contacts.ifInt(houses[selectedHouse].porches[selectedPorch].flatsLayout)==True: floors = ": " + str(houses[selectedHouse].porches[selectedPorch].flatsLayout)
                else: floors=""
                
                options=[
                    "По номеру",
                    "По этажам%s" % floors,
                    "По алфавиту",
                    "По статусу"
                ]
                
                if      houses[selectedHouse].porches[selectedPorch].flatsLayout=="н": selected=0
                elif    contacts.ifInt(houses[selectedHouse].porches[selectedPorch].flatsLayout)==True: selected=1
                elif    houses[selectedHouse].porches[selectedPorch].flatsLayout=="а": selected=2
                elif    houses[selectedHouse].porches[selectedPorch].flatsLayout=="с": selected=3
                else:   selected=2
                            
                choice3 = dialogs.dialogRadio(
                    title=icon("sort", settings[0][4]) + " Сортировка" + type2 + reports.getTimerIcon(settings[2][6], settings),
                    message="Выберите тип сортировки:",
                    options=options,
                    selected=selected
                )
                console.process(choice3, houses, settings, resources)
                if choice3==None: break                                
                elif contacts.ifInt(choice3[0])==True: result3 = options[choice3[0]]
                else: result3 = choice3
                
                if  result3=="По номеру":
                    houses[selectedHouse].porches[selectedPorch].flatsLayout="н"
                    break
                elif result3=="По этажам":
                    while 1:
                        choice4 = dialogs.dialog(icon("sort", settings[0][4], pureText=pureText) + " Сортировка" + type2 + reports.getTimerIcon(settings[2][6], settings), message="Сколько этажей?")
                        if choice4!=None:
                            if contacts.ifInt(choice4)!=True: io2.log("Ошибка, попробуйте еще раз")
                            else:
                                houses[selectedHouse].porches[selectedPorch].flatsLayout = choice4                
                                break
                        else: break
                    break
                elif result3=="По алфавиту":
                    houses[selectedHouse].porches[selectedPorch].flatsLayout="а"
                    break
                elif result3=="По статусу":
                    houses[selectedHouse].porches[selectedPorch].flatsLayout="с"                
                    break
                    
            io2.save(houses, settings, resources)
            
        elif "Заметка" in result: # porch note
            choice2 = dialogs.dialog(icon("pin", settings[0][4], pureText=pureText) + " Заметка%s " % type + reports.getTimerIcon(settings[2][6], settings), default=houses[selectedHouse].porches[selectedPorch].note)
            console.process(choice2, houses, settings, resources)
            if choice2 != None:
                houses[selectedHouse].porches[selectedPorch].note = choice2
                io2.save(houses, settings, resources)
                
        elif "Удалить" in result: # delete porch
            answer = dialogs.dialogConfirm(
                title = icon("cut", settings[0][4]) + " Удалить " + houses[selectedHouse].porches[selectedPorch].title + " " + reports.getTimerIcon(settings[2][6], settings),
                message = "Вы уверены?"
            )
            console.process(answer, houses, settings, resources)
            if answer== True:
                #io2.log("Подъезд «%s» в доме %s удален" % (houses[selectedHouse].porches[selectedPorch].title, houses[selectedHouse].title))
                del houses[selectedHouse].porches[selectedPorch]
                io2.save(houses, settings, resources)
                return "deleted"
                
        elif "Команды" in result: # commands
            if io2.osName=="android":
                if os.path.exists(io2.AndroidUserPath + "commands.txt"):   
                    with open(io2.AndroidUserPath + "commands.txt", encoding="utf-8") as file: help = file.read()
                    help=dialogs.dialogHelp(title=icon("help", settings[0][4]) + " Команды экрана подъезда (сегмента частного сектора, офиса) " + " " + reports.getTimerIcon(settings[2][6], settings), message=help)
                    console.process(help, houses, settings, resources)
                else: io2.log("Файл справки по командам не найден! Попробуйте перезагрузить архив программы")
            else:
                if os.path.exists("commands.txt"):   
                    with open("commands.txt", encoding="utf-8") as file: help = file.read()
                    help=dialogs.dialogHelp(title=icon("help", settings[0][4]) + " Команды экрана подъезда (сегмента частного сектора, офиса) " + " " + reports.getTimerIcon(settings[2][6], settings), message=help)
                    console.process(help, houses, settings, resources)
                else: io2.log("Файл справки по командам не найден! Попробуйте перезагрузить архив программы")
                
        elif "Карта" in result: extras.map(houses[selectedHouse].title) # map
                
        elif "JW Library" in result: extras.library() # JW Library
 
def flatSettings(houses, selectedHouse, selectedPorch, selectedFlat, settings, resources, virtual=False, delete=False):
    
    housesOrig=houses
    if virtual==True: houses=resources[1] # redefine houses if contact is virtual, but keep original for other operations
    
    if "--textconsole" in sys.argv: pureText=True
    else: pureText=False
    
    while 1:
        
        if houses[selectedHouse].type=="office": type=" сотрудника"
        else: type=" квартиры "        
        if virtual==True: type=" контакта "
            
        options = [
            icon("baloon", settings[0][4]) + " Правка номера и контакта",
            icon("pin", settings[0][4]) + " Заметка" + type,
            icon("cut", settings[0][4]) + " Удалить"
        ]
        
        if houses[selectedHouse].porches[selectedPorch].title=="virtual":
            options.append(icon("house", settings[0][4]) + " Правка адреса")
        
        phone = contacts.checkPhone(houses[selectedHouse].porches[selectedPorch].flats[selectedFlat])
        email = contacts.checkEmail(houses[selectedHouse].porches[selectedPorch].flats[selectedFlat])
        if email != "zzz": options.append(icon("export", settings[0][4]) + " Email на " + email)        
        if io2.osName=="android":
            if phone != "zzz":
                options.append(icon("call", settings[0][4]) + " Звонок на " + phone)        
                options.append(icon("call", settings[0][4]) + " SMS на " + phone)                    
        
        options.append(icon("globe", settings[0][4]) + " Карта")
        
        if io2.osName=="android": options.append(icon("jwlibrary", settings[0][4]) + " JW Library")
        
        if delete==True: result="Удалить"
        else:
            choice = dialogs.dialogList(
                title = icon("contact", settings[0][4]) + " " + houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].title + reports.getTimerIcon(settings[2][6], settings),
                message = "Выберите настройку:",
                form = "flatSettings",
                options = options)
            console.process(choice, housesOrig, settings, resources)
            choice2=""        
        
        if contacts.ifInt(choice)==True: result = options[choice]
        else: result = choice        
        
        if result == None: break
        
        elif "Правка номера" in result: # edit 
        
            if houses[selectedHouse].type=="office": message = "Введите номер (для учета) и описание сотрудника через запятую, например:\n3,продавец\n3, Марина, продавец"
            elif houses[selectedHouse].type=="private": message = "Введите номер частного дома (квартиры) и описание жильца через запятую, например:\n3,Иван Иванович 50"
            elif houses[selectedHouse].type=="condo" and virtual==False: message = "Введите номер квартиры и описание жильца через запятую, например:\n3,Иван Иванович 50"
            else: message = "Введите номер квартиры (офиса, частного дома) и описание контакта через запятую, например:\n3,Иван Иванович 50"
                
            choice2 = dialogs.dialog(
                icon("baloon", settings[0][4], pureText=pureText) + " Правка номера и контакта " + reports.getTimerIcon(settings[2][6], settings),
                message=message,
                default = houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].title
            )
            console.process(choice2, housesOrig, settings, resources)
            
            if virtual==True and "," not in choice2:
                choice2 = "?, " + choice2 # add ? if not entered
                
            if choice2 != None and len(choice2)>0 and choice2[0]!="," and choice2[0]!="." and choice2!="!" and choice2[0]!=" ":
                houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].title = "+" + choice2
                houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].setFlat("+" + choice2)
                io2.save(houses, settings, resources)
                break            
                
        elif "Заметка" in result: # flat note
            choice2 = dialogs.dialog(icon("pin", settings[0][4], pureText=pureText) + " Заметка%s " % type + reports.getTimerIcon(settings[2][6], settings), default = houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].note)
            console.process(choice2, housesOrig, settings, resources)
            if choice2 != None:
                houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].note = choice2
                io2.save(houses, settings, resources)
                
        elif "Удалить" in result: # delete flat
            answer=dialogs.dialogConfirm(
                    title = icon("cut", settings[0][4]) + " Удалить «%s» %s" % (houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].title, reports.getTimerIcon(settings[2][6], settings)),
                    neutralButton=False,
                    message = "Вы уверены?"
                )
            console.process(answer, housesOrig, settings, resources)
            if answer==True:
                #io2.log("Квартира «%s» удалена" % houses[selectedHouse].porches[selectedPorch].flats[selectedFlat].title)
                del houses[selectedHouse].porches[selectedPorch].flats[selectedFlat]
                if houses[selectedHouse].porches[selectedPorch].title=="virtual": # delete whole house if contact was standalone
                    del houses[selectedHouse]
                io2.save(houses, settings, resources)
                return "deleted" # exit to porch
                
        elif "Правка адреса" in result: # edit address of standalone contact
            while 1:
                if houses[selectedHouse].type=="office": message = "Введите название либо адрес объекта, например:\nТЦ «Радуга»\nПушкина, 20"
                elif houses[selectedHouse].type=="private": message = "Введите улицу, например:\nЛесная"
                elif houses[selectedHouse].type=="condo": message = "Введите улицу и номер дома, например:\nПушкина, 30"
                
                address = dialogs.dialog(title=icon("house", settings[0][4], pureText=pureText) + " Правка адреса " + reports.getTimerIcon(settings[2][6], settings),
                message = message,
                default = houses[selectedHouse].title)
                console.process(address, housesOrig, settings, resources)
                if address != None:
                    houses[selectedHouse].title = address.upper()
                break
            
        elif "Email" in result: # Email
            if io2.osName=="android":
                try:
                    from androidhelper import Android
                    Android().sendEmail(email,"","",attachmentUri=None) # email on Android
                except IOError: io2.log("Не удалось отправить письмо!")
                else: io2.consoleReturn()
            else: webbrowser.open("mailto:%s" % email) # email on Windows/Linux

        elif "Звонок на" in result: # phone call, Android-only
            if io2.osName=="android": 
                from androidhelper import Android
                Android().phoneCallNumber(phone)
            
        elif "SMS на" in result: # SMS, Android-only
            if io2.osName=="android": 
                text = dialogs.dialog(title=icon("call", settings[0][4], pureText=pureText) + " SMS на %s %s" % (phone, reports.getTimerIcon(settings[2][6], settings)), message="Введите текст SMS")
                console.process(text, housesOrig, settings, resources)
                if text==None or "cancelled" in text: continue
                from androidhelper import Android
                Android().smsSend(destinationAddress=phone, text=text)
                io2.log("SMS на номер %s отправлено" % phone)  
   
        elif "Карта" in result: extras.map(houses[selectedHouse].title) # map

        elif "JW Library" in result: extras.library() # JW Library, Android-only

def getStatus(status, settings, type=0):
    """ Returns symbol """
    
    string=""
                
    if io2.osName == "android":
        if settings[0][4]==0:
            if status=="0": string = "\u00A0\u2716\u00A0" # cross
            elif status=="1": string = "\u00A0\u21AA\u00A0" # arrow right 
            elif status=="2": string = "\ud83d\udd38" # yellow diamond
            elif status=="9": string = "\ud83d\udd39" # red diamond
            elif status=="":  string = "\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0" # spaces
            else:
                if settings[0][1]==0: # adaptation for small system fonts DISABLED
                    string = "\u00A0\u00A0?\u00A0\u00A0"
                else: string = "\u00A0\u00A0?\u00A0\u00A0\u00A0"
        else: # pseudo graphics on Android
            if status=="0": string = "\u00A0×\u00A0" # cross
            elif status=="1": string = "\u00A0>\u00A0" # arrow right 
            elif status=="2": string = "▫" # yellow diamond
            elif status=="9": string = "▪" # red diamond
            elif status=="":  string = "\u00A0\u00A0\u00A0\u00A0" # spaces
            else: string = "?"            
    else:
        if status=="0": string = "\u2716" # cross
        elif status=="1": string = "→" # arrow right 
        elif status=="2": string = "□" # yellow diamond
        elif status=="9": string = "■" # red diamond
        elif status=="":  string = "\u00A0" # spaces
        else: string = "?"    
    
    if   status=="2": value=0 # value serves to correctly sort by status 
    elif status=="1": value=1
    elif status=="":  value=3
    elif status=="0": value=4
    elif status=="9": value=5
    else: value=2
    
    if type==1:
        return string.strip(), value # strip spaces for more dense formatting
    else:
        return string, value
