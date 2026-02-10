import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple, cast

import pandas as pd
from common import file_name_utils, string_utils
from logger import logger_config

from polarionextractanalysis.constants import (
    PolarionAttributeType,
    PolarionSeverity,
    PolarionStatus,
    PolarionUserItemType,
    PolarionWorkItemType,
)

EXCEL_FILE_EXTENSION = ".xlsx"


class PolarionUserCompany:
    def __init__(self, full_name: str) -> None:
        self.full_name = full_name
        self.all_users: List[PolarionUser] = []


class PolarionUser:
    def __init__(self, users_library: "UsersLibrary", as_json_dict: Dict) -> None:
        self.users_library = users_library
        self.identifier = as_json_dict["id"]
        self.type_enum = PolarionUserItemType[string_utils.text_to_valid_enum_value_text(as_json_dict["type"])]
        attributes = as_json_dict["attributes"]
        self.full_name = attributes["name"]
        self.email = attributes["email"] if "email" in attributes else None
        self.initials = attributes["initials"]
        self.all_work_items_assigned: List[PolarionWorkItem] = []
        entity_name = cast(str, self.email).split("@")[-1] if self.email else None
        entity_name = "SNCF" if entity_name and "sncf" in entity_name.lower() else entity_name
        entity_name = "ATOS" if entity_name and "eviden" in entity_name.lower() else entity_name
        entity_name = entity_name.split(".")[0].upper() if entity_name else entity_name
        self.entity_name = entity_name
        self.company = users_library.get_or_create_user_company_user_by_full_name(self.entity_name if self.entity_name else "Unknown")
        self.company.all_users.append(self)


class UsersLibrary:
    def __init__(self, input_json_file_path: str) -> None:
        self.all_companies: List[PolarionUserCompany] = []
        self.all_users: List[PolarionUser] = []

        self.users_by_identifier: Dict[str, PolarionUser] = {}
        self.all_users_with_entity_dict: Dict[str, str] = {}
        self.all_users_by_entity: Dict[str, List[str]] = {}
        self.all_not_parsed_because_errors_users_as_json: List[str] = []

        with logger_config.stopwatch_with_label(f"User library {input_json_file_path} creation"):

            with logger_config.stopwatch_with_label(f"Read {input_json_file_path} file"):
                with open(input_json_file_path, "r", encoding="utf-8") as file:
                    all_items_as_json = json.load(file)
                    assert isinstance(all_items_as_json, list)

            with logger_config.stopwatch_with_label(f"Create {len(all_items_as_json)} users from parsed json file"):
                for user_as_json in all_items_as_json:
                    try:
                        assert isinstance(user_as_json, dict)
                        user = PolarionUser(users_library=self, as_json_dict=user_as_json)
                        assert user.identifier not in self.users_by_identifier
                        self.users_by_identifier[user.identifier] = user
                        self.all_users.append(user)
                    except KeyError as key_err:
                        logger_config.print_and_log_exception(key_err)
                        self.all_not_parsed_because_errors_users_as_json.append(user_as_json)

            logger_config.print_and_log_info(f"{len(self.all_users)} work items created. {len(self.all_not_parsed_because_errors_users_as_json)} could not be created")
            pass

    def get_user_by_identifier(self, identifier: str) -> PolarionUser:
        users_found = [user for user in self.all_users if user.identifier == identifier]
        assert users_found, f"user {identifier} not found"
        assert len(users_found) == 1
        return users_found[0]

    def get_or_create_user_company_user_by_full_name(self, full_name: str) -> PolarionUserCompany:
        found = [company for company in self.all_companies if company.full_name == full_name]
        if not found:
            self.all_companies.append(PolarionUserCompany(full_name))
            return self.get_or_create_user_company_user_by_full_name(full_name)
        assert len(found) == 1
        return found[0]

    def dump_to_excel_file(self, output_directory_path: str) -> None:

        excel_file_name = "all_users_" + file_name_utils.get_file_suffix_with_current_datetime() + EXCEL_FILE_EXTENSION
        excel_file_path = output_directory_path + "/" + excel_file_name
        with logger_config.stopwatch_with_label(f"Dump users to excel file {excel_file_name}"):
            df = pd.DataFrame(
                [
                    {
                        "type": user.type_enum.name if user.type_enum is not None else None,
                        "identifier": user.identifier,
                        "Company name": user.entity_name,
                        "Company": user.company.full_name,
                        "Number of work items": len(user.all_work_items_assigned),
                        "work_items": ",".join(w.long_identifier for w in user.all_work_items_assigned),
                    }
                    for user in self.all_users
                ]
            )
            df.to_excel(excel_file_path, index=False)

        excel_file_name = "all_companies_" + file_name_utils.get_file_suffix_with_current_datetime() + EXCEL_FILE_EXTENSION
        excel_file_path = output_directory_path + "/" + excel_file_name
        with logger_config.stopwatch_with_label(f"Dump companies to excel file {excel_file_name}"):
            df = pd.DataFrame(
                [
                    {
                        "Full name": company.full_name,
                        "Number of Users": len(company.all_users),
                        "Users": ",".join(user.full_name for user in company.all_users),
                    }
                    for company in self.all_companies
                ]
            )
            df.to_excel(excel_file_path, index=False)


class PolarionLibrary:
    def __init__(self, input_json_file_path: str, users_library: UsersLibrary) -> None:
        self.all_work_items: List[PolarionWorkItem] = []
        self.all_not_parsed_because_errors_work_items_as_json: List[Dict] = []
        self.users_library = users_library

        with logger_config.stopwatch_with_label(f"Library {input_json_file_path} creation"):

            with logger_config.stopwatch_with_label(f"Read {input_json_file_path} file"):
                with open(input_json_file_path, "r", encoding="utf-8") as file:
                    all_work_items_as_json = json.load(file)
                    assert isinstance(all_work_items_as_json, list)
                    # logger_config.print_and_log_info(f"{len(all_work_items_as_json)} objects found")

            with logger_config.stopwatch_with_label(f"Create {len(all_work_items_as_json)} work items from parsed json file"):
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

    def dump_to_excel_file(self, output_directory_path: str) -> None:

        excel_file_name = "all_work_items_" + file_name_utils.get_file_suffix_with_current_datetime() + EXCEL_FILE_EXTENSION
        excel_file_path = output_directory_path + "/" + excel_file_name
        with logger_config.stopwatch_with_label(f"Dump all work items to excel file {excel_file_name}"):
            df = pd.DataFrame(
                [
                    {
                        "identifier": work_item.attributes.identifier,
                        "type": work_item.attributes.type.name,
                        "Project name": work_item.project_name,
                        "Status": work_item.attributes.status.name,
                        "Created timestamp": work_item.created_timestamp.replace(tzinfo=None),
                        "Updated timestamp": work_item.updated_timestamp.replace(tzinfo=None),
                        "Entity assigned": ",".join(set(w.entity_name for w in work_item.assignees if w.entity_name)),
                        "Number users assigned": len(work_item.assignees),
                        "Users assigned": ",".join(w.identifier for w in work_item.assignees),
                    }
                    for work_item in self.all_work_items
                ]
            )
            df.to_excel(excel_file_path, index=False)


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
        self.status = PolarionStatus[string_utils.text_to_valid_enum_value_text(attributes_as_json_dict["status"])]


class PolarionWorkItem:

    def __init__(self, library: PolarionLibrary, work_item_as_json_dict: Dict) -> None:
        self.library = library
        self.item_type = PolarionWorkItemType[string_utils.text_to_valid_enum_value_text(work_item_as_json_dict["type"])]
        self.long_identifier = work_item_as_json_dict["id"]
        self.attributes = PolarionAttributes(work_item_as_json_dict["attributes"])
        self.short_identifier = self.attributes.identifier
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
                user_identifier = assignee_raw_data["id"]
                assignee = library.users_library.get_user_by_identifier(identifier=user_identifier)
                self.assignees.append(assignee)
                assignee.all_work_items_assigned.append(self)
