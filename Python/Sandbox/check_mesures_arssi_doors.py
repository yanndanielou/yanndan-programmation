import inspect
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas
from common import file_utils, json_encoders, reports_utils
from logger import logger_config

OUTPUT_PARENT_DIRECTORY_NAME = "output"


@dataclass
class Mesure:
    source_label: str
    arssi_id: str
    full_text: str

    def __post_init__(self) -> None:
        text = self.full_text

        # Try common mojibake repair path (windows-1252 -> utf-8), else ignore
        try:
            text = text.encode("cp1252", errors="replace").decode("utf8", errors="replace")
        except (UnicodeDecodeError, UnicodeEncodeError):
            text = self.full_text

        text = text.replace("�uvre", "oeuvre").replace("�", "")
        text = text.replace("œ", "oe").replace("Œ", "OE").replace("  ", " ")
        text = unicodedata.normalize("NFC", text)

        self.cleaned_text = text

    def __str__(self) -> str:
        return f"\n{self.source_label}\n{self.arssi_id}\n{self.cleaned_text}\n"


@dataclass
class MesureComparisonResult:
    reference_mesure: Mesure
    all_found_by_arssi_id: List[Mesure] = field(default_factory=list)
    mesure_found_by_arssi_id: Optional[Mesure] = None
    all_found_by_text: List[Mesure] = field(default_factory=list)
    mesure_found_by_text: Optional[Mesure] = None


def perform_check(parsed_mesures: List[Mesure], other_source_mesures: List[Mesure], parse_mesure_label: str, other_source_mesure_label: str) -> List[MesureComparisonResult]:

    comparison_results: List[MesureComparisonResult] = []

    for parsed_mesure in parsed_mesures:
        comparison_result = MesureComparisonResult(reference_mesure=parsed_mesure)
        comparison_results.append(comparison_result)
        comparison_result.all_found_by_arssi_id = [other_source_mesure for other_source_mesure in other_source_mesures if other_source_mesure.arssi_id == parsed_mesure.arssi_id]

        if len(comparison_result.all_found_by_arssi_id) > 1:
            logger_config.print_and_log_error(
                f"{len(comparison_result.all_found_by_arssi_id)} {other_source_mesure_label} mesures found with id {parsed_mesure.arssi_id}: {comparison_result.all_found_by_arssi_id}"
            )

        assert len(comparison_result.all_found_by_arssi_id) < 2
        comparison_result.mesure_found_by_arssi_id = comparison_result.all_found_by_arssi_id[0] if comparison_result.all_found_by_arssi_id else None

        comparison_result.all_found_by_text = [other_source_mesure for other_source_mesure in other_source_mesures if other_source_mesure.cleaned_text == parsed_mesure.cleaned_text]
        if len(comparison_result.all_found_by_text) > 1:
            logger_config.print_and_log_error(
                f"{len(comparison_result.all_found_by_text)} {other_source_mesure_label} mesures found with text \n{parsed_mesure.cleaned_text}\n:\n{'\n'.join(found_other_source_mesure.cleaned_text for found_other_source_mesure in  comparison_result.all_found_by_text)}"
            )

        if not comparison_result.all_found_by_text:
            logger_config.print_and_log_error(
                f"Could not find {parse_mesure_label} text \n{parsed_mesure.cleaned_text} in {other_source_mesure_label}.\nfound\n{comparison_result.mesure_found_by_arssi_id.cleaned_text if comparison_result.mesure_found_by_arssi_id else None}\nin {other_source_mesure_label} for {parsed_mesure.arssi_id}"
            )

        comparison_result.mesure_found_by_text = comparison_result.all_found_by_text[0] if comparison_result.all_found_by_text else None

        logger_config.print_and_log_info(
            f"Searching {parse_mesure_label} mesure {parsed_mesure}\nFound by ID\n{parsed_mesure.arssi_id}\n:\n{comparison_result.mesure_found_by_arssi_id is not None}\n,\nFound by text\n{parsed_mesure.cleaned_text}:{comparison_result.mesure_found_by_text is not None}\n"
        )

    reports_utils.save_rows_to_output_files(
        rows_as_list_dict=[
            {
                "Reference mesure source": comparison_result.reference_mesure.source_label,
                "Reference mesure id": comparison_result.reference_mesure.arssi_id,
                "Reference mesure text": comparison_result.reference_mesure.full_text,
                "Number of all_found_by_arssi_id": len(comparison_result.all_found_by_arssi_id),
                "comparison_result.mesure_found_by_arssi_id.full_text": comparison_result.mesure_found_by_arssi_id.full_text if comparison_result.mesure_found_by_arssi_id else None,
                "comparison_result.mesure_found_by_arssi_id.full_text is same": comparison_result.mesure_found_by_arssi_id.full_text if comparison_result.mesure_found_by_arssi_id else None,
                "Number of all_found_by_text": len(comparison_result.all_found_by_text),
                "comparison_result.mesure_found_by_text.arssi_id": (
                    comparison_result.mesure_found_by_text.arssi_id == comparison_result.reference_mesure.full_text if comparison_result.mesure_found_by_text else None
                ),
                "comparison_result.mesure_found_by_text.arssi_id is same": (
                    comparison_result.mesure_found_by_text.arssi_id == comparison_result.reference_mesure.arssi_id if comparison_result.mesure_found_by_text else None
                ),
            }
            for comparison_result in comparison_results
        ],
        file_base_name=f"Comparison {parse_mesure_label} with {other_source_mesure_label}",
        output_directory_path=OUTPUT_PARENT_DIRECTORY_NAME,
    )

    return comparison_results


def save_rows_to_output_files(rows_as_list_dict: List[Dict[str, Any]], file_base_name: str) -> None:
    with logger_config.stopwatch_with_label(f"{inspect.stack(0)[0].function} for {len(rows_as_list_dict)} lines to {file_base_name}", inform_beginning=True):
        file_path_without_suffix = f"{OUTPUT_PARENT_DIRECTORY_NAME}/{file_base_name}"
        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(rows_as_list_dict, f"{file_path_without_suffix}.json")
        pandas.DataFrame(rows_as_list_dict).to_excel(f"{file_path_without_suffix}.xlsx", index=False)
        pandas.DataFrame(rows_as_list_dict).to_csv(f"{file_path_without_suffix}.csv", index=False)


def main() -> None:

    with logger_config.application_logger():
        file_utils.create_folder_if_not_exist(OUTPUT_PARENT_DIRECTORY_NAME)

        doors_data_frame: pandas.DataFrame = pandas.read_excel(r"C:\Users\fr232487\Downloads\mesures ARSSI.xlsx", sheet_name="DOORS")
        arssi_v8_doors_data_frame: pandas.DataFrame = pandas.read_excel(r"C:\Users\fr232487\Downloads\mesures ARSSI.xlsx", sheet_name="ARSSI")

        doors_mesures: List[Mesure] = []
        arssi_v8_mesures: List[Mesure] = []

        for index, (_, row) in enumerate(doors_data_frame.iterrows()):
            doors_id = row["ID"]
            arssi_id = row["REQ Imported ID"]
            full_text_doors = row["Allocation Mesures Sous-système"]
            doors_mesures.append(Mesure(source_label="Doors", arssi_id=arssi_id, full_text=full_text_doors))
        logger_config.print_and_log_info(f"{len(doors_mesures)} doors_mesures")  # \n{'\n'.join(str(doors_mesures))}")

        for index, (_, row) in enumerate(arssi_v8_doors_data_frame.iterrows()):
            arssi_id = row["ID"]
            full_text = row["Description"]
            arssi_v8_mesures.append(Mesure(source_label="ARSSI V8", arssi_id=arssi_id, full_text=full_text))

        logger_config.print_and_log_info(f"{len(arssi_v8_mesures)} arssi_v8_mesures")  # \n{'\n'.join(str(arssi_v8_mesures))}")

        perform_check(
            parsed_mesures=arssi_v8_mesures,
            other_source_mesures=doors_mesures,
            parse_mesure_label="arssi v8",
            other_source_mesure_label="doors",
        )

        perform_check(
            parsed_mesures=doors_mesures,
            other_source_mesures=arssi_v8_mesures,
            parse_mesure_label="doors",
            other_source_mesure_label="arssi v8",
        )


if __name__ == "__main__":
    main()
