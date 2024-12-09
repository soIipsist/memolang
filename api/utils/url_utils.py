import re
from urllib.parse import urljoin, urlparse

from pydantic import BaseModel
from sqlalchemy import TypeDecorator, String

from utils.str_utils import remove_quotes
from utils.download_utils import download_file
import os
import requests
import functools


class URL(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not is_valid_url(value):
                raise ValueError(f"Invalid URL: {value}")
        return value


def is_valid_url(url: str):
    """Check if a given string is a valid URL."""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False


def fix_url(url, base_url=None):
    """
    Fix common URL issues (e.g., missing schema).
    If a base_url is provided, convert relative URLs to absolute URLs.
    """
    url = url.strip().strip('"').strip("'")

    if not urlparse(url).scheme:
        url = "http://" + url

    if base_url and not is_valid_url(url):
        url = urljoin(base_url, url)

    if is_valid_url(url):
        return url
    else:
        raise ValueError(f"Invalid URL after processing: {url}")


def get_path_from_url(url: str, directory: str = None, download: bool = True):

    if directory is None:
        directory = os.getcwd()
    path = os.path.join(directory, os.path.basename(url))

    if not os.path.exists(path) and download:
        path = download_file(url, path, return_response=False)

    return path
