#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from kivy import platform
    import plyer
    import requests
except:
    if platform != "android":
        print("Что-то из модулей не найдено. Устанавливаю, подождите...\nPlease wait, downloading missing modules...")
        from subprocess import check_call
        from sys import executable
        check_call([executable, '-m', 'pip', 'install', 'kivy==2.1.0'])
        check_call([executable, '-m', 'pip', 'install', 'plyer'])
        check_call([executable, '-m', 'pip', 'install', 'requests'])

from app import RM
if __name__ == "__main__": RM.run()