from typing import Dict, Any
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Update

# Bot token
TOKEN = "7204228490:AAEV6AJCfx6Ws0CGQqBHYzzOP5Xyn5Yd5Bo"

# User states and data
user_states: Dict[int, Any] = {}
user_cart: Dict[int, Dict[str, int]] = {}

# Menu items
MENU_ITEMS = {
    'wings': {
        'name': '🍗 Куриные крылышки',
        'items': {
            'wings_6': {'name': '6 крылышек', 'price': 35000},
            'wings_12': {'name': '12 крылышек', 'price': 65000},
            'wings_24': {'name': '24 крылышка', 'price': 120000}
        }
    },
    'burgers': {
        'name': '🍔 Бургеры',
        'items': {
            'twister': {'name': 'Твистер', 'price': 28000},
            'zinger': {'name': 'Зингер', 'price': 32000},
            'big_box': {'name': 'Биг Бокс', 'price': 45000}
        }
    },
    'drinks': {
        'name': '🥤 Напитки',
        'items': {
            'cola': {'name': 'Кола', 'price': 8000},
            'fanta': {'name': 'Фанта', 'price': 8000},
            'sprite': {'name': 'Спрайт', 'price': 8000}
        }
    }
}

# Main menu
def get_main_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton("🍗 Меню"), KeyboardButton("🛒 Корзина")],
        [KeyboardButton("📱 Контакты"), KeyboardButton("⚙️ Настройки")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = """
🍗 Добро пожаловать в KFC Uzbekistan Delivery!

Мы рады приветствовать вас в нашем боте доставки. Здесь вы можете:
• Заказать любимые блюда KFC
• Отслеживать статус заказа
• Узнать о наших акциях

Выберите действие из меню ниже:
    """
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu())

# Show full menu
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    menu_text = "🍗 Наше меню:\n\n"
    keyboard = []

    for category_id, category in MENU_ITEMS.items():
        menu_text += f"{category['name']}\n"
        keyboard.append([InlineKeyboardButton(category['name'], callback_data=f"category_{category_id}")])

    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(menu_text, reply_markup=reply_markup)

# Show category items
async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    category_id = query.data.split('_')[1]

    if category_id not in MENU_ITEMS:
        await query.answer("Ошибка: категория не найдена!")
        return

    category = MENU_ITEMS[category_id]
    menu_text = f"{category['name']}:\n\n"
    keyboard = []

    for item_id, item in category['items'].items():
        menu_text += f"{item['name']} - {item['price']} сум\n"
        keyboard.append([
            InlineKeyboardButton(f"➕ {item['name']}", callback_data=f"add_{item_id}"),
            InlineKeyboardButton(f"➖ {item['name']}", callback_data=f"remove_{item_id}")
        ])

    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data='menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(menu_text, reply_markup=reply_markup)

# Add item to cart
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    item_id = query.data.split('_')[1]

    if user_id not in user_cart:
        user_cart[user_id] = {}

    if item_id not in user_cart[user_id]:
        user_cart[user_id][item_id] = 0

    user_cart[user_id][item_id] += 1
    await query.answer("Товар добавлен в корзину!")

# Remove item from cart
async def remove_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    item_id = query.data.split('_')[1]

    if user_id in user_cart and item_id in user_cart[user_id]:
        user_cart[user_id][item_id] -= 1
        if user_cart[user_id][item_id] <= 0:
            del user_cart[user_id][item_id]
        await query.answer("Товар удален из корзины!")
    else:
        await query.answer("Товар не найден в корзине!")

# Show cart
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    cart_text = "🛒 Ваша корзина:\n\n"
    total = 0

    if user_id in user_cart and user_cart[user_id]:
        for item_id, quantity in user_cart[user_id].items():
            for category in MENU_ITEMS.values():
                if item_id in category['items']:
                    item = category['items'][item_id]
                    cart_text += f"{item['name']} x{quantity} - {item['price'] * quantity} сум\n"
                    total += item['price'] * quantity
                    break

        cart_text += f"\n💰 Итого: {total} сум"
        keyboard = [
            [InlineKeyboardButton("✅ Оформить заказ", callback_data='checkout')],
            [InlineKeyboardButton("❌ Очистить корзину", callback_data='clear_cart')],
            [InlineKeyboardButton("◀️ Назад", callback_data='back')]
        ]
    else:
        cart_text = "🛒 Ваша корзина пуста"
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(cart_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(cart_text, reply_markup=reply_markup)

# Contacts
async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    contacts_text = """
📱 Наши контакты:

☎️ Call-центр: +998 (78) 129-70-00
📍 Адреса ресторанов:
• Ташкент, ул. Навои, 1
• Ташкент, ул. Амира Темура, 15
• Самарканд, ул. Регистан, 5

⏰ Время работы: 10:00 - 23:00
    """
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(contacts_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(contacts_text, reply_markup=reply_markup)

# Settings
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings_text = """
⚙️ Настройки:

Выберите действие:
    """
    keyboard = [
        [InlineKeyboardButton("🌐 Язык", callback_data='language')],
        [InlineKeyboardButton("📱 Номер телефона", callback_data='phone')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(settings_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(settings_text, reply_markup=reply_markup)

# Handle plain text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if text == "🍗 Меню":
        await show_menu(update, context)
    elif text == "🛒 Корзина":
        await show_cart(update, context)
    elif text == "📱 Контакты":
        await contacts(update, context)
    elif text == "⚙️ Настройки":
        await settings(update, context)
    else:
        await update.message.reply_text("Пожалуйста, используйте кнопки меню.")

# Handle button callbacks
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == 'menu':
        await show_menu(update, context)
    elif data.startswith('category_'):
        await show_category(update, context)
    elif data.startswith('add_'):
        await add_to_cart(update, context)
    elif data.startswith('remove_'):
        await remove_from_cart(update, context)
    elif data == 'cart':
        await show_cart(update, context)
    elif data == 'contacts':
        await contacts(update, context)
    elif data == 'settings':
        await settings(update, context)
    elif data == 'back':
        await start(update, context)
    elif data == 'clear_cart':
        user_id = query.from_user.id
        if user_id in user_cart:
            user_cart[user_id] = {}
        await show_cart(update, context)
    elif data == 'checkout':
        await query.edit_message_text("Для оформления заказа, пожалуйста, отправьте ваш номер телефона.")

# Start the bot
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button))

    print("🤖 Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
