#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import io2
import dialogs
import set
import datetime
from icons import icon
import homepage

class Report():

    def __init__(self):
        
        self.hours = io2.settings[2][0]
        self.credit = io2.settings[2][1]
        self.placements = io2.settings[2][2]
        self.videos = io2.settings[2][3]
        self.returns = io2.settings[2][4]
        self.studies = io2.settings[2][5]
        self.startTime = io2.settings[2][6]
        self.endTime = io2.settings[2][7]
        self.reportTime = io2.settings[2][8]
        self.difTime = io2.settings[2][9]
        self.note = io2.settings[2][10]
        self.reminder = io2.settings[2][11]
        self.lastMonth = io2.settings[2][12]

    def saveReport(self, message="", mute=False, save=True, backup=False):
        """ Выгрузка данных из класса в настройки, сохранение и оповещение """
        io2.settings[2] = [
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
            self.reminder,
            self.lastMonth
        ]
        if mute == False:
            io2.log(message)
            date = time.strftime("%d.%m", time.localtime()) + "." + str(int(time.strftime("%Y", time.localtime())) - 2000)
            time2 = time.strftime("%H:%M:%S", time.localtime())
            io2.resources[2].insert(1, "\n%s %s: %s" % (date, time2, message))
        if save==True or backup==True:
            io2.save(forced=True, silent=True) # после выключения секундомера делаем резервную копию принудительно
        elif save==True:
            io2.save()

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
        if io2.settings[0][15]==1: # rollover seconds to next month if activated
            rolloverHours = round(self.hours,2) - int(round(self.hours,2))
            self.hours = int(round(self.hours,2)-rolloverHours)
            rolloverCredit = round(self.credit,2) - int(round(self.credit,2))
            self.credit = int(round(self.credit,2)-rolloverCredit)

        if io2.settings[0][2]==1:
            credit = "Кредит: %s\n" % timeFloatToHHMM(self.credit)[0 : timeFloatToHHMM(self.credit).index(":")] # whether save credit to file
        else:
            credit = ""

        # Save file of last month
        self.lastMonth = ("Отчет за %s:\nПубликации: %d\nВидео: %d\nЧасы: %s\n%sПовторные посещения: %d\nИзучения Библии: %d" % \
                       (monthName()[3],
                        self.placements,
                        self.videos,
                        timeFloatToHHMM(self.hours)[0 : timeFloatToHHMM(self.hours).index(":")],
                        credit,
                        self.returns,
                        self.studies)
                 )
        if self.note!="":
            self.lastMonth += "\nПримечание: " + self.note

        self.saveReport()
        
        # Clear service year in October        
        if int(time.strftime("%m", time.localtime())) == 10: 
            io2.settings[4] = [None, None, None, None, None, None, None, None, None, None, None, None]
        
        # Save last month hour+credit into service year
        io2.settings[4][monthName()[7]-1] = self.hours + self.credit

        io2.save()
        
        return rolloverHours, rolloverCredit # return rollovers for amending new month report
        
    def clear(self, rolloverHours, rolloverCredit):
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
        #self.lastMonth = ""
                
    def modify(self, input):
        """ Modifying report on external commands """

        #print(input)

        if input[0] == "(":  # start timer
            self.startTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
            time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
            vibrate(True)
            self.saveReport("Таймер запущен")

        elif input[0] == ")":  # остановка таймера
            if self.startTime > 0:
                self.endTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
                    time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
                self.reportTime = (self.endTime - self.startTime) / 3600
                if self.reportTime < 0: self.reportTime += 24  # if timer worked after 0:00
                self.hours += self.reportTime
                self.startTime = 0
                self.saveReport("Таймер остановлен, в отчет добавлено: %s ч." % timeFloatToHHMM(self.reportTime), save=False)
                self.reportTime = 0.0
                vibrate(False)
                self.saveReport(mute=True, backup=True)

        elif input[0] == "$":  # остановка таймера с кредитом
            if self.startTime > 0:
                self.endTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
                    time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
                self.reportTime = (self.endTime - self.startTime) / 3600
                if self.reportTime < 0: self.reportTime += 24  # if timer worked after 0:00
                self.credit += self.reportTime
                self.startTime = 0
                self.saveReport("Таймер остановлен, в отчет добавлено: %s ч. кредита" % timeFloatToHHMM(self.reportTime), save=False)
                self.reportTime = 0.0
                vibrate(False)
                self.saveReport(mute=True, backup=True)

        elif "р" in input or "ж" in input or "ч" in input or "б" in input or "в" in input or "п" in input or "и" in input or "к" in input:
            message="В отчет добавлено: "
            for i in range(len(input)):
                if input[i]=="=" and input[i+1]=="ч":
                    self.hours += 1
                    message += "\nчас"
                if input[i]=="=" and input[i+1]=="р":
                    self.credit += 1
                    message += "\nчас кредита"
                if input[i]=="=" and input[i+1]=="б":
                    self.placements += 1
                    message += "\nпубликация"
                if input[i]=="=" and input[i+1]=="ж":
                    self.placements += 1
                    message += "\nпубликация"
                if input[i]=="=" and input[i+1]=="к":
                    self.placements += 1
                    message += "\nпубликация"
                if input[i]=="=" and input[i+1]=="в":
                    self.videos += 1
                    message += "\nвидео"
                if input[i]=="=" and input[i+1]=="п":
                    self.returns += 1
                    message += "\nповторное"
                if input[i]=="=" and input[i+1]=="и":
                    self.studies += 1
                    message += "\nизучение"
            if message != "В отчет добавлено:":
                self.saveReport(message)
                
    def display(self):
        """ Displaying report """
        
        while 1:
            # Главный цикл показа отчета
            
            title = icon("report") + " Отчет за %s %s " % (monthName()[1], getTimerIcon(self.startTime))

            gap = float((self.hours+self.credit) - int(time.strftime("%d", time.localtime()))*io2.settings[0][3]/days())
            
            if gap >= 0:
                gap_str = icon("extra2") + " Запас: %s" % timeFloatToHHMM(gap) # happy emoticon
            else:
                gap_str = icon("slippage") + " Отставание: %s" % timeFloatToHHMM(-gap) # crying emoticon

            if self.startTime > 0 and self.reportTime == 0:
                self.endTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
                    time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
                self.difTime = (self.endTime - self.startTime) / 3600

            if io2.settings[0][2] == 1:
                if io2.Mode=="sl4a":
                    hoursLine = icon("timer") + " Часы: %s\n     (с кредитом: %s)" % (
                        timeFloatToHHMM(self.hours), timeFloatToHHMM(self.hours + self.credit)
                    )
                else:
                    hoursLine = icon("timer") + " Часы: %s (с кредитом: %s)" % (
                        timeFloatToHHMM(self.hours), timeFloatToHHMM(self.hours + self.credit)
                    )
            else:
                hoursLine = icon("timer") + " Часы: %s" % timeFloatToHHMM(self.hours)

            message = "Выберите действие:"
            options = [
                icon("placements") + " Публикации: %d" % self.placements,
                icon("video") + " Видео: %d" % self.videos,
                hoursLine
            ]
                
            if io2.settings[0][3]!=0:
                options.append(gap_str)
            if io2.settings[0][2]==1:
                options.append(icon("credit") + " Кредит: %s" % timeFloatToHHMM(self.credit))
            options.append(icon("returns")  + " Повторные: %d" % self.returns)
            options.append(icon("studies")  + " Изучения: %d" % self.studies)
            options.append(icon("pin") + " Примечание: %s" % self.note)
            if io2.Mode == "desktop" and io2.settings[0][1] == 0:  # убираем иконки на ПК
                for i in range(len(options)):
                    options[i] = options[i][2:]

            choice = dialogs.dialogList(
                title=title,
                form = "display",
                message=message,
                options=options,
                positive = icon("restore") + " " + monthName()[2],
                neutral = icon("logreport") + " Журнал"
            )

            choice2=""
            if homepage.menuProcess(choice) == True:
                continue
            elif choice==None:
                break
            elif choice=="positive": # last month report
                self.showLastMonthReport()
                continue
            elif choice=="neutral": # show logReport
                    message=""
                    for i in range(1, len(io2.resources[2])):
                        message += io2.resources[2][i]
                    dialogs.dialogInfo(
                        largeText=True,
                        doublesize=True,
                        title=icon("logreport") + " Журнал отчета",
                        message=message[1:]
                    )
                    continue
            elif set.ifInt(choice)==True:
                result = options[choice]
            else:
                continue

            if "Публикации" in result: # placements
                message = "Изменение на:"
                while choice2!=None:
                    choice2 = dialogs.dialogText(
                        autoplus=True,
                        title=icon("placements") + " Публикации " + getTimerIcon(self.startTime),
                        message=message
                    )
                    if choice2 == None or choice2=="":
                        break
                    else:
                        try:
                            self.placements += int(choice2)
                        except:
                            if choice2!=None:
                                if "cancelled!" in choice2:
                                    continue
                                if "neutral" in choice2:
                                    self.placements += 1
                                    self.saveReport("В отчет добавлена 1 публикация")
                                    break
                                message="Требуется целое число, можно с минусом."
                            continue
                        else:
                            self.saveReport("В отчет добавлено: %d пуб." % int(choice2))
                            break

            elif "Видео" in result: # video
                message="Изменение на:"
                while choice2!=None:
                    choice2 = dialogs.dialogText(
                        autoplus=True,
                        title=icon("video") + " Видео " + getTimerIcon(self.startTime),
                        message=message
                    )
                    if choice2 == None or choice2=="":
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
                                    break
                                message="Требуется целое число, можно с минусом."
                            continue
                        else:
                            self.saveReport("В отчет добавлено: %d вид." % int(choice2))
                            break

            elif "Часы" in result: # hours
                message="Изменение на:"
                while choice2!=None:
                    choice2 = dialogs.dialogText(
                        autoplus=True,
                        title=icon("timer") + " Часы " + getTimerIcon(self.startTime),
                        message=message
                    )
                    if choice2 == None or choice2=="":
                        break
                    else:
                        try:
                            input=timeHHMMToFloat(choice2)
                            if choice2[0]!="-":
                                if (self.hours + input) >= 500:
                                    message="Вы уверены, что так много часов?"
                                    continue
                                else:
                                    self.hours += input
                            else:
                                if (self.hours-input) >= 0: # проверка, чтобы отчет всегда был положительным
                                    self.hours -= input
                                else:
                                    message="Отчет не может быть отрицательным"
                                    continue
                        except:
                            if choice2!=None:
                                if "cancelled!" in choice2:
                                    continue
                                if "neutral" in choice2:
                                    self.hours += 1
                                    self.saveReport("В отчет добавлен 1 час")
                                    break
                                message="Требуется формат Ч или Ч:ММ, можно с минусом."
                            continue
                        else:
                            self.saveReport("В отчет добавлено: %s ч." % choice2)
                            break
                
            elif "Кредит" in result: # credit hours
                message="Изменение на:"
                while choice2!=None:
                    choice2 = dialogs.dialogText(
                        autoplus=True,
                        title=icon("credit") + " Кредит " + getTimerIcon(self.startTime),
                        message=message
                    )
                    if choice2 == None or choice2=="":
                        break
                    else:
                        try:
                            input = timeHHMMToFloat(choice2)
                            if choice2[0]!="-":
                                if (self.credit + input) >= 500:
                                    message="Вы уверены, что так много часов?"
                                    continue
                                else:
                                    self.credit += input
                            else:
                                if (self.credit - input) >= 0:  # проверка, чтобы отчет всегда был положительным
                                    self.credit -= input
                                else:
                                    message="Отчет не может быть отрицательным"
                                    continue
                        except:
                            if choice2!=None:
                                if "cancelled!" in choice2:
                                    continue
                                if "neutral" in choice2:
                                    self.credit += 1
                                    self.saveReport("В отчет добавлен 1 час кредита")
                                    break
                                message="Требуется формат Ч или Ч:ММ, можно с минусом."
                            continue
                        else:
                            self.saveReport("В отчет добавлено: %s ч. кредита" % choice2)
                            break

            elif "Повторные" in result: # returns
                message = "Изменение на:"
                while choice2!=None:
                    choice2 = dialogs.dialogText(
                        autoplus=True,
                        title=icon("returns") + " Повторные " + getTimerIcon(self.startTime),
                        message=message
                    )
                    if choice2 == None or choice2=="":
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
                                    break
                                message="Требуется целое число, можно с минусом."
                            continue
                        else:
                            self.saveReport("В отчет добавлено: %d ПП" % int(choice2))
                            break
            
            elif "Изучения" in result: # studies
                message = "Изменение на:"
                while choice2!=None:
                    choice2 = dialogs.dialogText(
                        autoplus=True,
                        title=icon("studies") + " Изучения " + getTimerIcon(self.startTime),
                        message=message
                    )
                    if choice2 == None or choice2=="":
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
                                    break
                                message="Требуется целое число, можно с минусом."
                            continue
                        else:
                            self.saveReport("В отчет добавлено: %d ИБ" % int(choice2))
                            break
              
            elif "Примечание" in result: # note
                choice2 = dialogs.dialogText(
                    title=icon("pin", simplified=False) + " Примечание " + getTimerIcon(self.startTime),
                    message="Примечание для себя и для отчета:",
                    default=self.note
                )
                if choice2 == None:
                    continue
                elif "cancelled!" in choice2:
                    continue
                else:
                    self.note = choice2.strip()
                    self.saveReport(self.note, mute=True)

            else:
                continue

        #if exit==1:
        #    return True

    def showLastMonthReport(self):
        """ Показываем отчет прошлого месяца """
        if io2.Mode == "sl4a":
            exportButton = " Экспорт"
        else:
            exportButton = " В буфер"
        answer = dialogs.dialogInfo(
            title=icon("report") + " Отчет прошлого месяца ",
            message=io2.settings[2][12],
            positive = icon("export") + exportButton,
            negative = "Назад",
            neutral=None
        )
        if answer == None:#123
            return
        elif "positive" or icon("export") in answer:  # export last month report
            if io2.Mode == "sl4a":
                time.sleep(0.5)
                try:
                    from androidhelper import Android
                    Android().sendEmail("Введите email", "Отчет за %s" % monthName()[3], self.lastMonth, attachmentUri=None)
                except IOError:
                    io2.log("Экспорт отчета не удался!")
                else:
                    io2.consoleReturn(pause=True)
            else:
                try:
                    from tkinter import Tk
                    r = Tk()
                    r.withdraw()
                    r.clipboard_clear()
                    r.clipboard_append(self.lastMonth)
                    r.destroy()
                except:
                    io2.log("Не удалось скопировать отчет в буфер обмена")
                else:
                    io2.log("Отчет скопирован в буфер обмена")

def updateTimer(startTime):
    """ Returns current endTime to anyone """

    endTime = int(time.strftime("%H", time.localtime())) * 3600 + int(time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
    return (endTime - startTime) / 3600

def getTimerIcon(startTime):
    """ Returns timer and ringer icon, if active, and add silent icon on Android """

    if startTime > 0:
        if io2.Mode != "desktop" and io2.settings[0][1] == 0:
            output = " " + icon("timer")
        else:
            output = ""
        if io2.Mode == "sl4a":
            if io2.settings[0][0] == 1:
        #        output += " " + icon("mute")
                vibrate(True)
            else:
                vibrate(False)
        return output
    else:
        return ""
    
def vibrate(key):
    """ Toggle ringer on/off """
    
    if io2.Mode != "sl4a":
        return
    if io2.settings[0][0]==1:
        from androidhelper import Android
        if key==True:
            Android().setRingerVolume(0)
            return
        elif key==False:
            Android().setRingerVolume(100)
            return

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

def timeHHMMToFloat(mytime):
    if mytime==None:
        return None

    if mytime[0]=="-":
        mytime = mytime[1:]

    if ":" not in mytime:
        result = abs(int(mytime.strip()))
    else:
        lis = [mytime]
        start_dt = datetime.datetime.strptime("00:00", '%H:%M')
        result = [float('{:0.2f}'.format((datetime.datetime.strptime(mytime, '%H:%M') - start_dt).seconds / 3600)) for mytime in lis][0]

    return result

def timeFloatToHHMM(hours):
    delta = str(datetime.timedelta(hours=hours)).strip()

    if "." in delta:
        delta = delta[ 0 : delta.index(".") ]

    if len(delta) == 7:  # "1:00:00"
        result = "%s:%s" % (delta[0:1], delta[2:4])

    elif len(delta) == 8:  # "10:00:00"
        result = "%s:%s" % (delta[0:2], delta[3:5])

    elif len(delta) == 6:  # "100:00"
        result = "%s:%s" % (delta[0:3], delta[4:6])

    elif "day" in delta and len(delta) == 14:  # "1 day, 6:00:00"
        days = int(delta[0]) * 24
        hours = days + int(delta[7:8])
        minutes = int(delta[9:11])
        result = str("%d:%02d" % (hours, minutes))

    elif "day" in delta and len(delta) == 15:  # "1 day, 12:00:00"
        days = int(delta[0]) * 24
        hours = days + int(delta[7:9])
        minutes = int(delta[10:12])
        result = str("%d:%02d" % (hours, minutes))

    elif "days" in delta and len(delta) == 15:  # "2 days, 2:00:00"
        days = int(delta[0]) * 24
        hours = days + int(delta[8:9])
        minutes = int(delta[10:12])
        result = str("%d:%02d" % (hours, minutes))

    elif "days" in delta and len(delta) == 16\
            and set.ifInt(delta[0])==True\
            and set.ifInt(delta[1])==False:     # "2 days, 12:00:00"
        days = int(delta[0]) * 24
        hours = days + int(delta[8:10])
        minutes = int(delta[12:13])
        result = str("%d:%02d" % (hours, minutes))
        
    elif "days" in delta and len(delta) == 16 \
            and set.ifInt(delta[0]) == True \
            and set.ifInt(delta[1]) == True:    # "12 days, 2:00:00"
        days = int(delta[0:2]) * 24
        hours = days + int(delta[9:10])
        minutes = int(delta[12:13])
        result = str("%d:%02d" % (hours, minutes))

    elif "days" in delta and len(delta) == 17:  # "12 days, 12:00:00"
        days = int(delta[0:2]) * 24
        hours = days + int(delta[9:11])
        minutes = int(delta[13:14])
        result = str("%d:%02d" % (hours, minutes))

    else:
        result=delta

    return result

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
    
def report(choice="", stop=False, newMonthDetected=False, disableNotification=False, showLastMonth=False):
    """ Callable program """
    exit=0
    
    report = Report() # create current report

    # Check if new month began
    
    if newMonthDetected==True:
        rolloverHours, rolloverCredit = report.saveLastMonth()
        report.clear(rolloverHours, rolloverCredit)
        report.reminder=1 # включить напоминание сдать отчет
        report.saveReport(mute=True)
        io2.log("Начался новый месяц, не забудьте сдать отчет!")
        stop=True

    if disableNotification==True:
        report.reminder = 0
        report.saveReport(mute=True)
        stop=True

    if showLastMonth==True:
        report.showLastMonthReport()
    
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

def toggleTimer():
    if io2.settings[2][6] == 0:
        report(choice="=(")
    else:
        if io2.settings[0][2] == False:
            report(choice="=)")  # запись обычного времени
        else:  # если в настройках включен кредит, спрашиваем:
            options = [icon("timer") + " Служение", icon("credit") + " Кредит"]
            if io2.Mode == "desktop" and io2.settings[0][1] == 0:  # убираем иконки на ПК
                for i in range(len(options)):
                    options[i] = options[i][2:]
            choice2 = dialogs.dialogList(
                title="Что записать?",
                options=options,
                selected=1,
                negative="Отмена"
            )
            if choice2 == 0:
                report(choice="=)")
            elif choice2 == 1:
                report("=$")

def getCurrentHours():
    """ Выдает общее количество часов в этом месяце с кредитом [0] и запас/отставание [1] """
    if io2.settings[0][2] == True:  # включен кредит часов
        credit = io2.settings[2][1]
    else:
        credit = 0
    total = io2.settings[2][0] + credit
    gap = float(
        total - int(time.strftime("%d", time.localtime())) * io2.settings[0][3] / days()
    )
    return timeFloatToHHMM(total), gap