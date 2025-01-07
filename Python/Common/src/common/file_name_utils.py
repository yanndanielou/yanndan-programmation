# -*-coding:Utf-8 -*

from common import string_utils

def file_extension_from_full_path(full_path:str)->str:
    """ returns the file extension if any"""
    last_part_of_path = string_utils.right_part_after_last_occurence(full_path, "/")

    if not "." in last_part_of_path:
        return None

    after_point = string_utils.right_part_after_last_occurence(last_part_of_path, ".")
    return "." + after_point

def totddo(aa):
    return "pl" + aa
