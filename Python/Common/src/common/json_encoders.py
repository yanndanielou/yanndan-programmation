# -*-coding:Utf-8 -*
"""json encoders"""
import json
import textwrap
from datetime import datetime
from json import JSONEncoder
from pathlib import Path
from typing import Any

from logger import logger_config

from common import singleton


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

    @staticmethod
    def serialize_list_objects_in_json_with_chunks(list_objects: list[Any], json_file_full_path: str) -> None:
        chunk_size = 10000

        # If list is small enough, use single file
        if len(list_objects) <= chunk_size:
            with logger_config.stopwatch_with_label(f"Serialize {len(list_objects)} in {json_file_full_path}"):
                with open(json_file_full_path, "w", encoding="utf-8") as json_file:
                    result_json_dump = json.dumps(list_objects, indent=4, cls=ListOfObjectsEncoder)
                    json_file.write(result_json_dump)
        else:
            # Split into chunks and create multiple files
            base_path = Path(json_file_full_path)
            stem = base_path.stem
            suffix = base_path.suffix
            parent = base_path.parent

            for chunk_index in range(0, len(list_objects), chunk_size):
                chunk = list_objects[chunk_index : chunk_index + chunk_size]
                chunk_number = chunk_index // chunk_size

                # Create filename with chunk number
                chunk_file_path = parent / f"{stem}_{chunk_number}{suffix}"

                with logger_config.stopwatch_with_label(f"Serialize {len(chunk)} in {chunk_file_path}"):
                    with open(chunk_file_path, "w", encoding="utf-8") as json_file:
                        result_json_dump = json.dumps(chunk, indent=4, cls=ListOfObjectsEncoder)
                        json_file.write(result_json_dump)
