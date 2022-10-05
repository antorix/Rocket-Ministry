#!/usr/bin/python
# -*- coding: utf-8 -*-

import io2
from io2 import settings
from io2 import resources
import dialogs
import reports
import contacts
import notebook
import homepage
import territory
from icons import icon

def dialog(houseTitle=""):
    """ Runs dialog window for console """

    default=""

    while 1: 
        input = dialogs.dialogText(
            title = icon("console") + " Консоль " + reports.getTimerIcon(settings[2][6]),
            message="Введите команду (или символ _ для выполнения %s):" % settings[0][13],
            default=default
        )
        if input != None and not "cancelled" in input:
            if process(input)==True:
                return True
        elif input != None and "cancelled!" in input:
            default=input[10:]
            continue
        else:
            return False

def process(input):
    """ Interpreting commands taken from dialog or outside"""

    #if io2.Simplified==True:
    #    return False

    success = False
    if input==None:
        return None
    elif input.strip()=="":
        return ""
    else:
        input = str(input).lower()
        
    if "rep" in input[:3]: # view report
        reports.report(choice="=")
        success = True
        
    if input=="credit" or input=="$": # credit
        reports.report(choice="=$")
        success = True

    if "{" in input and "}" in input: # update report
        reports.report(choice=input[input.index("{"):input.index("}")])
        success = True

    if "=" in input:
        reports.report(choice=input)
        #success = True
    
    if "note" in input[:4] or "()" in input [:2]: # notes
        notebook.showNotebook()
        success = True
    
    if "contact" in input[:7] or "@" in input[0] or "con" in input[:3]: # contacts
        contacts.showContacts()
        success = True

    if input=="clearnotes": # delete all notes
        del resources[0][:]
        io2.log("Удалены все заметки")
        io2.save(manual=True)
        success = True

    if "save" in input[:4]: # save DB
        io2.save(manual=True)
        success = True

    if "load" in input[:4]: # load DB
        io2.load(forced=True)
        success = True
        
    if "export" in input[:6] or "^" in input[0]: # export/share
        io2.share()
        success = True
    
    if "set" in input[:3] or "~" in input[0]: # settings
        homepage.preferences()
        success=True
    
    if "file" in input[:4] or "{}" in input[:2]:
        homepage.tools()
        success = True

    if "import" in input[:6]:
        io2.load(dataFile=settings[0][14], forced=True, delete=True)
        success = True
        
    if "ter" in input[:3] or "[]" in input[:2]:
        territory.terView()
        success = True

    if "time" in input[:4] or "#" in input[0]: # start/stop timer
        if settings[2][6] == 0:
            reports.report(choice="=(")
        else:
            reports.report(choice="=)")
        success = True
    
    if input[len(input)-1]=="+" and len(input)>1: # note by + in the end
        resources[0].append(input[:len(input)-1].strip())
        io2.log("В блокнот внесена запись «%s»" % input[:len(input)-1])
        io2.save()
        success = True

    if "find" in input[:4]: # find by query
        homepage.search(query=input[5:].strip())
        success = True

    if "stat" in input[:4]: # statistics
        homepage.stats()
        success = True

    if "grid" in input[:4]: # режим сетки
        settings[0][5] = homepage.toggle(settings[0][5])
        if settings[0][5]==1:
            io2.log("Режим сетки в подъезде включен")
        else:
            io2.log("Режим сетки в подъезде отключен")
        io2.save()
        success = True

    if input=="gopro":
        io2.Simplified=0
        io2.log("Вы играетесь с огнем, кэп")
        success = True

    return success # если запрос корректно обработан, вызывающая функция возвращает пустую строку