#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from time import sleep
    sleep(0.2)
    from androidhelper import Android
    phone = Android() # запускаем заcтавку
    phone.dialogCreateSpinnerProgress(title="\ud83d\ude80 Rocket Ministry", message="Поехали!", maximum_progress=100) # показываем заставку
    phone.dialogShow()
except:
    pass

from io2 import load, settings
import dialogs
import homepage as homepage
from icons import icon

def app():
    """ Callable program """

    print("Загружаем базу данных")
    load()

    if settings[0][17]!="":
        password=dialogs.dialogGetPassword(
            title = icon("lock") + " Введите пароль",
            cancel="Выход"
        )
    else:
        password=settings[0][17]
    if password is None:
        return
    elif password==settings[0][17]:
        homepage.homepage()

# Start program app

if __name__ == "__main__":
    app()
