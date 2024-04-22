import getInfAboutProduct
import telebot
import config
import takeToken
import sqlite3
import checkUser
import editUser

from telebot import types

import re
from io import BytesIO
import os

user_states = {}

bot = telebot.TeleBot(config.TOKEN)
bot.set_webhook()

def mainKeyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bottom1 = types.KeyboardButton("Главная")
    bottom2 = types.KeyboardButton("Консультация")
    bottom3 = types.KeyboardButton("Заказ")
    markup.row(bottom1, bottom2)
    markup.add(bottom3)
    return markup

@bot.message_handler(commands = ['start', 'main', 'hello'])
@bot.message_handler(func=lambda message: message.text.lower() == 'главная')
def welcome(message):
    #DB
    conn = sqlite3.connect('shop.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(255), tgId varchar(20) unique not null, phone varchar(20))')

    conn.commit()
    cur.close()
    conn.close()
    ###

    user_states[message.chat.id] = {'name':None, 'phone':None, 'tgId':None}
    sti = open('static/welcome.webp', 'rb')

    bot.send_sticker(message.chat.id, sti)
    bot.send_message(message.chat.id, "Добро пожаловать, {0.first_name}!\n "
                                      "Я - <b>электронный сотрудник магазина по продаже тканей</b>, бот созданный чтобы помочь тебе сделать заказ.".format(message.from_user, bot.get_me()),
                     parse_mode='html')

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Статус посылки", callback_data='status')
    btn2 = types.InlineKeyboardButton("Сделать заказ", callback_data='order')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, "{0.first_name}, если вы хотите получить информацию по доставке вашего заказа - нажмите на <b>Статус посылки</b>\n"
                                      "Если хотите сделать заказ - нажмите на <b>Сделать заказ</b>".format(message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['order'])
@bot.message_handler(func=lambda message: message.text.lower() == 'заказ')
def order(message):
    user_states[message.chat.id] = {'token' : None}
    #bot.delete_message(message.chat.id, message.message_id - 2)
    bot.send_message(message.chat.id, "Процесс создания заказа начат. Пожалуйста, следуйте инструкциям.", reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "Введите, пожалуйста, <b>артикул</b> товара\n"
                                      "<b>Пример ввода: 875234</b>\n\n"
                                      "Если вы забыли артикул товара, то можете перейти обратно в основной канал и посмотреть его\n"
                                      "<b>Вот ссылка -> https://t.me/bravissimo_nn</b>", parse_mode='html')
    bot.register_next_step_handler(message, get_token)
    #Обработка индефикатора и подтверждение правильности выбора товара
def get_token(message):
    #config.token = message.text.strip()
    #user_states[message.chat.id]['token':None]
    user_states[message.chat.id]['token'] = message.text.strip()
    #config.product_data = getInfAboutProduct.get_product_data(config.token)
    #user_states[message.chat.id]['product_data':None]
    user_states[message.chat.id]['product_data'] = getInfAboutProduct.get_product_data(user_states[message.chat.id]['token'])
    #Проверка на существование
    if (not user_states[message.chat.id]['product_data']):
        bot.send_message(message.chat.id, f'К сожалению такого артикула не существует😢\n'
                         f'Попробуйте снова!')
        order(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bottom1 = types.KeyboardButton("Верно")
        bottom2 = types.KeyboardButton("Неверно")
        markup.row(bottom1, bottom2)

        bot.send_message(message.chat.id, "Проверьте, пожалуйста, что вы правильно ввели артикул\n"
                                          "Данные по данному артикулу:")

        #name = config.product_data[1]
        #price = config.product_data[3]
        #width = config.product_data[4]
        #token = config.product_data[5]
        #photo = config.product_data[2]  # Бинарные данные фотографии из базы данных
        # Сохранение бинарных данных фотографии в файл
        with open(f'{user_states[message.chat.id]['product_data'][1]}.jpg', 'wb') as file:
            file.write(user_states[message.chat.id]['product_data'][2])
        # Отправка сообщения с данными о товаре и фотографией
        bot.send_photo(message.chat.id, open(f'{user_states[message.chat.id]['product_data'][1]}.jpg', 'rb'), caption = f'Name: {user_states[message.chat.id]['product_data'][1]}\n Price: {user_states[message.chat.id]['product_data'][3]}\n Width: {user_states[message.chat.id]['product_data'][4]}\n Token: {user_states[message.chat.id]['product_data'][5]}', reply_markup=markup)
        os.remove(f'{user_states[message.chat.id]['product_data'][1]}.jpg')
        #Проверка на правильный выбор
        bot.register_next_step_handler(message, check_product)
def check_product(message):
    if (message.text.strip() == 'Неверно'):
        order(message)
    elif (message.text.strip() == 'Верно'):
        get_info_user(message)
    else:
        bot.send_message(message.chat.id, "Выберите одну из кнопок: Верно или Невернно")
        bot.register_next_step_handler(message, check_product)
def get_info_user(message):
    #Register users
    #user_states[message.chat.id]['user_data':None]
    user_states[message.chat.id]['user_data'] = checkUser.get_user_data(message.from_user.id)
    #config.user_data = checkUser.get_user_data(message.from_user.id)
    if (user_states[message.chat.id]['user_data']):
        markup = types.InlineKeyboardMarkup()
        bottom1 = types.InlineKeyboardButton('Верно', callback_data='true_enter')
        bottom2 = types.InlineKeyboardButton('Изменились', callback_data='edit_data')
        markup.row(bottom1, bottom2)

        user_states[message.chat.id]['name'] = user_states[message.chat.id]['user_data'][1]
        user_states[message.chat.id]['phone'] = user_states[message.chat.id]['user_data'][3]
        user_states[message.chat.id]['tgId'] = message.from_user.id
        #config.name = config.user_data[1]
        #config.phone = config.user_data[3]
        #config.tg_id = config.user_data[2]

        bot.send_message(message.chat.id,f'Вы уже были в нашем магазине, и у нас есть ваши данные😁', reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id, f'Проверьте, пожалуйста, текущие данные на корректность:\n\n'
                                          f'ФИО: {user_states[message.chat.id]['user_data'][1]}\n'
                                          f'Номер телефона: {user_states[message.chat.id]['user_data'][3]}', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Сейчас нужно вас зарегестрирвоать!\n"
                                          "Введите, пожалуйста, свои: Фамилия, Имя, Отчество", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, user_name)
def user_name(message):
    user_states[message.chat.id]['name'] = message.text.strip()
    if re.match(r'^[А-ЯЁа-яё]+\s+[А-ЯЁа-яё]+\s+[А-ЯЁа-яё]+$', user_states[message.chat.id]['name']):
        # Ввод пользователя соответствует формату Фамилия Имя Отчество
        #config.name = full_name
        bot.send_message(message.chat.id, "Введите свой номер телефона в форматах:\n"
                                          "89*********\n"
                                          "+79*********")
        bot.register_next_step_handler(message, user_phone)
    else:
        # Ввод пользователя не соответствует формату ФИО
        bot.send_message(message.chat.id, "Пожалуйста, введите Фамилию Имя Отчество в правильном формате.")
        bot.register_next_step_handler(message, user_name)
def user_phone(message):
    user_states[message.chat.id]['phone'] = message.text.strip()
    if re.match(r'^(\+7|8)9\d{9}$', user_states[message.chat.id]['phone']):
        # Введенный номер телефона соответствует формату
        #config.phone = message.text.strip()
        #config.tg_id = message.from_user.id

        user_states[message.chat.id]['tgId'] = message.from_user.id
        markup = types.InlineKeyboardMarkup()
        bottom1 = types.InlineKeyboardButton('Верно', callback_data='true_enter')
        bottom2 = types.InlineKeyboardButton('Неверно', callback_data='false_enter')
        markup.row(bottom1,bottom2)

        bot.send_message(message.chat.id, f'Мы закончили небольшую регистрацию🔥')
        bot.send_message(message.chat.id,f'Проверьте, пожалуйста, ваши данные на корректность:\n ФИО: {user_states[message.chat.id]['name']}\n Номер телефона: {user_states[message.chat.id]['phone']}', reply_markup=markup)
    else:
        # Неверный формат номера телефона
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный номер телефона.")
        bot.register_next_step_handler(message, user_phone)

@bot.message_handler(commands=['advice'])
@bot.message_handler(func=lambda message: message.text.lower() == 'консультация')
def consult(message):
    #name = config.product_data[1]
    #price = config.product_data[3]
    #width = config.product_data[4]
    #token = config.product_data[5]
    #photo = config.product_data[2]  # Бинарные данные фотографии из базы данных

    # Сохранение бинарных данных фотографии в файл
    with open(f'{user_states[message.chat.id]['product_data'][1]}.jpg', 'wb') as file:
        file.write(user_states[message.chat.id]['product_data'][2])
    # Отправка сообщения с данными о товаре и фотографией
    bot.send_photo(config.manager_id, open(f'{user_states[message.chat.id]['product_data'][1]}.jpg', 'rb'), caption= f'Консультация!\n'
                                        f'Информация о заказе с артикулом - {user_states[message.chat.id]['product_data'][5]}:\n'
                                        f'Название: {user_states[message.chat.id]['product_data'][1]}\n'
                                        f'Цена: {user_states[message.chat.id]['product_data'][3]}\n'
                                        f'Ширина: {user_states[message.chat.id]['product_data'][4]}\n\n'
                                                                          
                                        f'Информация о пользователе:\n'
                                        f'Ник пользователя - {message.from_user.username}\n'
                                        f'ФИО - {user_states[message.chat.id]['name']}\n'
                                        f'Номер телефона - {user_states[message.chat.id]['phone']}')
    os.remove(f'{user_states[message.chat.id]['product_data'][1]}.jpg')

    bot.send_message(message.chat.id,f'Перейдите по следующей ссылке, чтобы связаться с менеджером. Обязательно отправьте артикул своего товара, чтобы менеджер смог вас понять)\n\n'
                                     f'<b>Переходи сюда</b> -> https://t.me/res12245', parse_mode='html', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['edit_name'])
@bot.message_handler(func=lambda message: message.text.lower() == 'фио')
def name(message):
    bot.send_message(message.chat.id, "Введите, пожалуйста, свои: Фамилия, Имя, Отчество", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_name)
def get_name(message):
    #full_name = message.text.strip()
    user_states[message.chat.id]['name'] = message.text.strip()
    if re.match(r'^[А-ЯЁа-яё]+\s+[А-ЯЁа-яё]+\s+[А-ЯЁа-яё]+$', user_states[message.chat.id]['name']):
        #config.name = full_name
        editUser.update_user_name(user_states[message.chat.id]['name'], message.from_user.id)
        markup = types.InlineKeyboardMarkup()
        bottom1 = types.InlineKeyboardButton('Верно', callback_data='true_enter')
        bottom2 = types.InlineKeyboardButton('Неверно', callback_data='edit_data')
        markup.row(bottom1, bottom2)
        bot.send_message(message.chat.id,f'Проверьте, пожалуйста, ваши данные на корректность:\n ФИО: {user_states[message.chat.id]['name']}\n Номер телефона: {user_states[message.chat.id]['phone']}',reply_markup=markup)
    else:
        # Ввод пользователя не соответствует формату ФИО
        bot.send_message(message.chat.id, "Пожалуйста, введите Фамилию Имя Отчество в правильном формате.")
        bot.register_next_step_handler(message, get_name)


@bot.message_handler(commands=['edit_phone'])
@bot.message_handler(func=lambda message: message.text.lower() == 'номер')
def phone(message):
    bot.send_message(message.chat.id, "Введите, пожалуйста, новый номер", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_phone)
def get_phone(message):
    # phone_nember = message.text.strip()
    user_states[message.chat.id]['phone'] = message.text.strip()
    if re.match(r'^79\d{9}$', user_states[message.chat.id]['phone']):
        #config.phone = phone_number
        editUser.update_user_phone(user_states[message.chat.id]['phone'], message.from_user.id)
        markup = types.InlineKeyboardMarkup()
        bottom1 = types.InlineKeyboardButton('Верно', callback_data='true_enter')
        bottom2 = types.InlineKeyboardButton('Неверно', callback_data='edit_data')
        markup.row(bottom1, bottom2)
        bot.send_message(message.chat.id,f'Проверьте, пожалуйста, ваши данные на корректность:\n ФИО: {user_states[message.chat.id]['name']}\n Номер телефона: {user_states[message.chat.id]['phone']}',reply_markup=markup)
    else:
        # Неверный формат номера телефона
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный номер телефона.")
        bot.register_next_step_handler(message, get_phone)


@bot.message_handler(commands=['edit_all'])
@bot.message_handler(func=lambda message: message.text.lower() == 'все')
def name_from_all(message):
    bot.send_message(message.chat.id, "Введите, пожалуйста, свои: Фамилия, Имя, Отчество", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_name_from_all)
def get_name_from_all(message):
    # full_name = message.text.strip()
    user_states[message.chat.id]['name'] = message.text.strip()
    if re.match(r'^[А-ЯЁа-яё]+\s+[А-ЯЁа-яё]+\s+[А-ЯЁа-яё]+$', user_states[message.chat.id]['name']):
        # config.name = full_name
        bot.send_message(message.chat.id, "Введите, пожалуйста, новый номер")
        bot.register_next_step_handler(message, get_all)
    else:
        # Ввод пользователя не соответствует формату ФИО
        bot.send_message(message.chat.id, "Пожалуйста, введите Фамилию Имя Отчество в правильном формате.")
        bot.register_next_step_handler(message, get_name_from_all)
def get_all(message):
    # phone_number = message.text.strip()
    user_states[message.chat.id]['phone'] = message.text.strip()
    if re.match(r'^79\d{9}$', user_states[message.chat.id]['phone']):
        # config.phone = phone_number
        editUser.update_user_all(user_states[message.chat.id]['phone'], user_states[message.chat.id]['name'], message.from_user.id)
        markup = types.InlineKeyboardMarkup()
        bottom1 = types.InlineKeyboardButton('Верно', callback_data='true_enter')
        bottom2 = types.InlineKeyboardButton('Неверно', callback_data='edit_data')
        markup.row(bottom1, bottom2)
        bot.send_message(message.chat.id,f'Проверьте, пожалуйста, ваши данные на корректность:\n ФИО: {user_states[message.chat.id]['name']}\n Номер телефона: {user_states[message.chat.id]['phone']}',reply_markup=markup)
    else:
        # Неверный формат номера телефона
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный номер телефона.")
        bot.register_next_step_handler(message, get_all)




@bot.message_handler(content_types = ['photo', 'video', 'audio', 'sticker', 'emoji'])
def noneContent(message):
    bot.reply_to(message, f'Извините, {message.from_user.first_name}, я не умею обрабатывать такие сообщения((')


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'status':
        bot.send_message(callback.message.chat.id,'Перенаправляю Вас на моего коллегу, регистрация в один клик, далее введите <b>/add (номер вашего заказа)</b>, а затем <b>/tracks</b>. Также напоминаю, что по правилам нашего магазина (далее правила по срокам доставки)\n\n' + "Ссылка -> https://t.me/RLabbot",parse_mode='html')
       # bot.delete_message(callback.message.chat.id, callback.message.message_id)
    elif callback.data == 'order':
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Заказ")
        markup1.add(item1)
        bot.send_message(callback.message.chat.id, "Чтобы сделать заказ, отправьте команду <b>/order</b> или нажмите на кнопку <b>Заказ</b>" , parse_mode='html', reply_markup=markup1)
    elif callback.data == 'true_enter':
        if (not user_states[callback.message.chat.id]['user_data']):
            conn = sqlite3.connect('shop.sql')
            cur = conn.cursor()
            cur.execute(f"INSERT INTO users(name, tgId, phone) VALUES ('{user_states[callback.message.chat.id]['name']}', '{user_states[callback.message.chat.id]['tgId']}', '{user_states[callback.message.chat.id]['phone']}')")
            conn.commit()
            cur.close()
            conn.close()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bottom1 = types.KeyboardButton("Консультация")
        bottom2 = types.KeyboardButton("Продолжаем")
        markup.row(bottom1, bottom2)

        bot.send_message(callback.message.chat.id, "Ваши данные успешно зарегестрированы)")
        bot.send_message(callback.message.chat.id, "Нужна ли вам дополнительная консультация с нашим менеджером по поводу заказа?\n\n"
                                                   "Выберите <b>Консультация</b>, если нужна\n"
                                                   "Выберите <b>Продолжаем</b>, если не нужна", parse_mode='html', reply_markup=markup)
        #bot.delete_message(callback.message.chat.id,callback.message.message_id)
    elif callback.data == 'false_enter':
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Заказ")
        markup1.add(item1)
        bot.send_message(callback.message.chat.id, "Давайте заполним ваши данные заново. Отправьте, пожалуйста, команду <b>/order</b> или нажмите на кнопку <b>Заказ</b>", parse_mode='html', reply_markup=markup1)
    elif callback.data == 'edit_data':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bottom1 = types.KeyboardButton("ФИО")
        bottom2 = types.KeyboardButton("Номер")
        bottom3 = types.KeyboardButton("Все")
        markup.row(bottom1, bottom2)
        markup.add(bottom3)
        bot.send_message(callback.message.chat.id, f'Выберите, пожалуйста, какие данные поменялись🙃', reply_markup=markup)

    bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text = 'Continue....', reply_markup=None)






@bot.message_handler()
def info(message):
    if (message.text.lower() == 'привет'):
        bot.send_message(message.chat.id, "😕")
        bot.send_message(message.chat.id, "Добро пожаловать, {0.first_name}!\n "
                                          "Я - <b>электронный сотрудник магазина по продаже тканей</b>, бот созданный чтобы помочь тебе сделать заказ.".format(message.from_user, bot.get_me()),
                         parse_mode='html')
    elif (message.text.lower() == 'id'):
        bot.reply_to(message, f'ID: {message.from_user.id}')
    elif (message.text.lower() == 'test'):
        conn = sqlite3.connect('shop.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users')
        products = cur.fetchall()
        info = ''
        for elm in products:
            info += f'name: {elm[1]}, phone: {elm[3]}, id: {elm[2]}'
            # Отправка сообщения с данными о товаре и фотографией
        bot.send_message(message.chat.id, info)
        cur.close()
        conn.close()
    else:
        bot.reply_to(message, f'Извините, {message.from_user.first_name}, я не умею обрабатывать такие сообщения((')



bot.polling(none_stop = True)