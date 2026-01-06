from typing import Any, List, Set

import pandas
from common import file_utils, json_encoders, file_name_utils
from logger import logger_config

from parsedml import parse_dml
import param

import uuid

INPUT_EXCEL_FILE = "Input/JALONS SIGNES_NExTEO-021100-01-0012-01 DML_NEXTEO_ATS+_V14_V41-00.xlsm"
OUTPUT_PARENT_DIRECTORY_NAME = "Output"
MAGIC_VALUE_SEPARATOR = str(uuid.uuid4())


def split_jalons_raw_to_jalon_names_list(jalons_raw: str) -> List[str]:

    if not jalons_raw or not isinstance(jalons_raw, str) or str(jalons_raw) in ["nan"] or jalons_raw.strip() == "":
        return []

    jalon_with_unique_separator = (
        jalons_raw.strip()
        .replace("\n", MAGIC_VALUE_SEPARATOR)
        .replace("\\", MAGIC_VALUE_SEPARATOR)
        .replace("/", MAGIC_VALUE_SEPARATOR)
        .replace(MAGIC_VALUE_SEPARATOR + MAGIC_VALUE_SEPARATOR, MAGIC_VALUE_SEPARATOR)
        .replace(MAGIC_VALUE_SEPARATOR + MAGIC_VALUE_SEPARATOR, MAGIC_VALUE_SEPARATOR)
    )

    assert MAGIC_VALUE_SEPARATOR + MAGIC_VALUE_SEPARATOR not in jalon_with_unique_separator, f"Could not handle raw jalon {jalons_raw}"

    jalons_list = [jalon.strip() for jalon in jalon_with_unique_separator.split(MAGIC_VALUE_SEPARATOR)]

    for jalon in jalons_list:
        assert MAGIC_VALUE_SEPARATOR not in jalon

    return jalons_list


class Doc:
    def __init__(self, code_moe_ged_raw: str) -> None:
        self.code_ged_moe = code_moe_ged_raw
        self.unique_jalons: Set[Jalon] = set()
        self.lines: List[DocLine] = []


class DocLine:
    def __init__(self, code_moe_ged_raw: str, jalons_raw: Any, doc: Doc, version: str, title: str) -> None:
        self.code_ged_moe = code_moe_ged_raw
        self.doc = doc
        self.jalons_raw = jalons_raw
        self._jalons: List[Jalon] = []
        self.version = version
        self.title = title
        doc.lines.append(self)

    def add_jalon(self, jalon: "Jalon") -> None:
        self._jalons.append(jalon)
        self.doc.unique_jalons.add(jalon)


class Jalon:
    def __init__(self, name: str) -> None:
        self.name = name
        self.docs_codes_ged_moe: Set[str] = set()

        assert self.name

        # logger_config.print_and_log_info(f"Create jalon {self.name}")


def main() -> None:
    all_jalons: List[Jalon] = []
    all_doc_lines: List[DocLine] = []
    all_docs: List[Doc] = []

    with logger_config.application_logger("extract_jalons_requested_by_customer"):

        with logger_config.stopwatch_with_label(f"Read excel {INPUT_EXCEL_FILE}", monitor_ram_usage=True, inform_beginning=True):
            main_data_frame: pandas.DataFrame = pandas.read_excel(INPUT_EXCEL_FILE, sheet_name="Database", skiprows=[0])

        with logger_config.stopwatch_with_label(f"Load and parse {len(main_data_frame)} DML lines"):
            for index, (_, row) in enumerate(main_data_frame.iterrows()):
                code_moe_ged_raw = row["Code GED MOE"]
                jalons_raw = row["Jalon fourniture"]
                version_raw = row["Version"]
                title_raw = row["Titre Document"]

                assert isinstance(code_moe_ged_raw, str)

                doc_already_created_with_ref = [doc_it for doc_it in all_docs if doc_it.code_ged_moe == code_moe_ged_raw]
                if doc_already_created_with_ref:
                    doc = doc_already_created_with_ref[0]
                else:
                    doc = Doc(code_moe_ged_raw)
                    all_docs.append(doc)

                doc_line = DocLine(code_moe_ged_raw=code_moe_ged_raw, jalons_raw=jalons_raw, doc=doc, version=version_raw, title=title_raw)
                all_doc_lines.append(doc_line)
                jalons_names_in_current_line = split_jalons_raw_to_jalon_names_list(jalons_raw)

                for jalon_name in jalons_names_in_current_line:
                    if not [jalon_found for jalon_found in all_jalons if jalon_found.name == jalon_name]:
                        jalon = Jalon(jalon_name)
                        all_jalons.append(jalon)

                    else:
                        jalon = [jalon_found for jalon_found in all_jalons if jalon_found.name == jalon_name][0]

                    # logger_config.print_and_log_info(f"Add doc {code_moe_ged_raw} to jalon {jalon_name}")
                    jalon.docs_codes_ged_moe.add(doc_line.code_ged_moe)
                    doc_line.add_jalon(jalon)

    logger_config.print_and_log_info(f"{len(all_jalons)} jalons found: \n{'\n'.join([jalon.name for jalon in all_jalons])}")
    logger_config.print_and_log_info(f"{len(all_jalons)} jalons found")

    assert all_jalons
    for jalon in all_jalons:
        assert jalon.name
        assert jalon.docs_codes_ged_moe, f"Jalon {jalon.name} has no doc"

    assert all_docs
    assert all_doc_lines

    for directory_path in [OUTPUT_PARENT_DIRECTORY_NAME]:
        file_utils.create_folder_if_not_exist(directory_path)

    json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(all_jalons, f"{OUTPUT_PARENT_DIRECTORY_NAME}/{file_name_utils.get_file_suffix_with_current_datetime()}_all_jalons.json")

    json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
        [(doc.code_ged_moe, [jalon.name for jalon in doc.unique_jalons]) for doc in all_docs if doc.unique_jalons],
        f"{OUTPUT_PARENT_DIRECTORY_NAME}/{file_name_utils.get_file_suffix_with_current_datetime()}_all_docs_with_jalons.json",
    )

    json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
        [doc.code_ged_moe for doc in all_docs if not doc.unique_jalons],
        f"{OUTPUT_PARENT_DIRECTORY_NAME}/{file_name_utils.get_file_suffix_with_current_datetime()}_all_docs_without_jalons.json",
    )

    with logger_config.stopwatch_with_label("Detect change jalons dans un doc"):
        for doc in all_docs:
            previous_jalons: List[Jalon] = doc.lines[0]._jalons
            for current_line in doc.lines[1:]:
                new_jalons_added = [jalon for jalon in current_line._jalons if jalon not in previous_jalons]
                old_jalons_removed = [jalon for jalon in previous_jalons if jalon not in current_line._jalons]

                if previous_jalons:
                    if new_jalons_added:
                        logger_config.print_and_log_warning(
                            f"Jalons {[jalon.name for jalon in new_jalons_added]} added in doc {doc.code_ged_moe}, in version {current_line.version} : previous jalons:{", ".join([jalon.name for jalon in previous_jalons])}, now {", ".join([jalon.name for jalon in current_line._jalons])}"
                        )
                        previous_jalons = previous_jalons + new_jalons_added

                if current_line._jalons:
                    if old_jalons_removed:
                        logger_config.print_and_log_info(
                            f"Jalons {[jalon.name for jalon in old_jalons_removed]} removed in doc {doc.code_ged_moe}, in version {current_line.version} : previous jalons:{", ".join([jalon.name for jalon in previous_jalons])}, now {", ".join([jalon.name for jalon in current_line._jalons])}"
                        )

    with logger_config.application_logger("ParseDML"):
        dml_file_content_built = parse_dml.DmlFileContent.Builder.build_with_excel_file(dml_excel_file_full_path=param.DML_FILE_WITH_USELESS_RANGES)

        for jalon in all_jalons:
            jalon_report_status = parse_dml.DocumentsStatusReport.Builder.build_by_code_ged_moe(name=jalon.name, dml_file_content=dml_file_content_built, codes_ged_moe=list(jalon.docs_codes_ged_moe))
            jalon_report_status.write_full_report_to_excel()
            jalon_report_status.write_synthetic_report_to_excel(warn_if_doc_deleted=True)


if __name__ == "__main__":
    main()
