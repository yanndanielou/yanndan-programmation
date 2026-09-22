from itertools import chain

from collections import OrderedDict

from common import json_encoders, reports_utils
from logger import logger_config

from stsloganalyzis.ppn import ppn_log
from stsloganalyzis.unisig import decode_unisig


def main() -> None:

    with logger_config.application_logger():
        library = ppn_log.ProfibusLogLibrary(
            directory_path=r"D:\temp\2026-09-20 logs PPN we mars 26\ppn_cab1_log.tar",
        )
        decode_unisig.SdaErrorsFound().log_stats()

        interesting_stm_ids = [179, 184, 175, 176]
        interesting_stm_messages = library.get_upper_layer_stms_by_stm_ids(interesting_stm_ids)

        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(interesting_stm_messages, f"STM {' '.join(str(interesting_stm_id) for interesting_stm_id in interesting_stm_ids)}")
        logger_config.print_and_log_info(f"interesting_stm_messages: {len(interesting_stm_messages)}")

        def build_row(interesting_stm_message):
            row = OrderedDict(
                {
                    "timestamp": interesting_stm_message.upper_layer_telegram.timestamp,
                    "nid_stm": interesting_stm_message.nid_stm,
                }
            )
            row.update({field_name: field_value for field_name, field_value in interesting_stm_message})
            return row

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[build_row(interesting_stm_message) for interesting_stm_message in interesting_stm_messages],
            file_base_name=f"interesting_stm_messages: {len(interesting_stm_messages)}",
        )
        pass


# Exemple d'utilisation
if __name__ == "__main__":
    main()
