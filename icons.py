#!/usr/bin/python
# -*- coding: utf-8 -*-

import io2

def icon(myIcon, forceText=False):
    if io2.Mode=="sl4a" and io2.settings[0][1]==False and forceText==False:
        if myIcon=="globe": return "🗺" #"\ud83c\udfe2" # if Android below 4.4
        elif myIcon=="map": return "🧭" #"\ud83d\udea9"
        elif myIcon=="rocket": return "🚀"
        elif myIcon=="timer": return "⌚" #"\u23F0"
        elif myIcon=="report": return "🗒" #"\ud83d\udcc3"
        elif myIcon=="contacts": return "\ud83d\udc65" # "\ud83d\udcc7"
        elif myIcon=="notebook": return "📗" #"\ud83d\udcd4"
        elif myIcon=="console": return "\ud83d\udcbb"
        elif myIcon=="database": return "\ud83d\uddc4\ufe0f"
        elif myIcon=="file": return "\ud83d\udcbe"
        elif myIcon=="appointment": return "📆"# 📅🗓📆
        elif myIcon=="calendar": return "📅" #"\ud83d\udcc5"
        elif myIcon=="preferences": return "⚙️" #"\ud83d\udd27" #"\ud83d\udd28"
        elif myIcon=="plus": return "\u2795"
        elif myIcon=="contact": return "\ud83d\udc64"
        elif myIcon=="case": return "💼"
        elif myIcon=="sort": return "\ud83d\udd03"
        elif myIcon=="mark": return "✅"#✔
        elif myIcon=="cross": return "❌"
        elif myIcon=="box": return "⬜"
        elif myIcon=="fail": return "\u274c"
        elif myIcon=="pin": return "📌" #"\ud83d\udd8d\ufe0f"
        elif myIcon=="cut": return "🗑"
        elif myIcon=="table": return "\u2702" # new
        elif myIcon=="smile": return "😍" #"\ud83d\ude42"
        elif myIcon=="note": return "\ud83d\udcc4"
        elif myIcon=="status": return "⚪"
        elif myIcon=="square": return "◼"
        elif myIcon=="mail": return "📤"
        elif myIcon=="download": return "📥"
        elif myIcon=="export": return "📨"
        elif myIcon=="edit": return "🖋"
        elif myIcon=="extra": return "\ud83d\ude0e"
        elif myIcon=="extra2": return "\ud83d\ude0e"
        elif myIcon=="slippage": return "\ud83d\ude22"
        elif myIcon=="placements": return "📚" #"\ud83d\udcda"
        elif myIcon=="video": return "🎞"
        elif myIcon=="credit": return "🖥️" #"\u231A"
        elif myIcon=="returns": return "⏩" #"\u23e9"
        elif myIcon=="studies": return "📖" #"\ud83d\udcd6"
        elif myIcon=="mute": return "\ud83d\udd07"
        elif myIcon=="unreachable": return "🚫"
        elif myIcon=="stats": return "📊"
        elif myIcon=="save": return "\ud83d\udcbe"
        elif myIcon=="load": return "\ud83d\udcc2"
        elif myIcon=="smartphone": return "📲"
        elif myIcon=="restore": return "\ud83d\udce4"
        elif myIcon=="help": return "❓"
        elif myIcon=="info": return "\u2139\ufe0f"
        elif myIcon=="house": return "🏢" #"\ud83c\udfe2"
        elif myIcon=="cottage": return "🏠" #"\ud83c\udfe0"
        elif myIcon=="office": return "🏫" #"\ud83c\udfeb"
        elif myIcon=="porch": return "🏣" #"\ud83c\udfe3"
        elif myIcon=="door": return "\ud83d\udeaa"
        elif myIcon=="baloon": return "📇" #"\ud83d\udcac"
        elif myIcon=="date": return "\ud83d\udcc6"
        elif myIcon=="call": return "\ud83d\udcf2"
        elif myIcon=="lamp": return "\ud83d\udca1"
        elif myIcon=="bullet": return "\ud83d\udd27"
        elif myIcon=="arrow": return "\u2197"
        elif myIcon=="star": return "⭐"
        elif myIcon=="search": return "\ud83d\udd0e"
        elif myIcon=="flag": return "\ud83d\udea9"
        elif myIcon=="calc": return "\ud83c\udf9b\ufe0f"
        elif myIcon=="import": return "\ud83d\udce9"
        elif myIcon=="logreport": return "\ud83d\udcd2"
        elif myIcon=="lock": return "🔒"
        elif myIcon=="jwlibrary": return "\ud83d\udc8e"
        elif myIcon=="image": return "🖼"
        elif myIcon=="circle": return "⚪"
        elif myIcon=="clipboard": return "📋"
        elif myIcon=="clear": return "🗑"
        elif myIcon=="mic": return "💬" #💭🗨
        elif myIcon=="intercom": return "📟"  #
        elif myIcon=="prevmonth": return "📋" # new
        elif myIcon=="up": return "🔼"#⬆
        elif myIcon=="down": return "🔽"#⬇
        elif myIcon=="phone": return "📱"
        elif myIcon=="phone2": return "☎"
        elif myIcon=="phone3": return "📞"
        elif myIcon=="warning": return "❗"
        elif myIcon=="explosion": return "💥"
        elif myIcon=="update": return "🔄"

        elif myIcon=="reject":
            if io2.Simplified==1 and io2.settings[0][16]==0:             # статус 0
                return "🔘"
            else:
                return "🥶"
        elif myIcon=="interest":
            if io2.Simplified == 1 and io2.settings[0][16] == 0:
                return "🙂"                                      # статус 1
            else:
                return "😍"
        elif myIcon=="green":
            if io2.Simplified==1 and io2.settings[0][16]==0:             # статус 2
                return "🟢"
            else:
                return "🤢"
        elif myIcon=="purple":
            if io2.Simplified==1 and io2.settings[0][16]==0:           # статус 3
                return "🟣"
            else:
                return "👾"
        elif myIcon=="brown":
            if io2.Simplified==1 and io2.settings[0][16]==0:           # статус 4
                return "🟤"
            else:
                return "🤠"
        elif myIcon=="danger":
            if io2.Simplified==1 and io2.settings[0][16]==0:           # статус 5
                return "🔴"
            else:
                return "😡"
        elif myIcon=="question":                            # статус ?
            if io2.Simplified == 1 and io2.settings[0][16] == 0:
                return "❔"
            else:
                return "🙄"#
        elif myIcon=="void": return "⚫"        # статус ""

        else: return "👽"

    else:
        if myIcon=="globe": return "⌂"
        elif myIcon=="map": return "↔"
        elif myIcon=="rocket": return "●"
        elif myIcon=="timer": return "●"
        elif myIcon=="report": return "±"
        elif myIcon=="contacts": return "Ω"
        elif myIcon=="notebook": return "□"
        elif myIcon=="console": return "▪"
        elif myIcon=="database": return "◊"
        elif myIcon=="file": return "■"
        elif myIcon=="appointment": return "☼"
        elif myIcon=="calendar": return "©"        
        elif myIcon=="preferences": return "✶"
        elif myIcon=="plus": return "+"
        elif myIcon=="contact": return "Ω"
        elif myIcon=="case": return "□"
        elif myIcon=="sort": return "±"        
        elif myIcon=="mark": return "√"
        elif myIcon=="cross": return "×"
        elif myIcon=="box": return "□"
        elif myIcon=="fail": return "˟"
        elif myIcon=="pin": return ">"
        elif myIcon=="cut": return "×"
        elif myIcon=="tablet": return "□"
        elif myIcon=="smile": return "☺"
        elif myIcon=="note": return "□"
        elif myIcon=="status": return "○"
        elif myIcon=="square": return "■"
        elif myIcon=="mail": return "@"
        elif myIcon=="export": return "▲"
        elif myIcon=="edit": return "✶"
        elif myIcon=="extra": return "☺"
        elif myIcon=="extra2": return "↑"
        elif myIcon=="slippage": return "↓"
        elif myIcon=="placements": return "▫"
        elif myIcon=="video": return "▫"
        elif myIcon=="credit": return "○"
        elif myIcon=="returns": return "▫" 
        elif myIcon=="studies": return "▫"
        elif myIcon=="mute": return "♪×"
        elif myIcon=="unreachable": return "○"
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
        elif myIcon=="jwlibrary": return "◊"
        elif myIcon=="image": return "□"
        elif myIcon=="circle": return "●"
        elif myIcon=="clipboard": return "→"
        elif myIcon=="clear": return "◌"
        elif myIcon=="mic": return "♫"
        elif myIcon=="intercom": return "◊"
        elif myIcon=="prevmonth": return "←"
        elif myIcon=="up": return "↑"
        elif myIcon=="down": return "↓"
        elif myIcon=="phone": return "◊"
        elif myIcon=="phone2": return "◊"
        elif myIcon=="phone3": return "◊"
        elif myIcon=="warning": return "⚠"
        elif myIcon=="explosion": return "☼"
        elif myIcon=="update": return "↨"

        elif myIcon=="reject": return "×"#○"#x"     # статус 0
        elif myIcon=="interest": return "●"         # статус 1
        elif myIcon=="green": return "◊"           # статус 2
        elif myIcon=="purple": return "○"            # статус 3
        elif myIcon=="brown": return "♦"            # статус 4
        elif myIcon=="danger": return "!"           # статус 5
        elif myIcon=="question": return "?"         # статус ?
        elif myIcon=="void": return " "         # статус ""
        else: return "?"