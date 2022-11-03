#!/usr/bin/python
# -*- coding: utf-8 -*-
import io2
import homepage
import dialogs

def app():
    """ Callable program """

    io2.load()

    if io2.Mode=="text":
        io2.settings[0][1] = 1
    else:
        io2.settings[0][1] = 0

    if io2.settings[0][17]!="":
        password=dialogs.dialogGetPassword(title="Rocket Ministry")
    else:
        password=io2.settings[0][17]
    if password is None:
        return
    elif password==io2.settings[0][17]:
        homepage.homepage()

# Start program app

if __name__ == "__main__":
    app()
