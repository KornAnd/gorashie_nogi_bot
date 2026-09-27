# Инструкция по запуску бота «Горящие Ноги»

## 1. Подготовка окружения
1. Убедитесь, что вы находитесь в папке проекта:
   `cd /Users/kornad/Yandex.Disk.localized/WORK/pulsar/gorashie_nogi_bot`

2. Активируйте виртуальное окружение:
   `source venv/bin/activate`

## 2. Настройка Telegram Токена
Получите токен у [@BotFather](https://t.me/BotFather) в Telegram и укажите его в переменной окружения:
`export BOT_TOKEN="ВАШ_ТОКЕН_БОТА"`

## 3. Запуск веб-сервера калькулятора и бота
Запустите сервер приложения:
`python main.py`

Приложение запустится локально на `http://0.0.0.0:8000`.

## 4. Подключение WebApp в Telegram
Для работы WebApp внутри Telegram потребуется HTTPS URL (например, через ngrok):
`ngrok http 8000`

Затем укажите полученную ссылку у [@BotFather](https://t.me/BotFather) в меню бота -> `Bot Settings` -> `Menu Button` -> `Configure menu button`.
