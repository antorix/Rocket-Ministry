#!/usr/bin/python
# -*- coding: utf-8 -*-

def initializeDB():
    """ Возвращает изначальное значение houses, settings, resources как при создании базы заново"""
    import time
    return [],\
        [
        [1, 5, 0, 0, "с", 0, 10, 0, 1.5, 0, 1, 1, 1, 1, "", 1, 0, "", "0", "д", 0, 0, 1], # program settings: settings[0][0…], see set.preferences()
        "",# дата последнего обновления settings[1]
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
         0,         # [11] to remind submit report (0: already submitted) - не используется с 2.0
         ""         # [12] отчет прошлого месяца
         ],
        time.strftime("%b", time.localtime()),  # month of last save: settings[3]
        [None, None, None, None, None, None, None, None, None, None, None, None] # service year: settings[4]
    ],\
        [
            [""],   # notebook              resources[0] - начиная с 2.0 глобальная заметка: resources[0][0]
            [],     # standalone contacts   resources[1]
            [],     # report log            resources[2]
    ]

houses, settings, resources = initializeDB()
Version = "2.1.1" # …14
Devmode = 0# DEVMODE!
"""
* Добавление квартир с помощью списка номеров через запятую. Можно ввести вручную или скопировать из буфера.

* Добавление времени в отчет с помощью циферблата с часами и минутами.

* Сетка подъезда может быть не только в центре, но может прилипать к одной из 8 точек по краям экрана. Удобно сделать ближе к той руке, которой вы держите телефон.

* В участке вместо простого показа карты теперь сразу запускается прокладка маршрута.  

* Сортировка контактов по заметке.

* Доработки дизайна и оптимизации.

* Оптимизации под Windows/Linux:
  - адаптация под ландшафтный режим интерфейса;
  - программа запоминает размер и положение окна при выходе;
  - загрузка файла простым перетаскиванием на окно программы;
  - переключение между полями ввода клавишей Tab.
"""

DBCreatedTime = ""
from kivy import platform
if platform == "android":
    UserPath = "../"#storage/emulated/0/Android/data/org.rocketministry/"
else:
    UserPath = ""

BackupFolderLocation = UserPath + "backup/"
DataFile = "data.jsn"

import datetime
import json
import time
import urllib.request
import requests
import shutil
import app
import os
import house
import plyer

Message = ""

LastTimeBackedUp = int(time.strftime("%H", time.localtime())) * 3600 \
                + int(time.strftime("%M", time.localtime())) * 60 \
                + int(time.strftime("%S", time.localtime()))

def log(message="", title="Внимание", timeout=3, forceNotify=False):
    """ Displaying and logging to file important system messages """
    try:
        if app.RM.platform == "mobile" and forceNotify == False:
            plyer.notification.notify(toast=True, message=message)
        else:
            if app.RM.platform == "mobile":
                icon = ""#"icon.png"
            else:
                icon = "icon.ico"
            if 1:#Devmode==0:
                plyer.notification.notify(app_name="Rocket Ministry", title="Rocket Ministry", app_icon=icon,
                                  ticker="Rocket Ministry", message=message, timeout=timeout)
    except:
        print(message)

def clearDB(silent=True):
    """ Очистка базы данных """

    houses.clear()
    settings.clear()
    resources.clear()
    settings[:] = initializeDB()[1][:]
    resources[:] = initializeDB()[2][:]
    if silent==False:
        log("База данных очищена!")
    #save()

def removeFiles(keepDatafile=False):
    """ Удаление базы данных и резервной папки"""
    global UserPath, DataFile, BackupFolderLocation
    if os.path.exists(UserPath + DataFile) and keepDatafile==False:
        os.remove(UserPath + DataFile)
    if os.path.exists(BackupFolderLocation):
        from shutil import rmtree
        rmtree(BackupFolderLocation)

def getDBCreatedTime():
    """ Выдает время последнего изменения базы данных """

    global DataFile, UserPath, DBCreatedTime

    try:
        if os.path.exists(UserPath + DataFile):
            DBCreatedTime = datetime.datetime.fromtimestamp(os.path.getmtime(UserPath + DataFile))
        else:
            DBCreatedTime = "не удалось получить"
        return "{:%d.%m %H:%M}".format(DBCreatedTime)
    except:
        return "нет"

def loadOutput(buffer):
    """ Загружает данные из буфера"""

    global houses, settings, resources

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

        if settings[1] != "": # определяем, что приложение запускается впервые, если ни разу не делалась проверка обновлений
            app.RM.firstRunFlag = False

    except:
        success=False
    else:
        success=True

    return success

def load(datafile=None, allowSave=True, forced=False, clipboard=None, silent=False):
    """ Loading houses and settings from JSON file """

    global DataFile, UserPath, houses, settings, resources
    if datafile == None:
        datafile = DataFile
    app.RM.popupForm = ""
    print("Загружаю буфер.")

    # Сначала получаем буфер

    buffer = []

    if clipboard != None: # берем буфер обмена

        try:
            print("Смотрим буфер обмена.")
            clipboard = str(clipboard).strip()

            if "drive.google.com" in clipboard: # получена ссылка на Google Drive
                URL = "https://docs.google.com/uc?export=download"
                id = clipboard[ clipboard.index("/d/")+3 : clipboard.index("/view")]
                session = requests.Session()
                response = session.get(URL, params={'id': id}, stream=True)
                with open("temp", "wb") as f:
                    for chunk in response.iter_content(32768):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                            print("Данные получены из Google Drive и записаны во временный файл.")

            else: # получен чистый текст
                clipboard = clipboard[ clipboard.index("[\"Rocket Ministry") : ]
                with open("temp", "w") as file:
                    file.write(clipboard)
                    print("Содержимое буфера обмена записано во временный файл.")
        except:
            return False

        try:
            with open("temp", "r") as file:
                buffer = json.load(file)
            print("Буфер получен из буфера обмена.")
            os.remove("temp")
        except:
            #app.RM.popup("Данные для импорта не найдены. Нажмите «Помощь», чтобы узнать о том, как переносить данные Rocket Ministry.")
            return False

    elif forced==True: # импорт по запросу с конкретным файлом
        try:
            with open(datafile, "r") as file:
                buffer = json.load(file)
                print("Буфер получен из импортированного файла.")
        except:
            if silent == False:
                app.RM.popup("Не удалось загрузить файл данных. Скорее всего, он поврежден или не соответствует формату.")
            return False

    else: # обычная загрузка
        if os.path.exists(UserPath + datafile):
            size = os.path.getsize(UserPath + datafile) # файл меньше 320 байт не загружаем
            if size < 320:
                message = "Файл данных найден, но пустой. Пытаюсь восстановить резервную копию."
                print(message)
                if forced == True:
                    app.RM.popup(title="Загрузка базы данных", message=message)
                if backupRestore(restoreWorking=True, allowSave=allowSave) == True:
                    print("База успешно загружена.")
                    if allowSave==True:
                        save(backup=True)  # успешный результат с загрузкой копии
                        print("База сохранена с резервированием.")
                    return True
                else:
                    print("Не удалось восстановить непустую резервную копию (ее нет?).")
            else:
                with open(UserPath + datafile, "r") as file:
                    buffer = json.load(file)
                print("Буфер получен из файла data.jsn в стандартном местоположении.")
        else:
            message = f"Файл базы данных {datafile} не найден, пытаюсь восстановить резервную копию."
            print(message)
            if forced==True:
                app.RM.popup(title="Загрузка базы данных", message=message)
            if backupRestore(restoreWorking=True, allowSave=allowSave) == True:
                print("База успешно загружена.")
                if allowSave == True:
                    save(backup=True)  # успешный результат с загрузкой копии
                    print("База сохранена с резервированием.")
                return True
            else:
                print("Не удалось восстановить непустую резервную копию (ее нет?).")

    # Буфер получен, читаем из него

    if len(buffer)==0:
        print("Создаю новую базу.")
        save(backup=True)  # успешный результат
        print("База сохранена с резервированием.")

    elif "Rocket Ministry application data file." in buffer[0]:
        print("База определена, контрольная строка совпадает.")
        del buffer[0]
        clearDB()
        result = loadOutput(buffer)
        if result == False:
            print("Ошибочный импорт, восстанавливаем резервную копию.")
            backupRestore(restoreWorking=True, allowSave=allowSave)
        else:
            if allowSave == True:
                save(backup=True)  # успешный результат
                print("База сохранена с резервированием.")
            return True

    else:
        print("База получена, но контрольная строка не совпадает.")
        if clipboard == None and forced == False:
            print("Восстанавливаю резервную копию.")
            backupRestore(restoreWorking=True)

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
    output = ["Rocket Ministry application data file. Do NOT edit manually!"] + [settings] + \
            [[resources[0], [resources[1][i].export() for i in range(len(resources[1]))], resources[2]]]
    for house in houses:
        output.append(house.export())

    return output

def save(backup=False, silent=True, export=False):
    """ Saving database to JSON file """

    global DataFile, LastTimeBackedUp, UserPath

    # Выгружаем все данные в список

    output = getOutput()

    # Сначала резервируем раз в 5 минут

    curTime = getCurTime()

    if backup==True or (curTime - LastTimeBackedUp) > 300:
        if os.path.exists(UserPath + DataFile):
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
                    app.RM.popup("Создана резервная копия.")
                LastTimeBackedUp = curTime

    # Сохраняем

    try:
        with open(UserPath + DataFile, "w") as file:
            json.dump(output, file)
        if silent == False:
            app.RM.popup("Выполнено сохранение базы данных.")
    except:
        print("Ошибка записи!")

    # Экспорт в файл на ПК, если найден файл sync.ini, где прописан путь

    if export == True and Devmode == 0 and os.path.exists("sync.ini"):
        try:
            with open("sync.ini", encoding='utf-8', mode="r") as f:
                folder = f.read()
            with open(folder + "/Данные Rocket Ministry.txt", "w") as file:
                json.dump(output, file)
        except:
            print("Произведена неудачная попытка сохранить данные в расположение, указанное в файле sync.ini. Скорее всего, путь указан неверно. Проверьте содержимое этого файла.")

def share(silent=False, clipboard=False, email=False, folder=None, file=False):
    """ Sharing database """

    global UserPath, DataFile

    output = getOutput()

    buffer = json.dumps(output)

    if clipboard == True: # копируем базу в буфер обмена
        try:
            s = str(buffer)
            Clipboard.copy(s)
        except:
            app.RM.popup("Не удалось загрузить базу данных в буфер обмена. Попробуйте еще раз.")
            return
        else:
            app.RM.popup("Данные помещены в буфер обмена.")

    elif email == True: # экспорт в сообщении
        s = str(buffer)
        date = time.strftime("%d", time.localtime())
        month = monthName()[5]
        timeCur = time.strftime("%H.%M", time.localtime())
        dated = "%s %s %s" % (date, month, timeCur)
        filename = "Данные Rocket Ministry от %s" % dated
        plyer.email.send(subject=filename, text=s, create_chooser=True)

    elif file == True: # экспорт в текстовый файл на компьютере
        try:
            from tkinter import filedialog
            folder = filedialog.askdirectory()
            date = time.strftime("%d", time.localtime())
            month = monthName()[5]
            timeCur = time.strftime("%H.%M", time.localtime())
            dated = "%s %s %s" % (date, month, timeCur)
            filename = folder + "/Данные Rocket Ministry от %s.txt" % dated
            with open(filename, "w") as file:
                json.dump(output, file)
        except:
            app.RM.popup("Ошибка экспорта!")
        else:
            app.RM.popup("Данные успешно экспортированы в файл «%s»." % filename)

    elif app.RM.devmode == 0 and folder != None: # экспорт в файл
        try:
            with open(folder + "/data.jsn", "w") as file:
                json.dump(output, file)
        except:
            app.RM.popup("Не удалось сохранить!")
        else:
            app.RM.popup("Данные успешно сохранены в файл %s." % folder + "/data.jsn")

    else:
        try:
            if platform == "android":
                ExportPath = "storage/emulated/0/Android/data/org.rocketministry/"
                #ExportPath = "storage/emulated/0/Download/"
                ExportPath = '/sdcard/'
                #if not os.path.exists(ExportPath):
                #    os.makedirs(ExportPath)
                with open(ExportPath + "data_backup.jsn", "w") as file:
                    json.dump(output, file)
                path = ExportPath
            else:
                with open(os.path.expanduser("~") + "/data_backup.jsn", "w") as file:
                    json.dump(output, file)
                path = os.path.expanduser("~")
        except:
            if silent==False:
                app.RM.popup("Не удалось выполнить экспорт базы данных.")
        else:
            if silent==False:
                app.RM.popup("Успешно выполнен экспорт базы данных в папку %s." % path)

def backupRestore(silent=True, allowSave=True, delete=False, restoreNumber=None, restoreWorking=False):
    """ Восстановление файла из резервной копии """

    if os.path.exists(BackupFolderLocation)==False:
        if silent == False:
            app.RM.popup(title="Восстановление", message="Резервные файлы еще не создавались!")
        return
    files = [f for f in os.listdir(BackupFolderLocation) if os.path.isfile(os.path.join(BackupFolderLocation, f))]
    fileDates = []
    for i in range(len(files)):
        fileDates.append(str("{:%d.%m.%Y, %H:%M:%S}".format(
            datetime.datetime.strptime(time.ctime((os.path.getmtime(BackupFolderLocation + files[i]))),
                                       "%a %b %d %H:%M:%S %Y"))))

    if restoreNumber != None: # восстановление файла по номеру
        files.sort(reverse=True)
        fileDates.sort(reverse=True)
        try:
            load(forced=True, allowSave=allowSave, datafile=BackupFolderLocation + files[restoreNumber])
        except:
            return False
        else:
            return fileDates[restoreNumber] # в случае успеха возвращает дату и время восстановленной копии

    elif restoreWorking == True: # восстановление самой последней непустой копии
        files.sort(reverse=True)
        fileDates.sort(reverse=True)
        for i in range(len(files)):
            size = os.path.getsize(BackupFolderLocation + files[i])
            if size > 320:
                try:
                    load(forced=True, allowSave=allowSave, datafile=BackupFolderLocation + files[i])
                except:
                    print("Непустая резервная копия не найдена.")
                    return False
                else:
                    print("Успешно загружена последняя непустая резервная копия.")
                    if silent == False:
                        app.RM.popup("Успешно загружена резервная копия от %s." % fileDates[i])
                    return True

    # Если выбран режим удаления лишних копий

    elif delete == True:
        print("Обрабатываем резервные копии.")
        limit = 10
        if len(files) > limit:  # лимит превышен, удаляем
            extra = len(files) - limit
            for i in range(extra):
                os.remove(BackupFolderLocation + files[i])

def update():
    """ Проверяем новую версию и при наличии обновляем программу с GitHub """

    global Version

    today = str(datetime.datetime.strptime(time.strftime('%Y-%m-%d'), "%Y-%m-%d"))
    today = today[0: today.index(" ")]
    settings[1] = today
    save()

    if app.RM.platform == "mobile":
        return # мобильная версия не проверяет обновления
    else:
        print("Проверяем обновления настольной версии.")

    try: # подключаемся к GitHub
        for line in urllib.request.urlopen("https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/version"):
            newVersion = line.decode('utf-8').strip()
    except:
        print("Не удалось подключиться к серверу.")
        return
    else: # успешно подключились, сохраняем сегодняшнюю дату последнего обновления
        print("Версия на сайте: ", newVersion)

    if newVersion > Version:
        try:
            print("Найдена новая версия, скачиваем.")
            file = "files.zip"
            urllib.request.urlretrieve(
                "https://github.com/antorix/Rocket-Ministry/archive/refs/heads/master.zip",
                file
            )
            from zipfile import ZipFile
            zip = ZipFile(file, "r")
            zip.extractall("")
            zip.close()
            downloadedFolder = "Rocket-Ministry-master"
            for file_name in os.listdir(downloadedFolder):
                source = downloadedFolder + "/" + file_name
                destination = file_name
                if os.path.isfile(source):
                    shutil.move(source, destination)
            os.remove(file)
            shutil.rmtree(downloadedFolder)
        except:
            print("Не удалось загрузить обновление.")
        else:
            from subprocess import check_call
            from sys import executable
            check_call([executable, '-m', 'pip', 'install', 'kivy'])

    else:
        print("Обновлений нет.")

def getCurTime():
    return int(time.strftime("%H", time.localtime())) * 3600 \
              + int(time.strftime("%M", time.localtime())) * 60 \
              + int(time.strftime("%S", time.localtime()))

def ifInt(char):
    """ Checks if value is integer """
    try: int(char) + 1
    except: return False
    else: return True

def addHouse(houses, input, type=True):
    """ Adding new house """
    if type == True:
        type = "condo"
    elif type == False:
        type = "private"
    houses.append(house.House())
    newHouse = len(houses) - 1
    houses[newHouse].title = (input.strip()).upper()
    houses[newHouse].type = type

def countTotalProgress():
    """ Подсчитывает общий уровень обработки всех участков"""
    percentage = 0.0
    for house in houses:
        percentage += house.getProgress()[0]
        #worked += house.getProgress()[1]

    if len(houses)>0:
        percentage = int( percentage / len(houses) * 100 )
    else:
        percentage = 0

    return percentage

def checkDate(date):
    """Проверяет, что дата в формате ГГГГ-ММ-ДД"""
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except:
        return False
    else:
        return True

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

def days():
    """ Returns number of days in current month """

    if time.strftime("%b", time.localtime()) == "Jan":
        return 31
    elif time.strftime("%b", time.localtime()) == "Feb":
        return 30
    elif time.strftime("%b", time.localtime()) == "Mar":
        return 31
    elif time.strftime("%b", time.localtime()) == "Apr":
        return 30
    elif time.strftime("%b", time.localtime()) == "May":
        return 31
    elif time.strftime("%b", time.localtime()) == "Jun":
        return 30
    elif time.strftime("%b", time.localtime()) == "Jul":
        return 31
    elif time.strftime("%b", time.localtime()) == "Aug":
        return 31
    elif time.strftime("%b", time.localtime()) == "Sep":
        return 30
    elif time.strftime("%b", time.localtime()) == "Oct":
        return 31
    elif time.strftime("%b", time.localtime()) == "Nov":
        return 30
    elif time.strftime("%b", time.localtime()) == "Dec":
        return 31
    else:
        return 30.5

def monthName(monthCode=None, monthNum=None):
    """ Returns names of current and last months in lower and upper cases """

    if monthCode != None:
        month = monthCode
    elif monthNum != None:
        if monthNum == 1:
            month = "Jan"
        elif monthNum == 2:
            month = "Feb"
        elif monthNum == 3:
            month = "Mar"
        elif monthNum == 4:
            month = "Apr"
        elif monthNum == 5:
            month = "May"
        elif monthNum == 6:
            month = "Jun"
        elif monthNum == 7:
            month = "Jul"
        elif monthNum == 8:
            month = "Aug"
        elif monthNum == 9:
            month = "Sep"
        elif monthNum == 10:
            month = "Oct"
        elif monthNum == 11:
            month = "Nov"
        elif monthNum == 12:
            month = "Dec"
    else:
        month = time.strftime("%b", time.localtime())

    if month == "Jan":
        curMonthUp = "Январь"
        curMonthLow = "январь"
        lastMonthUp = "Декабрь"
        lastMonthLow = "декабрь"
        lastMonthEn = "Dec"
        curMonthRuShort = "янв."
        monthNum = 1
        lastTheoMonthNum = 4
        curTheoMonthNum = 5
    elif month == "Feb":
        curMonthUp = "Февраль"
        curMonthLow = "февраль"
        lastMonthUp = "Январь"
        lastMonthLow = "январь"
        lastMonthEn = "Jan"
        curMonthRuShort = "фев."
        monthNum = 2
        lastTheoMonthNum = 5
        curTheoMonthNum = 6
    elif month == "Mar":
        curMonthUp = "Март"
        curMonthLow = "март"
        lastMonthUp = "Февраль"
        lastMonthLow = "февраль"
        lastMonthEn = "Feb"
        curMonthRuShort = "мар."
        monthNum = 3
        lastTheoMonthNum = 6
        curTheoMonthNum = 7
    elif month == "Apr":
        curMonthUp = "Апрель"
        curMonthLow = "апрель"
        lastMonthUp = "Март"
        lastMonthLow = "март"
        lastMonthEn = "Mar"
        curMonthRuShort = "апр."
        monthNum = 4
        lastTheoMonthNum = 7
        curTheoMonthNum = 8
    elif month == "May":
        curMonthUp = "Май"
        curMonthLow = "май"
        lastMonthUp = "Апрель"
        lastMonthLow = "апрель"
        lastMonthEn = "Apr"
        curMonthRuShort = "мая"
        monthNum = 5
        lastTheoMonthNum = 8
        curTheoMonthNum = 9
    elif month == "Jun":
        curMonthUp = "Июнь"
        curMonthLow = "июнь"
        lastMonthUp = "Май"
        lastMonthLow = "май"
        lastMonthEn = "May"
        curMonthRuShort = "июн."
        monthNum = 6
        lastTheoMonthNum = 9
        curTheoMonthNum = 10
    elif month == "Jul":
        curMonthUp = "Июль"
        curMonthLow = "июль"
        lastMonthUp = "Июнь"
        lastMonthLow = "июнь"
        lastMonthEn = "Jun"
        curMonthRuShort = "июл."
        monthNum = 7
        lastTheoMonthNum = 10
        curTheoMonthNum = 11
    elif month == "Aug":
        curMonthUp = "Август"
        curMonthLow = "август"
        lastMonthUp = "Июль"
        lastMonthLow = "июль"
        lastMonthEn = "Jul"
        curMonthRuShort = "авг."
        monthNum = 8
        lastTheoMonthNum = 11
        curTheoMonthNum = 12
    elif month == "Sep":
        curMonthUp = "Сентябрь"
        curMonthLow = "сентябрь"
        lastMonthUp = "Август"
        lastMonthLow = "август"
        lastMonthEn = "Aug"
        curMonthRuShort = "сен."
        monthNum = 9
        lastTheoMonthNum = 12
        curTheoMonthNum = 1
    elif month == "Oct":
        curMonthUp = "Октябрь"
        curMonthLow = "октябрь"
        lastMonthUp = "Сентябрь"
        lastMonthLow = "сентябрь"
        lastMonthEn = "Sep"
        curMonthRuShort = "окт."
        monthNum = 10
        lastTheoMonthNum = 1
        curTheoMonthNum = 2
    elif month == "Nov":
        curMonthUp = "Ноябрь"
        curMonthLow = "ноябрь"
        lastMonthUp = "Октябрь"
        lastMonthLow = "октябрь"
        lastMonthEn = "Oct"
        curMonthRuShort = "нояб."
        monthNum = 11
        lastTheoMonthNum = 2
        curTheoMonthNum = 3
    else:
        curMonthUp = "Декабрь"
        curMonthLow = "декабрь"
        lastMonthUp = "Ноябрь"
        lastMonthLow = "ноябрь"
        lastMonthEn = "Nov"
        curMonthRuShort = "дек."
        monthNum = 12
        lastTheoMonthNum = 3
        curTheoMonthNum = 4

    return curMonthUp, curMonthLow, lastMonthUp, lastMonthLow, lastMonthEn, curMonthRuShort, monthNum, lastTheoMonthNum, curTheoMonthNum

def timeHHMMToFloatUnadjusted(mytime):
    """ Преобразование HH:MM во float без коррекции погрешности """
    if mytime == None:
        return None
    try:
        if ":" not in mytime:
            result1 = abs(int(mytime.strip()))
            result2 = 0
        else:
            hours = mytime[: mytime.index(":")]
            minutes = mytime[mytime.index(":") + 1:]

            result1 = abs(int(hours))

            lis = ["00:%s" % minutes]
            start_dt = datetime.datetime.strptime("00:00", '%H:%M')
            result2 = \
            [float('{:0.2f}'.format((datetime.datetime.strptime(mytime, '%H:%M') - start_dt).seconds / 3600)) for mytime
             in lis][0]
    except:
        return None
    else:
        return result1 + result2

def timeHHMMToFloat(timeH):
    """ Преобразование HH:MM во float с коррекцией минутной погрешности на основе предыдущей функции """
    timeHHMMToFloatUnadjusted_timeH = timeHHMMToFloatUnadjusted(timeH)
    timeActualH2 = timeFloatToHHMM(timeHHMMToFloatUnadjusted_timeH)
    timeHHMMToFloatUnadjusted_timeActualH2 = timeHHMMToFloatUnadjusted(timeActualH2)

    if timeHHMMToFloatUnadjusted_timeActualH2 == timeHHMMToFloatUnadjusted_timeH:
        corrected = timeHHMMToFloatUnadjusted_timeActualH2
    elif timeHHMMToFloatUnadjusted_timeActualH2 < timeHHMMToFloatUnadjusted_timeH:
        corrected = timeHHMMToFloatUnadjusted_timeH + 0.016
    else:
        corrected = timeHHMMToFloatUnadjusted_timeH - 0.016

    return corrected

def sumHHMM(list=None, mode="+"):
    """ Складывает два значения времени вида HH:MM, полученных в списке """
    if list == None:
        list = ['25:06', '9:31']

    mysum = datetime.timedelta()

    for i in list:
        (h, m) = i.split(':')
        d = datetime.timedelta(hours=int(h), minutes=int(m))
        if mode == "+":
            mysum += d
        else:
            mysum -= d

    string = timeFloatToHHMM(delta=str(mysum))

    return string

def timeFloatToHHMM(hours=None, delta=None):
    if delta == None:
        delta = str(datetime.timedelta(hours=hours)).strip()

    if "." in delta:
        delta = delta[0: delta.index(".")]

    if len(delta) == 7:  # "1:00:00"
        result = "%s:%s" % (delta[0:1], delta[2:4])

    elif len(delta) == 8:  # "10:00:00"
        result = "%s:%s" % (delta[0:2], delta[3:5])

    elif len(delta) == 6:  # "100:00"
        result = "%s:%s" % (delta[0:3], delta[4:6])

    elif "day" in delta and len(delta) == 14:       # "1 day, 6:00:00"
        days = int(delta[0]) * 24
        hours = days + int(delta[7:8])
        minutes = int(delta[9:11])
        result = str("%d:%02d" % (hours, minutes))

    elif "day" in delta and len(delta) == 15:       # "1 day, 12:00:00"
        days = int(delta[0]) * 24
        hours = days + int(delta[7:9])
        minutes = int(delta[10:12])
        result = str("%d:%02d" % (hours, minutes))

    elif "days" in delta and len(delta) == 15:      # "2 days, 2:00:00"
        days = int(delta[0]) * 24
        hours = days + int(delta[8:9])
        minutes = int(delta[10:12])
        result = str("%d:%02d" % (hours, minutes))

    elif "days" in delta and len(delta) == 16 \
            and ifInt(delta[0]) == True \
            and ifInt(delta[1]) == False:           # "2 days, 12:00:00"
        days = int(delta[0]) * 24
        hours = days + int(delta[8:10])
        minutes = int(delta[11:13])
        result = str("%d:%02d" % (hours, minutes))

    elif "days" in delta and len(delta) == 16 \
            and ifInt(delta[0]) == True \
            and ifInt(delta[1]) == True:            # "12 days, 2:00:00"
        days = int(delta[0:2]) * 24
        hours = days + int(delta[9:10])
        minutes = int(delta[12:13])
        result = str("%d:%02d" % (hours, minutes))

    elif "days" in delta and len(delta) == 17:      # "12 days, 12:00:00"
        days = int(delta[0:2]) * 24
        hours = days + int(delta[9:11])
        minutes = int(delta[13:14])
        result = str("%d:%02d" % (hours, minutes))
    else:
        result = delta

    return result
