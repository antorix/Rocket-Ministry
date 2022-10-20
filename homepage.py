#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

import io2
from io2 import houses
from io2 import settings
from io2 import resources
import territory
import contacts
import dialogs
import reports
import set
import notebook
import house_op
import time
import datetime
from icons import icon
from os import path, name
import sys
try:
    from os import startfile
except:
    pass

def homepage():
    """ Home page """

    def firstRun():
        """ Срабатывает при первом запуске программы, определяется по отсутствию settings[1]"""

        if io2.Mode == "easygui": # установка шрифта
            if name=="nt" and not path.exists(
                    path.expandvars("%userprofile%") + "/AppData/Local/Microsoft/Windows/Fonts/LiberationMono-Regular.ttf")\
                    and dialogs.dialogConfirm(
                        "Установка Rocket Ministry",
                        "Перед первым запуском рекомендуется установить шрифт Liberation Mono. Сделать это сейчас?"
                    ) == True:
                try:
                    startfile("fonts_install.vbs")
                    time.sleep(2)
                except:
                    try:
                        import tkinter.messagebox
                        tkinter.messagebox.showinfo(
                            "Установка Rocket Ministry",
                            "На следующем экране, пожалуйста, подтвердите установку шрифта.")
                        startfile("LiberationMono-Regular.ttf")
                    except:
                        pass
        try:
            startfile("create_shortcuts.vbs") # установка иконок
        except:
            pass

        message = "У вас есть месячная норма часов? Введите ее или оставьте 0, если не нужна:"
        while 1:
            hours = dialogs.dialogText(
                title = icon("timer") + " Норма часов",
                message=message,
                default=str(io2.settings[0][3])
            )
            try:
                if hours != None:
                    if hours == "":
                        io2.settings[0][3] = 0
                    else:
                        io2.settings[0][3] = int(hours)
                else:
                    io2.save()
                    break
            except:
                message = "Не удалось изменить, попробуйте еще"
                continue
            else:
                io2.save()
                break

    def dailyRoutine():
        curTime = io2.getCurTime()

        if (curTime - io2.LastTimeDidChecks) > 86400 or (curTime - io2.LastTimeDidChecks) < 3:
            io2.LastTimeDidChecks = curTime

            print("Обрабатываем журнал отчета")
            limit = 500
            if len(resources[2]) > limit:
                extra = len(resources[2]) - limit
                for i in range(extra):
                    del resources[2][len(resources[2]) - 1]

            if settings[0][6] > 0:  # проверяем лишние резервные копии
                io2.backupRestore(delete=True, silent=True)

            if settings[0][11] == 1:
                print("Выясняем встречи на сегодня")
                if len(datedFlats) > 0:
                    dialogs.dialogNotify("Внимание", "Сегодня у вас встреча!")

            print("Определяем начало нового месяца")
            savedMonth = settings[3]
            currentMonth = time.strftime("%b", time.localtime())
            if savedMonth != currentMonth:
                reports.report(newMonthDetected=True)
                settings[3] = time.strftime("%b", time.localtime())
                settings[2][11] = 1

            if settings[2][11] == 1:
                print("Проверяем сдачу отчета")
                answer = dialogs.dialogConfirm(
                    title=icon("warning") + " Отчет",
                    message=" Вы уже сдали отчет?"
                )
                if answer == True:
                    reports.report(disableNotification=True)
                else:
                    reports.report(showLastMonth=True)

            print("Все готово!")

    def weeklyRoutine():

        try:  # проверяем обновления, если прошло больше недели
            today = datetime.datetime.strptime(time.strftime('%Y-%m-%d'), "%Y-%m-%d")
            lastUpdateDate = datetime.datetime.strptime(settings[1], "%Y-%m-%d")
            diff = str(today.date() - lastUpdateDate.date())
            if "," in diff:
                diff = int(diff[0 : diff.index(" ")])
            else:
                diff=0
        except:
            diff=8
        if diff>7 and settings[0][12] == 1:
            today = str(today)
            today = today[ 0 : today.index(" ")]
            settings[1] = today
            io2.save()
            if io2.update() == True:
                return True

        #if path.exists('python_distr'): # удаляем папку с установщиком Python, которая осталась после загрузки
        #    from shutil import rmtree
        #    rmtree('python_distr')

    #territory.porchView(houses[0], 0)

    # if "--textmode" in sys.argv:  # проверяем параметры командной строки

    if io2.Mode=="easygui": # определение положения окна
        import global_state
        try:
            with open("winpos.ini", "r") as file:
                line=file.read()
        except:
            global_state.window_size = "500x500" #
            global_state.window_position = "+500+250"
            with open("winpos.ini", "w") as file:
                file.write(global_state.window_size)
                file.write(global_state.window_position)
        else:
            global_state.window_position = '+' + line.split('+', 1)[1]
            global_state.window_size = line[0: line.index("+")]

    if settings[1]=="":
        firstRun()

    if weeklyRoutine() == True:
        return

    io2.save(forcedBackup=True)

    while 1:

        appointment = "" # поиск контактов со встречей на сегодня
        totalContacts, datedFlats = contacts.getContactsAmount(date=1)
        if len(datedFlats)>0:
            appointment = icon("appointment")

        dailyRoutine()

        if reports.updateTimer(settings[2][6]) >= 0: # проверка, включен ли таймер
            time2 = reports.updateTimer(settings[2][6])
        else:
            time2 = reports.updateTimer(settings[2][6]) + 24
        if settings[2][6] > 0:
            timerTime = " \u2b1b %s" % reports.timeFloatToHHMM(time2)
        else:
            timerTime = " \u25b6"

        if settings[2][11]==1:
            remind = icon("warning")
        else:
            remind=""

        if settings[0][3] != 0:
            if settings[0][2] == True:  # включен кредит часов
                credit = settings[2][1]
            else:
                credit = 0
            gap = float((settings[2][0] + credit) - int(time.strftime("%d", time.localtime())) * settings[0][3] / reports.days())
            if gap >= 0:
                gap_str = icon("extra")
            else:
                gap_str = icon("slippage")
        else:
            gap_str = ""

        housesDue=0 # подсчет просроченных домов
        for h in range(len(houses)):
            if house_op.days_between(
                    houses[h].date,
                    time.strftime("%Y-%m-%d", time.localtime())
            ) > 180:  # время просрочки
                housesDue += 1
        if housesDue==0:
            due = ""
        else:
            due = icon("warning")

        options = [
                icon("globe") +     " Участки (%d) %s" % (len(houses), due),
                icon("contacts")+   " Контакты (%d) %s" % (totalContacts, appointment),
                icon("report") +    " Отчет (%s) %s %s" % (reports.timeFloatToHHMM(settings[2][0]), gap_str, remind),
                icon("notebook")+   " Блокнот (%d)" % len(resources[0]),
                icon("search")  +   " Поиск",
                icon("stats")   +   " Статистика",
                icon("calendar")+   " Служебный год",
                icon("file")    +   " Файл",
                icon("preferences")+" Настройки",
                icon("help") +      " О программе"
                ]

        if io2.Mode == "sl4a":
            title = "%s Rocket Ministry %s" % ( icon("rocket"), reports.getTimerIcon(settings[2][6]) )
        else:
            title = "%s Rocket Ministry" % reports.getTimerIcon(settings[2][6])
            if io2.Mode=="text" or settings[0][1]==1:
                options.append(icon("timer") + " Таймер" + timerTime)

        dialogs.clearScreen() # очистка экрана на всякий случай
            #try:
            #    system("clear")
            #except:
            #    system('cls')

        # Run home screen

        choice = dialogs.dialogList(
            form = "home",
            title = title,
            options = options,
            positive=None,
            neutral = icon("timer") + " Таймер" + timerTime,
            negative=None
        )
        if menuProcess(choice)==True:
            continue
        elif choice == None and io2.Mode=="easygui" and settings[0][1]==0:
            return
        elif choice=="neutral": # таймер
            if settings[2][6] == 0:
                reports.report(choice="=(")
            else:
                if settings[0][2]==False:
                    reports.report(choice="=)")  # запись обычного времени
                else: # если в настройках включен кредит, спрашиваем:
                    choice2=dialogs.dialogList(
                        title="Запись времени",
                        options=[
                            icon("timer") + " Обычное время",
                            icon("credit") + " Кредит"
                        ],
                        negative="Отмена"
                    )
                    if choice2==0:
                        reports.report(choice="=)")
                    elif choice2==1:
                        reports.report("=$")
            continue
        elif set.ifInt(choice) == True:
            result = options[choice]
        #else:
        #    continue

            if "Участки" in result:
                territory.terView() # territory

            elif "Отчет" in result:
                reports.report() # report

            elif "Контакты" in result:
                contacts.showContacts() # contacts

            elif "Блокнот" in result:
                notebook.showNotebook() # notebook

            elif "Поиск" in result:
                search(query="") # search

            elif "Статистика" in result:
                stats() # stats

            elif "Служебный год" in result:
                serviceYear() # service year

            elif "Файл" in result:
                if fileActions()==True:
                    return True

            elif "Настройки" in result:
                preferences()

            elif "О программе" in result:
                about()

            elif "Выход" in result:
                return "quit"

def fileActions():
    """ Program settings on the start screen """

    while 1:

        options = [
            icon("restore") + " Восстановление резервной копии",
            icon("export") + " Экспорт",
            icon("clear") + " Очистка"
        ]

        if io2.Mode == "sl4a":
            options.insert(0, icon("download") + " Импорт из загрузок")
        else:
            options.insert(0, icon("import") + " Импорт из файла")

        if io2.Simplified == False:
            options.append(icon("load") + " Загрузка")
            options.append(icon("save") + " Сохранение")

        if io2.Mode == "sl4a":
            options.append(icon("explosion") + " Самоуничтожение")

        choice = dialogs.dialogList(  # display list of settings
            form="tools",
            title=icon("file") + " Файловые операции " + reports.getTimerIcon(settings[2][6]),
            message="Выберите действие:",
            options=options
        )
        if menuProcess(choice)==True:
            continue
        elif choice == None:
            break
        else:
            result = options[choice]

        if "Сохранение" in result:
            io2.save(forced=True, silent=False)  # save

        elif "Загрузка" in result:
            io2.houses.clear()
            io2.settings.clear()
            io2.resources.clear()
            io2.settings[:] = io2.initializeDB()[1][:]
            io2.resources[:] = io2.initializeDB()[2][:]
            io2.load(forced=True)  # load
            io2.save()

        elif "Экспорт" in result:
            io2.share()  # export

        elif "Импорт из загрузок" in result: # для Android
            io2.load(download=True, delete=True, forced=True)

        elif "Импорт из файла" in result: # для Windows
            io2.load(dataFile=None, forced=True, delete=True)

        elif "Восстановление" in result:  # restore backup
            #io2.save(forced=True, silent=True)
            io2.backupRestore(restore=True)
            #io2.save()

        elif "Очистка" in result:
            if dialogs.dialogConfirm(
                title=icon("clear") + " Очистка",
                message="Все пользовательские данные будут полностью удалены, включая все резервные копии! Вы уверены, что это нужно сделать?"
            )==True:
                io2.clearDB()
                io2.removeFiles()
                io2.log("База данных очищена!")
                io2.save()
        elif "Самоуничтожение" in result:
            if dialogs.dialogConfirm(
                title = icon("explosion") + " Самоуничтожение",
                message = "Внимание! Будут удалены ВСЕ пользовательские данные и ВСЕ файлы самой программы, после чего вы больше не сможете ее запустить, пока не установите заново. Вы уверены, что это нужно сделать?"
            ) == True:
                io2.removeFiles(totalDestruction=True)
                return True
        else:
            continue

    return False

def preferences():
    """ Program preferences """

    def status(setting):
        """ Переключение настройки """
        if setting == 0 or set.ifInt(setting) == False:
            return icon("cross") + " "
        else:
            return icon("mark") + " "

    def toggle(setting):
        if set.ifInt(setting) == False:
            setting=0
        if setting == 1:
            return 0
        else:
            return 1

    exit = 0

    while 1:
        options = []
        if settings[0][14] != "":
            importURL = "%s..." % settings[0][14]
        else:
            importURL = "нет"
        if settings[0][17] != "":
            password = settings[0][17]
        else:
            password = "нет"

        options.append(status(settings[0][13]) + "Пункт «нет дома» в первом посещении")
        options.append(status(settings[0][10]) + "Умная строка в первом посещении")
        options.append(status(settings[0][7]) +  "Автоматически записывать повторные посещения")
        options.append(                       "%s Норма часов в месяц: %d" % (icon("box"), settings[0][3]))
        options.append(status(settings[0][2])  + "Кредит часов")
        #if io2.Mode == "sl4a":
        options.append(status(settings[0][11]) + "Уведомления о встречах на сегодня")
        options.append(status(settings[0][8])  + "Напоминать о сдаче отчета")
        options.append(status(settings[0][15]) + "Переносить минуты отчета на следующий месяц")
        options.append(status(settings[0][20]) + "Предлагать разбивку по этажам в многоквартирных домах")
        if io2.Mode == "sl4a":
            options.append(status(settings[0][0])+"Бесшумный режим при включенном таймере")
        options.append(status(settings[0][21]) + "Статус обработки подъездов")
        options.append(status(settings[0][9]) +  "Последний символ посещения влияет на статус контакта")
        options.append(                       "%s Резервных копий: %d" % (icon("box"), settings[0][6]))
        if io2.Simplified==0 and io2.Mode!="sl4a":
            options.append(                   "%s Файл импорта базы данных: %s" % (icon("box"), importURL))
        options.append(                       "%s Пароль на вход: %s" % (icon("box"), password))
        options.append(status(settings[0][16]) + "Режим смайликов")
        options.append(status(settings[0][12]) + "Проверять обновления")
        if io2.Simplified==0 and io2.Mode != "text":
            options.append(status(settings[0][1])+"Консольный режим")

        # settings[0][4] - занято под сортировку контактов!
        # settings[0][19] - занято под сортировку участков!

        # Свободные настройки:
        # settings[0][18]

        choice = dialogs.dialogList(  # display list of settings
            form="preferences",
            title=icon("preferences") + " Настройки " + reports.getTimerIcon(settings[2][6]),
            options=options,
            positive=None,
            negative="Назад"
        )
        if menuProcess(choice)==True:
            continue
        elif choice==None:
            break
        elif set.ifInt(choice) == True:
            result = options[choice]
        else:
            continue

        if "Бесшумный режим" in result:
            settings[0][0] = toggle(settings[0][0])
            io2.save()

        elif "нет дома" in result:
            settings[0][13] = toggle(settings[0][13])
            io2.save()

        elif "Кредит часов" in result:
            settings[0][2] = toggle(settings[0][2])
            io2.save()

        elif "Норма" in result:
            message = "Введите месячную норму часов для подсчета запаса или отставания от нормы по состоянию на текущий день. Если эта функция не нужна, введите пустую строку или 0:"
            while 1:
                choice2 = dialogs.dialogText(
                    title="Месячная норма",
                    message=message,
                    default=str(settings[0][3])
                )
                try:
                    if choice2 != None:
                        if choice2 == "":
                            settings[0][3] = 0
                        else:
                            settings[0][3] = int(choice2)
                        io2.save()
                    else:
                        break
                except:
                    message = "Не удалось изменить, попробуйте еще"
                    continue
                else:
                    break

        elif "Резервных копий" in result:  # backup copies
            while 1:
                choice2 = dialogs.dialogText(
                    title="Число резервных копий",
                    message="От 0 до 10 000:",
                    default=str(settings[0][6]),
                )
                try:
                    if choice2 != None:
                        settings[0][6] = int(choice2)
                        if settings[0][6] > 10000:
                            settings[0][6] = 10000
                        elif settings[0][6] < 0:
                            settings[0][6] = 0
                        io2.save()
                    else:
                        break
                except:
                    io2.log("Не удалось изменить, попробуйте еще")
                    continue
                else:
                    break

        elif "Автоматически записывать" in result:
            settings[0][7] = toggle(settings[0][7])
            io2.save()

        elif "Режим смайликов" in result:
            settings[0][16] = toggle(settings[0][16])
            io2.save()

        elif "Статус обработки подъездов" in result:
            settings[0][21] = toggle(settings[0][21])
            if settings[0][21]==1:
                dialogs.dialogInfo(
                    title="Статус обработки подъездов",
                    message="При включении этого параметра вы сможете указывать для каждого подъезда участка, когда вы в нем были:\n\nв будний день в первой половине дня (первый кружок – 🟡);\n\nв будний день вечером (второй кружок – 🟣);\n\nв выходной (третий кружок – 🔴).\n\nЕсли подъезд посещен все три раза, он учитывается как обработанный в разделе статистики."
                )
            io2.save()

        elif "Умная строка" in result:
            settings[0][10] = toggle(settings[0][10])
            io2.save()

        elif "Напоминать о сдаче" in result:
            settings[0][8] = toggle(settings[0][8])
            io2.save()

        elif "Предлагать разбивку" in result:
            settings[0][20] = toggle(settings[0][20])
            io2.save()

        elif "Уведомления о встречах" in result:
            settings[0][11] = toggle(settings[0][11])
            io2.save()

        elif "Проверять обновления" in result:
            settings[0][12] = toggle(settings[0][12])
            io2.save()

        elif "Последний символ" in result:
            settings[0][9] = toggle(settings[0][9])
            if settings[0][9]==1:
                dialogs.dialogInfo(
                    title="Последний символ посещения влияет на статус контакта",
                    message="Внимание, вы входите в зону хардкора! :) При включении этого параметра в конце каждого посещения должна стоять цифра от 0 до 5. Она определит статус контакта (в стиле «умной строки», только во всех посещениях):\n\n0 = %s\n1 = %s\n2 = %s\n3 = %s\n4 = %s\n5 = %s\n\nЭто должен быть строго последний символ строки. При отсутствии такой цифры статус контакта становится неопределенным (%s)." %
                            ( icon("reject"), icon("interest"), icon("green"), icon("purple"), icon("brown"), icon("danger"), icon("question"))
                )
            io2.save()

        elif "Файл импорта" in result:
            choice2 = dialogs.dialogFileOpen(default=settings[0][14])
            if choice2 != None:
                settings[0][14] = choice2.strip()
                io2.save()

        elif "Переносить минуты" in result:
            settings[0][15] = toggle(settings[0][15])
            io2.save()

        elif "Консольный режим" in result:
            settings[0][1] = toggle(settings[0][1])
            io2.save()

        elif "Пароль на вход" in result:
            choice2 = dialogs.dialogText(
                title=icon("preferences") + " Пароль на вход",
                message="Задайте пароль для входа в программу. Чтобы отменить пароль, сохраните пустое поле:",
                default=str(settings[0][17])
            )
            if choice2 != None:
                settings[0][17] = choice2
                io2.save()

    if exit == 1:
        return True

def stats():
    status0 = status1 = status2 = status3 = status4 = status5 = nostatus = statusQ = returns = returns1 = returns2 = housesDue = porches = porchesCompleted = 0
    flats = records = 0.0

    # while 1:
    # Counting everything
    for h in range(len(houses)):
        d1 = houses[h].date
        d2 = time.strftime("%Y-%m-%d", time.localtime())
        if house_op.days_between(d1, d2) > 122:  # сколько просроченных домов
            housesDue += 1

        for p in range(len(houses[h].porches)):
            porches += 1
            if io2.Simplified==False:
                if houses[h].porches[p].status == "🟡🟣🔴":  # сколько подъездов обработано
                    porchesCompleted += 1

            for f in range(len(houses[h].porches[p].flats)):
                flats += 1
                if houses[h].porches[p].flats[f].status == "0":  # сколько квартир в разных статусах
                    status0 += 1
                if houses[h].porches[p].flats[f].status == "1":
                    status1 += 1
                if houses[h].porches[p].flats[f].status == "2":
                    status2 += 1
                if houses[h].porches[p].flats[f].status == "3":
                    status3 += 1
                if houses[h].porches[p].flats[f].status == "4":
                    status4 += 1
                if houses[h].porches[p].flats[f].status == "5":
                    status5 += 1
                if houses[h].porches[p].flats[f].getStatus()[1] == 4:
                    statusQ += 1
                if houses[h].porches[p].flats[f].status == "":
                    nostatus += 1
                if len(houses[h].porches[p].flats[f].records) > 1:  # квартир с более чем одной записью
                    returns += 1
                if len(houses[h].porches[p].flats[f].records) == 1:  # квартир с одной записью
                    returns1 += 1
                if len(houses[h].porches[p].flats[f].records) >= 2:  # квартир с более чем двумя записями
                    returns2 += 1

    if housesDue == 0:
        due = ""
    else:
        due = icon("warning")
    if records == 0:
        records = 0.0001
    if porches == 0:
        porches = 0.0001
    if flats == 0:
        flats = 0.0001  # чтобы не делить на ноль

    message =    "Участков: " + str(len(houses)) +\
                "\nПросрочено: %d %s" % (housesDue, due) +\
                "\n\nВсего квартир: %d" % flats +\
                "\n\nВ статусе %s: %s (%d%%)" % (icon("reject"), str(status0), status0 / flats * 100) +\
                "\nВ статусе %s: %s (%d%%)" % (icon("interest"), str(status1), status1 / flats * 100) + \
                "\nВ статусе %s: %s (%d%%)" % (icon("green"), str(status2), status2 / flats * 100) + \
                "\nВ статусе %s: %s (%d%%)" % (icon("purple"), str(status3), status3 / flats * 100) + \
                 "\nВ статусе %s: %s (%d%%)" % (icon("brown"), str(status4), status4 / flats * 100) + \
                 "\nВ статусе %s: %s (%d%%)" % (icon("danger"), str(status5), status5 / flats * 100) + \
                 "\nВ статусе %s: %s (%d%%)" % (icon("question"), str(statusQ), statusQ / flats * 100) + \
                 "\n\nБез посещений: %d (%d%%)" % (
                flats - returns1 - returns2, (flats - returns1 - returns2) / flats * 100) +\
                "\nС одним посещением: %d (%d%%)" % (returns1, returns1 / flats * 100) +\
                "\nС повт. посещениями: %d (%d%%)" % (returns2, returns2 / flats * 100)

    if settings[0][21]==1:
        message += "\n\nОбработано подъездов: %d/%d (%d%%)" % \
                        (porchesCompleted, porches, porchesCompleted / porches * 100)

    dialogs.dialogInfo(
        largeText=True,
        title=icon("stats") + " Статистика " + reports.getTimerIcon(settings[2][6]),
        message=message
    )

def search(query=""):
    """ Search flats/contacts """

    if query == "":
        exit = 0
    else:
        exit = 1  # если поисковый запрос задан, только показать результат и выйти
    while 1:
        if query == "":
            query = dialogs.dialogText(  # get search query
                title = icon("search") + " Поиск " + reports.getTimerIcon(settings[2][6]),
                default="",
                message="Найдите любую квартиру или контакт:",
                neutral="Очист."
            )

        elif query == None:
            return

        elif query != None:

            # Valid query, run search

            while 1:
                query = query.lower()
                query = query.strip()
                allContacts = contacts.getContacts(forSearch=True)
                list = []

                for i in range(len(allContacts)):  # start search in flats/contacts
                    found = False
                    if query in allContacts[i][2].lower() or query in allContacts[i][2].lower() or query in \
                            allContacts[i][3].lower() or query in allContacts[i][8].lower() or query in allContacts[i][
                        10].lower() or query in allContacts[i][11].lower() or query in allContacts[i][
                        12].lower() or query in allContacts[i][13].lower():
                        found = True

                    if allContacts[i][8] != "virtual":
                        for r in range(len(houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[
                                               allContacts[i][7][2]].records)):  # in records in flats
                            if query in houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[
                                allContacts[i][7][2]].records[r].title.lower():
                                found = True
                            if query in houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[
                                allContacts[i][7][2]].records[r].date.lower():
                                found = True
                    else:
                        for r in range(len(resources[1][allContacts[i][7][0]].porches[0].flats[
                                               0].records)):  # in records in contacts
                            if query in resources[1][allContacts[i][7][0]].porches[0].flats[0].records[r].title.lower():
                                found = True
                            if query in resources[1][allContacts[i][7][0]].porches[0].flats[0].records[r].date.lower():
                                found = True

                    if found == True:
                        list.append([allContacts[i][7], allContacts[i][8], allContacts[i][2]])

                options2 = []
                for i in range(len(list)):  # save results
                    if list[i][1] != "virtual":  # for regular flats
                        options2.append("%d) %s-%s" % (i + 1, houses[list[i][0][0]].title,
                                                       houses[list[i][0][0]].porches[list[i][0][1]].flats[
                                                           list[i][0][2]].title))
                    else:  # for standalone contacts
                        options2.append("%d) %s, %s" % (
                            i + 1, resources[1][list[i][0][0]].title,
                            resources[1][list[i][0][0]].porches[0].flats[0].title)
                                        )

                if len(options2) == 0:
                    options2.append("Ничего не найдено")

                choice2 = dialogs.dialogList(
                    form="search",
                    title=icon("search") + " Поиск по запросу «%s»" % query,
                    message="Результаты:",
                    options=options2
                )

                # Show results

                if menuProcess(choice2) == True:
                    continue

                elif choice2 == None:
                    if exit == 1:
                        return
                    else:
                        query = ""
                        break

                elif choice2 == "":
                    if exit == 1:
                        return
                    if settings[0][1] == True:
                        break

                elif not "не найдено" in options2[0]:  # go to flat
                    h = list[choice2][0][0]  # получаем номера дома, подъезда и квартиры
                    p = list[choice2][0][1]
                    f = list[choice2][0][2]
                    if list[choice2][1] != "virtual":  # regular contacts
                        delete = territory.flatView(flat=houses[h].porches[p].flats[f], house=houses[h])
                        if delete=="deleted":
                            houses[h].porches[p].deleteFlat(f)
                            io2.save()
                            query == None
                            break

                    else:  # standalone contacts
                        delete = territory.flatView(flat=resources[1][h].porches[0].flats[0], house=resources[1][h], virtual=True)
                        if delete == "deleted":
                            io2.log("«%s» удален" % resources[1][h].porches[0].flats[0].getName())
                            del resources[1][h]
                            io2.save()
                            query == None
                            break

def serviceYear():
    while 1:
        options = []
        for i in range(12):  # filling options by months
            if i < 4:
                monthNum = i + 9
            else:
                monthNum = i - 3
            if settings[4][i] == None:
                options.append(reports.monthName(monthNum=monthNum)[0])
            else:
                if settings[4][i] == settings[0][3]:
                    check = icon("mark")
                elif settings[4][i] < settings[0][3]:
                    check = icon("cross")
                elif settings[4][i] > settings[0][3] and settings[0][3] != 0:
                    check = icon("up")
                else:
                    check = ""
                options.append("%s %d %s" % ((reports.monthName(monthNum=monthNum)[0] + ":", settings[4][i], check)))

        #if int(time.strftime("%m", time.localtime())) <= 9:  # current service year, changes in October
        #    year = "%d" % int(time.strftime("%Y", time.localtime()))
        #else:
        #    year = "%d" % int(time.strftime("%Y", time.localtime()))

        hourSum = 0.0  # total sum of hours
        monthNumber = 0  # months entered
        for i in range(len(settings[4])):
            if settings[4][i] != None:
                hourSum += settings[4][i]
                monthNumber += 1
        yearNorm = float(settings[0][3]) * 12  # other stats
        gap = (12 - monthNumber) * float(settings[0][3]) - (yearNorm - hourSum)
        if gap >= 0:
            gapEmo = icon("extra")
            gapWord = "Запас"
        elif gap < 0:
            gapEmo = icon("slippage")
            gapWord = "Отставание"
        else:
            gapEmo = ""

        # Display dialog

        choice = dialogs.dialogList(
            title="%s Всего %s ч. ⇨ %+d %s %s" % (
                icon("calendar"),
                reports.timeFloatToHHMM(hourSum)[ 0 : reports.timeFloatToHHMM(hourSum).index(":") ],
                gap,
                gapEmo,
                reports.getTimerIcon(settings[2][6])
            ),
            message="Выберите месяц:",
            form="serviceYear",
            neutral=icon("calc") + " Аналитика",
            options=options)

        if choice == None:
            break

        elif choice == "neutral":  # calc

            if monthNumber != 12:
                average = (yearNorm - hourSum) / (12 - monthNumber)  # average
            else:
                average = yearNorm - hourSum
            dialogs.dialogInfo(
                largeText=True,
                title="%s Аналитика" % icon("calc"),
                message="Месяцев введено: %d\n\n" % monthNumber +
                        "Часов введено: %d\n\n" % hourSum +
                        "Годовая норма¹: %d\n\n" % yearNorm +
                        "Осталось часов: %d\n\n" % (yearNorm - hourSum) +
                        "%s: %d %s\n\n" % (gapWord, abs(gap), gapEmo) +
                        "Среднее за месяц²: %0.f\n\n" % average +
                        "____\n" +
                        "¹ Равна 12 * месячная норма (в настройках).\n\n" +
                        "² Среднее число часов, которые нужно служить каждый месяц в оставшиеся (не введенные) месяцы."
            )
        else:
            if choice < 4:
                monthNum = choice + 9
            else:
                monthNum = choice - 3

            if settings[4][choice]!=None:
                options2 = [icon("edit") + " Править ", icon("cut") + " Очистить "]
                choice2 = dialogs.dialogList(
                    title=icon("report") + " %s" % reports.monthName(monthNum=monthNum)[0],
                    options=options2,
                    message="Что делать с месяцем?",
                    form="noteEdit"
                )
            else:
                choice2=0

            if choice2 == 0:  # edit
                if settings[4][choice] != None:
                    default = str(int(settings[4][choice]))
                else:
                    default = ""
                message="Введите значение этого месяца:"
                while 1:
                    choice3 = dialogs.dialogText(
                        title=icon("report") + " %s" % reports.monthName(monthNum=monthNum)[0],
                        message=message,
                        default=default
                    )
                    if choice3 == None:
                        break
                    elif "cancelled!" in choice3:
                        continue
                    elif set.ifInt(choice3)==False or int(choice3)<0:
                        message="Требуется целое положительное число:"
                    else:
                        settings[4][choice] = int(choice3)
                        io2.save()
                        break

            if choice2 == 1:
                settings[4][choice] = None  # clear
                io2.save()
            else:
                continue

def about():
    choice = dialogs.dialogInfo(
        title=icon("help") + " Rocket Ministry " + reports.getTimerIcon(settings[2][6]),
        message =   "Универсальный комбайн вашего служения\n\n"+\
                    "Версия приложения: %s\n\n" % io2.Version +\
                    "Последнее изменение базы данных: %s\n\n" % io2.getDBCreatedTime() +\
                    "Официальная страница: github.com/antorix/Rocket-Ministry\n\n"+\
                    "Официальный Telegram-канал:\nt.me/rocketministry\n\n",
        positive=None,
        neutral="Помощь",
        negative="Назад"
    )
    if choice=="neutral" or choice=="Помощь":
        if io2.Mode=="sl4a":
            from androidhelper import Android
            Android().view("https://github.com/antorix/Rocket-Ministry/blob/master/README.md#часто-задаваемые-вопросы")
            io2.consoleReturn()
        else:
            from webbrowser import open
            open("https://github.com/antorix/Rocket-Ministry/blob/master/README.md#часто-задаваемые-вопросы")

def menuProcess(choice):
    """ Обрабатывает ввод, если он получен из меню (только в easygui)"""
    if io2.Mode!="easygui":
        return False
    result = False
    if choice=="report":
        reports.report()
        result = True
    elif choice=="file":
        fileActions()
        result = True
    elif choice=="settings":
        preferences()
        result = True
    elif choice=="notebook":
        notebook.showNotebook()
        result = True
    elif choice=="exit":
        sys.exit(0)
    return result
