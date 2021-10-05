import telebot
import yaml
from modules.mysql_connector import MysqlCollector
from modules.funcs import tiktok, get_video, convert
from datetime import datetime
import logging

config = yaml.safe_load(open('config/config.yml'))

telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(**config['bot'])


@bot.middleware_handler(update_types=['message'])
def registration(bot_instance, message):
    collector = MysqlCollector(**config['sql'])
    user_id = message.from_user.id
    r = collector.select(table='users', where=f'user_id={user_id}')
    if r['status']:
        if r['data']:
            time = datetime.isoformat(datetime.now())
            collector.insert(table='users', data={'user_id': user_id, 'time': time})
            logging.info(f'New user {user_id} registered')
    else:
        logging.error(f'User registration error: {r["data"]}')
    collector.close()


@bot.message_handler(commands=['start'])
def start(message):
    text = 'Этот бот умеет конвертировать webm видео в формат gif и mp4,' \
           'а также загружать видео из TikTok.\n\n' \
           '/help чтобы узнать подробности.'
    bot.send_message(chat_id=message.chat.id, text=text)


@bot.message_handler(commands=['help'])
def info(message):
    text = 'Чтобы конвертировать webm видео, отправь боту ссылку на него и выбери нужное ' \
           'действие.\n\n' \
           'Чтобы загрузить видео из TikTok, просто отправь на него ссылку\n\n' \
           'Также можно загружать видео из Pikabu, просто отправив ссылку на нужный пост.'
    bot.send_message(chat_id=message.chat.id, text=text)


@bot.message_handler(func=lambda message: message.entities and message.entities[0].type == 'url')
def url(message):
    entity = message.entities[0]
    link = message.text[entity.offset:entity.offset + entity.length]
    if 'tiktok' in link:
        tiktok(message=message, link=link)
    else:
        get_video(message=message, link=link)


@bot.message_handler(commands=['stats'])
def stats(message):
    user_id = message.from_user.id
    if user_id not in config['admins']:
        bot.send_message(chat_id=message.chat.id, text='Нет доступа')
        logging.warning(f'User with id {user_id} has no rights to show stats')
    else:
        collector = MysqlCollector(**config['sql'])
        r = collector.select(table='bot_stats', cols=['user_id'])
        if r['status']:
            bot.send_message(chat_id=message.chat.id, text=f'Всего пользователей: {len(r["data"])}')
        else:
            bot.send_message(chat_id=message.chat.id, text='Произошла ошибка')
            logging.error(f'Getting stats error: {r["data"]}')


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if 'video' in call.data or 'animation' in call.data or 'cancel' in call.data:
        convert(call=call)


if __name__ == '__main__':
    bot.infinity_polling(long_polling_timeout=5, timeout=10)
