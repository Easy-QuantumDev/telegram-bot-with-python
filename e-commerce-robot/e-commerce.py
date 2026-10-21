
import os
import sqlite3

import telebot
from telebot import types
from dotenv import load_dotenv


# =========================
# Configuration
# =========================

load_dotenv()

BOT_TOKEN = os.getenv("TOKEN")


if not BOT_TOKEN:
    raise ValueError("TOKEN در فایل .env تنظیم نشده است.")

bot = telebot.TeleBot(BOT_TOKEN)


products_data = [
    {
        "id": 1,
        "name": "iPhone 15",
        "price": 1200,
        "stock": 15,
    },
    {
        "id": 2,
        "name": "MacBook Pro",
        "price": 2500,
        "stock": 8,
    },
    {
        "id": 3,
        "name": "AirPods Pro",
        "price": 250,
        "stock": 20,
    },
]


# =========================
#  database
# =========================

def connect_db():
    connection = sqlite3.connect('shop.db')
    return connection
def init_db():
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS products(id  INTEGER PRIMARY KEY,name TEXT NOT NULL ,price INTEGER NOT NULL,inStock INTEGER  NOT NULL DEFAULT 1)')
    connection.commit()
    connection.close()
def add_product(id,name,price,inStock):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute('INSERT OR IGNORE INTO products (id,name,price,inStock) VALUES (?,?,?,?)',(id,name,price,inStock))
    connection.commit()
    connection.close()

def seed_products():
    for product in products_data:
        add_product(product['id'],product['name'],product['price'],product['stock'])
# =========================

# In-memory database
# =========================
carts = {}
orders = {}


# =========================
# Product helper
# =========================

def get_product(product_id):
    for product in products_data:
        if product["id"] == product_id:
            return product

    return None


# =========================
# Main menu
# =========================

def main_menu():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        "🛍️ محصولات",
        "🛒 سبد خرید",
    )

    keyboard.row(
        "📦 سفارش‌های من",
        "👤 حساب کاربری",
    )

    return keyboard


# =========================
# Show cart
# =========================

def show_cart(chat_id, user_id, message_id=None):
    user_cart = carts.get(user_id, {})

    if not user_cart:
        text = "🛒 سبد خرید شما خالی است."

        if message_id is not None:
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=types.InlineKeyboardMarkup(),
            )
        else:
            bot.send_message(chat_id, text)

        return

    text = "🛒 سبد خرید شما:\n\n"
    total_price = 0

    keyboard = types.InlineKeyboardMarkup()

    for product_id, quantity in user_cart.items():
        product = get_product(product_id)

        if product is None:
            continue

        item_total = product["price"] * quantity
        total_price += item_total

        text += (
            f"📦 {product['name']}\n"
            f"🔢 تعداد: {quantity}\n"
            f"💰 قیمت: ${item_total}\n\n"
        )

        keyboard.row(
            types.InlineKeyboardButton(
                "➕",
                callback_data=f"cart:increase:{product_id}",
            ),
            types.InlineKeyboardButton(
                "➖",
                callback_data=f"cart:decrease:{product_id}",
            ),
            types.InlineKeyboardButton(
                "🗑️",
                callback_data=f"cart:remove:{product_id}",
            ),
        )

    text += "━━━━━━━━━━━━\n"
    text += f"💳 مجموع کل: ${total_price}"

    keyboard.row(
        types.InlineKeyboardButton(
            "✅ ثبت سفارش",
            callback_data="cart:checkout",
        )
    )

    if message_id is not None:
        bot.edit_message_text(
            text,
            chat_id,
            message_id,
            reply_markup=keyboard,
        )
    else:
        bot.send_message(
            chat_id,
            text,
            reply_markup=keyboard,
        )


# =========================
# Start
# =========================

@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(
        message.chat.id,
        "سلام 👋\n"
        "به فروشگاه ما خوش آمدید 🛍️",
        reply_markup=main_menu(),
    )


# =========================
# Product list
# =========================

def build_products_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    for product in products_data:
        button = types.InlineKeyboardButton(
            text=f"{product['name']} - ${product['price']}",
            callback_data=f"product:{product['id']}",
        )

        keyboard.add(button)

    return keyboard


@bot.message_handler(
    func=lambda message: message.text == "🛍️ محصولات"
)
def products(message):
    bot.send_message(
        message.chat.id,
        "🛍️ محصولات فروشگاه:",
        reply_markup=build_products_keyboard(),
    )


# =========================
# Product details
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("product:")
)
def product_callback(call):
    product_id = int(call.data.split(":")[1])
    product = get_product(product_id)

    if product is None:
        bot.answer_callback_query(
            call.id,
            "محصول پیدا نشد.",
            show_alert=True,
        )
        return

    bot.answer_callback_query(call.id)

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "🛒 افزودن به سبد",
            callback_data=f"cart:add:{product_id}",
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🔙 بازگشت به محصولات",
            callback_data="products",
        )
    )

    bot.send_message(
        call.message.chat.id,
        f"📦 {product['name']}\n\n"
        f"💰 قیمت: ${product['price']}\n"
        f"📦 موجودی: {product['stock']} عدد",
        reply_markup=keyboard,
    )


# =========================
# Back to product list
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "products"
)
def back_to_products(call):
    bot.answer_callback_query(call.id)

    bot.edit_message_text(
        "🛍️ محصولات فروشگاه:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=build_products_keyboard(),
    )


# =========================
# Add to cart
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("cart:add:")
)
def add_to_cart_callback(call):
    user_id = call.from_user.id
    product_id = int(call.data.split(":")[2])

    product = get_product(product_id)

    if product is None:
        bot.answer_callback_query(
            call.id,
            "محصول پیدا نشد.",
            show_alert=True,
        )
        return

    user_cart = carts.setdefault(user_id, {})
    current_quantity = user_cart.get(product_id, 0)

    if current_quantity >= product["stock"]:
        bot.answer_callback_query(
            call.id,
            "موجودی این محصول کافی نیست.",
            show_alert=True,
        )
        return

    user_cart[product_id] = current_quantity + 1

    bot.answer_callback_query(
        call.id,
        "✅ محصول به سبد خرید اضافه شد!",
    )


# =========================
# Cart menu
# =========================

@bot.message_handler(
    func=lambda message: message.text == "🛒 سبد خرید"
)
def cart(message):
    show_cart(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
    )


# =========================
# Increase quantity
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("cart:increase:")
)
def increase_product(call):
    user_id = call.from_user.id
    product_id = int(call.data.split(":")[2])

    user_cart = carts.get(user_id, {})
    product = get_product(product_id)

    if product is None or product_id not in user_cart:
        bot.answer_callback_query(
            call.id,
            "محصول در سبد خرید پیدا نشد.",
            show_alert=True,
        )
        return

    if user_cart[product_id] >= product["stock"]:
        bot.answer_callback_query(
            call.id,
            "موجودی این محصول کافی نیست.",
        )
        return

    user_cart[product_id] += 1

    bot.answer_callback_query(
        call.id,
        "✅ تعداد محصول افزایش یافت.",
    )

    show_cart(
        chat_id=call.message.chat.id,
        user_id=user_id,
        message_id=call.message.message_id,
    )


# =========================
# Decrease quantity
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("cart:decrease:")
)
def decrease_product(call):
    user_id = call.from_user.id
    product_id = int(call.data.split(":")[2])

    user_cart = carts.get(user_id, {})
    product = get_product(product_id)

    if product is None or product_id not in user_cart:
        bot.answer_callback_query(
            call.id,
            "محصول در سبد خرید پیدا نشد.",
            show_alert=True,
        )
        return

    if user_cart[product_id] <= 1:
        bot.answer_callback_query(
            call.id,
            "برای حذف کامل محصول از دکمه 🗑️ استفاده کن.",
        )
        return

    user_cart[product_id] -= 1

    bot.answer_callback_query(
        call.id,
        "✅ تعداد محصول کاهش یافت.",
    )

    show_cart(
        chat_id=call.message.chat.id,
        user_id=user_id,
        message_id=call.message.message_id,
    )


# =========================
# Remove product
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("cart:remove:")
)
def remove_product(call):
    user_id = call.from_user.id
    product_id = int(call.data.split(":")[2])

    user_cart = carts.get(user_id, {})
    product = get_product(product_id)

    if product is None or product_id not in user_cart:
        bot.answer_callback_query(
            call.id,
            "محصول در سبد خرید پیدا نشد.",
            show_alert=True,
        )
        return

    del user_cart[product_id]

    bot.answer_callback_query(
        call.id,
        "✅ محصول با موفقیت حذف شد.",
    )

    show_cart(
        chat_id=call.message.chat.id,
        user_id=user_id,
        message_id=call.message.message_id,
    )


# =========================
# Checkout / Create order
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "cart:checkout"
)
def checkout(call):
    user_id = call.from_user.id
    user_cart = carts.get(user_id, {})

    if not user_cart:
        bot.answer_callback_query(
            call.id,
            "سبد خرید خالی است.",
            show_alert=True,
        )
        return

    total_price = 0
    text = "🛍️ محصولات سفارش شما:\n\n"

    # Validate products and stock before creating the order.
    for product_id, quantity in user_cart.items():
        product = get_product(product_id)

        if product is None:
            bot.answer_callback_query(
                call.id,
                "یکی از محصولات دیگر موجود نیست.",
                show_alert=True,
            )
            return

        if quantity <= 0 or quantity > product["stock"]:
            bot.answer_callback_query(
                call.id,
                f"موجودی {product['name']} کافی نیست.",
                show_alert=True,
            )
            return

        item_total = product["price"] * quantity
        total_price += item_total

        text += (
            f"📦 {product['name']}\n"
            f"🔢 تعداد: {quantity}\n"
            f"💰 قیمت این محصول: ${item_total}\n\n"
        )

    text += f"💳 مبلغ نهایی: ${total_price}"

    # Create an independent snapshot of the cart.
    order = {
        "items": user_cart.copy(),
        "total_price": total_price,
        "status": "pending",
    }

    if user_id not in orders:
        orders[user_id] = []

    orders[user_id].append(order)

    # Reduce inventory after the order is saved.
    for product_id, quantity in user_cart.items():
        product = get_product(product_id)
        product["stock"] -= quantity

    # Empty the cart after successful registration.
    carts[user_id] = {}

    bot.answer_callback_query(
        call.id,
        "✅ سفارش با موفقیت ثبت شد!",
    )

    bot.send_message(
        call.message.chat.id,
        "✅ سفارش شما ثبت شد!\n\n" + text,
    )


# =========================
# My orders
# =========================

@bot.message_handler(
    func=lambda message: message.text == "📦 سفارش‌های من"
)
def show_orders(message):
    user_id = message.from_user.id
    user_orders = orders.get(user_id, [])

    if not user_orders:
        bot.send_message(
            message.chat.id,
            "📦 شما هنوز سفارشی ثبت نکرده‌اید.",
        )
        return

    for index, order in enumerate(user_orders, start=1):
        text = f"📦 سفارش شماره {index}\n\n"

        for product_id, quantity in order["items"].items():
            product = get_product(product_id)

            product_name = (
                product["name"]
                if product is not None
                else f"محصول شماره {product_id}"
            )

            text += (
                f"• {product_name}\n"
                f"  تعداد: {quantity}\n"
            )

        text += (
            f"\n💰 مبلغ کل: ${order['total_price']}\n"
            f"📌 وضعیت: {order['status']}"
        )

        bot.send_message(message.chat.id, text)


# =========================
# Account
# =========================

@bot.message_handler(
    func=lambda message: message.text == "👤 حساب کاربری"
)
def account(message):
    bot.send_message(
        message.chat.id,
        "👤 حساب کاربری\n\n"
        f"نام: {message.from_user.first_name}\n"
        f"شناسه کاربری: {message.from_user.id}",
    )


# =========================
# Run bot
# =========================

if __name__ == "__main__":
    print("Bot is running...")
    init_db()
    seed_products()
    bot.infinity_polling()
