#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request
from os import path

url = "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/web_install.py"

if not path.exists("main.py"):

    if not path.exists("web_install.py"):
        urllib.request.urlretrieve(url, "web_install.py")

    from web_install import install
    install(desktop=False)

from main import app
app()