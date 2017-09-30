#!/usr/bin/python
# -*- coding: utf-8 -*-

import io2
#import sys

def icon(myIcon, setting=1, pureText=False):
    
    if io2.Textmode==True: pureText=True
    
    if setting==1 or io2.osName=="linux" or pureText==True:
        if myIcon=="globe": return "○"
        elif myIcon=="map": return "◦"    
        elif myIcon=="rocket": return "♠"
        elif myIcon=="timer": return "◷"
        elif myIcon=="report": return "±"
        elif myIcon=="contacts": return "☺"
        elif myIcon=="notebook": return "□"
        elif myIcon=="console": return "▪"
        elif myIcon=="file": return "▪"        
        elif myIcon=="appointment": return "☼"
        elif myIcon=="calendar": return "©"        
        elif myIcon=="preferences": return "▪"
        elif myIcon=="plus": return "+"          
        elif myIcon=="contact": return "☺"
        elif myIcon=="phone": return "(тел.)"     
        elif myIcon=="sort": return "±"          
        elif myIcon=="mark": return "√"           
        elif myIcon=="porch": return "\u2302" # small house
        elif myIcon=="pin": return ">"
        elif myIcon=="cut": return "\u2702" # scissors
        elif myIcon=="tablet": return "□"
        elif myIcon=="smile": return "☺"
        elif myIcon=="note": return "□"
        elif myIcon=="export": return "▲"
        elif myIcon=="edit": return "\u270f" # pen
        elif myIcon=="extra": return "▫"
        elif myIcon=="slippage": return "▫"
        elif myIcon=="placements": return "▫"
        elif myIcon=="videos": return "▫"
        elif myIcon=="credit": return "▫"
        elif myIcon=="returns": return "▫" 
        elif myIcon=="studies": return "▫"
        elif myIcon=="mute": return "♪×"
        elif myIcon=="stats": return "⅜"
        elif myIcon=="save": return "→"
        elif myIcon=="load": return "←"
        elif myIcon=="restore": return "↑"
        elif myIcon=="help": return "?"
        elif myIcon=="house": return "▓"
        elif myIcon=="cottage": return "▒"
        elif myIcon=="office": return "░"
        elif myIcon=="door": return "\u2302" # the same as porch
        elif myIcon=="baloon": return "\u201D" # quote
        elif myIcon=="date": return "12"
        elif myIcon=="call": return "→"
        elif myIcon=="lamp": return "☼"
        elif myIcon=="bullet": return "◦"
        elif myIcon=="arrow": return "↑"
        elif myIcon=="jwlibrary": return "◦"
        elif myIcon=="search": return "?"
        elif myIcon=="flag": return "\u2302" # the same as porch
        elif myIcon=="calc": return "▪"
        elif myIcon=="import": return "▼"
        elif myIcon=="logreport": return "□"
        elif myIcon=="lock": return ""
        
        else: return ""
        
    else:
        if myIcon=="globe":
            if io2.osName=="android" and io2.SDK<19: return "\ud83c\udfe2" # if Android below 4.4
            else: return "\ud83c\udf10"
            
        elif myIcon=="map":
            if io2.osName=="android" and io2.SDK<19: return "\ud83d\udea9"
            else: return "\uD83C\uDF0D"
        
        elif myIcon=="rocket": return "\ud83d\ude80"
        elif myIcon=="timer": return "\u23F0"
        elif myIcon=="report": return "\ud83d\udcc3"        
        elif myIcon=="contacts": return "\ud83d\udcc7"
        elif myIcon=="notebook": return "\ud83d\udcd2"
        elif myIcon=="console": return "\ud83d\udcbb"
        elif myIcon=="file": return "\ud83d\udcbe"
        elif myIcon=="appointment": return "\ud83d\udcc5"
        elif myIcon=="calendar": return "\ud83d\udcc5"
        elif myIcon=="preferences": return "\ud83d\udd27" #"\ud83d\udd28"      
        elif myIcon=="plus": return "\u2795"          
        elif myIcon=="contact": return "\ud83d\udc64"
        elif myIcon=="phone": return "\ud83d\udcf1"     
        elif myIcon=="sort": return "\ud83d\udd03"   
        elif myIcon=="mark": return "\u2714"     
        elif myIcon=="pin": return "\ud83d\udccc"     
        elif myIcon=="cut": return "\u2702"
        elif myIcon=="tablet": return "\ud83d\udccb"
        elif myIcon=="smile": return "\u263A"
        elif myIcon=="note": return "\ud83d\udcc4"
        elif myIcon=="export": return "\ud83d\udce7"
        elif myIcon=="edit": return "\u270f"
        elif myIcon=="extra": return "\ud83d\ude4c"
        elif myIcon=="slippage": return "\ud83d\ude2d"               
        elif myIcon=="placements": return "\ud83d\udcda"
        elif myIcon=="videos": return "\ud83d\udcf9"
        elif myIcon=="credit": return "\u231A"
        elif myIcon=="returns": return "\u23e9"
        elif myIcon=="studies": return "\ud83d\udcd6"
        elif myIcon=="mute": return "\ud83d\udd07"
        elif myIcon=="stats": return "\ud83d\udcca"
        elif myIcon=="save": return "\ud83d\udcbe"
        elif myIcon=="load": return "\ud83d\udcc2"
        elif myIcon=="restore": return "\ud83d\udce4"
        elif myIcon=="help": return "\u2753"
        elif myIcon=="house": return "\ud83c\udfe2"
        elif myIcon=="cottage": return "\ud83c\udfe0"
        elif myIcon=="office": return "\ud83c\udfeb"
        elif myIcon=="porch":
            if io2.osName=="android": return "\ud83c\udfe3" 
            else: return "\u2302"
        elif myIcon=="door": return "\ud83d\udeaa"
        elif myIcon=="baloon": return "\ud83d\udcac"
        elif myIcon=="date": return "\ud83d\udcc6"
        elif myIcon=="call": return "\ud83d\udcf2"
        elif myIcon=="lamp": return "\ud83d\udca1"
        elif myIcon=="bullet": return "\ud83d\udd27"
        elif myIcon=="arrow": return "\u2197"
        elif myIcon=="jwlibrary": return "\ud83d\udcd5"     
        elif myIcon=="search": return "\ud83d\udd0e"     
        elif myIcon=="flag": return "\ud83d\udea9"
        elif myIcon=="calc": return "\ud83d\udcdf"
        elif myIcon=="import": return "\ud83d\udce9"
        elif myIcon=="logreport": return "\uD83D\uDCD4"
        elif myIcon=="lock": return "\uD83D\uDD12"
        else: return ""       