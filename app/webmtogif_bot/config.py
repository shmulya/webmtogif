import os
from pathlib import Path
from typing import Union

import yaml

PROJECT_ROOT = Path(__file__).parent / "../"
CONFIG_PATH = os.environ.get('BOT_CONFIG', PROJECT_ROOT / './config/config.yml')

class Config:
    def __init__(self, config_path: Union[str, Path]):
        try:
            self.config = yaml.load(open(config_path, 'r').read())
        except IOError:
            self.config = {}

    def __getitem__(self, item):
        return self.config[item]

    def get(self, item, default=None):
        return self.config.get(item, default)


config = Config(CONFIG_PATH)
