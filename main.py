#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from kivy.app import App
except:
    from subprocess import check_call
    from sys import executable
    check_call([executable, '-m', 'pip', 'install', 'kivy'])
    from kivy.app import App

import app

if __name__ == "__main__":
    app.RM = app.RMApp()
    app.RM.run()
