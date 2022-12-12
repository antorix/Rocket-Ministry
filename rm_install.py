import os
from os.path import expanduser
import urllib.request
from zipfile import ZipFile
from shutil import move, rmtree

def install(standalone):

    targetFolder = expanduser("~")
    if os.name=="nt":
        targetFolder += "/AppData/Local/Programs"

    print("Установка Rocket Ministry. Не закрывайте это окно!\n")

    if standalone==True: # если установщик скачан и запущен отдельно – создаем папку в выбранном месте
        try:
            from tkinter import messagebox
            response = messagebox.askyesnocancel(
                "Установка Rocket Ministry",
                "Установить программу в пользовательскую папку программ (рекомендуется)?\n\nВыберите «Нет», если хотите выбрать папку вручную."
            )
        except:
            print("Графическая библиотека tkinter не найдена, программа будет установлена в папке по умолчанию.\n")
        else:
            if response==None: # пользователь не выбрал папку, выходим
                return
            elif response==False:
                from tkinter import filedialog
                targetFolder = filedialog.askdirectory()
        if os.name=="nt":
            targetFolder += "/Rocket Ministry"
        else:
            targetFolder += "/RocketMinistry"
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

    print("Загружаем компоненты для Windows...")
    from subprocess import check_call
    from sys import executable
    check_call([executable, '-m', 'pip', 'install', 'kivy'])
    check_call([executable, '-m', 'pip', 'install', 'python-docx'])
    check_call([executable, '-m', 'pip', 'install', 'docx'])

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

    if standalone==False: # файл запускался из архива
        print("Установка завершена. Поехали!\n\n=============================\n")
    else:
        if os.name=="nt":
            try:
                messagebox.showinfo(
                    "Установка Rocket Ministry",
                    "Установка завершена. Запустите программу, кликнув по ярлыку на рабочем столе!"
                )
            except:
                print("Установка завершена. Запустите программу, кликнув по ярлыку на рабочем столе!")
        elif os.name=="posix":
            print("Установка завершена. Откройте терминал в папке программы и введите:\n\npython3 main.py\n\nДанное окно можно закрыть.")
            input()
        else:
            print("Установка завершена. Данное окно можно закрыть.")
            input()

if __name__ == "__main__":
    install(standalone=True)
