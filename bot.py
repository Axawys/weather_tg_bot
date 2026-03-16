import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Читаем токен
with open("telegramapi.txt") as f:
    TOKEN = f.read().strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Это погодный бот, введите название города (можно на русском).")

async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city_name = update.message.text

    # 1. Ищем город (добавлен параметр language=ru)
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {
        "name": city_name,
        "count": 1,
        "language": "ru"  # Указываем русский язык для поиска и ответа
    }
    
    try:
        geo_response = requests.get(geo_url, params=geo_params)
        geo = geo_response.json()

        if "results" not in geo or len(geo["results"]) == 0:
            await update.message.reply_text("Город не найден, попробуйте еще раз.")
            return

        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        name = geo["results"][0].get("name", city_name)
        country = geo["results"][0].get("country", "")

        # 2. Получаем погоду
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "current_weather": "true",
            "timezone": "auto"
        }

        weather_response = requests.get(weather_url, params=weather_params)
        weather = weather_response.json()

        today_temp = weather["current_weather"]["temperature"]
        today_rain = weather["daily"]["precipitation_probability_max"][0]

        tomorrow_max = weather["daily"]["temperature_2m_max"][1]
        tomorrow_min = weather["daily"]["temperature_2m_min"][1]
        tomorrow_rain = weather["daily"]["precipitation_probability_max"][1]

        today_msg = (
            f"📍 {name} ({country})\n\n"
            f"Сейчас:\n"
            f"🌡 Температура: {today_temp}°C\n"
            f"🌧 Вероятность осадков: {today_rain}%"
        )

        tomorrow_msg = (
            f"Завтра:\n"
            f"🌡 Температура: {tomorrow_min}°C ... {tomorrow_max}°C\n"
            f"🌧 Вероятность осадков: {tomorrow_rain}%"
        )

        await update.message.reply_text(today_msg)
        await update.message.reply_text(tomorrow_msg)
        
    except Exception as e:
        print(f"Ошибка: {e}")
        await update.message.reply_text("Произошла ошибка при получении данных.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, city))

print("Бот запущен")
app.run_polling()
