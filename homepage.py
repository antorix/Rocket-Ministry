#!/usr/bin/python
# -*- coding: utf-8 -*-

import io2       
import territory
import contacts
import dialogs
import reports
import set
import notebook
import console
import extras
import sys
import os
import webbrowser
from icons import icon
from main import version

def homepage(houses, settings, resources):
    """ Home page """
    
    if "--console" in sys.argv: console.dialog(houses, settings, resources)
    
    while 1:            
            # Prepare data
            
            reports.report(houses, settings, resources, stop=True) # check new month
            
            if reports.updateTimer(settings[2][6])>=0: time2 = reports.updateTimer(settings[2][6])
            else: time2 = reports.updateTimer(settings[2][6]) + 24
            
            if settings[2][6] > 0: timerTime = " \u2b1b %0.2f ч." % time2 # check if timer is on to show time
            else: timerTime=" \u25b6"
            
            if settings[0][8]==1 and settings[2][11]==1: # report reminder
                remind = icon("lamp", settings[0][4])
            else: remind=""
            
            appointment = "" # сounting contacts and check closest appointment date, if enabled
            totalContacts, datedFlats = contacts.getContactsAmount(houses, resources, settings[0][11])
            if len(datedFlats)>0: appointment = icon("appointment", settings[0][4])
            else: appointment = ""
            
            options = [
                    icon("timer", settings[0][4])   + " Таймер" + timerTime,
                    icon("report", settings[0][4])  + " Отчет (%0.2f ч.)  %s" % (settings[2][0], remind),
                    icon("globe", settings[0][4])   + " Участки (%d)" % len(houses),
                    icon("contacts", settings[0][4])+ " Контакты (%d)  %s" % (totalContacts, appointment),
                    icon("notebook", settings[0][4])+ " Блокнот (%d)" % len(resources[0]),
                    icon("search", settings[0][4])  + " Поиск",
                    icon("console", settings[0][4]) + " Консоль",
                    icon("stats", settings[0][4])   + " Статистика",
                    icon("report", settings[0][4])  + " Служебный год",
                    icon("file", settings[0][4])    + " Файл",
                    icon("help", settings[0][4])    + " Справка"
                ]
            if io2.Textmode==True: del options[5]
            
            if io2.osName != "android": options.append(icon("preferences", settings[0][4]) + " Настройки") # neutral button on Android
            
            # Append mod items
            if io2.Mod==True: extras.modpack(options, 5, settings)
            
            # Run home screen
            try:
                choice = dialogs.dialogList( # display list of houses and options
                    form = "main",
                    title = icon("rocket", settings[0][4]) + " Prompt Ministry " + reports.getTimerIcon(settings[2][6], settings), # houses sorting type, timer icon
                    message = "Выберите раздел:",
                    options = options,
                    cancel = "Выход",
                    neutral = icon("preferences", settings[0][4]) + " Настройки",
                    neutralButton = True
                )
            except:
                io2.log("Ошибка вывода")
                return            
            console.process(choice, houses, settings, resources)
            
            if contacts.ifInt(choice)==True: result = options[choice]
            else: result = choice
            
            if result==None: # exit
                choice2 = dialogs.dialogConfirm(
                    title = " Prompt Ministry " + reports.getTimerIcon(settings[2][6], settings),
                    message = "Действительно выйти?",
                    neutralButton=True,
                    choices=["Да", "Да и экспорт", "Нет"]
                )
                console.process(choice2, houses, settings, resources)
                
                if choice2 == True: sys.exit(0)
                elif choice2=="neutral":
                    io2.share(houses, settings, resources, manual=True)
                    sys.exit(0)
                elif choice2==False: continue
                
            elif "neutral" in result: set.preferences(houses, settings, resources) # program settings
                
            elif "Таймер" in result: # start/stop timer
                if settings[2][6] == 0: reports.report(houses, settings, resources, choice="%(")
                else: reports.report(houses, settings, resources, choice="%)")
                
            elif "Отчет" in result: reports.report(houses, settings, resources) # report
                
            elif "Участки" in result: territory.terView(houses, settings, resources) # territory
                
            elif "Контакты" in result: contacts.showContacts(houses, settings, resources) # contacts
                
            elif "Блокнот" in result: notebook.showNotebook(houses, settings, resources) # notebook
            
            elif "Поиск" in result: set.search(houses, settings, resources) # search
            
            elif "Консоль" in result: console.dialog(houses, settings, resources) # console
            
            elif "Статистика" in result: extras.stats(houses, settings, resources) # stats
        
            elif "Служебный год" in result: extras.serviceYear(houses, settings, resources) # service year 
            
            elif "Файл" in result: houses, settings, resources, exit = set.tools(houses, settings, resources) # tools
            
            elif "Справка" in result: # help
                if io2.osName=="android":
                    if os.path.exists(io2.AndroidUserPath + "help.txt"):   
                        with open(io2.AndroidUserPath + "help.txt", encoding="utf-8") as file: help = file.read()
                        choice=dialogs.dialogHelp(
                            title=icon("help", settings[0][4]) + " Справка (Prompt Ministry %s) %s" % (version, reports.getTimerIcon(settings[2][6], settings)),
                            message=help
                        )
                        console.process(choice, houses, settings, resources)
                    else: io2.log("Файл справки не найден! Попробуйте перезагрузить архив программы")
                else:
                    if os.path.exists("help.txt"):   
                        with open("help.txt", encoding="utf-8") as file: help = file.read()
                        choice=dialogs.dialogHelp(
                            title=icon("help", settings[0][4]) + " Справка (Prompt Ministry %s) %s" % (version, reports.getTimerIcon(settings[2][6], settings)),
                            message=help
                        )
                        console.process(choice, houses, settings, resources)
                        
                    else: io2.log("Файл справки не найден! Попробуйте перезагрузить архив программы")
                    
            elif "Библия" in result: extras.bible()
            
            elif "Видео" in result: extras.mxplayer()
                    
            elif "Viber" in result: extras.viber()
            
            elif "JW.org" in result: webbrowser.open("https://www.jw.org/ru/")
            
            elif "JW Library" in result: extras.library()
