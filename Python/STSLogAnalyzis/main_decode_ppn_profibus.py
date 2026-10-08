# import os

from logger import logger_config

from stsloganalyzis.ppn import ppn_profibus_log
from stsloganalyzis.unisig.s5758 import decode_unisig_s57_s58


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
            library = ppn_profibus_log.ProfibusLogLibrary(
                directory_path=root_path + "\\" + child_directory,
                label=child_directory,
            )

            library.save_sdn_safe_time_layer_startup_messages()
            library.save_sdn_sync_and_reference_time_messages()
            library.save_all_stm_messages_with_errors()

            library.save_upper_layer_stms_by_stm_ids([161])
            library.save_upper_layer_stms_by_stm_ids([178])

            library.save_selected_unisig_messages(
                file_base_name=f"{library.label} SDA messages with timestamp",
                selected_unisig_messages=[
                    unisig_message
                    for unisig_message in library.all_unisig_messages
                    if isinstance(unisig_message, decode_unisig_s57_s58.OnboardSdaUnisigMessage) and unisig_message.stl_time_stamp is not None
                ],
            )

            library.save_upper_layer_stms_by_stm_ids([179, 184, 175, 176, 14, 177, 178])
            library.save_upper_layer_stms_by_stm_ids([15, 14])
            library.save_upper_layer_stms_by_stm_ids([161, 177])
            library.save_all_stm_messages()
            library.save_all_unisig_messages()
            library.save_stm_messages_for_each_interlocutor()


# Exemple d'utilisation
if __name__ == "__main__":
    main()
