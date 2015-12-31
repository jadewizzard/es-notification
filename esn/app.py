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


class Conky(object):
        """
        Класс для управления монитором Conky
        содержит базовые методы проверки
        и инициализации Conky
        """

        def check(self):
            if os.path.exists("/etc/conky/conky.conf"):
                return True

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

                if self.distribution == "debian":
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

    def check(self):
        access_token = self.get_token_from_config()
        if access_token:
            return True

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
                                "client_id="+str(self.app_id)+""
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
                                    "client_id="+str(self.app_id)+
                                    "&client_secret="+self.app_key+
                                    "&redirect_uri=https://oauth.vk.com/blank.html"
                                    "&code="+code+"")

                access_token = json.loads(r.text)["access_token"]
                if access_token:
                    print("Готово...")
                    # print(self.access_token) # debug info

                    self.write_config(access_token)
                    # записываем данные о подключение в конфигурационный файл
            else:
                print("Вы не ввели код, приложение будет закрыто.")

    def get_unread_message(self):
        access_token = self.get_token_from_config()
        r = requests.get("https://api.vk.com/method/messages.getDialogs?"
                         "&access_token="+access_token+""
                         "&unread=1"
                         "&v=5.14").text # получаем ответ от сервера в JSON формате
        print(json.loads(r)["response"]["count"])

    def get_token_from_config(self):
        f = open("config")
        config_array = json.loads(f.read())
        return config_array["vk"]["access_token"]

    def write_config(self, access_token):
        f = open("config")
        config_array = json.loads(f.read())
        # получаем массив с конфигом
        config_array["vk"]["access_token"] = access_token
        # создаем новый массив в с конфигом
        json_conf = json.dumps(config_array)
        # формируем json строку из массива с конфигом
        f = open("config", "w")
        f.write(json_conf)
        # записываем токен в конфиг

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

    def check(self):
        config_array = self.get_data_from_config()
        if config_array["access_token"]:
            r = requests.get("https://www.googleapis.com/gmail/v1/users/jadewizzard@gmail.com/threads?"
                             "q=is:unread&"
                             "access_token="+config_array["access_token"]+"")
            response_array = json.loads(r.text)

            if "threads" in response_array:
                return True
            else:
                self.get_new_token(config_array["refresh_token"])
                # пересоздаём токен
                return True
        else:
            return False


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

                if self.access_token and self.refresh_token:
                    self.write_config(self.access_token, self.refresh_token, "new")
                    # записываем полученные значения в конфиг

    def get_unread_message(self):
        thread_counter = 0 # счётчик для кол-ва писем
        config_array = self.get_data_from_config()
        # массив с кофигами
        if not self.next_page_token:
            """
            изначально нам не нужен токен для перехода на следующую страницу,
            поэтому совершаем 1 запрос без него, а последующе с ним (если токен есть)
            """
            r = requests.get("https://www.googleapis.com/gmail/v1/users/jadewizzard@gmail.com/threads?"
                             "q=is:unread&"
                             "access_token="+config_array["access_token"]+"")
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
                                 "pageToken="+self.next_page_token+"&"
                                 "access_token="+config_array["access_token"]+"")
                response_array = json.loads(r.text)

                for thread in response_array["threads"]:
                    if thread["id"]:
                        thread_counter = thread_counter + 1

                if "nextPageToken" in response_array:
                    self.next_page_token = response_array["nextPageToken"]
                else:
                    break

        print(thread_counter) # выводим кол-во непрочитанных сообщений

    def get_new_token(self, refresh_token):
        """
        Функция для обновления токена по refresh token
        """
        # получаем access token
        r = requests.post("https://www.googleapis.com/oauth2/v4/token",
                          data={"client_id": self.client_id,
                                "client_secret": self.client_secret,
                                "refresh_token": refresh_token,
                                "grant_type": "refresh_token"})
        response_array = json.loads(r.text)
        print(response_array)
        self.access_token = response_array["access_token"]
        # self.refresh_token = response_array["refresh_token"]

        if self.access_token:
            self.write_config(self.access_token)
            # записываем полученные значения в конфиг

    def get_data_from_config(self):
        f = open("config")
        config_array = json.loads(f.read())
        return config_array["gmail"]

    def write_config(self, access_token, refresh_token=None, write_type=None):
        f = open("config")
        config_array = json.loads(f.read())
        # получим массив с конфигом
        config_array["gmail"]["access_token"] = access_token
        
        if write_type == "new":
            # записываем refresh token только в том случае
            # если токена в конфиге не существует
            # (т.е пользователь небыл авторизован
            # или конфиг был испорчен.)
            config_array["gmail"]["refresh_token"] = refresh_token

        # запишем новые значения в массив
        json_config = json.dumps(config_array)
        f = open("config", "w")
        f.write(json_config)
        # записываем измнения в файл конфигурации