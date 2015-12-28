# -*- coding: utf-8 -*-
"""
Главный файл модуля, который выводит информацию
непосредственно в монитор Conky
"""

import app
import sys

check = app.InitialCheck()
vk = app.VKontakte()
gmail = app.GMail()

#if 1 in sys.argv:
if sys.argv[1] == "-vk":
    if check.vk():
        vk.get_unread_message()

if sys.argv[1] == "-gmail":
    gmail.get_unread_message()