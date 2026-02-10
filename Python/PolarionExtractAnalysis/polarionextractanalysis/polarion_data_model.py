import json
from typing import Dict, List, cast
from dataclasses import dataclass
from polarionextractanalysis.constants import PolarionWorkItemType, PolarionAttributeType, PolarionSeverity, PolarionUserItemType
from datetime import datetime
from logger import logger_config
from common import string_utils


class PolarionUser:
    def __init__(self, users_library: "UsersLibrary", type_enum: PolarionUserItemType, identifier: str) -> None:
        self.users_library = users_library
        self.type_enum = type_enum
        self.identifier = identifier
        self.all_work_items_assigned: List[PolarionWorkItem] = []


class UsersLibrary:
    def __init__(self) -> None:
        self.all_users: List[PolarionUser] = []

    def get_or_create_user_by_type_and_identifier(self, type_raw: str, identifier: str) -> PolarionUser:
        type_enum = PolarionUserItemType[string_utils.text_to_valid_enum_value_text(type_raw)]
        users_found = [user for user in self.all_users if user.identifier == identifier and user.type_enum == type_enum]
        if not users_found:
            user_created = PolarionUser(users_library=self, type_enum=type_enum, identifier=identifier)
            self.all_users.append(user_created)
            return self.get_or_create_user_by_type_and_identifier(type_raw=type_raw, identifier=identifier)
        else:
            assert len(users_found) == 1
            return users_found[0]


class PolarionLibrary:
    def __init__(self, input_json_file_path: str) -> None:
        self.all_work_items: List[PolarionWorkItem] = []
        self.all_not_parsed_because_errors_work_items_as_json: List[Dict] = []
        self.users_library = UsersLibrary()

        with open(input_json_file_path, "r", encoding="utf-8") as file:
            all_work_items_as_json = json.load(file)

            assert isinstance(all_work_items_as_json, list)
            logger_config.print_and_log_info(f"{len(all_work_items_as_json)} objects found")

        for work_item_as_json in all_work_items_as_json:
            try:
                assert isinstance(work_item_as_json, dict)
                work_item = PolarionWorkItem(library=self, work_item_as_json_dict=work_item_as_json)
                self.all_work_items.append(work_item)
            except KeyError as key_err:
                logger_config.print_and_log_exception(key_err)
                self.all_not_parsed_because_errors_work_items_as_json.append(work_item_as_json)

        logger_config.print_and_log_info(f"{len(self.all_work_items)} work items created. {len(self.all_not_parsed_because_errors_work_items_as_json)} could not be created")
        pass


@dataclass
class PolarionProject:
    identifier: str


class PolarionAttributes:
    def __init__(self, attributes_as_json_dict: Dict) -> None:
        self.type = PolarionAttributeType[string_utils.text_to_valid_enum_value_text(attributes_as_json_dict["type"])]
        self.identifier = cast(str, attributes_as_json_dict["id"])
        assert isinstance(self.identifier, str)
        self.title = cast(str, attributes_as_json_dict["title"])
        assert isinstance(self.title, str)
        self.severity = PolarionSeverity[string_utils.text_to_valid_enum_value_text(attributes_as_json_dict["severity"])] if "severity" in attributes_as_json_dict else None
        raw_created_timestamp = cast(str, attributes_as_json_dict["created"])
        self.created_timestamp = datetime.fromisoformat(raw_created_timestamp)
        self.updated_timestamp = datetime.fromisoformat(cast(str, attributes_as_json_dict["updated"]))


class PolarionWorkItem:

    def __init__(self, library: PolarionLibrary, work_item_as_json_dict: Dict) -> None:
        self.library = library
        self.type = PolarionWorkItemType[string_utils.text_to_valid_enum_value_text(work_item_as_json_dict["type"])]
        self.identifier = work_item_as_json_dict["id"]
        self.attributes = PolarionAttributes(work_item_as_json_dict["attributes"])
        self.attributes.identifier = work_item_as_json_dict["attributes"]["id"]
        # self.relationships = PolarionRelationships(work_item_as_json_dict["relationships"])
        self.project_name = work_item_as_json_dict["relationships"]["project"]["data"]["id"]
        self.created_timestamp = datetime.fromisoformat(work_item_as_json_dict["attributes"]["created"])
        self.updated_timestamp = datetime.fromisoformat(work_item_as_json_dict["attributes"]["updated"])
        self.assignees: List[PolarionUser] = []
        assignees_raw = cast(Dict[str, List[Dict[str, str]]], work_item_as_json_dict["relationships"]["assignee"])
        if "data" in assignees_raw:
            assignees_data_raw = assignees_raw["data"]
            for assignee_raw_data in assignees_data_raw:
                user_type_raw = assignee_raw_data["type"]
                user_identifier = assignee_raw_data["id"]
                assignee = library.users_library.get_or_create_user_by_type_and_identifier(type_raw=user_type_raw, identifier=user_identifier)
                self.assignees.append(assignee)
                assignee.all_work_items_assigned.append(self)
