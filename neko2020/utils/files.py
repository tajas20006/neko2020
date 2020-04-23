import os

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))