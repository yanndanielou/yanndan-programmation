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

from stsloganalyzis import decode_cck

OUTPUT_FOLDER_NAME = "output"

with logger_config.application_logger("main_pai_analyzis"):
    file_utils.create_folder_if_not_exist(OUTPUT_FOLDER_NAME)

    # cck_libary = decode_cck.CckMproTraceLibrary().load_folder(r"D:\temp\2027-01-27 avec hitachi\2027-01-27\SIG3\Traces\Traces_MPRO1_1_20260127_15 - Copie")
    cck_libary = decode_cck.CckMproTraceLibrary().load_folder(r"C:\Users\fr232487\Downloads\Traces_MPRO1_1_20260125_15_site_ccu")
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
