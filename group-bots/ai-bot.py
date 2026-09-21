import os
import telebot
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
token = os.getenv("BOT_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(token)

client = OpenAI(
    api_key=openai_api_key
)
@bot.message_handler(commands=['ai'])
def ai_command(msg):
    question = msg.text.replace('/ai',"",1).strip()
    if not question:
        
        bot.reply_to(
            msg,
            "🧠 مثال:\n\n"
            "/ai پایتون چیست؟"
        )
        return
    try:
        response = client.responses.create(model='gpt-5.4-mini',input=question)
        answer = response.output_text
        bot.reply_to(msg,f"🧠 {answer}")
    except ValueError :
        
        bot.reply_to(
            msg,
            "❌ در دریافت پاسخ مشکلی پیش آمد."
        )    
        
bot.infinity_polling()    