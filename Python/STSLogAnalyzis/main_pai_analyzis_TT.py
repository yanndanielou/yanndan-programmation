import matplotlib.pyplot as plt
from common import file_utils
from logger import logger_config

from stsloganalyzis import decode_pai_logs

OUTPUT_FOLDER_NAME = "output"

with logger_config.application_logger():
    file_utils.create_folder_if_not_exist(OUTPUT_FOLDER_NAME)

    for library_name, folder_path in [
        ("2027-01-27 P75 light_", r"D:\temp\2027-01-27 avec hitachi\2027-01-27\PAI75\TT-026401 (TT)\Archives_maint_light"),
        ("2027-01-27 P81 TT-026396", r"D:\temp\2027-01-27 avec hitachi\2027-01-27\PAI81\TT-026396\Archives_maint"),
        ("2027-01-27 P75 TT-026396", r"D:\temp\2027-01-27 avec hitachi\2027-01-27\PAI75\TT-026401 (TT)\Archives_maint"),
    ]:
        tt_maint_library = decode_pai_logs.TerminalTechniqueArchivesMaintLibrary(library_name).load_folder(folder_path)

        tt_maint_library.dump_all_events_to_text_file(output_folder_path=OUTPUT_FOLDER_NAME)
        tt_maint_library.export_back_to_past_with_context_to_excel(output_folder_path=OUTPUT_FOLDER_NAME)
        tt_maint_library.export_mesd_alarms_groups_to_excel(output_folder_path=OUTPUT_FOLDER_NAME)
        tt_maint_library.export_sahara_alarms_with_context_to_excel(output_folder_path=OUTPUT_FOLDER_NAME)
        tt_maint_library.export_equipments_with_alarms_to_excel(output_folder_path=OUTPUT_FOLDER_NAME, equipment_names_to_ignore=["81"])
        tt_maint_library.plot_back_to_past_by_period(output_folder_path=OUTPUT_FOLDER_NAME, interval_minutes=60, do_show=False)
        tt_maint_library.plot_sahara_alarms_by_period(output_folder_path=OUTPUT_FOLDER_NAME, interval_minutes=60, do_show=False)
        tt_maint_library.plot_sahara_mccs_back_to_past_by_period(output_folder_path=OUTPUT_FOLDER_NAME, interval_minutes=60, do_show=False)
        tt_maint_library.plot_alarms_by_period(
            output_folder_path=OUTPUT_FOLDER_NAME, equipment_names_to_ignore=["81", "75"], interval_minutes=60, do_show=False
        )  # Optionnel: affiche le graphique matplotlib

    pass
    # plt.show()

pass
