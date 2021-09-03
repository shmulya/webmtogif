import re

import requests

from ..config import config


class PikabuVideo:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
        }
        self.cookies = config.get('pikabu_cookies', {})


    def search_video(self, url):
        res = requests.get(url, headers=self.headers, cookies=self.cookies)
        if 200 <= res.status_code < 400:
            html = res.text
            data_webm = re.search('data-webm="(\S+)"', html)
            if data_webm is not None:
                webm_url = data_webm.group(1)
                return {'status': 'success', 'webm-url': webm_url}
            else:
                return {'status': 'error', 'error': 'Webm url did not found'}
        else:
            return {'status': 'error', 'error': f'Status code {res.status_code}'}
