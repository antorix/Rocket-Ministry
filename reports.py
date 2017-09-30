#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import io2
import os
import sys
import webbrowser
import dialogs
import console
import contacts
from icons import icon

class Report():
    
    def __init__(self, settings):
        
        self.hours = settings[0]
        self.credit = settings[1]
        self.placements = settings[2]
        self.videos = settings[3]
        self.returns = settings[4]
        self.studies = settings[5]
        self.startTime = settings[6]
        self.endTime = settings[7]
        self.reportTime = settings[8]
        self.difTime = settings[9]
        self.note = settings[10]
        self.reminder = settings[11]
   
    def save(self, settings):
        """ Save last month report to file """
        
        rolloverHours = rolloverCredit = 0.0
        
        # Calculate rollovers
        
        if settings[0][15]==1: # rollover seconds to next month if activated
            rolloverHours = self.hours - int(self.hours)
            self.hours = int(self.hours-rolloverHours)            
            rolloverCredit = self.credit - int(self.credit)
            self.credit = int(self.credit-rolloverCredit)

        if settings[0][2]==1: credit = "Кредит: %0.2f\n" % self.credit # whether save credit to file
        else: credit = ""
        
        output = "Отчет за %s\n\nПубликации: %d\nВидео: %d\nЧасы: %0.2f\n%sПовторные посещения: %d\nИзучения Библии: %d\nПримечание: %s" % (monthName()[3], self.placements, self.videos, self.hours, credit, self.returns, self.studies, self.note)
        
        # Save file of last month
        
        if io2.osName=="android": 
            with open(io2.AndroidUserPath + "%s.txt" % monthName()[4],"w", encoding="utf-8") as file: file.write(output) #json.dump(output, file)
        else:
            with open("%s.txt" % monthName()[4],"w", encoding="utf-8") as file: file.write(output) #json.dump(output, file)
        
        # Clear service year in October
        
        if int(time.strftime("%m", time.localtime())) == 10: 
            settings[4] = [None, None, None, None, None, None, None, None, None, None, None, None]
            io2.log("Предыдущий служебный год очищен" % int(time.strftime("%m", time.localtime())))
        
        # Save last month hour+credit into service year
        
        settings[4][monthName()[7]-1] = self.hours + self.credit
        
        return rolloverHours, rolloverCredit # return rollovers for amending new month report
        
    def clear(self, settings, rolloverHours, rolloverCredit):
        """ Clears all fields of report """
        
        self.hours = 0.0 + rolloverHours
        self.credit = 0.0 + rolloverCredit
        self.placements = 0
        self.videos = 0
        self.returns = 0
        self.studies = 0
        self.startTime = 0
        self.endTime = 0
        self.reportTime = 0.0
        self.difTime = 0.0
        self.note = ""
        self.reminder = 1
                
    def modify(self, input, settings):
        """ Modifying report on external commands """
        
        try:
            if input[0]=="(": # start timer
                self.startTime = int(time.strftime("%H", time.localtime()))*3600 + int(time.strftime("%M", time.localtime()))*60 + int(time.strftime("%S", time.localtime()))
                vibrate(True, settings)
                #io2.log("Таймер запущен")
                    
            elif input[0]==")": # stop timer
                if self.startTime > 0:
                    self.endTime = int(time.strftime("%H", time.localtime()))*3600 + int(time.strftime("%M", time.localtime()))*60 + int(time.strftime("%S", time.localtime()))
                    self.reportTime = (self.endTime-self.startTime)/3600
                    #print("starttime: %d\nendtime: %d\nreporttime: %f" % (self.startTime, self.endTime, self.reportTime))
                    if self.reportTime<0: self.reportTime += 24 # if timer worked after 0:00 
                    self.hours += self.reportTime
                    io2.logReport("Таймер остановлен, в отчет добавлено: %0.2f ч." % self.reportTime)
                    self.startTime = 0
                    self.reportTime = 0.0
                    vibrate(False, settings)                
                
            elif not "1" in input and not "2" in input and not "3" in input and not "4" in input and not "5" in input and not "6" in input and not "7" in input and not "8" in input and not "9" in input and not "0" in input and not "(" in input and not ")" in input and not "*" in input and ("р" in input or "ж" in input or "ч" in input or "б" in input or "в" in input or "п" in input or "и" in input or "к" in input):
                message="В отчет добавлено:"
                for i in range(len(input)):
                    if input[i]=="ч":
                        self.hours += 1
                        message += "\nчас"
                    if input[i]=="р":
                        self.credit += 1
                        message += "\nкр. час"
                    if input[i]=="б":
                        self.placements += 1
                        message += "\nпубликация"
                    if input[i]=="ж":
                        self.placements += 1
                        message += "\nпубликация"
                    if input[i]=="к":
                        self.placements += 1
                        message += "\nпубликация"
                    if input[i]=="в":
                        self.videos += 1
                        message += "\nвидео"
                    if input[i]=="п":
                        self.returns += 1
                        message += "\nповторное"
                    if input[i]=="и":
                        self.studies += 1
                        message += "\nизучение"
                io2.logReport(message)
                
            elif input[0]=="ч": # commands like @п2
                self.hours += float(input[1:])
                io2.logReport("В отчет добавлено: %0.2f ч." % float(input[1:]))
            elif input[0]=="ж":
                self.placements += int(input[1:])
                io2.logReport("В отчет добавлено: %d пуб." % int(input[1:]))
            elif input[0]=="к":
                self.placements += int(input[1:])
                io2.logReport("В отчет добавлено: %d пуб." % int(input[1:]))
            elif input[0]=="б":
                self.placements += int(input[1:])
                io2.logReport("В отчет добавлено: %d пуб." % int(input[1:]))
            elif input[0]=="р":
                self.credit += float(input[1:])
                io2.logReport("В отчет добавлено: %0.2f ч. кредита" % float(input[1:]))
            elif input[0]=="в":
                self.videos += int(input[1:])
                io2.logReport("В отчет добавлено: %d вид." % int(input[1:]))
            elif input[0]=="п":
                self.returns += int(input[1:])
                io2.logReport("В отчет добавлено: %d ПП" % int(input[1:]))
            elif input[0]=="и":
                self.studies += int(input[1:])
                io2.logReport("В отчет добавлено: %d ИБ" % int(input[1:]))
            elif input[0]=="*":
                self.note = input[1:]
                io2.logReport("Примечание отчета: %s" % self.note)
        except: pass
            #io2.log("Не удалось распознать ввод")
    
    def display(self, houses, settings, resources):
        """ Displaying report """
        
        if "--textconsole" in sys.argv: pureText=True
        else: pureText=False
        
        if settings[0][8]==1 and settings[2][11]==1: # show reminder dialog
            answer=dialogs.dialogConfirm(icon("lamp", settings[0][4]) + " " + getTimerIcon(self.startTime, settings), "Вы уже сдали отчет за %s?" % monthName()[3])
            console.process(answer, houses, settings, resources)
            if answer==True: self.reminder = 0
        
        while 1:            
            
            title = icon("report", settings[0][4]) + " Отчет за %s %s " % (monthName()[1], getTimerIcon(self.startTime, settings))
            
            gap = float((self.hours+self.credit) - int(time.strftime("%d", time.localtime()))*settings[0][3]/days())
            
            if gap >= 0: gap_str = icon("extra", settings[0][4]) + " Запас: %0.2f" % gap # happy emoticon
            else: gap_str = icon("slippage", settings[0][4]) + " Отставание: %0.2f" % -gap # crying emoticon
            
            if self.startTime > 0 and self.reportTime == 0:
                self.endTime = int(time.strftime("%H", time.localtime()))*3600 + int(time.strftime("%M", time.localtime()))*60 + int(time.strftime("%S", time.localtime()))
                self.difTime = (self.endTime-self.startTime)/3600
                
            # Main report list
            
            if settings[0][2]==1:
                hoursLine = icon("timer", settings[0][4]) + " Часы: %0.2f\n     (с кредитом: %0.2f)" % (self.hours, self.hours+self.credit)
            else:
                hoursLine = icon("timer", settings[0][4]) + " Часы: %0.2f" % self.hours
            
            message = "Ваш отчет"
            options = [
                icon("placements", settings[0][4]) + " Публикации: %d" % self.placements,
                icon("videos", settings[0][4]) + " Видео: %d" % self.videos,
                hoursLine]
                
            if settings[0][3]!=0: options.append(gap_str)
                
            if settings[0][2]==1: options.append(icon("credit", settings[0][4]) + " Кредит: %0.2f" % self.credit)
            
            options.append(icon("returns", settings[0][4]) + " Повторные: %d" % self.returns)
            options.append(icon("studies", settings[0][4]) + " Изучения: %d" % self.studies)
            options.append(icon("pin", settings[0][4]) + " Примечание: %s" % self.note)
            options.append(icon("logreport", settings[0][4]) + " Журнал")
                
            if io2.osName!="android":
                if io2.Textmode==False: options.append(icon("console", settings[0][4]) + " Консоль") # positive button on Android
                options.append(monthName()[2]) # neutral button on Android
                
            if settings[0][5]==1:
                consoleStatus = icon("console", settings[0][4]) + " Консоль"
                buttonStatus = True
            else:
                consoleStatus = ""
                buttonStatus = False
            
            choice = dialogs.dialogList(
                title=title,
                form = "display",
                message=message,
                options=options,
                settings=settings,
                neutral = monthName()[2],                
                neutralButton = True,
                positiveButton = buttonStatus,
                positive = consoleStatus)
            console.process(choice, houses, settings, resources)
            choice2=""
            
            if contacts.ifInt(choice)==True: result = options[choice]
            else: result=choice
         
            if result==None: break
            
            elif "neutral" in result: # last month report
                if io2.osName=="android":
                    if os.path.exists(io2.AndroidUserPath + "%s.txt" % monthName()[4]):
                        try:
                            with open(io2.AndroidUserPath + "%s.txt" % monthName()[4], "r", encoding="utf-8") as file: report=file.read()#report = json.load(file)
                        except:
                            io2.log("Не удалось загрузить отчет")
                            continue
                    else:
                        io2.log("Отчет за %s не найден!" % monthName()[3])
                        continue                        
                else:
                    if os.path.exists("%s.txt" % monthName()[4]):
                        with open("%s.txt" % monthName()[4], "r", encoding="utf-8") as file: report=file.read()#report = json.load(file)
                    else:
                        io2.log("Отчет за %s не найден!" % monthName()[3])                       
                        continue
                
                answer=dialogs.dialogConfirm(
                        title = icon("report", settings[0][4]) + " Архив " + getTimerIcon(settings[2][6], settings),
                        message=report,
                        choices=[icon("export", settings[0][4]) + " Экспорт", "Назад"]
                    )
                console.process(answer, houses, settings, resources)
                if answer==True: # export last month report
                    if io2.osName == "android":
                        try:
                            from androidhelper import Android
                            Android().sendEmail("Введите email","Отчет за %s" % monthName()[3],report,attachmentUri=None)
                            os.system("clear")
                            input("\nНажмите Enter для возврата")                
                        except IOError:
                            io2.log("Экспорт не удался!")
                        else: io2.log("Экспорт выполнен")
                        os.system("clear")
                    else: webbrowser.open(monthName()[4] + ".txt")
                
            elif "positive" in result: # console
                if console.dialog(houses, settings, resources)==True: return True
                    
                self.hours = settings[2][0]
                self.credit = settings[2][1]
                self.placements = settings[2][2]
                self.videos = settings[2][3]
                self.returns = settings[2][4]
                self.studies = settings[2][5]
                self.startTime = settings[2][6]
                self.endTime = settings[2][7]
                self.reportTime = settings[2][8]
                self.difTime = settings[2][9]
                self.note = settings[2][10]
                self.reminder = settings[2][11]
                    
            elif choice==None: break # exit
                
            elif "Публикации" in result: # placements
                while choice2!=None:
                    choice2 = dialogs.dialog(title=icon("placements", settings[0][4], pureText=pureText) + " Публикации " + getTimerIcon(self.startTime, settings), message="Изменение на:")     
                    console.process(choice2, houses, settings, resources)
                    try:
                        self.placements += int(choice2)
                    except:
                        if choice2!=None:
                            if "cancelled!" in choice2: continue
                            io2.log("Не удалось изменить, попробуйте еще")
                        continue
                    else:
                        io2.logReport("В отчет добавлено: %d пуб." % int(choice2))
                        break
            
            elif "Видео" in result: # video
                while choice2!=None:
                    choice2 = dialogs.dialog(title=icon("videos", settings[0][4], pureText=pureText) + " Видео " + getTimerIcon(self.startTime, settings), message="Изменение на:")                    
                    console.process(choice2, houses, settings, resources)
                    try: self.videos += int(choice2)
                    except:
                        if choice2!=None:
                            if "cancelled!" in choice2: continue
                            io2.log("Не удалось изменить, попробуйте еще")
                        continue
                    else:
                        io2.logReport("В отчет добавлено: %d вид." % int(choice2))
                        break
                        
            elif "Часы" in result: # hours
                while choice2!=None:
                    choice2 = dialogs.dialog(title=icon("timer", settings[0][4], pureText=pureText) + " Часы " + getTimerIcon(self.startTime, settings), message="Изменение на:")
                    console.process(choice2, houses, settings, resources)
                    try: self.hours += float(choice2)
                    except:
                        if choice2!=None:
                            if "cancelled!" in choice2: continue
                            io2.log("Не удалось изменить, попробуйте еще")
                        continue
                    else:
                        io2.logReport("В отчет добавлено: %0.2f ч." % float(choice2))
                        break
                        
            elif "Запас" in result or "Отставание" in result: # gap
                while 1:
                    choice2 = dialogs.dialog(
                    title=icon("extra", settings[0][4], pureText=pureText) + " Запас/отставание " + getTimerIcon(settings[2][6], settings),
                    message="Введите месячную норму часов для подсчета запаса или отставания от нормы по состоянию на текущий день. Чтобы не показывать норму в отчете, введите 0 (можно снова активировать в настройках):",
                    default = str(settings[0][3]))
                    console.process(choice2, houses, settings, resources)
                    try:
                        if choice2!=None:
                            if "cancelled!" in choice2: continue
                            elif choice2=="": settings[0][3]=0
                            else: settings[0][3] = int(choice2)
                        else: break
                    except:
                        io2.logReport("Не удалось изменить, попробуйте еще")
                        continue
                    else: break
                
            elif "Кредит" in result: # credit hours
                while choice2!=None:
                    choice2 = dialogs.dialog(title=icon("credit", settings[0][4], pureText=pureText) + " Кредит " + getTimerIcon(self.startTime, settings), message="Изменение на:")
                    console.process(choice2, houses, settings, resources)
                    try: self.credit += float(choice2)
                    except:
                        if choice2!=None:
                            if "cancelled!" in choice2: continue
                            io2.log("Не удалось изменить, попробуйте еще")
                        continue
                    else:
                        io2.logReport("В отчет добавлено: %0.2f ч. кредита" % float(choice2))
                        break
                        
            elif "Повторные" in result: # returns
                while choice2!=None:
                    choice2 = dialogs.dialog(title=icon("returns", settings[0][4], pureText=pureText) + " Повторные " + getTimerIcon(self.startTime, settings), message="Изменение на:") 
                    console.process(choice2, houses, settings, resources)
                    try: self.returns += int(choice2)
                    except:
                        if choice2!=None:
                            if "cancelled!" in choice2: continue
                            io2.log("Не удалось изменить, попробуйте еще")
                        continue
                    else:
                        io2.logReport("В отчет добавлено: %d ПП" % int(choice2))
                        break
            
            elif "Изучения" in result: # studies
                while choice2!=None:
                    choice2 = dialogs.dialog(title=icon("studies", settings[0][4], pureText=pureText) + " Изучения " + getTimerIcon(self.startTime, settings), message="Изменение на:") 
                    console.process(choice2, houses, settings, resources)
                    try: self.studies += int(choice2)
                    except:
                        if choice2!=None:
                            if "cancelled!" in choice2: continue
                            io2.log("Не удалось изменить, попробуйте еще")
                        continue
                    else:
                        io2.logReport("В отчет добавлено: %d ИБ" % int(choice2))
                        break  
              
            elif "Примечание" in result: # note
                choice2 = dialogs.dialog(title=icon("pin", settings[0][4], pureText=pureText) + " Примечание " + getTimerIcon(self.startTime, settings), default=self.note)            
                console.process(choice2, houses, settings, resources)
                if choice2!=None:
                    if "cancelled!" in choice2: continue
                    self.note = choice2
                    
            elif "Журнал" in result: # show logReport
                if io2.osName=="android":
                    if os.path.exists(io2.AndroidUserPath + "logreport.txt"):   
                        with open(io2.AndroidUserPath + "logreport.txt", encoding="utf-8") as file: text = file.read()
                        choice=dialogs.dialogInfo(
                            title=icon("logreport", settings[0][4]) + " Журнал отчета %s" % getTimerIcon(settings[2][6], settings),
                            message=text,
                            neutralButton=True,
                            neutral="Очистить"
                        )
                        console.process(choice, houses, settings, resources)
                        if choice=="neutral" and dialogs.dialogConfirm(message="Полностью очистить журнал отчета?")==True:
                            os.remove(io2.AndroidUserPath + "logreport.txt")
                    else: io2.log("Файл журнала не найден! Попробуйте внести хотя бы одно изменение в отчет.")
                else:
                    if os.path.exists("logreport.txt"):   
                        with open("logreport.txt", encoding="utf-8") as file: text = file.read()
                        choice=dialogs.dialogHelp(
                            title=icon("logreport", settings[0][4]) + " Журнал отчета %s" % getTimerIcon(settings[2][6], settings),
                            message=text,
                            neutral="Очистить"
                        )
                        console.process(choice, houses, settings, resources)                        
                        if choice.strip()=="" and dialogs.dialogConfirm(message="Полностью очистить журнал отчета?")==True:
                            os.remove("logreport.txt")
                    else: io2.log("Файл журнала не найден! Попробуйте внести хотя бы одно изменение в отчет.")
                
        if exit==1: return True
            
def updateTimer(startTime):
    """ Returns current endTime to anyone """
    
    endTime = int(time.strftime("%H", time.localtime()))*3600 + int(time.strftime("%M", time.localtime()))*60 + int(time.strftime("%S", time.localtime()))
    return (endTime - startTime)/3600
        
def getTimerIcon(startTime, settings):
    """ Returns timer and ringer icon, if active, and add silent icon on Android """
    
    if startTime > 0:
        output = " " + icon("timer", settings[0][4])
        if io2.osName=="android":
            if settings[0][0]==1:
                output += " " + icon("mute", settings[0][4])
                vibrate(True, settings)
            else: vibrate(False, settings)
            
        return output
        
    else: return ""
    
def vibrate(key, settings):
    """ Toggle ringer on/off """
    
    if io2.osName != "android": return
    if settings[0][0]==1:
        from androidhelper import Android
        if key==True:
            Android().setRingerVolume(0)
            return
        elif key==False:
            Android().setRingerVolume(100)
            return
    
def checkNewMonth(settings):
    """ Checks if month is over """
    
    savedMonth = settings[3]
    currentMonth = time.strftime("%b", time.localtime())    
    #print("Saved month: %s\nCurrent month: %s" % (savedMonth, currentMonth))    
    if savedMonth==currentMonth: return False   # same month
    else: return True                           # new month began    

def monthName(monthCode=None, monthNum=None):
    """ Returns names of current and last months in lower and upper cases """
    
    if monthCode!=None: month=monthCode
    elif monthNum!=None:
        if monthNum==1:     month="Jan"
        elif monthNum==2:   month="Feb"
        elif monthNum==3:   month="Mar"
        elif monthNum==4:   month="Apr"
        elif monthNum==5:   month="May"
        elif monthNum==6:   month="Jun"
        elif monthNum==7:   month="Jul"
        elif monthNum==8:   month="Aug"
        elif monthNum==9:   month="Sep"
        elif monthNum==10:   month="Oct"
        elif monthNum==11:   month="Nov"
        elif monthNum==12:   month="Dec"
    else:
        month = time.strftime("%b", time.localtime())

    if month=="Jan":
        curMonthUp = "Январь"
        curMonthLow = "январь"
        lastMonthUp = "Декабрь"
        lastMonthLow = "декабрь"
        lastMonthEn = "Dec"
        curMonthRuShort = "янв."
        monthNum = 1
        lastTheoMonthNum = 4
        curTheoMonthNum = 5
    if month=="Feb":
        curMonthUp = "Февраль"
        curMonthLow = "февраль"
        lastMonthUp = "Январь"
        lastMonthLow = "январь"
        lastMonthEn = "Jan"
        curMonthRuShort = "фев."
        monthNum = 2
        lastTheoMonthNum = 5
        curTheoMonthNum = 6
    if month=="Mar":
        curMonthUp = "Март"
        curMonthLow = "март"
        lastMonthUp = "Февраль"
        lastMonthLow = "февраль"
        lastMonthEn = "Feb"
        curMonthRuShort = "мар."
        monthNum = 3
        lastTheoMonthNum = 6
        curTheoMonthNum = 7
    if month=="Apr":
        curMonthUp = "Апрель"
        curMonthLow = "апрель"
        lastMonthUp = "Март"
        lastMonthLow = "март"
        lastMonthEn = "Mar"
        curMonthRuShort = "апр."
        monthNum = 4
        lastTheoMonthNum = 7
        curTheoMonthNum = 8
    if month=="May":
        curMonthUp = "Май"
        curMonthLow = "май"
        lastMonthUp = "Апрель"
        lastMonthLow = "апрель"
        lastMonthEn = "Apr"
        curMonthRuShort = "мая"
        monthNum = 5
        lastTheoMonthNum = 8
        curTheoMonthNum = 9
    if month=="Jun":
        curMonthUp = "Июнь"
        curMonthLow = "июнь"
        lastMonthUp = "Май"
        lastMonthLow = "май"
        lastMonthEn = "May"
        curMonthRuShort = "июн."
        monthNum = 6
        lastTheoMonthNum = 9
        curTheoMonthNum = 10
    if month=="Jul":
        curMonthUp = "Июль"
        curMonthLow = "июль"
        lastMonthUp = "Июнь"
        lastMonthLow = "июнь"
        lastMonthEn = "Jun"
        curMonthRuShort = "июл."
        monthNum = 7
        lastTheoMonthNum = 10
        curTheoMonthNum = 11
    if month=="Aug":
        curMonthUp = "Август"
        curMonthLow = "август"
        lastMonthUp = "Июль"
        lastMonthLow = "июль"
        lastMonthEn = "Jul"
        curMonthRuShort = "авг."
        monthNum = 8
        lastTheoMonthNum = 11
        curTheoMonthNum = 12
    if month=="Sep":
        curMonthUp = "Сентябрь"
        curMonthLow = "сентябрь"
        lastMonthUp = "Август"
        lastMonthLow = "август"
        lastMonthEn = "Aug"
        curMonthRuShort = "сен."
        monthNum = 9
        lastTheoMonthNum = 12
        curTheoMonthNum = 1
    elif month=="Oct":
        curMonthUp = "Октябрь"
        curMonthLow = "октябрь"
        lastMonthUp = "Сентябрь"
        lastMonthLow = "сентябрь"
        lastMonthEn = "Sep"
        curMonthRuShort = "окт."
        monthNum = 10
        lastTheoMonthNum = 1
        curTheoMonthNum = 2
    if month=="Nov":
        curMonthUp = "Ноябрь"
        curMonthLow = "ноябрь"
        lastMonthUp = "Октябрь"
        lastMonthLow = "октябрь"
        lastMonthEn = "Oct"
        curMonthRuShort = "нояб."
        monthNum = 11
        lastTheoMonthNum = 2
        curTheoMonthNum = 3
    if month=="Dec":
        curMonthUp = "Декабрь"
        curMonthLow = "декабрь"
        lastMonthUp = "Ноябрь"
        lastMonthLow = "ноябрь"
        lastMonthEn = "Nov"
        curMonthRuShort = "дек."
        monthNum = 12
        lastTheoMonthNum = 3
        curTheoMonthNum = 4
        
    return curMonthUp, curMonthLow, lastMonthUp, lastMonthLow, lastMonthEn, curMonthRuShort, monthNum, lastTheoMonthNum, curTheoMonthNum
        
def days():
    """ Returns number of days in current month """
    
    if time.strftime("%b", time.localtime())=="Jan": return 31
    elif time.strftime("%b", time.localtime())=="Feb": return 30
    elif time.strftime("%b", time.localtime())=="Mar": return 31
    elif time.strftime("%b", time.localtime())=="Apr": return 30
    elif time.strftime("%b", time.localtime())=="May": return 31
    elif time.strftime("%b", time.localtime())=="Jun": return 30
    elif time.strftime("%b", time.localtime())=="Jul": return 31
    elif time.strftime("%b", time.localtime())=="Aug": return 31
    elif time.strftime("%b", time.localtime())=="Sep": return 30
    elif time.strftime("%b", time.localtime())=="Oct": return 31
    elif time.strftime("%b", time.localtime())=="Nov": return 30
    elif time.strftime("%b", time.localtime())=="Dec": return 31
    else: return 30.5
    
def report(houses, settings, resources, choice="", stop=False):
    """ Callable program """
    
    exit=0
    
    report = Report(settings[2]) # create current report   
    
    # Check if new month began
    
    if checkNewMonth(settings)==True:
        rolloverHours, rolloverCredit = report.save(settings)
        report.clear(settings, rolloverHours, rolloverCredit)
        io2.logReport("Начался новый месяц, отчет за %s заархивирован" % monthName()[3])
        settings[3] = time.strftime("%b", time.localtime())
        settings[2][11]=1 # turn on report reminder
        stop=False
    
    if stop==True:
        if exit==1: return True
        else: return False    
    
    if len(choice) > 1:
        report.modify(choice[1:], settings) # if report called with string input, it is instantly passed to modify(), else just displays
    else:
        if report.display(houses, settings, resources)==True: exit=1
    
    settings[2] = [ # forming updated stats
    report.hours,
    report.credit,
    report.placements,
    report.videos,
    report.returns,
    report.studies,
    report.startTime,
    report.endTime,
    report.reportTime,
    report.difTime,
    report.note,
    report.reminder
    ]    
    
    io2.save(houses, settings, resources)

    if exit==1: return True
