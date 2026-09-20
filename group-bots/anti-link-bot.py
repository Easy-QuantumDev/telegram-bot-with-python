import telebot
token = 'TOKEN'
bot = telebot.TeleBot(token)

def is_admin(msg):
    user = bot.get_chat_member(msg.chat.id,msg.from_user.id)
    return user.status in [ "administrator","creator"]



@bot.message_handler(func=lambda msg :(
    msg.text is not None and not  msg.text.startswith("/")
    
))
def anti_link(msg):
    if is_admin(msg.chat.id,msg.from_user.id):
        return    
    text = msg.text.lower()
    link_words = [
        "http://",
        "https://",
        "www.",
        "t.me/",
        "telegram.me/"
    ]
    has_link = any(link in text
                   for link in link_words)
    if not has_link:
        return
    try:
        bot.delete_message(msg.chat.id,msg.message.id)

    except Exception:
        pass     