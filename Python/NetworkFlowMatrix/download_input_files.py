# Standard

from typing import Optional

# Other libraries
from common import download_utils, file_utils
from logger import logger_config
from rhapsody import rhapsody_utils

from networkflowmatrix import network_conf_files_descriptions_data


def get_download_instruction(conf_file_description: network_conf_files_descriptions_data.ExcelInputFileDescription) -> rhapsody_utils.DownloadFileInstruction:
    download_instruction = rhapsody_utils.DownloadFileInstruction(
        file_to_download_url=conf_file_description.rhapsody_download_link,
        file_to_download_pattern=conf_file_description.file_name_mask_downloaded,
        file_move_after_download_action=download_utils.DownloadFileDetector.FileMoveAfterDownloadAction(
            final_path=conf_file_description.excel_file_full_path,
            retry_in_case_of_error=download_utils.DownloadFileDetector.RetryInCaseOfErrorAction(),
        ),
    )

    return download_instruction


if __name__ == "__main__":

    with logger_config.application_logger("download_input_files"):

        file_utils.create_folder_if_not_exist(network_conf_files_descriptions_data.INPUT_DOWNLOAD_FOLDER)

        std_radio_network_conf = network_conf_files_descriptions_data.StdRadioNetworkConfV2Description()

        download_instructions = [
            get_download_instruction(std_radio_network_conf),
            get_download_instruction(network_conf_files_descriptions_data.SolStdNetworkConfV10Description()),
            get_download_instruction(network_conf_files_descriptions_data.BordAddressPlanV9Description()),
        ]
        file_downloaded: Optional[str] = rhapsody_utils.download_files_from_rhapsody(download_instructions)
        pass


if __name__ == "__main_old__":

    with logger_config.application_logger("download_input_files"):

        input_download_folder = "Input_Downloaded"
        file_utils.create_folder_if_not_exist(input_download_folder)
        file_downloaded: Optional[str] = rhapsody_utils.download_files_from_rhapsody(
            [
                rhapsody_utils.DownloadFileInstruction(
                    file_to_download_url="https://rhapsody.siemens.net/livelink/livelink.exe?func=ll&objId=90870046&objAction=Download",
                    file_to_download_pattern="NExTEO-S-273000-02-0125-01 Dossier de Configuration Réseau STD Radio - V01-00 Annexe A*.xlsx",
                    file_move_after_download_action=download_utils.DownloadFileDetector.FileMoveAfterDownloadAction(
                        final_path=f"{input_download_folder}/NExTEO-S-273000-02-0125-01 Dossier de Configuration Réseau STD Radio - V01-00 Annexe A.xlsx",
                        retry_in_case_of_error=download_utils.DownloadFileDetector.RetryInCaseOfErrorAction(),
                    ),
                ),
                rhapsody_utils.DownloadFileInstruction(
                    file_to_download_url="https://rhapsody.siemens.net/livelink/livelink.exe?func=ll&objId=91311347&objAction=Download",
                    file_to_download_pattern="NExTEO-S-271000-02-0125-02 Dossier de Configuration Réseau Sol - V10-00 Annexe A*.xlsb",
                    file_move_after_download_action=download_utils.DownloadFileDetector.FileMoveAfterDownloadAction(
                        final_path=f"{input_download_folder}/NExTEO-S-271000-02-0125-02 Dossier de Configuration Réseau Sol - V10-00 Annexe A.xlsb",
                        retry_in_case_of_error=download_utils.DownloadFileDetector.RetryInCaseOfErrorAction(),
                    ),
                ),
                rhapsody_utils.DownloadFileInstruction(
                    file_to_download_url="https://rhapsody.siemens.net/livelink/livelink.exe?func=ll&objId=91211232&objAction=Download",
                    file_to_download_pattern="NExTEO-B-272000-02-0125-00 Plan d adressage NExTEO Bord V09-00*.xlsm",
                    file_move_after_download_action=download_utils.DownloadFileDetector.FileMoveAfterDownloadAction(
                        final_path=f"{input_download_folder}/NExTEO-B-272000-02-0125-00 Plan d adressage NExTEO Bord V09-00.xlsm",
                        retry_in_case_of_error=download_utils.DownloadFileDetector.RetryInCaseOfErrorAction(),
                    ),
                ),
            ]
        )
