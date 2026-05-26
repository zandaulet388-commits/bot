import telebot

TOKEN = "8818405158:AAHWwdPc3qLRXjWvO4eOFQf-0L4MSaA80Ow"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот работает")

bot.infinity_polling()
