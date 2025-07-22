import json
from typing import Dict, cast


class ArchiveLine:
    def __init__(self, full_raw_archive_line: str) -> None:

        # Parsing JSON string
        self.full_archive_line_as_json: Dict = json.loads(full_raw_archive_line)

        # Directly copy all items from SQLARCH section into a new dictionary
        self.sqlarch_fields_dict: Dict[str, str | int] = self.full_archive_line_as_json.get("SQLARCH", {})

        # Access global fields
        self.date_raw = self.full_archive_line_as_json["date"]
        self.tags = self.full_archive_line_as_json["tags"]

        # Accessing specific fields
        self.sqlarch_json_section: Dict = self.full_archive_line_as_json["SQLARCH"]

        # Directly copy all items from SQLARCH section into a new dictionary
        self.sqlarch_fields_dict = self.full_archive_line_as_json.get("SQLARCH", {})
        self.sqlarch_fields_dict_raw = {f"{key}_raw": value for key, value in self.sqlarch_fields_dict.items()}

        # Accessing specific fields
        self.caller = self.sqlarch_json_section.get("caller")
        self.cat_ala = self.sqlarch_json_section.get("catAla")
        self.eqp = self.sqlarch_json_section.get("eqp")
        self.eqp_id = self.sqlarch_json_section.get("eqpId")
        self.exe_st = self.sqlarch_json_section.get("exeSt")
        self.id_field = self.sqlarch_json_section.get("id")
        self.jdb = self.sqlarch_json_section.get("jdb")
        self.label = self.sqlarch_json_section.get("label")
        self.loc = self.sqlarch_json_section.get("loc")

    def get_id(self) -> str:
        return cast(str, self.sqlarch_fields_dict.get("id"))

    def get_new_state_str(self) -> str:
        return cast(str, self.sqlarch_fields_dict.get("newSt"))

    def get_date_raw_str(self) -> str:
        return cast(str, self.date_raw)

    def print_all(self) -> None:
        # Print extracted fields
        print("Caller:", self.caller)
        print("CatAla:", self.cat_ala)
        print("Eqp:", self.eqp)
        print("EqpId:", self.eqp_id)
        print("ExeSt:", self.exe_st)
        print("ID:", self.id_field)
        print("Jdb:", self.jdb)
        print("Label:", self.label)
        print("Loc:", self.loc)

        # Print the dictionary for SQLARCH fields
        for key, value in self.sqlarch_fields_dict.items():
            print(f"{key}: {value}")

        print("Date:", self.date_raw)
        print("Tags:", self.tags)
