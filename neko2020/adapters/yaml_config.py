import os
from copy import deepcopy
from functools import reduce

import yaml

from neko2020.application.ports import IConfigProvider


def _deep_merge(*dicts):
    def merge_into(d1, d2):
        for key in d2:
            if key not in d1 or not isinstance(d1[key], dict):
                d1[key] = deepcopy(d2[key])
            else:
                d1[key] = merge_into(d1[key], d2[key])
        return d1

    return reduce(merge_into, dicts, {})


class YamlConfigProvider(IConfigProvider):
    def __init__(self, default_path: str, user_path: str):
        self._default_path = default_path
        self._user_path = user_path
        self._config: dict = {}

    def reload(self) -> None:
        with open(self._default_path) as f:
            config = yaml.load(f, Loader=yaml.BaseLoader)
        if os.path.exists(self._user_path):
            with open(self._user_path) as f:
                user_config = yaml.load(f, Loader=yaml.BaseLoader)
            config = _deep_merge(config, user_config)
        self._config = config

    def _get_value(self, config_path):
        node = self._config
        if not isinstance(config_path, list):
            config_path = config_path.split(".")
        for path in config_path:
            node = node.get(path, None)
        return node

    def get_int(self, path: str) -> int:
        return int(self._get_value(path))

    def get_float(self, path: str) -> float:
        return float(self._get_value(path))

    def get_string(self, path: str) -> str:
        return str(self._get_value(path))
