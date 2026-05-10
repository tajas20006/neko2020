import os
import random


def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def get_user_resource_dir():
    xdg_config_home = os.getenv(
        "XDG_CONFIG_HOME",
        os.path.join(os.path.expanduser("~"), ".config"),
    )
    return os.path.join(xdg_config_home, "neko2020", "resources")


def select_random_directory(basedir):
    entries = os.listdir(basedir)
    directories = [
        f for f in entries if os.path.isdir(os.path.join(basedir, f))
    ]
    return random.choice(directories)


def select_random_directory_merged(project_basedir, user_basedir):
    dirs = set()
    if os.path.isdir(project_basedir):
        dirs.update(
            f
            for f in os.listdir(project_basedir)
            if os.path.isdir(os.path.join(project_basedir, f))
        )
    if os.path.isdir(user_basedir):
        dirs.update(
            f
            for f in os.listdir(user_basedir)
            if os.path.isdir(os.path.join(user_basedir, f))
        )
    return random.choice(list(dirs))
