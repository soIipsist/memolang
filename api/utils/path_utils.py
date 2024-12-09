import os


def is_valid_dir(path, raise_error=True):
    if os.path.isdir(path):
        return path
    else:
        if raise_error:
            raise NotADirectoryError(path)


def is_valid_path(path, raise_error=True):
    if not os.path.exists(path):
        if raise_error:
            raise FileNotFoundError(path)
        return None
    return path
