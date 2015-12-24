# -*- coding: utf-8 -*-
"""
Главный файл модуля, который выводит информацию
непосредственно в монитор Conky
"""

import app

check = app.InitialCheck()
vk = app.VKontakte()

if check.conky():
    if check.vk():
        vk.getUnreadMessage()