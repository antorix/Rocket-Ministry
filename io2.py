#!/usr/bin/python
# -*- coding: utf-8 -*-

Textmode=False
import sys
import os
if os.name=="posix": # check OS 
    try: from androidhelper import Android
    except:
        osName = "linux"
        if "--textmode" in sys.argv: Textmode=True
    else:
        osName = "android" 
        phone = Android()        
        phone.dialogCreateSpinnerProgress(title="\ud83d\ude80 Prompt Ministry", message="Зажигание", maximum_progress=100)
        phone.dialogShow()        
        AndroidUserPath = phone.environment()[1]["download"][:phone.environment()[1]["download"].index("/Download")] + "/qpython/scripts3/" # check location of PM folder      
        SDK = int(phone.environment()[1]["SDK"]) # check Android version        
else:
    osName = "windows"
    if "--textmode" in sys.argv: Textmode=True

if osName=="android" and os.path.exists(AndroidUserPath + "mod.ini"): Mod=True
elif osName != "android" and os.path.exists("mod.ini"): Mod=True
else: Mod=False

import json
import time
import house_op
import dialogs
import reports
import console
from icons import icon
import urllib.request

def log(message):
    """ Displaying and logging to file important system messages """
    
    if osName == "android": phone.makeToast(message)
    else:
        print("%s\n" % message)
        if Textmode==True or "--textconsole" in sys.argv: time.sleep(0.5)
        #date = strftime("%d.%m", localtime()) + "." + str(int(strftime("%Y", localtime()))-2000)
        #time2 = strftime("%H:%M:%S", localtime())    
        #with open("log.txt", "a", encoding="utf-8") as f: f.write("%s %s: %s\n" % (date, time2, message))

def logReport(entry):
    """ Log all report changes into separate file """
    
    date = time.strftime("%d.%m", time.localtime()) + "." + str(int(time.strftime("%Y", time.localtime()))-2000)
    time2 = time.strftime("%H:%M:%S", time.localtime())
    if osName == "android": file = open(AndroidUserPath + "logreport.txt", "a")
    else: file = open("logreport.txt", "a", encoding="utf-8")
    file.write("%s %s: %s\n" % (date, time2, entry))
    file.close()    
    log(entry)

def load(UserFile="data.jsn", url=None, forced=False):
    """ Loading houses and settings from JSON file """
    
    houses = []
    
    month = time.strftime("%b", time.localtime())
    
    settings = [
        [1, 0, 0, 70, 0, 0, 30, 1, 1, 1, "в", 1, "Говорили о", "jw", "", 1, None, ""],
                    # program settings              settings[0], see set.preferences()
            "а",    # house layout type             settings[1]
                    # report:                       settings[2]
        [   0.0,    # [0] hours                     settings[2][0…]
            0,      # [1] credit
            0,      # [2] placements
            0,      # [3] videos
            0,      # [4] returns,
            0,      # [5] studies,
            0,      # [6] startTime
            0,      # [7] endTime 
            0.0,    # [8] reportTime 
            0.0,    # [9] difTime
            "",     # [10] note
            0       # [11] to remind submit report (0: already submitted)
    ],    
            month,  # month of last save            settings[3]
            [None, None, None, None, None, None, None, None, None, None, None, None]
                    # service year                  settings[4]
    ]
    
    resources = [[],# notebook                      resources[0]
                []  # standalone contacts           resources[1]
    ]    
    
    fileExists = False # loading JSON file, if exists
    
    if osName=="android":
        
        if url!=None: # download file from URL and save it locally (beta)
            phone.dialogCreateSpinnerProgress(title="\ud83d\ude80 Prompt Ministry", message="Импортирую", maximum_progress=100)
            phone.dialogShow()
            #log("Импорт базы данных, подождите...")
            try: urllib.request.urlretrieve(url, AndroidUserPath + "data.tmp")        
            except: log("Недействительный URL импорта, проверьте настройку")
            else:
                with open(AndroidUserPath + "data.tmp", "r") as f: tempLine = f.read(100) # check control string
                if "Prompt Ministry application data file. Format: JSON. Do NOT edit manually!" in tempLine:
                    os.remove(AndroidUserPath + UserFile)
                    os.rename(AndroidUserPath + "data.tmp", AndroidUserPath + UserFile)
                    log("Импорт выполнен успешно")
                else:
                    log("Загруженный файл не является файлом базы данных Prompt Ministry. Переключаюсь на локальную копию...")
                    os.remove(AndroidUserPath + "data.tmp")    
            
        if os.path.exists(AndroidUserPath + UserFile):   
            with open(AndroidUserPath + UserFile, "r") as file:
                buffer = json.load(file)            
            fileExists = True
            
        phone.dialogDismiss()
        
    else:
        if url!=None:  # download file from URL and save it locally (beta)
            log("Импорт базы данных, подождите...")
            try: urllib.request.urlretrieve(url, "data.tmp")                                        
            except: log("Недействительный URL импорта, проверьте настройку")
            else:
                with open("data.tmp", "r") as f: tempLine = f.read(100) # check control string
                if "Prompt Ministry application data file. Format: JSON. Do NOT edit manually!" in tempLine:
                    os.remove(UserFile)
                    os.rename("data.tmp", UserFile)
                    log("Импорт выполнен успешно")
                else:
                    log("Загруженный файл не является файлом базы данных Prompt Ministry. Переключаюсь на локальную копию...")
                    os.remove("data.tmp")                    
            
        if os.path.exists(UserFile):            
            with open(UserFile, "r") as file:
                buffer = json.load(file)
            fileExists = True        
        
    if fileExists == False:
        if forced==True: log("Локальная база данных не найдена, проверьте файл data.jsn в папке программы!")
        return [houses, settings, resources]
    
    # Check control string and load settings
    
    if buffer[0] == "Prompt Ministry application data file. Format: JSON. Do NOT edit manually!":
        del buffer[0]
        settings[0] = buffer[0][0]    
        settings[1] = buffer[0][1]
        settings[2] = buffer[0][2]
        settings[3] = buffer[0][3]
        settings[4] = buffer[0][4]
    else:
        settings[0] = buffer[0][0]    
        settings[1] = buffer[0][1]
        settings[2] = buffer[0][2]
        settings[3] = buffer[0][3]
        settings[4] = [None, None, None, None, None, None, None, None, None, None, None, None]
    
    # Match settings with previous data file versions
    
    if len(settings[0])==4: # appending various settings
        settings[0].append(0)
        settings[0].append(0)
        settings[0].append(30)
        settings[0].append(1)
        
    if len(settings[0])==8: settings[0].append(1) # appending various settings
    if len(settings[0])==9: settings[0].append(1)
    if len(settings[0])==10: settings[0].append("в")
    if len(settings[0])==11: settings[0].append(1)
    if len(settings[0])==12: settings[0].append("Говорили о , оставили")    
    if len(settings[0])==13: settings[0].append("jw")    
    if len(settings[0])==14: settings[0].append("")
    if len(settings[0])==15: settings[0].append(1)
    if len(settings[0])==16: settings[0].append(None)
    if len(settings[0])==17: settings[0].append("")
    
    if len(settings[2])==11: settings[2].append(0) # appending toggle to remind submit report, settings[2][11]
    
    if len(settings)==3: settings.append([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]) # appending service year, settings[4]
    
    # Load resources
    
    resources[0] = buffer[1][0] # notebook
    resources[1] = []           # virtual houses
    
    virHousesNumber = int(len(buffer[1][1]))    
    hr = []
    for s in range(virHousesNumber): hr.append(buffer[1][1][s]) # creating temporary string houses, one string per house    
    houseRetrieve(resources[1], virHousesNumber, hr, settings)

    # Loading houses
    
    housesNumber = int(len(buffer))-2
    h = []
    for s in range(2, housesNumber+2): h.append(buffer[s]) # creating temporary string houses, one string per house    
    houseRetrieve(houses, housesNumber, h, settings)
    
    if forced==True: log("База успешно загружена")
    return [houses, settings, resources]
    
def houseRetrieve(houses, housesNumber, h, settings):
    """ Retrieves houses from JSON buffer into objects """
    
    for a in range(housesNumber): 
        
        if len(h[a])==5: h[a].insert(4, "condo") # matching with versions before 1.2.1: inserting type of house
        
        house_op.addHouse(houses, h[a][0], h[a][4]) # creating house and writing its title and type
        houses[a].porchesLayout = h[a][1]
        houses[a].date = h[a][2]
        houses[a].note = h[a][3]
        porchesNumber = len(h[a][5]) # counting porches
        
        for b in range(porchesNumber):
            houses[a].addPorch(h[a][5][b][0]) # creating porch and writing its title and layout
            houses[a].porches[b].flatsLayout = h[a][5][b][1]
            houses[a].porches[b].note = h[a][5][b][2]
            flatsNumber = len(h[a][5][b][3]) # counting flats
        
            for c in range (flatsNumber):
                houses[a].porches[b].addFlat("+" + h[a][5][b][3][c][0], settings) # creating flat and writing its title
                houses[a].porches[b].flats[c].note = h[a][5][b][3][c][1]
                visitNumber = len(h[a][5][b][3][c][2]) # counting visits
                
                for d in range(visitNumber):
                    houses[a].porches[b].flats[c].addRecord(h[a][5][b][3][c][2][d][1]) # creating visit and writing its title
                    houses[a].porches[b].flats[c].records[d].date = h[a][5][b][3][c][2][d][0] # rewriting date to original
                    houses[a].porches[b].flats[c].records[d].note = h[a][5][b][3][c][2][d][2] # note

def save(houses, settings, resources, manual=False):
    """ Saving database to JSON file """
    
    output = ["Prompt Ministry application data file. Format: JSON. Do NOT edit manually!"] + [settings] + [[resources[0], [ resources[1][i].export() for i in range(len(resources[1])) ] ]]
    for i in range(len(houses)): output.append(houses[i].export())
    
    if settings[0][6] != 0: backup(output, settings[0][6])
    
    if osName == "android":
        os.system("clear")
        try:
            with open(AndroidUserPath + "data.jsn", "w") as file:
                json.dump(output, file)
        except IOError: log("Не удалось сохранить базу!")
        else:
            if manual==True: log("База успешно сохранена")
        
    else:
        try:
            with open("data.jsn", "w") as file:
                json.dump(output, file)
        except IOError: log("Не удалось сохранить базу!")
        else:
            if manual==True: log("База успешно сохранена")
        
        share(houses, settings, resources, manual)
        
    """if osName=="windows": # Save to Dropbox on Windows
        try:
            with open("C:\\Users\\antor\\Dropbox\\Public\\data_rRR13578lkji38dKDl34dk_2!kjWd3jdl900__23.jsn", "w") as file:
                json.dump(output, file)
        except IOError: log("Не удалось сохранить базу в Dropbox!")
        else:
            if manual==True: log("База успешно сохранена в Dropbox")"""

def share(houses, settings, resources, outside=False, manual=False, filePick=False, fileChoice=None, bluetooth=False):
    """ Sharing database """
    
    output = ["Prompt Ministry application data file. Format: JSON. Do NOT edit manually!"] + [settings] + [[resources[0], [ resources[1][i].export() for i in range(len(resources[1])) ] ]]
    for i in range(len(houses)): output.append(houses[i].export())
    
    buffer = json.dumps(output)    
    
    if osName == "android": # Sharing to cloud if on Android
        try:
            if bluetooth==False: phone.sendEmail("Введите email","data.jsn",buffer,attachmentUri=None)
            else:
                log(1)
                log(phone.bluetoothGetConnectedDeviceName(connID=None))
                phone.bluetoothWrite(buffer,connID=phone.bluetoothGetConnectedDeviceName(connID=None))
        except IOError: log("Не удалось отправить базу!")
        else:
            if outside==False: consoleReturn()
            else: log("Выгрузка базы данных Prompt Ministry")
    else:
        if filePick==True:
            
            choice = dialogs.dialogConfirm(
                title=icon("export", settings[0][4]) + " Экспорт " + reports.getTimerIcon(settings[2][6], settings),
                message="В Windows/Linux экспорт в заданный файл осуществляется автоматически при каждом сохранении. Необходимо лишь выбрать путь к файлу. Выбрать путь или отключить экспорт?",
                choices=["Выбрать путь", "Отключить"]
            )
            console.process(choice, houses, settings, resources)
            
            if choice==True:
                fileChoice = dialogs.dialogFileSave(title="Введите путь к файлу экспорта")
                console.process(fileChoice, houses, settings, resources)
                if fileChoice!=None:
                    settings[0][16] = fileChoice
                    log("Включен экспорт в файл: %s" % settings[0][16])
                else: log("Экспорт отключен")
            else:
                settings[0][16] = None
                log("Экспорт отключен")
            
        if settings[0][16] != None:
            try:
                with open(settings[0][16],"w") as file:
                    file.write(buffer)
                    if manual==True: log("Успешный экспорт")
            except:
                log("Не удалось экспортировать в выбранное местоположение, отключаю экспорт")
                settings[0][16]=None
    
def backup(output, limit):
    """ Backing up """
    
    if osName == "android":
        folderLocation = AndroidUserPath + "backup/"
    else: folderLocation = "./backup/"
       
    if not os.path.exists(folderLocation): # creating if does not exist
        try: os.makedirs(folderLocation)
        except IOError:
            log("Не удалось создать резервную копию!")
            return
    
    backupnumber = 0
    for i in range(1, 100): # counting existing backup files
        file_i = folderLocation + "data_" + ("%03d" % i) + ".jsn"
        if os.path.isfile(file_i):
            continue
        else:
            backupnumber = i-1
            break

    if i < limit: # limit not reached, regular backup
        with open(file_i, "w") as newbkfile:            
            json.dump(output, newbkfile)
    else: # limit reached, first renaming up to the limit
        if os.path.isfile(folderLocation + "data_001.jsn"): os.remove(folderLocation + "data_001.jsn")
        for i in range(1, backupnumber):
            if i <= limit:
                file_i = folderLocation + "data_" + ("%03d" %  i)    + ".jsn"
                file_i1= folderLocation + "data_" + ("%03d" % (i+1)) + ".jsn"
                os.rename(file_i1, file_i)        
        
        with open(file_i, "w") as newbkfile:            
            json.dump(output, newbkfile)            

        for i in range(limit+1, 100): # deleting all files after limit, if any
            file_i = folderLocation + "data_" + ("%03d" % i) + ".jsn"
            if os.path.isfile(file_i):
                os.remove(file_i)

def consoleReturn():
    os.system("clear")
    input("\nНажмите Enter/Ввод для возврата")
    os.system("clear")
