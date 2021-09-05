import logging
from datetime import datetime
from json import dumps
from os import getcwd, remove
from threading import Thread

import requests

from .config import config
from .modules.bot import Bot, Update
from .modules.converter import Converter
from .modules.mysql_connector import MysqlCollector

logging.basicConfig(filename='bot.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

bot = Bot(config['token'])


def register_user(user_id):
    collector = MysqlCollector(server=config['server'], username=config['username'],
                               passwd=config['passwd'], db=config['db'])
    r = collector.select(table='bot_stats', where=f'user_id={user_id}')
    if r['status']:
        if not r['data']:
            time = datetime.isoformat(datetime.now())
            r = collector.insert(table='bot_stats', data={'user_id': user_id, 'time': time})
            logging.info(f'New user {user_id} added')
    collector.close()
    return r


def get_stats(u, upd):
    if u['message']['from']['id'] not in config['admins']:
        bot.send_message(chat_id=upd.chat_id, message='Нет доступа')
        logging.warning(f'User with id {u["message"]["from"]["id"]} has no rights to show stats')
        return {'status': False, 'data': 'Unauthorized'}
    else:
        collector = MysqlCollector(server=config['server'], username=config['username'],
                                   passwd=config['passwd'], db=config['db'])
        r = collector.select(table='bot_stats', cols=['user_id'])
        return r


def video(u):
    c = Converter()
    if 'video' in u.callback['data']:
        path = getcwd() + '/files/' + u.callback['data'].split('_')[1]
        bot.edit_message(u.chat_id, u.callback['message_id'], 'Конвертирование...')
        try:
            result = c.to_mp4(path)
        except Exception as e:
            logging.error('File converting error: ' + str(e))
            bot.edit_message(u.chat_id, u.callback['message_id'], 'Ошибка при конвертировании.')
            c.delete(path)
        else:
            if result['status'] == 'success':
                bot.edit_message(u.chat_id, u.callback['message_id'], 'Отправка видео...')
                try:
                    sending = bot.send_video(u.chat_id, result['path'])
                except Exception as e:
                    logging.error('File uploading error: ' + str(e))
                    bot.edit_message(u.chat_id, u.callback['message_id'], 'Ошибка при отправке.')
                    c.delete(result['path'])
                    c.delete(path)
                else:
                    if sending['status'] == 'ok':
                        bot.delete_message(u.chat_id, u.callback['message_id'])
                        c.delete(path)
                        c.delete(result['path'])
                    else:
                        logging.warning('File uploading error: ' + str(sending['error']))
                        bot.edit_message(u.chat_id, u.callback['message_id'],
                                         'Ошибка при отправке. Возможно, '
                                         'файл имеет слишком большой размер.')
                        c.delete(path)
                        c.delete(result['path'])
            else:
                logging.warning('File converting error: ' + str(result['error']))
                bot.edit_message(u.chat_id, u.callback['message_id'], 'Ошибка при конвертировании.')
                c.delete(path)

    elif 'animation' in u.callback['data']:
        path = getcwd() + '/files/' + u.callback['data'].split('_')[1]
        bot.edit_message(u.chat_id, u.callback['message_id'], 'Конвертирование...')
        try:
            result = c.to_gif(path)
        except Exception as e:
            logging.error('File converting error: ' + str(e))
            bot.edit_message(u.chat_id, u.callback['message_id'], 'Ошибка при конвертировании.')
            c.delete(path)
        else:
            if result['status'] == 'success':
                bot.edit_message(u.chat_id, u.callback['message_id'], 'Отправка анимации...')
                try:
                    sending = bot.send_animation(u.chat_id, result['path'])
                except Exception as e:
                    logging.error('File uploading error: ' + str(e))
                    bot.edit_message(u.chat_id, u.callback['message_id'], 'Ошибка при отправке.')
                    c.delete(result['path'])
                    c.delete(path)
                else:
                    if sending['status'] == 'ok':
                        bot.delete_message(u.chat_id, u.callback['message_id'])
                        c.delete(path)
                        c.delete(result['path'])
                    else:
                        logging.warning('File uploading error: ' + str(sending['error']))
                        bot.edit_message(u.chat_id, u.callback['message_id'],
                                         'Ошибка при отправке. Возможно, '
                                         'файл имеет слишком большой размер.')
                        c.delete(path)
                        c.delete(result['path'])
            else:
                logging.warning('File converting error: ' + str(result['error']))
                bot.edit_message(u.chat_id, u.callback['message_id'], 'Ошибка при конвертировании.')
                c.delete(path)

    elif 'cancel' in u.callback['data']:
        bot.delete_message(u.chat_id, u.callback['message_id'])
        c.delete(getcwd() + '/files/' + u.callback['data'].split('_')[1])


def formatting(u):
    c = Converter()
    msg_id = bot.send_message(u.chat_id, 'Загрузка видеозаписи...')['message_id']
    try:
        result = c.download(u.url, u.chat_id)
    except Exception as e:
        logging.error('File loading error: ' + str(e))
        bot.edit_message(u.chat_id, msg_id,
                         'Не удалось загрузить видео. Возможно, указана неверная ссылка.')
    else:
        if result['status'] == 'success':
            keyboard = {
                'inline_keyboard': [
                    [
                        {
                            'text': 'mp4',
                            'callback_data': 'video_' + result['path']
                        },
                        {
                            'text': 'gif',
                            'callback_data': 'animation_' + result['path']
                        },
                    ],
                    [
                        {
                            'text': 'Отмена',
                            'callback_data': 'cancel_' + result['path']
                        }
                    ]
                ]
            }
            bot.edit_message(u.chat_id, msg_id, 'Видео успешно загружено. Выберите действие.',
                             dumps(keyboard))
        else:
            logging.warning('File loading error: ' + str(result['error']))
            bot.edit_message(u.chat_id, msg_id,
                             'Не удалось загрузить видео. Возможно, файл, находящийся по ссылке, '
                             'имеет расширение отличное от webm.')


def tiktok(u):
    msg_id = bot.send_message(u.chat_id, 'Загрузка видеозаписи...')['message_id']
    try:
        result = requests.post(url=config['url'], data={'url': u.url}).json()
    except Exception as e:
        logging.error(f'TikTok downloading error: {e}')
        bot.edit_message(u.chat_id, msg_id, 'Не удалось загрузить видео.')
    else:
        if result['status'] == 'success':
            bot.edit_message(u.chat_id, msg_id, 'Отправка видео...')
            try:
                sending = bot.send_video(u.chat_id, result['path'])
            except Exception as e:
                logging.error(f'Video uploading error: {e}')
                bot.edit_message(u.chat_id, msg_id, 'Ошибка при отправке видео.')
                remove(result['path'])
            else:
                if sending['status'] == 'ok':
                    bot.delete_message(u.chat_id, msg_id)
                    remove(result['path'])
                else:
                    logging.error(f'Video uploading error: {sending["error"]}')
                    bot.edit_message(u.chat_id, msg_id, 'Ошибка при отправке видео.')
        else:
            bot.edit_message(u.chat_id, msg_id, 'Не удалось загрузить видео.')
            logging.error(f'TikTok downloading error: {result["error"]}')


def init():
    updates = bot.get_updates()
    if updates['status'] != 'ok':
        logging.fatal(f'Getting updates error: {updates["error"]}')
        raise Exception(updates['error'])
    updates['updates'] = [updates['updates'][-1]]
    offset = updates['last_update_id'] + 1
    print('Bot started')
    logging.info('Bot started')
    while True:
        for i in updates['updates']:
            update = Update(i)
            if i.get('message') is not None:
                user_id = i['message']['from']['id']
            elif i.get('callback_query') is not None:
                user_id = i['callback_query']['from']['id']
            if user_id:
                result = register_user(user_id)
                if not result['status']:
                    logging.error(f'User registration error: {result["data"]}')
            if update.type == 'command':
                if update.command == '/start':
                    bot.send_message(update.chat_id,
                                     'Этот бот умеет конвертировать webm видео в формат gif и mp4,'
                                     'а также загружать видео из TikTok.\n\n'
                                     '/help чтобы узнать подробности.')
                elif update.command == '/help':
                    message = 'Чтобы конвертировать webm видео, отправь боту ссылку на него и выбери нужное ' \
                              'действие.\n\n' \
                              'Чтобы загрузить видео из TikTok, просто отправь на него ссылку\n\n' \
                              'Также можно загружать видео из Pikabu, просто отправив ссылку на нужный пост.'
                    bot.send_message(update.chat_id, message)
                elif update.command == '/stats':
                    result = get_stats(i, update)
                    if result['status']:
                        bot.send_message(update.chat_id,
                                         f'Всего пользователей: {len(result["data"])}')
                    else:
                        logging.error(f'Getting stats error: {result["data"]}')
                        bot.send_message(update.chat_id, 'Произошла ошибка.')

            elif update.type == 'url':
                if 'tiktok' in update.url:
                    t = Thread(target=tiktok, args=(update,))
                    t.start()
                else:
                    t = Thread(target=formatting, args=(update,))
                    t.start()

            elif update.type == 'callback_query':
                t = Thread(target=video, args=(update,))
                t.start()

        for i in range(10):
            updates = bot.get_updates(offset)
            if updates['status'] != 'ok':
                if i < 9:
                    logging.error(f'Getting updates error {i}/9: {updates["error"]}')
                else:
                    logging.fatal(f'Getting updates error {i}/9: {updates["error"]}')
            else:
                break
            i += 1

        offset = updates['last_update_id'] + 1
