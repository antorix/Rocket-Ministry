#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import time
import app

def getCurTime():
    return int(time.strftime("%H", time.localtime())) * 3600 \
              + int(time.strftime("%M", time.localtime())) * 60 \
              + int(time.strftime("%S", time.localtime()))

def checkDate(date):
    """Проверяет, что дата в формате ГГГГ-ММ-ДД"""
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except:
        return False
    else:
        return True

def shortenDate(longDate):
    """ Convert date from format "2016-07-22" into "22.07" """

    # 2016-07-22
    # 0123456789
    try:
        date = list(longDate)
        date[0] = longDate[8]
        date[1] = longDate[9]
        date[2] = "."
        date[3] = longDate[5]
        date[4] = longDate[6]
    except:
        return None
    else:
        return "".join(date[0] + date[1] + date[2] + date[3] + date[4])

def days():
    """ Returns number of days in current month """
    if time.strftime("%b", time.localtime()) == "Jan":
        return 31
    elif time.strftime("%b", time.localtime()) == "Feb":
        return 30
    elif time.strftime("%b", time.localtime()) == "Mar":
        return 31
    elif time.strftime("%b", time.localtime()) == "Apr":
        return 30
    elif time.strftime("%b", time.localtime()) == "May":
        return 31
    elif time.strftime("%b", time.localtime()) == "Jun":
        return 30
    elif time.strftime("%b", time.localtime()) == "Jul":
        return 31
    elif time.strftime("%b", time.localtime()) == "Aug":
        return 31
    elif time.strftime("%b", time.localtime()) == "Sep":
        return 30
    elif time.strftime("%b", time.localtime()) == "Oct":
        return 31
    elif time.strftime("%b", time.localtime()) == "Nov":
        return 30
    elif time.strftime("%b", time.localtime()) == "Dec":
        return 31
    else:
        return 30.5

def monthName(monthCode=None, monthNum=None):
    """ Returns names of current and last months in lower and upper cases """

    if monthCode != None:
        month = monthCode
    elif monthNum != None:
        if monthNum == 1:
            month = "Jan"
        elif monthNum == 2:
            month = "Feb"
        elif monthNum == 3:
            month = "Mar"
        elif monthNum == 4:
            month = "Apr"
        elif monthNum == 5:
            month = "May"
        elif monthNum == 6:
            month = "Jun"
        elif monthNum == 7:
            month = "Jul"
        elif monthNum == 8:
            month = "Aug"
        elif monthNum == 9:
            month = "Sep"
        elif monthNum == 10:
            month = "Oct"
        elif monthNum == 11:
            month = "Nov"
        elif monthNum == 12:
            month = "Dec"
    else:
        month = time.strftime("%b", time.localtime())

    if month == "Jan":
        curMonthUp = app.RM.msg[259]
        curMonthLow = app.RM.msg[260]
        lastMonthUp = app.RM.msg[261]
        lastMonthLow = app.RM.msg[262]
        lastMonthEn = "Dec"
        curMonthRuShort = app.RM.msg[283]
        monthNum = 1
        lastTheoMonthNum = 4
        curTheoMonthNum = 5
    elif month == "Feb":
        curMonthUp = app.RM.msg[263]
        curMonthLow = app.RM.msg[264]
        lastMonthUp = app.RM.msg[259]
        lastMonthLow = app.RM.msg[260]
        lastMonthEn = "Jan"
        curMonthRuShort = app.RM.msg[284]
        monthNum = 2
        lastTheoMonthNum = 5
        curTheoMonthNum = 6
    elif month == "Mar":
        curMonthUp = app.RM.msg[265]
        curMonthLow = app.RM.msg[266]
        lastMonthUp = app.RM.msg[263]
        lastMonthLow = app.RM.msg[264]
        lastMonthEn = "Feb"
        curMonthRuShort = app.RM.msg[285]
        monthNum = 3
        lastTheoMonthNum = 6
        curTheoMonthNum = 7
    elif month == "Apr":
        curMonthUp = app.RM.msg[267]
        curMonthLow = app.RM.msg[268]
        lastMonthUp = app.RM.msg[265]
        lastMonthLow = app.RM.msg[266]
        lastMonthEn = "Mar"
        curMonthRuShort = app.RM.msg[286]
        monthNum = 4
        lastTheoMonthNum = 7
        curTheoMonthNum = 8
    elif month == "May":
        curMonthUp = app.RM.msg[269]
        curMonthLow = app.RM.msg[270]
        lastMonthUp = app.RM.msg[267]
        lastMonthLow = app.RM.msg[268]
        lastMonthEn = "Apr"
        curMonthRuShort = app.RM.msg[287]
        monthNum = 5
        lastTheoMonthNum = 8
        curTheoMonthNum = 9
    elif month == "Jun":
        curMonthUp = app.RM.msg[271]
        curMonthLow = app.RM.msg[272]
        lastMonthUp = app.RM.msg[269]
        lastMonthLow = app.RM.msg[270]
        lastMonthEn = "May"
        curMonthRuShort = app.RM.msg[288]
        monthNum = 6
        lastTheoMonthNum = 9
        curTheoMonthNum = 10
    elif month == "Jul":
        curMonthUp = app.RM.msg[273]
        curMonthLow = app.RM.msg[274]
        lastMonthUp = app.RM.msg[271]
        lastMonthLow = app.RM.msg[272]
        lastMonthEn = "Jun"
        curMonthRuShort = app.RM.msg[289]
        monthNum = 7
        lastTheoMonthNum = 10
        curTheoMonthNum = 11
    elif month == "Aug":
        curMonthUp = app.RM.msg[275]
        curMonthLow = app.RM.msg[276]
        lastMonthUp = app.RM.msg[273]
        lastMonthLow = app.RM.msg[274]
        lastMonthEn = "Jul"
        curMonthRuShort = app.RM.msg[290]
        monthNum = 8
        lastTheoMonthNum = 11
        curTheoMonthNum = 12
    elif month == "Sep":
        curMonthUp = app.RM.msg[277]
        curMonthLow = app.RM.msg[278]
        lastMonthUp = app.RM.msg[275]
        lastMonthLow = app.RM.msg[276]
        lastMonthEn = "Aug"
        curMonthRuShort = app.RM.msg[291]
        monthNum = 9
        lastTheoMonthNum = 12
        curTheoMonthNum = 1
    elif month == "Oct":
        curMonthUp = app.RM.msg[279]
        curMonthLow = app.RM.msg[280]
        lastMonthUp = app.RM.msg[277]
        lastMonthLow = app.RM.msg[278]
        lastMonthEn = "Sep"
        curMonthRuShort = app.RM.msg[292]
        monthNum = 10
        lastTheoMonthNum = 1
        curTheoMonthNum = 2
    elif month == "Nov":
        curMonthUp = app.RM.msg[281]
        curMonthLow = app.RM.msg[282]
        lastMonthUp = app.RM.msg[279]
        lastMonthLow = app.RM.msg[280]
        lastMonthEn = "Oct"
        curMonthRuShort = app.RM.msg[293]
        monthNum = 11
        lastTheoMonthNum = 2
        curTheoMonthNum = 3
    else: # Dec
        curMonthUp = app.RM.msg[261]
        curMonthLow = app.RM.msg[262]
        lastMonthUp = app.RM.msg[281]
        lastMonthLow = app.RM.msg[282]
        lastMonthEn = "Nov"
        curMonthRuShort = app.RM.msg[294]
        monthNum = 12
        lastTheoMonthNum = 3
        curTheoMonthNum = 4

    return curMonthUp, curMonthLow, lastMonthUp, lastMonthLow, lastMonthEn, curMonthRuShort, monthNum, lastTheoMonthNum, curTheoMonthNum

def timeHHMMToFloat(timeH):
    """ Преобразование HH:MM во float с коррекцией минутной погрешности """

    def __timeHHMMToFloatUnadjusted(mytime):
        """ Преобразование HH:MM во float без коррекции погрешности """
        if mytime == None:
            return None
        try:
            if ":" not in mytime:
                result1 = abs(int(mytime.strip()))
                result2 = 0
            else:
                hours = mytime[: mytime.index(":")]
                minutes = mytime[mytime.index(":") + 1:]
                result1 = abs(int(hours))
                lis = ["00:%s" % minutes]
                start_dt = datetime.datetime.strptime("00:00", '%H:%M')
                result2 = \
                [float('{:0.2f}'.format((datetime.datetime.strptime(mytime, '%H:%M') - start_dt).seconds / 3600)) for mytime
                 in lis][0]
        except:
            return None
        else:
            return result1 + result2

    timeHHMMToFloatUnadjusted_timeH = __timeHHMMToFloatUnadjusted(timeH)
    timeActualH2 = timeFloatToHHMM(timeHHMMToFloatUnadjusted_timeH)
    timeHHMMToFloatUnadjusted_timeActualH2 = __timeHHMMToFloatUnadjusted(timeActualH2)

    if timeHHMMToFloatUnadjusted_timeActualH2 == timeHHMMToFloatUnadjusted_timeH:
        corrected = timeHHMMToFloatUnadjusted_timeActualH2
    elif timeHHMMToFloatUnadjusted_timeActualH2 < timeHHMMToFloatUnadjusted_timeH:
        corrected = timeHHMMToFloatUnadjusted_timeH + 0.016
    else:
        corrected = timeHHMMToFloatUnadjusted_timeH - 0.016

    return corrected

def sumHHMM(list=None, mode="+"):
    """ Складывает два значения времени вида HH:MM, полученных в списке """
    if list == None: list = ['25:06', '9:31']
    mysum = datetime.timedelta()
    for i in list:
        (h, m) = i.split(':')
        d = datetime.timedelta(hours=int(h), minutes=int(m))
        if mode == "+":
            mysum += d
        else:
            mysum -= d
    string = timeFloatToHHMM(delta=str(mysum))
    return string

def timeFloatToHHMM(hours=None, delta=None):
    if delta == None:
        delta = str(datetime.timedelta(hours=hours)).strip()

    if "." in delta:
        delta = delta[0: delta.index(".")]

    if len(delta) == 7:  # "1:00:00"
        result = "%s:%s" % (delta[0:1], delta[2:4])

    elif len(delta) == 8:  # "10:00:00"
        result = "%s:%s" % (delta[0:2], delta[3:5])

    elif len(delta) == 6:  # "100:00"
        result = "%s:%s" % (delta[0:3], delta[4:6])

    elif "day" in delta and len(delta) == 14:       # "1 day, 6:00:00"
        days = int(delta[0]) * 24
        hours = days + int(delta[7:8])
        minutes = int(delta[9:11])
        result = str("%d:%02d" % (hours, minutes))

    elif "day" in delta and len(delta) == 15:       # "1 day, 12:00:00"
        days = int(delta[0]) * 24
        hours = days + int(delta[7:9])
        minutes = int(delta[10:12])
        result = str("%d:%02d" % (hours, minutes))

    elif "days" in delta and len(delta) == 15:      # "2 days, 2:00:00"
        days = int(delta[0]) * 24
        hours = days + int(delta[8:9])
        minutes = int(delta[10:12])
        result = str("%d:%02d" % (hours, minutes))

    elif "days" in delta and len(delta) == 16 \
            and delta[0].isnumeric() \
            and not delta[1].isnumeric():           # "2 days, 12:00:00"
        days = int(delta[0]) * 24
        hours = days + int(delta[8:10])
        minutes = int(delta[11:13])
        result = str("%d:%02d" % (hours, minutes))

    elif "days" in delta and len(delta) == 16 \
            and delta[0].isnumeric() \
            and delta[1].isnumeric():            # "12 days, 2:00:00"
        days = int(delta[0:2]) * 24
        hours = days + int(delta[9:10])
        minutes = int(delta[12:13])
        result = str("%d:%02d" % (hours, minutes))

    elif "days" in delta and len(delta) == 17:      # "12 days, 12:00:00"
        days = int(delta[0:2]) * 24
        hours = days + int(delta[9:11])
        minutes = int(delta[13:14])
        result = str("%d:%02d" % (hours, minutes))
    else:
        result = delta

    return result

def dprint(text):
    if app.Devmode == 1:
        print(text)

def filterOutFormatting(string):
    """ Удаляет из отчета теги форматирования """
    string = string.replace('[u]', '')
    string = string.replace('[/u]', '')
    string = string.replace('[b]', '')
    string = string.replace('[/b]', '')
    string = string.replace('[i]', '')
    string = string.replace('[/i]', '')
    return string