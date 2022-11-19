#!/usr/bin/python
# -*- coding: utf-8 -*-

import io2
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

        if io2.Mode == "desktop": # установка шрифта
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

            if io2.settings[0][6] > 0:  # проверяем лишние резервные копии
                io2.backupRestore(delete=True, silent=True)

            if io2.settings[0][11] == 1:
                print("Выясняем встречи на сегодня")
                if len(datedFlats) == 1:
                    dialogs.dialogInfo(
                        title = icon("appointment") + " Встречи на сегодня",
                        message = "Сегодня у вас запланирована встреча! Вас ждет %s." % datedFlats[0].getName(),
                        positive="OK",
                        negative=None

                    )
                    territory.flatView(datedFlats[0])
                elif len(datedFlats) > 1:
                    dialogs.dialogInfo(
                        title = icon("appointment") + " Встречи на сегодня",
                        message = "Сегодня у вас запланированы %d встречи!" % len(datedFlats),
                        positive="OK",
                        negative=None
                    )
                    io2.settings[0][4] = "в"
                    contacts.showContacts()

            print("Определяем начало нового месяца")
            savedMonth = io2.settings[3]
            currentMonth = time.strftime("%b", time.localtime())
            if savedMonth != currentMonth:
                reports.report(newMonthDetected=True)
                io2.settings[3] = time.strftime("%b", time.localtime())
                io2.settings[2][11] = 1
                io2.save()

            if io2.settings[2][11] == 1:
                print("Проверяем сдачу отчета")
                answer = dialogs.dialogConfirm(
                    title=icon("warning") + " Отчет",
                    message="Вы уже сдали отчет?"
                )
                if answer == True:
                    reports.report(disableNotification=True)
                else:
                    reports.report(showLastMonth=True)

            print("Все готово!")

    def weeklyRoutine():

        try:  # проверяем, что прошло больше недели
            today = datetime.datetime.strptime(time.strftime('%Y-%m-%d'), "%Y-%m-%d")
            lastUpdateDate = datetime.datetime.strptime(io2.settings[1], "%Y-%m-%d")
            diff = str(today.date() - lastUpdateDate.date())
            if "," in diff:
                diff = int(diff[0 : diff.index(" ")])
            else:
                diff=0
        except:
            diff=8
        if diff>7 and io2.settings[0][12] == 1:

            limit = 300
            print("Оптимизируем размер журнала отчета")
            if len(io2.resources[2]) > limit:
                extra = len(io2.resources[2]) - limit
                for i in range(extra):
                    del io2.resources[2][len(io2.resources[2]) - 1]

            if io2.update() == True:
                return True

    io2.load()
    if "--capmode" in sys.argv:
        io2.simplified=0
        io2.settings[0][1]=1
    if io2.Mode == "desktop" and io2.settings[0][1] == 0:
        try:
            import desktop
        except:
            print("Класс Desktop не обнаружен")
            io2.Mode = "text"
        else:
            dialogs.MainGUI = desktop.Desktop()

    if io2.settings[1]=="":
        firstRun()

    if weeklyRoutine() == True:
        return

    io2.save(forcedBackup=True)

    if "--capmode" in sys.argv:  # проверяем параметры командной строки
        io2.Simplified=0
        io2.settings[0][1]=1

    while 1:

        appointment = "" # поиск контактов со встречей на сегодня
        totalContacts, datedFlats = contacts.getContactsAmount(date=1)
        if len(datedFlats)>0:
            appointment = icon("appointment")

        dailyRoutine()

        if reports.updateTimer(io2.settings[2][6]) >= 0: # проверка, включен ли таймер
            time2 = reports.updateTimer(io2.settings[2][6])
        else:
            time2 = reports.updateTimer(io2.settings[2][6]) + 24
        if io2.settings[2][6] > 0:
            if io2.Mode != "desktop":
                timerTime = " \u2b1b %s" % reports.timeFloatToHHMM(time2)
            else:
                timerTime = " " + reports.timeFloatToHHMM(time2)
        else:
            if io2.Mode != "desktop":
                timerTime = " \u25b6"
            else:
                timerTime = " "

        if io2.settings[2][11]==1:
            remind = icon("bell")
        else:
            remind=""

        if io2.settings[0][3] != 0:
            if io2.settings[0][2] == True:  # включен кредит часов
                credit = io2.settings[2][1]
            else:
                credit = 0
            gap = reports.getCurrentHours()[1]
            if gap >= 0:
                gap_str = icon("extra")
            else:
                gap_str = icon("slippage", simplified=False)
        else:
            gap_str = ""

        if house_op.calcDueTers() == 0: # подсчет просроченных домов
            due = ""
        else:
            due = icon("warning")

        options = [
                icon("globe") +     " Участки (%d) %s" % (len(io2.houses), due),
                icon("contacts")+   " Контакты (%d) %s" % (totalContacts, appointment),
                icon("report") +    " Отчет (%s) %s %s" % (reports.getCurrentHours()[0], gap_str, remind),
                icon("notebook")+   " Блокнот (%d)" % len(io2.resources[0]),
                icon("search")  +   " Поиск",
                icon("stats")   +   " Статистика (%s%%)" % house_op.countTotalProgress(),
                icon("calendar")+   " Служебный год",
                icon("file")    +   " Файл",
                icon("preferences")+" Настройки",
                icon("info") +      " О программе"
                ]

        if io2.Mode=="desktop" and io2.settings[0][1]==0: # убираем иконки на ПК
            for i in range(len(options)):
                options[i] = options[i][2:]

        if io2.Mode=="text" or io2.settings[0][1]==1:
            title = "Добро пожаловать в Rocket Ministry! Введите help, если нужна помощь по работе в консольном режиме. %s" % reports.getTimerIcon(io2.settings[2][6])
        else:
            title = "🚀 Rocket Ministry " + reports.getTimerIcon(io2.settings[2][6])

        if io2.Simplified == 0:
            negative = "Выход"
        else:
            negative=None

        if io2.Mode == "sl4a":
            io2.clearScreen()
            io2.consoleReturn(pause=False)

        # Run home screen

        if io2.Mode != "desktop" or io2.settings[0][1]!=0:
            choice = dialogs.dialogList(
            form = "home",
            message = "Главная страница, список действий:",
            title = title,
            options = options,
            positive=None,
            neutral = icon("timer") + " Таймер" + timerTime,
            negative=negative
        )
        else:
            territory.terView()
            continue
        if menuProcess(choice)==True:
            continue
        elif choice=="neutral": # таймер
            reports.toggleTimer()
            continue
        elif choice==None and negative!=None:
            return "quit"
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
                if preferences()==True:
                    return True

            elif "О программе" in result:
                if about()==True:
                    return True

            #elif "Выход" in result:
            #    return "quit"

def fileActions():
    """ Program settings on the start screen """

    while 1:

        options = [
            icon("download") + " Импорт из файла",
            icon("export") + " Экспорт",
            icon("restore") + " Восстановление",
            icon("clear") + " Очистка"
        ]

        if io2.Mode == "sl4a":
            options.insert(1, icon("smartphone") + " Импорт из загрузок")

        if io2.Simplified == False:
            options.append(icon("load") + " Загрузка")
            options.append(icon("save") + " Сохранение")

        if io2.Mode == "sl4a":
            options.append(icon("explosion") + " Самоуничтожение")

        if io2.Mode=="desktop" and io2.settings[0][1]==0: # убираем иконки на ПК
            for i in range(len(options)):
                options[i] = options[i][2:]

        choice = dialogs.dialogList(  # display list of settings
            form="tools",
            title=icon("file") + " Файловые операции " + reports.getTimerIcon(io2.settings[2][6]),
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
            io2.load(download=True, forced=True, delete=True)

        elif "Импорт из файла" in result:
            io2.load(dataFile=None, forced=True, delete=True)

        elif "Восстановление" in result:  # restore backup
            io2.backupRestore(restore=True)

        elif "Очистка" in result:
            io2.clearDB(silent=False)

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

def toggle(setting):
    if set.ifInt(setting) == False:
        setting=0
    if setting == 1:
        return 0
    else:
        return 1

def preferences(getOptions=False):
    """ Program preferences """

    def status(setting):
        """ Переключение настройки """
        if setting == 0 or set.ifInt(setting) == False:
            return icon("cross", simplified=False) + " "
        else:
            return icon("mark", simplified=False) + " "

    exit = 0

    while 1:
        options = []
        if io2.settings[0][14] != ".":
            importURL = "%s" % io2.settings[0][14]
        else:
            importURL = "нет"

        options.append(status(io2.settings[0][13]) + "Пункт «нет дома» в первом посещении")
        options.append(status(io2.settings[0][18]) + "Пункт «невозможно попасть» в первом посещении")
        options.append(status(io2.settings[0][10]) + "Умная строка в первом посещении")
        options.append(status(io2.settings[0][7]) +  "Автоматический учет повторных посещений")
        options.append(                       "%s Норма часов в месяц: %d" % (icon("box", simplified=False), io2.settings[0][3]))
        if io2.Mode != "desktop":
            options.append(status(io2.settings[0][20]) + "Режим справочной")
        options.append(status(io2.settings[0][2])  + "Кредит часов")
        options.append(status(io2.settings[0][11]) + "Уведомления о встречах на сегодня")
        options.append(status(io2.settings[0][8])  + "Напоминать о сдаче отчета")
        options.append(status(io2.settings[0][15]) + "Переносить минуты отчета на следующий месяц")
        if io2.Mode == "sl4a":
            options.append(status(io2.settings[0][0])+"Бесшумный режим при включенном таймере")
        options.append(status(io2.settings[0][21]) + "Статус обработки подъездов")
        options.append(status(io2.settings[0][9]) +  "Обновление статуса цифрой в посещении")
        options.append(                       "%s Резервных копий: %d" % (icon("box", simplified=False), io2.settings[0][6]))
        if io2.Simplified==0 and io2.Mode!="sl4a":
            options.append(                   "%s Файл импорта базы данных: %s" % (icon("box", simplified=False), importURL))
        if io2.Mode == "sl4a":
            options.append(status(io2.settings[0][16]) + "Режим смайликов")
        options.append(status(io2.settings[0][12]) + "Проверять обновления")
        #if io2.Mode != "text":
        #    options.append(status(io2.settings[0][1])  + "Консольный режим")
        if io2.Simplified == 0:
            options.append(status(territory.GridMode) + "Консольный вид подъезда")

        # settings[0][4] - занято под сортировку контактов!

        # settings[0][19] - занято под сортировку участков!

        # settings[0][17] - свободно

        if getOptions==True:
            return options

        choice = dialogs.dialogList(  # display list of settings
            form="preferences",
            title=icon("preferences") + " Настройки " + reports.getTimerIcon(io2.settings[2][6]),
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

        feedSetting(result)

    if exit == 1:
        return True

def feedSetting(result, self=None):
    """ Получает строку и по ней выставляет настройку """

    if io2.Mode == "desktop" and io2.settings[0][1] == 0:
        dialogs.MainGUI.getWindowPosition()

    if "Бесшумный режим" in result:
        io2.settings[0][0] = toggle(io2.settings[0][0])
        io2.save()

    elif "нет дома" in result:
        io2.settings[0][13] = toggle(io2.settings[0][13])
        io2.save()

    elif "Кредит часов" in result:
        io2.settings[0][2] = toggle(io2.settings[0][2])
        io2.save()

    elif "Норма" in result:
        message = "Введите месячную норму часов для подсчета запаса или отставания от нормы по состоянию на текущий день. Если эта функция не нужна, введите пустую строку или 0:"
        while 1:
            choice2 = dialogs.dialogText(
                height=5,
                title="Месячная норма",
                message=message,
                default=str(io2.settings[0][3])
            )
            try:
                if choice2 != None:
                    if choice2 == "":
                        io2.settings[0][3] = 0
                    else:
                        io2.settings[0][3] = int(choice2)
                    if io2.Mode == "desktop" and io2.settings[0][1] == 0:
                        self.settingsMenu.entryconfig(4, label="Норма часов в месяц: %d" % io2.settings[0][3])
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
                default=str(io2.settings[0][6]),
            )
            try:
                if choice2 != None:
                    io2.settings[0][6] = int(choice2)
                    if io2.settings[0][6] > 10000:
                        io2.settings[0][6] = 10000
                    elif io2.settings[0][6] < 0:
                        io2.settings[0][6] = 0
                    if io2.Mode == "desktop" and io2.settings[0][1] == 0:
                        self.settingsMenu.entryconfig(11, label="Резервных копий: %s" % choice2)
                    io2.save()
                else:
                    break
            except:
                io2.log("Не удалось изменить, попробуйте еще")
                continue
            else:
                break

    elif "Автоматический учет" in result:
        io2.settings[0][7] = toggle(io2.settings[0][7])
        io2.save()

    elif "Режим смайликов" in result:
        io2.settings[0][16] = toggle(io2.settings[0][16])
        io2.save()

    elif "Статус обработки подъездов" in result:
        io2.settings[0][21] = toggle(io2.settings[0][21])
        if io2.settings[0][21] == 1:
            dialogs.dialogInfo(
                doublesize=True,
                title="Статус обработки подъездов",
                message="При включении этого параметра вы сможете указывать для каждого подъезда участка, когда вы в нем были:\n\nв будний день в первой половине дня (первый кружок – %s)\n\nв будний день вечером (второй кружок – %s)\n\nв выходной (третий кружок – %s)\n\nЕсли подъезд посещен все три раза, он учитывается как обработанный в разделе статистики." % (
                icon("porchCircle1"), icon("porchCircle2"), icon("porchCircle3")),
                positive="OK",
                negative=None
            )
        io2.save()

    elif "Режим справочной" in result:
        io2.settings[0][20] = toggle(io2.settings[0][20])
        io2.save()

    elif "Умная строка" in result:
        io2.settings[0][10] = toggle(io2.settings[0][10])
        io2.save()

    elif "Напоминать о сдаче" in result:
        io2.settings[0][8] = toggle(io2.settings[0][8])
        io2.save()

    elif "невозможно попасть" in result:
        io2.settings[0][18] = toggle(io2.settings[0][18])
        io2.save()

    elif "Уведомления о встречах" in result:
        io2.settings[0][11] = toggle(io2.settings[0][11])
        io2.save()

    elif "Проверять обновления" in result:
        io2.settings[0][12] = toggle(io2.settings[0][12])
        io2.save()

    elif "Пароль на вход " in result:
        choice2 = dialogs.dialogText(
            title=icon("preferences") + " Пароль на вход",
            message="Здесь можно задать пароль на вход в программу. Запомните его как следует – восстановление пароля не предусмотрено! Также в целях безопасности будут удалены все резервные копии, созданные до установки пароля. Чтобы отменить существующий пароль (если есть), сохраните пустое поле:",
            height=7
        )
        if choice2 == None:
            pass
        elif choice2 != "":
            io2.settings[0][16] = choice2
            io2.removeFiles(keepDatafile=True)
            io2.log("Пароль установлен")
        else:
            io2.settings[0][16] = ""
            io2.log("Пароль не установлен")
        io2.save()

    elif "Обновление статуса" in result:
        io2.settings[0][9] = toggle(io2.settings[0][9])
        if io2.settings[0][9] == 1:
            dialogs.dialogInfo(
                doublesize=True,
                title="Обновление статуса цифрой в посещении",
                message="Здесь можно переключиться на альтернативный способ обновления статуса контакта после каждого посещения. Теперь, вместо ручного выбора статуса, нужно ставить цифру от 0 до 5 в конце каждого посещения. Эта цифра определяет статус контакта (как в «умной строке»):\n\n0 = %s\n1 = %s\n2 = %s\n3 = %s\n4 = %s\n5 = %s\n\nЭто должен быть строго последний символ строки. При отсутствии такой цифры статус контакта становится неопределенным (%s)." %
                        (icon("reject"), icon("interest"), icon("green"), icon("purple"), icon("brown"), icon("danger"),
                         icon("question")),
                positive="OK",
                negative=None
            )
        io2.save()

    elif "Файл импорта" in result:
        choice2 = dialogs.dialogFileOpen(default=io2.settings[0][14])
        if choice2 != ".":
            io2.settings[0][14] = choice2.strip()
        else:
            choice2="нет"
        if io2.Mode == "desktop" and io2.settings[0][1] == 0:
            self.settingsMenu.entryconfig(12, label="Файл импорта базы данных: %s" % choice2)
        io2.save()

    elif "Переносить минуты" in result:
        io2.settings[0][15] = toggle(io2.settings[0][15])
        io2.save()

    elif "Консольный режим" in result:
        io2.settings[0][1] = toggle(io2.settings[0][1])
        io2.save()
        if io2.Mode == "desktop":
            if io2.settings[0][1] == 1:
                io2.settings[0][1] = 0
                dialogs.dialogInfo(
                    title="Внимание",
                    message="Чтобы войти в консольный режим, программа должна быть запущена через файл Rocket Ministry.py или main.py.",
                    positive="OK",
                    negative=None,
                )
                io2.settings[0][1] = 1
            else:
                try:
                    import desktop
                except:
                    print("Класс Desktop не обнаружен")
                    io2.Mode = "text"
                else:
                    try:
                        dialogs.MainGUI.update()
                    except:
                        dialogs.MainGUI = desktop.Desktop()

    elif set.r()[0] in result:
        choice2 = dialogs.dialogGetLib(
            title=icon("preferences") + " %s" % set.r()[0],
            message=set.r()[1],
            height=7,
            lib=False
        )
        if choice2 == None:
            if io2.Mode == "desktop" and io2.settings[0][1] == 0:
                self.settingsMenu.entryconfig(13, label="%s нет" % set.r()[0])
            io2.save()
        elif choice2 != "":
            set.r(choice=choice2, set=True)
            if io2.Mode=="desktop" and io2.settings[0][1]==0:
                self.settingsMenu.entryconfig(13, label="%s %s" % (set.r()[0], set.r(choice=choice2, set=True, replace=True, getO=True)))
            io2.save()
        else:
            del io2.resources[2][0]
            io2.resources[2].insert(0, "")
            set.SysMarker = ""
            io2.log(set.r()[3])
            if io2.Mode == "desktop" and io2.settings[0][1] == 0:
                self.settingsMenu.entryconfig(13, label="%s нет" % set.r()[0])
            io2.save()

    elif "Консольный вид" in result:
        territory.GridMode = toggle(territory.GridMode)

    if io2.Mode == "desktop" and io2.settings[0][1] == 0 and self!=None:
        self.update(choices = self.choices)

def stats():
    status0 = status1 = status2 = status3 = status4 = status5 = nostatus = statusQ = returns = returns1 = returns2 = housesDue = porches = porchesCompleted = 0
    flats = records = percentage = worked = 0.0

    for house in io2.houses:
        d1 = house.date
        d2 = time.strftime("%Y-%m-%d", time.localtime())
        if house_op.days_between(d1, d2) > 122:  # сколько просроченных домов
            housesDue += 1
        percentage += house.getProgress()[0]
        worked += house.getProgress()[1]

        for porch in house.porches:
            porches += 1
            if porch.status == "🟡🟣🔴" or porch.status == "●●●":  # сколько подъездов обработано
                porchesCompleted += 1

            for flat in porch.flats:
                if "." in flat.number:
                    continue
                flats += 1
                if flat.status == "0":  # сколько квартир в разных статусах
                    status0 += 1
                if flat.status == "1":
                    status1 += 1
                if flat.status == "2":
                    status2 += 1
                if flat.status == "3":
                    status3 += 1
                if flat.status == "4":
                    status4 += 1
                if flat.status == "5":
                    status5 += 1
                if flat.getStatus()[1] == 4:
                    statusQ += 1
                if flat.status == "":
                    nostatus += 1
                if len(flat.records) > 1:  # квартир с более чем одной записью
                    returns += 1
                if len(flat.records) == 1:  # квартир с одной записью
                    returns1 += 1
                if len(flat.records) >= 2:  # квартир с более чем двумя записями
                    returns2 += 1

    if len(io2.houses)>0:
        percentage = int( percentage / len(io2.houses) * 100 )
    else:
        percentage = 0

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

    message =    "Участков: " + str(len(io2.houses)) +\
                "\nПросрочено: %d %s" % (housesDue, due) +\
                "\n\nУровень обработки: %d/%d (%d%%)" % (worked, flats, percentage) +\
                "\n\nВ статусе %s: %s (%d%%)" % (icon("reject"), str(status0), status0 / flats * 100) +\
                "\nВ статусе %s: %s (%d%%)" % (icon("interest"), str(status1), status1 / flats * 100) + \
                "\nВ статусе %s: %s (%d%%)" % (icon("green"), str(status2), status2 / flats * 100) + \
                "\nВ статусе %s: %s (%d%%)" % (icon("purple"), str(status3), status3 / flats * 100) + \
                 "\nВ статусе %s: %s (%d%%)" % (icon("brown"), str(status4), status4 / flats * 100) + \
                 "\nВ статусе %s: %s (%d%%)" % (icon("danger"), str(status5), status5 / flats * 100) + \
                 "\nВ статусе %s: %s (%d%%)" % (icon("question"), str(statusQ), statusQ / flats * 100)# + \
                 #"\n\nБез посещений: %d (%d%%)" % (flats - worked, (flats - worked) / flats * 100) +\
                #"\nС одним посещением: %d (%d%%)" % (returns1, returns1 / flats * 100) +\
                #"\nС повт. посещениями: %d (%d%%)" % (returns2, returns2 / flats * 100)

    if io2.settings[0][21]==1:
        message += "\n\nОбработано подъездов: %d/%d (%d%%)" % \
                        (porchesCompleted, porches, porchesCompleted / porches * 100)

    dialogs.dialogInfo(
        doublesize=True,
        title=icon("stats") + " Статистика " + reports.getTimerIcon(io2.settings[2][6]),
        message=message,
        positive=None,
        negative="Назад"
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
                title = icon("search") + " Поиск " + reports.getTimerIcon(io2.settings[2][6]),
                default="",
                message="Найдите любую квартиру или контакт:",
                neutral="Очист."
            )
            if query == None or query=="":
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
                        for r in range(len(io2.houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[
                                               allContacts[i][7][2]].records)):  # in records in flats
                            if query in io2.houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[
                                allContacts[i][7][2]].records[r].title.lower():
                                found = True
                            if query in io2.houses[allContacts[i][7][0]].porches[allContacts[i][7][1]].flats[
                                allContacts[i][7][2]].records[r].date.lower():
                                found = True
                    else:
                        for r in range(len(io2.resources[1][allContacts[i][7][0]].porches[0].flats[
                                               0].records)):  # in records in contacts
                            if query in io2.resources[1][allContacts[i][7][0]].porches[0].flats[0].records[r].title.lower():
                                found = True
                            if query in io2.resources[1][allContacts[i][7][0]].porches[0].flats[0].records[r].date.lower():
                                found = True

                    if found == True:
                        list.append([allContacts[i][7], allContacts[i][8], allContacts[i][2]])

                options2 = []
                for i in range(len(list)):  # save results
                    if io2.Mode == "text" or io2.settings[0][1] == 1:
                        number = ""
                    else:
                        number = "%d) " % (i+1)
                    if list[i][1] != "virtual":  # for regular flats
                        options2.append("%s%s-%s" % (number, io2.houses[list[i][0][0]].title,
                                                       io2.houses[list[i][0][0]].porches[list[i][0][1]].flats[
                                                           list[i][0][2]].title))
                    else:  # for standalone contacts
                        if io2.resources[1][list[i][0][0]].title == "":
                            title = ""
                        else:
                            title = io2.resources[1][list[i][0][0]].title + ", "
                        options2.append("%s%s%s" % (
                            number,
                            title,
                            io2.resources[1][list[i][0][0]].porches[0].flats[0].title))

                if len(options2) == 0:
                    options2.append("Ничего не найдено")

                # Show results

                choice2 = dialogs.dialogList(
                    form="search",
                    title=icon("search") + " Поиск по запросу «%s»" % query,
                    message="Результаты:",
                    options=options2
                )

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
                    if io2.settings[0][1] == True:
                        break

                elif not "не найдено" in options2[0]:  # go to flat
                    h = list[choice2][0][0]  # получаем номера дома, подъезда и квартиры
                    p = list[choice2][0][1]
                    f = list[choice2][0][2]
                    if list[choice2][1] != "virtual":  # regular contacts
                        result = territory.flatView(flat=io2.houses[h].porches[p].flats[f], house=io2.houses[h])
                        if result =="deleted":
                            io2.houses[h].porches[p].deleteFlat(f)
                            io2.save()
                            #query = None
                            break
                        elif result == "createdRecord" and io2.settings[0][9] == 0:
                            set.flatSettings(flat=io2.houses[h].porches[p].flats[f], house=io2.houses[h], jumpToStatus=True)
                            continue

                    else:  # standalone contacts
                        result = territory.flatView(flat=io2.resources[1][h].porches[0].flats[0], house=io2.resources[1][h], virtual=True)
                        if result == "deleted":
                            io2.log("Контакт %s удален" % io2.resources[1][h].porches[0].flats[0].getName())
                            del io2.resources[1][h]
                            io2.save()
                            #query = None
                            break
                        elif result == "createdRecord" and io2.settings[0][9] == 0:
                            set.flatSettings(flat=io2.resources[1][h].porches[0].flats[0], house=io2.resources[1][h], jumpToStatus=True)
                            continue

def serviceYear(count=False):
    while 1:
        options = []
        for i in range(12):  # filling options by months
            if i < 4:
                monthNum = i + 9
            else:
                monthNum = i - 3
            if io2.settings[4][i] == None:
                options.append(reports.monthName(monthNum=monthNum)[0])
            else:
                if io2.settings[4][i] == io2.settings[0][3]:
                    check = icon("mark")
                elif io2.settings[4][i] < io2.settings[0][3]:
                    check = icon("cross")
                elif io2.settings[4][i] > io2.settings[0][3] and io2.settings[0][3] != 0:
                    check = icon("up")
                else:
                    check = ""
                options.append("%s %d %s" % ((reports.monthName(monthNum=monthNum)[0] + ":", io2.settings[4][i], check)))

        #if int(time.strftime("%m", time.localtime())) <= 9:  # current service year, changes in October
        #    year = "%d" % int(time.strftime("%Y", time.localtime()))
        #else:
        #    year = "%d" % int(time.strftime("%Y", time.localtime()))

        hourSum = 0.0  # total sum of hours
        monthNumber = 0  # months entered
        for i in range(len(io2.settings[4])):
            if io2.settings[4][i] != None:
                hourSum += io2.settings[4][i]
                monthNumber += 1
        yearNorm = float(io2.settings[0][3]) * 12  # other stats
        gap = (12 - monthNumber) * float(io2.settings[0][3]) - (yearNorm - hourSum)
        if count==True:
            return gap
        if gap >= 0:
            gapEmo = icon("extra")
            gapWord = "Запас"
        elif gap < 0:
            gapEmo = icon("slippage")
            gapWord = "Отставание"
        else:
            gapEmo = ""
        if io2.settings[0][3]!=0:
            neutral = icon("calc") + " Аналитика"
        else:
            neutral = None
        title = "%s Всего %s ч." % (icon("calendar"), reports.timeFloatToHHMM(hourSum)[ 0 : reports.timeFloatToHHMM(hourSum).index(":") ],)
        if io2.settings[0][3] != 0:
            title += " ⇨ %+d %s %s" % (gap, gapEmo, reports.getTimerIcon(io2.settings[2][6]))

        # Display dialog

        choice = dialogs.dialogList(
            title=title,
            message="Выберите месяц:",
            form="serviceYear",
            neutral=neutral,
            options=options)

        if menuProcess(choice)==True:
            continue

        elif choice == None:
            break

        elif choice == "x":
            continue

        elif choice == "neutral":  # calc

            if monthNumber != 12:
                average = (yearNorm - hourSum) / (12 - monthNumber)  # average
            else:
                average = yearNorm - hourSum
            dialogs.dialogInfo(
                doublesize=True,
                title="%s Аналитика" % icon("calc"),
                message="Месяцев введено: %d\n\n" % monthNumber +
                        "Часов введено: %d\n\n" % hourSum +
                        "Годовая норма¹: %d\n\n" % yearNorm +
                        "Осталось часов: %d\n\n" % (yearNorm - hourSum) +
                        "%s: %d %s\n\n" % (gapWord, abs(gap), gapEmo) +
                        "Среднее за месяц²: %0.f\n\n" % average +
                        "____\n" +
                        "¹ Равна 12 * месячная норма (в настройках).\n\n" +
                        "² Среднее число часов, которые нужно служить каждый месяц в оставшиеся (не введенные) месяцы.",
                negative="Назад"
            )
        else:
            if choice < 4:
                monthNum = choice + 9
            else:
                monthNum = choice - 3
            if io2.settings[4][choice]!=None:
                options2 = [icon("edit") + " Править ", icon("cut") + " Очистить "]
                if io2.Mode == "desktop" and io2.settings[0][1] == 0:  # убираем иконки на ПК
                    for i in range(len(options2)):
                        options2[i] = options2[i][2:]
                choice2 = dialogs.dialogList(
                    title=icon("report") + " %s" % reports.monthName(monthNum=monthNum)[0],
                    options=options2,
                    message="Что делать с месяцем?",
                    form="noteEdit"
                )
            else:
                choice2=0

            if choice2 == 0:  # edit
                if io2.settings[4][choice] != None:
                    default = str(int(io2.settings[4][choice]))
                else:
                    default = ""
                message="Введите значение этого месяца:"
                while 1:
                    choice3 = dialogs.dialogText(
                        title=icon("report") + " %s" % reports.monthName(monthNum=monthNum)[0],
                        message=message,
                        default=default,
                        height=1
                    )
                    if choice3 == None:
                        break
                    elif "cancelled!" in choice3:
                        continue
                    elif set.ifInt(choice3)==False or int(choice3)<0:
                        message="Требуется целое положительное число:"
                    else:
                        io2.settings[4][choice] = int(choice3)
                        io2.save()
                        break

            if choice2 == 1:
                io2.settings[4][choice] = None  # clear
                io2.save()
            else:
                continue

def about():
    while 1:
        choice = dialogs.dialogInfo(
            title=icon("info") + " О программе " + reports.getTimerIcon(io2.settings[2][6]),
            largeText=True,
            message =   "Универсальный комбайн вашего служения\n\n"+\
                        "Версия приложения: %s\n\n" % io2.Version +\
                        "Последнее изменение базы данных: %s\n\n" % io2.getDBCreatedTime() +\
                        "Официальная страница:\ngithub.com/antorix/Rocket-Ministry\n\n"+\
                        "Официальный Telegram-канал:\nt.me/rocketministry",
            positive = icon("update") + " Обновл.",
            neutral = icon("help") + " Помощь",
            negative="Назад"
        )
        if choice=="positive":
            if io2.update(forced=True) == True:
                return True
        elif choice=="neutral":
            helpPage = "https://github.com/antorix/Rocket-Ministry/wiki#часто-задаваемые-вопросы"
            if io2.Mode=="sl4a":
                time.wait(0.5)
                from androidhelper import Android
                Android().view(helpPage)
                io2.consoleReturn()
            else:
                from webbrowser import open
                open(helpPage)
        else:
            break

def menuProcess(choice):
    """ Обрабатывает ввод, если он получен из меню (только на ПК)"""
    if io2.Mode!="desktop":
        return False
    result = False
    if choice=="ter":
        territory.terView()
        result = True
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
    elif choice=="home":
        territory.terView()
        result = True
    elif choice=="about":
        about()
        result = True
    elif choice=="timer":
        reports.toggleTimer()
        result = True
    elif choice=="contacts":
        contacts.showContacts()
        result = True
    elif choice=="statistics":
        stats()
        result = True
    elif choice=="serviceyear":
        serviceYear()
        result = True
    elif choice == "import":
        io2.load(dataFile=None, forced=True, delete=True)
    elif choice == "export":
        io2.share()
    elif choice == "restore":
        io2.backupRestore(restore=True)
    elif choice == "wipe":
        io2.clearDB(silent=False)
    elif choice == "exit":
        io2.share(silent=True)
        #sys.exit(0)
    return result
