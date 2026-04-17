# -*-coding:Utf-8 -*
"""json encoders"""
import textwrap
import json
from json import JSONEncoder
from typing import Any
from datetime import datetime

from common import singleton

from logger import logger_config


class ListOfObjectsEncoder(JSONEncoder):
    def default(self, o: Any) -> list | Any:
        if isinstance(o, set):
            return list(o)
        if isinstance(o, datetime):
            return str(o)
        # return json.JSONEncoder.default(self, obj)
        return o.__dict__


class JsonEncodersUtils(metaclass=singleton.Singleton):

    @staticmethod
    def serialize_list_objects_in_json(list_objects: list[Any], json_file_full_path: str) -> None:

        with logger_config.stopwatch_with_label(f"Serialize {len(list_objects)} in {json_file_full_path}"):
            with open(json_file_full_path, "w", encoding="utf-8") as json_file:
                result_json_dump = json.dumps(list_objects, indent=4, cls=ListOfObjectsEncoder)
                json_file.write(result_json_dump)

    @staticmethod
    def serialize_list_objects_in_json_improved(list_objects: list[Any], json_file_full_path: str) -> None:

        with logger_config.stopwatch_with_label(f"Serialize {len(list_objects)} in {json_file_full_path}"):
            with open(json_file_full_path, "w", encoding="utf-8") as json_file:
                json_file.write("[\n")
                first_item = True

                for item in list_objects:
                    if not first_item:
                        json_file.write(",\n")

                    item_json = json.dumps(item, indent=4, cls=ListOfObjectsEncoder, ensure_ascii=False)
                    json_file.write(textwrap.indent(item_json, "    "))
                    first_item = False

                json_file.write("\n]" if not first_item else "]")
