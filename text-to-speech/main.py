import telebot
from gtts import gTTS
bot = telebot.TeleBot("Your Token")
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(message.chat.id,  text="""
    
<b>🎙️ Welcome to Text-to-Speech Bot!</b>

✨ Turn your text into <b>natural-sounding speech</b> in seconds.

📝 Simply send me any text, and I'll convert it into <i>audio</i> for you.

🚀 <b>Let's get started! for start send (/voice)</b>
    


    """,parse_mode="html")


@bot.message_handler(commands=["voice"])

def text_to_speech(message):
    msg = bot.send_message(message.chat.id,"please send me a text to convert to speech")
    bot.register_next_step_handler(msg,conver_to_voice)

def conver_to_voice(message):
    text = message.text
    speech = gTTS(text, lang='en')
    speech.save("voice.mp3")
    with open("voice.mp3","rb") as voice :
        bot.send_voice(message.chat.id, voice=voice, caption="your speech is ready thanks to choose me :)")

bot.infinity_polling()
