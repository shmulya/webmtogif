from gevent import monkey
monkey.patch_all()
import requests
from TikTokApi import TikTokApi
from os import urandom


class TikTokVideo:
    def __init__(self, url):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
        self.url = self.normalise_url(url)
        self.api = TikTokApi.get_instance()
        self.device_id = self.api.generate_device_id()

    def download(self):
        try:
            video = self.api.get_video_by_url(video_url=self.url, custom_device_id=self.device_id)
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
        else:
            path = 'files/' + urandom(3).hex() + '.mp4'

            with open(path, 'wb') as file:
                file.write(video)
                file.close()

            return {'status': 'success', 'path': path}

    def normalise_url(self, url):
        r = requests.get(url, headers=self.headers)
        return r.url
