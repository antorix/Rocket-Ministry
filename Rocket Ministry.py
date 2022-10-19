#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request
from os import path

url = "https://github.com/antorix/Rocket-Ministry/releases/download/Python/rocket_ministry_install_script.py"

installFile = "rm-install.py"

if not path.exists("main.py"):

    if not path.exists(installFile):
        urllib.request.urlretrieve(url, installFile)

    from rm-install import install
    install(desktop=False)

from main import app
app()
