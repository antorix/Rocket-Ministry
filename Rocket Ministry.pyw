#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request
from os import path

url = "https://raw.githubusercontent.com/antorix/Rocket-Ministry/master/web_install.py"

if path.exists("main.py"):
    from main import app
    app()

elif path.exists(url):
    from web_install import install
    install()

else:
    urllib.request.urlretrieve(url, "web_install.py")
    from web_install import install
    install()
