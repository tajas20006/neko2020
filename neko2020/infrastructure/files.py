import os
import random


def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def get_user_config_dir():
    xdg_config_home = os.getenv(
        "XDG_CONFIG_HOME",
        os.path.join(os.path.expanduser("~"), ".config"),
    )
    return os.path.join(xdg_config_home, "neko2020")


def get_user_resource_dir():
    return os.path.join(get_user_config_dir(), "resources")


def _subdirectories(basedir):
    if not os.path.isdir(basedir):
        return set()
    return {
        f
        for f in os.listdir(basedir)
        if os.path.isdir(os.path.join(basedir, f))
    }


def list_animals(project_basedir=None, user_basedir=None):
    """Sorted names of the sprite sets in the bundled and user dirs."""
    if project_basedir is None:
        project_basedir = os.path.join(get_project_root(), "resource")
    if user_basedir is None:
        user_basedir = get_user_resource_dir()
    return sorted(
        _subdirectories(project_basedir) | _subdirectories(user_basedir)
    )


def select_random_directory_merged(project_basedir, user_basedir):
    return random.choice(list_animals(project_basedir, user_basedir))
