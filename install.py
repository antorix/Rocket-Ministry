import subprocess
import sys
import os, win32com.client
import urllib.request
from zipfile import ZipFile
from shutil import move, rmtree

def install():

    curPath = os.path.dirname(os.path.abspath(__file__))

    print("Установка Rocket Ministry. Не закрывайте это окно!\n")
    try:
        print("Загружаем файлы программы...\n")
        url = "https://github.com/antorix/Rocket-Ministry/archive/refs/heads/master.zip"
        file="files.zip"
        urllib.request.urlretrieve(url, file)
        zip = ZipFile(file, "r")
        zip.extractall("")
        zip.close()
        downloadedFolder = curPath + "\Rocket-Ministry-master"

        for file_name in os.listdir(downloadedFolder):
            source = downloadedFolder + "\\" + file_name
            destination = curPath + "\\" + file_name
            if os.path.isfile(source):
                move(source, destination)
        os.remove(file)
        rmtree(downloadedFolder)

    except:
        print("Не удалось загрузить файлы Rocket Ministry. Проверьте подключение к Интернету и попробуйте еще раз.")
        return

    try:
        print("Устанавливаем шрифт...\n")
        os.startfile("install_fonts.vbs")
    except:
        os.startfile("LiberationMono-Regular.ttf")  # попытка установить шрифт напрямую

    print("Создаем иконку на рабочем столе...\n")
    try:
        import winshell
    except:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "winshell"])
        import winshell
    desktop = winshell.desktop()
    path = os.path.join(desktop, 'Rocket Ministry.lnk')
    target = curPath + "/main.py"
    icon =  curPath + "/icon.ico"
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.IconLocation = icon
    shortcut.save()

    if os.path.exists("install.py"):
        print("Удаляем установочный файл...\n")
        remove("install.py")

    print("Поехали!\n")
    print("===================================================\n")
    from main import app
    app()

install()