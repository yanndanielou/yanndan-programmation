import logging
import math
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, cast
from warnings import deprecated

import pandas
from common import excel_utils, string_utils, file_name_utils
from logger import logger_config

import param

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
        return f"{self.full_raw_reference}"

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

        self.version_and_revision = f"V{self.version}-{self.revision}"

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
        return f"Line: code_ged_moe:{self.code_ged_moe} version:{self.version} title:{self.title}"


@dataclass
class DmlDocument:
    dml_lines: List[DmlLine] = field(default_factory=list)

    def get_sorted_dml_lines(self) -> List[DmlLine]:
        return sorted(self.dml_lines, key=lambda l: (l.version, l.revision))

    def get_last_dml_line(self) -> DmlLine:
        return self.get_sorted_dml_lines()[-1]

    def get_penultimate_dml_line(self) -> Optional[DmlLine]:
        return self.get_sorted_dml_lines()[-2] if len(self.get_sorted_dml_lines()) >= 2 else None

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
    elif raw_doc_produit_column_content.lower() == "yes":
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
                f"Searching {code_ged_moe} {title} {fa}. Found with FA (was renamed and reference changed). found doc {document_found_by_fa.get_all_code_ged_moes()} {document_found_by_fa.get_all_titles()} with FAs {document_found_by_fa.get_all_fa_names()}"
            )
            return document_found_by_fa

    return None


@dataclass
class OneDocumentLineStatusReport:
    dml_document: DmlDocument
    line_number: int
    code_ged_moe: str
    title: str
    version: int
    revision: int
    status: DmlStatus
    actual_livraison: Optional[datetime]
    doc_deleted: bool
    fa: Optional[FaPa]
    pa: Optional[FaPa]

    def __post_init__(self) -> None:
        self.version_and_revision = f"V{self.version}-{self.revision}"

    def print_report(self) -> None:
        logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{self.line_number}\tversion:{self.version}\trevision:{self.revision}")
        logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{self.line_number}\tstatus:{self.status}")
        logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{self.line_number}\tactual_livraison:{self.actual_livraison}")
        logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{self.line_number}\tdoc_deleted:{self.doc_deleted}")
        logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{self.line_number}\tfa:{self.fa}")
        logging.info(f"{self.dml_document.get_all_code_ged_moes()}\tLine #{self.line_number}\tpa:{self.pa}")
        logging.info(f"\n")


@dataclass
class OneDocumentStatusReport:
    dml_document: DmlDocument
    all_documents_lines_status_reports: List[OneDocumentLineStatusReport] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.all_code_ged_moes = self.dml_document.get_all_code_ged_moes()
        logger_config.print_and_log_info(f"Prepare report for {self.all_code_ged_moes}")
        # self.document_sorted_dml_lines = self.dml_document.get_sorted_dml_lines()

        self.last_line = self.dml_document.get_last_dml_line()
        assert self.last_line

        self.penultimate_line = self.dml_document.get_penultimate_dml_line()

        for line_number, line in enumerate(self.dml_document.dml_lines):
            self.all_documents_lines_status_reports.append(
                OneDocumentLineStatusReport(
                    dml_document=self.dml_document,
                    line_number=line_number,
                    code_ged_moe=line.code_ged_moe,
                    title=line.title,
                    version=line.version,
                    revision=line.revision,
                    status=line.status,
                    actual_livraison=line.actual_livraison,
                    doc_deleted=line.doc_deleted,
                    fa=line.fa,
                    pa=line.pa,
                )
            )

    def print_all_lines_report(self) -> None:
        for line_number, documents_line_status_report in enumerate(self.all_documents_lines_status_reports):
            documents_line_status_report.print_report()
            logging.info(f"\n")

        self.print_last_line()

    def print_last_line(self) -> None:
        last_line = self.dml_document.get_last_dml_line()
        assert last_line

        logger_config.print_and_log_info(
            f"{self.dml_document.get_all_code_ged_moes()}\tLast line: code_ged_moe:{last_line.code_ged_moe}\ttitle:{last_line.title}\tversion:{last_line.version}\trevision:{last_line.revision}\tstatus:{last_line.status}\tactual_livraison:{last_line.actual_livraison}\tfa:{last_line.fa}\tpa:{last_line.pa}\n\n"
        )

    def print_report(self, full: bool) -> None:
        self.print_all_lines_report()
        self.print_last_line()

    class Builder:

        @staticmethod
        def build_by_code_ged_moe(dml_file_content: "DmlFileContent", code_ged_moe: str) -> "OneDocumentStatusReport":
            dml_document = dml_file_content.find_document_by_code_ged_moe(code_ged_moe)
            assert dml_document, f"Could not find doc {code_ged_moe}"
            document_status_report = OneDocumentStatusReport(dml_document=dml_document)
            return document_status_report


@dataclass
class DocumentsStatusReport:
    name: str
    all_documents_status_reports: List[OneDocumentStatusReport]

    def __post_init__(self) -> None:
        self.output_directory_path = "Reports"

        os.makedirs(self.output_directory_path, exist_ok=True)

        self.output_file_name_without_extension = "Report_" + self.name + "_" + file_name_utils.get_file_suffix_with_current_datetime()
        self.output_file_full_report_full_path = self.output_directory_path + "/" + self.output_file_name_without_extension + "_full_report.xlsx"
        self.output_file_synthetic_report_full_path = self.output_directory_path + "/" + self.output_file_name_without_extension + "_synthetic_report.xlsx"

    class Builder:

        @staticmethod
        def build_by_code_ged_moe(name: str, dml_file_content: "DmlFileContent", codes_ged_moe: List[str]) -> "DocumentsStatusReport":
            all_documents_status_reports: List[OneDocumentStatusReport] = []
            for code_ged_moe in set(codes_ged_moe):
                one_document_status_report = OneDocumentStatusReport.Builder.build_by_code_ged_moe(dml_file_content=dml_file_content, code_ged_moe=code_ged_moe)
                all_documents_status_reports.append(one_document_status_report)

            ret = DocumentsStatusReport(name=name, all_documents_status_reports=all_documents_status_reports)
            return ret

    def write_full_report_to_excel(self) -> None:
        """Write all OneDocumentLineStatusReport entries from all documents into an Excel file.

        The output file path is `self.output_file_full_path`.
        Columns written correspond to attributes of `OneDocumentLineStatusReport`.
        """
        rows: List[Dict[str, object]] = []

        for document_status in self.all_documents_status_reports:
            for line_status in document_status.all_documents_lines_status_reports:
                # Convert complex attributes to serializable representations
                dml_document_codes = ",".join(sorted(document_status.dml_document.get_all_code_ged_moes()))

                row: Dict[str, object] = {
                    "dml_document_codes": dml_document_codes,
                    "doc_deleted": line_status.doc_deleted,
                    "line_number": line_status.line_number,
                    "code_ged_moe": line_status.code_ged_moe,
                    "title": line_status.title,
                    "version": line_status.version,
                    "revision": line_status.revision,
                    "version_and_revision": line_status.version_and_revision,
                    "status": line_status.status.name if line_status.status is not None else None,
                    "actual_livraison": line_status.actual_livraison.strftime("%Y-%m-%d") if line_status.actual_livraison else None,
                    "fa_reference": line_status.fa.reference.full_raw_reference if line_status.fa and line_status.fa.reference else None,
                    "fa_actual_delivery": line_status.fa.actual_delivery.strftime("%Y-%m-%d") if line_status.fa and line_status.fa.actual_delivery else None,
                    "pa_reference": line_status.pa.reference.full_raw_reference if line_status.pa and line_status.pa.reference else None,
                    "pa_actual_delivery": line_status.pa.actual_delivery.strftime("%Y-%m-%d") if line_status.pa and line_status.pa.actual_delivery else None,
                }

                rows.append(row)

        df = pandas.DataFrame(rows)

        # Ensure output directory exists (in case it was removed after instantiation)
        os.makedirs(self.output_directory_path, exist_ok=True)

        report_full_path = self.output_file_full_report_full_path
        df.to_excel(report_full_path, index=False)
        logger_config.print_and_log_info(f"Wrote {len(df)} rows to {report_full_path}")

    def prepare_synthetic_report_to_excel(self, warn_if_doc_deleted: bool, include_report_name: bool = False) -> List[Dict[str, object]]:
        """Write all OneDocumentLineStatusReport entries from all documents into an Excel file.

        The output file path is `self.output_file_full_path`.
        Columns written correspond to attributes of `OneDocumentLineStatusReport`.
        """
        rows: List[Dict[str, object]] = []

        for document_status in self.all_documents_status_reports:
            last_line = document_status.last_line
            penultimate_line = document_status.penultimate_line

            if warn_if_doc_deleted and last_line.doc_deleted:
                logger_config.print_and_log_warning(f"{self.name}: doc {last_line.code_ged_moe} is deleted!")

            # Convert complex attributes to serializable representations
            dml_document_codes = ",".join(sorted(document_status.dml_document.get_all_code_ged_moes()))

            row: Dict[str, object] = {
                "report_name": self.name,
                "dml_document_codes": dml_document_codes,
                "doc_deleted": last_line.doc_deleted,
                "last_line code_ged_moe": last_line.code_ged_moe,
                "last_line title": last_line.title,
                "last_line version_and_revision": last_line.version_and_revision,
                "last_line status": last_line.status.name if last_line.status is not None else None,
                "last_line actual_livraison": last_line.actual_livraison.strftime("%Y-%m-%d") if last_line.actual_livraison else None,
                "last_line fa": last_line.fa,
                "last_line pa": last_line.pa,
                "penultimate_line version_and_revision": "NA" if penultimate_line is None else penultimate_line.version_and_revision,
                "penultimate_line status": "NA" if penultimate_line is None else penultimate_line.status.name if penultimate_line.status is not None else None,
                "penultimate_line actual_livraison": ("NA" if penultimate_line is None else (penultimate_line.actual_livraison.strftime("%Y-%m-%d") if penultimate_line.actual_livraison else None)),
                "penultimate_line fa": ("NA" if penultimate_line is None else penultimate_line.fa),
                "penultimate_line fa_reference": (
                    "NA" if penultimate_line is None else penultimate_line.fa.reference.full_raw_reference if penultimate_line.fa and penultimate_line.fa.reference else None
                ),
                "penultimate_line fa_actual_delivery": (
                    "NA" if penultimate_line is None else penultimate_line.fa.actual_delivery.strftime("%Y-%m-%d") if penultimate_line.fa and penultimate_line.fa.actual_delivery else None
                ),
                "last_line version": last_line.version,
                "last_line revision": last_line.revision,
                "last_line fa_reference": last_line.fa.reference.full_raw_reference if last_line.fa and last_line.fa.reference else None,
                "last_line fa_actual_delivery": last_line.fa.actual_delivery.strftime("%Y-%m-%d") if last_line.fa and last_line.fa.actual_delivery else None,
                "last_line pa_reference": last_line.pa.reference.full_raw_reference if last_line.pa and last_line.pa.reference else None,
                "last_line pa_actual_delivery": last_line.pa.actual_delivery.strftime("%Y-%m-%d") if last_line.pa and last_line.pa.actual_delivery else None,
            }

            rows.append(row)

        return rows

    def write_synthetic_report_to_excel(self, warn_if_doc_deleted: bool) -> None:
        """Write all OneDocumentLineStatusReport entries from all documents into an Excel file.

        The output file path is `self.output_file_full_path`.
        Columns written correspond to attributes of `OneDocumentLineStatusReport`.
        """
        rows = self.prepare_synthetic_report_to_excel(warn_if_doc_deleted)

        df = pandas.DataFrame(rows)

        # Ensure output directory exists (in case it was removed after instantiation)
        os.makedirs(self.output_directory_path, exist_ok=True)

        report_full_path = self.output_file_synthetic_report_full_path
        df.to_excel(report_full_path, index=False)
        logger_config.print_and_log_info(f"Wrote {len(df)} rows to {report_full_path}")


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
