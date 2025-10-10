from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, cast
import pandas
from enum import Enum, auto
from datetime import datetime

from common import string_utils
import param

from logger import logger_config
import math


class GuideValue(Enum):
    OUI = auto()
    NON = auto()
    TBD = auto()


class DmlStatus(Enum):
    FAVORABLE = auto()
    ARPCPA = auto()
    ARAC = auto()
    DEFAVORABLE = auto()
    SUPPRIME = auto()
    NON_LIVRE = auto()
    PAS_DE_FA = auto()
    EN_ATTENTE_FA = auto()
    LIVRE_POUR_INFORMATION = auto()
    NON_EXAMINE = auto()
    DOCUMENT_INTERNE = auto()
    ABANDONNE = auto()


class ReferenceFaPa:
    NO_FA = "Pas de FA"

    def __init__(self, full_reference: str) -> None:
        self.full_reference = full_reference


@dataclass
class DmlLine:
    code_ged_moe: str
    title: str
    version: int
    revision: int
    status: DmlStatus
    guide: bool
    actual_livraison: Optional[datetime]
    reference_fa: Optional[ReferenceFaPa]
    reference_pa: Optional[ReferenceFaPa]
    reference_rpa: Optional[ReferenceFaPa]
    reference_rrpa: Optional[ReferenceFaPa]
    responsible_core_team: str
    lot_wbs: str
    be_number: str


def dml_date_to_datetime(dml_date: str) -> Optional[datetime]:
    pass


@dataclass
class DmlFileContent:
    dml_lines: List[DmlLine]

    class Builder:

        @staticmethod
        def build_with_excel_file(dml_excel_file_full_path: str) -> "DmlFileContent":

            with logger_config.stopwatch_with_label(f"Load {dml_excel_file_full_path}", monitor_ram_usage=True, inform_beginning=True):
                main_data_frame = pandas.read_excel(dml_excel_file_full_path, sheet_name=param.USEFUL_DML_SHEET_NAME)
            logger_config.print_and_log_info(f"{dml_excel_file_full_path} has {len(main_data_frame)} items")
            logger_config.print_and_log_info(f" {dml_excel_file_full_path} columns  {main_data_frame.columns[:10]} ...")

            all_lines_found: List[DmlLine] = []

            with logger_config.stopwatch_with_label(f"Load and parse {len(main_data_frame)} DML lines"):

                for _, row in main_data_frame.iterrows():

                    code_ged_moe = str(row["Code GED MOE"])
                    title = str(row["Titre Document"])
                    raw_version = row["Version"]
                    if type(raw_version) is not str and math.isnan(raw_version):
                        raw_version = "-1"
                    version = int(raw_version)
                    raw_revision = row["Révision"]
                    if type(raw_revision) is not str and math.isnan(raw_revision):
                        raw_revision = "-1"
                    revision = int(raw_revision)
                    status = DmlStatus[string_utils.text_to_valid_enum_value_text(str(row["Statut"]))]
                    guide = GuideValue[string_utils.text_to_valid_enum_value_text(str(row["GUIDE"]))]
                    actual_livraison = dml_date_to_datetime(str(row["Actual Livraison"]))
                    reference_fa: Optional[ReferenceFaPa] = ReferenceFaPa(row["Référence FA"])
                    reference_pa: Optional[ReferenceFaPa] = ReferenceFaPa(row["Référence PA"])
                    reference_rpa: Optional[ReferenceFaPa] = ReferenceFaPa(row["Référence RPA"])
                    reference_rrpa: Optional[ReferenceFaPa] = ReferenceFaPa(row["Référence RRPA"])
                    responsible_core_team = str(row["Code GED MOE"])
                    lot_wbs = str(row["Code GED MOE"])
                    be_number = str(row["Code GED MOE"])

                    dml_line = DmlLine(
                        code_ged_moe, title, version, revision, status, guide, actual_livraison, reference_fa, reference_pa, reference_rpa, reference_rrpa, responsible_core_team, lot_wbs, be_number
                    )
                    all_lines_found.append(dml_line)

            logger_config.print_and_log_info(f"{len(all_lines_found)} lines found")
            dml_file_content = DmlFileContent(dml_lines=all_lines_found)

            return dml_file_content


if __name__ == "__main__":

    with logger_config.application_logger("ParseDML"):
        dml_file_content = DmlFileContent.Builder.build_with_excel_file(dml_excel_file_full_path=param.DML_FILE_CLEANED_FINAL)
