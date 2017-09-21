#!/usr/bin/python
# -*- coding: utf-8 -*-

import io2
import extras
import os
import dialogs
import webbrowser
import reports
import sys
import time
import contacts
import notebook
import house_op
import house_cl
import set
import territory
from icons import icon

def dialog(houses, settings, resources, houseTitle=""):
    """ Runs dialog window for console """
    
    if io2.Textmode==True or "--textconsole" in sys.argv: pureText=True
    else: pureText=False
    default=""
    
    while 1: 
        input = dialogs.dialog(
            title = icon("console", settings[0][4], pureText=pureText) + " Консоль " + reports.getTimerIcon(settings[2][6], settings),
            message="Введите команду (или символ _ для выполнения %s):" % settings[0][13],
            default=default
        )
        if input != None and not "cancelled" in input:
            if process(input, houses, settings, resources)==True: return True
            
        elif input != None and "cancelled!" in input:
            default=input[10:]
            continue
                
        else: return False

def process(inputOrig, houses, settings, resources, houseTitle=""):
    """ Interpreting commands taken from dialog or outside"""
    exit=False
    input = str(inputOrig).strip()    
    
    if input=="_": input = settings[0][13] # Substitution of default command
    elif input==None or input=="": return exit
    else: input = input.lower()       
    
    if "%" in input[0]: # update report
        reports.report(houses, settings, resources, choice=input)
        
    if "rep" in input[:3]: # view report
        reports.report(houses, settings, resources, choice="%")
        
    if "credit" in input[:6] or "₽" in input[0]: # manual interception and saving credit hours from regular timer
        if settings[0][2]==0:
            io2.log("Включите учет кредита в настройках")
        elif settings[2][6]!=0:
            endTime = int(time.strftime("%H", time.localtime()))*3600 + int(time.strftime("%M", time.localtime()))*60 + int(time.strftime("%S", time.localtime()))
            reportTime = (endTime - settings[2][6])/3600
            settings[2][1] += reportTime
            settings[2][6] = 0
            io2.logReport("Таймер остановлен, в отчет добавлено: %.2f ч. кредита" % reportTime)
            reportTime = 0.0
            reports.vibrate(False, settings)
            io2.save(houses, settings, resources)

    if "{" in input and "}" in input: # update report
        reports.report(houses, settings, resources, choice=input[input.index("{"):input.index("}")])

    if "/ж" in input or "/б" in input or "/к" in input or "/ч" in input or "/р" in input or "/в" in input or "/п" in input or "/и" in input or "=ж" in input or "=б" in input or "=к" in input or "=ч" in input or "=р" in input or "=в" in input or "=п" in input or "=и" in input : # update report
        reports.report(houses, settings, resources, choice="   ") # check new month
        message="В отчет добавлено:"
        for i in range(len(input)):
            if input[i]=="/" or input[i]=="=":
                if input[i+1]=="ч":
                    settings[2][0] += 1
                    message += "\nчас"
                if input[i+1]=="р":
                    settings[2][1] += 1
                    message += "\nчас кредита"
                if input[i+1]=="б":
                    settings[2][2] += 1
                    message += "\nпубликация"
                if input[i+1]=="ж":
                    settings[2][2] += 1
                    message += "\nпубликация"
                if input[i+1]=="к":
                    settings[2][2] += 1
                    message += "\nпубликация"
                if input[i+1]=="в":
                    settings[2][3] += 1
                    message += "\nвидео"
                if input[i+1]=="п":
                    settings[2][4] += 1
                    message += "\nПП"
                if input[i+1]=="и":
                    settings[2][5] += 1
                    message += "\nИБ"
        io2.logReport(message)
        io2.save(houses, settings, resources)
    
    if "note" in input[:4] or "()" in input [:2]: # notes    
        notebook.showNotebook(houses, settings, resources)
    
    if "contact" in input[:7] or "©" in input[0] or "//" in input[:2]: # contacts
        contacts.showContacts(houses, settings, resources)

    if "save" in input[:4] or "$" in input[0]: # save
        io2.save(houses, settings, resources, manual=True)
        
    if "send" in input[:4] or "^" in input[0]: # share
        io2.share(houses, settings, resources)
        
    if "help" in input[:4] or "??" in input[:2]: # load
        if io2.osName=="android":
            if os.path.exists("/storage/sdcard0/qpython/projects3/Prompt Ministry/help.txt"):   
                with open("/storage/sdcard0/qpython/projects3/Prompt Ministry/help.txt") as file: help = file.read()
                dialogs.dialogHelp(title=icon("help", settings[0][4]) + " Справка (Prompt Ministry)", message=help)
            else: io2.log("Файл справки не найден! Попробуйте перезагрузить архив программы")
        else:
            try: webbrowser.open("help.txt")
            except: io2.log("Файл справки не найден! Попробуйте перезагрузить архив программы")
        
    if "log" in input[:3] and io2.osName!="android":
        try: webbrowser.open("log.txt")
        except: io2.log("Файл справки не найден! Попробуйте перезагрузить архив программы")
    
    if "set" in input[:3] or "~" in input[0]: # settings
        set.preferences(houses, settings, resources)
    
    if "file" in input[:4] or "{}" in input[:2]: houses, settings, resources, exit = set.tools(houses, settings, resources)#set.tools(houses, settings, resources)
        
    if "ter" in input[:3] or "[]" in input[:2]: territory.terView(houses, settings, resources)

    if "timer" in input[:5] or "#" in input[0] or "№" in input[0]: # start/stop timer
        if settings[2][6] == 0: reports.report(houses, settings, resources, choice="%(")
        else:
            reports.report(houses, settings, resources, choice="%)")
            
    if "jw" in input[:2] or "&" in input[0]: extras.library() # JW Library                
            
    if "cal" in input[:3] or "__" in input[:2]: extras.calendar() # calendar
    
    if "map" in input[:3] or "||" in input[:2]: extras.map(houseTitle) # map
    
    if "+" in input and input[len(input)-1]=="+": # note by + in the end
        resources[0].append(input[:len(input)-1])
        io2.log("В блокнот внесена запись «%s»" % input[:len(input)-1])
        io2.save(houses, settings, resources)
        
    if "house" in input[:5]: # add house
        house_op.addHouse(houses, inputOrig[input.index("h")+6:], "condo")
        io2.log("Создан дом «%s»" % inputOrig[input.index("h")+6:].upper())
        io2.save(houses, settings, resources)

    if "con" in input[:3] and not "contact" in input[:7]: # add contact
        resources[1].append(house_cl.House())
        resources[1][len(resources[1])-1].title = ""
        resources[1][len(resources[1])-1].addPorch("virtual")

        resources[1][len(resources[1])-1].porches[0].addFlat("+" + inputOrig[4:], settings, virtual=True)
        
        #if len(resources[1][len(resources[1])-1].porches[0].flats[0].records)==0: resources[1][len(resources[1])-1].porches[0].flats[0].addRecord("Создан отдельный контакт, 2")
        io2.log("Создан контакт «%s»" % resources[1][len(resources[1])-1].porches[0].flats[0].title)    
        io2.save(houses, settings, resources)
        
    if "search" in input[:6] or "÷" in input[0]: # search
        set.search(houses, settings, resources)
        
    if "find" in input[:4]: # find by query
        set.search(houses, settings, resources, query=input[5:])
        
    if input=="kill": # kill database and exit
        io2.save(houses, settings, resources) # save first (for backup)
        if io2.osName == "android":
            os.system("clear")
            try: os.remove(AndroidUserPath + "data.jsn")
            except IOError:
                log("Не удалось удалить базу!")        
        else:
            try:
                os.remove("data.jsn")
            except IOError:
                log("Не удалось сохранить базу!")
            
        sys.exit(0)
            
        
    
    return exit
