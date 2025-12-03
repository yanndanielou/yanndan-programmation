import math
from warnings import deprecated
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, cast

from common import excel_utils

import pandas
from common import string_utils
from logger import logger_config
import param
import logging


STANDARD_FA_CLEANED_PATTERN = re.compile(r"FA(?P<FA_number>\d+)-?(?P<FA_indice>\d+)?$")


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

    def __init__(self, initial_full_raw_reference: str) -> None:

        self.number = None
        self.index = None
        self.name = None
        self.empty_by_error = not isinstance(initial_full_raw_reference, str)

        full_raw_reference = initial_full_raw_reference
        if not self.empty_by_error:
            full_raw_reference = full_raw_reference.strip().replace("  ", " ")
            if full_raw_reference in param.PATCHED_FA_NAMES:
                logger_config.print_and_log_info(f"FA {initial_full_raw_reference} patched to {param.PATCHED_FA_NAMES[full_raw_reference]}")
                full_raw_reference = param.PATCHED_FA_NAMES[full_raw_reference]

            self.full_raw_reference = full_raw_reference

            self.full_cleaned_reference = full_raw_reference.replace(" ", "_").replace("FA-", "FA").replace("FA_", "FA").upper()

            if STANDARD_FA_CLEANED_PATTERN.match(self.full_cleaned_reference):
                matched = STANDARD_FA_CLEANED_PATTERN.match(self.full_cleaned_reference)
                assert matched
                self.name = matched.group("FA_number")
                self.number = int(matched.group("FA_number"))
                group_fa_indice = matched.group("FA_indice")
                self.index = int(group_fa_indice) if bool(group_fa_indice) else 1

            elif full_raw_reference.lower() != ReferenceFaPa.NO_FA.lower() and full_raw_reference != ReferenceFaPa.REFUSE:
                self.name = string_utils.left_part_after_last_occurence(input_string=self.full_cleaned_reference, separator="-")
                self.number = int(self.full_cleaned_reference.replace("FA", "").split("_")[0].split("-")[0])
                self.index = int(string_utils.right_part_after_last_occurence(input_string=self.full_cleaned_reference, separator="-"))
        else:
            self.full_raw_reference = full_raw_reference

    def __str__(self) -> str:
        return f"FA __str__ {self.full_raw_reference}"

    def __repr__(self) -> str:
        return f"FA __repr__ {self.full_raw_reference}"

    def is_refused(self) -> bool:
        return self.full_raw_reference.lower() == ReferenceFaPa.REFUSE.lower() if not self.empty_by_error else False

    def is_no_fa(self) -> bool:
        return self.full_raw_reference.lower() == ReferenceFaPa.NO_FA.lower() if not self.empty_by_error else False

    def is_standard_fa(self) -> bool:
        if self.empty_by_error:
            return False
        if self.is_refused():
            return False
        if self.is_no_fa():
            return False
        return True


@dataclass
class FaPa:
    reference: ReferenceFaPa
    actual_delivery: Optional[datetime]


@dataclass
class Rpa(FaPa):
    status: Optional[DmlStatus]


@dataclass
class DmlLine:
    full_row: pandas.Series
    dml_document: "DmlDocument"
    code_ged_moe: str
    raw_title: str
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
    is_last_submit_of_doc: bool

    def __post_init__(self) -> None:
        self.dml_document.dml_lines.append(self)

        self.all_unique_fa_numbers: Set[int] = set()
        if self.fa and self.fa.reference.is_standard_fa():
            assert self.fa.reference.number
            self.all_unique_fa_numbers.add(self.fa.reference.number)
        if self.rpa and self.rpa.reference.is_standard_fa():
            assert self.rpa.reference.number
            self.all_unique_fa_numbers.add(self.rpa.reference.number)

        self.all_unique_fa_names: Set[str] = set()
        if self.fa and self.fa.reference.is_standard_fa():
            assert self.fa.reference.name
            self.all_unique_fa_names.add(self.fa.reference.name)
        if self.rpa and self.rpa.reference.is_standard_fa():
            assert self.rpa.reference.name
            self.all_unique_fa_names.add(self.rpa.reference.name)

    def __str__(self) -> str:
        return f"Line __str__ code_ged_moe:{self.code_ged_moe} version:{self.version} title:{self.title}"

    def __repr__(self) -> str:
        return f"Line __repr__ code_ged_moe:{self.code_ged_moe} version:{self.version} title:{self.title}"


@dataclass
class DmlDocument:
    dml_lines: List[DmlLine] = field(default_factory=list)

    def get_sorted_dml_lines(self) -> List[DmlLine]:
        return sorted(self.dml_lines, key=lambda l: (l.version, l.revision))

    def get_last_dml_line(self) -> DmlLine:
        return self.get_sorted_dml_lines()[-1]

    def get_all_code_ged_moes(self) -> set[str]:
        all_code_ged_moes = {dml_line.code_ged_moe for dml_line in self.dml_lines}
        return all_code_ged_moes

    def get_all_titles(self) -> set[str]:
        all_titles = {dml_line.title for dml_line in self.dml_lines}
        return all_titles

    def get_all_version_revisions(self) -> List[Tuple[int, int]]:
        all_version_revisions = [(dml_line.version, dml_line.revision) for dml_line in self.dml_lines]
        return all_version_revisions

    def get_all_fa_numbers(self) -> set[int]:
        return {fa_number for line in self.dml_lines for fa_number in line.all_unique_fa_numbers}

    def get_all_fa_names(self) -> set[str]:
        return {fa_name for line in self.dml_lines for fa_name in line.all_unique_fa_names}

    def has_several_fa_numbers(self) -> bool:
        return len(self.get_all_fa_names()) > 1

    def __str__(self) -> str:
        return f"DmlDocument __str__ {len(self.dml_lines)} lines: {'\n'.join([str(dml_line) for dml_line in self.dml_lines])}"


def convert_is_last_submit_of_doc(raw_last_submit_of_doc: str) -> bool:
    if raw_last_submit_of_doc in ["0", "O", "x", "X"]:
        return True
    elif raw_last_submit_of_doc in ["No", "na", "N/A", "nan", "", str(excel_utils.EXCEL_NA_NUMERIC_VALUE)]:
        return False

    logger_config.print_and_log_error(f"Unsupported raw_last_submit_of_doc {raw_last_submit_of_doc}")
    assert False


def convert_dml_date_to_datetime(dml_date: str) -> Optional[datetime]:
    if dml_date == "NaT":
        return None
    return datetime.strptime(dml_date, "%Y-%m-%d %H:%M:%S")


def convert_doc_produit_column(raw_doc_produit_column_content: str) -> Optional[bool]:
    if raw_doc_produit_column_content == "nan":
        return None

    raw_doc_produit_column_content = raw_doc_produit_column_content.strip()
    if raw_doc_produit_column_content.upper() == "NO":
        return False
    if raw_doc_produit_column_content == "Non":
        return False
    elif raw_doc_produit_column_content == "Yes":
        return True
    elif raw_doc_produit_column_content == "Oui":
        return True

    assert False, f"convert_doc_produit_column, Unsupported {raw_doc_produit_column_content}"


def convert_document_supprime_column(raw_document_supprime_column_content: str) -> bool:
    return raw_document_supprime_column_content.lower() == "x"


def find_document_by_code_ged_moe_title_or_fa(dml_documents: List[DmlDocument], code_ged_moe: str, title: str, fa: Optional[FaPa], version: int, revision: int) -> Optional[DmlDocument]:
    documents_found_by_code_ged_moe = [document for document in dml_documents if code_ged_moe in document.get_all_code_ged_moes()]
    if documents_found_by_code_ged_moe:
        assert len(documents_found_by_code_ged_moe) == 1
        return documents_found_by_code_ged_moe[0]

    # Document has changed reference but kept title
    documents_found_by_title = [document for document in dml_documents if title in document.get_all_titles() and (version, revision) not in document.get_all_version_revisions()]
    if documents_found_by_title:
        assert len(documents_found_by_title) == 1
        document_found_by_title = documents_found_by_title[0]
        logger_config.print_and_log_info(
            f"Searching {code_ged_moe} {title} {fa}. Found with title. Previous references: {document_found_by_title.get_all_code_ged_moes()}, previous titles {document_found_by_title.get_all_titles()}"
        )

        return documents_found_by_title[0]

    # Document has changed reference and title, search by FA
    if fa:
        fa_name = fa.reference.name
        documents_found_by_fa = [document for document in dml_documents if fa_name in document.get_all_fa_names() and (version, revision) not in document.get_all_version_revisions()]
        if documents_found_by_fa:
            assert len(documents_found_by_fa) == 1
            document_found_by_fa = documents_found_by_fa[0]

            logger_config.print_and_log_info(
                f"Searching {code_ged_moe} {title} {fa}. Found with FA (was renamed and reference changed). found doc {document_found_by_fa} with FAs {document_found_by_fa.get_all_fa_names()}"
            )
            return document_found_by_fa

    return None


@dataclass
class DocumentStatusReport:
    dml_document: DmlDocument

    def __post_init__(self) -> None:
        pass

    def print_report(self) -> None:

        self.dml_document.get_all_code_ged_moes()
        logger_config.print_and_log_info(f"Print report for {self.dml_document.get_all_code_ged_moes()}")
        document_sorted_dml_lines = self.dml_document.get_sorted_dml_lines()

        last_line = self.dml_document.get_last_dml_line()
        assert last_line
        for line_number, line in enumerate(self.dml_document.dml_lines):
            logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{line_number}")
            logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{line_number}\tcode_ged_moe:{line.code_ged_moe}")
            logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{line_number}\ttitle:{line.title}")
            logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{line_number}\tversion:{line.version}\trevision:{line.revision}")
            logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{line_number}\tstatus:{line.status}")
            logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{line_number}\tactual_livraison:{line.actual_livraison}")
            logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{line_number}\tdoc_deleted:{line.doc_deleted}")
            logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{line_number}\tfa:{line.fa}")
            logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{line_number}\tpa:{line.pa}")
            logging.info(f"\n")

        logger_config.print_and_log_info(
            f"{self.dml_document.get_all_code_ged_moes()}\tLast line: code_ged_moe:{last_line.code_ged_moe}\ttitle:{last_line.title}\tversion:{last_line.version}\trevision:{line.revision}\tstatus:{last_line.status}\tactual_livraison:{last_line.actual_livraison}\tfa:{last_line.fa}\tpa:{last_line.pa}\n\n"
        )

    class Builder:

        @staticmethod
        def build_by_code_ged_moe(dml_file_content: "DmlFileContent", code_ged_moe: str) -> "DocumentStatusReport":
            dml_document = dml_file_content.find_document_by_code_ged_moe(code_ged_moe)
            assert dml_document
            document_status_report = DocumentStatusReport(dml_document=dml_document)
            return document_status_report


@dataclass
class DmlFileContent:
    dml_lines: List[DmlLine]
    dml_lines_by_code_ged_moe: Dict[str, List[DmlLine]]
    dml_lines_by_title: Dict[str, List[DmlLine]]
    dml_documents: List[DmlDocument]
    could_not_be_parsed_because_error_rows: List[pandas.Series]

    responsible_core_team_library: ResponsibleCoreTeamLibrary
    lot_wbs_library: LotWbsLibrary

    def get_dml_document_by_code_ged_moe(self, code_ged_moe: str) -> Optional[DmlDocument]:
        dml_lines_found_by_code_ged_moe = self.dml_lines_by_code_ged_moe[code_ged_moe]
        if dml_lines_found_by_code_ged_moe:
            return dml_lines_found_by_code_ged_moe[0].dml_document
        else:
            return None

    def get_dml_line_by_code_ged_moe_and_version(self, code_ged_moe: str, version: int, revision: int = 0) -> Optional[DmlLine]:
        dml_lines_found_by_code_ged_moe = self.dml_lines_by_code_ged_moe[code_ged_moe]

        dml_lines_found = [dml_line for dml_line in dml_lines_found_by_code_ged_moe if dml_line.code_ged_moe == code_ged_moe and dml_line.version == version and dml_line.revision == revision]
        assert dml_lines_found
        assert len(dml_lines_found) == 1
        dml_line_found = dml_lines_found[0]
        return dml_line_found

    def find_document_by_code_ged_moe_title_or_fa(self, code_ged_moe: str, title: str, fa: Optional[FaPa], version: int, revision: int) -> Optional[DmlDocument]:
        return find_document_by_code_ged_moe_title_or_fa(self.dml_documents, code_ged_moe, title, fa, version, revision)

    def find_document_by_code_ged_moe(self, code_ged_moe: str) -> Optional[DmlDocument]:
        documents_found_by_code_ged_moe = [document for document in self.dml_documents if code_ged_moe in document.get_all_code_ged_moes()]
        if documents_found_by_code_ged_moe:
            assert len(documents_found_by_code_ged_moe) == 1
            return documents_found_by_code_ged_moe[0]
        return None

    def find_document_by_title(self, title: str) -> Optional[DmlDocument]:
        documents_found_by_title = [document for document in self.dml_documents if title in document.get_all_titles()]
        if documents_found_by_title:
            assert len(documents_found_by_title) == 1
            return documents_found_by_title[0]
        return None

    class Builder:

        @staticmethod
        def build_with_excel_file(dml_excel_file_full_path: str) -> "DmlFileContent":

            with logger_config.stopwatch_with_label(f"Load {dml_excel_file_full_path}", monitor_ram_usage=True, inform_beginning=True):
                main_data_frame: pandas.DataFrame = pandas.read_excel(dml_excel_file_full_path, sheet_name="Database")
            logger_config.print_and_log_info(f"{dml_excel_file_full_path} has {len(main_data_frame)} items")
            logger_config.print_and_log_info(f" {dml_excel_file_full_path} columns  {main_data_frame.columns[:5]} ...")

            all_lines_found: List[DmlLine] = []
            dml_lines_by_code_ged_moe: Dict[str, List[DmlLine]] = {}
            dml_lines_by_title: Dict[str, List[DmlLine]] = {}
            all_documents_found: List[DmlDocument] = []
            responsible_core_team_library = ResponsibleCoreTeamLibrary()
            lot_wbs_library = LotWbsLibrary()
            could_not_be_parsed_because_error_rows: List[pandas.Series] = []

            with logger_config.stopwatch_with_label("Sort main_data_frame by version"):
                main_data_frame.sort_values(by=["Version"], inplace=True)

            with logger_config.stopwatch_with_label(f"Load and parse {len(main_data_frame)} DML lines"):

                for index, (_, row) in enumerate(main_data_frame.iterrows()):

                    try:

                        code_ged_moe = str(row["Code GED MOE"])
                        raw_title = str(row["Titre Document"])
                        title = raw_title.replace("\n", "_")
                        raw_version = row["Version"]
                        if not isinstance(raw_version, str) and math.isnan(raw_version):
                            raw_version = "-1"
                        version = int(raw_version)
                        raw_revision = row["Révision"]
                        if not isinstance(raw_revision, str) and math.isnan(raw_revision):
                            raw_revision = "-1"
                        revision = int(raw_revision)
                        status = DmlStatus[string_utils.text_to_valid_enum_value_text(str(row["Statut"]))]
                        guide = GuideValue[string_utils.text_to_valid_enum_value_text(str(row["GUIDE"]))] if str(row["GUIDE"]).upper() != "NAN" else GuideValue.NON
                        actual_livraison = convert_dml_date_to_datetime(str(row["Actual Livraison"]))
                        is_last_submit_of_doc = convert_is_last_submit_of_doc(str(row["Dernière Soumission "]))

                        fa = (
                            FaPa(reference=ReferenceFaPa(row["Référence FA"]), actual_delivery=convert_dml_date_to_datetime(str(row["Actual FA"])))
                            if str(row["Actual FA"]) not in ["NaT", "nan", "na"]
                            else None
                        )
                        pa = (
                            FaPa(reference=ReferenceFaPa(row["Référence PA"]), actual_delivery=convert_dml_date_to_datetime(str(row["Actual Emission PA"])))
                            if str(row["Actual Emission PA"]) not in ["NaT", "nan", "na"]
                            else None
                        )
                        rpa = (
                            Rpa(
                                reference=ReferenceFaPa(row["Référence RPA"]),
                                status=DmlStatus[string_utils.text_to_valid_enum_value_text(str(row["Statut RPA"]))] if str(row["Statut RPA"]) not in ["nan", " "] else None,
                                actual_delivery=convert_dml_date_to_datetime(str(row["Actual Retour PA"])),
                            )
                            if str(row["Actual Retour PA"]) not in ["NaT", "nan", "na"]
                            else None
                        )
                        rrpa = (
                            FaPa(reference=ReferenceFaPa(row["Référence RRPA"]), actual_delivery=convert_dml_date_to_datetime(str(row["Actual RRPA"])))
                            if str(row["Actual RRPA"]) not in ["NaT", "nan", "na"]
                            else None
                        )

                        responsible_core_team = responsible_core_team_library.get_responsible_core_team_by_name(str(row["ResponsableCoreTeam"]))
                        lot_wbs = lot_wbs_library.get_lot_wbs_by_name(str(row["Lot WBS"]))
                        be_number = str(row["Numéro du BE"])
                        produit = convert_doc_produit_column(str(row["Document Produit\n(Yes/No)"]))
                        doc_deleted = convert_document_supprime_column(str(row["Document Supprimé"]))

                        dml_document = find_document_by_code_ged_moe_title_or_fa(all_documents_found, code_ged_moe, title, fa, version, revision)
                        if not dml_document:
                            dml_document = DmlDocument()
                            all_documents_found.append(dml_document)

                        dml_line = DmlLine(
                            full_row=row,
                            dml_document=dml_document,
                            code_ged_moe=code_ged_moe,
                            raw_title=raw_title,
                            title=title,
                            version=version,
                            revision=revision,
                            status=status,
                            guide=guide,
                            actual_livraison=actual_livraison,
                            is_last_submit_of_doc=is_last_submit_of_doc,
                            fa=fa,
                            pa=pa,
                            rpa=rpa,
                            rrpa=rrpa,
                            responsible_core_team=responsible_core_team,
                            lot_wbs=lot_wbs,
                            be_number=be_number,
                            produit=produit,
                            doc_deleted=doc_deleted,
                        )

                        all_lines_found.append(dml_line)

                        if code_ged_moe not in dml_lines_by_code_ged_moe:
                            dml_lines_by_code_ged_moe[code_ged_moe] = []
                        dml_lines_by_code_ged_moe[code_ged_moe].append(dml_line)

                        if title not in dml_lines_by_title:
                            dml_lines_by_title[title] = []
                        dml_lines_by_title[title].append(dml_line)

                    except Exception as e:
                        could_not_be_parsed_because_error_rows.append(row)
                        logger_config.print_and_log_exception(e)
                        logger_config.print_and_log_error(f"Could not create line number {index}, code_ged_moe:{code_ged_moe} {row}")
                        logger_config.print_and_log_error(f"Could not create line {row}")

            logger_config.print_and_log_info(f"{len(all_lines_found)} lines found")
            logger_config.print_and_log_info(f"{len(all_documents_found)} documents found")
            logger_config.print_and_log_info(f"{len(responsible_core_team_library.elements)} responsibles core team found")
            logger_config.print_and_log_info(f"{len(lot_wbs_library.elements)} lots wbs found")
            dml_file_content = DmlFileContent(
                dml_documents=all_documents_found,
                dml_lines=all_lines_found,
                dml_lines_by_code_ged_moe=dml_lines_by_code_ged_moe,
                dml_lines_by_title=dml_lines_by_title,
                responsible_core_team_library=responsible_core_team_library,
                lot_wbs_library=lot_wbs_library,
                could_not_be_parsed_because_error_rows=could_not_be_parsed_because_error_rows,
            )
            return dml_file_content
