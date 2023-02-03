#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import utils
import app

class Report(object):

    def __init__(self):
        self.hours = utils.settings[2][0]
        self.credit = utils.settings[2][1]
        self.placements = utils.settings[2][2]
        self.videos = utils.settings[2][3]
        self.returns = utils.settings[2][4]
        self.studies = utils.settings[2][5]
        self.startTime = utils.settings[2][6]
        self.endTime = utils.settings[2][7]
        self.reportTime = utils.settings[2][8]
        self.difTime = utils.settings[2][9]
        self.note = utils.settings[2][10]
        self.reminder = utils.settings[2][11]
        self.lastMonth = utils.settings[2][12]

    def saveReport(self, message="", mute=False, save=True, forceNotify=False):
        """ Выгрузка данных из класса в настройки, сохранение и оповещение """
        utils.settings[2] = [
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
            utils.log(message, forceNotify=forceNotify)
            date = time.strftime("%d.%m", time.localtime()) + "." + str(int(time.strftime("%Y", time.localtime())) - 2000)
            time2 = time.strftime("%H:%M:%S", time.localtime())
            utils.resources[2].insert(0, f"\n{date} {time2}: {message}")
        if save==True:
            utils.save(backup=True, silent=True)

    def checkNewMonth(self, forceDebug=False):
        savedMonth = utils.settings[3]
        currentMonth = time.strftime("%b", time.localtime())
        if savedMonth != currentMonth or forceDebug == True:
            if app.RM.displayed.form == "rep":
                app.RM.mainList.clear_widgets()
            saveTimer = self.startTime
            #utils.log(app.RM.msg[221])
            app.RM.popup(app.RM.msg[221], options=[app.RM.button["yes"], app.RM.button["no"]])
            app.RM.popupForm = "submitReport"
            rolloverHours, rolloverCredit = self.saveLastMonth()
            self.clear(rolloverHours, rolloverCredit)
            utils.settings[3] = time.strftime("%b", time.localtime())
            self.reminder = 1
            self.saveReport(mute=True)

            #if app.RM.displayed.form == "rep":
            #    app.RM.repPressed(jumpToPrevMonth=True)

            if saveTimer != 0: # если при окончании месяца работает таймер, принудительно выключаем его
                self.startTime = saveTimer
                def __stopTimer(*args):
                    app.RM.timerPressed()
                from kivy.clock import Clock
                Clock.schedule_once(__stopTimer, 0.1)

    def toggleTimer(self):
        result = 0
        if self.startTime == 0:
            self.modify("(")
        else:
            if utils.settings[0][2] == 0:  # если выключен кредит
                result = 1
            else:  # если в настройках включен кредит, спрашиваем:
                result = 2
        return result

    def getCurrentHours(self):
        """ Выдает общее количество часов в этом месяце с кредитом (str) [0],
            запас/отставание (float) [1] и
            строку с текстом показа запаса/отставания (str) [2] """
        value = self.hours + self.credit
        gap = value - float(time.strftime("%d", time.localtime())) * \
        utils.settings[0][3] / utils.days()
        if utils.settings[0][3] == 0:
            gap_str = ""
        elif gap >= 0:
            gap_str = " (+%s)" % utils.timeFloatToHHMM(gap)
        else:
            gap_str = " (-%s)" % utils.timeFloatToHHMM(-gap)
        return utils.timeFloatToHHMM(value), gap, gap_str

    def saveLastMonth(self):
        """ Save last month report to file """
        rolloverHours = rolloverCredit = 0.0

        # Calculate rollovers
        if utils.settings[0][15]==1: # rollover seconds to next month if activated
            rolloverHours = round(self.hours,2) - int(round(self.hours,2))
            self.hours = int(round(self.hours,2)-rolloverHours)
            rolloverCredit = round(self.credit,2) - int(round(self.credit,2))
            self.credit = int(round(self.credit,2)-rolloverCredit)

        if utils.settings[0][2]==1:
            credit = f"{app.RM.msg[222]} {utils.timeFloatToHHMM(self.credit)[0 : utils.timeFloatToHHMM(self.credit).index(':')]}\n" # whether save credit to file
        else:
            credit = ""

        # Save file of last month
        self.lastMonth =    f"[u]{app.RM.msg[223]}[/u]\n\n" % utils.monthName()[3] +\
                            f"{app.RM.msg[102]}: [b]%d[/b]\n" % self.placements +\
                            f"{app.RM.msg[103]}: [b]%d[/b]\n" % self.videos +\
                            f"{app.RM.msg[104]}: [b]%s[/b]\n" % utils.timeFloatToHHMM(self.hours)[0 : utils.timeFloatToHHMM(self.hours).index(":")] +\
                            f"{app.RM.msg[108]}: [b]%d[/b]\n" % self.returns + \
                            f"{app.RM.msg[109]}: [b]%d[/b]\n" % self.studies
        if credit != "":
            self.lastMonth += f"[i]{app.RM.msg[224]}: %s[/i]" % credit
        
        # Clear service year in October        
        if int(time.strftime("%m", time.localtime())) == 10: 
            utils.settings[4] = [None, None, None, None, None, None, None, None, None, None, None, None]
        
        # Save last month hour+credit into service year
        utils.settings[4][utils.monthName()[7]-1] = self.hours + self.credit
        
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
                
    def modify(self, input=" "):
        """ Modifying report on external commands """

        if input == "(":  # start timer
            self.startTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
            time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
            if utils.settings[0][0] == 1:
                forceNotify = True
            else:
                forceNotify = False
            self.saveReport(app.RM.msg[225], forceNotify=forceNotify)

        elif input == ")":  # остановка таймера
            if self.startTime > 0:
                self.endTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
                    time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
                self.reportTime = (self.endTime - self.startTime) / 3600
                if self.reportTime < 0:
                    self.reportTime += 24  # if timer worked after 0:00
                self.hours += self.reportTime
                self.startTime = 0
                self.saveReport(app.RM.msg[226] % utils.timeFloatToHHMM(self.reportTime), save=False)
                self.reportTime = 0.0
                self.saveReport(mute=True, save=True) # после выключения секундомера делаем резервную копию принудительно

        elif input == "$":  # остановка таймера с кредитом
            if self.startTime > 0:
                self.endTime = int(time.strftime("%H", time.localtime())) * 3600 + int(
                    time.strftime("%M", time.localtime())) * 60 + int(time.strftime("%S", time.localtime()))
                self.reportTime = (self.endTime - self.startTime) / 3600
                if self.reportTime < 0:
                    self.reportTime += 24  # if timer worked after 0:00
                self.credit += self.reportTime
                self.startTime = 0
                self.saveReport(app.RM.msg[227] % utils.timeFloatToHHMM(self.reportTime), save=False)
                self.reportTime = 0.0
                self.saveReport(mute=True, save=True) # после выключения секундомера делаем резервную копию принудительно

        elif input[0] == "{": # отчет со счетчиков в посещениях
            if len(input) > 1:
                message = f"{app.RM.msg[228]}: "
                pub = input.count('б')
                vid = input.count('в')
                ret = input.count('п')
                if pub > 0:
                    message += f"{pub} {app.RM.msg[229]}"
                    if vid > 0 or ret > 0:
                        message += ", "
                if vid > 0:
                    message += f"{vid} {app.RM.msg[172]}"
                    if ret > 0:
                        message += ", "
                if ret > 0:
                    message += f"1 {app.RM.msg[230]}"
                self.saveReport(message=message)

        elif "р" in input or "ж" in input or "ч" in input or "б" in input or "в" in input or "п" in input or "и" in input or "к" in input:
            if input[0]=="ч":
                if input=="ч":
                    self.hours += 1
                    self.saveReport(app.RM.msg[231])
                else:
                    self.hours = utils.timeHHMMToFloat(app.RM.time3)
                    self.saveReport(app.RM.msg[232] % input[1:])

            elif input[0]=="р":
                if input == "р":
                    self.credit += 1
                    self.saveReport(app.RM.msg[233])
                else:
                    self.credit = utils.timeHHMMToFloat(app.RM.time3)
                    self.saveReport(app.RM.msg[234] % input[1:])
            elif input[0]=="б":
                if input=="б" or input=="б1":
                    self.placements += 1
                    self.saveReport(app.RM.msg[235])
                else:
                    self.placements += int(input[1:])
                    self.saveReport(app.RM.msg[236] % int(input[1:]))
            elif input[0]=="в":
                if input == "в" or input=="в1":
                    self.videos += 1
                    self.saveReport(app.RM.msg[237])
                else:
                    self.videos += int(input[1:])
                    self.saveReport(app.RM.msg[238] % int(input[1:]))
            elif input[0]=="п":
                if input == "п" or input=="п1":
                    self.returns += 1
                    self.saveReport(app.RM.msg[239])
                else:
                    self.returns += int(input[1:])
                    self.saveReport(app.RM.msg[240] % int(input[1:]))
            elif input=="и":
                self.studies += 1
                self.saveReport(app.RM.msg[241])

        self.checkNewMonth()

    def getCurrentMonthReport(self):
        """ Выдает отчет текущего месяца"""
        if utils.settings[0][2]==1:
            credit = f"{app.RM.msg[222]} {utils.timeFloatToHHMM(self.credit)[0 : utils.timeFloatToHHMM(self.credit).index(':')]}\n" # whether save credit to file
        else:
            credit = ""
        result =         f"[u]{app.RM.msg[223]}[/u]\n\n" % utils.monthName()[1] + \
                         f"{app.RM.msg[102]}: [b]%d[/b]\n" % self.placements + \
                         f"{app.RM.msg[103]}: [b]%d[/b]\n" % self.videos + \
                         f"{app.RM.msg[104]}: [b]%s[/b]\n" % \
                         utils.timeFloatToHHMM(self.hours)[0: utils.timeFloatToHHMM(self.hours).index(":")] + \
                         f"{app.RM.msg[108]}: [b]%d[/b]\n" % self.returns + \
                         f"{app.RM.msg[109]}: [b]%d[/b]\n" % self.studies
        if credit != "":
            result += f"[i]{app.RM.msg[224]}: %s[/i]" % credit
        result = self.filterOutFormatting(result)
        return result

    def getLastMonthReport(self):
        """ Выдает отчет прошлого месяца """
        self.lastMonthNoFormatting = self.filterOutFormatting(self.lastMonth)
        return self.lastMonth, self.lastMonthNoFormatting, utils.monthName()[2], utils.monthName()[3]
    
    def filterOutFormatting(self, string):
        """ Удаляет из отчета теги форматирования """
        string = string.replace('[u]', '')
        string = string.replace('[/u]', '')
        string = string.replace('[b]', '')
        string = string.replace('[/b]', '')
        string = string.replace('[i]', '')
        string = string.replace('[/i]', '')
        return string
