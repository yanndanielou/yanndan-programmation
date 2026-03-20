from logger import logger_config
import pandas
from typing import List
from dataclasses import dataclass, field


@dataclass
class Mesure:
    arssi_id: str
    full_text: str


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
    logger_config.print_and_log_info(f"{len(doors_mesures)} doors_mesures")

    for index, (_, row) in enumerate(arssi_v8_doors_data_frame.iterrows()):
        arssi_id = row["ID"]
        full_text = row["Description"]
        arssi_v8_mesures.append(Mesure(arssi_id=arssi_id, full_text=full_text))

    logger_config.print_and_log_info(f"{len(arssi_v8_mesures)} arssi_v8_mesures")

    for arssi_mesure in arssi_v8_mesures:
        found_doors_mesures_by_arssi_id = [doors_mesure for doors_mesure in doors_mesures if doors_mesure.arssi_id == arssi_mesure.arssi_id]
        assert len(found_doors_mesures_by_arssi_id) < 2
        found_doors_mesure_by_arssi_id = found_doors_mesures_by_arssi_id[0] if found_doors_mesures_by_arssi_id else None

        found_doors_mesures_by_full_text = [doors_mesure for doors_mesure in doors_mesures if doors_mesure.full_text == arssi_mesure.full_text]
        if len(found_doors_mesures_by_full_text) > 1:
            logger_config.print_and_log_error(f"{len(found_doors_mesures_by_full_text)} doors mesures found with text {arssi_mesure.full_text}: {found_doors_mesures_by_full_text}")

        if not found_doors_mesures_by_full_text:
            logger_config.print_and_log_error(
                f"Could not find ARSSI text {arssi_mesure.full_text} in doors. found {found_doors_mesure_by_arssi_id.full_text if found_doors_mesure_by_arssi_id else None} in doors for {arssi_mesure.arssi_id}"
            )

        found_doors_mesure_by_full_text = found_doors_mesures_by_full_text[0] if found_doors_mesures_by_full_text else None

        logger_config.print_and_log_info(
            f"Searching arssi mesure {arssi_mesure}\nFound by ID {arssi_mesure.arssi_id}:{found_doors_mesure_by_arssi_id is not None},\nFound by text {arssi_mesure.full_text}:{found_doors_mesure_by_full_text is not None}\n"
        )

    for arssi_mesure in arssi_v8_mesures:
        found_doors_mesures_by_arssi_id = [doors_mesure for doors_mesure in doors_mesures if doors_mesure.arssi_id == arssi_mesure.arssi_id]
        assert len(found_doors_mesures_by_arssi_id) < 2
        found_doors_mesure_by_arssi_id = found_doors_mesures_by_arssi_id[0] if found_doors_mesures_by_arssi_id else None

        found_doors_mesures_by_full_text = [doors_mesure for doors_mesure in doors_mesures if doors_mesure.full_text == arssi_mesure.full_text]
        if len(found_doors_mesures_by_full_text) > 1:
            logger_config.print_and_log_error(f"{len(found_doors_mesures_by_full_text)} doors mesures found with text {arssi_mesure.full_text}: {found_doors_mesures_by_full_text}")

        if not found_doors_mesures_by_full_text:
            logger_config.print_and_log_error(
                f"Could not find ARSSI text {arssi_mesure.full_text} in doors. found {found_doors_mesure_by_arssi_id.full_text if found_doors_mesure_by_arssi_id else None} in doors for {arssi_mesure.arssi_id}"
            )

        found_doors_mesure_by_full_text = found_doors_mesures_by_full_text[0] if found_doors_mesures_by_full_text else None

        logger_config.print_and_log_info(
            f"Searching arssi mesure {arssi_mesure}\nFound by ID {arssi_mesure.arssi_id}:{found_doors_mesure_by_arssi_id is not None},\nFound by text {arssi_mesure.full_text}:{found_doors_mesure_by_full_text is not None}\n"
        )
