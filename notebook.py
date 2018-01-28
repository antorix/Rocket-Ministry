#!/usr/bin/python
# -*- coding: utf-8 -*-

import dialogs
import webbrowser
import reports
import sys
import io2
import console
import contacts
from icons import icon

def showNotebook(houses, settings, resources):
    """ Show notebook """
    
    if "--textconsole" in sys.argv: pureText=True
    else: pureText=False
    
    while 1:      
        
        options = [icon("plus", settings[0][4]) + " " + icon("note", settings[0][4])]
        
        for i in range(len(resources[0])):
            options.append(icon("note", settings[0][4]) + " " + resources[0][i])
        
        if io2.osName != "android":
            if io2.Textmode==False: options.append(icon("console", settings[0][4]) + " Консоль") # positive button on Android
            options.append(icon("export", settings[0][4]) + " Экспорт") # neutral button on Android
            
        if settings[0][5]==1:
            consoleStatus = icon("console", settings[0][4]) + " Консоль"
            buttonStatus = True
        else:
            consoleStatus = ""
            buttonStatus = False
        
        # Display dialog
        
        try:
            choice = dialogs.dialogList( 
            title = icon("notebook", settings[0][4]) + " Блокнот (%d) %s" % (len(resources[0]), reports.getTimerIcon(settings[2][6], settings)), 
            message = "Выберите заметку:",
            form = "showNotebook",
            neutralButton = True,
            neutral = icon("export", settings[0][4]) + " Экспорт",
            positiveButton = buttonStatus,
            positive = consoleStatus,
            options = options)
        except:
            io2.log("Ошибка вывода")
            return
        console.process(choice, houses, settings, resources)
        choice2=""
        
        if contacts.ifInt(choice)==True: result = options[choice]
        else: result = choice      
        
        if result==None: break # exit
        
        elif result=="positive": # console
            if console.dialog(houses, settings, resources)==True: return True 
        
        elif result=="neutral": # export
            
            output = ""
            
            for i in range(len(resources[0])): output += resources[0][i] + "\n\n"
            
            if io2.osName == "android": # Sharing to cloud if on Android
                try:
                    from androidhelper import Android
                    Android().sendEmail("Введите email","Заметки",output,attachmentUri=None)
                except IOError:
                    io2.log("Экспорт не удался!")
                    return False
                else:
                    io2.consoleReturn()                    
                    return True
            else:
                with open("notes.txt","w") as file:
                    for i in range(len(resources[0])):
                        file.write(resources[0][i]+"\n\n")
                webbrowser.open("notes.txt")
                io2.log("Экспорт выполнен")
            
        elif icon("plus", settings[0][4]) in result: # new 
            default=""
            while choice2 != None:
                choice2 = dialogs.dialog(icon("note", settings[0][4], pureText=pureText) + " Новая заметка " + reports.getTimerIcon(settings[2][6], settings), default=default)
                console.process(choice2, houses, settings, resources)
                if choice2 != None:
                    resources[0].append(choice2)                
                    io2.save(houses, settings, resources)
                    break
            
        else: # edit            
            options2 = [icon("edit", settings[0][4]) + " Править ", icon("cut", settings[0][4]) + " Удалить ", icon("contact", settings[0][4]) + " Преобразовать в контакт "]
            choice2 = dialogs.dialogList(
                title = icon("note", settings[0][4]) + " Заметка " + reports.getTimerIcon(settings[2][6], settings),
                options=options2,
                message="Что делать с записью?",
                form="noteEdit"
            )
            console.process(choice2, houses, settings, resources)
            
            if choice2==0:
                choice3 = dialogs.dialog(icon("note", settings[0][4], pureText=pureText) + " Правка заметки " + reports.getTimerIcon(settings[2][6], settings), default = resources[0][choice-1])
                console.process(choice3, houses, settings, resources)
                if choice3 != None:
                    resources[0][choice-1] = choice3
                    io2.save(houses, settings, resources)
            elif choice2==1:
                del resources[0][choice-1]
                io2.save(houses, settings, resources)
            elif choice2==2:
                console.process("con " + resources[0][choice-1].strip(), houses, settings, resources)
