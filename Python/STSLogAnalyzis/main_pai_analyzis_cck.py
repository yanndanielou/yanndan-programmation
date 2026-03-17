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

    for library_name, folder_path in [
        ("2026-02-03 CTI Upgrade FW CTI", r"D:\temp\2026-03-02 cck\2026-02-03 cck"),
        # ("ITC SaDi 2026-01-31", r"D:\temp\2026-02-01 dimanche matin Stan\26-02-01 - logs SIG3 chute P81 et P75\Traces_MROU_1_20260201_1"),
        # ("2027-01-27 avec hitachi", r"D:\temp\2027-01-27 avec hitachi\2027-01-27\SIG3\Traces\Traces_MPRO1_1_20260127_15"),
    ]:

        cck_libary = decode_cck.CckMproTraceLibrary(name=library_name).load_folder(folder_path)
        # cck_libary = decode_cck.CckMproTraceLibrary(name="Nuit 20260125 CCU").load_folder(r"C:\Users\fr232487\Downloads\Traces_MPRO1_1_20260125_15_site_ccu")
        cck_libary.dump_temporary_loss_link_to_excel(
            output_folder_path=OUTPUT_FOLDER_NAME,
        )
        cck_libary.export_temporary_loss_link_to_excel(
            output_folder_path=OUTPUT_FOLDER_NAME,
        )
        cck_libary.plot_problems_and_loss_link_by_period(output_folder_path=OUTPUT_FOLDER_NAME, interval_minutes=2, do_show=False)

        for interval_minutes in [2, 10, 15, 30, 60]:
            cck_libary.plot_loss_link_by_period(output_folder_path=OUTPUT_FOLDER_NAME, interval_minutes=interval_minutes, do_show=False)
            cck_libary.plot_loss_link_by_period(output_folder_path=OUTPUT_FOLDER_NAME, interval_minutes=interval_minutes, do_show=False, maximum_link_loss_duration_to_consider_in_seconds=5)

        enchainement_protocolaire_lines = [line for line in cck_libary.all_processed_lines if line.problem_enchainement_numero_protocolaire]
        logger_config.print_and_log_info(f"{len(enchainement_protocolaire_lines)} problèmes de enchainement numero protocolaire")
        # decode_cck.save_cck_mpro_lines_in_excel(
        #    library_name=library_name,
        #    trace_lines=enchainement_protocolaire_lines,
        #    output_folder_path=OUTPUT_FOLDER_NAME,
        #    excel_output_file_name_without_extension="Problèmes enchainement numéro protocolaire",
        # )
        # pertes_liaisons = [line for line in cck_libary.all_processed_lines if line.changement_etat_liaison and line.changement_etat_liaison.new_state == decode_cck.EtatLiaisonMpro.KO]
        # pertes_liaisons_courtes = [line for line in cck_libary.all_processed_lines if line.changement_etat_liaison and line.changement_etat_liaison.new_state == decode_cck.EtatLiaisonMpro.KO]
        # for interval_minutes in [2, 10, 30]:
        #    decode_cck.plot_bar_graph_list_cck_mpro_lines_by_period(
        #        library_name=library_name, trace_lines=pertes_liaisons, output_folder_path=OUTPUT_FOLDER_NAME, label="pertes_liaisons", interval_minutes=interval_minutes
        #    )

        pass
    plt.show()

pass
