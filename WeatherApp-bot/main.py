import requests
import telebot
import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def welcome(msg):
    bot.send_message(
        msg.chat.id,
        """
<b>🌤️ Welcome to Weather Bot!</b>

I can show you the current weather of any city.

🌍 Use /weather to check the weather.

🚀 Let's get started!
""",
        parse_mode="HTML"
    )

@bot.message_handler(commands=['weather'])
def weather(msg):
    sent_msg = bot.send_message(msg.chat.id,'please enter your city :')
    bot.register_next_step_handler(sent_msg,get_weather)
WEATHER_CODES = {
    0: "☀️ Clear sky",

    1: "🌤️ Mainly clear",
    2: "⛅ Partly cloudy",
    3: "☁️ Overcast",

    45: "🌫️ Fog",
    48: "🌫️ Depositing rime fog",

    51: "🌦️ Light drizzle",
    53: "🌦️ Moderate drizzle",
    55: "🌧️ Dense drizzle",

    61: "🌦️ Slight rain",
    63: "🌧️ Moderate rain",
    65: "🌧️ Heavy rain",

    71: "🌨️ Slight snow",
    73: "❄️ Moderate snow",
    75: "❄️ Heavy snow",

    80: "🌦️ Slight rain showers",
    81: "🌧️ Moderate rain showers",
    82: "🌧️ Violent rain showers",

    95: "⛈️ Thunderstorm",

    96: "⛈️ Thunderstorm with hail",
    99: "⛈️ Thunderstorm with heavy hail"
}

def get_weather(msg):
    city = msg.text.strip()
    try:

        url = 'https://geocoding-api.open-meteo.com/v1/search'
        params = {
            'name':city,
            "count":1,
            'language':'en',
            'format':'json'

        }
        response = requests.get(url,params)
        data  = response.json()
        if 'results' not in data or not data['results']:
            bot.send_message(msg.chat.id, f"❌ I couldn't find <b>{city}</b>.", parse_mode="HTML")
            return

        result = data['results'][0]
        latitude = result['latitude']
        longitude = result["longitude"]

        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "timezone": "auto"
        }
        weather_response = requests.get(weather_url,weather_params)
        weather_data = weather_response.json()

        current = weather_data["current"]

        temperature = current["temperature_2m"]

        humidity = current["relative_humidity_2m"]

        wind_speed = current["wind_speed_10m"]

        weather_code = current["weather_code"]

        weather_status = WEATHER_CODES.get(
            weather_code,
            "❓ Unknown weather"
        )

        bot.send_message(msg.chat.id,    f"""
    🌤️ <b>Weather Report</b>
    
    📍 City: {city}
    
    🌡️ Temperature: {temperature}°C
    
    💧 Humidity: {humidity}%
    
    🌬️ Wind Speed: {wind_speed} km/h
    
    ☁️ Weather Code: {weather_status}
    """,
        parse_mode="HTML")
    except requests.RequestException:
        bot.send_message(msg.chat.id, "⚠️ Weather service is currently unavailable.")

bot.infinity_polling()

