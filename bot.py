        import os
import asyncio
import time
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ БОТА И АДМИНКИ ---
TOKEN = "8586142798:AAGxUeK-EwV_t6FwQp5b-A_yIqXN2wKzD8s"  # Ваш рабочий токен от @BotFather
ADMIN_ID = 8341066688  # Ваш Telegram ID
GOLDEN_KEY = "v1frcp8yh3dqtkt14p5xwp82juxlw1rj"  # Ваш токен FunPay

# Ссылки вашего магазина
FUNPAY_URL = "https://funpay.com/uk/lots/1290/trade"
PAYGAME_URL = "https://paygame.ru/users/SAKO1"
REVIEWS_URL = "https://funpay.com/uk/lots/1290/trade"
SUPPORT_URL = "t.me/SK_SAKO"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Переменная для хранения статуса автоподнятия (по умолчанию включено)
AUTORAISE_ENABLED = True

# Список товаров клана SK¹
products = {
    "7-Я|СОПРОВОД|ГАРАНТ 20КК+ШМОТ": "230 ₽",
    "7-Я|СОПРОВОД|ГАРАНТ 10КК+ШМОТ": "150 ₽",
    "7-Я|СОПРОВОД|ГАРАНТ 50КК+ШМОТ": "450 ₽",
    "5-Я|СОПРОВОД|ГАРАНТ 10КК+ШМОТ": "150 ₽",
    "5-Я|СОПРОВОД|ГАРАНТ 20КК+ШМОТ": "250 ₽",
    "7-Я|БУСТ|20КК-БЕЗ ШМОТА": "200 ₽",
    "7-Я|БУСТ|50КК-БЕЗ ШМОТА": "400 ₽"
}

# --- КЛАСС ОБРАБОТЧИКА ДЛЯ ПИНГА RENDER ---
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Бот активен и работает!".encode("utf-8"))

    def log_message(self, format, *args):
        return

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    httpd = HTTPServer(("", port), PingHandler)
    httpd.serve_forever()

# --- УЛУЧШЕННАЯ ФУНКЦИЯ ПОДНЯТИЯ ЛОТОВ НА FUNPAY ---
def raise_funpay_lots():
    """Функция делает POST запрос на FunPay для поднятия лотов"""
    url = "https://funpay.com"
    headers = {
        "Cookie": f"golden_key={GOLDEN_KEY}",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://funpay.com",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive"
    }
    data = {"game_id": ""} 
    
    try:
        # Тайм-аут увеличен до 30 секунд для стабильности при плохом сигнале
        response = requests.post(url, headers=headers, data=data, timeout=30)
        if response.status_code == 200:
            return True, response.text
        else:
            return False, f"Статус код: {response.status_code}"
    except Exception as e:
        return False, "Сервер сайта временно недоступен. Бот повторит попытку автоматически."

# --- ФОНОВЫЙ ПОТОК ДЛЯ АВТОПОДНЯТИЯ ПО ТАЙМЕРУ ---
def funpay_loop():
    global AUTORAISE_ENABLED
    time.sleep(15)  # Даем боту полностью запуститься
    
    while True:
        if AUTORAISE_ENABLED:
            success, info = raise_funpay_lots()
            try:
                if success:
                    asyncio.run(bot.send_message(chat_id=ADMIN_ID, text="[FunPay] Лоты успешно подняты автоматически! 🔄"))
                else:
                    # Если сайт временно недоступен, не пугаем админа, просто пишем лог в консоль Render
                    if "недоступен" in str(info):
                        print(f"[FunPay Log] {info}")
                    else:
                        asyncio.run(bot.send_message(chat_id=ADMIN_ID, text=f"[FunPay] Ошибка автоподнятия лотов ❌\nПроверьте токен. Инфо: {info}"))
            except Exception as tg_err:
                print(f"Не удалось отправить уведомление админу: {tg_err}")
                
            # Интервал между поднятиями: 2 часа (7200 секунд)
            time.sleep(7200)
        else:
            time.sleep(10)

# --- ЛОГИКА ТЕЛЕГРАМ-БОТА (МАГАЗИН PUBG) ---

@dp.message(CommandStart())
async def start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Услуги клана SK¹", callback_data="view_products")
    kb.button(text="⭐ Отзывы клиентов", url=REVIEWS_URL)
    kb.button(text="💬 Связаться с админом", url=SUPPORT_URL)
    kb.adjust(1)
    
    await message.answer(
        "🎒 Добро пожаловать в METRO ROYALE SHOP от клана SK¹!\n\n"
        "Мы — профессиональная команда клана SK¹. Предоставляем топовые услуги качественного сопровождения и буста в PUBG Mobile.\n\n"
        "🔒 Почему выбирают клан SK¹:\n"
        "• Профессиональные бойцы нашего клана\n"
        "• Быстрое выполнение и гарантия окупаемости\n"
        "• Полная безопасность вашего игрового аккаунта\n"
        "• Честные цены и сотни довольных клиентов\n\n"
        "Выбирайте нужный раздел в меню ниже 👇",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "view_products")
async def show_products(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    for idx, (product, price) in enumerate(products.items()):
        kb.button(text=f"{product} — {price}", callback_data=f"prod:{idx}")
        
    kb.button(text="⬅️ Назад в меню", callback_data="back_to_menu")
    kb.adjust(1)
    
    await callback.message.edit_text(
        "📱 СПИСОК ДОСТУПНЫХ УСЛУГ КЛАНА SK¹\n\n"
        "Выберите интересующий вас вариант, чтобы открыть площадки для оплаты:",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("prod:"))
async def select_platform(callback: CallbackQuery):
    prod_idx = int(callback.data.split(":"))
    product_name = list(products.keys())[prod_idx]
    product_price = list(products.values())[prod_idx]
    
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Купить на FunPay", url=FUNPAY_URL)
    kb.button(text="💳 Купить на PayGame", url=PAYGAME_URL)
    kb.button(text="⬅️ Назад к услугам SK¹", callback_data="view_products")
    kb.adjust(1)
    
    await callback.message.edit_text(
        f"🛒 Вы выбрали услугу от клана SK¹:\n{product_name}\n\n"
        f"💰 Цена услуги: {product_price}\n\n"
        f"Выберите удобную для вас торговую площадку для безопасной покупки у нашего клана:",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Услуги клана SK¹", callback_data="view_products")
    kb.button(text="⭐ Отзывы клиентов", url=REVIEWS_URL)
    kb.button(text="💬 Связаться с админом", url=SUPPORT_URL)
    kb.adjust(1)
    
    message_text = (
        "🎒 Добро пожаловать в METRO ROYALE SHOP от клана SK¹!\n\n"
        "Выбирайте нужный раздел в меню ниже 👇"
    )
    await callback.message.edit_text(message_text, reply_markup=kb.as_markup())
    await callback.answer()

# --- СЕКРЕТНАЯ АДМИН-ПАНЕЛЬ ДЛЯ ВАС ---

def get_admin_kb():
    kb = InlineKeyboardBuilder()
    status = "🟢 ВКЛЮЧЕНО" if AUTORAISE_ENABLED else "🔴 ВЫКЛЮЧЕНО"
    
    kb.button(text="🟢 Включить автоподнятие", callback_data="fp_on")
    kb.button(text="🔴 Выключить автоподнятие", callback_data="fp_off")
    kb.button(text="⚡ Поднять прямо сейчас", callback_data="fp_now")
    kb.adjust(1)
    return kb.as_markup(), status

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
        
    reply_markup, status = get_admin_kb()
    await message.answer(
        f"🤖 **АДМИН-ПАНЕЛЬ FUNPAY**\n"
        f"└ Текущий статус автоподнятия: {status}\n\n"
        f"Управляйте скриптом с помощью кнопок ниже:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "fp_on")
async def fp_on(callback: CallbackQuery):
    global AUTORAISE_ENABLED
    if callback.from_user.id != ADMIN_ID: return
    
    AUTORAISE_ENABLED = True
    reply_markup, status = get_admin_kb()
    await callback.message.edit_text(f"🤖 **АДМИН-ПАНЕЛЬ FUNPAY**\n└ Текущий статус автоподнятия: {status}\n\nРежим успешно изменен!", reply_markup=reply_markup, parse_mode="Markdown")
    await callback.answer("Автоподнятие включено! ✅")

@dp.callback_query(F.data == "fp_off")
async def fp_off(callback: CallbackQuery):
    global AUTORAISE_ENABLED
    if callback.from_user.id != ADMIN_ID: return
    
    AUTORAISE_ENABLED = False
    reply_markup, status = get_admin_kb()
    await callback.message.edit_text(f"🤖 **АДМИН-ПАНЕЛЬ FUNPAY**\n└ Текущий статус автоподнятия: {status}\n\nРежим успешно изменен!", reply_markup=reply_markup, parse_mode="Markdown")
    await callback.answer("Автоподнятие отключено! 🔴")

@dp.callback_query(F.data == "fp_now")
async def fp_now(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    await callback.answer("Запрос отправлен...")
    
    success, info = raise_funpay_lots()
    if success:
        await callback.message.answer("[FunPay] Ручное поднятие выполнено успешно! ⚡✅")
    else:
        await callback.message.answer(f"[FunPay] Результат выполнения ❌\n{info}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    # 1. Запускаем мини-веб-сервер для пинга
    Thread(target=run_dummy_server, daemon=True).start()
    
    # 2. Запускаем фоновый цикл для автоподнятия FunPay
    Thread(target=funpay_loop, daemon=True).start()
    
    # 3. Запускаем основного бота
    asyncio.run(main())
    
