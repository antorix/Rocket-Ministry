#!/usr/bin/python
# -*- coding: utf-8 -*-
Simplified=1

try: # определяем ОС
    print("Загружаем графическую библиотеку")
    from androidhelper import Android
except:
    try:
        import global_state
    except:
        Mode = "text"
        UserPath = ""
        BackupFolderLocation = "./backup/"
        print("Графическая библиотека не найдена, входим в консольный режим")
    else:
        Mode = "easygui"
        UserPath = ""
        BackupFolderLocation = "./backup/"
else:
    Mode = "sl4a"
    phone = Android()
    UserPath = phone.environment()[1]["download"][:phone.environment()[1]["download"].index("/Download")]\
                      + "/qpython/projects3/RocketMinistry/" # check location of PM folder
    BackupFolderLocation = UserPath + "backup/"
    AndroidDownloadPath = Android().environment()[1]["download"] + "/"

def initializeDB():
    """ Возвращает изначальное значение houses, settings, resources как при создании базы заново"""
    import time
    return [],\
        [
        [1, 0, 0, 0, "с", 0, 50, 1, 1, 0, 1, 1, 1, 1, "", 1, 0, "", 1, "д", 1, 0, 1], # program settings: settings[0][0…], see set.preferences()
        0,  # не используется!         settings[1]
        # report:                       settings[2]
        [0.0,       # [0] hours         settings[2][0…]
         0.0,       # [1] credit
         0,         # [2] placements
         0,         # [3] videos
         0,         # [4] returns,
         0,         # [5] studies,
         0,         # [6] startTime
         0,         # [7] endTime
         0.0,       # [8] reportTime
         0.0,       # [9] difTime
         "",        # [10] note
         0,         # [11] to remind submit report (0: already submitted)
         ""         # [12] отчет прошлого месяца
         ],
        time.strftime("%b", time.localtime()),  # month of last save: settings[3]
        [None, None, None, None, None, None, None, None, None, None, None, None] # service year: settings[4]
    ],\
        [
            [],     # notebook              resources[0]
            [],     # standalone contacts   resources[1]
            []      # report log            resources[2]
    ]

houses, settings, resources = initializeDB()
DBCreatedTime = ""
Version = "0.0.99"

import dialogs
import sys
import os
import datetime
import json
import time
import urllib.request
from copy import deepcopy
from house_op import addHouse
from icons import icon

LastTimeDidChecks = LastTimeBackedUp = int(time.strftime("%H", time.localtime())) * 3600 \
                + int(time.strftime("%M", time.localtime())) * 60 \
                + int(time.strftime("%S", time.localtime()))

def log(message):
    """ Displaying and logging to file important system messages """

    if Mode == "sl4a":
        phone.makeToast(message)
    else:
        print("%s" % message)
        if settings[0][1]==True or "--textconsole" in sys.argv:
            time.sleep(0.5)

def clearDB():
    """ Очистка базы данных """
    houses.clear()
    settings.clear()
    resources.clear()
    settings[:] = initializeDB()[1][:]
    resources[:] = initializeDB()[2][:]

def removeFiles():
    """ Удаление базы данных и резервной папки"""
    if os.path.exists(UserPath + "data.jsn"):
        os.remove(UserPath + "data.jsn")
    if os.path.exists(UserPath + 'backup'):
        from shutil import rmtree
        rmtree(UserPath + 'backup')

def getDBCreatedTime(dataFile="data.jsn"):
    """ Выдает время последнего изменения базы данных, но не в упрощенном режиме """
    try:
        if Mode=="sl4a" and os.path.exists(UserPath + dataFile):
            DBCreatedTime = datetime.datetime.fromtimestamp(os.path.getmtime(UserPath + dataFile))
        elif os.path.exists(dataFile):
            DBCreatedTime = datetime.datetime.fromtimestamp(os.path.getmtime(dataFile))
        else:
            DBCreatedTime = "не удалось получить"
        return "{:%d.%m %H:%M}".format(DBCreatedTime)
    except:
        return "нет"

def loadOutput(buffer):
    """ Загружает данные из буфера"""
    try:
        settings[0] = buffer[0][0]      # загружаем настройки
        settings[1] = buffer[0][1]
        settings[2] = buffer[0][2]
        settings[3] = buffer[0][3]
        settings[4] = buffer[0][4]

        resources[0] = buffer[1][0]     # загружаем блокнот

        resources[1] = []               # загружаем отдельные контакты
        virHousesNumber = int(len(buffer[1][1]))
        hr = []
        for s in range(virHousesNumber):
            hr.append(buffer[1][1][s])
        houseRetrieve(resources[1], virHousesNumber, hr, silent=True)

        resources[2] = buffer[1][2]     # загружаем журнал отчета

        housesNumber = int(len(buffer)) - 2     # загружаем участки
        h = []
        for s in range(2, housesNumber + 2):
            h.append(buffer[s])
        houseRetrieve(houses, housesNumber, h, silent=True)
    except:
        success=False
    else:
        success=True

    return success

def load(dataFile="data.jsn", download=False, forced=False, delete=False):
    """ Loading houses and settings from JSON file """

    global houses, settings, resources
    from dialogs import dialogAlert
    buffer=[]
    temp = deepcopy(getOutput())  # создаем временную базу

    if Mode == "sl4a":
        if download == True: # загрузка файла из папки загрузок телефона
            if os.path.exists(AndroidDownloadPath + dataFile):
                with open(AndroidDownloadPath + dataFile, "r") as file:
                    buffer = json.load(file)
            else:
                dialogAlert(title="Загрузка базы данных",
                            message="Файл базы данных data.jsn не найден в папке «Загрузки» либо поврежден!")
                return

        elif os.path.exists(UserPath + dataFile): # обычная загрузка
            with open(UserPath + dataFile, "r") as file:
                buffer = json.load(file)

    else: # обычная загрузка файла по умолчанию или через импорт
        if forced==True:
            if dataFile==None:
                from dialogs import dialogFileOpen
                dataFile = dialogFileOpen()
                if dataFile==".":
                    return
            else:
                print("Загружаем из настроек, кэп")

        if forced==False and not os.path.exists(dataFile):
            print("База не найдена, начинаем заново")
        try:
            with open(dataFile, "r") as file:
                buffer = json.load(file)
        except:
            if forced==True:
                dialogAlert(title="Загрузка базы данных",
                            message="Файл базы данных не найден в указанном месте либо поврежден!")
                settings[0][14]=""
            return

    # буфер получен, читаем из него
    if buffer[0] == "Rocket Ministry application data file. Format: JSON. Do NOT edit manually!":
        del buffer[0]
        clearDB()
        if loadOutput(buffer)==False: # ошибочный импорт, восстанавливаем временную базу
            dialogAlert(title="Загрузка базы данных",
                        message="Файл базы данных поврежден!")
            clearDB()
            loadOutput(temp[1:])
            settings[0][14] = ""
        elif forced == True:
            log("База успешно загружена")
            save()
            #if delete==True:
            #    if Mode=="sl4a":
            #        os.remove(AndroidDownloadPath + dataFile) # на телефоне файл удаляется, чтобы при последующем сохранении на телефоне у него не изменилось название
            #    else:
            #        os.remove(dataFile)  # файл на компьютере удаляется, поскольку с телефона может не получиться перезаписать существующий файл


    else:
        dialogAlert(title="Загрузка базы данных", message="Файл базы данных поврежден, создаю новый.")
        clearDB()
        loadOutput(temp[1:])
    #save()


def houseRetrieve(containers, housesNumber, h, silent=False):
    """ Retrieves houses from JSON buffer into objects """

    for a in range(housesNumber):

        addHouse(containers, h[a][0], h[a][4])  # creating house and writing its title and type
        containers[a].porchesLayout = h[a][1]
        containers[a].date = h[a][2]
        containers[a].note = h[a][3]

        porchesNumber = len(h[a][5])  # counting porches
        for b in range(porchesNumber):
            containers[a].addPorch(h[a][5][b][0])  # creating porch and writing its title and layout
            containers[a].porches[b].status = h[a][5][b][1]
            containers[a].porches[b].flatsLayout = h[a][5][b][2]
            containers[a].porches[b].floor1 = h[a][5][b][3]
            containers[a].porches[b].note = h[a][5][b][4]
            containers[a].porches[b].type = h[a][5][b][5]

            flatsNumber = len(h[a][5][b][6])  # counting flats
            for c in range(flatsNumber):
                containers[a].porches[b].flats.append(containers[a].porches[b].Flat())  # creating flat and writing its title
                containers[a].porches[b].flats[c].title = h[a][5][b][6][c][0]
                containers[a].porches[b].flats[c].note = h[a][5][b][6][c][1]
                containers[a].porches[b].flats[c].number = h[a][5][b][6][c][2]
                containers[a].porches[b].flats[c].status = h[a][5][b][6][c][3]
                containers[a].porches[b].flats[c].phone = h[a][5][b][6][c][4]
                containers[a].porches[b].flats[c].meeting = h[a][5][b][6][c][5]

                visitNumber = len(h[a][5][b][6][c][6])  # counting visits
                for d in range(visitNumber):
                    containers[a].porches[b].flats[c].records.append(containers[a].porches[b].flats[c].Record())
                    containers[a].porches[b].flats[c].records[d].date = h[a][5][b][6][c][6][d][0]
                    containers[a].porches[b].flats[c].records[d].title= h[a][5][b][6][c][6][d][1]

def getOutput():
    """ Возвращает строку со всеми данными программы, которые затем либо сохраняются локально, либо экспортируются"""
    output = ["Rocket Ministry application data file. Format: JSON. Do NOT edit manually!"] + [settings] + \
            [[resources[0], [resources[1][i].export() for i in range(len(resources[1]))], resources[2]]]
    for i in range(len(houses)):
        output.append(houses[i].export())
    return output

def save(forced=False, silent=True, forcedBackup=False):
    """ Saving database to JSON file """

    global LastTimeBackedUp

    # Выгружаем все данные в список

    output = getOutput()

    # Сначала резервируем раз в 5 минут

    curTime = getCurTime()
    if forced==True or forcedBackup==True or (settings[0][6] > 0 and (curTime - LastTimeBackedUp) > 300):
        if not os.path.exists(BackupFolderLocation):
            try:
                os.makedirs(BackupFolderLocation)
            except IOError:
                log("Не удалось создать резервную копию!")
                return
        savedTime = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
        with open(BackupFolderLocation + "data_" + savedTime + ".jsn", "w") as newbkfile:
            json.dump(output, newbkfile)
            if silent == False:
                log("Создана резервная копия")
            LastTimeBackedUp = curTime

    if forcedBackup==True:
        return

    # Сохраняем

    try:
        with open(UserPath + "data.jsn", "w") as file:
            json.dump(output, file)
    except IOError:
        log("Не удалось сохранить базу!")
    else:
        if silent == False:
            log("База успешно сохранена")

def share():
    """ Sharing database """
    
    output = getOutput()
    
    buffer = json.dumps(output)    
    
    if Mode == "sl4a": # Sharing to cloud if on Android
        try:
            phone.sendEmail("Введите email","data.jsn",buffer,attachmentUri=None)
        except IOError:
            log("Не удалось отправить базу!")
        else:
            consoleReturn()
    else:
        from webbrowser import open
        open("data.jsn")

def backupRestore(restore=False, delete=False, silent=False):
    """ Восстановление файла из резервной копии """

    from dialogs import dialogAlert
    if os.path.exists(BackupFolderLocation)==False:
        if silent == False:
            dialogAlert(title="Восстановление", message="Папки резервных файлов не существует!")
        return
    files = [f for f in os.listdir(BackupFolderLocation) if os.path.isfile(os.path.join(BackupFolderLocation, f))]
    fileDates = []
    for i in range(len(files)):
        fileDates.append(str("{:%d.%m.%Y, %H:%M:%S}".format(
            datetime.datetime.strptime(time.ctime((os.path.getmtime(BackupFolderLocation + files[i]))),
                                       "%a %b %d %H:%M:%S %Y"))))

    # Если выбран режим восстановления

    if restore == True:
        from dialogs import dialogList
        from icons import icon
        choice2 = dialogList(
            title=icon(
                "restore") + " Восстановление",
            message="Выберите дату и время резервной копии базы данных, которую нужно восстановить:",
            options=fileDates,
            form="restore"
        )  # choose file

        if choice2 == None:
            return
        elif choice2 == "":
            if settings[0][1] == True:
                return
        else:
            del houses[:]
            try:
                load(dataFile="backup/" + files[int(choice2)])  # load from backup copy
            except:
                log("Не удалось восстановить данные!")
            else:
                log("Данные успешно восстановлены из файла " + BackupFolderLocation + files[choice2])
                save()

    # Если выбран режим удаления лишних резервных файлов

    elif delete == True:
        print("Обрабатываем резервные копии")
        limit = settings[0][6]
        if len(files) > limit:  # лимит превышен, удаляем
            extra = len(files) - limit
            for i in range(extra):
                os.remove(BackupFolderLocation + files[i])

def update():
    """ Проверяем новую версию и при наличии обновляем программу с GitHub """

    print("Проверяем обновления")
    try:
        for line in urllib.request.urlopen("https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/version"):
            newVersion = line.decode('utf-8').strip()
    except:
        print("Не удалось подключиться к серверу")
        return
    if newVersion > Version:
        choice = dialogs.dialogConfirm(icon("lamp") + " Обновление", "Найдена новая версия %s! Установить?" % newVersion)
        if choice==True:
            print("Скачиваю…")
            try:
                urls = ["https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/console.py",
                        "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/contacts.py",
                        "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/dialogs.py",
                        "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/homepage.py",
                        "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/house_cl.py",
                        "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/house_op.py",
                        "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/icons.py",
                        "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/io2.py",
                        "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/main.py",
                        "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/notebook.py",
                        "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/reports.py",
                        "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/set.py",
                        "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/territory.py"
                        ]
                if Mode=="easy_gui":
                    urls += [   "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/global_state.py",
                                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/choice_box.py",
                                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/button_box.py",
                                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/fileboxsetup.py",
                                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/fileopen_box.py",
                                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/fillable_box.py",
                                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/text_box.py",
                                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/utils.py",
                                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/Rocket Ministry.vbs",
                                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/main.pyw",
                                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/icon.ico",
                    ]
                for url in urls:
                    urllib.request.urlretrieve(url, UserPath + url[url.index("master/") + 7:])
            except:
                dialogs.dialogAlert(icon("lamp") + " Обновление", "Не удалось загрузить обновление. Попробуйте еще раз или, если не помогло, свяжитесь с разработчиком (раздел «О программе»)")
            else:
                dialogs.dialogAlert(icon("lamp") + " Обновление", "Обновление завершено, необходим перезапуск программы.")
                return True

def consoleReturn():
    os.system("clear")
    input("\nНажмите Enter для возврата")
    os.system("clear")

def getCurTime():
    return int(time.strftime("%H", time.localtime())) * 3600 \
              + int(time.strftime("%M", time.localtime())) * 60 \
              + int(time.strftime("%S", time.localtime()))