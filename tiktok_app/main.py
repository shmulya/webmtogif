from flask import Flask, request
from time import sleep
from json import dumps
from modules.tiktokvideo import TikTokVideo


app = Flask(__name__, static_url_path='')

THREAD_RUNNING = False


@app.route('/download_video', methods=['POST', 'GET'])
def download_from_tiktok():
    global THREAD_RUNNING
    url = request.form.get('url')
    tiktok = TikTokVideo(url=url)

    while THREAD_RUNNING:
        sleep(1)

    THREAD_RUNNING = True
    result = tiktok.download()
    THREAD_RUNNING = False

    if result['status'] == 'success':
        response = app.response_class(
            response=dumps(result),
            status=200,
            content_type='application/json'
        )
    else:
        response = app.response_class(
            response=dumps(result),
            status=500,
            content_type='application/json'
        )

    return response


if __name__ == '__main__':
    app.run('0.0.0.0')
