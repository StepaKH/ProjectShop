import telebot
import config
import sqlite3

import random

from io import BytesIO
import os

from telebot import types

name_product = None
photo_product = None
price_product = None
width_product = None

bot = telebot.TeleBot(config.TOKEN2)

@bot.message_handler(commands = ['start', 'main', 'hello'])
def start(message):
    # DB
    conn = sqlite3.connect('shop.sql')
    cur = conn.cursor()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS tokens (id int auto_increment primary key, name varchar(255), photo BLOB, price varchar(20) default(NULL), width varchar(20) default(NULL), token varchar(20) default(NULL))')

    conn.commit()
    cur.close()
    conn.close()
    ###

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Получить артикул", callback_data='token')
    markup.add(btn1)

    bot.send_message(message.chat.id, "Нажмите на кнопку <b><u>получить артикул</u></b>, после чего внесите все необходимые данные", parse_mode='html', reply_markup=markup)

@bot.message_handler(commands = ['get'])
@bot.message_handler(func=lambda message: message.text.lower() == 'получить')
def get(message):
    bot.send_message(message.chat.id, "Введите, пожалуйста, название товара")
    bot.register_next_step_handler(message, get_name)
def get_name(message):
    global name_product
    name_product = message.text.strip()
    bot.send_message(message.chat.id, "Введите цену товара")
    bot.register_next_step_handler(message, get_price)
def get_price(message):
    global price_product
    price_product = message.text.strip()
    bot.send_message(message.chat.id, "Введите ширину товара")
    bot.register_next_step_handler(message, get_width)
def get_width(message):
    global width_product
    width_product = message.text.strip()
    bot.send_message(message.chat.id, "Введите фотографию товара")
    bot.register_next_step_handler(message, get_photo)
def get_photo(message):
    global photo_product
    photo = message.photo[-1]  # Получаем последнюю (наибольшую по размеру) фотографию
    file_id = photo.file_id  # Получаем идентификатор файла
    file_info = bot.get_file(file_id)  # Получаем информацию о файле
    downloaded_file = bot.download_file(file_info.file_path)  # Скачиваем файл
    photo_product = downloaded_file

    markup = types.InlineKeyboardMarkup()
    bottom1 = types.InlineKeyboardButton('Верно', callback_data='true')
    bottom2 = types.InlineKeyboardButton('Неверно', callback_data='false')
    markup.row(bottom1,bottom2)

    bot.send_message(message.chat.id,f'Проверьте, пожалуйста, ваши данные на корректность:\n Name: {name_product}\n Price: {price_product}\n Width: {width_product}')
    bot.send_photo(message.chat.id, photo_product, reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'token':
        bot.send_message(callback.message.chat.id, "Введите - <b>получить</b>", parse_mode='html')
    elif callback.data == 'true':
        random_number = random.randint(100000, 999999)
        conn = sqlite3.connect('shop.sql')
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO tokens (name, photo, price, width, token) VALUES (?, ?, ?, ?, ?)",
            (name_product, photo_product, price_product, width_product, random_number))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, f"Товар успешно сохранен!\n"
                                                   f"Вот сгенерированный артикул - {random_number}")
    elif callback.data == 'false':
        bot.send_message(callback.message.chat.id, "Введите - <b>получить</b>", parse_mode='html')

@bot.message_handler()
def fan(message):
    conn = sqlite3.connect('shop.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM tokens')
    products = cur.fetchall()
    info = ''
    for elm in products:
        name = elm[1]
        price = elm[3]
        width = elm[4]
        token = elm[5]
        photo_data = elm[2]  # Бинарные данные фотографии из базы данных
        # Сохранение бинарных данных фотографии в файл
        with open(f'{name}.jpg', 'wb') as file:
            file.write(photo_data)
        # Отправка сообщения с данными о товаре и фотографией
        bot.send_message(message.chat.id, f'name: {name}, price: {price}, width: {width}, token: {token}')
        bot.send_photo(message.chat.id, open(f'{name}.jpg', 'rb'))
        os.remove(f'{name}.jpg')
    cur.close()
    conn.close()



bot.polling(none_stop = True)