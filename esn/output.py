# -*- coding: utf-8 -*-
"""
Главный файл модуля, который выводит информацию
непосредственно в монитор Conky
"""

import app
import sys

conky = app.Conky()
vk = app.VKontakte()
gmail = app.GMail()

if conky.check():
    if sys.argv[1] == "-vk":
        if vk.check():
            vk.get_unread_message()
        else:
            print("Нет соеденения с VK")
            print("Запустите файл settings.py")
            print("Для настройки VK")

    if sys.argv[1] == "-gmail":
        if gmail.check():
            gmail.get_unread_message()
        else:
            print("Нет соеденения с GMail")
            print("Запустите файл settings.py")
            print("Для настройки GMail")
            gmail.authorization()
            # debug
else:
    conky.install()
