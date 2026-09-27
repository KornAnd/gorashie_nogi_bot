import os
import asyncio
import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

from database import init_db, get_user_settings

# Инициализация БД
init_db()

BOT_TOKEN = "8890631054:AAHA3rEfyyBXMRfisCek2A-ZRjdCGoQYPxk"
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:8000")

app = FastAPI(title="Gorashie Nogi WebApp")
templates = Jinja2Templates(directory="templates")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@app.get("/", response_class=HTMLResponse)
async def serve_webapp(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/user_settings/{user_id}")
async def user_settings(user_id: int):
    return get_user_settings(user_id)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    # Если запущен внешний tunnel, используем его, иначе локальный URL
    current_url = WEBAPP_URL if WEBAPP_URL != "http://localhost:8000" else "https://telegram.org"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🏃‍♂️ Открыть беговые калькуляторы",
                web_app=WebAppInfo(url=current_url)
            )
        ]
    ])
    
    await message.answer(
        "🔥 Привет! Добро пожаловать в бот сообщества **«Горящие Ноги»**!\n\n"
        "Здесь собраны все необходимые калькуляторы для бега и тренировок:\n"
        "• ⏱️ Интервальный таймер\n"
        "• 💓 Пульсовые зоны\n"
        "• 📏 Калькулятор темпа и дистанции\n"
        "• ⚡ Конвертер темпа и скорости\n"
        "• 👟 Размерная сетка кроссовок\n\n"
        "Нажмите кнопку ниже, чтобы открыть приложение 👇",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def start_bot():
    print("🤖 Telegram бот 'Горящие Ноги' запускается...")
    asyncio.create_task(dp.start_polling(bot))

if __name__ == "__main__":
    import uvicorn
    # Запускаем aiogram при старте
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Регистрируем событие запуска бота
    @app.on_event("startup")
    async def on_startup():
        asyncio.create_task(dp.start_polling(bot))

    uvicorn.run(app, host="0.0.0.0", port=8000)
