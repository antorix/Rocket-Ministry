#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import io2
from io2 import settings
import os
import webbrowser
import dialogs
import console
import set
import datetime
from icons import icon

class Report():

    def __init__(self):
        
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
   
    def saveReport(self, message=""):
        """ Выгрузка данных из класса в настройки, сохранение и оповещение """
        settings[2] = [
            self.hours,
            self.credit,
            self.placements,
            self.videos,
            self.returns,
            self.studies,
            self.startTime,
            self.endTime,
            self.reportTime,
            self.difTime,
            self.note,
            self.reminder
        ]
        io2.save()
        io2.logReport(message)

    def saveLastMonth(self):
        """ Save last month report to file """
        
        rolloverHours = rolloverCredit = 0.0
                
        """
        # Adjust credit so that self.hours + self.credit <= 75 h.
        
        creditOld = self.credit
        if (self.hours + self.credit) > 75:
            self.credit = 75 - self.hours            
            if self.credit < 0:
                self.credit = 0
            io2.log("Отсечено %0.2f ч. кредита" % (creditOld - self.credit))
        """

        # Calculate rollovers
        if settings[0][15]==1: # rollover seconds to next month if activated
            rolloverHours = round(self.hours,2) - int(round(self.hours,2))
            self.hours = int(round(self.hours,2)-rolloverHours)
            rolloverCredit = round(self.credit,2) - int(round(self.credit,2))
            self.credit = int(round(self.credit,2)-rolloverCredit)

        if settings[0][2]==1:
            credit = "Кредит: %0.2f\n" % self.credit # whether save credit to file
        else:
            credit = ""

        # Save file of last month
        output = "Отчет за %s\n\nПубликации: %d\nВидео: %d\nЧасы: %0.2f\n%sПовторные посещения: %d\nИзучения Библии: %d" %\
                 (monthName()[3], self.placements, self.videos, self.hours, credit, self.returns, self.studies)
        if self.note!="":
            output += "\nПримечание: " + self.note
        if io2.osName=="android": 
            with open(io2.AndroidUserPath + "%s.txt" % monthName()[4],"w", encoding="utf-8") as file: file.write(output) #json.dump(output, file)
        else:
            with open("%s.txt" % monthName()[4],"w", encoding="utf-8") as file: file.write(output) #json.dump(output, file)
        
        # Clear service year in October        
        if int(time.strftime("%m", time.localtime())) == 10: 
            settings[4] = [None, None, None, None, None, None, None, None, None, None, None, None]
            io2.log("Предыдущий, %s-й, служебный год очищен" % int(time.strftime("%Y", time.localtime())))
        
        # Save last month hour+credit into service year
        settings[4][monthName()[7]-1] = self.hours + self.credit
        
        return rolloverHours, rolloverCredit # return rollovers for amending new month report
        
    def clear(self, rolloverHours, rolloverCredit):
        """ Clears all fields of report """
        
        self.hours = "00:00" #+ rolloverHours
        self.credit = "00:00" #+ rolloverCredit
        self.placements = 0
        self.videos = 0
        self.returns = 0
        self.studies = 0
        self.startTime = "00:00"
        self.endTime = "00:00"
        self.reportTime = "00:00"
        self.difTime = "00:00"
        self.note = ""
        self.reminder = 1
                
    def modify(self, input):
        """ Modifying report on external commands """

        if input[0]=="(": # start timer
            self.startTime = time.strftime("%H:%M", time.localtime())
            vibrate(True)
            self.saveReport("Таймер запущен")

        elif input[0]==")": # stop timer
            if timeHHMMToTimeDelta(self.startTime) > zeroTimeDelta():
                self.endTime = time.strftime("%H:%M", time.localtime())
                hoursStart=int(self.startTime[0:2])
                minutesStart=int(self.startTime[3:5])
                hoursEnd = int(self.endTime[0:2])
                minutesEnd = int(self.endTime[3:5])
                self.reportTime = timeDeltaToHHMM(
                    datetime.timedelta(hours=hoursEnd, minutes=minutesEnd) -\
                    datetime.timedelta(hours=hoursStart, minutes=minutesStart)
                )
                self.hours = timeDeltaToHHMM( timeHHMMToTimeDelta(self.hours) + timeHHMMToTimeDelta(self.reportTime) )
                self.saveReport("Таймер остановлен, в отчет добавлено: %s." % self.reportTime)
                self.startTime = "00:00"
                self.reportTime = "00:00"
                self.saveReport()
                vibrate(False)

        elif input[0]=="$": # credit
            if settings[0][2] == 0:
                io2.log("Включите учет кредита в настройках")
            elif timeHHMMToTimeDelta(settings[2][6]) != zeroTimeDelta():
                self.endTime = time.strftime("%H:%M", time.localtime())
                hoursStart = int(self.startTime[0:2])
                minutesStart = int(self.startTime[3:5])
                hoursEnd = int(self.endTime[0:2])
                minutesEnd = int(self.endTime[3:5])
                self.reportTime = timeDeltaToHHMM(
                    datetime.timedelta(hours=hoursEnd, minutes=minutesEnd) - \
                    datetime.timedelta(hours=hoursStart, minutes=minutesStart)
                )
                self.credit = timeDeltaToHHMM(timeHHMMToTimeDelta(self.credit) + timeHHMMToTimeDelta(self.reportTime))
                self.saveReport("Таймер остановлен, в отчет добавлено: %s кредита" % self.reportTime)
                self.startTime = "00:00"
                self.reportTime = "00:00"
                self.saveReport()
                vibrate(False)

        elif not "1" in input and not "2" in input and not "3" in input and not "4" in input and not "5" in input\
                and not "6" in input and not "7" in input and not "8" in input and not "9" in input and not "0" in input\
                and not "(" in input and not ")" in input and not "*" in input\
                and ("р" in input or "ж" in input or "ч" in input or "б" in input or "в" in input or "п" in input or "и" in input or "к" in input):
            message="В отчет добавлено:"
            for i in range(len(input)):
                if input[i]=="ч":
                    self.hours = timeDeltaToHHMM(timeHHMMToTimeDelta(self.hours) + datetime.timedelta(hours=1))
                    message += "\nчас"
                if input[i]=="р":
                    self.credit = timeDeltaToHHMM(timeHHMMToTimeDelta(self.credit) + datetime.timedelta(hours=1))
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
            self.saveReport(message)

        elif input[0]=="ч": # commands like %ч2
            self.hours = timeDeltaToHHMM(timeHHMMToTimeDelta(self.hours) + datetime.timedelta(hours=int(input[1:])))
            self.saveReport("В отчет добавлено: %d ч." % int(input[1:]))
        elif input[0] == "р":
            self.credit = timeDeltaToHHMM(timeHHMMToTimeDelta(self.credit) + datetime.timedelta(hours=int(input[1:])))
            self.saveReport("В отчет добавлено: %d ч. кредита" % int(input[1:]))
        elif input[0]=="ж":
            self.placements += int(input[1:])
            self.saveReport("В отчет добавлено: %d пуб." % int(input[1:]))
        elif input[0]=="к":
            self.placements += int(input[1:])
            self.saveReport("В отчет добавлено: %d пуб." % int(input[1:]))
        elif input[0]=="б":
            self.placements += int(input[1:])
            self.saveReport("В отчет добавлено: %d пуб." % int(input[1:]))
        elif input[0]=="в":
            self.videos += int(input[1:])
            self.saveReport("В отчет добавлено: %d вид." % int(input[1:]))
        elif input[0]=="п":
            self.returns += int(input[1:])
            self.saveReport("В отчет добавлено: %d ПП" % int(input[1:]))
        elif input[0]=="и":
            self.studies += int(input[1:])
            self.saveReport("В отчет добавлено: %d ИБ" % int(input[1:]))
        elif input[0]=="*":
            self.note = input[1:]
            self.saveReport("Примечание отчета: %s" % self.note)
        #except:
        #    io2.log("Не удалось распознать ввод")
                
    def display(self):
        """ Displaying report """

        if settings[0][8]==1 and settings[2][11]==1: # show reminder dialog
            if io2.osName == "android":
                from androidhelper import Android
                Android().notify("Отчет", "Не забыть сдать отчет!")
            answer=dialogs.dialogConfirm(icon("lamp") + " " + getTimerIcon(self.startTime), "Вы уже сдали отчет за %s?" % monthName()[3])
            #console.process(answer)
            if answer==True:
                self.reminder = 0
        
        while 1:

            # Главный цикл показа отчета
            
            title = icon("report") + " Отчет за %s %s " % (monthName()[1], getTimerIcon(self.startTime))

            gap = hourGap(self.hours, self.credit)
            
            if gap >= 0:
                gap_str = icon("extra2") + " Запас: %s" % timeFloatToHHMM(gap) # happy emoticon
            else:
                gap_str = icon("slippage") + " Отставание: %s" % timeFloatToHHMM(-gap) # crying emoticon
            
            if timeHHMMToTimeDelta(self.startTime) > zeroTimeDelta() and timeHHMMToTimeDelta(self.reportTime) == zeroTimeDelta():
                self.endTime = time.strftime("%H:%M", time.localtime())
                hoursStart = int(self.startTime[0:2])
                minutesStart = int(self.startTime[3:5])
                hoursEnd = int(self.endTime[0:2])
                minutesEnd = int(self.endTime[3:5])
                self.difTime = timeDeltaToHHMM(
                    datetime.timedelta(hours=hoursEnd, minutes=minutesEnd) -\
                    datetime.timedelta(hours=hoursStart, minutes=minutesStart)
                )
            
            if settings[0][2]==1:
                combinedHours = timeDeltaToHHMM( timeHHMMToTimeDelta(self.hours) + timeHHMMToTimeDelta(self.credit) )
                hoursLine = icon("timer") + " Часы: %s\n     (с кредитом: %s)" % (self.hours, combinedHours)
            else:
                hoursLine = icon("timer") + " Часы: %s" % self.hours
            
            message = "Ваш отчет"
            options = [
                icon("placements") + " Публикации: %d" % self.placements,
                icon("video") + " Видео: %d" % self.videos,
                hoursLine
            ]
                
            if settings[0][3]!=0:
                options.append(gap_str)
                
            if settings[0][2]==1:
                options.append(icon("credit") + " Кредит: %s" % self.credit)
            
            options.append(icon("returns")  + " Повторные: %d" % self.returns)
            options.append(icon("studies")  + " Изучения: %d" % self.studies)
            options.append(icon("pin")      + " Примечание: %s" % self.note)
            options.append(icon("logreport")+ " Журнал")
                
            if io2.osName!="android":
                options.append(icon("prevmonth") + " " + monthName()[2]) # neutral button on Android

            choice = dialogs.dialogList(
                title=title,
                form = "display",
                message=message,
                options=options,
                neutral = monthName()[2],                
                neutralButton = True)
            #console.process(choice)
            choice2=""
            result=set.unify(options, choice)
         
            if result==None:                
                return

            elif result == "":
                if io2.settings[0][1] == True:
                    return
            
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
                        title = icon("report") + " Архив " + getTimerIcon(settings[2][6]),
                        message=report,
                        choices=[icon("export") + " Экспорт", "Назад"]
                    )
                #console.process(answer)
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
                    else:
                        webbrowser.open(monthName()[4] + ".txt")
                    
            elif choice==None:
                break # exit

            elif "Публикации" in result: # placements
                while choice2!=None:
                    choice2 = dialogs.dialogText(
                        neutralButton=True,
                        autoplus=True,
                        title=icon("placements") + " Публикации " + getTimerIcon(self.startTime),
                        message="Изменение на:"
                    )
                    #console.process(choice2)
                    if choice2 == "":
                        break
                    else:
                        try:
                            self.placements += int(choice2)
                            self.saveReport()
                        except:
                            if choice2!=None:
                                if "cancelled!" in choice2:
                                    continue
                                if "neutral" in choice2:
                                    self.placements += 1
                                    self.saveReport("В отчет добавлена 1 публикация")
                                    continue
                                io2.log("Не удалось изменить, попробуйте еще")
                            continue
                        else:
                            self.saveReport("В отчет добавлено: %d пуб." % int(choice2))
                            break
            
            elif "Видео" in result: # video
                while choice2!=None:
                    choice2 = dialogs.dialogText(
                        neutralButton=True,
                        autoplus=True,
                        title=icon("videos") + " Видео " + getTimerIcon(self.startTime),
                        message="Изменение на:"
                    )
                    console.process(choice2)
                    if choice2 == "":
                        break
                    else:
                        try:
                            self.videos += int(choice2)
                        except:
                            if choice2!=None:
                                if "cancelled!" in choice2:
                                    continue
                                if "neutral" in choice2:
                                    self.videos += 1
                                    self.saveReport("В отчет добавлено 1 видео")
                                    continue
                                io2.log("Не удалось изменить, попробуйте еще")
                            continue
                        else:
                            self.saveReport("В отчет добавлено: %d вид." % int(choice2))
                            break
                        
            elif "Часы" in result: # hours
                while choice2!=None:
                    choice2 = dialogs.dialogText(
                        neutralButton=True,
                        autoplus=True,
                        title=icon("timer") + " Часы " + getTimerIcon(self.startTime),
                        message="Изменение на (ЧЧ:ММ):"
                    )
                    console.process(choice2)
                    if choice2 == "":
                        break
                    else:
                        try:
                            if choice2[0]!="-":
                                self.hours = timeDeltaToHHMM( timeHHMMToTimeDelta(self.hours) + timeHHMMToTimeDelta(choice2) )
                            else:
                                self.hours = timeDeltaToHHMM( timeHHMMToTimeDelta(self.hours) - timeHHMMToTimeDelta(choice2[1:]) )
                        except:
                            if choice2!=None:
                                if "cancelled!" in choice2:
                                    continue
                                if "neutral" in choice2:
                                    self.hours = timeDeltaToHHMM( timeHHMMToTimeDelta(self.hours) + datetime.timedelta(hours=1) )
                                    self.saveReport("В отчет добавлен 1 час")
                                    continue
                                io2.log("Ошибка! Требуется формат Ч или ЧЧ:ММ, можно с минусом")
                            continue
                        else:
                            self.saveReport("В отчет добавлено: %s ч." % choice2)
                            break
                        
            elif "Запас" in result or "Отставание" in result: # gap
                while 1:
                    choice2 = dialogs.dialogText(
                        title=icon("extra") + " Запас/отставание " + getTimerIcon(settings[2][6]),
                        message="Введите месячную норму часов для подсчета запаса или отставания от нормы по состоянию на текущий день. Чтобы не показывать норму в отчете, введите 0 (можно снова активировать в настройках):",
                        default = str(settings[0][3])
                    )
                    console.process(choice2)
                    if choice2 == "":
                        break
                    else:
                        try:
                            if choice2!=None:
                                if "cancelled!" in choice2: continue
                                elif choice2=="":
                                    settings[0][3]=0
                                    io2.save()
                                else:
                                    settings[0][3] = int(choice2)
                                    io2.save()
                            else: break
                        except:
                            io2.logReport("Ошибка! Требуется формат Ч или ЧЧ:ММ, можно с минусом")
                            continue
                        else:
                            break
                
            elif "Кредит" in result: # credit hours
                while choice2!=None:
                    choice2 = dialogs.dialogText(
                        neutralButton=True,
                        autoplus=True,
                        title=icon("credit") + " Кредит " + getTimerIcon(self.startTime),
                        message="Изменение на:"
                    )
                    console.process(choice2)
                    if choice2 == "":
                        break
                    else:
                        try:
                            if choice2[0]!="-":
                                self.credit = timeDeltaToHHMM(timeHHMMToTimeDelta(self.credit) + timeHHMMToTimeDelta(choice2))
                            else:
                                self.credit = timeDeltaToHHMM(timeHHMMToTimeDelta(self.credit) - timeHHMMToTimeDelta(choice2[1:]))
                        except:
                            if choice2!=None:
                                if "cancelled!" in choice2:
                                    continue
                                if "neutral" in choice2:
                                    self.credit = timeDeltaToHHMM(timeHHMMToTimeDelta(self.credit) + datetime.timedelta(hours=1))
                                    self.saveReport("В отчет добавлен 1 час кредита")
                                    continue
                                io2.log("Не удалось изменить, попробуйте еще")
                            continue
                        else:
                            self.saveReport("В отчет добавлено: %s ч. кредита" % choice2)
                            break
                        
            elif "Повторные" in result: # returns
                while choice2!=None:
                    choice2 = dialogs.dialogText(
                        neutralButton=True,
                        autoplus=True,
                        title=icon("returns") + " Повторные " + getTimerIcon(self.startTime),
                        message="Изменение на:"
                    )
                    console.process(choice2)
                    if choice2 == "":
                        break
                    else:
                        try:
                            self.returns += int(choice2)
                        except:
                            if choice2!=None:
                                if "cancelled!" in choice2:
                                    continue
                                if "neutral" in choice2:
                                    self.returns += 1
                                    self.saveReport("В отчет добавлено 1 повт. посещение")
                                    continue
                                io2.log("Не удалось изменить, попробуйте еще")
                            continue
                        else:
                            self.saveReport("В отчет добавлено: %d ПП" % int(choice2))
                            break
            
            elif "Изучения" in result: # studies
                while choice2!=None:
                    choice2 = dialogs.dialogText(
                        neutralButton=True,
                        autoplus=True,
                        title=icon("studies") + " Изучения " + getTimerIcon(self.startTime),
                        message="Изменение на:"
                    )
                    console.process(choice2)
                    if choice2 == "":
                        break
                    else:
                        try:
                            self.studies += int(choice2)
                        except:
                            if choice2!=None:
                                if "cancelled!" in choice2:
                                    continue
                                if "neutral" in choice2:
                                    self.studies += 1
                                    self.saveReport("В отчет добавлено 1 изучение")
                                    continue
                                io2.log("Не удалось изменить, попробуйте еще")
                            continue
                        else:
                            self.saveReport("В отчет добавлено: %d ИБ" % int(choice2))
                            break
              
            elif "Примечание" in result: # note
                choice2 = dialogs.dialogText(
                    title=icon("pin") + " Примечание " + getTimerIcon(self.startTime),
                    default=self.note
                )
                console.process(choice2)
                if choice2==None or "cancelled!" in choice2:
                    continue
                else:
                    self.note = choice2.strip()
                    self.saveReport()

            elif "Журнал" in result: # show logReport
                if io2.osName=="android":
                    if os.path.exists(io2.AndroidUserPath + "logreport.txt"):
                        with open(io2.AndroidUserPath + "logreport.txt", encoding="utf-8") as file:
                            text = file.read()
                        choice=dialogs.dialogInfo(
                            title=icon("logreport") + " Журнал отчета %s" % getTimerIcon(settings[2][6]),
                            message=text,
                            neutralButton=True,
                            neutral="Очистить"
                        )
                        console.process(choice)
                        if choice=="neutral" and dialogs.dialogConfirm(message="Полностью очистить журнал отчета?")==True:
                            os.remove(io2.AndroidUserPath + "logreport.txt")
                    else:
                        io2.log("Файл журнала не найден! Попробуйте внести хотя бы одно изменение в отчет.")
                else:
                    if os.path.exists("logreport.txt"):
                        with open("logreport.txt", encoding="utf-8") as file:
                            text = file.read()
                        choice=dialogs.dialogHelp(
                            title=icon("logreport") + " Журнал отчета %s" % getTimerIcon(settings[2][6]),
                            message=text,
                            neutral="Очистить"
                        )
                        console.process(choice)
                        if choice=="" and dialogs.dialogConfirm(message="Полностью очистить журнал отчета?")==True:
                            os.remove("logreport.txt")
                    else:
                        io2.log("Файл журнала не найден! Внесите хотя бы одно изменение в отчет.")
        
        if exit==1:            
            return True

def timeDeltaToHHMM(delta):
    delta=str(delta)
    if len(delta)==7:                           # "1:00:00"
        result = "0%s:%s" % (delta[0:1], delta[2:4])

    elif len(delta)==8:                         # "10:00:00"
        result = "%s:%s" % (delta[0:2], delta[3:5])

    elif len(delta)==6:                         # "100:00"
        result = "%s:%s" % (delta[0:3], delta[4:6])

    elif "day" in delta and len(delta)==14:     # "1 day, 6:00:00"
        days=int(delta[0])*24
        hours = days + int(delta[7:8])
        minutes = int(delta[9:11])
        result = str("%02d:%02d" % (hours, minutes))

    elif "day" in delta and len(delta)==15:     # "1 day, 12:00:00"
        days=int(delta[0])*24
        hours = days + int(delta[7:9])
        minutes = int(delta[10:12])
        result = str("%02d:%02d" % (hours, minutes))

    elif "days" in delta and len(delta)==15:    # "2 days, 2:00:00"
        days=int(delta[0])*24
        hours = days + int(delta[8:9])
        minutes = int(delta[10:12])
        result = str("%02d:%02d" % (hours, minutes))

    elif "days" in delta and len(delta)==16:    # "2 days, 12:00:00"
        days=int(delta[0])*24
        hours = days + int(delta[8:10])
        minutes = int(delta[12:13])
        result = str("%02d:%02d" % (hours, minutes))

    else:
        result = delta#"999:99"#"00:00"
    return result

def timeHHMMToTimeDelta(time="00:00"):
    time=time.strip()
    if ":" not in time:  # "1"
        hours = int(time)
        minutes=0
        print(time)
    elif len(time)==5:   # "00:00"
        hours = int(time[0:2])
        minutes = int(time[3:5])
    elif len(time)==6:  # "100:00"
        hours = int(time[0:3])
        minutes = int(time[4:6])
    else:
        hours=0
        minutes=0
    return datetime.timedelta(hours=hours, minutes=minutes)

def zeroTimeDelta():
    return datetime.timedelta(hours=0, minutes=0)

def updateTimer(startTime):
    """ Returns current endTime to anyone """
    endTime = time.strftime("%H:%M", time.localtime())
    hoursStart = int(startTime[0:2])
    minutesStart = int(startTime[3:5])
    hoursEnd = int(endTime[0:2])
    minutesEnd = int(endTime[3:5])
    return datetime.timedelta(hours=hoursEnd, minutes=minutesEnd) - datetime.timedelta(hours=hoursStart, minutes=minutesStart)

def getTimerIcon(startTime):
    """ Returns timer and ringer icon, if active, and add silent icon on Android """

    if timeHHMMToTimeDelta(startTime) > zeroTimeDelta():
        output = " " + icon("timer")
        if io2.osName=="android":
            if settings[0][0]==1:
                output += " " + icon("mute")
                vibrate(True)
            else:
                vibrate(False)
            
        return output
    else:
        return ""
    
def vibrate(key):
    """ Toggle ringer on/off """
    
    if io2.osName != "android":
        return
    if settings[0][0]==1:
        from androidhelper import Android
        if key==True:
            Android().setRingerVolume(0)
            return
        elif key==False:
            Android().setRingerVolume(100)
            return
    
def checkNewMonth():
    """ Checks if month is over """
    
    savedMonth = settings[3]
    currentMonth = time.strftime("%b", time.localtime())
    if savedMonth==currentMonth:
        return False   # same month
    else:
        return True                           # new month began

def monthName(monthCode=None, monthNum=None):
    """ Returns names of current and last months in lower and upper cases """
    
    if monthCode!=None:     month=monthCode
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

def hourGap(hours, credit):
    """Вычисление запаса или отставания от месячной нормы"""
    h = timeDeltaToHHMM( timeHHMMToTimeDelta(hours) + timeHHMMToTimeDelta(credit) )
    combinedHours = int( h[0 : h.index(":")] ) # обычные часы и кредит
    d = int(time.strftime("%d", time.localtime())) # текущий день месяца
    norm = settings[0][3] # месячная норма
    result = combinedHours - d * norm / days()
    return result

def timeHHMMToFloat(time):
    lis = [time]
    start_dt = datetime.datetime.strptime("00:00", '%H:%M')
    result=[float('{:0.2f}'.format((datetime.datetime.strptime(time, '%H:%M') - start_dt).seconds / 3600)) for time in lis][0]
    return result

def timeFloatToHHMM(hours):
    return str(datetime.timedelta(hours=hours)).rsplit(':', 1)[0]

def days():
    """ Returns number of days in current month """
    
    if time.strftime("%b", time.localtime())=="Jan":   return 31
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
    
def report(choice="", stop=False):
    """ Callable program """
    exit=0
    
    report = Report() # create current report
    
    # Check if new month began
    
    if checkNewMonth()==True:
        rolloverHours, rolloverCredit = report.saveLastMonth()
        report.clear(rolloverHours, rolloverCredit)
        settings[3] = time.strftime("%b", time.localtime())
        settings[2][11]=1 # turn on report reminder
        self.saveReport("Начался новый месяц, отчет за %s заархивирован" % monthName()[3])
        stop=False
    
    if stop==True:
        if exit==1:
            return True
        else:
            return False
    
    if len(choice) > 1:
        report.modify(choice[1:]) # if report called with string input, it is instantly passed to modify(), else just displays
    else:
        if report.display()==True:
            exit=1

    if exit==1:
        return True