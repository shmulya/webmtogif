import yaml
from modules.bot import Bot, Update
from modules.converter import Converter
from threading import Thread
import re
import logging
from json import dumps
from os import getcwd

logging.basicConfig(filename='bot.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

config = yaml.load(open('./config/config.yml', 'r').read())
bot = Bot(config['token'])


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
                        bot.edit_message(u.chat_id, u.callback['message_id'], 'Ошибка при отправке. Возможно, '
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
                        bot.edit_message(u.chat_id, u.callback['message_id'], 'Ошибка при отправке. Возможно, '
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
        bot.edit_message(u.chat_id, msg_id, 'Не удалось загрузить видео. Возможно, указана неверная ссылка.')
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
            bot.edit_message(u.chat_id, msg_id, 'Видео успешно загружено. Выберите действие.', dumps(keyboard))
        else:
            logging.warning('File loading error: ' + str(result['error']))
            bot.edit_message(u.chat_id, msg_id, 'Не удалось загрузить видео. Возможно, файл, находящийся по ссылке, '
                                                'имеет расширение отличное от webm.')


if __name__ == '__main__':
    updates = bot.get_updates()
    if updates['status'] != 'ok':
        logging.fatal('Getting updates error: ' + updates['error'])
        raise Exception(updates['error'])
    updates['updates'] = [updates['updates'][-1]]
    offset = updates['last_update_id'] + 1
    print('Bot started')
    logging.info('Bot started')
    while True:
        for i in updates['updates']:
            update = Update(i)
            if update.type == 'command':
                if update.command == '/start':
                    bot.send_message(update.chat_id, 'Этот бот умеет конвертировать видео из webm в mp4 или gif!\n\n'
                                                     '/help чтобы узнать подробности.')

                elif update.command == '/help':
                    message = 'Этот бот умеет ковертировать видео из формата webm в mp4 или gif!\n\n' \
                              'Чтобы начать конвертацию, отправь ссылку на видео и выбери, что хочешь с ним сделать.'
                    bot.send_message(update.chat_id, message)

            elif update.type == 'url':
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
