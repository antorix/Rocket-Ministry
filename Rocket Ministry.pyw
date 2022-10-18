#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request
from os import path
import tkinter.messagebox

url = "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/web_install.py"

if not path.exists("main.py"):
    tkinter.messagebox.showinfo(
        "Установка Rocket Ministry",
        "Первый запуск программы. Закройте это окно и подождите несколько секунд.")

    if not path.exists("web_install.py"):
        urllib.request.urlretrieve(url, "web_install.py")

    from web_install import install
    install(desktop=False)

from main import app
app()
