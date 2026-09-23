import os
from collections import OrderedDict
from itertools import chain

from common import reports_utils
from logger import logger_config

from stsloganalyzis.ppn import ppn_log


def main() -> None:

    with logger_config.application_logger():

        root_path = r"D:\temp\2026-09-20 logs PPN we mars 26"
        # all_sub_directories = os.listdir(root_path)
        all_sub_directories = [
            "log_cab1_PPN_A.tar",
            "ppn_cab2_log.tar",
        ]  # + os.listdir(root_path)

        logger_config.print_and_log_info(f"{len(all_sub_directories)} child directories")
        for child_directory in all_sub_directories:

            logger_config.print_and_log_info(f"Handling directory {child_directory}")
            library = ppn_log.ProfibusLogLibrary(
                directory_path=root_path + "\\" + child_directory,
            )

            interesting_stm_ids = [179, 184, 175, 176, 14, 177, 178]
            interesting_stm_messages = library.get_upper_layer_stms_by_stm_ids(interesting_stm_ids)

            # json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(interesting_stm_messages, f"STM {' '.join(str(interesting_stm_id) for interesting_stm_id in interesting_stm_ids)}")
            logger_config.print_and_log_info(f"interesting_stm_messages: {len(interesting_stm_messages)}")

            reports_utils.save_rows_to_output_files(
                rows_as_list_dict=[
                    OrderedDict(
                        {
                            "timestamp": interesting_stm_message.upper_layer_telegram.profibus_log_line.timestamp,
                            "Line Source": interesting_stm_message.upper_layer_telegram.profibus_log_line.source,
                            "Line Target": interesting_stm_message.upper_layer_telegram.profibus_log_line.target,
                            "Line Mode": interesting_stm_message.upper_layer_telegram.profibus_log_line.mode.name,
                            "Line length": interesting_stm_message.upper_layer_telegram.profibus_log_line.length,
                            "file path": interesting_stm_message.upper_layer_telegram.profibus_log_line.file_path,
                            "line number": interesting_stm_message.upper_layer_telegram.profibus_log_line.line_number,
                            "nid stm": interesting_stm_message.nid_stm,
                            "Number of errors": len(interesting_stm_message.creational_and_decoding_errors + interesting_stm_message.upper_layer_telegram.creational_and_decoding_errors),
                            "STM messages decoded in this line": ",".join([str(stm_message.nid_stm) for stm_message in interesting_stm_message.upper_layer_telegram.upper_layer_decoded_stms]),
                            "Safe time layer timestamp": interesting_stm_message.upper_layer_telegram.stl_time_stamp,
                            "STM message: number remaining bits to decode": interesting_stm_message.number_remaining_undecoded_bits,
                            "STM message: remaining bits to decode": interesting_stm_message.remaining_undecoded_bits,
                            "log line: number remaining bits to decode": interesting_stm_message.upper_layer_telegram.number_remaining_undecoded_bits,
                            "log line: remaining bits to decode": interesting_stm_message.upper_layer_telegram.remaining_undecoded_bits,
                            "errors": interesting_stm_message.creational_and_decoding_errors + interesting_stm_message.upper_layer_telegram.creational_and_decoding_errors,
                            **{field_name: field_value for field_name, field_value in interesting_stm_message.fields_names_and_values.items()},
                        }
                    )
                    for interesting_stm_message in interesting_stm_messages
                ],
                file_base_name=f"{child_directory} bugs_pae interesting_stm_messages {' '.join(str(interesting_stm_id) for interesting_stm_id in interesting_stm_ids)}",
                create_csv_file=False,
                create_txt_file=False,
                split_big_files=False,
            )
        pass


# Exemple d'utilisation
if __name__ == "__main__":
    main()
