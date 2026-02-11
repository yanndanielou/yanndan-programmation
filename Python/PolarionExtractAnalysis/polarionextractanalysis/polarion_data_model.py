import json
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, cast

from common import string_utils
from logger import logger_config

from polarionextractanalysis.constants import (
    PolarionAttributeType,
    PolarionSeverity,
    PolarionStatus,
    PolarionUserItemType,
)


class PolarionUserCompany:
    def __init__(self, full_name: str) -> None:
        self.full_name = full_name
        self.all_users_definitions: List[PolarionUserDefinition] = []


class PolarionUserDefinition:
    def __init__(self, users_library: "PolarionUsersLibrary", as_json_dict: Dict) -> None:
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
        self.company = users_library.get_or_create_user_company_user_by_full_name(entity_name if entity_name else "Unknown")
        self.company.all_users_definitions.append(self)


class PolarionUser:
    def __init__(self, users_library: "PolarionUsersLibrary", as_json_dict: Dict) -> None:
        self.user_definition = PolarionUserDefinition(users_library=users_library, as_json_dict=as_json_dict)
        self.all_work_items_assigned: List[PolarionWorkItem] = []


class PolarionUsersLibrary:
    def __init__(self, input_json_file_path: str, polarion_library: "PolarionLibrary") -> None:
        self.all_companies: List[PolarionUserCompany] = []
        self.all_users: List[PolarionUser] = []

        self.users_by_identifier: Dict[str, PolarionUser] = {}
        self.all_users_with_entity_dict: Dict[str, str] = {}
        self.all_users_by_entity: Dict[str, List[str]] = {}
        self.all_not_parsed_because_errors_users_as_json: List[str] = []

        self.polarion_library = polarion_library

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
                        assert user.user_definition.identifier not in self.users_by_identifier
                        self.users_by_identifier[user.user_definition.identifier] = user
                        self.all_users.append(user)
                    except KeyError as key_err:
                        logger_config.print_and_log_exception(key_err)
                        self.all_not_parsed_because_errors_users_as_json.append(user_as_json)

            logger_config.print_and_log_info(f"{len(self.all_users)} work items created. {len(self.all_not_parsed_because_errors_users_as_json)} could not be created")

    def get_user_by_identifier(self, identifier: str) -> PolarionUser:
        users_found = [user for user in self.all_users if user.user_definition.identifier == identifier]
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


class PolarionLibrary:
    def __init__(self, work_items_input_json_file_path: str, users_input_json_file_path: str) -> None:
        self.project_library = PolarionProjectLibrary(polarion_library=self)
        self.users_library = PolarionUsersLibrary(input_json_file_path=users_input_json_file_path, polarion_library=self)
        self.work_item_library = PolarionWorkItemLibrary(input_json_file_path=work_items_input_json_file_path, polarion_library=self)


class PolarionWorkItemLibrary:
    def __init__(self, input_json_file_path: str, polarion_library: PolarionLibrary) -> None:
        self.polarion_library = polarion_library
        self.all_work_items: List[PolarionWorkItem] = []
        self.all_not_parsed_because_errors_work_items_as_json: List[Dict] = []
        self.all_work_items_by_type: Dict[PolarionAttributeType, List[PolarionWorkItem]] = {}

        with logger_config.stopwatch_with_label(f"Library {input_json_file_path} creation"):

            with logger_config.stopwatch_with_label(f"Read {input_json_file_path} file"):
                with open(input_json_file_path, "r", encoding="utf-8") as file:
                    all_work_items_as_json = json.load(file)
                    assert isinstance(all_work_items_as_json, list)

            with logger_config.stopwatch_with_label(f"Create {len(all_work_items_as_json)} work items from parsed json file"):
                for work_item_as_json in all_work_items_as_json:
                    try:
                        assert isinstance(work_item_as_json, dict)
                        work_item: PolarionWorkItem
                        if work_item_as_json["attributes"]["type"] == "secondRegard":
                            work_item = PolarionSecondRegardWorkItem(polarion_library=self.polarion_library, work_item_as_json_dict=work_item_as_json)
                        elif work_item_as_json["attributes"]["type"] == "FAN_Titulaire":
                            work_item = PolarionFicheAnomalieTitulaireWorkItem(polarion_library=self.polarion_library, work_item_as_json_dict=work_item_as_json)
                        else:
                            work_item = PolarionWorkItem(polarion_library=self.polarion_library, work_item_as_json_dict=work_item_as_json)
                        self.all_work_items.append(work_item)

                        if work_item.attributes.type not in self.all_work_items_by_type:
                            self.all_work_items_by_type[work_item.attributes.type] = []
                        self.all_work_items_by_type[work_item.attributes.type].append(work_item)

                    except KeyError as key_err:
                        logger_config.print_and_log_exception(key_err)
                        self.all_not_parsed_because_errors_work_items_as_json.append(work_item_as_json)

            logger_config.print_and_log_info(f"{len(self.all_work_items)} work items created. {len(self.all_not_parsed_because_errors_work_items_as_json)} could not be created")


@dataclass
class PolarionProjectLibrary:
    def __init__(self, polarion_library: PolarionLibrary) -> None:
        self.polarion_library = polarion_library

        self.all_projects: List[PolarionProject] = []

    def get_by_identifier(self, identifier: str) -> "PolarionProject":
        found = [project for project in self.all_projects if project.identifier == identifier]
        if not found:
            self.all_projects.append(PolarionProject(identifier=identifier))
            return self.get_by_identifier(identifier=identifier)
        else:
            assert len(found) == 1
            return found[0]


@dataclass
class PolarionProject:

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        self.all_work_items: List[PolarionWorkItem] = []


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

    def __init__(self, polarion_library: PolarionLibrary, work_item_as_json_dict: Dict) -> None:
        self.library = polarion_library
        # self.item_type = PolarionWorkItemType[string_utils.text_to_valid_enum_value_text(work_item_as_json_dict["type"])]
        self.long_identifier = work_item_as_json_dict["id"]
        self.attributes = PolarionAttributes(work_item_as_json_dict["attributes"])
        self.short_identifier = self.attributes.identifier
        self.attributes.identifier = work_item_as_json_dict["attributes"]["id"]

        project_name = work_item_as_json_dict["relationships"]["project"]["data"]["id"]
        self.project = polarion_library.project_library.get_by_identifier(identifier=project_name)
        self.project.all_work_items.append(self)
        self.created_timestamp = datetime.fromisoformat(work_item_as_json_dict["attributes"]["created"])
        self.updated_timestamp = datetime.fromisoformat(work_item_as_json_dict["attributes"]["updated"])
        author_raw = work_item_as_json_dict["relationships"]["author"]["data"]
        self.author = polarion_library.users_library.get_user_by_identifier(identifier=author_raw["id"])
        self.assignees: List[PolarionUser] = []
        assignees_raw = cast(Dict[str, List[Dict[str, str]]], work_item_as_json_dict["relationships"]["assignee"])
        if "data" in assignees_raw:
            assignees_data_raw = assignees_raw["data"]
            for assignee_raw_data in assignees_data_raw:
                user_identifier = assignee_raw_data["id"]
                assignee = polarion_library.users_library.get_user_by_identifier(identifier=user_identifier)
                self.assignees.append(assignee)
                assignee.all_work_items_assigned.append(self)


class PolarionSecondRegardWorkItem(PolarionWorkItem):
    def __init__(self, polarion_library: PolarionLibrary, work_item_as_json_dict: Dict) -> None:
        super().__init__(polarion_library=polarion_library, work_item_as_json_dict=work_item_as_json_dict)
        self.theme = cast(str, work_item_as_json_dict["attributes"]["SR_theme"])


class PolarionFicheAnomalieTitulaireWorkItem(PolarionWorkItem):
    def __init__(self, polarion_library: PolarionLibrary, work_item_as_json_dict: Dict) -> None:
        super().__init__(polarion_library=polarion_library, work_item_as_json_dict=work_item_as_json_dict)
        self.suspected_element = cast(str, work_item_as_json_dict["attributes"]["Element"])
        self.environment = cast(str, work_item_as_json_dict["attributes"]["Environnement"])
