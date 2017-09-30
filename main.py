#!/usr/bin/python
# -*- coding: utf-8 -*-
version = "1.4.03"

import io2
import homepage
import sys
import dialogs
import reports
from icons import icon

def app():
    """ Callable program """
    
    if "--textconsole" in sys.argv: pureText=True
    else: pureText=False
    
    # Check arguments, load data
    if "--import" in sys.argv: houses, settings, resources = io2.load(url=settings[0][14])
    else: houses, settings, resources = io2.load()
    
    while 1: # check password
        if settings[0][17]!="": password = dialogs.dialog(title = icon("lock", settings[0][4]) + " Введите пароль %s " % reports.getTimerIcon(settings[2][6], settings), cancel="Выход")        
        else: password=settings[0][17]
        
        if password==None: break
        elif password==settings[0][17]:
    
            # Stop spinning picture    
            if io2.osName == "android":
                from androidhelper import Android
                Android().dialogDismiss()
        
            # Run homepage  
            homepage.homepage(houses, settings, resources) 

# Start program app

if __name__ == "__main__":
    app()
