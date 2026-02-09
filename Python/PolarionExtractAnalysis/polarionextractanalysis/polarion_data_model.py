import json
from typing import Dict, List, cast
from dataclasses import dataclass
from polarionextractanalysis.constants import PolarionWorkItemType, PolarionAttributeType, PolarionSeverity
from datetime import datetime
from logger import logger_config
from common import string_utils


class PolarionLibrary:
    def __init__(self, input_json_file_path: str) -> None:
        self.all_work_items: List[PolarionWorkItem] = []
        self.all_not_parsed_because_errors_work_items_as_json: List[Dict] = []

        with open(input_json_file_path, "r", encoding="utf-8") as file:
            all_workitems_as_json = json.load(file)

            assert isinstance(all_workitems_as_json, list)
            logger_config.print_and_log_info(f"{len(all_workitems_as_json)} objects found")

        for workitem_as_json in all_workitems_as_json:
            try:
                assert isinstance(workitem_as_json, dict)
                self.all_work_items.append(PolarionWorkItem(workitem_as_json))
            except KeyError as key_err:
                logger_config.print_and_log_exception(key_err)
                self.all_not_parsed_because_errors_work_items_as_json.append(workitem_as_json)
        pass


@dataclass
class PolarionProject:
    identifier: str


@dataclass
class PolarionRelationships:
    type: PolarionAttributeType


class PolarionAttributes:
    def __init__(self, attributes_as_json: Dict) -> None:
        self.type = PolarionAttributeType[string_utils.text_to_valid_enum_value_text(attributes_as_json["type"])]
        self.identifier = cast(str, attributes_as_json["id"])
        assert isinstance(self.identifier, str)
        self.title = cast(str, attributes_as_json["title"])
        assert isinstance(self.title, str)
        self.severity = PolarionSeverity[string_utils.text_to_valid_enum_value_text(attributes_as_json["severity"])]
        raw_created_timestamp = cast(str, attributes_as_json["created"])
        self.created_timestamp = datetime.fromisoformat(raw_created_timestamp)
        self.updated_timestamp = datetime.fromisoformat(cast(str, attributes_as_json["updated"]))


class PolarionWorkItem:

    def __init__(self, workitem_as_json: Dict) -> None:
        self.type = PolarionWorkItemType[string_utils.text_to_valid_enum_value_text(workitem_as_json["type"])]
        self.identifier = workitem_as_json["id"]
        self.attributes = PolarionAttributes(workitem_as_json["attributes"])
        self.attributes.identifier
        relationships = PolarionRelationships(workitem_as_json["relationships"])
