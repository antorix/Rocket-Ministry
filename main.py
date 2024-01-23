#!/usr/bin/python
# -*- coding: utf-8 -*-

from subprocess import check_call
from sys import executable

try: import kivy
except ImportError as e:
    print(e, "Installing...")
    check_call([executable, '-m', 'pip', 'install', 'kivy==2.1.0'])

try: import plyer
except ImportError as e:
    print(e, "Installing...")
    check_call([executable, '-m', 'pip', 'install', 'plyer'])

try: import requests
except ImportError as e:
    print(e, "Installing...")
    check_call([executable, '-m', 'pip', 'install', 'requests'])

from app import RM
if __name__ == "__main__": RM.run()