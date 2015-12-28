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
 - Telegram
 - Gmail
 - Yandex.Mail

TO-DO
 - Разделить методы установки сервиса
   и метод авторизации в сервисе.
 - добавить поддержку Telegram

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
            self.vk_manager.authorization()


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

    def authorization(self):
        print("=====================")
        print("Авторизация ВКонтакте")
        print("=====================")
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

            code = raw_input("Код: ") # запрашиваем код для авторизации

            if code:
                print("Код принят")
                print("==========")
                print("Ожидайте...")

                r = requests.get("https://oauth.vk.com/access_token?"
                                    "client_id="+ str(self.app_id) +
                                    "&client_secret="+ self.app_key +
                                    "&redirect_uri=https://oauth.vk.com/blank.html"
                                    "&code="+ code +"")

                self.access_token = json.loads(r.text)["access_token"]
                if self.access_token:
                    print("Готово...")
                    print(self.access_token) # debug info

                    self.config_array = {"vk": {"access_token": self.access_token}} # массив с кофигурацией
            else:
                print("Вы не ввели код, приложение будет закрыто.")

    def get_unread_message(self):
        r = requests.get("https://api.vk.com/method/messages.getDialogs?"
                           "&access_token=71be8543f00c7068e47686600c05bdfc8825895db1503f63430fec9267c4482a85bc45e3b71e3bd46df71"
                           "&unread=1"
                           "&v=5.14").text # получаем ответ от сервера в JSON формате
        print(json.loads(r)["response"]["count"])


class GMail(object):

    def __init__(self):
        self.auth_code = None
        self.access_token = None
        self.refresh_token = None
        self.next_page_token = None

        # данные для доступа к GMAIL API
        self.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        self.client_id = "490232413632-h95bfg9ck1ffc1gtoaanue0vakn5acnv.apps.googleusercontent.com"
        self.client_secret = "dHX1alSVj6_Cl3QDPrGPW5bj"

    def authorization(self):
        print("=================")
        print("Авторизация Gmail")
        print("=================")
        print("Через несколько секунд в вашем браузере будет открыто новое окно "
              "вам нужно скопировать код из поля ввода и передать его приложению.")
        print("1) Хорошо")
        print("2) Я не знаю, что мне делать (подробный мануал)")
        print("3) Выход")

        act = input("Выберете действие: ")
        if act == 1:
            auth_uri = "https://accounts.google.com/o/oauth2/v2/auth?" \
                       "scope=https://www.googleapis.com/auth/gmail.readonly&" \
                       "redirect_uri="+ self.redirect_uri +"&" \
                       "response_type=code&" \
                       "client_id="+ self.client_id +""

            time.sleep(3) # задержка перед открытием браузера
            webbrowser.open(auth_uri) # открываем окно авторизации

            time.sleep(1)
            print("\n")
            # для красивого отображения в консоли

            code = raw_input("Код: ") # запрашиваем код

            if code:
                # получаем access token
                r = requests.post("https://www.googleapis.com/oauth2/v4/token",
                                  data={"code": code,
                                        "client_id": self.client_id,
                                        "client_secret": self.client_secret,
                                        "redirect_uri": self.redirect_uri,
                                        "grant_type": "authorization_code",
                                        "access_type": "offline"})
                response_array = json.loads(r.text)
                self.access_token = response_array["access_token"]
                self.refresh_token = response_array["refresh_token"]

                print(self.access_token)

    def get_unread_message(self):
        thread_counter = 0 # счётчик для кол-ва писем
        if not self.next_page_token:
            """
            изначально нам не нужен токен для перехода на следующую страницу,
            поэтому совершаем 1 запрос без него, а последующе с ним (если токен есть)
            """
            r = requests.get("https://www.googleapis.com/gmail/v1/users/jadewizzard@gmail.com/threads?"
                             "q=is:unread&"
                             "access_token=ya29.WALUYXJ3uum_y-6uWkVXb9WbbfrNHuBakPbY2RrVIq9JjkG-AxeU3Nh3EBjF4MP7A-2P")
            response_array = json.loads(r.text)

            for thread in response_array["threads"]:
                if thread["id"]:
                    thread_counter = thread_counter + 1

            if "nextPageToken" in response_array:
                self.next_page_token = response_array["nextPageToken"]

            while self.next_page_token:
                """
                если в полученном выше массиве response_array есть
                next_page_token, значит в ящике есть ещё страницы,
                циклом проходим по ним.
                """
                r = requests.get("https://www.googleapis.com/gmail/v1/users/jadewizzard@gmail.com/threads?"
                                 "q=is:unread&"
                                 "pageToken="+ self.next_page_token +"&"
                                 "access_token=ya29.WALUYXJ3uum_y-6uWkVXb9WbbfrNHuBakPbY2RrVIq9JjkG-AxeU3Nh3EBjF4MP7A-2P")
                response_array = json.loads(r.text)

                for thread in response_array["threads"]:
                    if thread["id"]:
                        thread_counter = thread_counter + 1

                if "nextPageToken" in response_array:
                    self.next_page_token = response_array["nextPageToken"]
                else:
                    break

        print(thread_counter) # выводим кол-во непрочитанных сообщений