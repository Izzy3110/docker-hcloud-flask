import os


def safe_create_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
        if os.path.isdir(path):
            return True
        return False
    return False
