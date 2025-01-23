# -*-coding:Utf-8 -*
""" json encoders """

import json
from json import JSONEncoder
from typing import Any

from common import singleton

class ListOfObjectsEncoder(JSONEncoder):
    def default(self, o:Any)-> (list | Any):
        if isinstance(o, set):
            return list(o)
        #return json.JSONEncoder.default(self, obj)
        return o.__dict__

class JsonEncodersUtils(metaclass=singleton.Singleton):

    @staticmethod
    def serialize_list_objects_in_json(list_objects:list[Any], json_file_full_path:str) -> None:
        json_file = open(json_file_full_path, "w", encoding="utf-8")

        result_json_dump = json.dumps(list_objects, indent=4, cls=ListOfObjectsEncoder)

        json_file.write(result_json_dump)

        json_file.close()
