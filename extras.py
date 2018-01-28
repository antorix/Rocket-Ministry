#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import io2
import webbrowser
import dialogs
import reports
import console
import time
from icons import icon
from set import getStatus

if io2.osName=="android":
    from androidhelper import Android
    phone = Android()      

def stats(houses, settings, resources):
    status0 = status1= status2 = status9 = statusQ = statusNo = returns = returns1 = returns2 = returns3 = 0
            
    flats = records = 0.0
    
    # Counting everything
    
    for h in range(len(houses)):
        for p in range(len(houses[h].porches)):
            for f in range(len(houses[h].porches[p].flats)):
                flats+=1
                if houses[h].porches[p].flats[f].status=="0": status0 += 1
                if houses[h].porches[p].flats[f].status=="1": status1 += 1
                if houses[h].porches[p].flats[f].status=="2": status2 += 1
                if houses[h].porches[p].flats[f].status=="9": status9 += 1
                if houses[h].porches[p].flats[f].status=="?": statusQ += 1
                if houses[h].porches[p].flats[f].status=="": statusNo += 1
                for r in range(len(houses[h].porches[p].flats[f].records)):
                    records+=1
                    if len(houses[h].porches[p].flats[f].records)>1: returns += 1
                    if len(houses[h].porches[p].flats[f].records)==1: returns1 += 1
                    if len(houses[h].porches[p].flats[f].records)==2: returns2 += 1
                    if len(houses[h].porches[p].flats[f].records)>=3: returns3 += 1                    

    if records==0: records=0.0001
    if flats==0: flats=0.0001
    #choice=dialogs.dialogInfo(
    choice=dialogs.dialogHelp(
    title = icon("stats", settings[0][4]) + " Статистика " + reports.getTimerIcon(settings[2][6], settings),
    message =   "Участков: " + str(len(houses)) +
    
                "\n\nСоздано квартир: %d" % int(flats) +
                "\nКвартир в статусе %s: %s (%d%%)" % (getStatus("0", settings, type=1)[0], str(status0), status0/flats*100) +
                "\nКвартир в статусе %s: %s (%d%%)" % (getStatus("1", settings, type=1)[0], str(status1), status1/flats*100) +
                "\nКвартир в статусе %s: %s (%d%%)" % (getStatus("2", settings, type=1)[0], str(status2), status2/flats*100) +
                "\nКвартир в статусе %s: %s (%d%%)" % (getStatus("9", settings, type=1)[0], str(status9), status9/flats*100) +
                "\nКвартир в статусе ? : %s (%d%%)" % (str(statusQ), statusQ/flats*100) +
                "\nКвартир без статуса: %s (%d%%)" % (str(statusNo), statusNo/flats*100) +
                
                "\n\nЗаписей посещений: %d" % int(flats) +
                "\nИз них повторных: %d (%d%%) " % (returns, returns/records*100) +
                "\nКвартир с одной записью: %d (%d%%)" % (returns1, returns1/records*100) +
                "\nКвартир с 2 записями: %d (%d%%)" % (returns2, returns2/records*100) +
                "\nКвартир с 3 и более записями: %d (%d%%)" % (returns3, returns3/records*100) +
                
                "\n\nПриблизительная проработанность участков: %d%%" % ((status0+status2+status9)/flats*100) +
                
                "\n\nКонтактов без участков: " + str(len(resources[1]))
        )
    console.process(choice, houses, settings, resources)

def library():    
    if io2.osName=="android":
        try: phone.startActivity(action="ACTION_MAIN",uri=None,type=None,extras=None,wait=True,packagename='org.jw.jwlibrary.mobile',classname='org.jw.jwlibrary.mobile.MainActivity')
        except: io2.log("Не удалось запустить JW Library")
        else: pass# io2.consoleReturn()
    else: webbrowser.open("http://wol.jw.org")

def calendar():    
    if io2.osName=="android":
        from androidhelper import Android
        phone = Android()
        try: phone.startActivity(action="ACTION_MAIN",uri=None,type=None,extras=None,wait=True,packagename="com.android.calendar",classname="com.android.calendar.AllInOneActivity")
        except: io2.log("Не удалось запустить JW Library")
        else: pass# io2.consoleReturn()
    else: webbrowser.open("https://calendar.google.com")

def map(houseTitle):
    
    if io2.osName=="android":        
        try: 
            from androidhelper import Android
            phone = Android() 
            phone.viewMap(houseTitle) 
            os.system("clear")
        except: io2.log("Не удалось выполнить поиск на карте")                                        
        else: io2.consoleReturn()  
        
    else: webbrowser.open("https://yandex.ru/maps/?text=%s" % houseTitle)               

def serviceYear(houses, settings, resources):    
    while 1:            
        if settings[0][5]==1:
            consoleStatus = icon("console", settings[0][4]) + " Консоль"
            buttonStatus = True
        else:
            consoleStatus = ""
            buttonStatus = False
        
        options=[]         
        for i in range(12): # filling options by months
            if i<4: monthNum = i+9
            else: monthNum = i-3
            if settings[4][i]==None: options.append(reports.monthName(monthNum=monthNum)[0])
            else: options.append("%s: %d" % ((reports.monthName(monthNum=monthNum)[0], settings[4][i])))
        
        if io2.osName != "android":
            if io2.Textmode==False: options.append(icon("console", settings[0][4]) + " Консоль") # positive button on Android
            options.append(icon("calc", settings[0][4]) + " Расчеты") # neutral button on Android
        
        if int(time.strftime("%m", time.localtime())) <= 9: # current service year, changes in October
            year = "%d/%d" % ( int(time.strftime("%Y", time.localtime()))-1, int(time.strftime("%Y", time.localtime()))-2000 )
        else: year = "%s/%d" % ( time.strftime("%Y", time.localtime()), int(time.strftime("%Y", time.localtime()))-1999 )
        
        hourSum = 0.0 # total sum of hours
        monthNumber = 0 # months entered
        for i in range(len(settings[4])):
            if settings[4][i] != None:
                hourSum += settings[4][i]
                monthNumber += 1
        yearNorm = float(settings[0][3])*12 # other stats
        gap = (12 - monthNumber) * float(settings[0][3]) - (yearNorm - hourSum)        
        if gap>0: gapEmo = icon("extra", settings[0][4])
        elif gap<0: gapEmo = icon("slippage", settings[0][4])
        else: gapEmo=""
        
        # Display dialog      
                
        try:
            choice = dialogs.dialogList( 
            title = icon("calendar", settings[0][4]) + " %s: итого %d ч. %s %s" % (year, hourSum, gapEmo, reports.getTimerIcon(settings[2][6], settings)), 
            message = "Выберите месяц:",
            form = "serviceYear",
            neutralButton = True,
            neutral = icon("calc", settings[0][4]) + " Расчеты",
            positiveButton = buttonStatus,
            positive = consoleStatus,
            options = options)
        except:
            io2.log("Ошибка вывода")
            return
        choice2=""
        console.process(choice, houses, settings, resources)
        
        if choice==None: break
        
        elif choice=="positive": # console
            if console.dialog(houses, settings, resources)==True: return True 
        
        elif choice=="neutral": # calc     
            
            if monthNumber != 12: average = (yearNorm - hourSum) / (12 - monthNumber) # average
            else: average = yearNorm - hourSum

            #choice1=dialogs.dialogInfo(
            choice1=dialogs.dialogHelp(
                title = icon("calc", settings[0][4]) + " Расчеты " + reports.getTimerIcon(settings[2][6], settings),
                message =   "Месяцев введено: %d\n\n" % monthNumber +
                            "Часов введено: %d\n\n" % hourSum +
                            "Годовая норма¹: %d\n\n" % yearNorm +
                            "Осталось часов: %d\n\n" % (yearNorm - hourSum) +
                            "Отклонение от нормы²: %d %s\n\n" % (gap, gapEmo) +
                            "Среднее за месяц³: %0.1f\n\n" % average +
                            
                            "____\n" +
                            "¹ Равна 12 * месячная норма (в настройках).\n\n" +
                            "² Отклонение от годовой нормы часов исходя из введенных месяцев. Отрицательно, если вы отстаете (плохо), положительно – если образовался запас часов (хорошо).\n\n" +
                            "³ Среднее число часов, которые нужно служить каждый месяц в оставшиеся (не введенные) месяцы.\n\n" +                            
                            "%s Экспериментируйте со всеми полями, чтобы строить планы и прогнозы!" % icon("lamp", settings[0][4])
            )
            console.process(choice1, houses, settings, resources)
        
        else:
            if choice<4: monthNum = choice+9
            else: monthNum = choice-3
            
            options2 = [icon("edit", settings[0][4]) + " Править ", icon("cut", settings[0][4]) + " Очистить "]
            choice2 = dialogs.dialogList(
                title = icon("report", settings[0][4]) + " %s %s " % (reports.monthName(monthNum=monthNum)[0], reports.getTimerIcon(settings[2][6], settings)),
                options=options2,
                message="Что делать с месяцем?",
                form="noteEdit"
            )
            console.process(choice2, houses, settings, resources)

            if choice2==0: # edit            
                if settings[4][choice]!=None: default = str(int(settings[4][choice]))
                else: default=""                
                choice3 = dialogs.dialog(icon("report", settings[0][4]) + " %s %s " % (reports.monthName(monthNum=monthNum)[0], reports.getTimerIcon(settings[2][6], settings)), default=default)
                console.process(choice3, houses, settings, resources)
                if choice3 != None:
                    if "cancelled!" in choice3: continue     
                    try:
                        if choice3!="": settings[4][choice] = int(choice3)
                        else: settings[4][choice] = None
                    except: pass
            
            if choice2==1: settings[4][choice]=None # clear
            
            else: continue
            
            io2.save(houses, settings, resources)
            
def bible():
    if io2.osName=="android":
        from androidhelper import Android
        phone = Android()
        try:
            phone.startActivity(action="ACTION_MAIN",uri=None,type=None,extras=None,wait=True,packagename="com.areastudio.floatingbible",classname="com.areastudio.floatingbible.SplashActivity")
        except: io2.log("Не удалось запустить")
    else:
        webbrowser.open("https://wol.jw.org/ru/wol/binav/r2/lp-u/bi12/U/2007")
        
def viber():
    if io2.osName=="android":
        from androidhelper import Android
        phone = Android()
        try:            
            phone.startActivity(action="ACTION_MAIN",uri=None,type=None,extras=None,wait=True,packagename="com.viber.voip",classname="com.viber.voip.WelcomeActivity")
        except: io2.log("Не удалось запустить")
    else: pass
        #webbrowser.open('C:\Users\antor\AppData\Local\Viber\Viber.exe')
        
def mxplayer():
    if io2.osName=="android":
        from androidhelper import Android
        phone = Android()
        try:            
            phone.startActivity(action="ACTION_MAIN",uri=None,type=None,extras=None,wait=True,packagename="com.mxtech.videoplayer.pro",classname="com.mxtech.videoplayer.pro.ActivityMediaList")
        except: io2.log("Не удалось запустить")
    else:
        webbrowser.open("https://www.jw.org/ru/публикации/видео/#ru/categories/AllVideos")

def modpack(list, position, settings):
    """Insert additional items into list"""
    list.insert(position, icon("viber", settings[0][4]) + " Viber")
    #list.insert(position, "\uD83D\uDC8E" + " JW.org")
    list.insert(position, icon("jwlibrary", settings[0][4]) + " JW Library")
    #list.insert(position, icon("video", settings[0][4]) + " Видео")
    #list.insert(position, icon("bible", settings[0][4]) + " Библия")
    
