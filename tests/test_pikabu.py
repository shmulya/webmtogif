from app.webmtogif_bot.modules.pikabu import PikabuVideo


def test_search_video():
    p = PikabuVideo()
    result = p.search_video("https://pikabu.ru/story/ot_menya_eshche_nikto_ne_ukhodil_8445100")
    assert result == {
        'status': 'success',
        'webm-url': 'https://cs14.pikabu.ru/video/2021/08/31/1630417166233233358_704x1280.webm'
    }


def test_search_video_nsfw():
    p = PikabuVideo()
    result = p.search_video("https://pikabu.ru/story/st_louis_8446551")

    assert result == {
        'status': 'success',
        'webm-url': 'https://cs14.pikabu.ru/video/2021/09/01/1630481189271114975_1280x720.webm'
    }
