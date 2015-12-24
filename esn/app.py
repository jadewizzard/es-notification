# -*- coding: utf-8 -*-
"""
Данный файл содержит в себе все классы и функции,
для работы модуля ES-Notification.

========================================================
ES Notification модул для системного монитора Conky,
который предоставляет возможность выводить кол-во
непрочитанных сообщений / писем в популярных сервисах.

На данный момент поддерживаются следующие сервисы:
 - VK.com
В планах реализовать поддержку:
 - Telegramm
 - Gmail
 - Yandex.Mail

Автор модуля - Дмитрий Буряков
"""

import os
import webbrowser
import time
import requests
import json

class InitialCheck(object):
    """
    Проверка и инициализация модуля,
    а также связанных с модулем приложений
    """

    def __init__(self):
        self.conky_status = False
        self.vk_status = True # debug

        self.vk_manager = VKontakte()
        self.conky_manager = Conky()

    def conky(self):
        """
        Если есть файл conky.conf, то скорее всего
        conky на ПК установлен, иначе предлагаем установить.
        """
        if os.path.exists("/etc/conky/conky.conf"):
            return True
        else:
            self.conky_manager.install()

    def vk(self):
        if self.vk_status:
            return True # тесты!
        else:
            self.vk_manager.install()


class Conky(object):
        """
        Класс для управления монитором Conky
        содержит базовые методы проверки
        и инициализации Conky
        """

        def install(self):
            """
            Функция определит дистриубтив и пакетную
            систему дистрибутива и предложит установить
            conky.
            """
            print("Кажется у вас не установлен монитор Conky, желаете установить?")
            act = raw_input("y/N: ")

            if act == "y":
                self.distribution = os.uname()[1] # определям дистриубутив пользователя

                if(self.distribution == "debian"):
                    # устанавливаем conky в deb-подобных ситсемах
                    os.system("sudo apt-get install conky")


class VKontakte(object):
    """
    Класс для базового управления сервисом VK,
    для связи с API VK и вывода информации от VK
    """

    def __init__(self):
        self.access_token = None
        self.app_id = 5199621
        self.app_key = "PF3XLgWZBWp417MXLmrf"
        self.config_array = {}

    def install(self):
        print("===================")
        print("Настройка ВКонтакте")
        print("===================")
        print("Через несколько секунд в вашем браузере будет открыто новое окно "
              "скопируйте параметр code из адесной строки и передайте программе.")
        print("1) Хорошо")
        print("2) Я не знаю, что мне делать (подробный мануал)")
        print("3) Выход")

        act = input("Выберете действие: ")

        if act == 1:
            # установка ВКонтакте
            time.sleep(3) # задержка перед открытием браузера
            webbrowser.open_new("https://oauth.vk.com/authorize?"
                                "client_id="+ str(self.app_id) +
                                "&display=page&redirect_uri="
                                "https://oauth.vk.com/blank.html"
                                "&scope=messages,offline&response_type=code")

            # Следующие строки нужны для того, что бы
            # предотвратить сливание ввода и сообщения
            # от модуля webbrowser об открытие новой вкладки
            time.sleep(1)
            print("\n")

            code = raw_input("Код: ")

            if code:
                print("Код принят")
                print("==========")
                print("Ожидайте...")

                src = requests.get("https://oauth.vk.com/access_token?"
                                    "client_id="+ str(self.app_id) +
                                    "&client_secret="+ self.app_key +
                                    "&redirect_uri=https://oauth.vk.com/blank.html"
                                    "&code="+ code +"")

                self.access_token = json.loads(src.text)["access_token"]
                if self.access_token:
                    print("Готово...")
                    print(self.access_token) # debug info

                    self.config_array = {"vk": {"access_token": self.access_token}} # массив с кофигурацией
            else:
                print("Вы не ввели код, приложение будет закрыто.")


    def getUnreadMessage(self):
        src = requests.get("https://api.vk.com/method/messages.getDialogs?"
                           "&access_token=71be8543f00c7068e47686600c05bdfc8825895db1503f63430fec9267c4482a85bc45e3b71e3bd46df71"
                           "&unread=1"
                           "&v=5.14").text # получаем ответ от сервера в JSON формате
        print(json.loads(src)["response"]["count"])
