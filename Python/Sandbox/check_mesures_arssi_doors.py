from dataclasses import dataclass
from typing import List

import pandas
from logger import logger_config


@dataclass
class Mesure:
    arssi_id: str
    full_text: str

    def __post_init__(self) -> None:
        self.cleaned_text = self.full_text.replace("�uvre", "oeuvre").replace("�", "")


def perform_check(parsed_mesures: List[Mesure], other_source_mesures: List[Mesure], parse_mesure_label: str, other_source_mesure_label: str) -> None:

    for parsed_mesure in parsed_mesures:
        found_other_source_mesures_by_arssi_id = [other_source_mesure for other_source_mesure in other_source_mesures if other_source_mesure.arssi_id == parsed_mesure.arssi_id]

        if len(found_other_source_mesures_by_arssi_id) > 1:
            logger_config.print_and_log_error(
                f"{len(found_other_source_mesures_by_arssi_id)} {other_source_mesure_label} mesures found with id {parsed_mesure.arssi_id}: {found_other_source_mesures_by_arssi_id}"
            )

        assert len(found_other_source_mesures_by_arssi_id) < 2
        found_other_source_mesure_by_arssi_id = found_other_source_mesures_by_arssi_id[0] if found_other_source_mesures_by_arssi_id else None

        found_other_source_mesures_by_full_text = [other_source_mesure for other_source_mesure in other_source_mesures if other_source_mesure.cleaned_text == parsed_mesure.cleaned_text]
        if len(found_other_source_mesures_by_full_text) > 1:
            logger_config.print_and_log_error(
                f"{len(found_other_source_mesures_by_full_text)} {other_source_mesure_label} mesures found with text {parsed_mesure.cleaned_text}: {found_other_source_mesures_by_full_text}"
            )

        if not found_other_source_mesures_by_full_text:
            logger_config.print_and_log_error(
                f"Could not find {parse_mesure_label} text \n{parsed_mesure.cleaned_text} in {other_source_mesure_label}.\nfound\n{found_other_source_mesure_by_arssi_id.cleaned_text if found_other_source_mesure_by_arssi_id else None}\nin {other_source_mesure_label} for {parsed_mesure.arssi_id}"
            )

        found_other_source_mesure_by_full_text = found_other_source_mesures_by_full_text[0] if found_other_source_mesures_by_full_text else None

        logger_config.print_and_log_info(
            f"Searching {parse_mesure_label} mesure {parsed_mesure}\nFound by ID {parsed_mesure.arssi_id}:{found_other_source_mesure_by_arssi_id is not None},\nFound by text {parsed_mesure.cleaned_text}:{found_other_source_mesure_by_full_text is not None}\n"
        )


with logger_config.application_logger():

    doors_data_frame: pandas.DataFrame = pandas.read_excel(r"C:\Users\fr232487\Downloads\mesures ARSSI.xlsx", sheet_name="DOORS")
    arssi_v8_doors_data_frame: pandas.DataFrame = pandas.read_excel(r"C:\Users\fr232487\Downloads\mesures ARSSI.xlsx", sheet_name="ARSSI")

    doors_mesures: List[Mesure] = []
    arssi_v8_mesures: List[Mesure] = []

    for index, (_, row) in enumerate(doors_data_frame.iterrows()):
        doors_id = row["ID"]
        arssi_id = row["REQ Imported ID"]
        full_text_doors = row["Allocation Mesures Sous-système"]
        doors_mesures.append(Mesure(arssi_id=arssi_id, full_text=full_text_doors))
    logger_config.print_and_log_info(f"{len(doors_mesures)} doors_mesures\n{'\n'.join(str(doors_mesures))}")

    for index, (_, row) in enumerate(arssi_v8_doors_data_frame.iterrows()):
        arssi_id = row["ID"]
        full_text = row["Description"]
        arssi_v8_mesures.append(Mesure(arssi_id=arssi_id, full_text=full_text))

    logger_config.print_and_log_info(f"{len(arssi_v8_mesures)} arssi_v8_mesures\n{'\n'.join(str(arssi_v8_mesures))}")

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
