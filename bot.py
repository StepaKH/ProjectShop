import telebot
import config
import takeToken
import sqlite3
import checkUser
import editUser

from telebot import types

token = 123

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands = ['start', 'main', 'hello'])
def welcome(message):
    #DB
    conn = sqlite3.connect('shop.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(255), tgId varchar(20) unique not null, phone varchar(20))')

    conn.commit()
    cur.close()
    conn.close()
    ###

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
    bot.delete_message(message.chat.id, message.message_id - 2)
    bot.send_message(message.chat.id, "Процесс создания заказа начат. Пожалуйста, следуйте инструкциям.", reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "Введите, пожалуйста, <b>артикул</b> товара\n"
                                      "<b>Пример ввода: 875234</b>\n\n"
                                      "Если вы забыли артикул товара, то можете перейти обратно в основной канал и посмотреть его\n"
                                      "<b>Вот ссылка -> https://t.me/bravissimo_nn</b>", parse_mode='html')

    #Обработка индефикатора и подтверждение правильности выбора товара

    #Register users
    config.user_data = checkUser.get_user_data(message.from_user.id)
    if (config.user_data):
        markup = types.InlineKeyboardMarkup()
        bottom1 = types.InlineKeyboardButton('Верно', callback_data='true_enter')
        bottom2 = types.InlineKeyboardButton('Изменились', callback_data='edit_data')
        markup.row(bottom1, bottom2)

        config.name = config.user_data[1]
        config.phone = config.user_data[3]
        config.tg_id = config.user_data[2]

        bot.send_message(message.chat.id, f'Вы уже были в нашем магазине, и у нас есть ваши данные😁\n'
                                          f'Проверьте, пожалуйста, текущие данные на корректность:\n'
                                          f'ФИО: {config.name}\n'
                                          f'Номер телефона: {config.phone}', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Сейчас нужно вас зарегестрирвоать!\n"
                                          "Введите, пожалуйста, свои: Фамилия, Имя, Отчество")
        bot.register_next_step_handler(message, user_name)
def user_name(message):
    config.name = message.text.strip()
    bot.send_message(message.chat.id, "Введите свой номер телефона " + config.name)
    bot.register_next_step_handler(message, user_phone)
def user_phone(message):
    config.phone = message.text.strip()
    config.tg_id = message.from_user.id

    markup = types.InlineKeyboardMarkup()
    bottom1 = types.InlineKeyboardButton('Верно', callback_data='true_enter')
    bottom2 = types.InlineKeyboardButton('Неверно', callback_data='false_enter')
    markup.row(bottom1,bottom2)

    bot.send_message(message.chat.id, f'Мы закончили небольшую регистрацию🔥')
    bot.send_message(message.chat.id,f'Проверьте, пожалуйста, ваши данные на корректность:\n ФИО: {config.name}\n Номер телефона: {config.phone}', reply_markup=markup)


@bot.message_handler(commands=['advice'])
@bot.message_handler(func=lambda message: message.text.lower() == 'консультация')
def consult(message):
    bot.send_message(config.manager_id, f'Информация по заказу с артикулом - {token}\n'
                                        f'ФИО - {config.name}\n'
                                        f'Номер телефона - {config.phone}')

    bot.send_message(message.chat.id,f'Перейдите по следующей ссылке, чтобы связаться с менеджером. Обязательно отправьте артикул своего товара, чтобы менеджер смог вас понять)\n\n'
                                     f'<b>Переходи сюда</b> -> https://t.me/res12245', parse_mode='html')


@bot.message_handler(commands=['edit_name'])
@bot.message_handler(func=lambda message: message.text.lower() == 'фио')
def name(message):
    bot.send_message(message.chat.id, "Введите, пожалуйста, свои: Фамилия, Имя, Отчество")
    bot.register_next_step_handler(message, get_name)
def get_name(message):
    config.name = message.text.strip()
    editUser.update_user_name(config.name, config.tg_id)
    markup = types.InlineKeyboardMarkup()
    bottom1 = types.InlineKeyboardButton('Верно', callback_data='true_enter')
    bottom2 = types.InlineKeyboardButton('Неверно', callback_data='edit_data')
    markup.row(bottom1, bottom2)
    bot.send_message(message.chat.id,f'Проверьте, пожалуйста, ваши данные на корректность:\n ФИО: {config.name}\n Номер телефона: {config.phone}',reply_markup=markup)



@bot.message_handler(commands=['edit_phone'])
@bot.message_handler(func=lambda message: message.text.lower() == 'номер')
def phone(message):
    bot.send_message(message.chat.id, "Введите, пожалуйста, новый номер")
    bot.register_next_step_handler(message, get_phone)
def get_phone(message):
    config.phone = message.text.strip()
    editUser.update_user_name(config.phone, config.tg_id)
    markup = types.InlineKeyboardMarkup()
    bottom1 = types.InlineKeyboardButton('Верно', callback_data='true_enter')
    bottom2 = types.InlineKeyboardButton('Неверно', callback_data='edit_data')
    markup.row(bottom1, bottom2)
    bot.send_message(message.chat.id,f'Проверьте, пожалуйста, ваши данные на корректность:\n ФИО: {config.name}\n Номер телефона: {config.phone}',reply_markup=markup)



@bot.message_handler(commands=['edit_all'])
@bot.message_handler(func=lambda message: message.text.lower() == 'все')
def name_from_all(message):
    bot.send_message(message.chat.id, "Введите, пожалуйста, свои: Фамилия, Имя, Отчество")
    bot.register_next_step_handler(message, get_name_from_all)
def get_name_from_all(message):
    config.name = message.text.strip()
    bot.send_message(message.chat.id, "Введите, пожалуйста, новый номер")
    bot.register_next_step_handler(message, get_all)
def get_all(message):
    config.phone = message.text.strip()
    editUser.update_user_all(config.phone, config.name, config.tg_id)
    markup = types.InlineKeyboardMarkup()
    bottom1 = types.InlineKeyboardButton('Верно', callback_data='true_enter')
    bottom2 = types.InlineKeyboardButton('Неверно', callback_data='edit_data')
    markup.row(bottom1, bottom2)
    bot.send_message(message.chat.id,f'Проверьте, пожалуйста, ваши данные на корректность:\n ФИО: {config.name}\n Номер телефона: {config.phone}',reply_markup=markup)



@bot.message_handler(content_types = ['photo', 'video', 'audio', 'sticker', 'emoji'])
def noneContent(message):
    bot.reply_to(message, f'Извините, {message.from_user.first_name}, я не умею обрабатывать такие сообщения((')


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'status':
        bot.send_message(callback.message.chat.id,'Перенаправляю Вас на моего коллегу, регистрация в один клик, далее введите <b>/add (номер вашего заказа)</b>, а затем <b>/tracks</b>. Также напоминаю, что по правилам нашего магазина (далее правила по срокам доставки)\n\n' + "Ссылка -> https://t.me/RLabbot",parse_mode='html')
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
    elif callback.data == 'order':
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Заказ")
        markup1.add(item1)
        bot.send_message(callback.message.chat.id, "Чтобы сделать заказ, отправьте команду <b>/order</b> или нажмите на кнопку <b>Заказ</b>" , parse_mode='html', reply_markup=markup1)
    elif callback.data == 'true_enter':
        if (not config.user_data):
            conn = sqlite3.connect('shop.sql')
            cur = conn.cursor()
            cur.execute(f"INSERT INTO users(name, tgId, phone) VALUES ('{config.name}', '{config.tg_id}', '{config.phone}')")
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
        bot.delete_message(callback.message.chat.id,callback.message.message_id)
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






@bot.message_handler()
def info(message):
    if (message.text.lower() == 'привет'):
        bot.send_message(message.chat.id, "Добро пожаловать, {0.first_name}!\n "
                                          "Я - <b>электронный сотрудник магазина по продаже тканей</b>, бот созданный чтобы помочь тебе сделать заказ.".format(message.from_user, bot.get_me()),
                         parse_mode='html')
    elif (message.text.lower() == 'id'):
        bot.reply_to(message, f'ID: {message.from_user.id}')
    else:
        bot.reply_to(message, f'Извините, {message.from_user.first_name}, я не умею обрабатывать такие сообщения((')




bot.polling(none_stop = True)