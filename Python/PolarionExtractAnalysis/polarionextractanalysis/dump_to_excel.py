from typing import List

import pandas as pd
from common import file_name_utils
from logger import logger_config

from polarionextractanalysis import polarion_data_model

EXCEL_FILE_EXTENSION = ".xlsx"


def dump_users_to_excel_file(all_users: List[polarion_data_model.PolarionUser], output_directory_path: str) -> None:

    excel_file_name = "all_users_" + file_name_utils.get_file_suffix_with_current_datetime() + EXCEL_FILE_EXTENSION
    excel_file_path = output_directory_path + "/" + excel_file_name
    with logger_config.stopwatch_with_label(f"Dump users to excel file {excel_file_name}"):
        df = pd.DataFrame(
            [
                {
                    "type": user.type_enum.name if user.type_enum is not None else None,
                    "identifier": user.identifier,
                    "Full name": user.full_name,
                    "Company": user.company.full_name,
                    "Number of work items": len(user.all_work_items_assigned),
                    "work_items": ",".join(w.long_identifier for w in user.all_work_items_assigned),
                }
                for user in all_users
            ]
        )
        df.to_excel(excel_file_path, index=False)


def dump_companies_to_excel_file(all_companies: List[polarion_data_model.PolarionUserCompany], output_directory_path: str) -> None:
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
                for company in all_companies
            ]
        )
        df.to_excel(excel_file_path, index=False)


def dump_work_items_to_excel_file(all_work_items: List[polarion_data_model.PolarionWorkItem], output_directory_path: str) -> None:

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
                    "Companies assigned": ",".join(set(w.company.full_name for w in work_item.assignees)),
                    "Number users assigned": len(work_item.assignees),
                    "Users assigned": ",".join(w.full_name for w in work_item.assignees),
                }
                for work_item in all_work_items
            ]
        )
        df.to_excel(excel_file_path, index=False)
