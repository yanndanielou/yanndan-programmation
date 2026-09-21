from common import file_utils
from logger import logger_config

from stsloganalyzis.ppn import ppn_log
from stsloganalyzis.unisig import decode_unisig


def main() -> None:

    with logger_config.application_logger():
        all_ppn_logs_paths = file_utils.get_files_by_directory_and_file_name_mask(
            directory_path=r"D:\temp\2026-09-20 logs PPN we mars 26\ppn_cab1_log.tar",
            # directory_path=r"D:\temp\2026-09-20 logs PPN we mars 26",
            file_sort_order=file_utils.FileSortOrder.TIMESTAMP_OLDER_TO_NEWER,
            filename_pattern="profibus*",
            # filename_pattern="*.txt",
        )

        for ppn_log_path in all_ppn_logs_paths:

            decoded_file = ppn_log.ProfibusLogFile(
                file_full_path=ppn_log_path,
            )
            decoded_file.process()

            logger_config.print_and_log_info(f"Decode {len(decoded_file.decoded_lines)} lines of {ppn_log_path}")
            for line_number, decoded_line in enumerate(decoded_file.decoded_lines):
                decoded_line.decode_sdn_or_sna()

        pass
        decode_unisig.SdaErrorsFound().log_stats()


# Exemple d'utilisation
if __name__ == "__main__":
    main()
