import telebot
from datetime import timedelta
import datetime



TOKEN = ""
bad_words = [
    'کصکش',
    'کونی',
    'جاکش',
    'کیری',
    'کیر'
    
]

warnings = {}

bot = telebot.TeleBot(TOKEN)



def is_admin(chat_id,user_id):
    
    member = bot.get_chat_member(chat_id=chat_id,user_id=user_id)
    
    return member.status in [
         "administrator",
         "creator"
     ]
    



def add_warning(chat_id,user_id):
  key = (chat_id, user_id)

  if key not in warnings:
      
      warnings[key] = 0

  warnings[key] += 1

  return warnings[key]
    
@bot.message_handler(commands=['start'])
def start(msg):
    
    bot.reply_to(msg,     "🤖 سلام!\n"
        "من ربات مدیریت گروه هستم.\n\n"
        "برای مشاهده قوانین:\n"
        "/rules"
        )
@bot.message_handler(commands=['rules'])
def rules(msg):
    
    text = """
📜 قوانین گروه

1️⃣ احترام به سایر اعضا
2️⃣ ارسال اسپم ممنوع
3️⃣ تبلیغات بدون اجازه ممنوع
4️⃣ ارسال لینک ممنوع
5️⃣ محتوای نامناسب ممنوع

⚠️ رعایت نکردن قوانین باعث اخطار یا محدودیت کاربر می‌شود.
"""
    bot.reply_to(msg, text)

@bot.message_handler(commands=['new_chat_members'])
def welcome_to_new_member(msg):
    for user in msg.new_chat_members:
        firstname = user.first_name
        username = user.username
        if username:
            username_text = f'@{username}'
        else:
            username_text = 'no username'
            
                
    bot.send_message(msg.chat.id,text=f'welcome to the group {firstname}')
        



@bot.message_handler(func=lambda msg:True)
def bad_word_finder(msg):
    for bad_word in bad_words:
        if bad_word in msg.text:
            bot.delete_message(msg.chat.id,msg.message_id)
            warning_count = add_warning(msg.chat.id,msg.from_user.id)
            bot.reply_to(msg,text=f'dont use bad words\nyour warnings : {warning_count}')
            if warning_count < 3:

                bot.send_message(
                    msg.chat.id,
                    f"""
⚠️ پیام شما حذف شد.

🚫 دلیل:
استفاده از کلمات نامناسب

👤 کاربر:
{msg.from_user.first_name}

⚠️ Warning:
{warning_count}/3
"""
                )
            else:
                until_date = datetime.now() + timedelta(
                    minutes=10
                )
            try:
                bot.restrict_chat_member(chat_id=msg.chat.id,user_id=msg.from_user.id,permissions=telebot.types.ChatPermissions(can_send_messages=False,can_send_other_messages=False),until_date=until_date)
                bot.send_message(msg.chat.id,f"""
🚫 پیام {msg.from_user.first_name} حذف شد.

⚠️ Warning: 3/3

🔇 کاربر به مدت 10 دقیقه سایلنت شد.
"""
)
            except ValueError:
                
                pass                              
bot.infinity_polling()

