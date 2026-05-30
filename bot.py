import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен в одну сплошную строку без лишних слов
TOKEN = "8586142798:AAEJ3iqff4TnmqM19e-enCzpLylaNe1-Ca0"
ADMIN_ID = 8341066688

bot = Bot(token=TOKEN)
dp = Dispatcher()

products = {
    "7-Я|СОПРОВОД|ГАРАНТ 20КK+ШМОТ": "230 ₽",
    "7-Я|СОПРОВОД|ГАРАНТ 10КK+ШМОТ": "150 ₽",
    "7-Я|СОПРОВОД|ГАРАНТ 50КK+ШМОТ": "450 ₽",
    "5-Я|СОПРОВОД|ГАРАНТ 10КK+ШМОТ": "150 ₽",
    "5-Я|СОПРОВОД|ГАРАНТ 20КK+ШМОТ": "250 ₽",
    "7-Я|БУСТ|20КК-БЕЗ ШМОТА": "200 ₽",
    "7-Я|БУСТ|50КК-БЕЗ ШМОТА": "400 ₽",
}

user_orders = {}

@dp.message(CommandStart())
async def start(message: Message):
    kb = InlineKeyboardBuilder()
    for product, price in products.items():
        kb.button(
            text=f"{product} - {price}",
            callback_data=f"buy:{product}"
        )
    kb.adjust(1)
    await message.answer(
        "📱 PUBG METRO SHOP\n\nВыберите пакет услуг:",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data.startswith("buy:"))
async def select_product(callback: CallbackQuery):
    product = callback.data.split(":")[1]
    user_orders[callback.from_user.id] = product
    await callback.message.answer(
        f"Вы выбрали {product}\n\nОтправьте ваш PUBG ID и ожидайте ответа."
    )
    await callback.answer()

@dp.message()
async def get_pubg_id(message: Message):
    user_id = message.from_user.id
    if user_id not in user_orders:
        await message.answer("Нажмите /start и выберите товар.")
        return
    product = user_orders[user_id]
    pubg_id = message.text
    username = message.from_user.username
    if username:
        username = f"@{username}"
    else:
        username = "нет username"
    await bot.send_message(
        ADMIN_ID,
        f"🛒 НОВЫЙ ЗАКАЗ\n\n"
        f"Товар: {product}\n"
        f"PUBG ID: {pubg_id}\n"
        f"Покупатель: {username}\n"
        f"Telegram ID: {user_id}"
    )
    await message.answer(
        "✅ Заказ принят.\nОжидайте сообщения от администратора."
    )
    del user_orders[user_id]

async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
