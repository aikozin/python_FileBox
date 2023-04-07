import json


class Config:
    def __init__(self, default_config):
        with open(default_config) as f:
            default_config = json.load(f)
        self.DEBUG = default_config['DEBUG']
        self.MAX_CONTENT_LENGTH = default_config['MAX_CONTENT_LENGTH']
        self.SECRET_KEY = default_config['SECRET_KEY']
        self.TYPE_FILES = default_config['TYPE_FILES']
        self.STATUS_FILES = default_config['STATUS_FILES']
        self.SOURCE_FILES = default_config['SOURCE_FILES']
        self.UPLOAD_FOLDER = default_config['UPLOAD_FOLDER']
        self.LIFE_TIME = default_config['LIFE_TIME']
        self.INFINITY_LIFE_TIME = default_config['INFINITY_LIFE_TIME']
        self.TRASH_COLLECTOR_INTERVAL = default_config['TRASH_COLLECTOR_INTERVAL']
        self.HOST = default_config['DATABASE']['HOST']
        self.NAME = default_config['DATABASE']['NAME']
        self.USER = default_config['DATABASE']['USER']
        self.PASSWORD = default_config['DATABASE']['PASSWORD']

    def update_config(self, local_config):
        with open(local_config, 'r') as f:
            local_config = json.load(f)
        [[setattr(self, nested_key, nested_value) for nested_key, nested_value in value.items()]
         if isinstance(value, dict) else setattr(self, key, value) for key, value in local_config.items()]


config = Config('config_files/default_config.json')
config.update_config('config_files/local_config.json')
