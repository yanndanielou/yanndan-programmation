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

with logger_config.application_logger("main_pai_analyzis"):
    file_utils.create_folder_if_not_exist(OUTPUT_FOLDER_NAME)

    tt_maint_library = decode_pai_logs.TerminalTechniqueArchivesMaintLibrary("2027-01-27 P81 TT-026396").load_folder(r"D:\temp\2027-01-27 avec hitachi\2027-01-27\PAI81\TT-026396\Archives_maint")
    tt_maint_library.export_equipments_with_alarms_to_excel(output_folder_path=OUTPUT_FOLDER_NAME, excel_output_file_name_without_extension="Alarms", equipment_names_to_ignore=["81"])

    cck_libary = decode_cck.CckMproTraceLibrary(name="2027-01-27 avec hitachi").load_folder(r"D:\temp\2027-01-27 avec hitachi\2027-01-27\SIG3\Traces\Traces_MPRO1_1_20260127_15")
    # cck_libary = decode_cck.CckMproTraceLibrary(name="Nuit 20260125 CCU").load_folder(r"C:\Users\fr232487\Downloads\Traces_MPRO1_1_20260125_15_site_ccu")
    cck_libary.export_temporary_loss_link_to_excel(
        output_folder_path=OUTPUT_FOLDER_NAME, excel_output_file_name_without_extension="temporary_loss_link" + file_name_utils.get_file_suffix_with_current_datetime()
    )
    cck_libary.plot_problems_and_loss_link_by_period(output_folder_path=OUTPUT_FOLDER_NAME, interval_minutes=2, do_show=False)

    enchainement_protocolaire_lines = [line for line in cck_libary.all_processed_lines if line.problem_enchainement_numero_protocolaire]
    logger_config.print_and_log_info(f"{len(enchainement_protocolaire_lines)} problèmes de enchainement numero protocolaire")
    decode_cck.save_cck_mpro_lines_in_excel(
        trace_lines=enchainement_protocolaire_lines, output_folder_path=OUTPUT_FOLDER_NAME, excel_output_file_name_without_extension="Problèmes enchainement numéro protocolaire"
    )
    decode_cck.plot_bar_graph_list_cck_mpro_lines_by_period(
        trace_lines=enchainement_protocolaire_lines, output_folder_path=OUTPUT_FOLDER_NAME, label="enchainement_protocolaire_lines", interval_minutes=2
    )

    pass
    plt.show()

pass
