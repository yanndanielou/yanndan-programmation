# -*-coding:Utf-8 -*

import importlib.util, sys

import humanize

import os
cwd = os.getcwd()

sys.path.insert(1, os.getcwd())
sys.path.insert(1, "Dependencies/Common")
sys.path.insert(1, "Dependencies/Logger")

import logger_config

import urllib.request
from urllib.error import URLError, HTTPError

def get_url_file_size(link:str)-> tuple[bool,int|str]:
    """ get_url_file_size """
    try:
        with urllib.request.urlopen(link) as url_open:
            return True, url_open.length
    except HTTPError as e:
        # do something
        logger_config.print_and_log_error(f'Error code: {e.code}')
        return False, f'Error! {e}'
    except URLError as e:
        # do something
        logger_config.print_and_log_error(f'Error code: {e}')
        return False, f'Error! {e}'

def convert_bits_to_human_readable_size(size_as_bits:int)-> str:
    """ https://stackoverflow.com/questions/1094841/get-a-human-readable-version-of-a-file-size """
    return humanize.naturalsize(size_as_bits)
