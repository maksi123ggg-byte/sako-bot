import asyncio
from threading import Thread

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ================== НАСТРОЙКИ ==================
TOKEN = "8586142798:AAEJ3iqff4TnmqM19e-enCzpLylaNe1-Ca0"
ADMIN_ID = 123456789  # <-- сюда свой ID

FUNPAY_URL = "https://funpay.com/uk/users/19612186/"
PAYGAME_URL = "https://paygame.ru/users/SAKO1"
REVIEWS_URL = "https://funpay.com/uk/users/19612186/"
SUPPORT_URL = "https://t.me/SK_SAKO"

AUTORAISE_ENABLED = False

products = {
    "7-Я|СОПРОВОД|ГАРАНТ 20КК+ШМОТ": "230 ₽",
    "7-Я|СОПРОВОД|ГАРАНТ 10КК+ШМОТ": "150 ₽",
    "7-Я|СОПРОВОД|ГАРАНТ 50КК+ШМОТ": "450 ₽",
    "5-Я|СОПРОВОД|ГАРАНТ 10КК+ШМОТ": "150 ₽",
    "5-Я|СОПРОВОД|ГАРАНТ 20КК+ШМОТ": "250 ₽",
    "7-Я|БУСТ|20КК-БЕЗ ШМОТА": "200 ₽",
    "7-Я|БУСТ|50КК-БЕЗ ШМОТА": "400 ₽"
}

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================== СТАРТ ==================
@dp.message(Command("start"))
async def start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Услуги клана SK¹", callback_data="view_products")
    kb.button(text="⭐ Отзывы", url=REVIEWS_URL)
    kb.button(text="💬 Поддержка", url=SUPPORT_URL)
    kb.adjust(1)

    await message.answer(
        "🎒 Добро пожаловать в METRO ROYALE SHOP от клана SK¹!\n\n"
        "Выбирайте нужный раздел 👇",
        reply_markup=kb.as_markup()
    )

# ================== ТОВАРЫ ==================
@dp.callback_query(F.data == "view_products")
async def show_products(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()

    for idx, (product, price) in enumerate(products.items()):
        kb.button(text=f"{product} — {price}", callback_data=f"prod:{idx}")

    kb.button(text="⬅️ Назад", callback_data="back_to_menu")
    kb.adjust(1)

    await callback.message.edit_text(
        "📱 СПИСОК УСЛУГ\n\nВыберите:",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

# ================== ВЫБОР ==================
@dp.callback_query(F.data.startswith("prod:"))
async def select_product(callback: CallbackQuery):
    prod_idx = int(callback.data.split(":")[1])

    product_name = list(products.keys())[prod_idx]
    product_price = list(products.values())[prod_idx]

    kb = InlineKeyboardBuilder()
    kb.button(text="💳 FunPay", url=FUNPAY_URL)
    kb.button(text="💳 PayGame", url=PAYGAME_URL)
    kb.button(text="⬅️ Назад", callback_data="view_products")
    kb.adjust(1)

    await callback.message.edit_text(
        f"🛒 {product_name}\n\n💰 Цена: {product_price}",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

# ================== НАЗАД ==================
@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Услуги", callback_data="view_products")
    kb.button(text="⭐ Отзывы", url=REVIEWS_URL)
    kb.button(text="💬 Поддержка", url=SUPPORT_URL)
    kb.adjust(1)

    await callback.message.edit_text(
        "Главное меню 👇",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

# ================== АДМИНКА ==================
def get_admin_kb():
    kb = InlineKeyboardBuilder()
    status = "🟢 ВКЛ" if AUTORAISE_ENABLED else "🔴 ВЫКЛ"

    kb.button(text="🟢 Включить", callback_data="fp_on")
    kb.button(text="🔴 Выключить", callback_data="fp_off")
    kb.button(text="⚡ Поднять сейчас", callback_data="fp_now")
    kb.adjust(1)

    return kb.as_markup(), status

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    kb, status = get_admin_kb()

    await message.answer(
        f"🤖 АДМИНКА\nСтатус: {status}",
        reply_markup=kb
    )

@dp.callback_query(F.data == "fp_on")
async def fp_on(callback: CallbackQuery):
    global AUTORAISE_ENABLED

    if callback.from_user.id != ADMIN_ID:
        return

    AUTORAISE_ENABLED = True
    kb, status = get_admin_kb()

    await callback.message.edit_text(f"Статус: {status}", reply_markup=kb)
    await callback.answer("Включено")

@dp.callback_query(F.data == "fp_off")
async def fp_off(callback: CallbackQuery):
    global AUTORAISE_ENABLED

    if callback.from_user.id != ADMIN_ID:
        return

    AUTORAISE_ENABLED = False
    kb, status = get_admin_kb()

    await callback.message.edit_text(f"Статус: {status}", reply_markup=kb)
    await callback.answer("Выключено")

@dp.callback_query(F.data == "fp_now")
async def fp_now(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    await callback.answer("Готово (заглушка)")

# ================== ЗАПУСК ==================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
