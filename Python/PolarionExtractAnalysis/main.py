import os

from logger import logger_config

from polarionextractanalysis import dump_to_excel, polarion_data_model, create_graphs

DEFAULT_DOWNLOAD_DIRECTORY = os.path.expandvars(r"%userprofile%\downloads")
OUTPUT_DIRECTORY_NAME = "output"
DISPLAY_OUTPUT = False


def main() -> None:

    with logger_config.application_logger():

        if not os.path.exists(OUTPUT_DIRECTORY_NAME):
            os.mkdir(OUTPUT_DIRECTORY_NAME)

        users_input_json_file_path = DEFAULT_DOWNLOAD_DIRECTORY + "/" + "Extraction_POLARION_User.json"
        work_items_input_json_file_path = DEFAULT_DOWNLOAD_DIRECTORY + "/" + "Extraction_POLARION_Full.json"

        polarion_library = polarion_data_model.PolarionLibrary(users_input_json_file_path=users_input_json_file_path, work_items_input_json_file_path=work_items_input_json_file_path)

        create_graphs.create_baregraph_work_item_per_user(output_directory_path=OUTPUT_DIRECTORY_NAME, users_library=polarion_library.users_library)
        create_graphs.create_baregraph_work_item_number_by_status_by_type(output_directory_path=OUTPUT_DIRECTORY_NAME, polarion_library=polarion_library)
        create_graphs.create_baregraph_work_item_number_cumulative_by_status(output_directory_path=OUTPUT_DIRECTORY_NAME, polarion_library=polarion_library)
        create_graphs.create_baregraph_work_item_number_by_company(output_directory_path=OUTPUT_DIRECTORY_NAME, polarion_library=polarion_library)
        create_graphs.create_baregraph_work_item_number_by_company_per_type(output_directory_path=OUTPUT_DIRECTORY_NAME, polarion_library=polarion_library)
        create_graphs.create_baregraph_work_item_number_by_company_stacked_by_status_per_type(output_directory_path=OUTPUT_DIRECTORY_NAME, polarion_library=polarion_library)
        create_graphs.create_baregraph_work_item_number_by_company_stacked_by_status(output_directory_path=OUTPUT_DIRECTORY_NAME, polarion_library=polarion_library)

        dump_to_excel.dump_companies_to_excel_file(users_library=polarion_library.users_library, output_directory_path=OUTPUT_DIRECTORY_NAME)
        dump_to_excel.dump_users_to_excel_file(users_library=polarion_library.users_library, output_directory_path=OUTPUT_DIRECTORY_NAME)
        dump_to_excel.dump_projects_to_excel_file(project_library=polarion_library.project_library, output_directory_path=OUTPUT_DIRECTORY_NAME)
        dump_to_excel.dump_work_items_to_excel_file(work_items_library=polarion_library.work_item_library, output_directory_path=OUTPUT_DIRECTORY_NAME)


if __name__ == "__main__":
    main()
