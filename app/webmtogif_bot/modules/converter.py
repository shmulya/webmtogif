import subprocess
import requests
from os import getcwd, remove
from .pikabu import PikabuVideo

class Converter:

    def __init__(self):
        self.WORKDIR = getcwd()

    def download(self, url, name=None):
        """
        Download source video from _url_
        :param name: filename
        :param url: source video url
        :return: status dict
        """
        if 'https://pikabu.ru/story/' in url:
            pikabu = PikabuVideo()
            video = pikabu.search_video(url)
            if video['status'] == 'success':
                url = video['webm-url']
            elif video['status'] == 'error':
                return {'status': 'error', 'error': video['error']}
        try:
            req = requests.get(url)
            if 200 <= req.status_code < 400:
                source = req.content
            else:
                return {'status': 'error', 'error': 'request code ' + str(req.status_code)}
        except Exception as e:
            return {'status': 'error', 'error': e}
        else:
            filename = url.split('/').pop()
            if filename.split('.').pop() != 'webm':
                return {'status': 'error', 'error': 'wrong extension'}
            if name is not None:
                filename = str(name) + '.webm'
            file = open(self.WORKDIR+'/files/' + filename, 'wb')
            file.write(source)
            file.close()
            return {'status': 'success', 'path': filename}

    def to_gif(self, filename):
        """
        Convert source file to GIF
        :param filename: source file path
        :return:
        """
        filename_gif = ''.join(filename.split('.')[:-1]) + '.gif'
        command = f"/usr/bin/ffmpeg -i {filename} -y " \
                  "-filter_complex " \
                  "'fps=10,scale=320:-1:flags=lanczos,split [o1] [o2];[o1] " \
                  f"palettegen [p]; [o2] fifo [o3];[o3] [p] paletteuse' {filename_gif}"
        try:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL,
                           stderr=open('ffmpeg_error.log', 'a'))
        except Exception as e:
            return {'status': 'error', 'error': e}
        else:
            return {'status': 'success', 'path': filename_gif}

    def to_mp4(self, filename):
        """
        Convert source file to MP4
        :param filename: source file path
        :return: status dict
        """
        filename_mp4 = ''.join(filename.split('.')[:-1]) + '.mp4'
        command = f"/usr/bin/ffmpeg -i {filename} -pix_fmt yuv420p -vcodec libx264 -profile:v main " \
                  f"-crf 25 -strict -2 -y -movflags faststart {filename_mp4}"
        try:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL,
                           stderr=open('ffmpeg_error.log', 'a'))
        except Exception as e:
            return {'status': 'error', 'error': e}
        else:
            return {'status': 'success', 'path': filename_mp4}

    def delete(self, path):
        """
        Delete file path
        :param path: file path
        :return: status dict
        """
        try:
            remove(path)
        except Exception as e:
            return {'status': 'error', 'error': e}
        else:
            return {'status': 'success'}
