# Standard

import inspect
from dataclasses import dataclass
from typing import Optional

# Other libraries
from common import download_utils, excel_utils, file_utils
from logger import logger_config
from rhapsody import rhapsody_utils

if __name__ == "__main__":

    with logger_config.application_logger("download_input_files"):

        input_download_folder = "Input_Downloaded"
        file_utils.create_folder_if_not_exist(input_download_folder)
        file_downloaded: Optional[str] = rhapsody_utils.download_files_from_rhapsody(
            [
                rhapsody_utils.DownloadFileInstruction(
                    file_to_download_url="https://rhapsody.siemens.net/livelink/livelink.exe?func=ll&objId=90870046&objAction=Download",
                    file_to_download_pattern="NExTEO-S-273000-02-0125-01 Dossier de Configuration Réseau STD Radio - V01-00 Annexe A*.xlsx",
                    file_move_after_download_action=download_utils.DownloadFileDetector.FileMoveAfterDownloadAction(
                        final_path="Input_Downloaded/NExTEO-S-273000-02-0125-01 Dossier de Configuration Réseau STD Radio - V01-00 Annexe A.xlsx",
                        retry_in_case_of_error=download_utils.DownloadFileDetector.RetryInCaseOfErrorAction(),
                    ),
                ),
                rhapsody_utils.DownloadFileInstruction(
                    file_to_download_url="https://rhapsody.siemens.net/livelink/livelink.exe?func=ll&objId=91311347&objAction=Download",
                    file_to_download_pattern="NExTEO-S-271000-02-0125-02 Dossier de Configuration Réseau Sol - V10-00 Annexe A*.xlsb",
                    file_move_after_download_action=download_utils.DownloadFileDetector.FileMoveAfterDownloadAction(
                        final_path="Input_Downloaded/NExTEO-S-271000-02-0125-02 Dossier de Configuration Réseau Sol - V10-00 Annexe A.xlsb",
                        retry_in_case_of_error=download_utils.DownloadFileDetector.RetryInCaseOfErrorAction(),
                    ),
                ),
            ]
        )
