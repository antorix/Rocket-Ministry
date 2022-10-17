#!/usr/bin/python
# -*- coding: utf-8 -*-

from io2 import load, settings
import dialogs
import homepage as homepage
from icons import icon

def app(reply=None):
    """ Callable program """

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
        homepage.homepage(reply)

# Start program app

if __name__ == "__main__":
    app()
