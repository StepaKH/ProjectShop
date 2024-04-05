import telebot
import config
import takeToken

from telebot import types

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands = ['start', 'main', 'hello'])
def welcome(message):
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



@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'status':
        bot.send_message(callback.message.chat.id,'Перенаправляю Вас на моего коллегу, регистрация в один клик, далее введите <b>/add (номер вашего заказа)</b>, а затем <b>/tracks</b>. Также напоминаю, что по правилам нашего магазина (далее правила по срокам доставки)\n\n' + "Ссылка -> https://t.me/RLabbot",parse_mode='html')
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
    elif callback.data == 'order':
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("/order")
        markup1.add(item1)
        bot.send_message(callback.message.chat.id, "Чтобы сделать заказ, отправьте команду <b>/order</b>", parse_mode='html', reply_markup=markup1)




@bot.message_handler(commands=['order'])
def order(message):
    bot.delete_message(message.chat.id, message.message_id - 2)
    bot.send_message(message.chat.id, "Процесс создания заказа начат. Пожалуйста, следуйте инструкциям.", reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "Введите, пожалуйста, <b>артикул</b> товара\n"
                                      "<b>Пример ввода: 875234</b>\n\n"
                                      "Если вы забыли артикул товара, то можете перейти обратно в основной канал и посмотреть его\n"
                                      "<b>Вот ссылка -> https://t.me/bravissimo_nn</b>", parse_mode='html')




@bot.message_handler(content_types = ['photo', 'video', 'audio', 'sticker', 'emoji'])
def noneContent(message):
    bot.reply_to(message, f'Извините, {message.from_user.first_name}, я не умею обрабатывать такие сообщения((')



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