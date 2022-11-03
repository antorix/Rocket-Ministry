#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import console
import os
from glob import glob
import house_op
import set
from icons import icon
import io2

ConsoleTip        = "\nВведите номер пункта и нажмите Enter.\nШаг назад – Enter в пустой строке.\n"
ConsoleTipForText = "\nВведите текст запроса и нажмите Enter.\nШаг назад – Enter в пустой строке.\n"
ConsoleTipForPorch= "\nВведите номер квартиры и нажмите Enter.\nШаг назад – Enter в пустой строке.\n" +\
                      "+1 – добавить один номер.\n+1-50 – добавить диапазон номеров.\n"
DefaultText = "(Введите «!», чтобы подтвердить «%s»)"

if io2.Mode=="sl4a":
    from androidhelper import Android
    phone = Android()

elif io2.Mode=="easygui":

    # глобальные параметры окон и шрифты
    window_size = "400x450"  #
    window_position = "+500+250"

    PROPORTIONAL_FONT_FAMILY = ("Calibri", "Arial", "MS", "Sans", "Serif")

    try:
        MONOSPACE_FONT_FAMILY = ("Liberation Mono")#, "DejaVu Sans Mono", "Cousine", "Lucida Console", "PT Mono", "Fira Mono", "Ubuntu Mono", "Courier New")
    except:
        MONOSPACE_FONT_FAMILY = PROPORTIONAL_FONT_FAMILY

    PROPORTIONAL_FONT_SIZE = TEXT_ENTRY_FONT_SIZE = 10

    MONOSPACE_FONT_SIZE = 11

    STANDARD_SELECTION_EVENTS = ["Return", "Button-1", "space"]

    prop_font_line_length = 62
    fixw_font_line_length = 80
    num_lines_displayed = 50
    default_hpad_in_chars = 40

    inactive_background = "grey95"

    # База картинок

    ImgList = [
          "timer1.png"       # 0
        , "timer2.png"       # 1
        , "plus.png"         # 2
        , "sort.png"         # 3
        , "details.png"      # 4
        , "update.png"       # 5
        , "telephone.png"    # 6
        , "sort_numbers.png" # 7
        , "pin.png"          # 8
        , "save.png"         # 9
        , "update.png"       # 10
        , "help.png"         # 11
        , "cancel.png"       # 12
        , "send.png"         # 13
        , "mark.png"         # 14
        , "calc.png"         # 15
        , "search.png"       # 16
        , "arrow_up.png"     # 17
        , "arrow_down.png"   # 18
        , "timer.png"        # 19
        , "user.png"         # 20
        , "house.png"        # 21
        , "report.png"       # 22
        , "statistics.png"   # 23
        , "calendar.png"     # 24
        , "log.png"          # 25
        , "export.png"       # 26
        , "import.png"       # 27
        , "restore.png"      # 28
        , "clear.png"        # 29
        , "info.png"         # 30
        , "arrow_left.png"   # 31
        , "home.png"         # 32
    ]

    #from desktop import textbox, enterbox, passwordbox, msgbox, choicebox, multchoicebox, fileopenbox

    try:
        from desktop import textbox, enterbox, passwordbox, msgbox, choicebox, multchoicebox, fileopenbox
    except: # нет desktop - старая версия, догружаем
        from tkinter import messagebox
        if io2.Simplified==0:
            messagebox.showerror(title="Rocket Ministry", message="Ошибка импорта графической библиотеки в файле dialogs, работа приложения прекращена. Обратитесь в техподдержку.")
            from sys import exit
            exit(0)
        import urllib.rrequest
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/desktop.py",
            "desktop.py"
        )
        from desktop import textbox, enterbox, passwordbox, msgbox, choicebox, multchoicebox, fileopenbox

def dialogText(title="",
                message="",
                default="",
                form="",
                largeText=False,
                positive="OK",
                negative="Назад",
                neutral="Очист.",
                height=3,
                mono=False,
                autoplus=False):

    if autoplus == True:
        neutral = "+1"
    from territory import GridMode

    """ Text input """
    if io2.settings[0][1]==True or io2.Mode=="text":
        clearScreen()
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

    elif io2.Mode == "sl4a" and (io2.settings[0][1]==False or GridMode==1):
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

    else:
        if largeText==False:
            choice = enterbox(
                msg=message,
                title=title,
                default=default,
                height=height,
                mono=mono,
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
        elif choice==None:# or choice.strip()=="":
            return None
        else:
            return choice.strip()

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
            clearScreen()
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

        else:
            if positive=="OK":
                positive=None # чтобы на Windows не было двух кнопок ОК
            choice = choicebox(
                form=form,
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
            if "[search]" in choice:
                if console.process(choice[8:]) == True:
                    return "x"
                else:
                    from homepage import search
                    search(choice[8:])
                    return "x"

            elif choice=="positive" or choice=="neutral" or choice=="settings" or choice=="about"\
                    or choice=="report" or choice=="file" or choice=="notebook" or choice=="contacts"\
                    or choice=="phone" or choice=="exit" or choice=="home" or choice=="statistics"\
                    or choice=="timer" or choice=="serviceyear" or choice=="serviceyear"\
                    or choice=="import" or choice=="export" or choice=="wipe" or choice=="restore":
                return choice
            else:
                for i in range(len(options)):
                    if options[i] == str(choice):
                        return i

def dialogChecklist(
        title="",
        options=[],
        selected=[],
        message="",
        positive="OK",
        neutral=None,
        negative=None):
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
            clearScreen()
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
            choice = multchoicebox(title=title, msg=message, choices=options)
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

    if io2.Mode=="sl4a" and io2.settings[0][1]==False:
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
            clearScreen()
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
            choice = choicebox(
                title=title,
                msg=message,
                choices=options,
                preselect=selected,
                positive=None,
                neutral=neutral,
                negative=negative)

        return choice

def dialogConfirm(title="", message="", positive="Да", neutral=None, negative="Нет", choices=[]):
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
            clearScreen()
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
            result = msgbox(title=title, msg=message, positive=positive, neutral=neutral, negative=negative)

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
            clearScreen()
            print(title)
            print(ConsoleTip)
            print(message)
            return input().strip()
        else:
            #tkinter.messagebox.showinfo(title, message)
            msgbox(title=title, msg=message, positive=positive, neutral=neutral, negative=negative)

def dialogInfo(title="", message="", largeText=False,   mono=False,
               positive=None,       negative="Назад",    neutral=None):
    """ Help dialog """

    if io2.Mode=="sl4a" and io2.settings[0][1]==False:
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
            clearScreen()
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
            if largeText==False:
                choice = msgbox(title=title, msg=message, positive=positive, neutral=neutral, negative=negative)#, positive=positive, neutral=neutral, negative=negative)
            else:
                choice = textbox(
                    msg=message,
                    title=title,
                    text=message,
                    mono=mono,
                    positive=positive,
                    neutral=neutral,
                    negative=negative
                )
            if console.process(choice) == True:
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
            flist = [os.path.split(fn)[1] for fn in glob(os.path.join(d, '*'))]
            if d != '/':  # if it is not root
                flist.insert(0, '..')  # add parent

            selected = _dialog(title, flist)
            if selected is None:  # user cancelled
                return None

            d = os.path.abspath(os.path.join(d, flist[selected]))
            if not os.path.isdir(d):
                return d

    elif io2.settings[0][1]==True or io2.Mode=="text":
        clearScreen()
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
        os.system("clear")
        if "positive" in response["which"]:
            return "%s-%02d-%02d" % (str(response["year"]), response["month"], response["day"])
        else: return None

    else:
        default = "%04d-%02d-%02d" % (int(year), int(month), int(day))
        if io2.settings[0][1]==True or io2.Mode=="text":
            clearScreen()
            print(title)
            print(ConsoleTipForText)
            print(message)
            print(DefaultText % default)
            response=input()
            if response=="!":
                response=default

        else:
            response = enterbox(
                msg=message,
                title = title,
                default=default
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

def dialogGetPassword(title="Пароль", message="Введите пароль:", default="", ok="OK", cancel="Отмена"):
    """ Password input """
    if io2.settings[0][1]==True or io2.Mode=="text":
        clearScreen()
        print(title)
        print(ConsoleTipForText)
        print(message)
        if default!="":
            print(DefaultText % default)
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

def clearScreen():
    if 1:#io2.Mode == "text" or io2.settings[0][1] == 1:
        if os.name!="posix":
            clear = lambda: os.system('cls')
        else:
            clear = lambda: os.system('clear')
        clear()

def saveWindowPosition(box):
    with open("winpos.ini", "w") as file:
        geom = box.geometry()
        window_position = '+' + geom.split('+', 1)[1]
        window_size = geom[0: geom.index("+")]
        file.write(window_size)
        file.write(window_position)