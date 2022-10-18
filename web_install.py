import subprocess
import sys
import os
import urllib.request
from zipfile import ZipFile
from shutil import move, rmtree

def install(desktop):

    print("Установка Rocket Ministry. Не закрывайте это окно!\n")

    if desktop==True:
        try:
            import winshell
        except:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "winshell"])
            import winshell
        targetFolder = winshell.desktop()
        print("Создаем папку Rocket Ministry на рабочем столе...\n")
        targetFolder += "\Rocket Ministry"
        if not os.path.exists(targetFolder):
            os.mkdir(targetFolder)
    else:
        targetFolder = os.path.dirname(os.path.abspath(__file__))

    try:
        print("Загружаем файлы программы...\n")
        url = "https://github.com/antorix/Rocket-Ministry/archive/refs/heads/master.zip"
        file = "files.zip"
        urllib.request.urlretrieve(url, file)
        zip = ZipFile(file, "r")
        zip.extractall("")
        zip.close()
        downloadedFolder = "Rocket-Ministry-master"

        for file_name in os.listdir(downloadedFolder):
            source = downloadedFolder + "\\" + file_name
            destination = targetFolder + "\\" + file_name
            if os.path.isfile(source):
                move(source, destination)
        os.remove(file)
        rmtree(downloadedFolder)
    except:
        print("Не удалось загрузить файлы Rocket Ministry. Проверьте подключение к Интернету. Также вероятно отсутствие административных прав на запись в данную папку - тогда просто перенесите этот файл в местоположение собственной учетной записи, например на рабочий стол.")
        input()
        return

    try:
        print("Устанавливаем шрифт...\n")
        #os.startfile(targetFolder + "\install_fonts.vbs")
    except:
        os.startfile(targetFolder + "\LiberationMono-Regular.ttf")  # попытка установить шрифт напрямую

    try:
        print("Создаем ярлыки на рабочем столе и в списке установленных программ...\n")
        os.startfile(targetFolder + "\create_shortcut.vbs")
    except:
        pass

    if os.path.exists("install-установка.exe"):
        print("Удаляем установщик Python...\n")
        os.remove("install-установка.exe")
    if os.path.exists("unattend.xml"):
        os.remove("unattend.xml")

    print("Установка завершена! Кликните по иконке на рабочем столе. Это окно можно закрыть.")
    input()

install(desktop=True)