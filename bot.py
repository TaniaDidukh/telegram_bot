from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp
import os

TOKEN = "8436762066:AAFCOwMe5eIgAtK5iL6lORyOPV8_--pVglc"

# Зберігаємо тимчасово формат для користувача
user_format = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли посилання з YouTube або TikTok 🎥")

# Обробка посилання
async def ask_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    user_format[update.effective_user.id] = {'url': url}
    
    keyboard = [
        [InlineKeyboardButton("Відео", callback_data='video')],
        [InlineKeyboardButton("Аудіо", callback_data='audio')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Що хочеш завантажити?", reply_markup=reply_markup)

# Обробка вибору кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    user_id = query.from_user.id
    
    url = user_format[user_id]['url']
    file_name = "file.mp4" if choice == 'video' else "file.mp3"
    ydl_opts = {"outtmpl": file_name, "format": "mp4" if choice=='video' else "bestaudio/best"}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Відправка файлу
        with open(file_name, "rb") as f:
            if choice == 'video':
                await query.message.reply_video(f)
            else:
                await query.message.reply_audio(f)

        os.remove(file_name)
    except Exception as e:
        await query.message.reply_text(f"Помилка: {e}")

# Запуск бота
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_format))
app.add_handler(CallbackQueryHandler(button))

print("Бот запущений ✅")
app.run_polling()
