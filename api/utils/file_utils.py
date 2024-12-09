from io import BytesIO
import mimetypes
import os
import json
from typing import Union
from urllib.parse import urlparse


f


def read_file(file_path, encoding="utf-8", errors=None):
    """
    Returns a file object.
    """

    try:
        with open(file_path, "r", encoding=encoding, errors=errors) as file:
            return file.read()

    except FileNotFoundError:
        raise ValueError("File not found")

    except (ValueError, json.JSONDecodeError, Exception) as e:
        return f"An error occurred: {e}, {e.__class__}"
