import json
from typing import TYPE_CHECKING, List, Optional, cast, Any
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


def treat_cx_line(
    line_number: int,
    acq_term_original_line: str,
    eqpt_id: str,
    term_id: str,
    input_file_line_splitted: List[str],
    signal_number_position: int,
    ats_v6_14_inv: AtsInvDatabaseForVersion,
    patched_ats_inv: AtsInvDatabaseForVersion,
    output_file: Any,
    offset_in_signal_number: int,
) -> None:
    signal_id = "_".join(
        term_id.replace("_RC_SIGNAL_OVERRIDE_STATUS", "").replace("_ST_ANDREWS_CROSS_MAINT_SIGNAL_LIGHT_REQ_ON", "").replace("_ST_ANDREWS_CROSS_MAINT_SIGNAL_LIGHT_REQ_OFF", "").split("_")[3:]
    )
    signal_number_str_in_original_acq_term = input_file_line_splitted[signal_number_position]
    signal_number_int_in_original_acq_term_without_offset = int(signal_number_str_in_original_acq_term)
    signal_number_int_in_original_acq_term_with_offset = signal_number_int_in_original_acq_term_without_offset + offset_in_signal_number

    entry_in_ats_v6_14_inv = ats_v6_14_inv.get_entry_by_zc_and_signal_id(zc_id=eqpt_id, signal_id=signal_id)
    entry_in_patched_ats_inv = patched_ats_inv.get_entry_by_zc_and_signal_id(zc_id=eqpt_id, signal_id=signal_id)

    assert signal_number_int_in_original_acq_term_with_offset == entry_in_ats_v6_14_inv.num_signal_zc

    if signal_number_int_in_original_acq_term_with_offset == entry_in_patched_ats_inv.num_signal_zc:
        logger_config.print_and_log_info(
            f"Line {line_number}, {term_id}, signal {signal_id}, pas {eqpt_id}: do nothing, keep {signal_number_int_in_original_acq_term_with_offset}, to:{entry_in_ats_v6_14_inv.num_signal_zc}"
        )
        output_file.write(acq_term_original_line)

    else:
        acq_term_line_before_signal_number = ";".join(input_file_line_splitted[:signal_number_position]) + ";"
        acq_term_line_after_signal_number = ";" + ";".join(input_file_line_splitted[signal_number_position + 1 :])

        reconstructed_initial_line = acq_term_line_before_signal_number + str(signal_number_int_in_original_acq_term_without_offset) + acq_term_line_after_signal_number
        assert reconstructed_initial_line == acq_term_original_line

        new_line = acq_term_line_before_signal_number + str(entry_in_patched_ats_inv.num_signal_zc - offset_in_signal_number) + acq_term_line_after_signal_number
        output_file.write(new_line)

        logger_config.print_and_log_info(
            f"Line {line_number}, {term_id}, signal {signal_id}, pas {eqpt_id}: change : {signal_number_int_in_original_acq_term_with_offset}, to:{entry_in_ats_v6_14_inv.num_signal_zc}, in patched_ats_inv:{entry_in_patched_ats_inv.num_signal_zc}"
        )
    pass


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

            for line_number, input_file_original_line in enumerate(input_acq_term_file_lines):
                input_file_line_splitted = input_file_original_line.split(";")
                eqpt_id = input_file_line_splitted[1]
                term_id = input_file_line_splitted[3]
                assert term_id

                if "RC_SIGNAL_OVERRIDE_STATUS" in term_id:

                    treat_cx_line(
                        line_number=line_number,
                        acq_term_original_line=input_file_original_line,
                        eqpt_id=eqpt_id,
                        term_id=term_id,
                        input_file_line_splitted=input_file_line_splitted,
                        signal_number_position=9,
                        output_file=output_file,
                        ats_v6_14_inv=ats_v6_14_inv,
                        patched_ats_inv=patched_ats_inv,
                        offset_in_signal_number=1,
                    )
                    """
                    signal_id = "_".join(term_id.replace("_RC_SIGNAL_OVERRIDE_STATUS", "").split("_")[3:])
                    signal_number_str_in_original_acq_term = input_file_line_splitted[9]
                    signal_number_int_in_original_acq_term = int(signal_number_str_in_original_acq_term)
                    signal_number_int_in_original_acq_term_starting_1 = signal_number_int_in_original_acq_term + 1

                    entry_in_ats_v6_14_inv = ats_v6_14_inv.get_entry_by_zc_and_signal_id(zc_id=eqpt_id, signal_id=signal_id)
                    entry_in_patched_ats_inv = patched_ats_inv.get_entry_by_zc_and_signal_id(zc_id=eqpt_id, signal_id=signal_id)

                    assert signal_number_int_in_original_acq_term_starting_1 == entry_in_ats_v6_14_inv.num_signal_zc

                    if signal_number_int_in_original_acq_term_starting_1 == entry_in_patched_ats_inv.num_signal_zc:
                        logger_config.print_and_log_info(
                            f"Line {line_number}, {term_id}, signal {signal_id}, pas {eqpt_id}: do nothing, keep {signal_number_int_in_original_acq_term}, to:{entry_in_ats_v6_14_inv.num_signal_zc}"
                        )
                        output_file.write(input_file_original_line)

                    else:
                        new_line = ";".join(input_file_line_splitted[:8]) + ";" + str(entry_in_patched_ats_inv.num_signal_zc - 1) + ";" + ";".join(input_file_line_splitted[10:])
                        output_file.write(new_line)

                        logger_config.print_and_log_info(
                            f"Line {line_number}, {term_id}, signal {signal_id}, pas {eqpt_id}: change : {signal_number_int_in_original_acq_term}, to:{entry_in_ats_v6_14_inv.num_signal_zc}, in patched_ats_inv:{entry_in_patched_ats_inv.num_signal_zc}"
                        )
                        """
                    pass

                elif "ST_ANDREWS_CROSS_MAINT_SIGNAL_LIGHT" in term_id:

                    treat_cx_line(
                        line_number=line_number,
                        acq_term_original_line=input_file_original_line,
                        eqpt_id=eqpt_id,
                        term_id=term_id,
                        input_file_line_splitted=input_file_line_splitted,
                        signal_number_position=12,
                        output_file=output_file,
                        ats_v6_14_inv=ats_v6_14_inv,
                        patched_ats_inv=patched_ats_inv,
                        offset_in_signal_number=0,
                    )
                    """signal_id = "_".join(term_id.replace("_ST_ANDREWS_CROSS_MAINT_SIGNAL_LIGHT_REQ_ON", "").replace("_ST_ANDREWS_CROSS_MAINT_SIGNAL_LIGHT_REQ_OFF", "").split("_")[3:])
                    signal_number_str_in_original_acq_term = input_file_line_splitted[12]
                    signal_number_int_in_original_acq_term = int(signal_number_str_in_original_acq_term)

                    entry_in_ats_v6_14_inv = ats_v6_14_inv.get_entry_by_zc_and_signal_id(zc_id=eqpt_id, signal_id=signal_id)
                    entry_in_patched_ats_inv = patched_ats_inv.get_entry_by_zc_and_signal_id(zc_id=eqpt_id, signal_id=signal_id)

                    assert signal_number_int_in_original_acq_term == entry_in_ats_v6_14_inv.num_signal_zc

                    if signal_number_int_in_original_acq_term == entry_in_patched_ats_inv.num_signal_zc:
                        logger_config.print_and_log_info(
                            f"Line {line_number}, {term_id}, signal {signal_id}, pas {eqpt_id}: do nothing, keep {signal_number_int_in_original_acq_term}, to:{entry_in_ats_v6_14_inv.num_signal_zc}"
                        )
                        output_file.write(input_file_original_line)

                    else:
                        new_line = ";".join(input_file_line_splitted[:11]) + ";" + str(entry_in_patched_ats_inv.num_signal_zc) + ";" + ";".join(input_file_line_splitted[13:])
                        output_file.write(new_line)

                        logger_config.print_and_log_info(
                            f"Line {line_number}, {term_id}, signal {signal_id}, pas {eqpt_id}: change : {signal_number_int_in_original_acq_term}, to:{entry_in_ats_v6_14_inv.num_signal_zc}, in patched_ats_inv:{entry_in_patched_ats_inv.num_signal_zc}"
                        )"""
                    pass

                else:
                    pass
                    output_file.write(input_file_original_line)


if __name__ == "__main__":
    main()
