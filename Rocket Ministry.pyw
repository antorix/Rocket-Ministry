#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ИНСТРУКЦИИ:

Если Python успешно установился, для запуска Rocket Ministry просто запустите этот файл. Необходимо подключение к Интернету. Затем нужно подождать несколько секунд. При необходимости подтвердите установку шрифта.

Если в системе отсутствует Python, запустите файл install заново. Если это не помогает, скачайте и установите Python с официального сайта python.org.

Если проблемы остаются, пишите на antorix@gmail.com. Разработчик отвечает оперативно на все вопросы!

"""

"""

ИНСТРУКЦИИ:

Если Python успешно установился, для запуска Rocket Ministry просто запустите этот файл. Необходимо подключение к Интернету. Затем нужно подождать несколько секунд. При необходимости подтвердите установку шрифта.

Если в системе отсутствует Python, запустите файл install заново. Если это не помогает, скачайте и установите Python с официального сайта python.org.

Если проблемы остаются, пишите на antorix@gmail.com. Разработчик отвечает оперативно на все вопросы!

"""

from os import path, remove, startfile
import tkinter.messagebox
import urllib.request

reply=None

if not path.exists("main.py"): # если основное приложение не найдено, скачиваем его
    title = "Rocket Ministry"
    reply = tkinter.messagebox.askyesno(
        title,
        "Первый запуск программы. После закрытия этого окна нужно подождать несколько секунд.\n\n" +\
        "А пока один вопрос: у вас есть месячная норма часов?"
    )
    try:
        for line in urllib.request.urlopen("https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/version"):
            newVersion = line.decode('utf-8').strip()
    except:
        tkinter.messagebox.showinfo(
            title,
            "Не удалось подключиться к серверу GitHub! Проверьте наличие Интернета и попробуйте еще раз."
        )
    else:
        urls = ["https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/icon.ico",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/console.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/contacts.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/dialogs.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/homepage.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/house_cl.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/house_op.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/icons.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/io2.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/main.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/notebook.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/reports.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/set.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/territory.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/global_state.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/choice_box.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/button_box.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/fileboxsetup.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/fileopen_box.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/fillable_box.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/text_box.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/utils.py",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/create_shortcut.vbs",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/install_fonts.vbs",
                "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/LiberationMono-Regular.ttf"
                ]
    try:
        for url in urls:
            urllib.request.urlretrieve(url, url[url.index("master/") + 7:])
    except:
        tkinter.messagebox.showinfo(
            title,
            "Не удалось загрузить файлы Rocket Ministry. Проверьте подключение к Интернету и попробуйте еще раз."
        )
    else:
        print("Файлы Rocket Ministry успешно загружены.")
    
        print("Удаляем установочный файл Python...")
        if path.exists("install-установка.exe"):
            remove("install-установка.exe")
        if path.exists("unattend.xml"):
            remove("unattend.xml")
    
        print("Устанавливаем шрифт Liberation Mono...")
        startfile("install_fonts.vbs")
    
        print("Создаем ярлык...")
        startfile("create_shortcut.vbs")
    
print("Поехали!")
from main import app
app(reply)
