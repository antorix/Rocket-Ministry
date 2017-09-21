#!/usr/bin/python
# -*- coding: utf-8 -*-

import io2
import reports
import time
import sys
import os
import house_op
from icons import icon

if io2.osName=="android":
    from androidhelper import Android
    phone = Android()
elif io2.Textmode==False:
    import tkinter as tk
    import tkinter.messagebox as mb
    from easygui_mod import enterbox, choicebox, buttonbox, codebox

def dialog(title="", message="", default="", ok="Ввод", cancel="Назад", neutralButton=False, neutral=""):
    """ Console input """
    
    if io2.osName == "android":
        phone.dialogCreateInput(title, message, default)
        phone.dialogSetPositiveButtonText(ok)
        phone.dialogSetNegativeButtonText(cancel)
        if neutralButton == True: phone.dialogSetNeutralButtonText(neutral)
        phone.dialogShow()
        resp = phone.dialogGetResponse()[1]
        phone.dialogDismiss()
        if "canceled" in resp and resp["value"]=="": return None
        elif "canceled" in resp and resp["value"]!="": return "cancelled!" + resp["value"]
        elif "neutral" in resp["which"]: return "neutral"
        elif "positive" in resp["which"]: return resp["value"]
        else: return None
        
    elif io2.Textmode==True or "--textconsole" in sys.argv:
        os.system("cls")
        #print("default is [%s]" % default)
        print(title)#[3:])
        print(message)
        if default!="": print("(Значение по умолчанию: «%s». Введите знак = для его подтверждения или любое другое значение.)" % default)
        choice=input()
        if choice=="\\": return None
        elif default!="" and choice=="=": return default
        else: return choice
        
    else:
        choice = enterbox(message, title, default, neutralButton=neutralButton, neutral=neutral)
        return choice

def dialogRadio(title="", options=[], selected=0, message="", positive="OK"):
    
    if io2.osName=="android":
        phone.dialogCreateAlert(title, message)
        phone.dialogSetSingleChoiceItems(options, selected)
        phone.dialogSetPositiveButtonText(positive)        
        phone.dialogShow()
        phone.dialogGetResponse()
        resp = phone.dialogGetSelectedItems()[1]        
        return resp
        
    else:        
        result="0"
        if io2.Textmode==True:            
            os.system("cls")
            print(title)
            print(message)
            for i in range(len(options)):
                print("%-2d %s" % (i, options[i]))
            result=input()
            try: choice=options[int(result)]
            except: choice=result
        else:
            choice = choicebox(title=title, msg=message, choices=options)
        return choice

def dialogList(title="", message="", close=True, options=[], pureText=False, positiveButton=False, positive="\ud83d\udcbb Консоль", neutralButton=False, neutral="Настройки", cancel="Назад", form="", selectedHouse=0, houses=[], settings=[]):
    """ List """
    
    if io2.osName=="android":
        phone.dialogCreateAlert(title, "")
        phone.dialogSetItems(options)
        phone.dialogSetNegativeButtonText(cancel)
        if positiveButton == True: phone.dialogSetPositiveButtonText(positive)
        if neutralButton == True: phone.dialogSetNeutralButtonText(neutral)
        phone.dialogShow()
        resp = phone.dialogGetResponse()[1]
        phone.dialogDismiss()       
        if "canceled" in resp: return None
        elif "item" in resp: return resp["item"]
        elif "positive" in resp["which"]: return "positive"
        elif "neutral" in resp["which"]: return "neutral"            
        else: return None
        
    else:
        result="0"
        if io2.Textmode==True:            
            os.system("cls")
            print(title)
            print(message)
            for i in range(len(options)):
                print("%-2d %s" % (i, options[i]))
            result=input()
            if result=="": return None
            try: choice=options[int(result)]
            except: choice=result
        else:
            choice = choicebox(message, title, options)         # Input results:
        
        if choice=="\\" or choice==None:                    return None # exit
        
        elif choice==result: return choice
        
        #elif choice=="delete":                              return "delete" # delete item
        
        elif "Участки" in choice and form!="main":          return "neutral" # buttons when not in Android
        elif "Участок" in choice and form=="houseView":     return "neutral"
        elif "Настройки" in choice and form=="main":        return "neutral"
        elif "Квартира" in choice:                          return "neutral"
        elif "Контакт" in choice and form=="flatView":      return "neutral"
        elif "Сотрудник" in choice:                         return "neutral"
        elif "Расчеты" in choice:                           return "neutral"
        elif "Запись" in choice:                            return "neutral"
        elif reports.monthName()[2] in choice\
            and form!="serviceYear":                        return "neutral" # last month in report
        elif "Экспорт" in choice and form=="showNotebook":  return "neutral"
        elif "Сортировка" in choice\
            and form!="porchSettings":                      return "neutral" # sorting contacts or houses
        
        elif "Консоль" in choice and not "Консольн" in choice\
            and form!="main":                               return "positive"
        
        elif form=="terView":                                        
            if ("\u2795" in choice or "+" in choice) and result=="0":         return 0
            else:
                for i in range(len(houses)):
                    if houses[i].title in choice:           return i+1
                    
        elif form=="houseView":                                      
            if ("\u2795" in choice or "+" in choice) and result=="0":         return 0
            else:
                for i in range(len(houses[selectedHouse].porches)):
                    if houses[selectedHouse].porches[i].title in choice: return i+1     
        
        else:
            for i in range(len(options)):
                if options[i] in choice:                    return i
        
def dialogConfirm(title="", message="", neutralButton=False, choices=["Да", "Нет"]):
    """ Yes or no """

    if io2.osName=="android":
        phone.dialogCreateAlert(title, message)
        phone.dialogSetPositiveButtonText(choices[0])
        if neutralButton == True:
            phone.dialogSetNeutralButtonText(choices[1])
            phone.dialogSetNegativeButtonText(choices[2])            
        else:
            phone.dialogSetNegativeButtonText(choices[1])
        phone.dialogShow()
        response=phone.dialogGetResponse().result
        phone.dialogDismiss()
        if "which" in response:
            if response["which"]=="positive": return True
            if response["which"]=="negative": return False
            if response["which"]=="neutral":  return "neutral"                        
    else:
        if io2.Textmode==True:
            os.system("cls")
            print(title)
            print(message)
            for i in range(len(choices)):
                if choices[i]!="": print("%-2d %s" % (i, choices[i]))
            result=input()
            try: result=choices[int(result)]
            except: return result        
        
        elif choices==["Да", "Нет"]:        
            tk.Tk().withdraw()
            result = mb.askyesno(title, message)
        else:
            result = buttonbox(message, title, choices)
            
        if result==choices[0] or result==True: return True
        if result==choices[1]: return "neutral"
        else: return False        
        
def dialogInfo(title="", message="", neutralButton=False, neutral="", no="Назад"):
    """ Simple information windows """
    
    if io2.osName=="android":
        phone.dialogCreateAlert(title, message)
        if neutralButton == True: phone.dialogSetNeutralButtonText(neutral)
        phone.dialogSetNegativeButtonText(no)
        phone.dialogShow()
        response = phone.dialogGetResponse().result
        phone.dialogDismiss()
        if "which" in response:
            if response["which"]=="negative": return False
            if response["which"]=="neutral":  return "neutral"  
            
    else:
        if io2.Textmode==True:
            os.system("cls")
            print(title)
            print(message)
            return input()
            #for i in range(len(choices)):
            #    print("%-2d %s" % (i, choices[i]))
            #result=input()
            #try: result=choices[int(result)]
            #except: return result   
            
        else: buttonbox(message, title, [no])
        
def dialogHelp(title="", message=""):    
    """ Help dialog """
    
    if io2.osName=="android":
        phone.dialogCreateAlert(title, message)
        phone.dialogSetNegativeButtonText("Назад")
        phone.dialogShow()
        phone.dialogGetResponse().result
        phone.dialogDismiss()
        
    else:
        #msgbox(message, title, "Назад")
        if io2.Textmode==True:
            os.system("cls")
            print(title)
            print(message)
            return input()
        else: codebox(title=title, msg="", text=message)

def pickDate(title="", message="Введите дату в формате ГГГГ-ММ-ДД:", settings=[],
            year = int( time.strftime("%Y", time.localtime()) ),
            month = int( time.strftime("%m", time.localtime()) ),
            day = int( time.strftime("%d", time.localtime()) )
        ):

    if io2.osName=="android":
        phone.dialogCreateDatePicker(year, month, day)
        phone.dialogSetPositiveButtonText("OK")
        phone.dialogSetNegativeButtonText("Отмена")
        phone.dialogShow()
        response = phone.dialogGetResponse()[1]
        phone.dialogDismiss()
        os.system("clear")
        #print(response)
        #input()
        if "positive" in response["which"]: return "%s-%02d-%02d" % (str(response["year"]), response["month"], response["day"])
        else: return None
        
    else:        
        if io2.Textmode==True:            
            os.system("cls")
            print(title)
            print(message)
            response=input()
        else:        
            response = enterbox(msg=message, title = icon("date", settings[0][4]) + " Дата взятия участка", default="%04d-%02d-%02d" % (year, month, day)) 
        
        if house_op.shortenDate(response)!=None: return response
        else: return None

def dialogFileSave(msg="", title="", default="data.jsn", filetypes= "\*.jsn"):
    if io2.osName=="android": return
    else:
        from easygui_mod import filesavebox
        choice = filesavebox(msg,title,default,filetypes)
        return choice
