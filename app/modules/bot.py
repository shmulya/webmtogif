import requests


class Bot:
    def __init__(self, token):
        self.url = 'https://api.telegram.org/bot{}/'.format(token)
        try:
            response = requests.get(url=self.url + 'getMe').json()
        except Exception as e:
            raise e
        else:
            if response['ok'] is False:
                raise Exception(f'{response["error_code"]} {response["description"]}')

    def get_updates(self, offset=None, timeout=30):
        params = {'timeout': timeout, 'offset': offset}
        while True:
            try:
                response = requests.get(url=self.url + 'getUpdates', params=params).json()
            except Exception as e:
                return {'status': 'error', 'error': e}
            else:
                if response['ok'] is False:
                    return {'status': 'error', 'error': f'{response["error_code"]} {response["description"]}'}
                else:
                    if len(response['result']) != 0:
                        return {'status': 'ok', 'updates': response['result'],
                                'last_update_id': response['result'][-1]['update_id']}

    def send_message(self, chat_id, text, reply_markup=None):
        params = {'chat_id': chat_id, 'text': text, 'reply_markup': reply_markup}
        try:
            response = requests.get(url=self.url + 'sendMessage', params=params).json()
        except Exception as e:
            return {'status': 'error', 'error': e}
        else:
            if response['ok'] is False:
                return {'status': 'error', 'error': f'{response["error_code"]} {response["description"]}'}
            else:
                return {'status': 'ok', 'message_id': response['result']['message_id']}

    def send_animation(self, chat_id, animation_path):
        params = {'chat_id': chat_id}
        try:
            file = open(animation_path, 'rb')
        except Exception as e:
            return {'status': 'error', 'error': e}
        else:
            pass
        files = {'animation': file}
        try:
            response = requests.post(url=self.url + 'sendAnimation', params=params, files=files).json()
        except Exception as e:
            return {'status': 'error', 'error': e}
        else:
            if response['ok'] is False:
                return {'status': 'error', 'error': f'{response["error_code"]} {response["description"]}'}
            else:
                return {'status': 'ok'}

    def send_video(self, chat_id, video_path):
        params = {'chat_id': chat_id}
        try:
            file = open(video_path, 'rb')
        except Exception as e:
            return {'status': 'error', 'error': e}
        else:
            pass
        files = {'video': file}
        try:
            response = requests.post(url=self.url + 'sendVideo', params=params, files=files).json()
        except Exception as e:
            return {'status': 'error', 'error': e}
        else:
            if response['ok'] is False:
                return {'status': 'error', 'error': f'{response["error_code"]} {response["description"]}'}
            else:
                return {'status': 'ok'}

    def delete_message(self, chat_id, message_id):
        params = {'chat_id': chat_id, 'message_id': message_id}
        try:
            response = requests.get(url=self.url + 'deleteMessage', params=params).json()
        except Exception as e:
            return {'status': 'error', 'error': e}
        else:
            if response['ok'] is False:
                return {'status': 'error', 'error': f'{response["error_code"]} {response["description"]}'}
            else:
                return {'status': 'ok'}

    def edit_message(self, chat_id, message_id, text, reply_markup=None):
        params = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'reply_markup': reply_markup}
        try:
            response = requests.get(url=self.url + 'editMessageText', params=params).json()
        except Exception as e:
            return {'status': 'error', 'error': e}
        else:
            if response['ok'] is False:
                return {'status': 'error', 'error': f'{response["error_code"]} {response["description"]}'}
            else:
                return {'status': 'ok'}

    def answer_callback_query(self, callback_query_id):
        params = {'callback_query_id': callback_query_id}
        try:
            response = requests.get(url=self.url + 'answerCallbackQuery', params=params).json()
        except Exception as e:
            return {'status': 'error', 'error': e}
        else:
            if response['ok'] is False:
                return {'status': 'error', 'error': f'{response["error_code"]} {response["description"]}'}
            else:
                return {'status': 'ok'}


class Update:
    def __init__(self, update):
        self.type = None
        self.text = None
        self.chat_id = None
        self.callback = {}
        self.command = None
        self.url = None

        if 'callback_query' in update:
            self.type = 'callback_query'
            self.chat_id = update['callback_query']['message']['chat']['id']
            self.callback = {
                'id': update['callback_query']['id'],
                'data': update['callback_query']['data'],
                'message_id': update['callback_query']['message']['message_id']
            }

        elif 'message' in update:
            self.chat_id = update['message']['chat']['id']
            self.type = 'message'

            if 'text' in update['message']:
                self.text = update['message']['text']

            if 'entities' in update['message']:
                if update['message']['entities'][0]['type'] == 'bot_command':
                    self.type = 'command'
                    temp = {
                        'offset': update['message']['entities'][0]['offset'],
                        'length': update['message']['entities'][0]['length']
                    }
                    s = temp['offset'] + temp['length']
                    self.command = self.text[temp['offset']:s]

                elif update['message']['entities'][0]['type'] == 'url':
                    self.type = 'url'
                    temp = {
                        'offset': update['message']['entities'][0]['offset'],
                        'length': update['message']['entities'][0]['length']
                    }
                    s = temp['offset'] + temp['length']
                    self.url = self.text[temp['offset']:s]