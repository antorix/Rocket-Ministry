#!/usr/bin/python
# -*- coding: utf-8 -*-

import io2
from os import name

def icon(myIcon, forceText=False, simplified=True):
    simplified=True
    if io2.Mode=="sl4a" and io2.settings[0][1]==False and forceText==False:#) or name=="posix":
        if myIcon=="globe": return "🗺"
        elif myIcon=="map": return "🧭"
        elif myIcon=="rocket": return "🚀"
        elif myIcon=="timer": return "⌚"
        elif myIcon=="report": return "🗒"
        elif myIcon=="contacts": return "👥"
        elif myIcon=="notebook": return "📗"
        elif myIcon=="database": return "🗄"
        elif myIcon=="file": return "💾"
        elif myIcon=="appointment": return "📆"# 📅🗓📆
        elif myIcon=="calendar": return "📅"
        elif myIcon=="preferences": return "⚙️"#"🔧"#⚙
        elif myIcon=="plus": return "➕"
        elif myIcon=="contact": return "👤"
        elif myIcon=="case": return "💼"
        elif myIcon=="sort": return "🔃"#
        elif myIcon=="mark": return "✅"#✔️️
        elif myIcon=="cross": return "❌"
        elif myIcon=="box": return "⬜"
        elif myIcon=="fail": return "❌"
        elif myIcon=="pin": return "📌"
        elif myIcon=="cut": return "🗑"
        elif myIcon=="smile": return "😍" #"\ud83d\ude42"
        elif myIcon=="note": return "📄"
        elif myIcon=="status": return "⚪"
        elif myIcon=="square": return "◼"
        elif myIcon=="mail": return "📤"
        elif myIcon=="download": return "📥"
        elif myIcon=="export": return "📨"
        elif myIcon=="edit": return "🖋"
        elif myIcon=="extra": return "😎"
        elif myIcon=="extra2": return "😎"
        elif myIcon=="slippage": return "😥"
        elif myIcon=="placements": return "📚"
        elif myIcon=="video": return "🎞"
        elif myIcon=="credit": return "🖥️"
        elif myIcon=="returns": return "⏩"
        elif myIcon=="studies": return "📖"
        elif myIcon=="mute": return "🔇"
        elif myIcon=="unreachable": return "🚫"
        elif myIcon=="stats": return "📊"
        elif myIcon=="save": return "💾"
        elif myIcon=="load": return "📁"
        elif myIcon=="smartphone": return "📲"
        elif myIcon=="restore": return "📤"
        elif myIcon=="help": return "❓"
        elif myIcon=="info": return "ℹ️"#\u2139\ufe0f" #
        elif myIcon=="house": return "🏢"
        elif myIcon=="cottage": return "🏠"
        elif myIcon=="office": return "🏫"
        elif myIcon=="porch": return "🏣"
        elif myIcon=="door": return "🚪"
        elif myIcon=="baloon": return "📇"
        elif myIcon=="date": return "📆"
        elif myIcon=="call": return "📲"
        elif myIcon=="lamp": return "💡"
        elif myIcon=="bullet": return "•"
        elif myIcon=="arrow": return "↑"
        elif myIcon=="star": return "⭐"
        elif myIcon=="search": return "🔎"
        elif myIcon=="flag": return "🚩"
        elif myIcon=="calc": return "🎛"
        elif myIcon=="import": return "📥"
        elif myIcon=="logreport": return "📒"
        elif myIcon=="lock": return "🔒"
        elif myIcon=="image": return "🖼"
        elif myIcon=="circle": return "⚪"
        elif myIcon=="clipboard": return "📋"
        elif myIcon=="clear": return "🗑"
        elif myIcon=="mic": return "💬" #💭🗨
        elif myIcon=="intercom": return "📟"  #
        elif myIcon=="prevmonth": return "📋" # new
        elif myIcon=="up": return "↑"#⬆
        elif myIcon=="down": return "↓"#⬇
        elif myIcon=="phone": return "📱" # телефон в настройках контакта
        elif myIcon=="phone2": return "☎" # иконка телефонного участка и режима справочной
        elif myIcon=="phone3": return "📱" # используется для показа в списке жильцов, заменяется на "т."
        elif myIcon=="phone4": return "📞" # иконка диапазона (подъезда) в телефонном участке
        elif myIcon=="warning": return "⚠️"
        elif myIcon=="explosion": return "💥"
        elif myIcon=="update": return "🔄"
        elif myIcon=="numbers": return "🔢"
        elif myIcon=="porchCircle1": return "🟡"
        elif myIcon=="porchCircle2": return "🟣"
        elif myIcon=="porchCircle3": return "🔴"

        elif myIcon=="reject":
            if io2.settings[0][16]==0:             # статус 0
                return "🔘"
            else:
                return "🥶"
        elif myIcon=="interest":
            if io2.settings[0][16] == 0:
                return "🙂"                                      # статус 1
            else:
                return "😍"
        elif myIcon=="green":
            if io2.settings[0][16]==0:             # статус 2
                return "🟢"
            else:
                return "🤢"
        elif myIcon=="purple":
            if io2.settings[0][16]==0:           # статус 3
                return "🟣"
            else:
                return "👾"
        elif myIcon=="brown":
            if io2.settings[0][16]==0:           # статус 4
                return "🟤"
            else:
                return "🤠"
        elif myIcon=="danger":
            if io2.settings[0][16]==0:           # статус 5
                return "🔴"
            else:
                return "😡"
        elif myIcon=="question":                                        # статус ?
            if io2.settings[0][16] == 0:
                return "❔"
            else:
                return "🙄"#
        elif myIcon=="void": return "⚫"                               # статус ""

        else: return "👽"

    else:
        if myIcon=="globe": return "⌂"
        elif myIcon=="map": return "↔"
        elif myIcon=="rocket":
            if io2.settings[0][1] != 1 and simplified==False:
                return "🚀"
            else:
                return "●"
        elif myIcon=="timer": return "●"
        elif myIcon=="report": return "±"
        elif myIcon=="contacts": return "Ω"
        elif myIcon=="notebook": return "□"
        elif myIcon=="console": return "▪"
        elif myIcon=="database": return "◊"
        elif myIcon=="file": return "■"
        elif myIcon=="appointment":
            if io2.settings[0][1] != 1 and simplified == False:
                return "📆"
            else:
                return "☼"
        elif myIcon=="calendar": return "©"        
        elif myIcon=="preferences":
            if io2.settings[0][1] != 1 and simplified==False:
                return "⚙️"
            else:
                return "*"
        elif myIcon=="plus":
            if io2.settings[0][1] != 1 and simplified == False:
                return "➕"
            else:
                return "+"
        elif myIcon=="contact": return "Ω"
        elif myIcon=="case": return "□"
        elif myIcon=="sort":
            if io2.settings[0][1] != 1 and simplified == False:
                return "🔄"
            else:
                return "±"
        elif myIcon=="mark":
            if io2.settings[0][1] != 1 and simplified == False:
                return "✅"
            else:
                return "√"
        elif myIcon=="cross":
            if io2.settings[0][1] != 1 and simplified == False:
                return "❌"
            else:
                return "×"
        elif myIcon=="box":
            if io2.settings[0][1] != 1 and simplified == False:
                return "⬜"
            else:
                return "□"
        elif myIcon=="fail": return "˟"
        elif myIcon=="pin":
            if io2.settings[0][1] != 1 and simplified == False:
                return "📌"
            else:
                return "•"#>
        elif myIcon=="cut":
            if io2.settings[0][1] != 1 and simplified==False:
                return "🗑"
            else:
                return "×"
        elif myIcon=="smile": return "☺"
        elif myIcon=="note": return "□"
        elif myIcon=="status": return "○"
        elif myIcon=="square": return "■"
        elif myIcon=="mail": return "@"
        elif myIcon=="download": return "▼"
        elif myIcon=="export": return "▲"
        elif myIcon=="edit": return "✶"
        elif myIcon=="extra": return "☺"
        elif myIcon=="extra2": return "↑"
        elif myIcon=="slippage":
            if io2.settings[0][1] != 1 and simplified==False:
                return "😥"
            else:
                return "↓"
        elif myIcon=="placements": return "▫"
        elif myIcon=="video": return "▫"
        elif myIcon=="credit": return "○"
        elif myIcon=="returns": return "▫" 
        elif myIcon=="studies": return "▫"
        elif myIcon=="mute": return "♪×"
        elif myIcon=="unreachable":
            if io2.settings[0][1] != 1 and simplified==False:
                return "🚫"
            else:
                return "○"
        elif myIcon=="stats": return "⅜"
        elif myIcon=="save": return "↓"
        elif myIcon=="load": return "←"
        elif myIcon=="smartphone": return "→"
        elif myIcon=="restore": return "↑"
        elif myIcon=="help": return "?"
        elif myIcon=="info": return "i"
        elif myIcon=="house": return "▓"
        elif myIcon=="cottage": return "▒"
        elif myIcon=="office": return "░"
        elif myIcon=="porch": return "⌂"  # small house
        elif myIcon=="door": return "⌂" # the same as porch
        elif myIcon=="baloon": return "«" # quote
        elif myIcon=="date": return "√"
        elif myIcon=="call": return "→"
        elif myIcon=="lamp": return "☼"
        elif myIcon=="bullet": return "◦"
        elif myIcon=="arrow": return "↑"
        elif myIcon=="star": return "✶"
        elif myIcon=="search": return "?"
        elif myIcon=="flag": return "╒" # the same as porch
        elif myIcon=="calc": return "▪"
        elif myIcon=="import": return "▼"
        elif myIcon=="logreport": return "□"
        elif myIcon=="lock": return "◊"
        elif myIcon=="image": return "□"
        elif myIcon=="circle": return "●"
        elif myIcon=="clipboard": return "→"
        elif myIcon=="clear": return "◌"
        elif myIcon=="mic":
            if io2.settings[0][1]!=1 and simplified==False:
                return "💬"
            else:
                return "≈"#«
        elif myIcon=="intercom": return "◘"
        elif myIcon=="prevmonth": return "←"
        elif myIcon=="up": return "↑"
        elif myIcon=="down": return "↓"
        elif myIcon=="phone": return "§"#
        elif myIcon=="phone2": return "▲"#◊
        elif myIcon=="phone3": return "т."
        elif myIcon=="phone4": return "§"
        elif myIcon=="warning": return "⚠"
        elif myIcon=="explosion": return "☼"
        elif myIcon=="update": return "↨"
        elif myIcon=="numbers":
            if io2.settings[0][1]!=1 and simplified==False:
                return "🔢"
            else:
                return "№"
        elif myIcon=="porchCircle1": return "●○○"
        elif myIcon=="porchCircle2": return "○●○"
        elif myIcon=="porchCircle3": return "○○●"

        elif myIcon=="reject":
            if io2.settings[0][1] != 1 and simplified==False:
                return "✖"
            else:
                return "×"#✖○"#x"     # статус 0
        elif myIcon=="interest" and io2.settings[0][1]==0:
            return "☺" #●                          # статус 1 для графики
        elif myIcon == "interest" and io2.settings[0][1] == 1:
            return "☻" #●                          # статус 1 для консоли
        elif myIcon=="green": return "○"            # статус 2
        elif myIcon=="purple": return "◊"           # статус 3
        elif myIcon=="brown": return "♦"           # статус 4
        elif myIcon=="danger": return "!"           # статус 5
        elif myIcon=="question": return "?"         # статус ?
        elif myIcon=="void": return " "          # статус ""
        else: return "?"
