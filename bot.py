import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes


with open("telegramapi.txt") as f:
    TOKEN = f.read().strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Это погодный бот, введите свой город.")


async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text

    # ищем город
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo = requests.get(geo_url).json()

    if "results" not in geo:
        await update.message.reply_text("Город не найден, попробуйте еще")
        return

    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]
    name = geo["results"][0]["name"]

    # получаем погоду
    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        "&current_weather=true"
        "&timezone=auto"
    )

    weather = requests.get(weather_url).json()

    today_temp = weather["current_weather"]["temperature"]

    today_rain = weather["daily"]["precipitation_probability_max"][0]

    tomorrow_max = weather["daily"]["temperature_2m_max"][1]
    tomorrow_min = weather["daily"]["temperature_2m_min"][1]
    tomorrow_rain = weather["daily"]["precipitation_probability_max"][1]

    today_msg = (
        f"{name}\n\n"
        f"Сегодня:\n"
        f"Температура: {today_temp}°C\n"
        f"Вероятность осадков: {today_rain}%"
    )

    tomorrow_msg = (
        f"Завтра:\n"
        f"Температура: {tomorrow_min}°C – {tomorrow_max}°C\n"
        f"Вероятность осадков: {tomorrow_rain}%"
    )

    await update.message.reply_text(today_msg)
    await update.message.reply_text(tomorrow_msg)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, city))

print("Бот запущен")
app.run_polling()