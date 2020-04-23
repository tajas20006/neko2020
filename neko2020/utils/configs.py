import os
from copy import deepcopy
from functools import reduce

import yaml

from neko2020.utils import files

config = None


def deep_merge(*dicts, update=False):
    def merge_into(d1, d2):
        for key in d2:
            if key not in d1 or not isinstance(d1[key], dict):
                d1[key] = deepcopy(d2[key])
            else:
                d1[key] = merge_into(d1[key], d2[key])
        return d1

    if update:
        return reduce(merge_into, dicts[1:], dicts[0])
    else:
        return reduce(merge_into, dicts, {})


def read_config(config_file=None):
    default_config_file = os.path.join(
        files.get_project_root(), "config", "default_config.yml"
    )

    with open(default_config_file) as f:
        default_config = yaml.load(f, Loader=yaml.BaseLoader)
    if config_file is None:
        return default_config

    with open(config_file) as f:
        user_config = yaml.load(f, Loader=yaml.BaseLoader)
    return deep_merge(default_config, user_config)


def get_value(config_path):
    this_config = config
    if this_config is None:
        this_config = read_config()
    if type(config_path) is not list:
        config_path = config_path.split(".")
    for path in config_path:
        this_config = this_config.get(path, None)
    return this_config


def get_int(config_path):
    return int(get_value(config_path))


def get_string(config_path):
    return str(get_value(config_path))
