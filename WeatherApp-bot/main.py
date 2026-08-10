import os
import requests
import telebot



city = "tehran"
url = "https://geocoding-api.open-meteo.com/v1/search"
params = {
    "name": city,
    "count": 1,
    "language": "en",
    "format": "json"
}

response = requests.get(url,params)
data = response.json()
print(data)


# bot = telebot.TeleBot("YOUR TOKEN")
#
#
#     @bot.message_handler(commands=['start'])
#     def send_welcome(msg):
#         bot.reply_to(msg,'')