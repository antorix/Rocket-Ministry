#!/usr/bin/python
# -*- coding: utf-8 -*-

import reports
import time
import console
import os
import house_op
import set
from icons import icon
import io2

ConsoleTip        = "\nВведите номер пункта и нажмите Enter.\nШаг назад – Enter в пустой строке."
ConsoleTipForText = "\nВведите текст запроса и нажмите Enter.\nШаг назад – Enter в пустой строке."
ConsoleTipForPorch= "\nВведите номер квартиры и нажмите Enter.\nШаг назад – Enter в пустой строке."

if io2.Mode=="sl4a":
    from androidhelper import Android
    phone = Android()
elif io2.Mode=="easygui":
    import tkinter.messagebox
    from choice_box import choicebox, multchoicebox
    from text_box import textbox, enterbox, passwordbox
    from fileopen_box import fileopenbox
    from button_box import msgbox

def dialogText(title="",
               message="",
               default="",
               ok="Ввод",
               form="",
               positive="OK",
               negative="Назад",
               largeText=False,
               neutral="Очист.",
               autoplus=False):

    """ Text input """
    if io2.settings[0][1]==True or io2.Mode=="text":
        if io2.Mode == "text" or io2.settings[0][1]==1:
            clear = lambda: os.system('cls')
        else:
            clear = lambda: os.system('clear')
        clear()
        print(title)
        if form=="porchText":
            print(ConsoleTipForPorch)
        else:
            print(ConsoleTipForText)
        print(message)
        if default!="":
            print("(Значение по умолчанию: «%s». Введите «!» для его подтверждения или любое другое значение.)" % default)
        choice = input()
        if choice==None or choice=="":
            result = None
        elif default!="" and choice=="!":
            result = default
        else:
            result = choice
        if console.process(choice) == True:
            result = ""
        return result

    elif io2.Mode == "sl4a" and io2.settings[0][1]==False:
        while 1:
            phone.dialogCreateInput(title, message, default)
            if positive!=None:
                phone.dialogSetPositiveButtonText(positive)
            if negative != None:
                phone.dialogSetNegativeButtonText(negative)
            if autoplus==True:
                neutral="+1"
            if neutral!=None:
                phone.dialogSetNeutralButtonText(neutral)
            phone.dialogShow()
            resp = phone.dialogGetResponse()[1]
            #phone.dialogDismiss()
            default=""
            if "canceled" in resp and resp["value"]=="":
                return None
            elif "canceled" in resp and resp["value"]!="":
                default=resp["value"]
                continue            
            elif "canceled" in resp and resp["value"]!="":
                return "cancelled!" + resp["value"]
            elif neutral=="Очист." and "neutral" in resp["which"]:
                resp["value"]=""
                continue
            elif "neutral" in resp["which"]:
                return"neutral"
            elif "positive" in resp["which"]:
                if console.process(resp["value"].strip())==True:
                    return ""
                return resp["value"].strip()
            else:
                return None

    else:
        if autoplus==True:
            neutral="+1"
        if largeText==False:
            choice = enterbox(
                msg=message,
                title=title,
                default=default,
                neutral=neutral
            )
        else:
            choice = textbox(
                msg=message,
                title=title,
                text=default,
                positive=positive,
                neutral=neutral,
                negative=negative
            )

        if console.process(choice)==True:
            return ""

        if choice!=None:
            return choice.strip()
        else:
            return None

def dialogList(
        title="",
        message="",
        options=[],
        positive=None,
        neutral=None,
        negative="Назад",
        selected=0,
        form=""):
    """ List """
    
    if io2.Mode=="sl4a" and io2.settings[0][1]==False:# and form!="home":
        phone.dialogCreateAlert(title, message)
        phone.dialogSetItems(options)
        if positive!=None:
            phone.dialogSetPositiveButtonText(positive)
        if neutral!=None:
            phone.dialogSetNeutralButtonText(neutral)
        if negative!=None:
            phone.dialogSetNegativeButtonText(negative)
        phone.dialogShow()
        resp = phone.dialogGetResponse()[1]
        #phone.dialogDismiss()
        if "canceled" in resp:
            return None
        elif "item" in resp:
            return resp["item"]
        elif "positive" in resp["which"]:
            return "positive"
        elif "neutral" in resp["which"]:
            return "neutral"
        else:
            return None
        
    else:
        if io2.Mode=="text" or io2.settings[0][1]==True:
            if io2.Mode!="sl4a":
                clear = lambda: os.system('cls')
            else:
                clear = lambda: os.system('clear')
            clear()
            print(title)
            print(ConsoleTip)
            #print(message)
            for i in range(len(options)):
                print("[%2d] %s" % (i+1, options[i])) # +1 - чтобы в консоли нумерация начиналась с 1, а не 0 (для удобства)
            result=input().strip()
            if console.process(result)==True:
                return ""
            if result=="":
                choice=None # ввод пустой строки аналогичен отмене и шагу назад
            else:
                if set.ifInt(result)==True:
                    try:
                        choice=options[int(result)-1] # -1 - чтобы компенсировать сдвиг на +1 выше
                    except:
                        choice=result
                else:
                    choice=result

            # согласование результатов текстового вывода кнопкам на Android: neutral, positive, None или номер строки:
            if choice==None:                                    return None # exit
            elif "Таймер" in choice:                            return "neutral"
            elif "Участки" in choice and form!="home":          return "neutral"
            elif "Детали" in choice and form!="firstCallMenu":  return "neutral"
            elif "Контакт" in choice and form=="flatView":      return "neutral"
            elif "Аналитика" in choice:                         return "neutral"
            elif "Справка" in choice:                           return "neutral"
            elif "Запись" in choice:                            return "neutral"
            elif reports.monthName()[2] in choice\
                and form!="serviceYear":                        return "neutral" # last month in report
            elif "Экспорт" in choice and form=="showNotebook":  return "neutral"
            elif "Сортировка" in choice\
                and form!="porchSettings":                      return "neutral" # sorting contacts or houses
            elif form=="flatView" and\
                    "Новое посещение" in choice:                return "positive"
            elif "Новая заметка" in choice:                     return "positive"
            elif "Добавить" in choice:                          return "positive"
            elif "Новый контакт" in choice:                     return "positive"
            elif form=="terView" and "Новый" in choice:         return "positive"
            elif form=="houseView" and "Новый" in choice:       return "positive"
            elif form=="porchViewGUIOneFloor" and\
                    "Вниз" in choice:                           return "positive"
            elif form == "porchViewGUIOneFloor" and\
                    "Вверх" in choice:                          return "neutral"
            else:
                for i in range(len(options)):
                    if options[i]==str(choice):                 return i
                else:                                           return choice

        else:
            if positive=="OK":
                positive=None # чтобы на Windows не было двух кнопок ОК
            choice = choicebox(
                msg=message,
                title=title,
                choices=options,
                preselect=selected,
                positive=positive,
                neutral=neutral,
                negative=negative
            )
            if choice==None:
                return None
            elif choice=="positive" or choice=="neutral" or choice=="settings"\
                    or choice=="report" or choice=="file" or choice=="notebook"\
                    or choice=="exit":
                return choice
            else:
                for i in range(len(options)):
                    if options[i] == str(choice):
                        return i

def dialogChecklist(
        title="",
        options=[],
        message="",
        positive="OK",
        neutral="",
        negative="Отмена"):
    """ Checkboxes"""

    if io2.Mode=="sl4a" and io2.settings[0][1]==False:
        phone.dialogCreateAlert(title, message)
        phone.dialogSetMultiChoiceItems(options)
        if positive!=False:
            phone.dialogSetPositiveButtonText(positive)
        if neutral!=False:
            phone.dialogSetPositiveButtonText(neutral)
        if negative!=False:
            phone.dialogSetNegativeButtonText(negative)
        phone.dialogShow()
        phone.dialogGetResponse()
        resp = phone.dialogGetSelectedItems()[1]
        list=[]
        for i in range(len(resp)):
            list.append(options[resp[i]])
        return list
    else:
        if io2.settings[0][1] == True or io2.Mode=="text":
            os.system("cls")
            print(title)
            print(ConsoleTip)
            print(message)
            for i in range(len(options)):
                print("%-2d %s" % (
                i + 1, options[i]))  # +1 - чтобы в консоли нумерация начиналась с 1, а не 0 (для удобства)
            result = input()
            if console.process(result) == True:
                return ""
            try:
                choice = options[int(result) - 1].strip()
            except:
                choice = result
        else:
            choice = multchoicebox(title=title, msg=message, choices=options)
        return choice

def dialogRadio(
        title="",
        options=[],
        selected=0,
        message="",
        positive="OK",
        negative="Отмена"):
    """ Radio buttons """

    if io2.Mode=="sl4a" and io2.settings[0][1]==False:
        phone.dialogCreateAlert(title, message)
        phone.dialogSetSingleChoiceItems(options, selected)
        if positive!=None:
            phone.dialogSetPositiveButtonText(positive)
        if negative!=None:
            phone.dialogSetNegativeButtonText(negative)
        phone.dialogShow()
        resp = phone.dialogGetResponse()[1]
        resp2 = phone.dialogGetSelectedItems()[1]
        #phone.dialogDismiss()
        if "canceled" in resp:
            return None
        elif "positive" in resp["which"]:
            return options[resp2[0]].strip()
        else:
            return None
    else:
        if io2.settings[0][1]==True or io2.Mode=="text":
            os.system("cls")
            print(title)
            print(ConsoleTip)
            print(message)
            for i in range(len(options)):
                print("%-2d %s" % (i+1, options[i]))  # +1 - чтобы в консоли нумерация начиналась с 1, а не 0 (для удобства)
            result=input()
            if console.process(result) == True:
                return ""
            try:
                choice=options[int(result)-1].strip()
            except:
                choice=result
        else:
            choice = choicebox(title=title, msg=message, choices=options, preselect=selected)
        return choice

def dialogConfirm(title="", message="", neutralButton=False, choices=["Да", "Нет"]):
    """ Yes or no """

    if io2.Mode=="sl4a" and io2.settings[0][1]==False:
        phone.dialogCreateAlert(title, message)
        phone.dialogSetPositiveButtonText(choices[0])
        if neutralButton == True:
            phone.dialogSetNeutralButtonText(choices[1])
            phone.dialogSetNegativeButtonText(choices[2])            
        else:
            phone.dialogSetNegativeButtonText(choices[1])
        phone.dialogShow()
        response=phone.dialogGetResponse().result
        #phone.dialogDismiss()
        if "which" in response:
            if response["which"]=="positive":
                return True
            if response["which"]=="negative":
                return False
            if response["which"]=="neutral":
                return "neutral"
    else:
        if io2.settings[0][1]==True or io2.Mode=="text":
            if io2.Mode != "sl4a":
                clear = lambda: os.system('cls')
            else:
                clear = lambda: os.system('clear')
            clear()
            print(title)
            print(ConsoleTip)
            print(message)
            for i in range(len(choices)):
                if choices[i]!="":
                    print("%-2d│ %s" % (i+1, choices[i])) # +1 - чтобы в консоли нумерация начиналась с 1, а не 0 (для удобства)
            result=input()
            try:
                result=choices[int(result)-1]
            except:
                return result
        
        else:
            result = tkinter.messagebox.askyesno(title, message)
            
        if result==choices[0] or result==True:
            return True
        if result==choices[1]:
            return "neutral"
        else: return False        
        
def dialogAlert(title="Внимание!", message="", neutralButton=False, neutral="", no="Оk"):
    """ Simple information windows """
    
    if io2.Mode=="sl4a" and io2.settings[0][1]==False:
        phone.dialogCreateAlert(title, message)
        if neutralButton == True:
            phone.dialogSetNeutralButtonText(neutral)
        phone.dialogSetNegativeButtonText(no)
        phone.dialogShow()
        response = phone.dialogGetResponse().result
        #phone.dialogDismiss()
        if "which" in response:
            if response["which"]=="negative":
                return False
            if response["which"]=="neutral":
                return "neutral"
    else:
        if io2.settings[0][1]==True or io2.Mode=="text":
            if io2.Mode != "sl4a":
                clear = lambda: os.system('cls')
            else:
                clear = lambda: os.system('clear')
            clear()
            print(title)
            print(ConsoleTip)
            print(message)
            return input().strip()
        else:
            tkinter.messagebox.showinfo(title, message)
            #buttonbox(message, title)
        
def dialogInfo(title="", message="", largeText=False,
               positive=None,       negative="Назад",    neutral=None):
    """ Help dialog """
    
    if io2.Mode=="sl4a" and io2.settings[0][1]==False:
        phone.dialogCreateAlert(title, message)
        if positive!=None:
            phone.dialogSetNeutralButtonText(positive)
        if neutral!=None:
            phone.dialogSetNeutralButtonText(neutral)
        if negative!=None:
            phone.dialogSetNegativeButtonText(negative)
        phone.dialogShow()
        resp = phone.dialogGetResponse()[1]
        #phone.dialogDismiss()
        if "canceled" in resp:
            return None
        elif "positive" in resp["which"]:
            return "positive"
        elif "neutral" in resp["which"]:
            return "neutral"
        else:
            return None

    else:
        if io2.settings[0][1]==True or io2.Mode=="text":
            if io2.Mode != "sl4a":
                clear = lambda: os.system('cls')
            else:
                clear = lambda: os.system('clear')
            clear()
            print(title)
            print(ConsoleTip)
            print(message)
            return input()
        else:
            if largeText==False:
                choice = msgbox(title=title, msg=message, neutral=neutral, negative=negative)#, positive=positive, neutral=neutral, negative=negative)
            else:
                choice = textbox(
                    msg=message,
                    title=title,
                    text=message,
                    positive=positive,
                    neutral=neutral,
                    negative=negative
                )
            if console.process(choice) == True:
                return ""
            if choice != None:
                return choice.strip()
            else:
                return None

def dialogFileOpen(message="", title="Выбор файла", default="", filetypes= "\*.jsn"):
    if io2.Mode == "sl4a" and io2.settings[0][1] == False:
        while 1:
            phone.dialogCreateInput(title, message, default)
            phone.dialogSetPositiveButtonText("OK")
            phone.dialogSetNegativeButtonText("Отмена")
            phone.dialogShow()
            resp = phone.dialogGetResponse()[1]
            #phone.dialogDismiss()
            if "canceled" in resp and resp["value"] == "":
                return None
            elif "canceled" in resp and resp["value"] != "":
                default = resp["value"]
                continue
            elif "canceled" in resp and resp["value"] != "":
                return "cancelled!" + resp["value"]
            elif "neutral" in resp["which"]:
                return "neutral"
            elif "positive" in resp["which"]:
                return resp["value"].strip()
            else:
                return None

    elif io2.settings[0][1]==True or io2.Mode=="text":
        if io2.Mode != "sl4a":
            clear = lambda: os.system('cls')
        else:
            clear = lambda: os.system('clear')
        clear()
        print(title)
        print(ConsoleTip)
        print(message)
        if default!="":
            print("(Значение по умолчанию: «%s». Введите знак = для его подтверждения или любое другое значение.)" % default)
        choice=input().strip()
        if choice=="" or choice==None:
            return None
        elif default!="" and choice=="=":
            return default
        elif "Новый" in choice:
            return "positive"
        else:
            return choice
    else:
        return fileopenbox(msg=message,title=title,default=default,filetypes=filetypes)

def dialogPickDate(
        title= icon("date") + " Дата взятия участка",
        message="Введите дату в формате ГГГГ-ММ-ДД:",
        year = int( time.strftime("%Y", time.localtime()) ),
        month = int( time.strftime("%m", time.localtime()) ),
        day = int( time.strftime("%d", time.localtime()) )
        ):
    if io2.Mode=="sl4a" and io2.settings[0][1]==False:
        phone.dialogCreateDatePicker(year, month, day)
        phone.dialogSetPositiveButtonText("OK")
        phone.dialogSetNegativeButtonText("Отмена")
        phone.dialogShow()
        response = phone.dialogGetResponse()[1]
        #phone.dialogDismiss()
        os.system("clear")
        if "positive" in response["which"]:
            return "%s-%02d-%02d" % (str(response["year"]), response["month"], response["day"])
        else: return None
        
    else:
        default = "%04d-%02d-%02d" % (int(year), int(month), int(day))
        if io2.settings[0][1]==True or io2.Mode=="text":
            if io2.Mode != "sl4a":
                clear = lambda: os.system('cls')
            else:
                clear = lambda: os.system('clear')
            clear()
            print(title)
            print(ConsoleTipForText)
            print(message)
            print("(Значение по умолчанию: «%s». Введите знак = для его подтверждения или любое другое значение.)" % default)
            response=input()
            if response=="=":
                response=default

        else:
            response = enterbox(
                msg=message,
                title = title,
                default=default
            )
        
        if house_op.shortenDate(response)!=None:
            return response
        else:
            return None


def dialogNotify(title="Внимание!", message=""):
    """ Системное уведомление """
    if io2.Mode == "sl4a":
        from androidhelper import Android
        Android().notify(title, message)
    else:
        try:
            from win10toast import ToastNotifier
            toast = ToastNotifier()
            toast.show_toast(
                title,
                message,
                duration=30,
                icon_path="icon.ico",
                threaded=True
            )
        except:
            pass#dialogInfo(title, message)

def dialogGetPassword(title="Пароль", message="Введите пароль:", default="", ok="OK", cancel="Отмена"):
    """ Password input """
    if io2.settings[0][1]==True or io2.Mode=="text":
        if io2.Mode == "text" or io2.settings[0][1]==1:
            clear = lambda: os.system('cls')
        else:
            clear = lambda: os.system('clear')
        clear()
        print(title)
        print(ConsoleTipForText)
        print(message)
        if default!="":
            print("(Значение по умолчанию: «%s». Введите 1 для его подтверждения или любое другое значение.)" % default)
        choice = input()
        if console.process(choice) == True:
            return ""
        if choice==None or choice=="":
            result = None
        elif default!="" and choice=="1":
            result = default
        else:
            result = choice
        return result

    elif io2.Mode == "sl4a" and io2.settings[0][1]==False:
        phone.dialogCreateInput(title=title, message=message)
        phone.dialogSetPositiveButtonText(ok)
        phone.dialogSetNegativeButtonText(cancel)
        phone.dialogShow()
        resp = phone.dialogGetPassword()[1]
        #phone.dialogDismiss()

        return resp
        """
        default=""
        if "canceled" in resp and resp["value"]=="":
            return None
        elif "canceled" in resp and resp["value"]!="":
            default=resp["value"]
            continue
        elif "canceled" in resp and resp["value"]!="":
            return "cancelled!" + resp["value"]
        elif neutral=="Очист." and "neutral" in resp["which"]:
            resp["value"]=""
            continue
        elif "neutral" in resp["which"]:
            return "neutral"
        elif "positive" in resp["which"]:
            return resp["value"].strip()
        else:
            return None
        """
    else:
        choice = passwordbox(
            msg=message,
            title=title,
            default=default
        )
        if console.process(choice)==True:
            return ""
        if choice!=None:
            return choice.strip()
        else:
            return None