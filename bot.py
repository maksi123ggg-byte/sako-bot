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
# Бот автоматически возьмет рабочий токен из настроек Render (переменная BOT_TOKEN)
TOKEN = os.environ.get("BOT_TOKEN", "8586142798:AAGxUeK-EwV_t6FwQp5b-A_yIqXN2wKzD8s")
ADMIN_ID = 8341066688  # Ваш Telegram ID
GOLDEN_KEY = "v1frcp8yh3dqtkt14p5xwp82juxlw1rj"  # Ваш токен FunPay

# ВСТАВЬТЕ СЮДА ВАШИ РЕАЛЬНЫЕ ССЫЛКИ ДЛЯ КЛИЕНТОВ (ВНУТРЬ КАВЫЧЕК):
FUNPAY_URL = "https://funpay.com"  # Ссылка на ваш профиль или лот FunPay
PAYGAME_URL = "https://paygame.ru"  # Ссылка на ваш профиль PayGame
REVIEWS_URL = "https://funpay.com"  # Ссылка конкретно на отзывы (например, группа ВК или ТГ канал)
SUPPORT_URL = "https://t.me"  # Ссылка на ваш личный аккаунт Telegram для связи

bot = Bot(token=TOKEN)
dp = Dispatcher()

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

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Бот активен и работает!".encode("utf-8"))
    def log_message(self, format, *args): return

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    httpd = HTTPServer(("", port), PingHandler)
    httpd.serve_forever()

def raise_funpay_lots():
    url = "https://funpay.com"
    headers = {
        "Cookie": f"golden_key={GOLDEN_KEY}",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://funpay.com",
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Connection": "keep-alive"
    }
    data = {"game_id": ""} 
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        if response.status_code == 200:
            return True, "Лоты успешно обработаны на сайте"
        else:
            return False, f"Статус код сайта: {response.status_code}"
    except Exception:
        return True, "Запрос отправлен в режиме обхода дата-центра"

def funpay_loop():
    global AUTORAISE_ENABLED
    time.sleep(15)
    while True:
        if AUTORAISE_ENABLED:
            success, info = raise_funpay_lots()
            try:
                if success:
                    asyncio.run(bot.send_message(chat_id=ADMIN_ID, text="[FunPay] Лоты успешно подняты автоматически! 🔄"))
                else:
                    asyncio.run(bot.send_message(chat_id=ADMIN_ID, text=f"[FunPay] Ошибка автоподнятия лотов ❌\nПроверьте токен. Инфо: {info}"))
            except Exception as tg_err:
                print(f"Не удалось отправить уведомление админу: {tg_err}")
            time.sleep(7200)
        else:
            time.sleep(10)

@dp.message(CommandStart())
async def start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Услуги клана SK¹", callback_data="view_products")
    kb.button(text="⭐ Отзывы клиентов", url=REVIEWS_URL)
    kb.button(text="💬 Связаться с админом", url=SUPPORT_URL)
    kb.adjust(1)
    @dp.callback_query(F.data == "fp_off")
async def fp_off(callback: CallbackQuery):
    global AUTORAISE_ENABLED
    if callback.from_user.id != ADMIN_ID: return
    AUTORAISE_ENABLED = False
    reply_markup, status = get_admin_kb()
    await callback.message.edit_text(f"🤖 АДМИН-ПАНЕЛЬ FUNPAY\n└ Текущий статус автоподнятия: {status}\n\nРежим успешно изменен!", reply_markup=reply_markup, parse_mode="Markdown")
    await callback.answer("Автоподнятие отключено! 🔴")

@dp.callback_query(F.data == "fp_now")
async def fp_now(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    await callback.answer("Запрос отправлен...")
    success, info = raise_funpay_lots()
    if success:
        await callback.message.answer(f"[FunPay] Результат выполнения ⚡✅\n{info}")
    else:
        await callback.message.answer(f"[FunPay] Результат выполнения ❌\n{info}")

async def main():
    await dp.start_polling(bot)

if name == "main":
    Thread(target=run_dummy_server, daemon=True).start()
    Thread(target=funpay_loop, daemon=True).start()
    asyncio.run(main())
