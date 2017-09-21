#!/usr/bin/python
# -*- coding: utf-8 -*-

import house_cl
    
def sortHouses(houses, settings, resources):
    """ Sorts houses on the start screen """
    
    if settings[1]=="д": # by date
        houses.sort(key=lambda x: x.date, reverse=False)
    elif settings[1]=="а": # alphabetic by title
        houses.sort(key=lambda x: x.title, reverse=False)
    elif settings[1]=="и": # by number of interested persons
        for i in range(len(houses)):
            houses[i].interest = houses[i].getHouseStats()[1]
        houses.sort(key=lambda x: x.interest, reverse=True)
    elif settings[1]=="п": # by number of visited persons
        for i in range(len(houses)):
            houses[i].visited = houses[i].getHouseStats()[0]
        houses.sort(key=lambda x: x.visited, reverse=False)

def addHouse(houses, input, type):
    """ Adding new house """
    
    houses.append(house_cl.House())
    newHouse=len(houses)-1
    houses[newHouse].title = (input.strip()).upper()
    houses[newHouse].type = type
    
def delHouse(houses, input):
    """ Deleting house """
    
    del houses[int(input[1:])-1]

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
    except: return None
    else: return "".join(date[0]+date[1]+date[2]+date[3]+date[4])
