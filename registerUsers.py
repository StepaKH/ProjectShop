import telebot
import config
import sqlite3

from telebot import types

name = None
phone = None

bot = telebot.TeleBot(config.TOKEN)

def user(message):
    bot.send_message(message.chat.id, "Сейчас нужно тебя зарегестрирвоать!\n"
                                      "Введите, пожалуйста, свои: Имя, Фамилия, Отчество")
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, "Введите свой номер телефона")
    bot.register_next_step_handler(message, user_phone)

def user_phone(message):
    phone = message.text.strip()
    tg_id = message.from_user.id

    conn = sqlite3.connect('shop.sql')
    cur = conn.cursor()

    cur.execute("INSERT INTO users(name, tgId, phone) VALUES ('%s', '%s', '%s')" % (name, tg_id, phone))
    conn.commit()
    cur.close()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Список пользователей', callback_data='list'))
    bot.send_message(message.chat.id, "Ваши данные внесены", reply_markup=markup)

    #bot.send_message(message.chat.id, "Введите свой номер телефона")
    #bot.register_next_step_handler(message, user_phone)