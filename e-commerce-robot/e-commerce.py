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
DB_NAME = "shop.db"

# فقط برای اولین اجرای دیتابیس استفاده می‌شود.
# INSERT OR IGNORE باعث می‌شود موجودی محصولات موجود بازنویسی نشود.
INITIAL_PRODUCTS = [
    {"id": 1, "name": "iPhone 15", "price": 1200, "stock": 15},
    {"id": 2, "name": "MacBook Pro", "price": 2500, "stock": 8},
    {"id": 3, "name": "AirPods Pro", "price": 250, "stock": 20},
]


# =========================
# Database helpers
# =========================
def connect_db():
    connection = sqlite3.connect(DB_NAME, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    """ساخت جدول‌های موردنیاز فروشگاه."""
    with connect_db() as connection:
        connection.execute("""
                            CREATE TABLE IF NOT EXISTS products (
                                id INTEGER PRIMARY KEY,
                                name TEXT NOT NULL,
                                price INTEGER NOT NULL CHECK(price >= 0),
                                inStock INTEGER NOT NULL DEFAULT 0 CHECK(inStock >= 0)
                            )
                        """)

        connection.execute("""
                            CREATE TABLE IF NOT EXISTS cart_items (
                                user_id INTEGER NOT NULL,
                                product_id INTEGER NOT NULL,
                                quantity INTEGER NOT NULL CHECK(quantity > 0),
                                PRIMARY KEY (user_id, product_id),
                                FOREIGN KEY (product_id) REFERENCES products(id)
                                    ON DELETE CASCADE
                            )
                        """)

        connection.execute("""
                            CREATE TABLE IF NOT EXISTS orders (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                total_price INTEGER NOT NULL CHECK(total_price >= 0),
                                status TEXT NOT NULL DEFAULT 'pending',
                                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                            )
                        """)

        connection.execute("""
                            CREATE TABLE IF NOT EXISTS order_items (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                order_id INTEGER NOT NULL,
                                product_id INTEGER,
                                product_name TEXT NOT NULL,
                                quantity INTEGER NOT NULL CHECK(quantity > 0),
                                unit_price INTEGER NOT NULL CHECK(unit_price >= 0),
                                FOREIGN KEY (order_id) REFERENCES orders(id)
                                    ON DELETE CASCADE,
                                FOREIGN KEY (product_id) REFERENCES products(id)
                                    ON DELETE SET NULL
                            )
                        """)


def seed_products():
    """محصولات اولیه را فقط در صورت نبودن شناسه وارد می‌کند."""
    with connect_db() as connection:
        for product in INITIAL_PRODUCTS:
            connection.execute("""
                                INSERT OR IGNORE INTO products (id, name, price, inStock)
                                VALUES (?, ?, ?, ?)
                            """, (
                product["id"],
                product["name"],
                product["price"],
                product["stock"],
            ))


def get_all_products():
    with connect_db() as connection:
        rows = connection.execute("""
                            SELECT id, name, price, inStock
                            FROM products
                            ORDER BY id
                        """).fetchall()

    return [
        {
            "id": row["id"],
            "name": row["name"],
            "price": row["price"],
            "stock": row["inStock"],
        }
        for row in rows
    ]


def get_product(product_id):
    with connect_db() as connection:
        row = connection.execute("""
                            SELECT id, name, price, inStock
                            FROM products
                            WHERE id = ?
                        """, (product_id,)).fetchone()

    if row is None:
        return None

    return {
        "id": row["id"],
        "name": row["name"],
        "price": row["price"],
        "stock": row["inStock"],
    }


# =========================
# Persistent cart helpers
# =========================
def get_cart(user_id):
    with connect_db() as connection:
        rows = connection.execute("""
                            SELECT product_id, quantity
                            FROM cart_items
                            WHERE user_id = ?
                        """, (user_id,)).fetchall()

    return {row["product_id"]: row["quantity"] for row in rows}


def set_cart_quantity(user_id, product_id, quantity):
    """تعداد محصول در سبد را ثبت می‌کند؛ صفر یعنی حذف."""
    with connect_db() as connection:
        if quantity <= 0:
            connection.execute("""
                                DELETE FROM cart_items
                                WHERE user_id = ? AND product_id = ?
                            """, (user_id, product_id))
        else:
            connection.execute("""
                                INSERT INTO cart_items (user_id, product_id, quantity)
                                VALUES (?, ?, ?)
                                ON CONFLICT(user_id, product_id)
                                DO UPDATE SET quantity = excluded.quantity
                            """, (user_id, product_id, quantity))


def clear_cart(user_id, connection=None):
    if connection is not None:
        connection.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
    else:
        with connect_db() as db:
            db.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))


# =========================
# UI helpers
# =========================
def main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🛍️ محصولات", "🛒 سبد خرید")
    keyboard.row("📦 سفارش‌های من", "👤 حساب کاربری")
    return keyboard


def build_products_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    for product in get_all_products():
        keyboard.add(types.InlineKeyboardButton(
            text=f"{product['name']} - ${product['price']} (موجودی: {product['stock']})",
            callback_data=f"product:{product['id']}",
        ))

    return keyboard


def show_cart(chat_id, user_id, message_id=None):
    user_cart = get_cart(user_id)

    if not user_cart:
        text = "🛒 سبد خرید شما خالی است."
        if message_id is not None:
            try:
                bot.edit_message_text(
                    text, chat_id, message_id,
                    reply_markup=types.InlineKeyboardMarkup(),
                )
            except telebot.apihelper.ApiTelegramException:
                bot.send_message(chat_id, text)
        else:
            bot.send_message(chat_id, text)
        return

    lines = ["🛒 سبد خرید شما:\n"]
    total_price = 0
    keyboard = types.InlineKeyboardMarkup()

    for product_id, quantity in user_cart.items():
        product = get_product(product_id)
        if product is None:
            continue

        item_total = product["price"] * quantity
        total_price += item_total
        lines.append(
            f"📦 {product['name']}\n"
            f"🔢 تعداد: {quantity}\n"
            f"💰 قیمت: ${item_total}\n"
        )
        keyboard.row(
            types.InlineKeyboardButton("➕", callback_data=f"cart:increase:{product_id}"),
            types.InlineKeyboardButton("➖", callback_data=f"cart:decrease:{product_id}"),
            types.InlineKeyboardButton("🗑️", callback_data=f"cart:remove:{product_id}"),
        )

    lines.append(f"━━━━━━━━━━━━\n💳 مجموع کل: ${total_price}")
    keyboard.row(types.InlineKeyboardButton(
        "✅ ثبت سفارش", callback_data="cart:checkout"
    ))

    text = "\n".join(lines)
    if message_id is not None:
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=keyboard)
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(chat_id, text, reply_markup=keyboard)
    else:
        bot.send_message(chat_id, text, reply_markup=keyboard)


# =========================
# Start / product list
# =========================
@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(
        message.chat.id,
        "سلام 👋\nبه فروشگاه ما خوش آمدید 🛍️",
        reply_markup=main_menu(),
    )


@bot.message_handler(func=lambda message: message.text == "🛍️ محصولات")
def products(message):
    bot.send_message(
        message.chat.id,
        "🛍️ محصولات فروشگاه:",
        reply_markup=build_products_keyboard(),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("product:"))
def product_callback(call):
    product_id = int(call.data.split(":")[1])
    product = get_product(product_id)

    if product is None:
        bot.answer_callback_query(call.id, "محصول پیدا نشد.", show_alert=True)
        return

    bot.answer_callback_query(call.id)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
        "🛒 افزودن به سبد", callback_data=f"cart:add:{product_id}"
    ))
    keyboard.add(types.InlineKeyboardButton(
        "🔙 بازگشت به محصولات", callback_data="products"
    ))
    bot.send_message(
        call.message.chat.id,
        f"📦 {product['name']}\n\n"
        f"💰 قیمت: ${product['price']}\n"
        f"📦 موجودی: {product['stock']} عدد",
        reply_markup=keyboard,
    )


@bot.callback_query_handler(func=lambda call: call.data == "products")
def back_to_products(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        "🛍️ محصولات فروشگاه:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=build_products_keyboard(),
    )


# =========================
# Cart actions
# =========================
@bot.callback_query_handler(func=lambda call: call.data.startswith("cart:add:"))
def add_to_cart_callback(call):
    user_id = call.from_user.id
    product_id = int(call.data.split(":")[2])
    product = get_product(product_id)

    if product is None:
        bot.answer_callback_query(call.id, "محصول پیدا نشد.", show_alert=True)
        return

    current_quantity = get_cart(user_id).get(product_id, 0)
    if product["stock"] <= current_quantity:
        bot.answer_callback_query(
            call.id, "موجودی این محصول کافی نیست.", show_alert=True
        )
        return

    set_cart_quantity(user_id, product_id, current_quantity + 1)
    bot.answer_callback_query(call.id, "✅ محصول به سبد خرید اضافه شد!")


@bot.message_handler(func=lambda message: message.text == "🛒 سبد خرید")
def cart(message):
    show_cart(message.chat.id, message.from_user.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cart:increase:"))
def increase_product(call):
    user_id = call.from_user.id
    product_id = int(call.data.split(":")[2])
    user_cart = get_cart(user_id)
    product = get_product(product_id)

    if product is None or product_id not in user_cart:
        bot.answer_callback_query(call.id, "محصول در سبد خرید پیدا نشد.", show_alert=True)
        return

    if user_cart[product_id] >= product["stock"]:
        bot.answer_callback_query(call.id, "موجودی این محصول کافی نیست.", show_alert=True)
        return

    set_cart_quantity(user_id, product_id, user_cart[product_id] + 1)
    bot.answer_callback_query(call.id, "✅ تعداد محصول افزایش یافت.")
    show_cart(call.message.chat.id, user_id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cart:decrease:"))
def decrease_product(call):
    user_id = call.from_user.id
    product_id = int(call.data.split(":")[2])
    user_cart = get_cart(user_id)

    if product_id not in user_cart:
        bot.answer_callback_query(call.id, "محصول در سبد خرید پیدا نشد.", show_alert=True)
        return

    if user_cart[product_id] <= 1:
        bot.answer_callback_query(
            call.id, "برای حذف کامل محصول از دکمه 🗑️ استفاده کن."
        )
        return

    set_cart_quantity(user_id, product_id, user_cart[product_id] - 1)
    bot.answer_callback_query(call.id, "✅ تعداد محصول کاهش یافت.")
    show_cart(call.message.chat.id, user_id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cart:remove:"))
def remove_product(call):
    user_id = call.from_user.id
    product_id = int(call.data.split(":")[2])

    if product_id not in get_cart(user_id):
        bot.answer_callback_query(call.id, "محصول در سبد خرید پیدا نشد.", show_alert=True)
        return

    set_cart_quantity(user_id, product_id, 0)
    bot.answer_callback_query(call.id, "✅ محصول حذف شد.")
    show_cart(call.message.chat.id, user_id, call.message.message_id)


# =========================
# Checkout: order + items + stock in one transaction
# =========================
@bot.callback_query_handler(func=lambda call: call.data == "cart:checkout")
def checkout(call):
    user_id = call.from_user.id
    connection = connect_db()

    try:
        # قفل نوشتن را زودتر می‌گیریم تا دو خرید هم‌زمان موجودی را منفی نکنند.
        connection.execute("BEGIN IMMEDIATE")

        cart_rows = connection.execute("""
                            SELECT ci.product_id, ci.quantity, p.name, p.price, p.inStock
                            FROM cart_items AS ci
                            JOIN products AS p ON p.id = ci.product_id
                            WHERE ci.user_id = ?
                        """, (user_id,)).fetchall()

        if not cart_rows:
            connection.rollback()
            bot.answer_callback_query(call.id, "سبد خرید خالی است.", show_alert=True)
            return

        total_price = 0
        for row in cart_rows:
            if row["quantity"] <= 0 or row["quantity"] > row["inStock"]:
                connection.rollback()
                bot.answer_callback_query(
                    call.id,
                    f"موجودی {row['name']} کافی نیست.",
                    show_alert=True,
                )
                return
            total_price += row["price"] * row["quantity"]

        cursor = connection.execute("""
                            INSERT INTO orders (user_id, total_price, status)
                            VALUES (?, ?, 'pending')
                        """, (user_id, total_price))
        order_id = cursor.lastrowid

        lines = [f"✅ سفارش شماره {order_id} ثبت شد!\n"]
        for row in cart_rows:
            connection.execute("""
                                INSERT INTO order_items
                                    (order_id, product_id, product_name, quantity, unit_price)
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                order_id, row["product_id"], row["name"],
                row["quantity"], row["price"],
            ))

            updated = connection.execute("""
                                UPDATE products
                                SET inStock = inStock - ?
                                WHERE id = ? AND inStock >= ?
                            """, (row["quantity"], row["product_id"], row["quantity"]))

            if updated.rowcount != 1:
                raise ValueError(f"موجودی {row['name']} تغییر کرده است.")

            lines.append(
                f"📦 {row['name']}\n"
                f"🔢 تعداد: {row['quantity']}\n"
                f"💰 قیمت واحد: ${row['price']}\n"
            )

        clear_cart(user_id, connection)
        connection.commit()

        lines.append(f"💳 مبلغ نهایی: ${total_price}\n📌 وضعیت: در انتظار")
        bot.answer_callback_query(call.id, "✅ سفارش با موفقیت ثبت شد!")
        bot.send_message(call.message.chat.id, "\n".join(lines))

    except (sqlite3.Error, ValueError) as error:
        connection.rollback()
        print(f"Checkout database error: {error}")
        bot.answer_callback_query(
            call.id,
            "ثبت سفارش انجام نشد؛ لطفاً دوباره تلاش کن.",
            show_alert=True,
        )
    finally:
        connection.close()


# =========================
# Order history
# =========================
@bot.message_handler(func=lambda message: message.text == "📦 سفارش‌های من")
def show_orders(message):
    user_id = message.from_user.id

    with connect_db() as connection:
        user_orders = connection.execute("""
                            SELECT id, total_price, status, created_at
                            FROM orders
                            WHERE user_id = ?
                            ORDER BY id DESC
                        """, (user_id,)).fetchall()

        if not user_orders:
            bot.send_message(message.chat.id, "📦 شما هنوز سفارشی ثبت نکرده‌اید.")
            return

        for order in user_orders:
            items = connection.execute("""
                                SELECT product_name, quantity, unit_price
                                FROM order_items
                                WHERE order_id = ?
                                ORDER BY id
                            """, (order["id"],)).fetchall()

            lines = [
                f"📦 سفارش شماره {order['id']}",
                f"🕒 زمان: {order['created_at']}",
                "",
            ]
            for item in items:
                lines.append(
                    f"• {item['product_name']}\n"
                    f"  تعداد: {item['quantity']}\n"
                    f"  قیمت واحد: ${item['unit_price']}"
                )

            lines.append(
                f"\n💰 مبلغ کل: ${order['total_price']}"
                f"\n📌 وضعیت: {order['status']}"
            )
            bot.send_message(message.chat.id, "\n".join(lines))


# =========================
# Account
# =========================
@bot.message_handler(func=lambda message: message.text == "👤 حساب کاربری")
def account(message):
    bot.send_message(
        message.chat.id,
        "👤 حساب کاربری\n\n"
        f"نام: {message.from_user.first_name}\n"
        f"شناسه کاربری: {message.from_user.id}",
    )


# =========================
# Run
# =========================
if __name__ == "__main__":
    init_db()
    seed_products()
    print("Bot is running...")
    bot.infinity_polling()
