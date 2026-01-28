import fnmatch
import os
import shutil
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime
from typing import List, Tuple, cast

import matplotlib.pyplot as plt
from common import file_name_utils, file_utils
from logger import logger_config

from stsloganalyzis import decode_cck, decode_pai_logs

OUTPUT_FOLDER_NAME = "output"

with logger_config.application_logger("main_pai_analyzis_TT test"):
    file_utils.create_folder_if_not_exist(OUTPUT_FOLDER_NAME)

    tt_maint_p81_library = decode_pai_logs.TerminalTechniqueArchivesMaintLibrary("Test").load_folder(r"D:\temp\test")
    for tt_maint_library in [tt_maint_p81_library]:
        tt_maint_library.export_equipments_with_alarms_to_excel(output_folder_path=OUTPUT_FOLDER_NAME, excel_output_file_name_without_extension="Alarms", equipment_names_to_ignore=["81"])
        tt_maint_library.plot_back_to_past_by_period(output_folder_path=OUTPUT_FOLDER_NAME, interval_minutes=60, do_show=False)
        tt_maint_library.plot_sahara_alarms_by_period(output_folder_path=OUTPUT_FOLDER_NAME, interval_minutes=60, do_show=False)
        tt_maint_library.plot_sahara_mccs_back_to_past_by_period(output_folder_path=OUTPUT_FOLDER_NAME, interval_minutes=60, do_show=False)
        tt_maint_library.plot_alarms_by_period(
            output_folder_path=OUTPUT_FOLDER_NAME, equipment_names_to_ignore=["81", "75"], interval_minutes=60, do_show=True
        )  # Optionnel: affiche le graphique matplotlib

    pass
    plt.show()

pass
