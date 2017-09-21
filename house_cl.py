#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import io2
import dialogs
import set
import reports
import contacts
from set import icon

class House():
    
    def __init__(self):
        self.title = ""
        self.porchesLayout = "а"
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        self.note = ""
        self.type = ""
        self.porches = []        
        
    def getHouseStats(self):
        """ Finds how many interested (status==2) people in house """
        
        visited=0
        interest=0
        for a in range(len(self.porches)):
            for b in range(len(self.porches[a].flats)):
                if self.porches[a].flats[b].status !=  "": visited += 1
                if self.porches[a].flats[b].status == "2": interest += 1
        return [visited, interest]
    
    def sortPorches(self):
        if self.porchesLayout=="н": # numeric by number
            self.porches.sort(key=lambda x: float(x.title), reverse=False)
        if self.porchesLayout=="а": # alphabetic by title
            self.porches.sort(key=lambda x: x.title, reverse=False)
            
    def showPorches(self, settings):        
        self.sortPorches()
        message = "Создан %s %s %s\n\n" % (self.date, " %s" % icon("mark", settings[0][4]) + str(self.getHouseStats()[0]), " %s" % icon("arrow", settings[0][4]) + str(self.getHouseStats()[1]))
        for i in range(len(self.porches)):
            message += icon("porch", settings[0][4]) + "%s)" % self.porches[i].title
            if i != len(self.porches)-1: message += " "
        message += "\n"
        if self.note != "": message += "\n%s %s" % (icon("pin", settings[0][4]), self.note)
        return message
        
    def addPorch(self, input=""):
        self.porches.append(self.Porch()) 
        self.porches[len(self.porches)-1].title = input.strip()
        
    def rename(self, input):
        self.title = input[3:].upper()
        
    def export(self):
        return [self.title, self.porchesLayout, self.date, self.note, self.type, [self.porches[i].export() for i in range(len(self.porches))]]
            
    class Porch():
        
        def __init__(self):
            self.title = ""
            self.flatsLayout = "н"
            self.note = ""
            self.flats = [] # list of Flat instances, initially empty
            self.id = "porch"
            
        def sortFlats(self):                         
            if self.flatsLayout=="н": # numeric by number
                try:
                    self.flats.sort(key=lambda x: float(x.number))
                except:
                    self.flatsLayout="а"
                    self.flats.sort(key=lambda x: x.getNumericalTitle(), reverse=False)
            elif self.flatsLayout=="а": # numeric-alphabetic by number                
                self.flats.sort(key=lambda x: x.title)                
                self.flats.sort(key=lambda x: x.getNumericalTitle())                
            elif self.flatsLayout=="с": # alphabetic by status character
                self.flats.sort(key=lambda x: x.checkStatus())
            else: # floors view with reversed numeric order
                try:
                    a = len(self.flats)/int(self.flatsLayout[0:])
                    if not a.is_integer(): return 1 # stop=1                    
                    self.flats.sort(key=lambda x: float(x.getNumericalTitle()))                    
                    
                    # Reversing order in rows to straight                    
                    rows = int(self.flatsLayout[0:])
                    columns = int(len(self.flats) / rows)
                    
                    row=[i for i in range(rows)]
                    i=0
                    for r in range(rows):
                        row[r]=self.flats[i:i+columns]
                        i += columns
                    row = row[::-1]                
                    del self.flats [:]
                    for r in range(rows): self.flats += row[r]             
                except:
                    self.flatsLayout="а"                
            return 0
                
        def showFlats(self, type, settings):
            stop = self.sortFlats()
            
            if len(self.flats)==0:
                if type=="condo": message = "Нет ни одной квартиры. Создайте их с помощью команды, например:\n+1\n+1,ж45\n+1, Иван\n+1-30\n*1\nПодробную справку по командам смотрите в меню «Подъезд»."
                elif type=="office": message = "Нет ни одного сотрудника. Создайте их с помощью команды, например:\n+1\n+1,продавец\n+1, Марина, продавец\n*1\nПодробную справку по командам смотрите в меню «Офис»."
                else: message = "Нет ни одной квартиры (дома). Создайте их с помощью команды, например:\n+1\n+1,ж45\n+1, Иван\n+1-30\n*1\nПодробную справку по командам смотрите в меню «Сегмент»."
            else:
                message = ""
                       
                if self.flatsLayout=="н" or self.flatsLayout=="а" or self.flatsLayout=="с":
                    rows = 1
                    columns = 999
                elif stop==1: # if per-floor layout activated
                    io2.log("Не хватает объектов для поэтажной расстановки, добавьте или убавьте объекты")
                    rows = 1
                    columns = 999
                    try: self.flats.sort(key=lambda x: float(x.number))
                    except:
                        self.flats.sort(key=lambda x: x.getNumericalTitle())
                else:
                    rows = int(self.flatsLayout[0:])
                    columns = int(len(self.flats) / rows) 
                i = 0
                
                for r in range(rows):
                    for c in range(columns):
                        if c < len(self.flats):
                            
                            if io2.osName=="android":
                                
                                if settings[0][1]==0: # adaptation for small system fonts DISABLED
                                    if   len(self.flats[i].number)==1: gap = "\u00A0\u00A0\u00A0" # formatting by spaces (Android)
                                    elif len(self.flats[i].number)==2: gap = "\u00A0"
                                    #elif len(self.flats[i].number)==3: gap = "\u00A0"
                                    else: gap = ""
                                else:
                                    if   len(self.flats[i].number)==1: gap = "\u00A0\u00A0\u00A0\u00A0" # formatting by spaces (Android)
                                    elif len(self.flats[i].number)==2: gap = "\u00A0\u00A0"
                                    elif len(self.flats[i].number)==3: gap = "\u00A0"
                                    else: gap = ""
                            else:
                                if   len(self.flats[i].number)==1: gap = "" 
                                elif len(self.flats[i].number)==2: gap = ""
                                elif len(self.flats[i].number)==3: gap = ""
                                else: gap = ""
                            
                            message += "%s%s)%s\t" % (gap, self.flats[i].number, set.getStatus(self.flats[i].status, settings)[0])
                            #message += "%3s)%s\t" % (self.flats[i].number, set.getStatus(self.flats[i].status, settings))
                            i+=1
                    
                    #print("rows: %d\nr: %d" % (rows, r))                
                    if rows-r != 1:
                        message += "\n"              
                
            if len(self.flats)==1: message += "\n\nДля входа в единственный объект просто нажмите ввод."
        
            return message
        
        def addFlat(self, input, settings, virtual=False):            
            self.flats.append(self.Flat()) 
            last = len(self.flats)-1 # number of modified flat is the last appended
            record = self.flats[last].setFlat(input, virtual)
            createdFlat = last
            delete = False
            enter = 0
            
            if record != "": # add record at once (if any)
                self.flats[last].addRecord(record)                 
            
            # Check if flat with such number already exists, it is deleted
            
            for i in range(last): 
                if self.flats[i].number == self.flats[last].number: # flat with identical number (i) found
                    if len(self.flats[i].title) <= len(self.flats[i].number): delete=True # title not bigger than number - no tenant, delete silently
                    else:
                        if dialogs.dialogConfirm(icon("cut", settings[0][4]) + " Перезапись «%s»" % self.flats[i].title, "Здесь есть описание контакта! Точно перезаписать?") == True: delete=True # title bigger, user approves
                        else:
                            del self.flats[last] # user reconsidered, delete the newly created empty flat
                            createdFlat = -1
                            record = ""
                    break
                    
            if delete==True: # deletion
                del self.flats[i]
                createdFlat = last-1
                
            if ">" in input: # for automatic entry into flat
                for i in range(len(input)):
                    if input[i] == ">":
                        self.flats[last].title = self.flats[last].title[:i-1]
                        self.flats[last].number = self.flats[last].number[:i-1]
                        enter = 1 # True: entry"""
            
            return [createdFlat, record, enter]
            
        def addFlats(self, input, settings):
            s=0
            f=0        
            for i in range(len(input)):
                if input[i]=="-": s=i
                if input[i]=="/": f=i
            start = int(input[1:s])
            if f==0: end = int(input[s+1:])
            else: end = int(input[s+1:f])
            if start >= end: return [start, end, 1] # stop if start higher than end
            
            for i in range(start, end+1):
                self.flats.append(self.Flat())
                self.flats[len(self.flats)-1].title =  str(i)
                self.flats[len(self.flats)-1].number = str(i)
            
            if f!=0: self.flatsLayout = input[f+1:]                
            
            return [start, end, 0]            
            
        def export(self):
            return [self.title, self.flatsLayout, self.note, [self.flats[i].export() for i in range(len(self.flats))]]

        class Flat():
            
            def __init__(self):
                self.title = ""
                self.number = "" # automatically generated from first characters of title
                self.status = "" # automatically generated from last symbol of last record
                self.note = ""
                self.records = [] # list of Record instances, initially empty
            
            def getNumericalTitle(self):                
                output=""                
                for char in self.number:
                    if contacts.ifInt(char)==True: output+=char
                try: return int(output)
                except: return 0                
            
            def showRecords(self, settings):
                options = [icon("plus", settings[0][4]) + " " + icon("tablet", settings[0][4])]
                for i in range(len(self.records)):
                    options.append(icon("tablet", settings[0][4]) + " %s: %s" % (self.records[i].date, self.records[i].title))
                #options.append("\ud83d\udccc %s" % self.note)
                return options
                
            def addRecord(self, input):
                self.records.append(self.Record())
                self.records[len(self.records)-1].title = input
                
                date = time.strftime("%d", time.localtime())
                month = reports.monthName()[5]
                #year = time.strftime("%Y", time.localtime())
                timeCur = time.strftime("%H:%M", time.localtime())
                
                self.records[len(self.records)-1].date = "%s %s, %s" % (date, month, timeCur)
                
                self.status = self.records[len(self.records)-1].title[len(input)-1] # status set to last character of last record
                return len(self.records)-1
                
            def setFlat(self, input, virtual=False):            
                """ Set title and number, return call record if exists """
                
                if "." in input and not "," in input: # lone "."
                    if virtual==False:
                        self.title = self.number = input[1:input.index(".")]
                    else:
                        self.title = "?, " + input[1:input.index(".")]
                        self.number = "?"
                    return input[input.index(".")+1:]
                    
                if not "." in input and not "," in input: # whole input
                    if virtual==False:
                        self.title = self.number = input[1:]                     
                    else:
                        self.title = "?, " + input[1:] 
                        self.number = "?"
                    return ""
                
                if "," in input and not "." in input: # whole input
                    self.number = input[1:input.index(",")] 
                    self.title = input[1:]    
                    return ""
            
                if "." in input and "," in input: # if both present in right order, correctly return record
                    if input.index(",") < input.index("."): # , .
                        self.title = input[1:input.index(".")]
                        self.number = input[1:input.index(",")]
                    else: # . , 
                        if virtual==False:
                            self.title = self.number = input[1:input.index(".")]
                        else:
                            self.title = "?, " + input[1:input.index(".")]
                            self.number = "?"
                    return input[input.index(".")+1:]
                    
            def checkStatus(self):                
                if   self.status=="2": return 0 # value serves to correctly sort by status 
                elif self.status=="1": return 1
                elif self.status=="":  return 3
                elif self.status=="0": return 4
                elif self.status=="9": return 5
                else: return 2
                
            def export(self):                
                return [self.title, self.note, [self.records[i].export() for i in range(len(self.records))]]
            
            class Record():            
                
                def __init__(self):
                    self.date = ""
                    self.title = ""
                    self.note = ""
                    
                def showContent(self, settings):
                    message = self.title
                    if self.note != "": message += "\n\n%s %s" % (self.note, icon("pin", settings[0][4]))
                    return message
                    
                def export(self):
                    return [self.date, self.title, self.note]
