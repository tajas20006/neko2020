import os
import random


def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def select_random_directory(basedir):
    files = os.listdir(basedir)
    directories = [f for f in files if os.path.isdir(os.path.join(basedir, f))]
    return random.choice(directories)
