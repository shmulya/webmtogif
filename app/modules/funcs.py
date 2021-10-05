import requests
from app.main import bot, config
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.modules.converter import Converter
import logging
from os import remove, getcwd


def tiktok(message, link):
    url = config['tiktok']['url']
    msg = bot.send_message(chat_id=message.chat.id, text='Загрузка видеозаписи...')
    try:
        r = requests.post(url=url, data={'url': link}).json()
    except Exception as e:
        logging.error(f'Tiktok downloading error: {e}')
        bot.edit_message(chat_id=msg.chat.id, message_id=msg.id, text='Не удалось загрузить видео.')
    else:
        if r['status'] == 'success':
            bot.edit_message(chat_id=msg.chat.id, message_id=msg.id, text='Отправка видео...')
            try:
                vid = open(r['path'], 'rb')
                bot.send_video(chat_id=msg.chat.id, data=vid)
            except Exception as e:
                logging.error(f'Video uploading error: {e}')
                bot.edit_message(chat_id=msg.chat.id, message_id=msg.id, text='Ошибка при отправке видео.')
            else:
                bot.delete_message(chat_id=msg.chat.id, message_id=msg.id)
            finally:
                remove(r['path'])


def get_video(message, link):
    c = Converter()
    msg = bot.send_message(chat_id=message.chat.id, text='Загрузка видеозаписи...')
    try:
        r = c.download(url=link, name=msg.chat.id)
    except Exception as e:
        logging.error(f'File downloading error: {e}')
        bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.id, text='Не удалось загрузить видео')
    else:
        if r['status'] == 'success':
            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(InlineKeyboardButton(text='mp4', callback_data=f'video_{r["path"]}'),
                         InlineKeyboardButton(text='gif', callback_data=f'animation_{r["path"]}'))
            keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'cancel_{r["path"]}'))
            bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.id, reply_markup=keyboard,
                                  text='Видео успешно загружено. Выберите действие.')
        else:
            logging.error(f'File downloading error: {r["error"]}')
            bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.id, text='Не удалось загрузить видео')


def convert(call):
    c = Converter()
    if 'video' in call.data:
        path = getcwd() + '/files/' + call.data.split('_')[1]
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Конвертирование...')
        try:
            r = c.to_mp4(filename=path)
        except Exception as e:
            logging.error(f'File converting error: {e}')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text='Ошибка при конвертировании.')
        else:
            if r['status'] == 'success':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text='Отправка видео...')
                try:
                    vid = open(r['path'], 'rb')
                    bot.send_video(chat_id=call.message.chat.id, data=vid)
                except Exception as e:
                    logging.error(f'File converting error: {e}')
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                          text='Ошибка при отправке.')
                else:
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
                finally:
                    c.delete(r['path'])
            else:
                logging.error(f'File converting error: {r["error"]}')
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text='Ошибка при конвертировании.')
        finally:
            c.delete(path)

    elif 'animation' in call.data:
        path = getcwd() + '/files/' + call.data.split('_')[1]
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Конвертирование...')
        try:
            r = c.to_gif(filename=path)
        except Exception as e:
            logging.error(f'File converting error: {e}')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text='Ошибка при конвертировании.')
        else:
            if r['status'] == 'success':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text='Отправка анимации...')
                try:
                    vid = open(r['path'], 'rb')
                    bot.send_video(chat_id=call.message.chat.id, data=vid)
                except Exception as e:
                    logging.error(f'File converting error: {e}')
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                          text='Ошибка при отправке.')
                else:
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
                finally:
                    c.delete(r['path'])
            else:
                logging.error(f'File converting error: {r["error"]}')
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text='Ошибка при конвертировании.')
        finally:
            c.delete(path)

    elif 'cancel' in call.data:
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
        path = getcwd() + '/files/' + call.data.split('_')[1]
        c.delete(path)