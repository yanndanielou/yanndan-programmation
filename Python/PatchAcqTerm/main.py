import json
from typing import TYPE_CHECKING, List, Optional, cast
from dataclasses import dataclass, field
from typing import Dict

from common import file_utils, json_encoders
from logger import logger_config

import pandas


OUTPUT_PARENT_DIRECTORY_NAME = "Output"


@dataclass
class AtsSignalZcInvariantEntry:
    signal_id: str
    num_signal_zc: int
    zc_id: str


@dataclass
class AtsInvDatabaseForVersion:
    file_path: str
    all_signal_zc_entries: List[AtsSignalZcInvariantEntry] = field(default_factory=list)

    def get_entry_by_zc_and_signal_id(self, zc_id: str, signal_id: str) -> AtsSignalZcInvariantEntry:
        matchs_found = [entry for entry in self.all_signal_zc_entries if entry.signal_id == signal_id and entry.zc_id == zc_id]
        assert matchs_found
        assert len(matchs_found) == 1
        return matchs_found[0]


def build_ats_inv_for_version(file_path: str) -> AtsInvDatabaseForVersion:

    with logger_config.stopwatch_with_label(f"Load {file_path}", monitor_ram_usage=True, inform_beginning=False):
        signal_zc_csv_data_frame = pandas.read_csv(filepath_or_buffer=file_path, sep=";")

    ats_inv = AtsInvDatabaseForVersion(file_path)
    for _, row in signal_zc_csv_data_frame.iterrows():
        signal_id = row["signal_id".upper()]
        num_signal_zc = int(row["num_signal_zc".upper()])
        zc_id = row["zc_id".upper()]
        entry = AtsSignalZcInvariantEntry(signal_id=signal_id, num_signal_zc=num_signal_zc, zc_id=zc_id)
        ats_inv.all_signal_zc_entries.append(entry)

    logger_config.print_and_log_info(f"{len(ats_inv.all_signal_zc_entries)} entries built for {file_path}")
    return ats_inv


def main() -> None:
    with logger_config.application_logger("patchacqterm"):

        with open(file="Input_Downloaded/NEXT_acqTermes.csv", mode=("r"), encoding="ANSI") as input_acq_term_file:
            input_acq_term_file_content = input_acq_term_file
            input_acq_term_file_lines = input_acq_term_file_content.readlines()

        dc_signal_pas_csv_file_path = "Input_Downloaded/dc_signal_pas.csv"
        with logger_config.stopwatch_with_label(f"Load {dc_signal_pas_csv_file_path}", monitor_ram_usage=True, inform_beginning=True):
            dc_signal_pas_data_frame = pandas.read_csv(filepath_or_buffer=dc_signal_pas_csv_file_path, sep=";")

        ats_v6_14_inv = build_ats_inv_for_version("Input_Downloaded/SIGNAL_ZC_V6_14.csv")

        patched_ats_inv = build_ats_inv_for_version("Input_Downloaded/Patch_SIGNAL_ZC.csv")

        with open("output/output_acq_term.csv", mode="w", encoding="ANSI") as output_file:

            for input_file_original_line in input_acq_term_file_lines:
                input_file_line_splitted = input_file_original_line.split(";")
                eqpt_id = input_file_line_splitted[1]
                term_id = input_file_line_splitted[3]
                assert term_id

                term_id_splitted_underscore = term_id.split("_")

                if "RC_SIGNAL_OVERRIDE_STATUS" in term_id:
                    signal_id = "_".join(term_id.replace("_RC_SIGNAL_OVERRIDE_STATUS", "").split("_")[3:])
                    signal_number_str_in_original_acq_term = input_file_line_splitted[9]
                    signal_number_int_in_original_acq_term = int(signal_number_str_in_original_acq_term)

                    entry_in_ats_v6_14_inv = ats_v6_14_inv.get_entry_by_zc_and_signal_id(zc_id=eqpt_id, signal_id=signal_id)
                    entry_in_patched_ats_inv = patched_ats_inv.get_entry_by_zc_and_signal_id(zc_id=eqpt_id, signal_id=signal_id)

                    logger_config.print_and_log_info(f"{term_id}, signal {signal_id}, pas {eqpt_id}, current signal number in acq term: {signal_number_int_in_original_acq_term}")
                    pass

                elif "ST_ANDREWS_CROSS_MAINT_SIGNAL_LIGHT" in term_id:
                    signal_id = "_".join(term_id.replace("_ST_ANDREWS_CROSS_MAINT_SIGNAL_LIGHT_REQ_ON", "").replace("_ST_ANDREWS_CROSS_MAINT_SIGNAL_LIGHT_REQ_OFF", "").split("_")[3:])
                    signal_number_str_in_original_acq_term = input_file_line_splitted[10]
                    signal_number_int_in_original_acq_term = int(signal_number_str_in_original_acq_term)

                    entry_in_ats_v6_14_inv = ats_v6_14_inv.get_entry_by_zc_and_signal_id(zc_id=eqpt_id, signal_id=signal_id)
                    entry_in_patched_ats_inv = patched_ats_inv.get_entry_by_zc_and_signal_id(zc_id=eqpt_id, signal_id=signal_id)

                    logger_config.print_and_log_info(
                        f"{term_id}, signal {signal_id}, pas {eqpt_id},  current signal number in acq term: {signal_number_int_in_original_acq_term}, in v6_14_inv:{entry_in_ats_v6_14_inv.num_signal_zc}, in patched_ats_inv:{entry_in_patched_ats_inv.num_signal_zc}"
                    )
                    pass

                else:
                    pass
                    output_file.write(input_file_original_line)


if __name__ == "__main__":
    main()
