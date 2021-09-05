import copy

import pytest



@pytest.fixture()
def config():
    from app.config import config as _config
    backup_conf = copy.deepcopy(_config.config)

    yield _config

    _config.config = backup_conf
