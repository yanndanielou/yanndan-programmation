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
            "log_cab1_PPN_A NEXT-16708 2026-03-29 2236",
            "ppn_cab2_log.tar",
        ]  # + os.listdir(root_path)

        logger_config.print_and_log_info(f"{len(all_sub_directories)} child directories")
        for child_directory in all_sub_directories:

            logger_config.print_and_log_info(f"Handling directory {child_directory}")
            library = ppn_log.ProfibusLogLibrary(
                directory_path=root_path + "\\" + child_directory,
                label=child_directory,
            )

            library.save_upper_layer_stms_by_stm_ids([179, 184, 175, 176, 14, 177, 178])
            library.save_upper_layer_stms_by_stm_ids([15, 14])
            library.save_selected_stm_messages(library.all_upper_layer_stms, file_base_name=f"{library.label} all")
            library.save_selected_stm_messages_for_each_interlocutor()

        pass


# Exemple d'utilisation
if __name__ == "__main__":
    main()
