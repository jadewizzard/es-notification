# -*- coding: utf-8 -*-
"""
Главный файл модуля, который выводит информацию
непосредственно в монитор Conky
"""

import app
import sys

check = app.InitialCheck()
vk = app.VKontakte()

app_arg = sys.argv[1]
# получаем аргумент переданный программе
# первый аргумент передоваемый программе
# это указание на сервис из которого нужно
# получить кол-во непрочитанных сообщений / писем
# соответственно:
# -vk - Вконтакте
# -tm - Telegramm

if app_arg == "-vk":
    if check.vk():
        vk.getUnreadMessage()