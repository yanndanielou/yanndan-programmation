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

with logger_config.application_logger():
    file_utils.create_folder_if_not_exist(OUTPUT_FOLDER_NAME)

    tt_maint_p75_light_library = decode_pai_logs.TerminalTechniqueArchivesMaintLibrary("2027-01-27 P75 light_").load_folder(
        r"D:\temp\2027-01-27 avec hitachi\2027-01-27\PAI75\TT-026401 (TT)\Archives_maint_light"
    )

    for tt_maint_library in [tt_maint_p75_light_library]:
        tt_maint_library.dump_all_events_to_text_file(output_folder_path=OUTPUT_FOLDER_NAME)
        tt_maint_library.export_back_to_past_with_context_to_excel(output_folder_path=OUTPUT_FOLDER_NAME)
        tt_maint_library.export_mesd_alarms_groups_with_context_to_excel(output_folder_path=OUTPUT_FOLDER_NAME)
        tt_maint_library.export_sahara_alarms_with_context_to_excel(output_folder_path=OUTPUT_FOLDER_NAME)
        tt_maint_library.export_equipments_with_alarms_to_excel(output_folder_path=OUTPUT_FOLDER_NAME, equipment_names_to_ignore=["81"])
        tt_maint_library.plot_back_to_past_by_period(output_folder_path=OUTPUT_FOLDER_NAME, interval_minutes=60, do_show=False)
        tt_maint_library.plot_sahara_alarms_by_period(output_folder_path=OUTPUT_FOLDER_NAME, interval_minutes=60, do_show=False)
        tt_maint_library.plot_sahara_mccs_back_to_past_by_period(output_folder_path=OUTPUT_FOLDER_NAME, interval_minutes=60, do_show=False)
        tt_maint_library.plot_alarms_by_period(output_folder_path=OUTPUT_FOLDER_NAME, equipment_names_to_ignore=["81", "75"], interval_minutes=60, do_show=False)
    pass
    # plt.show()

pass
