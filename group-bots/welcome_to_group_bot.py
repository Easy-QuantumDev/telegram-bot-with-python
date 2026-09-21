import telebot
TOKEN = 'your token'
bot = telebot.TeleBot(TOKEN)
@bot.message_handler(content_types=['new_chat_members'])
def welcome(msg):
    for user in msg.new_chat_members:
        if user.username:
            username = f'@{user.username}'\
        
        else:
        
            username = user.first_name
        bot.send_message(msg.chat.id,
            f"""
👋 خوش آمدی {username}!

🎉 به گروه ما خوش اومدی.

📜 قبل از فعالیت، حتماً قوانین گروه رو بخون.

🔹 برای مشاهده قوانین:
/rules
"""
        )
            