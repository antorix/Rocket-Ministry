#!/usr/bin/python
# -*- coding: utf-8 -*-
import io2
from io2 import load, settings
import dialogs
import homepage as homepage
from icons import icon

def app():
    """ Callable program """

    load()
    if io2.Mode=="text":
        io2.settings[0][1] = 1
    else:
        io2.settings[0][1] = 0

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
