#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Голосовой помощник Trex."""

import datetime  # Работа со временем
import wave  # Создание и чтение аудиофайлов формата .wav
import os  # Работа с файловой системой
import json  # Работа с данными в формате JSON
import webbrowser  # Открытие вкладок браузера
import traceback  # Формирование информации об исключениях
import subprocess  # Запуск новых процессов
import random  # Генератор случайных чисел
from pathlib import Path  # Работа с путями файловой системы
import smtplib  # Работа с почтой

import pyttsx3  # Синтез речи
import speech_recognition as sr  # Распознавание речи online
from vosk import Model, KaldiRecognizer  # Распознавание речи offline
import wikipediaapi  # Доступ к API Википедии
from googletrans import Translator  # Доступ к API Google Translate
from pyowm import OWM  # Доступ к API OpenWeatherMap
from pyowm.utils.config import get_default_config  # Параметры по умолчанию для OWM
from email.mime.multipart import MIMEMultipart  # Создание многочастных сообщений электронной почты
from email.mime.text import MIMEText  # Создание текстовых частей в сообщениях электронной почты
import requests  # Отправка HTTP-запросов и получение ответов от Web-серверов


class bot:
    """Класс ассистента."""

    bot_name_ru = ""
    bot_name_en = ""
    city = ""
    language = ""


class bot_translate:
    """Класс для мультиязычности."""

    with open("translations.json", "r", encoding="UTF-8") as file:  # Подключение к файлу с переводами
        translations = json.load(file)

    def get(self, text: str) -> str:
        if text in self.translations:
            return self.translations[text][trex.language]
        else:
            print(f"Для фразы: {text} нет перевода.")  # Если перевод не найден - ошибка
            return text


def speak(my_bot: bot, text: str) -> None:
    """Воспроизведение речи ассистента."""
    print(f"{my_bot.bot_name_ru} говорит: {text}.")
    engine.say(text)
    engine.runAndWait()


def voice_listening() -> None:
    """Прослушивание голосов, доступных в ОС."""
    i = 0
    for voice in voices:
        engine.setProperty('voice', voices[i].id)
        print('Имя: %s' % voice.name)
        print('ID: ', i)
        speak(trex, "1")
        print("--------------------")
        i = i + 1


def greetings() -> None:
    """Приветственное сообщение при запуске программы."""
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 6:
        speak(trex, f"Доброй ночи! Я - {trex.bot_name_ru}, твой голосовой помощник. Чем могу помочь?")
    elif hour >= 6 and hour < 12:
        speak(trex, f"Доброе утро! Я - {trex.bot_name_ru}, твой голосовой помощник. Чем могу помочь?")
    elif hour >= 12 and hour < 18:
        speak(trex, f"Добрый день! Я - {trex.bot_name_ru}, твой голосовой помощник. Чем могу помочь?")
    else:
        speak(trex, f"Добрый вечер! Я - {trex.bot_name_ru}, твой голосовой помощник. Чем могу помочь?")


def record() -> str:
    """Запись речи."""
    query = ""
    with microphone:
        recognizer.adjust_for_ambient_noise(microphone, duration=1)  # Регулирование уровня окружающего шума
        try:
            print(f"{trex.bot_name_ru} слушает...")
            rec_audio = recognizer.listen(microphone, 5, 5)  # Запись голоса с микрофона
            with open("recorded_speech.wav", "wb") as file:  # Сохранение аудио в файл
                file.write(rec_audio.get_wav_data())
            query = online_recognition()  # Запуск online-распознавания
        except sr.WaitTimeoutError:
            speak(trex, translator.get("Извините, я вас не понял. Повторите, пожалуйста, запрос"))
    return query


def online_recognition() -> str:
    """Online-распознавание речи."""
    query = ""
    try:
        rec_audio = sr.WavFile("recorded_speech.wav")  # Чтение аудиофайла с речью
        with rec_audio as audio:
            content = recognizer.record(audio)
        print(f"{trex.bot_name_ru} распознает речь...")
        query = recognizer.recognize_google(content, language="ru-RU").lower()
    except sr.UnknownValueError:
        pass
    except sr.RequestError:  # При недоступности Интернета - переключение на offline-распознавание
        print(f"{trex.bot_name_ru} не смог подключиться к Интернету. Попытка offline-распознавания...")
        query = offline_recognition()
    return query


def offline_recognition() -> str:
    """Offline-распознавание речи."""
    vosk_model = "vosk-model-ru-0.42"  # Используемая модель Vosk
    query = ""
    try:
        if not os.path.exists(f"models/{vosk_model}"):  # Проверка наличия модели на нужном языке в каталоге приложения
            print(f"ВНИМАНИЕ: Для offline-распознавания необходимо загрузить языковую модель \"{vosk_model}\" с сайта https://alphacephei.com/vosk/models и распаковать в директорию проекта.")
            exit(1)
        audio_file = wave.open("recorded_speech.wav", "rb")
        model = Model(f"models/{vosk_model}")
        offline_recognizer = KaldiRecognizer(model, audio_file.getframerate())
        audio = audio_file.readframes(audio_file.getnframes())
        if len(audio) > 0:
            if offline_recognizer.AcceptWaveform(audio):
                query = offline_recognizer.Result()
                query = json.loads(query)
                query = query["text"]
    except:
        speak(trex, "Извините, я не смог распознать речь. Пожалуйста, повторите запрос")
    return query


def search_wiki(query: str) -> None:
    """
    Поиск по Википедии.

    - поиск страницы по запросу
    - открытие найденной страницы в браузере
    - чтение первых двух предложений
    """
    speak(trex, "Произвожу поиск по Википедии")
    wiki = wikipediaapi.Wikipedia(f"{trex.bot_name_en} ({trex.bot_name_en}@selectel.ru)", "ru")
    query = query.replace("википедия ", "")  # Удаляем ненужные слова запроса
    query = query.replace("википедии ", "")
    query = query.replace("wikipedia ", "")
    wiki_page = wiki.page(query)
    try:
        if wiki_page.exists():
            speak(trex, f"Вот что мне удалось найти в Википедии по запросу \"{query}\"")
            webbrowser.open(wiki_page.fullurl)  # Открытие ссылки в браузере
            result = wiki_page.summary.split(".")[:2]  # Выборка двух первых предложений
            speak(trex, result)
        else:
            speak(trex, f"К сожалению, я не смог ничего найти на Википедии по запросу \"{query}\"")
    except:
        speak(trex, "Произошла ошибка работы модуля \"Поиск по Википедии\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return


def search_google(query: str) -> None:
    """
    Поиск в Google.

    - запоминаем фразу
    - удаляем лишнее из запроса
    - открываем браузер и вставляем подготовленную ссылку
    """
    speak(trex, "Произвожу поиск в Google")
    query = query.replace("гугл ", "")  # Удаление ненужных слов в запросе
    query = query.replace("гугле ", "")
    query = query.replace("google ", "")
    try:
        URI = "https://google.com/search?q=" + query
        webbrowser.open(URI)
        speak(trex, f"Вот что мне удалось найти в Google по запросу \"{query}\"")
    except:
        speak(trex, "Произошла ошибка работы модуля \"Поиск в Google\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return


def search_yandex(query: str) -> None:
    """
    Поиск в Яндексе.

    - запоминаем фразу
    - удаляем лишнее из запроса
    - открываем браузер и вставляем подготовленную ссылку
    """
    speak(trex, "Произвожу поиск в Яндексе")
    query = query.replace("яндекс ", "")    # Удаление ненужных слов в запросе
    query = query.replace("yandex ", "")
    try:
        URI = "https://ya.ru/search?text=" + query
        webbrowser.open(URI)
        speak(trex, f"Вот что мне удалось найти в Яндексе по запросу \"{query}\"")
    except:
        speak(trex, "Произошла ошибка работы модуля \"Поиск в Яндексе\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return


def search_youtube(query: str) -> None:
    """Поиск по YouTube."""
    speak(trex, "Произвожу поиск на YouTube")
    query = query.replace("ютуб ", "")  # Удаление ненужных слов в запросе
    query = query.replace("youtube ", "")
    try:
        URI = "https://www.youtube.com/results?search_query=" + query
        webbrowser.open(URI)
        speak(trex, f"Вот что мне удалось найти на YouTube по запросу \"{query}\"")
    except:
        speak(trex, "Произошла ошибка работы модуля \"Поиск на YouTube\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return


def search_rutube(query: str) -> None:
    """Поиск по RuTube."""
    speak(trex, "Произвожу поиск на RuTube")
    query = query.replace("рутуб ", "")  # Удаление ненужных слов в запросе
    query = query.replace("rutube ", "")
    try:
        URI = "https://rutube.ru/search/?query=" + query
        webbrowser.open(URI)
        speak(trex, f"Вот что мне удалось найти на RuTube по запросу \"{query}\"")
    except:
        speak(trex, "Произошла ошибка работы модуля \"Поиск на RuTube\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return


def search_website(query: str) -> None:
    """Открытие веб-сайта."""
    query = query.replace("открой ", "")  # Удаление ненужных слов
    query = query.replace("open ", "")
    speak(trex, f"Произвожу поиск сайта \"{query}\"")
    try:
        URI = "https://www." + query
        webbrowser.open(URI)
        speak(trex, f"Открываю \"{query}\"")
    except:
        speak(trex, "Произошла ошибка работы модуля \"Открыть website\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return


def translate(query: str) -> None:
    """Переводчик."""
    gt = Translator()
    if ("с английского" in query):  # Инициализация переменных для перевода С АНГЛИЙСКОГО
        lang_src = "en"
        lang_dest = "ru"
    elif ("на английский" in query):  # Инициализация переменных для перевода НА АНГЛИЙСКИЙ
        lang_src = "ru"
        lang_dest = "en"
    else:
        speak(trex, "Извините, поддерживается только перевод с английского на русский и наоборот")
        return
    query = query.replace("переведи с английского ", "")  # Удаление ненужных слов в запросе
    query = query.replace("переведи на английский ", "")
    try:
        translate_query = gt.translate(query, src=lang_src, dest=lang_dest)  # Перевод
        speak(trex, translate_query.text)
    except:
        speak(trex, "Произошла ошибка работы модуля \"Переводчик\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return


def get_weather(query: str) -> None:
    """Погода."""
    weather_api_key = [line.strip() for line in open("OpenWeather_key.txt")][0]  # API-ключ
    config_dict = get_default_config()  # Сброс настроек
    config_dict['language'] = 'ru'  # Установка языка
    try:
        open_weather_map = OWM(weather_api_key, config_dict)
        weather_manager = open_weather_map.weather_manager()
        if ("в городе" in query):  # Установка города из запроса
            city = query.split(" ")[-1:]
            city = str(city).strip("[]'")
        else:
            city = trex.city  # Установка города по умолчанию
        observation = weather_manager.weather_at_place(city)
        weather = observation.weather
    except:
        speak(trex, "Произошла ошибка работы модуля \"Погода\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return
    status = weather.detailed_status
    temperature = weather.temperature('celsius')["temp"]
    wind_speed = weather.wind()["speed"]
    pressure = int(weather.pressure["press"] / 1.333)  # Из гПА в мм рт.ст.
    speak(trex, f"В городе {city} {status}")
    speak(trex, f"Температура {str(temperature)} градусов по Цельсию")
    speak(trex, f"Скорость ветра составляет {str(wind_speed)} метров в секунду")
    speak(trex, f"Давление составляет {str(pressure)} миллиметров ртутного столба")


def time() -> None:
    """Время."""
    time_time = datetime.datetime.now().strftime("%H:%M:%S")
    speak(trex, f"Текущее время: {time_time}")


def start_app(query: str) -> None:
    """Запуск приложения."""
    query = query.replace("запусти ", "")
    print(query)
    if ("edge" in query):
        subprocess.run("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe")
    elif ("калькулятор" in query):
        subprocess.run(["start calc"])
    elif ("браузер" in query):
        subprocess.run(["start chrome"])


def play_music() -> None:
    """Запуск музыки."""
    music_dir_name = "C:\\MyMusic"
    music_dir = Path(music_dir_name)
    music = os.listdir(music_dir)
    print(f"В директории \"{music_dir}\" найдены следующие композиции: \n", music)
    music_count = len(list(music_dir.iterdir()))
    print(f"В папке {music_dir} есть {music_count} объектов")
    os.startfile(os.path.join(music_dir, music[random.randint(0, music_count-1)]))


def send_email() -> None:
    """
    Отправка почты.

    - подключение к SMTP-серверу
    - аутентификация с паролем внешних приложений
    - выбор получателя письма (В нашей реализации выбор получателя происходит только из заранее определённого списка.)
    - указание заголовка письма
    - указание текста письма
    - отправка
    """
    try:
        server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
        server.ehlo()
        server.login('email_from@mail.ru', 'password')
        msg = MIMEMultipart()
        msg["From"] = "email_from@mail.ru"
        speak(trex, "Скажите получателя письма")
        query = record()
        if ("руководитель" in query):
            msg["To"] = "email_to1@mail.ru"
        elif ("мама" in query):
            msg["To"] = "email_to2@mail.ru"
        print(f"Получатель письма: {msg["To"]}")
        speak(trex, "Скажите заголовок письма")
        msg["Subject"] = record()
        print(f"Заголовок письма: {msg["Subject"]}")
        speak(trex, "Скажите текст письма")
        text = record()
        print(f"Текст письма: {text}")
        msg.attach(MIMEText(text, "plain"))
        server.sendmail(msg["From"], msg["To"], msg.as_string())
        speak(trex, f"Письмо для {msg["To"]} успешно отправлено")
        server.close()
    except:
        speak(trex, "Произошла ошибка работы модуля \"Отправка электронного письма\". Подробности ошибки выведены в терминал")
        traceback.print_exc()
        return


def billing_selectel():
    """Просмотр баланса Selectel."""
    apikey_selectel = "your_api_key"
    headers = {'X-Token': apikey_selectel}
    response = requests.get('https://api.selectel.ru/v3/balances', headers=headers)
    if response.status_code == 200:
        balance_info = response.json()
        # Проходим по всем типам биллинга и выводим их сумму
        for billing in balance_info['data']['billings']:
            billing_type = billing['billing_type']
            balances_values_sum = billing['balances_values_sum']
            billing_type = str(billing_type).replace("primary", "Основной")
            billing_type = str(billing_type).replace("vpc", "Облачная платформа")
            billing_type = str(billing_type).replace("storage", "Хранилище и CDN")
            billing_type = str(billing_type).replace("vmware", "Облако на базе VMware")
            speak(trex, f"Баланс для типа '{billing_type}': {balances_values_sum/100} рублей")
    else:
        speak(trex, "Не удалось получить информацию о балансе.")


if __name__ == "__main__":
    trex = bot()
    trex.bot_name_ru = "Тирекс"
    trex.bot_name_en = "Trex"
    trex.city = "Москва"
    trex.language = "ru"

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # voice_listening(engine, voices)
    if trex.language == "ru":
        engine.setProperty('voice', voices[0].id)
    elif trex.language == "en":
        engine.setProperty('voice', voices[1].id)

    # Приветствие
    greetings()

    # Инициализация инструментов для ввода и распознавания речи
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # Инициализация объекта класса для мультиязычности
    translator = bot_translate()

    while True:
        query = record()
        # query = "Википедия кошка"
        # query = "Google ЦОД Selectel"
        # query = "Яндекс ЦОД Selectel"
        # query = "YouTube ЦОД Selectel"
        # query = "RuTube ЦОД Selectel"
        # query = "Открой selectel.ru"
        # query = "Переведи с английского i love you"
        # query = "Погода в городе Санкт-Петербурге"
        # query = "Время"
        os.remove("recorded_speech.wav")
        if (query == ""):
            print(f"{trex.bot_name_ru} не распознал речь. Возможно, вы ничего не сказали.")
            print("--------------------")
            continue
        print(f"Вы сказали: {query}.")
        query = query.lower()
        # Вызов функций в соответствии с распознанным запросом
        if ("википедия" in query) or ("википедии" in query) or ("wikipedia" in query):
            search_wiki(query)
        elif ("гугл" in query) or ("google" in query):
            search_google(query)
        elif ("яндекс" in query) or ("yandex" in query):
            search_yandex(query)
        elif ("ютуб" in query) or ("youtube" in query):
            search_youtube(query)
        elif ("рутуб" in query) or ("rutube" in query):
            search_rutube(query)
        elif ("открой" in query) or ("open" in query):
            search_website(query)
        elif ("переведи" in query) or ("перевод" in query) or ("translate" in query):
            translate(query)
        elif ("погода" in query) or ("weather" in query):
            get_weather(query)
        elif ("время" in query) or ("time" in query):
            time()
        elif ("запуск" in query) or ("запусти" in query) or ("start" in query):
            start_app(query)
        elif ("музыка" in query) or ("музыку" in query) or ("music" in query):
            play_music()
        elif ("e-mail" in query) or ("письмо" in query):
            send_email()
        elif ("баланс selectel" in query):
            billing_selectel()
        print("--------------------")
