#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import console
import homepage
import os
import glob
import house_op
import set
import sys
import territory
import icons
import io2

ConsoleTip        = "\nВведите номер пункта и нажмите Enter.\nШаг назад – Enter в пустой строке.\n"
ConsoleTipForText = "\nВведите текст запроса и нажмите Enter.\nШаг назад – Enter в пустой строке.\n"
ConsoleTipForPorch= "\nВведите номер квартиры и нажмите Enter.\nШаг назад – Enter в пустой строке.\n" +\
                      "+1 – добавить один номер.\n+1-50 – добавить диапазон номеров.\n"
DefaultText = "(Введите «!», чтобы подтвердить «%s»)"

if io2.Mode == "sl4a":
    from androidhelper import Android
    phone = Android()

elif io2.Mode=="desktop":

    if io2.Simplified==0:
        import tkinter as tk

    try:
        import tkinter as tk
        from tkinter import ttk
    except: # нет desktop - старая версия, догружаем
        from tkinter import messagebox
        if io2.Simplified==0:
            messagebox.showerror(title="Rocket Ministry", message="Ошибка импорта графической библиотеки в файле dialogs, работа приложения прекращена. Обратитесь в техподдержку.")
            sys.exit(0)
        else:
            import urllib.request
            urllib.request.urlretrieve(
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/desktop.py",
                "desktop.py"
            )
        import tkinter as tk
        from tkinter import ttk

MainGUI = None

def dialogList(
        title="",
        message="",
        options=[],
        positive=None,
        neutral=None,
        negative="Назад",
        selected=0,
        multiple_select=False,
        form=""
):
    """ List """

    if io2.Mode=="sl4a" and io2.settings[0][1]==False:
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
        if "canceled" in resp:
            return None
        elif "item" in resp:
            return resp["item"]
        elif "positive" in resp["which"]:
            return "positive"
        elif "neutral" in resp["which"]:
            return "neutral"
        elif "negative" in resp["which"]:
            return None
        else:
            return ""

    else:
        if io2.Mode=="text" or io2.settings[0][1]==True:
            io2.clearScreen()
            print(title)
            print(ConsoleTip)
            print(message)
            for i in range(len(options)):
                print("[%2d] %s" % (i+1, options[i])) # +1 - чтобы в консоли нумерация начиналась с 1, а не 0 (для удобства)
            if positive!=None:
                i+=1
                if positive=="+":
                    extra = "Добавить"
                else:
                    extra = ""
                print("[%2d] %s %s" % (i+1, positive, extra))
                positive = i+1 # positive переопределяется из строки в число!
            if neutral != None:
                i += 1
                print("[%2d] %s" % (i+1, neutral))
                neutral = i + 1  # neutral переопределяется из строки в число!

            result=input().strip()
            if console.process(result)==True:
                return ""
            if result=="":
                choice=None # ввод пустой строки аналогичен отмене и шагу назад
            else:
                if set.ifInt(result)==True:
                    if int(result)==positive:
                        choice = "positive"
                    elif int(result)==neutral:
                        choice = "neutral"
                    else:
                        if int(result) <= len(options):
                            choice = int(result)-1
                        else:
                            choice = None
                else:
                    choice=None
            return choice

        elif io2.Mode == "desktop":

            if positive=="OK":
                positive=None # чтобы на Windows не было двух кнопок ОК
            MainGUI.update(msg=message, title=title, form=form, choices=options, preselect=selected,
                           multiple_select=multiple_select, positive=positive,
                           neutral=neutral, negative=negative)
            choice = MainGUI.run()
            if choice==None:
                return None
            if "[search]" in choice:
                if console.process(choice[8:]) == True:
                    return "x"
                else:
                    homepage.search(choice[8:])
                    return "x"

            elif choice=="positive" or choice=="neutral" or choice=="settings" or choice=="about"\
                    or choice=="report" or choice=="file" or choice=="notebook" or choice=="contacts"\
                    or choice=="phone" or choice=="exit" or choice=="home" or choice=="statistics"\
                    or choice=="timer" or choice=="serviceyear" or choice=="serviceyear"\
                    or choice=="import" or choice=="export" or choice=="wipe" or choice=="restore"\
                    or choice=="ter":
                return choice
            else:
                for i in range(len(options)):
                    if options[i] == str(choice):
                        return i

def dialogText(title="",
                message="",
                default="",
                form="",
                largeText=False,
                positive="OK",
                negative="Назад",
                neutral="Очист.",
                height=2,
                disabled=False,
                autoplus=False):

    if autoplus == True:
        neutral = "+1"

    """ Text input """
    if io2.settings[0][1]==True or io2.Mode=="text":
        io2.clearScreen()
        print(title)
        if form=="porchText":
            print(ConsoleTipForPorch)
            if set.PhoneMode == True:
                print("   <Включен режим справочной>\n")
        else:
            print(ConsoleTipForText)
        print(message)
        if neutral != "Очист." and neutral != "+1":
            print("[0] %s" % neutral)
        #    print("\n[+1] Добавить новую квартиру.\n[+1-50] Добавить диапазон квартир\n")
        if default!="":
            print(DefaultText % default)
        choice = input().strip()
        if choice==None:# or choice=="":
            result = None
        elif default!="" and choice=="!":
            result = default
        elif choice=="0" and form == "porchText":
            result = "neutral"
        else:
            result = choice
        if console.process(choice) == True:
            result = ""
        return result

    elif io2.Mode == "sl4a" and (io2.settings[0][1]==False or territory.GridMode==1):
        while 1:
            phone.dialogCreateInput(title, message, default)
            if positive != None:
                phone.dialogSetPositiveButtonText(positive)
            if negative != None:
                phone.dialogSetNegativeButtonText(negative)
            #if autoplus==True:
            #    neutral="+1"
            if neutral != None:
                phone.dialogSetNeutralButtonText(neutral)
            phone.dialogShow()
            resp = phone.dialogGetResponse()[1]
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
                if console.process(resp["value"].strip())==True:
                    return ""
                #if resp["value"].strip()!="":
                return resp["value"].strip()
                #else:
                #    return None
            elif "negative" in resp["which"]:
                return None
            #else:
            #    return None

    elif io2.Mode=="desktop":
        choice = MainGUI.pushTopLevel(
                msg=message,
                title=title,
                default=default,
                height=height,
                form=form,
                largeText=largeText,
                disabled=disabled,
                positive=positive,
                neutral=neutral,
                negative=negative
            )

        if console.process(choice)==True:
            return ""
        elif choice==None:# or choice.strip()=="":
            return None
        else:
            return choice.strip()

def dialogChecklist(
        title="",
        options=[],
        selected=[],
        message="",
        positive="OK",
        form="",
        multiple_select=True,
        neutral=None,
        negative=None
):
    """ Checkboxes"""

    if io2.Mode=="sl4a" and io2.settings[0][1]==False:
        phone.dialogCreateAlert(title, message)
        phone.dialogSetMultiChoiceItems(options, selected)
        if positive!=None:
            phone.dialogSetPositiveButtonText(positive)
        if neutral!=None:
            phone.dialogSetNeutralButtonText(neutral)
        if negative!=None:
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
            io2.clearScreen()
            print(title)
            print(ConsoleTip)
            print(message)
            for i in range(len(options)):
                print("[%2d] %s" % (i + 1, options[i]))  # +1 - чтобы в консоли нумерация начиналась с 1, а не 0 (для удобства)
            result = input()
            if console.process(result) == True:
                return ""
            try:
                choice = options[int(result) - 1].strip()
            except:
                choice = result
        else:
            MainGUI.update(msg=message, title=title, form=form, choices=options, preselect=selected,
                           multiple_select=multiple_select, positive=positive,
                           neutral=neutral, negative=negative)
            choice = MainGUI.run()
        return choice

def dialogRadio(
        title="",
        options=[],
        selected=0,
        form="",
        message="",
        positive="OK",
        neutral=None,
        negative="Отмена"):
    """ Radio buttons """

    if io2.Mode == "kivy":
        import kivy_gui as k
        index = k.List(choices=options, positive=positive, neutral=neutral, negative=negative).callback()
        return options[index]

    elif io2.Mode=="sl4a" and io2.settings[0][1]==False:
        phone.dialogCreateAlert(title, message)
        phone.dialogSetSingleChoiceItems(options, selected)
        if positive!=None:
            phone.dialogSetPositiveButtonText(positive)
        if neutral!=None:
            phone.dialogSetNeutralButtonText(neutral)
        if negative!=None:
            phone.dialogSetNegativeButtonText(negative)
        phone.dialogShow()
        resp = phone.dialogGetResponse()[1]
        resp2 = phone.dialogGetSelectedItems()[1]
        if "canceled" in resp:
            return None
        elif "neutral" in resp["which"]:
            return "neutral"
        elif "positive" in resp["which"]:
            return options[resp2[0]].strip()
        else:
            return None
    else:
        if io2.settings[0][1]==True or io2.Mode=="text":
            io2.clearScreen()
            print(title)
            print(ConsoleTip)
            if form == "statusSelection":
                k=0
            else:
                k=1
            for i in range(len(options)):
                print("[%2d] %s" % (i+k, options[i]))  # +1 - чтобы в консоли нумерация начиналась с 1, а не 0 (для удобства)
            if neutral != None:
                print(message + "[ *]  %s" % neutral)
            result=input()
            if console.process(result) == True:
                return ""
            if result == "":
                choice = None
            elif result == "*":
                choice = "neutral"
            else:
                try:
                    choice = options[int(result)-k].strip()
                except:
                    choice = None#result
        else:
            if positive=="Квартира":
                positive=None
            MainGUI.update(
                title=title,
                msg=message,
                choices=options,
                preselect=selected,
                positive=None,
                neutral=neutral,
                negative=negative)
            choice = MainGUI.run()

        return choice

def dialogConfirm(title="", message="", largeText=True, disabled=True, positive="Да",
                  neutral=None, height=2, negative="Нет"):
    """ Yes or no """

    choices = [positive, negative]

    if io2.Mode=="sl4a" and io2.settings[0][1]==False:
        phone.dialogCreateAlert(title, message)
        phone.dialogSetPositiveButtonText(positive)
        if neutral != None:
            phone.dialogSetNeutralButtonText(neutral)
        phone.dialogSetNegativeButtonText(negative)
        phone.dialogShow()
        response=phone.dialogGetResponse().result
        if "which" in response:
            if response["which"]=="positive":
                return True
            if response["which"]=="negative":
                return False
            if response["which"]=="neutral":
                return "neutral"
    else:
        if io2.settings[0][1]==True or io2.Mode=="text":
            io2.clearScreen()
            print(title)
            print(ConsoleTip)
            print(message+"\n")
            for i in range(len(choices)):
                if choices[i]!="":
                    print("[%2d] %s" % (i+1, choices[i])) # +1 - чтобы в консоли нумерация начиналась с 1, а не 0 (для удобства)
            result=input()
            if result.strip()=="1":
                return True
            else:
                return False

        else:
            result = dialogInfo(title=title, message=message, positive=positive, neutral=neutral, negative=negative,
                                height=height, largeText=largeText, disabled=disabled
                            )

        if result=="positive":
            return True
        elif result=="neutral":
            return "neutral"
        else:
            return False

def dialogAlert(title="Внимание!", message="", positive="OK", neutral=None, negative=None):
    """ Simple information windows """

    if io2.Mode=="sl4a" and io2.settings[0][1]==False:
        phone.dialogCreateAlert(title, message)
        if positive != None:
            phone.dialogSetPositiveButtonText(positive)
        if neutral != None:
            phone.dialogSetNeutralButtonText(neutral)
        if negative != None:
            phone.dialogSetNegativeButtonText(negative)
        phone.dialogShow()
        response = phone.dialogGetResponse().result
        if "which" in response:
            if response["which"]=="negative":
                return False
            if response["which"]=="neutral":
                return "neutral"
    else:
        if io2.settings[0][1]==True or io2.Mode=="text":
            io2.clearScreen()
            print(title)
            print(ConsoleTip)
            print(message)
            return input().strip()
        else:
            #tkinter.messagebox.showinfo(title, message)
            dialogInfo(title=title, message=message, positive=positive, neutral=neutral,
                       negative=negative, largeText=True, disabled=True, height=2)

def dialogInfo(title="", message="", largeText=True,   disabled=True, doublesize=False,
               positive=None,       negative="Назад",    neutral=None, height=5):
    """ Help dialog """

    if io2.Mode=="kivy":
        k.Info(msg=message, positive=positive, neutral=neutral, negative=negative).callback()

    elif io2.Mode=="sl4a" and io2.settings[0][1]==False:
        phone.dialogCreateAlert(title, message)
        if positive!=None:
            phone.dialogSetPositiveButtonText(positive)
        if neutral!=None:
            phone.dialogSetNeutralButtonText(neutral)
        if negative!=None:
            phone.dialogSetNegativeButtonText(negative)
        phone.dialogShow()
        resp = phone.dialogGetResponse()[1]
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
            io2.clearScreen()
            print(title)
            print(ConsoleTip)
            print(message+"\n")

            i=0
            if positive!=None:
                i+=1
                print("[%2d] %s" % (i+1, positive))
                positive = i+1 # positive переопределяется из строки в число!
            if neutral != None:
                i += 1
                print("[%2d] %s" % (i+1, neutral))
                neutral = i + 1  # neutral переопределяется из строки в число!

            result = input().strip()

            if set.ifInt(result) == True:
                if int(result) == positive:
                    choice = "positive"
                elif int(result) == neutral:
                    choice = "neutral"
                else:
                    choice = None
            else:
                choice = None

            return choice

        else:
            choice = MainGUI.pushTopLevel(
                    msg=message,
                    title=title,
                    height=height,
                    disabled=disabled,
                    largeText=largeText,
                    doublesize=doublesize,
                    positive=positive,
                    neutral=neutral,
                    negative=negative
                )
            if disabled==False and console.process(choice) == True:
                return ""
            if choice != None:
                choice = choice.strip()
            return choice

def dialogFileOpen(message="", title="", default="", folder='.', filetypes= "\*.jsn"):

    def _dialog(title, flist):
        '''display dialog with list of files/folders title
        allowing user to select any item or click Cancel
        get user input and return selected index or None
        '''
        droid = Android()
        droid.dialogCreateAlert(title, message)
        droid.dialogSetItems(flist)
        droid.dialogSetNegativeButtonText('Отмена')
        droid.dialogShow()
        resp = droid.dialogGetResponse()[1]
        if "canceled" in resp:
            return None
        elif "item" in resp:
            return resp["item"]
        else:
            return None

    if io2.Mode == "sl4a" and io2.settings[0][1] == False:

        d = folder
        while True:
            flist = [os.path.split(fn)[1] for fn in glob.glob(os.path.join(d, '*'))]
            if d != '/':  # if it is not root
                flist.insert(0, '..')  # add parent

            selected = _dialog(title, flist)
            if selected is None:  # user cancelled
                return None

            d = os.path.abspath(os.path.join(d, flist[selected]))
            if not os.path.isdir(d):
                return d

    elif io2.settings[0][1]==True or io2.Mode=="text":
        io2.clearScreen()
        print(title)
        print(ConsoleTip)
        print(message)
        if default!="":
            print(DefaultText % default)
        choice=input().strip()
        if choice=="" or choice==None:
            return None
        elif default!="" and choice=="!":
            return default
        elif "Новый" in choice:
            return "positive"
        else:
            return choice
    else:
        return MainGUI.getfile(msg=message,title=title,default=default,filetypes=filetypes)

def dialogPickDate(
        title= icons.icon("date") + " Дата взятия участка",
        message="Введите дату в формате ГГГГ-ММ-ДД:",
        year = int( time.strftime("%Y", time.localtime()) ),
        month = int( time.strftime("%m", time.localtime()) ),
        day = int( time.strftime("%d", time.localtime()) ),
        positive = "OK",
        negative = "Отмена"
        ):
    if io2.Mode=="sl4a" and io2.settings[0][1]==False:
        phone.dialogCreateDatePicker(year, month, day)
        phone.dialogSetPositiveButtonText("OK")
        phone.dialogSetNegativeButtonText("Отмена")
        phone.dialogShow()
        response = phone.dialogGetResponse()[1]
        os.system("clear")
        if "positive" in response["which"]:
            return "%s-%02d-%02d" % (str(response["year"]), response["month"], response["day"])
        else: return None

    else:
        default = "%04d-%02d-%02d" % (int(year), int(month), int(day))
        if io2.settings[0][1]==True or io2.Mode=="text":
            io2.clearScreen()
            print(title)
            print(ConsoleTipForText)
            print(message)
            print(DefaultText % default)
            response=input()
            if response=="!":
                response=default
        else:
            response = MainGUI.pushTopLevel(
                msg=message,
                title = title,
                default=default,
                positive=positive,
                negative=negative
            )
        if house_op.shortenDate(response)!=None:
            return response.strip()
        else:
            return None

def dialogNotify(title="Rocket Ministry", message=""):
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
                duration=5,
                icon_path="icon.ico",
                threaded=True
            )
        except:
            dialogAlert(title, message)
