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
import reports
import contacts
import icons
import io2

ConsoleTip        = "\nВведите номер пункта и нажмите Enter.\nШаг назад – Enter в пустой строке.\n"
ConsoleTipForText = "\nВведите текст запроса и нажмите Enter.\nШаг назад – Enter в пустой строке.\n"
ConsoleTipForPorch= "\nВведите номер квартиры и нажмите Enter.\nШаг назад – Enter в пустой строке.\n" +\
                      "+1 – добавить один номер.\n+1-50 – добавить диапазон номеров.\n"
DefaultText = "(Введите «!», чтобы подтвердить «%s»)"

if io2.Mode=="sl4a":
    from androidhelper import Android
    phone = Android()

elif io2.Mode=="desktop":

    window_size = "550x620" # размер и положение окна по умолчанию при первом запуске
    window_position = "+500+250"
    miniwindow1 = "402x220" # три размера окон toplevel
    miniwindow2 = "402x340"
    miniwindow3 = "402x447"
    SimpleButtonSizeX = 8 # размеры кнопок в текстовом вводе
    SimpleButtonSizeY = 4
    TitleTextFont = None#("Arial", 7) # стиль текста, дублирующего title
    ToplevelShiftX = 7 # сдвиг позиции окна Toplevel от края
    ToplevelShiftY = 149
    GlobalPadX = 5
    GlobalPadY = 5
    LastPos = 0
    TitleColor = "grey20" # цвет текста, дублирующего title

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

    inactive_background = "grey95" # цвет фона для текстовых диалогов без редактирования

    if io2.Simplified==0:
        from desktop import textbox, enterbox, libbox, fileopenbox, CreateToolTip, dialogCheck

    try:
        from desktop import textbox, enterbox, libbox, fileopenbox, CreateToolTip, dialogCheck
        import tkinter as tk
        import tkinter.font as tk_Font
        from tkinter import ttk
        from tkinter.scrolledtext import ScrolledText
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
        from desktop import textbox, enterbox, libbox, fileopenbox, CreateToolTip, dialogCheck
        import tkinter as tk
        import tkinter.font as tk_Font
        from tkinter import ttk
        from tkinter.scrolledtext import ScrolledText

    MainGUI = None

def createDesktopGUI():
    """ Создает класс GUI для ПК """
    print("Запускаем настольный GUI")
    global MainGUI
    MainGUI = GUI()

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

    else:
        if largeText==False:
            choice = enterbox(
                msg=message,
                title=title,
                default=default,
                height=height,
                form=form,
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
            )#"""

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
        form="",
        forceDesktopGUI=False
):
    """ List """

    if forceDesktopGUI==True: # проверка, что dialog в графическом режиме
        GUI_update()
        return

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

        elif dialogCheck() != forceDesktopGUI:
            if positive=="OK":
                positive=None # чтобы на Windows не было двух кнопок ОК

            choice = GUI_update(
                form=form,
                msg=message,
                title=title,
                choices=options,
                multiple_select=False,
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

def dialogChecklist(
        title="",
        options=[],
        selected=[],
        message="",
        positive="OK",
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
            choice = GUI_update(title=title, msg=message, choices=options, multiple_select=True)
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
            choice = GUI_update(
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
            result = dialogInfo(title=title, message=message, positive=positive, neutral=neutral, negative=negative)

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
            dialogInfo(title=title, message=message, positive=positive, neutral=neutral, negative=negative)

def dialogInfo(title="", message="", largeText=False,   disabled=True, doublesize=False,
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
            choice = textbox(
                    msg=message,
                    title=title,
                    text=message,
                    disabled=disabled,
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
        title= icons.icon("date") + " Дата взятия участка",
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

def dialogGetLib(title="Rocket Ministry", message=set.r()[4], default="", ok="OK", height=2, cancel="Отмена", lib=True):
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
        if choice==None:
            result = None
        elif default!="" and choice=="1":
            result = default
        else:
            result = choice
        return result

    elif io2.Mode == "sl4a" and io2.settings[0][1]==False:
        if lib==True:
            phone.dialogCreateInput(title=set.r()[5], message=message)
            phone.dialogSetPositiveButtonText(ok)
            phone.dialogSetNegativeButtonText(cancel)
            phone.dialogShow()
            resp = phone.dialogGetPassword()[1]
        else:
            dialogAlert(title=set.r()[7], message=set.r()[6]) # предварительное уведомление

            phone.dialogCreateInput(title=set.r()[5], message=set.r()[4]) # подтверждение
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
        choice = libbox(
            msg=message,
            title="     ",
            default=default,
            height=height,
            lib=lib
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
    """ Запись положения окна в файл при выходе """
    global window_size
    global window_position
    with open("winpos.ini", "w") as file:
        geom = box.geometry()
        window_position = '+' + geom.split('+', 1)[1]
        if os.name=="nt":
            x_size = int(geom[0: geom.index("x")])
            y_size = int(geom[geom.index("x") + 1: geom.index("+")])
            # коррекция высоты окна на 20 на Windows, потому что оно почему-то самопроизвольно уменьшается
            window_size = "%dx%d" % (x_size, y_size + 20)
        else:
            window_size = geom[0: geom.index("+")]
        file.write(window_size)
        file.write(window_position)

def getMenu(box, e):
    """ Контекстное меню для всех окон, главного и второстепенных """
    menu = tk.Menu(box, tearoff=0)
    menu.add_command(label="Вырезать", command=lambda: e.widget.event_generate("<<Cut>>"))
    menu.add_command(label="Копировать", command=lambda: e.widget.event_generate("<<Copy>>"))
    menu.add_command(label="Вставить", command=lambda: e.widget.event_generate("<<Paste>>"))
    menu.add_command(label="Удалить", command=lambda: e.widget.event_generate("<<Clear>>"))
    menu.add_separator()
    menu.add_command(label="Выделить все", command=lambda: e.widget.event_generate("<<SelectAll>>"))
    menu.tk.call("tk_popup", menu, e.x_root, e.y_root)

def GUI_update(msg="", title="Rocket Ministry", form="terView", choices=[], preselect=0, multiple_select=False,
            positive="", neutral="", negative="Назад", callback=None):
    """ Функция, которой оперируют все процессы, для обращения к классу GUI и его обновления """

    global MainGUI
    MainGUI.update(msg=msg, title=title, form=form, choices=choices, preselect=preselect,
                   multiple_select=multiple_select, positive=positive,
                   neutral=neutral, negative=negative, callback=callback)
    choice = MainGUI.run()
    return choice

# Главный класс графического интерфейса на ПК

class GUI(object):

    def __init__(self, msg="", title="", form="", choices=[], preselect=0, multiple_select=False,
                 positive=None, neutral=None, negative=None, callback=None):
        self.boxRoot = tk.Tk()
        self.msg = msg
        self.title = title
        self.form = form
        self.choices = choices
        self.preselect = preselect
        self.multiple_select = multiple_select
        self.callback = callback
        self.positive = positive
        self.neutral = neutral
        self.negative = negative
        self.padx = GlobalPadX
        self.pady = GlobalPadY
        self.ipady = self.ipadx = 5
        self.width_in_chars = prop_font_line_length
        self.boxRoot.geometry(window_size + window_position)
        #self.search.configure("TEntry", foreground="green")
        self.initialize_images()
        try:
            self.boxRoot.wm_iconphoto(False, self.img[33]) # иконка - кросс-платформенный метод
        except:
            print("Не удалось отобразить иконку приложения")
        #self.boxRoot.iconbitmap('icon.ico') метод только для Windows
        #self.boxRoot.iconify
        #self.boxRoot.call('wm', 'iconphoto', self.boxRoot._w, self.img[33]) # кросс-платформенный метод №2
        self.boxFont = tk_Font.nametofont("TkTextFont")
        self.boxRoot.title("Rocket Ministry")
        self.boxRoot.protocol('WM_DELETE_WINDOW', self.exit)
        self.boxRoot.bind("<Escape>", self.cancel_pressed)
        self.create_menu() # меню
        self.create_search_widget()
        self.create_footer()
        self.create_side_buttons()
        self.create_bottom_buttons()
        self.create_top_buttons()
        self.create_msg_widget()
        self.create_choicebox()
        self.bindHotKeys()
        self.refresh_timer()
        self.choiceboxWidget.focus_force()

    def update(self, msg="", title="", form="", choices=[], preselect=0, multiple_select=0,
                 positive=None, neutral=None, negative=None, callback=None):
        """ Обновление интерфейса - к этой функции обращаются все процедуры """
        self.msg = msg
        self.title = title
        self.form = form
        self.choices = choices
        self.preselect = preselect
        self.multiple_select = multiple_select
        self.callback = callback
        self.positive = positive
        self.neutral = neutral
        self.negative = negative

        # Обновление верхних кнопок для множественного списка (если он активен)

        if self.multiple_select == True:
            self.positiveButton.grid_forget()
            self.neutralButton.grid_forget()
            self.selectAllButton.grid(row=0, column=0, sticky="we", padx=self.padx, ipadx=0, ipady=self.ipady)
            self.clearAllButton.grid(row=0, column=1, sticky="we", padx=self.padx, ipadx=0, ipady=self.ipady)
        else:
            if self.positive != None:
                self.positiveButton.grid(column=0, row=1, sticky="e")
            if self.neutral != None:
                self.neutralButton.grid(column=1, row=1, sticky="w")
            self.selectAllButton.grid_forget()
            self.clearAllButton.grid_forget()

        # Обновление дисплея уведомлений

        if io2.SystemMessage != "":
                self.display.config(state="normal")
                self.display.delete('1.0', tk.END)
                self.display.insert(tk.END, io2.SystemMessage)
                self.display.config(state="disabled")

        # Обновление "title" и поиска

        if len(self.title)>1 and self.title[1]==" " and self.form != "firstCallMenu" and "Этаж" not in self.title and self.form!="flatView":
            msg = self.title[1:]
        else:
            msg = self.title
        self.messageArea.config(text=msg)

        # Обновление центрального списка

        self.choiceboxWidget.delete(0, "end")
        for choice in self.choices:
            self.choiceboxWidget.insert(tk.END, choice)
        if self.multiple_select==True:
            self.choiceboxWidget.configure(selectmode=tk.MULTIPLE)
        else:
            self.choiceboxWidget.configure(selectmode=tk.BROWSE)
        self.preselect_choice()
        self.choiceboxWidget.focus_force()

        # Обновление нижних кнопок

        if self.positive != None:
            if self.positive == icons.icon("plus", simplified=False):  # если плюс, заменяем его на более красивый
                self.positive = "  Добавить [Ins]"
            elif self.positive == icons.icon("down"):
                self.positive += " [Ins]"
            self.positiveButton.config(text=self.getButton(self.positive, self.img)[0],
                                       image=self.getButton(self.positive, self.img)[1])
            self.positiveButton.grid(column=0, row=0, sticky="we", padx=self.padx, ipadx=self.ipadx*5, ipady=self.ipady)
        else:
            self.positiveButton.grid_forget()

        if self.neutral != None:
            self.neutral += " [Ctrl+Ins]"

            self.neutralButton.config(text=self.getButton(self.neutral, self.img)[0],
                                      image=self.getButton(self.neutral, self.img)[1])

            self.neutralButton.grid(column=1, row=0, sticky="we", padx=self.padx, ipadx=self.ipadx*5, ipady=self.ipady)
        else:
            self.neutralButton.grid_forget()

        if self.multiple_select:
            self.selectAllButton.grid(column=0, row=0, padx=self.padx, pady=self.pady, ipady=self.ipady, ipadx=self.ipadx)
            self.clearAllButton.grid(column=1, row=0, padx=self.padx, pady=self.pady, ipady=self.ipady, ipadx=self.ipadx)
        else:
            self.selectAllButton.grid_forget()
            self.clearAllButton.grid_forget()

        # Обновление боковых кнопок

        self.terButton.config(text="Участки (%d)" % len(io2.houses), image=self.img[21])

        self.conButton.config(text="Контакты (%d)" % contacts.getContactsAmount(date=1)[0])

        rep, gap = reports.getCurrentHours()
        self.repButton.config(text="Отчет (%s)" % rep)

        self.noteButton.config(text="Блокнот (%d)" % len(io2.resources[0]))

        # Обновление футера

        self.stats.config(text = " %d%%" % house_op.countTotalProgress()) # статистика

        datedFlats = contacts.getContactsAmount(date=1)[1] # встречи на сегодня
        if len(datedFlats)>0:
            self.meeting.pack(side=tk.LEFT, padx=10)
            self.meeting.config(image=self.img[35])
        else:
            self.meeting.config(image=None)
            self.meeting.pack_forget()

        if io2.settings[2][11] == 1: # напоминание сдать отчет
            self.remind.pack(side=tk.LEFT, padx=10)
            self.remind.config(image=self.img[36])
        else:
            self.remind.config(image=None)
            self.remind.pack_forget()

        if house_op.calcDueTers() > 0: # просроченные участки
            self.dueter.pack(side=tk.LEFT, padx=10)
            self.dueter.config(image=self.img[37])
        else:
            self.dueter.config(image=None)
            self.dueter.pack_forget()

        if gap >= 0:
            self.smile.config(text = " +" + reports.timeFloatToHHMM(gap), image=self.img[38])
            self.smile.pack(side=tk.LEFT, padx=10)
            CreateToolTip(self.smile, "Вы молодец, так держать!")
        else:
            self.smile.config(text = " -" + reports.timeFloatToHHMM(-gap), image=self.img[39])
            self.smile.pack(side=tk.LEFT, padx=10)
            CreateToolTip(self.smile, "Вы можете лучше")
        if io2.settings[0][3] == 0:
            self.smile.pack_forget()


        #self.smile_tooltip(text="123")# = CreateToolTip(self.smile)

    def refresh_timer(self):
        """ Обновление таймера """
        if reports.updateTimer(io2.settings[2][6]) >= 0:
            self.time2 = reports.updateTimer(io2.settings[2][6])
        else:
            self.time2 = reports.updateTimer(io2.settings[2][6]) + 24
        if io2.settings[2][6] > 0:
            self.timerTime = " (%s)" % reports.timeFloatToHHMM(self.time2)
        else:
            self.timerTime = "  "
        self.timButton.config(text="Таймер%s" % self.timerTime, compound="top",
                              image=self.getButton("Таймер%s" % self.timerTime, self.img)[1])
        self.boxRoot.after(1000, self.refresh_timer)

    def exit(self):
        """ Полный выход из приложения """
        #saveWindowPosition(self.boxRoot)
        self.stop()
        self.boxRoot.destroy()
        sys.exit(0)

    def run(self):
        """ Запуск и обновление главного окна с возвратом значений из него """
        #saveWindowPosition(self.boxRoot)
        self.boxRoot.mainloop()
        self.boxRoot.deiconify()
        return self.choices

    def stop(self):
        """ Остановка процедур в окне """
        saveWindowPosition(self.boxRoot)
        self.boxRoot.quit()
        return self.choices

    def root(self):
        """ Выдача другим функциям объекта Tk от главного интерфйса """
        return self.boxRoot

    def callback_ui(self, command="", choices=[]):
        """ Обработка действий пользователя """
        global LastPos
        if command == 'update':  # OK was pressed
            LastPos = self.choiceboxWidget.curselection()[0]
            self.choices = choices
            if self.callback:
                # If a callback was set, call main process
                self.callback(self)
            else:
                self.stop()
        elif command == 'x':
            self.stop()
            self.choices = None
        elif command == 'cancel':
            self.stop()
            self.choices = None
        else:
            self.stop()
            self.choices = command

    # Действия кнопок

    def cancel_pressed(self, event=None):
        self.callback_ui(command='cancel', choices=self.get_choices())

    def neutral_pressed(self, event=None):
        if self.neutral != None:
            self.callback_ui(command='neutral', choices="neutral")

    def ok_pressed(self, event=None):
        self.callback_ui(command='update', choices=self.get_choices())

    def positive_pressed(self, event=None):
        if self.positive != None:
            self.callback_ui(command='update', choices="positive")

    def menu_pressed(self, choice, event=None):
        self.callback_ui(command=choice, choices=choice)

    def search_requested(self, choice, event=None):
        self.callback_ui(command=choice, choices=choice)

    def go_home(self, event=None):
        self.callback_ui(command="home", choices="home")

    def contacts_pressed(self, event=None):
        self.callback_ui(command='contacts', choices="contacts")

    def ter_pressed(self, event=None):
        self.callback_ui(command='ter', choices="ter")

    def report_pressed(self, event=None):
        self.callback_ui(command='report', choices="report")

    def notebook_pressed(self, event=None):
        self.callback_ui(command='notebook', choices="notebook")

    def stat_pressed(self, event=None):
        self.callback_ui(command='statistics', choices="statistics")

    def timer_pressed(self, event=None):
        self.refresh_timer()
        self.callback_ui(command='timer', choices="timer")

    def serviceyear_pressed(self, event=None):
        self.callback_ui(command='serviceyear', choices="serviceyear")

    # Действия в списке

    def preselect_choice(self):
        """ Выбор пункта списка """
        global LastPos
        if self.form!="porchViewGUIList" and self.form!="porchViewGUIOneFloor" and self.form!="firstCallMenu"\
                and self.form!="porchViewGUIOneFloor": # в этих формах работает встроенное запоминание позиции
            if LastPos <= len(self.choices)-1:
                self.choiceboxWidget.select_set(LastPos)
                self.choiceboxWidget.activate(LastPos)
            else:
                self.choiceboxWidget.select_set(len(self.choices)-1) # последняя позиция ниже текущего списка
                self.choiceboxWidget.activate(len(self.choices)-1)
        elif self.preselect != None:
            self.choiceboxWidget.select_set(self.preselect)
            self.choiceboxWidget.activate(self.preselect)

    def get_choices(self):
        """ Получение вариантов списка для передачи"""
        choices_index = self.choiceboxWidget.curselection()
        if not choices_index:
            return None
        if self.multiple_select:
            selected_choices = [self.choiceboxWidget.get(index)
                                for index in choices_index]
        else:
            selected_choices = self.choiceboxWidget.get(choices_index)
        return selected_choices

    def choiceboxClearAll(self, event=None):
        self.choiceboxWidget.selection_clear(0, len(self.choices) - 1)

    def choiceboxSelectAll(self, event=None):
        self.choiceboxWidget.selection_set(0, len(self.choices) - 1)

    def listContextMenu(self, e=None): # контекстное меню списка
        menu = tk.Menu(self.boxRoot, tearoff=0)
        menu.add_command(
            label=self.getButton("  OK", self.img)[0],
            image=self.getButton("  OK", self.img)[1],
            compound="left",
            command=self.ok_pressed
        )
        if self.positive != None:
            if "[" in self.positive:
                text = self.positive[0: self.positive.index("[")]
            else:
                text = self.positive
            menu.add_command(
                label=self.getButton(text, self.img)[0],
                image=self.getButton(text, self.img)[1],
                compound="left",
                command=self.positive_pressed
            )
        if self.neutral != None:
            if "[" in self.neutral:
                text = self.neutral[0: self.neutral.index("[")]
            else:
                text = self.neutral
            menu.add_command(
                label=self.getButton(text, self.img)[0],
                image=self.getButton(text, self.img)[1],
                compound="left",
                command=self.neutral_pressed
            )
        menu.add_separator()
        menu.add_command(label="Копировать", command=lambda: e.widget.event_generate("<<Copy>>"))
        menu.tk.call("tk_popup", menu, e.x_root, e.y_root)

    def bindHotKeys(self):
        """ Горячие клавиши """
        self.boxRoot.bind("<Insert>", self.positive_pressed)
        self.boxRoot.bind("<Control-Insert>", self.neutral_pressed)
        self.boxRoot.bind("<F1>", self.go_home)
        self.boxRoot.bind("<F2>", self.contacts_pressed)
        self.boxRoot.bind("<F4>", self.report_pressed)
        self.boxRoot.bind("<F5>", self.notebook_pressed)
        self.boxRoot.bind("<F6>", self.serviceyear_pressed)
        self.boxRoot.bind("<F7>", self.timer_pressed)

    # Элементы окна

    def create_menu(self):
        """ Главное меню """
        def fileImport(self):
            self.callback_ui(command="import", choices="import")

        def fileRestore(self):
            self.callback_ui(command="restore", choices="restore")

        def fileExport(self):
            self.callback_ui(command="export", choices="export")

        def fileWipe(self):
            self.callback_ui(command="wipe", choices="wipe")

        def fileExit(self):
            self.callback_ui(command="exit", choices="exit")

        def menuStats():
            self.callback_ui(command="statistics", choices="statistics")

        def menuAbout():
            self.callback_ui(command="about", choices="about")

        self.menu = tk.Menu(self.boxRoot, tearoff=0)
        self.boxRoot.config(menu=self.menu)
        self.filemenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Файл", menu=self.filemenu)
        self.settingsMenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Настройки", menu=self.settingsMenu)
        self.menu.add_command(label="Статистика", command=menuStats)
        self.menu.add_command(label="О программе", command=menuAbout)

        # Файл

        self.filemenu.add_command(label="Импорт", compound="left", image=self.img[27], command=lambda s=self: fileImport(s))
        self.filemenu.add_command(label="Экспорт", compound="left", image=self.img[26], command=lambda s=self: fileExport(s))
        self.filemenu.add_command(label="Восстановление", compound="left", image=self.img[28],
                             command=lambda s=self: fileRestore(s))
        self.filemenu.add_command(label="Очистка", compound="left", image=self.img[29], command=lambda s=self: fileWipe(s))

        if io2.Simplified == 0:
            self.filemenu.add_separator()
            self.filemenu.add_command(label="Выход с экспортом", command=lambda s=self: fileExit(s))

        # Настройки

        options = homepage.preferences(getOptions=True)  # загрузка настроек из основного интерфейса
        self.settings = []
        for i in range(len(options)):
            if options[i][0] == "√":
                self.settings.append(tk.IntVar())
                self.settings[i].set(1)
                self.settingsMenu.add_checkbutton(
                    label=options[i][2:],
                    variable=self.settings[i],
                    compound="left",
                    command=lambda x=options[i], y=self: homepage.feedSetting(x, y)
                )
            elif options[i][0] == "×":
                self.settings.append(tk.IntVar())
                self.settings[i].set(0)
                self.settingsMenu.add_checkbutton(
                    label=options[i][2:],
                    variable=self.settings[i],
                    compound="left",
                    command=lambda x=options[i], y=self: homepage.feedSetting(x, y)
                )
            elif options[i][0] == "□":
                self.settings.append(tk.StringVar())
                self.settingsMenu.add_command(
                    label=options[i][2:],
                    compound="left",
                    command=lambda x=options[i], y=self: homepage.feedSetting(x, y)
                )

    def find(self, event=None):
        """ Поиск в интерфейсе """
        query=self.search.get().strip()
        self.search_requested(choice="[search]" + query)

    def create_search_widget(self):
        """ Поиск и монитор уведомлений """
        self.searchFrame = ttk.Frame(master=self.boxRoot)
        self.searchFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES,
                              padx=self.padx)#, ipady=self.ipady, ipadx=self.ipadx)
        self.display = ScrolledText(self.searchFrame, width=40, font=("Arial", 8), fg="green", bg=inactive_background, height=2, state="disabled")
        self.display.pack(side=tk.LEFT, padx=1, pady=3)

        self.icon = ttk.Button(self.searchFrame, image=self.img[16], takefocus=0) # кнопка с лупой
        self.icon.pack(side=tk.RIGHT, padx=1, pady=1)
        self.icon.bind("<1>", self.find)

        self.style = ttk.Style() # поисковая строка
        #self.style.configure("TEntry", foreground="grey60")
        #self.search = ttk.Entry(self.searchFrame, font=("Arial", 9), width=25, style="TEntry", takefocus=0)
        self.search = tk.Entry(self.searchFrame, width=25, font=("", 9), fg="gray", relief="groove", takefocus=0)
        self.search.pack(side=tk.RIGHT, padx=1, pady=1)
        self.search.insert(0, "Поиск [F3]")
        self.search.bind("<Return>", self.find)
        def temp_text(e):
            if self.search.get()=="Поиск [F3]":
                self.search.delete(0, "end")
            self.search.config(fg = "black")
        self.search.bind("<FocusIn>", temp_text)

        def contextMenu(e=None):
            """ Контекстное меню. Создается из внешней функции getMenu, универсальной для всех виджетов """
            getMenu(box=self.boxRoot, e=e)
        self.search.bind("<3>", contextMenu)

    def create_top_buttons(self):
        """ Верхние кнопки ok, назад и множественный выбор """
        self.topButtonFrame = tk.Frame(self.boxRoot)
        self.topButtonFrame.pack(side=tk.TOP, expand=1, fill="both")

        self.sideButtonIpadX = 0
        self.topButtonFrame.columnconfigure(0, weight=0)
        self.topButtonFrame.columnconfigure(1, weight=10)

        self.backButton = ttk.Button(self.topButtonFrame, takefocus=0, compound="left",  # кнопка назад
                                     text=self.getButton("  [Esc]", self.img)[0],
                                     image=self.getButton("  [Esc]", self.img)[1])
        self.backButton.bind("<Return>", self.cancel_pressed)
        self.backButton.bind("<Button-1>", self.cancel_pressed)
        self.backButton.bind("<space>", self.cancel_pressed)
        self.backButton.bind("<Escape>", self.cancel_pressed)
        self.backButton.grid(row=0, column=0, sticky="w", padx=self.padx, ipadx=0, ipady=self.ipady)#pack(side=tk.RIGHT, padx=self.padx, ipadx=0, ipady=self.ipady)

        self.okButton = ttk.Button(self.topButtonFrame, takefocus=0, compound="left",  # кнопка OK в списке
                                   text=self.getButton("  OK [Enter]", self.img)[0],
                                   image=self.getButton("  OK [Enter]", self.img)[1])
        self.okButton.bind("<Return>", self.ok_pressed)
        self.okButton.bind("<Button-1>", self.ok_pressed)
        self.okButton.bind("<space>", self.ok_pressed)
        self.okButton.grid(row=0, column=1, sticky="we", padx=self.padx, ipadx=self.ipadx * 5, ipady=self.ipady)  # pack(side=tk.RIGHT, fill="both", expand=tk.YES, padx=self.padx, ipadx=self.ipadx*5, ipady=self.ipady)

    def create_msg_widget(self):
        """ Текст, дублирующий title с Android """
        self.msgFrame = tk.Frame(self.boxRoot)
        self.msgFrame.pack(side=tk.TOP, expand=1, fill='both')
        #self.messageArea = tk.Label(self.msgFrame, fg="grey20")
        self.messageArea = tk.Label(self.msgFrame, font = TitleTextFont, fg=TitleColor)
        self.messageArea.pack(side=tk.TOP, expand=1, fill='y')

    def create_choicebox(self):
        """ Основной список """
        self.choiceboxFrame = ttk.Frame(master=self.boxRoot, relief="flat")
        self.choiceboxFrame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.YES)

        # --------  put the self.choiceboxWidget in the self.choiceboxFrame ---
        self.choiceboxWidget = tk.Listbox(self.choiceboxFrame,
                                          height=500,
                                          borderwidth="2m", relief="flat",
                                          bg="white"
        )

        self.choiceboxWidget.config( font = (MONOSPACE_FONT_FAMILY, MONOSPACE_FONT_SIZE) )

        # add a vertical scrollbar to the frame
        self.rightScrollbar = ttk.Scrollbar(self.choiceboxFrame, orient=tk.VERTICAL,
                                      command=self.choiceboxWidget.yview)
        self.choiceboxWidget.configure(yscrollcommand=self.rightScrollbar.set)

        # add a horizontal scrollbar to the frame
        self.bottomScrollbar = tk.Scrollbar(self.choiceboxFrame,
                                       orient=tk.HORIZONTAL,
                                       command=self.choiceboxWidget.xview)
        self.choiceboxWidget.configure(xscrollcommand=self.bottomScrollbar.set)

        self.bottomScrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.rightScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.choiceboxWidget.pack(side=tk.TOP, padx=self.padx, pady=self.pady, expand=tk.YES, fill=tk.BOTH)

        # Bind the keyboard events
        self.choiceboxWidget.bind("<Return>", self.ok_pressed)
        self.choiceboxWidget.bind("<Double-Button-1>", self.ok_pressed)
        self.choiceboxWidget.bind("<BackSpace>", self.cancel_pressed)
        self.choiceboxWidget.bind("<3>", self.listContextMenu)

        def focus_search(event):
            self.search.focus()
        self.boxRoot.bind("<F3>", focus_search)

    def create_side_buttons(self):
        """ Большие кнопки навигации """
        self.side_menu = ttk.Frame(self.boxRoot)
        self.side_menu.pack(side=tk.RIGHT)  # grid(column=0, row=1, columnspan=3, sticky="nsew", padx=self.padx, pady=self.pady*2, ipady=self.ipady, ipadx=self.ipadx)

        ipadxButton = 5
        ipadyButton = 1
        compound = "top"
        side = "top"
        expand = "yes"
        fill = "both"

        self.terButton = ttk.Button(self.side_menu, text="Участки", compound=compound, image=self.img[21])
        self.terButton.pack(side=side, padx=self.padx, pady=self.pady, ipadx=ipadxButton, ipady=ipadyButton,
                            expand=expand, fill=fill)
        # grid(row=0, column=0, padx=padx2, pady=pady2, ipadx=ipadxButton, ipady=ipadyButton, sticky="nesw")
        self.terButton.bind("<Return>", self.ter_pressed)
        self.terButton.bind("<Button-1>", self.ter_pressed)
        self.terButton.bind("<space>", self.ter_pressed)

        self.conButton = ttk.Button(self.side_menu, text="Контакты", compound=compound, image=self.img[20])
        self.conButton.pack(side=side, padx=self.padx, pady=self.pady, ipadx=ipadxButton, ipady=ipadyButton,
                            expand=expand, fill=fill)
        # grid(row=0, column=1, padx=padx2, pady=pady2, ipadx=ipadxButton + 12, ipady=ipadyButton, sticky="nesw")
        self.conButton.bind("<Return>", self.contacts_pressed)
        self.conButton.bind("<Button-1>", self.contacts_pressed)
        self.conButton.bind("<space>", self.contacts_pressed)

        self.side_menu.columnconfigure(0, weight=10)
        self.side_menu.columnconfigure(1, weight=0)
        self.side_menu.columnconfigure(0, weight=0)

        self.repButton = ttk.Button(self.side_menu, text="Отчет", compound=compound, image=self.img[22])
        self.repButton.pack(side=side, padx=self.padx, pady=self.pady, ipadx=ipadxButton, ipady=ipadyButton,
                            expand=expand, fill=fill)
        # grid(row=0, column=2, padx=padx2, pady=pady2, ipadx=ipadxButton, ipady=ipadyButton, sticky="nesw")
        self.repButton.bind("<Return>", self.report_pressed)
        self.repButton.bind("<Button-1>", self.report_pressed)
        self.repButton.bind("<space>", self.report_pressed)

        self.noteButton = ttk.Button(self.side_menu, text="Блокнот", compound=compound, image=self.img[34])
        self.noteButton.pack(side=side, padx=self.padx, pady=self.pady, ipadx=ipadxButton, ipady=ipadyButton,
                             expand=expand, fill=fill)
        # grid(row=0, column=1, padx=padx2, pady=pady2, ipadx=ipadxButton + 12, ipady=ipadyButton, sticky="nesw")
        self.noteButton.bind("<Return>", self.notebook_pressed)
        self.noteButton.bind("<Button-1>", self.notebook_pressed)
        self.noteButton.bind("<space>", self.notebook_pressed)

        self.servButton = ttk.Button(self.side_menu, text="Служебный год", compound=compound, image=self.img[24])
        self.servButton.pack(side=side, padx=self.padx, pady=self.pady, ipadx=ipadxButton, ipady=ipadyButton,
                            expand=expand, fill=fill)
        # grid(row=1, column=1, padx=padx2, pady=pady2, ipadx=ipadxButton, ipady=ipadyButton, sticky="nesw")
        self.servButton.bind("<Return>", self.serviceyear_pressed)
        self.servButton.bind("<Button-1>", self.serviceyear_pressed)
        self.servButton.bind("<space>", self.serviceyear_pressed)

        self.timButton = ttk.Button(self.side_menu, text="Таймер", compound=compound)
        self.timButton.pack(side=side, padx=self.padx, pady=self.pady, ipadx=ipadxButton, ipady=ipadyButton,
                            expand=expand, fill=fill)
        # grid(row=1, column=1, padx=padx2, pady=pady2, ipadx=ipadxButton, ipady=ipadyButton, sticky="nesw")
        self.timButton.bind("<Return>", self.timer_pressed)
        self.timButton.bind("<Button-1>", self.timer_pressed)
        self.timButton.bind("<space>", self.timer_pressed)

    def create_bottom_buttons(self):
        """ Кнопки управления списком """
        self.buttonsFrame = ttk.Frame(self.boxRoot)
        self.buttonsFrame.pack(side=tk.BOTTOM, fill="y", expand=1)

        self.positiveButton = ttk.Button(self.buttonsFrame, takefocus=tk.YES, compound="left",
                                        text=self.getButton(self.positive, self.img)[0],
                                        image=self.getButton(self.positive, self.img)[1])
        self.positiveButton.bind("<Return>", self.positive_pressed)
        self.positiveButton.bind("<Button-1>", self.positive_pressed)
        self.positiveButton.bind("<space>", self.positive_pressed)

        self.neutralButton = ttk.Button(self.buttonsFrame, takefocus=tk.YES, compound="left",
                                        text=self.getButton(self.neutral, self.img)[0],
                                        image=self.getButton(self.neutral, self.img)[1])

        self.neutralButton.bind("<Return>", self.neutral_pressed)
        self.neutralButton.bind("<Button-1>", self.neutral_pressed)
        self.neutralButton.bind("<space>", self.neutral_pressed)

        # Кнопки, которые появляются только на множественном списке (Checklist) вместо positive и neutral

        self.selectAllButton = ttk.Button(self.buttonsFrame, text="Выбрать все")
        self.clearAllButton = ttk.Button(self.buttonsFrame, text="Снять все")
        self.selectAllButton.bind("<Button-1>", self.choiceboxSelectAll)
        self.clearAllButton.bind("<Button-1>", self.choiceboxClearAll)

        #ttk.Label(self.buttonsFrame, font=("Arial", 2)).grid(row=99) # небольшой разрыв под нижними кнопками для красоты

    def getButton(self, text="", img=[]):
        """ Выдает по запросу обработанный текст и картинку """
        if text != None:
            text2 = text[2:]
        else:
            return None, None
        image = None
        if "Таймер" in text:
            if ":" in text:
                image = img[1]
            else:
                image = img[0]
        elif reports.monthName()[2] in text:
            image = img[28]
        elif "Добавить" in text:
            image = img[2]
        elif "Сорт." in text and icons.icon("phone2") in text:
            image = img[6]
        elif "Сорт." in text and icons.icon("numbers") in text:
            image = img[7]
        elif "Сорт." in text and icons.icon("pin") in text:
            image = img[8]
        elif "Сорт." in text:
            image = img[3]
        elif "Детали" in text:
            image = img[4]
        elif "Обновл." in text:
            image = img[10]
        elif "Обнов" in text:
            image = img[5]
        elif "OK [Enter]" in text:
            image = img[14]
        elif "OK" in text:
            image = img[14]
            text2 = text
        elif "Назад" in text:
            image = None
            text2 = text
        elif "Сохранить" in text:
            image = img[9]
        elif "Помощь" in text:
            image = img[11]
        elif "Отмена [Esc]" in text:
            image = img[12]
        elif "[Esc]" in text:
            image = img[31]
        elif icons.icon("export") in text:
            image = img[13]
        elif "Аналитика" in text:
            image = img[15]
        elif "↑" in text:
            image = img[17]
        elif "↓" in text:
            image = img[18]
        elif "Журнал" in text:
            image = img[25]
        elif "Справка" in text:
            image = img[30]
        elif "F1" in text:
            image = img[32]
        else:
            text2 = text

        return text2, image

    def initialize_images(self):
        """ Загрузка картинок """
        ImgList = [
            "timer1.png"  # 0
            , "timer2.png"  # 1
            , "plus.png"  # 2
            , "sort.png"  # 3
            , "details.png"  # 4
            , "cancel.png"  # 5
            , "telephone.png"  # 6
            , "sort_numbers.png"  # 7
            , "pin.png"  # 8
            , "save.png"  # 9
            , "cancel.png"  # 10
            , "cancel.png"  # 11
            , "cancel.png"  # 12
            , "send.png"  # 13
            , "mark.png"  # 14
            , "calc.png"  # 15
            , "search.png"  # 16
            , "arrow_up.png"  # 17
            , "arrow_down.png"  # 18
            , "cancel.png"  # 19
            , "user.png"  # 20
            , "house.png"  # 21
            , "report.png"  # 22
            , "statistics.png"  # 23
            , "calendar.png"  # 24
            , "log.png"  # 25
            , "export.png"  # 26
            , "import.png"  # 27
            , "restore.png"  # 28
            , "clear.png"  # 29
            , "cancel.png"  # 30
            , "arrow_left.png"  # 31
            , "home.png"  # 32
            , "rocket64.png"  # 33
            , "notebook.png"  # 34
            , "calendar2.png"  # 35
            , "bell.png"  # 36
            , "error.png"  # 37
            , "happy.png"  # 38
            , "sad.png"     # 39
        ]
        self.img = []
        for image in ImgList:
            self.img.append(tk.PhotoImage(file=image))

    def create_footer(self):
        """ Подвал страницы """
        self.footerFrame = tk.Frame()
        self.footerFrame.pack(side=tk.BOTTOM, fill="both", expand=tk.YES)

        ttk.Separator(self.footerFrame, orient='horizontal').pack(fill='x')

        self.stats = tk.Label(self.footerFrame, compound="left", image = self.img[23], cursor="cross") # обработка участков
        self.stats.bind("<1>", self.stat_pressed)
        self.stats.pack(side=tk.LEFT)
        CreateToolTip(self.stats, "Средний уровень обработки ваших участков")

        def contacts_pressed_with_sort(event=None): # встречи на сегодня
            io2.settings[0][4]="в"
            self.contacts_pressed()
        self.meeting = tk.Label(self.footerFrame, compound="left", cursor="cross")
        self.meeting.bind("<1>", contacts_pressed_with_sort)
        CreateToolTip(self.meeting, "Встречи с контактами, запланированные на сегодня")

        def report_show(event=None): # напоминание сдать отчет
            report = reports.Report()
            report.showLastMonthReport()
        self.remind = tk.Label(self.footerFrame, compound="left", cursor="cross")
        self.remind.bind("<1>", report_show)
        CreateToolTip(self.remind, "Не забудьте сдать отчет!")

        def dueter_show(event=None):   # просроченный участок
            io2.settings[0][19] = "д"
            self.ter_pressed()
        self.dueter = tk.Label(self.footerFrame, compound="left", cursor="cross")
        self.dueter.bind("<1>", dueter_show)
        CreateToolTip(self.dueter, "У вас есть участки, которым больше полугода!")

        self.smile = tk.Label(self.footerFrame, compound="left", cursor="cross") # смайлик про запас или отставание
        self.smile.bind("<1>", self.report_pressed)

        ttk.Sizegrip(self.footerFrame).pack(side=tk.RIGHT) # грип