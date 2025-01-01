# -*-coding:Utf-8 -*

import importlib.util, sys

import os
cwd = os.getcwd()

sys.path.insert(1, os.getcwd())
sys.path.insert(1, "Dependencies/Common")
sys.path.insert(1, "Dependencies/Logger")

import logger_config

import urllib.request
from urllib.error import URLError, HTTPError

def get_url_filze_size(link:str)-> int:
    try:
        with urllib.request.urlopen(link) as url_open:
            return True, url_open.length
    except HTTPError as e:
        # do something
        logger_config.print_and_log_error(f'Error code: {e.code}')
        return False, f'Error! {e}'
    except URLError as e:
        # do something
        logger_config.print_and_log_error(f'Error code: {e.code}')
        return False, f'Error! {e}'