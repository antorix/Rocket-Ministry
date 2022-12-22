#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request
from os import path
import app

installFile = "rm_install.py"

url = "https://github.com/antorix/Rocket-Ministry/releases/download/Python/" + installFile

if not path.exists("main.py"):

    if not path.exists(installFile):
        urllib.request.urlretrieve(url, installFile)

    from rm_install import install
    install(standalone=False)

app.RM = app.RMApp()
app.RM.run()