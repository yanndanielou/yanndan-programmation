# -*-coding:Utf-8 -*

import importlib.util, sys

import os
cwd = os.getcwd()

sys.path.insert(1, os.getcwd())
sys.path.insert(1, "Dependencies/Common")

#importlib.util.spec_from_loader
#string_utils = importlib.util.spec_from_file_location("string_utils", "string_utils.py")

import string_utils #pylint: disable=wrong-import-position
#import Dependencies.Common.string_utils

def file_extension_from_full_path(full_path:str)->str:
    """ returns the file extension if any"""
    last_part_of_path = string_utils.right_part_after_last_occurence(full_path, "/")

    if not "." in last_part_of_path:
        return None

    after_point = string_utils.right_part_after_last_occurence(last_part_of_path, ".")
    return "." + after_point
