#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request
from os import path

url="web_install.py"

if path.exists("main.py"):
    from main import app
    app()

elif not path.exists(url):
    urllib.request.urlretrieve(url, url[url.index("master/") + 7:])
    from install import install
    install()
