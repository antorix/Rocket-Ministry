import os
import urllib.request
from zipfile import ZipFile
from shutil import move, rmtree
from tkinter import filedialog

def install(desktop):

    print("Установка Rocket Ministry. Не закрывайте это окно!\n")

    if desktop==True: # если установщик скачан и запущен отдельно – создаем папку в выбранном месте
        print("Выберите путь, в котором будет создана папка Rocket Ministry с файлами программы.\n")
        targetFolder = filedialog.askdirectory()
        if targetFolder=="": # пользователь не выбрал папку, выходим
            return
        targetFolder += "/Rocket Ministry"
        print("Создаем папку %s...\n" % targetFolder)
        if not os.path.exists(targetFolder):
            os.mkdir(targetFolder)
    else: # если установщик скачан в архиве с дистрибутивом Python – кладем все файлы локально
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
            source = downloadedFolder + "/" + file_name
            destination = targetFolder + "/" + file_name
            if os.path.isfile(source):
                move(source, destination)
        os.remove(file)
        rmtree(downloadedFolder)
    except:
        print("Не удалось загрузить файлы Rocket Ministry. Проверьте подключение к Интернету. Также вероятно отсутствие административных прав на запись в данную папку - тогда просто перенесите этот файл в местоположение собственной учетной записи, например на рабочий стол.")
        input()
        return

    try:
        print("Устанавливаем шрифт, может потребоваться ваше подтверждение...\n")
        os.startfile(targetFolder + "/install_fonts.vbs")
    except:
        os.startfile(targetFolder + "/LiberationMono-Regular.ttf")  # попытка установить шрифт напрямую

    try:
        print("Создаем ярлыки на рабочем столе и в списке установленных программ...\n")
        os.startfile(targetFolder + "/create_shortcuts.vbs")
    except:
        pass

    if os.path.exists("Установить Rocket Ministry.exe"):
        print("Удаляем установщик Python...\n")
        os.remove("Установить Rocket Ministry.exe")
    if os.path.exists("unattend.xml"):
        os.remove("unattend.xml")

    print("Установка завершена. Поехали!\n\n=============================\n")

if __name__ == "__main__":
    install(desktop=True)