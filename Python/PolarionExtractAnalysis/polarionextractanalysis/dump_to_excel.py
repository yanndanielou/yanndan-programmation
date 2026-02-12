from typing import List

import pandas as pd
from common import file_name_utils
from logger import logger_config

from polarionextractanalysis import polarion_data_model

EXCEL_FILE_EXTENSION = ".xlsx"


def dump_users_to_excel_file(users_library: polarion_data_model.PolarionUsersLibrary, output_directory_path: str) -> None:

    excel_file_name = "all_users_" + file_name_utils.get_file_suffix_with_current_datetime() + EXCEL_FILE_EXTENSION
    excel_file_path = output_directory_path + "/" + excel_file_name
    with logger_config.stopwatch_with_label(f"Dump users to excel file {excel_file_name}"):
        df = pd.DataFrame(
            [
                {
                    "type": user.user_definition.type_enum.name if user.user_definition.type_enum is not None else None,
                    "identifier": user.user_definition.identifier,
                    "Full name": user.user_definition.full_name,
                    "Company": user.user_definition.company.full_name,
                    "Number of work items": len(user.all_work_items_assigned),
                    "work_items": ",".join(w.long_identifier for w in user.all_work_items_assigned),
                }
                for user in users_library.all_users
            ]
        )
        df.to_excel(excel_file_path, index=False)


def dump_projects_to_excel_file(project_library: polarion_data_model.PolarionProjectLibrary, output_directory_path: str) -> None:

    excel_file_name = "all_projects_" + file_name_utils.get_file_suffix_with_current_datetime() + EXCEL_FILE_EXTENSION
    excel_file_path = output_directory_path + "/" + excel_file_name
    with logger_config.stopwatch_with_label(f"Dump projects to excel file {excel_file_name}"):
        df = pd.DataFrame(
            [
                {
                    "identifier": project.identifier,
                    "Number of work items": len(project.all_work_items),
                    "work_items": ",".join(w.short_identifier for w in project.all_work_items),
                }
                for project in project_library.all_projects
            ]
        )
        df.to_excel(excel_file_path, index=False)


def dump_companies_to_excel_file(users_library: polarion_data_model.PolarionUsersLibrary, output_directory_path: str) -> None:
    excel_file_name = "all_companies_" + file_name_utils.get_file_suffix_with_current_datetime() + EXCEL_FILE_EXTENSION
    excel_file_path = output_directory_path + "/" + excel_file_name
    with logger_config.stopwatch_with_label(f"Dump companies to excel file {excel_file_name}"):
        df = pd.DataFrame(
            [
                {
                    "Full name": company.full_name,
                    "Number of Users": len(company.all_users_definitions),
                    "Users": ",".join(user_definition.full_name for user_definition in company.all_users_definitions),
                }
                for company in users_library.all_companies
            ]
        )
        df.to_excel(excel_file_path, index=False)


def dump_work_items_to_excel_file(work_items_library: polarion_data_model.PolarionWorkItemLibrary, output_directory_path: str) -> None:

    excel_file_name = "all_work_items_" + file_name_utils.get_file_suffix_with_current_datetime() + EXCEL_FILE_EXTENSION
    excel_file_path = output_directory_path + "/" + excel_file_name
    with logger_config.stopwatch_with_label(f"Dump all work items to excel file {excel_file_name}"):
        rows = []
        for work_item in work_items_library.all_work_items:
            row = {
                "identifier": work_item.attributes.identifier,
                "type": work_item.attributes.type.name,
                "Project": work_item.project.identifier,
                "Status": work_item.attributes.status.name,
                "title": work_item.attributes.title,
                "Author": work_item.author.user_definition.full_name,
                "Author company": work_item.author.user_definition.company.full_name,
                "Created timestamp": work_item.created_timestamp.replace(tzinfo=None),
                "Updated timestamp": work_item.updated_timestamp.replace(tzinfo=None),
                "Companies assigned": ",".join(set(w.user_definition.company.full_name for w in work_item.assignees)),
                "Number users assigned": len(work_item.assignees),
                "Users assigned": ",".join(w.user_definition.full_name for w in work_item.assignees),
            }

            if isinstance(work_item, polarion_data_model.PolarionSecondRegardWorkItem):
                row["SR_theme"] = work_item.theme

            if isinstance(work_item, polarion_data_model.PolarionFicheAnomalieTitulaireWorkItem):
                row["FAN_titulaire_Element"] = work_item.suspected_element
                row["FAN_titulaire_Environnement"] = work_item.environment.value

            if isinstance(work_item, polarion_data_model.PolarionFicheAnomalieWorkItem):
                row["FAN_suspected_element"] = work_item.suspected_element
                row["FAN_next_reference"] = work_item.next_reference
                row["FAN_destinataire"] = work_item.destinataire.name if work_item.destinataire is not None else None
                row["FAN_test_environment"] = work_item.test_environment.value if work_item.test_environment else None
                row["FAN_ref_anomalie_destinataire"] = work_item.ref_anomalie_destinataire

            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_excel(excel_file_path, index=False)
