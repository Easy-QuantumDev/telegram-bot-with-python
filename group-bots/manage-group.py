import telebot
from telebot.types import ChatPermissions
from datetime import datetime, timedelta


TOKEN = "YOUR_BOT_TOKEN"


bad_words = [
    "کصکش",
    "کونی",
    "جاکش",
    "کیری",
    "کیر",
]


warnings = {}


bot = telebot.TeleBot(TOKEN)


def is_admin(chat_id, user_id):

    member = bot.get_chat_member(
        chat_id=chat_id,
        user_id=user_id
    )

    return member.status in [
        "administrator",
        "creator"
    ]


def add_warning(chat_id, user_id):

    key = (chat_id, user_id)

    if key not in warnings:
        warnings[key] = 0

    warnings[key] += 1

    return warnings[key]


def get_target_user(msg):

    if not msg.reply_to_message:
        bot.reply_to(
            msg,
            "❌ باید روی پیام کاربر Reply کنید."
        )
        return None

    return msg.reply_to_message.from_user


@bot.message_handler(commands=["start"])
def start(message):

    bot.reply_to(
        message,
        "🤖 سلام!\n\n"
        "من ربات مدیریت گروه هستم.\n\n"
        "📜 برای مشاهده قوانین:\n"
        "/rules"
    )


@bot.message_handler(commands=["rules"])
def rules(message):

    text = """
📜 قوانین گروه

1️⃣ احترام به سایر اعضا
2️⃣ ارسال اسپم ممنوع
3️⃣ تبلیغات بدون اجازه ممنوع
4️⃣ ارسال لینک ممنوع
5️⃣ محتوای نامناسب ممنوع

⚠️ رعایت نکردن قوانین باعث اخطار یا محدودیت کاربر می‌شود.
"""

    bot.reply_to(message, text)


@bot.message_handler(content_types=["new_chat_members"])
def welcome_to_new_member(message):

    for user in message.new_chat_members:

        firstname = user.first_name

        if user.username:
            username_text = f"@{user.username}"
        else:
            username_text = firstname

        bot.send_message(
            message.chat.id,
            f"👋 خوش آمدی {username_text}!\n\n"
            f"📜 لطفاً قوانین گروه را مطالعه کن:\n"
            f"/rules"
        )


@bot.message_handler(
    func=lambda message: (
        message.text is not None
        and not message.text.startswith("/")
    )
)
def bad_word_finder(message):

    if is_admin(
        message.chat.id,
        message.from_user.id
    ):
        return

    text = message.text.lower()

    for bad_word in bad_words:

        if bad_word in text:

            try:
                bot.delete_message(
                    message.chat.id,
                    message.message_id
                )
            except Exception:
                pass

            warning_count = add_warning(
                message.chat.id,
                message.from_user.id
            )

            if warning_count < 3:

                bot.send_message(
                    message.chat.id,
                    f"""
⚠️ پیام حذف شد.

👤 کاربر:
{message.from_user.first_name}

🚫 دلیل:
استفاده از کلمات نامناسب

⚠️ Warning:
{warning_count}/3
"""
                )

            else:

                until_date = (
                    datetime.now()
                    + timedelta(minutes=10)
                )

                try:

                    bot.restrict_chat_member(
                        chat_id=message.chat.id,
                        user_id=message.from_user.id,
                        permissions=ChatPermissions(
                            can_send_messages=False
                        ),
                        until_date=until_date
                    )

                    bot.send_message(
                        message.chat.id,
                        f"""
🚫 پیام {message.from_user.first_name} حذف شد.

⚠️ Warning: 3/3

🔇 کاربر به مدت 10 دقیقه Mute شد.
"""
                    )

                    warnings[
                        (message.chat.id, message.from_user.id)
                    ] = 0

                except Exception as error:

                    print("Mute Error:", error)

            break


@bot.message_handler(commands=["mute"])
def mute_user(msg):

    if not is_admin(
        msg.chat.id,
        msg.from_user.id
    ):
        bot.reply_to(
            msg,
            "❌ فقط ادمین‌ها می‌توانند از این دستور استفاده کنند."
        )
        return

    target_user = get_target_user(msg)

    if target_user is None:
        return

    if is_admin(
        msg.chat.id,
        target_user.id
    ):
        bot.reply_to(
            msg,
            "❌ نمی‌توانی یک ادمین را Mute کنی."
        )
        return

    parts = msg.text.split()

    if len(parts) != 2:
        bot.reply_to(
            msg,
            "❌ نحوه استفاده:\n\n"
            "/mute 10\n\n"
            "عدد بر اساس دقیقه است."
        )
        return

    try:

        minutes = int(parts[1])

    except ValueError:

        bot.reply_to(
            msg,
            "❌ مدت زمان باید عدد باشد."
        )
        return

    if minutes <= 0:

        bot.reply_to(
            msg,
            "❌ مدت زمان باید بیشتر از صفر باشد."
        )
        return

    until_date = (
        datetime.now()
        + timedelta(minutes=minutes)
    )

    try:

        bot.restrict_chat_member(
            msg.chat.id,
            target_user.id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_other_messages=False
            ),
            until_date=until_date
        )

        bot.reply_to(
            msg,
            f"🔇 کاربر {target_user.first_name} "
            f"به مدت {minutes} دقیقه Mute شد."
        )

    except Exception as error:

        print("Mute Error:", error)

        bot.reply_to(
            msg,
            "❌ نتوانستم کاربر را Mute کنم."
        )


@bot.message_handler(commands=["unmute"])
def unmute_user(msg):

    if not is_admin(
        msg.chat.id,
        msg.from_user.id
    ):
        bot.reply_to(
            msg,
            "❌ فقط ادمین‌ها می‌توانند از این دستور استفاده کنند."
        )
        return

    target_user = get_target_user(msg)

    if target_user is None:
        return

    try:

        bot.restrict_chat_member(
            msg.chat.id,
            target_user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )

        bot.reply_to(
            msg,
            f"🔊 کاربر {target_user.first_name} از Mute خارج شد."
        )

    except Exception as error:

        print("Unmute Error:", error)

        bot.reply_to(
            msg,
            "❌ نتوانستم کاربر را Unmute کنم."
        )


@bot.message_handler(commands=["ban"])
def ban_user(msg):

    if not is_admin(
        msg.chat.id,
        msg.from_user.id
    ):
        bot.reply_to(
            msg,
            "❌ فقط ادمین‌ها می‌توانند از این دستور استفاده کنند."
        )
        return

    target_user = get_target_user(msg)

    if target_user is None:
        return

    if is_admin(
        msg.chat.id,
        target_user.id
    ):
        bot.reply_to(
            msg,
            "❌ نمی‌توانی یک ادمین را Ban کنی."
        )
        return

    try:

        bot.ban_chat_member(
            msg.chat.id,
            target_user.id
        )

        bot.reply_to(
            msg,
            f"🚫 کاربر {target_user.first_name} Ban شد."
        )

    except Exception as error:

        print("Ban Error:", error)

        bot.reply_to(
            msg,
            "❌ نتوانستم کاربر را Ban کنم."
        )


@bot.message_handler(commands=["unban"])
def unban_user(msg):

    if not is_admin(
        msg.chat.id,
        msg.from_user.id
    ):
        bot.reply_to(
            msg,
            "❌ فقط ادمین‌ها می‌توانند از این دستور استفاده کنند."
        )
        return

    parts = msg.text.split()

    if len(parts) != 2:
        bot.reply_to(
            msg,
            "❌ نحوه استفاده:\n\n"
            "/unban USER_ID"
        )
        return

    try:

        user_id = int(parts[1])

    except ValueError:

        bot.reply_to(
            msg,
            "❌ User ID باید عدد باشد."
        )
        return

    try:

        bot.unban_chat_member(
            msg.chat.id,
            user_id=user_id
        )

        bot.reply_to(
            msg,
            f"🔓 کاربر با ID `{user_id}` از Ban خارج شد.",
            parse_mode="Markdown"
        )

    except Exception as error:

        print("Unban Error:", error)

        bot.reply_to(
            msg,
            "❌ نتوانستم کاربر را Unban کنم."
        )


print("🤖 Bot is running...")

bot.infinity_polling()