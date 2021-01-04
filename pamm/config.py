import os
import logging.config

from ast import literal_eval
from pamm.dataproviders.dataproviders import Dataproviders
from pamm.entrypoints.entrypoints import Entrypoints
from simple_settings import LazySettings

log = logging.getLogger(__name__)


class Config:
    SEPARATOR = '_'
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    CONFIG_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, 'config'))
    MAIN_CONFIG = os.path.join(CONFIG_DIR, 'main.json')
    LOGGING_CONFIG = os.path.join(CONFIG_DIR, 'logging.json')

    def __init__(self, config_path=None):
        self.PREFIX = os.environ.get('SERVICE_CONFIG_PREFIX', '') + '_'
        self.config = self._init_config(config_path)
        self.entrypoints = []

        for e in self.config['entrypoints']:
            entrypoint = Entrypoints(e['type'], e['options'])
            self.entrypoints.append(entrypoint)

        self.repo = Dataproviders(self.config['repository']['type'], self.config['repository']['options'])
        self.options = self.config['service']

    def _init_config(self, config_path):
        def get_config(*args_):
            config_ = LazySettings(*args_).as_dict()
            if 'service' in config_.keys():
                if 'log_level' in config_['service'].keys():
                    config_['logging']['root']['level'] = config_['service']['log_level']
            for k, handler in config_['logging']['handlers'].items():
                if k == 'console':
                    continue
                handler['filename'] = \
                    os.path.join(os.path.abspath(os.path.join(self.PROJECT_ROOT, 'logs')), handler['filename'])
                logs_dirname = os.path.dirname(handler['filename'])
                if not os.path.exists(logs_dirname):
                    os.makedirs(logs_dirname)
            logging.config.dictConfig(config_['logging'])
            return config_

        if config_path is not None:
            return get_config(config_path, self.LOGGING_CONFIG)

        config = get_config(self.MAIN_CONFIG, self.PREFIX + '.environ', self.LOGGING_CONFIG)

        envs = {}
        for key, value in config.items():
            if key.startswith(self.PREFIX):
                if value[0] in ('[', '(', '{'):
                    value = literal_eval(value)
                envs[key.replace(self.PREFIX, '')] = value

        for key, value in envs.items():
            env_path_array = key.lower().split(self.SEPARATOR)
            self._find_and_replace(config, env_path_array, value)
        return config

    def _find_and_replace(self, basic_: any, env_path_array_: list, env_value_: any) -> bool:
        if not len(env_path_array_):
            return False

        env_path_value_ = env_path_array_.pop(0)
        if isinstance(basic_, dict):
            for basic_key in basic_.keys():
                clean_basic_key = ''.join(e for e in basic_key.lower() if e.isalnum())
                if clean_basic_key == env_path_value_:
                    if len(env_path_array_):
                        basic_current = basic_.get(basic_key)
                        return self._find_and_replace(basic_current, env_path_array_, env_value_)
                    else:
                        basic_[basic_key] = env_value_
                        return True
        if isinstance(basic_, list):
            if len(basic_) and int(env_path_value_) in range(0, len(basic_)):
                if len(env_path_array_):
                    basic_current = basic_[int(env_path_value_)]
                    return self._find_and_replace(basic_current, env_path_array_, env_value_)
                else:
                    basic_[int(env_path_value_)] = env_value_
                    return True
        return False
