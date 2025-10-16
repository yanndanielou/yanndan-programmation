import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, cast, Set

import pandas
from common import string_utils
from logger import logger_config


class ElementGenericLibrary:

    @dataclass
    class Element:
        full_name: str

    def __init__(self) -> None:
        self.elements: List[ElementGenericLibrary.Element] = []
        self.elements_by_name: Dict[str, ElementGenericLibrary.Element] = {}

    def get_element_by_name(self, element_name: str) -> "ElementGenericLibrary.Element":
        if element_name in self.elements_by_name:
            return self.elements_by_name[element_name]

        else:
            responsible_core_team = ElementGenericLibrary.Element(element_name)
            self.elements.append(responsible_core_team)
            self.elements_by_name[element_name] = responsible_core_team
            return responsible_core_team


class LotWbsLibrary(ElementGenericLibrary):

    class LotWbs(ElementGenericLibrary.Element):
        pass

    def get_lot_wbs_by_name(self, lot_wbs_name: str) -> "LotWbsLibrary.LotWbs":
        return cast(LotWbsLibrary.LotWbs, self.get_element_by_name(lot_wbs_name))


class ResponsibleCoreTeamLibrary(ElementGenericLibrary):

    @dataclass
    class ResponsibleCoreTeam(ElementGenericLibrary.Element):
        pass

    def get_responsible_core_team_by_name(self, responsible_core_team_name: str) -> "ResponsibleCoreTeamLibrary.ResponsibleCoreTeam":
        return cast(ResponsibleCoreTeamLibrary.ResponsibleCoreTeam, self.get_element_by_name(responsible_core_team_name))


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
    REFUSE = "refusé"

    def __init__(self, full_raw_reference: str) -> None:
        self.full_raw_reference = full_raw_reference

        self.empty_by_error = not isinstance(full_raw_reference, str)

        self.number = None
        self.index = None
        self.name = None
        self.full_cleaned_reference = None

        if not self.empty_by_error:
            self.full_cleaned_reference = full_raw_reference.replace(" ", "_").replace("FA-", "FA").upper()
            if full_raw_reference.lower() != ReferenceFaPa.NO_FA.lower() and full_raw_reference != ReferenceFaPa.REFUSE:
                self.name = string_utils.left_part_after_last_occurence(input_string=self.full_cleaned_reference, separator="-")
                self.number = int(self.full_cleaned_reference.replace("FA", "").split("_")[0].split("-")[0])
                self.index = string_utils.right_part_after_last_occurence(input_string=self.full_cleaned_reference, separator="-")

    def is_no_fa(self) -> bool:
        return self.full_raw_reference.lower() == ReferenceFaPa.NO_FA.lower() if not self.empty_by_error else False


@dataclass
class FaPa:
    reference: ReferenceFaPa
    actual_delivery: Optional[datetime]


@dataclass
class Rpa(FaPa):
    status: Optional[DmlStatus]


@dataclass
class DmlLine:
    dml_document: "DmlDocument"
    code_ged_moe: str
    title: str
    version: int
    revision: int
    status: DmlStatus
    guide: GuideValue
    actual_livraison: Optional[datetime]
    fa: Optional[FaPa]
    pa: Optional[FaPa]
    rpa: Optional[Rpa]
    rrpa: Optional[FaPa]
    responsible_core_team: ResponsibleCoreTeamLibrary.ResponsibleCoreTeam
    lot_wbs: LotWbsLibrary.LotWbs
    be_number: str
    produit: Optional[bool]
    doc_deleted: bool

    def __post_init__(self) -> None:
        self.all_unique_fa_numbers: Set[int] = set()
        if self.fa and not self.fa.reference.empty_by_error and not self.fa.reference.is_no_fa():
            assert self.fa.reference.number
            self.all_unique_fa_numbers.add(self.fa.reference.number)
        if self.rpa and not self.rpa.reference.empty_by_error and not self.rpa.reference.is_no_fa():
            assert self.rpa.reference.number
            self.all_unique_fa_numbers.add(self.rpa.reference.number)

        self.all_unique_fa_names: Set[int] = set()
        if self.fa and not self.fa.reference.is_no_fa() and not self.fa.reference.empty_by_error:
            assert self.fa.reference.name
            self.all_unique_fa_names.add(self.fa.reference.name)
        if self.rpa and not self.rpa.reference.is_no_fa() and not self.rpa.reference.empty_by_error:
            assert self.rpa.reference.name
            self.all_unique_fa_names.add(self.rpa.reference.name)


@dataclass
class DmlDocument:
    dml_lines: List[DmlLine] = field(default_factory=list)

    def get_all_code_ged_moes(self) -> set[str]:
        all_code_ged_moes = {dml_line.code_ged_moe for dml_line in self.dml_lines}
        return all_code_ged_moes

    def get_all_titles(self) -> set[str]:
        all_titles = {dml_line.title for dml_line in self.dml_lines}
        return all_titles

    def get_all_fa_numbers(self) -> set[int]:
        all_fa_numbers: Set[int] = set()
        all_fa_numbers.union({dml_line.all_unique_fa_numbers for dml_line in self.dml_lines})
        return all_fa_numbers

    def get_all_fa_names(self) -> set[str]:
        all_fa_names: Set[str] = set()
        all_fa_names.union({dml_line.all_unique_fa_names for dml_line in self.dml_lines})
        return all_fa_names


def convert_dml_date_to_datetime(dml_date: str) -> Optional[datetime]:
    if dml_date == "NaT":
        return None
    return datetime.strptime(dml_date, "%Y-%m-%d %H:%M:%S")


def convert_doc_produit_column(raw_doc_produit_column_content: str) -> Optional[bool]:
    if raw_doc_produit_column_content == "nan":
        return None

    raw_doc_produit_column_content = raw_doc_produit_column_content.strip()
    if raw_doc_produit_column_content == "No":
        return False
    elif raw_doc_produit_column_content == "Yes":
        return True
    elif raw_doc_produit_column_content == "Oui":
        return True

    assert False, f"convert_doc_produit_column, Unsupported {raw_doc_produit_column_content}"


def convert_document_supprime_column(raw_document_supprime_column_content: str) -> bool:
    return raw_document_supprime_column_content.lower() == "x"


def get_or_create_document_by_code_ged_moe_title_or_fa(dml_documents: List[DmlDocument], code_ged_moe: str, title: str, fa: Optional[FaPa]) -> DmlDocument:
    found = find_document_by_code_ged_moe_title_or_fa(dml_documents, code_ged_moe, title, fa)
    return found if found else DmlDocument()


def find_document_by_code_ged_moe_title_or_fa(dml_documents: List[DmlDocument], code_ged_moe: str, title: str, fa: Optional[FaPa]) -> Optional[DmlDocument]:
    documents_found_by_code_ged_moe = [document for document in dml_documents if code_ged_moe in document.get_all_code_ged_moes()]
    if documents_found_by_code_ged_moe:
        assert len(documents_found_by_code_ged_moe) == 1
        return documents_found_by_code_ged_moe[0]

    # Document has changed reference but kept title
    documents_found_by_title = [document for document in dml_documents if title in document.get_all_titles()]
    if documents_found_by_title:
        assert len(documents_found_by_title) == 1
        return documents_found_by_title[0]

    # Document has changed reference and title, search by FA
    if fa:
        fa_name = fa.reference.name
        documents_found_by_fa = [document for document in dml_documents if fa_name in document.get_all_fa_names()]
        if documents_found_by_fa:
            assert len(documents_found_by_fa) == 1
            return documents_found_by_fa[0]

    return None


@dataclass
class DmlFileContent:
    dml_lines: List[DmlLine]
    dml_documents: List[DmlDocument]

    responsible_core_team_library: ResponsibleCoreTeamLibrary
    lot_wbs_library: LotWbsLibrary

    def get_dml_line_by_code_ged_moe_and_version(self, code_ged_moe: str, version: int, revision: int = 0) -> Optional[DmlLine]:
        dml_lines_found = [dml_line for dml_line in self.dml_lines if dml_line.code_ged_moe == code_ged_moe and dml_line.version == version and dml_line.revision == revision]
        assert dml_lines_found
        assert len(dml_lines_found) == 1
        dml_line_found = dml_lines_found[0]
        return dml_line_found

    def find_document_by_code_ged_moe_title_or_fa(self, code_ged_moe: str, title: str, fa: Optional[FaPa]) -> Optional[DmlDocument]:
        return find_document_by_code_ged_moe_title_or_fa(self.dml_documents, code_ged_moe, title, fa)

    class Builder:

        @staticmethod
        def build_with_excel_file(dml_excel_file_full_path: str) -> "DmlFileContent":

            with logger_config.stopwatch_with_label(f"Load {dml_excel_file_full_path}", monitor_ram_usage=True, inform_beginning=True):
                main_data_frame = pandas.read_excel(dml_excel_file_full_path, sheet_name="Database")
            logger_config.print_and_log_info(f"{dml_excel_file_full_path} has {len(main_data_frame)} items")
            logger_config.print_and_log_info(f" {dml_excel_file_full_path} columns  {main_data_frame.columns[:10]} ...")

            all_lines_found: List[DmlLine] = []
            all_documents_found: List[DmlDocument] = []
            responsible_core_team_library = ResponsibleCoreTeamLibrary()
            lot_wbs_library = LotWbsLibrary()

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
                    actual_livraison = convert_dml_date_to_datetime(str(row["Actual Livraison"]))

                    fa = (
                        FaPa(reference=ReferenceFaPa(row["Référence FA"]), actual_delivery=convert_dml_date_to_datetime(str(row["Actual FA"])))
                        if str(row["Actual FA"]) not in ["NaT", "nan", "na"]
                        else None
                    )
                    pa = (
                        FaPa(reference=ReferenceFaPa(row["Référence PA"]), actual_delivery=convert_dml_date_to_datetime(str(row["Actual Emission PA"])))
                        if str(row["Actual Emission PA"]) != "NaT"
                        else None
                    )
                    rpa = (
                        Rpa(
                            reference=ReferenceFaPa(row["Référence RPA"]),
                            status=DmlStatus[string_utils.text_to_valid_enum_value_text(str(row["Statut RPA"]))] if str(row["Statut RPA"]) not in ["nan", " "] else None,
                            actual_delivery=convert_dml_date_to_datetime(str(row["Actual Retour PA"])),
                        )
                        if str(row["Actual Retour PA"]) != "NaT"
                        else None
                    )
                    rrpa = FaPa(reference=ReferenceFaPa(row["Référence RRPA"]), actual_delivery=convert_dml_date_to_datetime(str(row["Actual RRPA"]))) if str(row["Actual RRPA"]) != "NaT" else None

                    responsible_core_team = responsible_core_team_library.get_responsible_core_team_by_name(str(row["ResponsableCoreTeam"]))
                    lot_wbs = lot_wbs_library.get_lot_wbs_by_name(str(row["Lot WBS"]))
                    be_number = str(row["Numéro du BE"])
                    produit = convert_doc_produit_column(str(row["Document Produit\n(Yes/No)"]))
                    doc_deleted = convert_document_supprime_column(str(row["Document Supprimé"]))

                    dml_document = find_document_by_code_ged_moe_title_or_fa(all_documents_found, code_ged_moe, title, fa)
                    if not dml_document:
                        dml_document = DmlDocument()
                        all_documents_found.append(dml_document)
                    dml_line = DmlLine(
                        dml_document, code_ged_moe, title, version, revision, status, guide, actual_livraison, fa, pa, rpa, rrpa, responsible_core_team, lot_wbs, be_number, produit, doc_deleted
                    )
                    all_lines_found.append(dml_line)

            logger_config.print_and_log_info(f"{len(all_lines_found)} lines found")
            logger_config.print_and_log_info(f"{len(responsible_core_team_library.elements)} responsibles core team found")
            logger_config.print_and_log_info(f"{len(lot_wbs_library.elements)} lots wbs found")
            dml_file_content = DmlFileContent(
                dml_documents=all_documents_found, dml_lines=all_lines_found, responsible_core_team_library=responsible_core_team_library, lot_wbs_library=lot_wbs_library
            )
            return dml_file_content
