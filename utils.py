#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import time

def getCurTime():
    """ Получаем текущее время """
    return int(time.strftime("%H", time.localtime())) * 3600 \
              + int(time.strftime("%M", time.localtime())) * 60 \
              + int(time.strftime("%S", time.localtime()))

def checkDate(date):
    """ Проверяет, что дата в формате ГГГГ-ММ-ДД """
    try:    datetime.datetime.strptime(date, "%Y-%m-%d")
    except: return False
    else:   return True

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
    if time.strftime("%b", time.localtime()) == "Jan": return 31
    elif time.strftime("%b", time.localtime()) == "Feb": return 30
    elif time.strftime("%b", time.localtime()) == "Mar": return 31
    elif time.strftime("%b", time.localtime()) == "Apr": return 30
    elif time.strftime("%b", time.localtime()) == "May": return 31
    elif time.strftime("%b", time.localtime()) == "Jun": return 30
    elif time.strftime("%b", time.localtime()) == "Jul": return 31
    elif time.strftime("%b", time.localtime()) == "Aug": return 31
    elif time.strftime("%b", time.localtime()) == "Sep": return 30
    elif time.strftime("%b", time.localtime()) == "Oct": return 31
    elif time.strftime("%b", time.localtime()) == "Nov": return 30
    elif time.strftime("%b", time.localtime()) == "Dec": return 31
    else: return 30.5

def timeHHMMToFloat(timeH):
    """ Преобразование HH:MM во float с коррекцией минутной погрешности """
    def __timeHHMMToFloatUnadjusted(mytime):
        """ Преобразование HH:MM во float без коррекции погрешности """
        if mytime == None: return None
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
        except: return None
        else: return result1 + result2
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
        if mode == "+": mysum += d
        else: mysum -= d
    string = timeFloatToHHMM(delta=str(mysum))
    return string

def timeFloatToHHMM(hours=None, delta=None):
    """ Преобразует числовое время в HHMM в зависимости от типа и длины строки, которую выдает timedelta """
    if delta == None: delta = str(datetime.timedelta(hours=hours)).strip()
    if "." in delta: delta = delta[0: delta.index(".")]
    if len(delta) == 7:                             # "1:00:00"
        result = "%s:%s" % (delta[0:1], delta[2:4])
    elif len(delta) == 8:                           # "10:00:00"
        result = "%s:%s" % (delta[0:2], delta[3:5])
    elif len(delta) == 6:                           # "100:00"
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

def numberize(line):
    """ Убирает из слова все нечисловые символы, чтобы получилось отсортировать по номеру """
    result = 0
    try:
        return float(line)
    except:
        l = len(line)
        while l > 0:
            if line[:l].isnumeric():
                result = float(line[:l])
                break
            else: l -= 1
    return result

def alpha(line):
    return "000"+line
