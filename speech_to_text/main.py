import telebot
from dotenv import load_dotenv
import speech_recognition as sr
from pydub import AudioSegment

load_dotenv()



bot = telebot.TeleBot("BOT_TOKEN")
@bot.message_handler(commands=['start'])
def welcome(msg):
    bot.send_message(
        msg.chat.id,
        """
🎙️ <b>Speech-to-Text Bot</b>

Send me a voice message and
I'll convert it into text. 📝
""",
        parse_mode="HTML")


@bot.message_handler(content_types=['voice'])
def voice_handler(msg):

    bot.send_message(
        msg.chat.id,
        "⏳ <b>Processing your voice...</b>",
        parse_mode="HTML"
    )
    file_id = msg.voice.file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = bot.download_file(file_path)

    with open('voice.ogg','wb') as voice :
        voice.write(downloaded_file)
    audio = AudioSegment.from_ogg('voice.ogg')
    audio.export('voice.wav',format='wav')

    recognizer = sr.Recognizer()
    with sr.AudioFile('voice.wav') as source:
        audio_data = recognizer.record(source)
    try:
         text = recognizer.recognize_google(
             audio_data,
             language="en-US"
         )

         bot.send_message(
         msg.chat.id,
         f"""
         📝 <b>Transcription:</b>

         {text}
         """,
         parse_mode = "HTML"
    )
    except sr.UnknownValueError:
         bot.send_message(msg.chat.id,'❌ I couldnt understand the audio.')
     except sr.RequestError:
         bot.send_message(msg.chat.id,'⚠️ Speech recognition service is unavailable.')
bot.infinity_polling()

