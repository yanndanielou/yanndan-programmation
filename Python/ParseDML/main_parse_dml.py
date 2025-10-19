from logger import logger_config
from parsedml import parse_dml
from common import json_encoders
import param


def dump_errors(dml_file_content_built: parse_dml.DmlFileContent) -> None:
    row_errors = dml_file_content_built.could_not_be_parsed_because_error_rows
    with open("logs/errors.txt", mode="w", encoding="utf-8") as error_file:
        error_file.write("\n".join([str(row_error) for row_error in row_errors]))


if __name__ == "__main__":

    with logger_config.application_logger("ParseDML"):
        dml_file_content_built = parse_dml.DmlFileContent.Builder.build_with_excel_file(dml_excel_file_full_path=param.DML_FILE_CLEANED_FINAL)
        all_documents_that_have_several_titles = [document for document in dml_file_content_built.dml_documents if len(document.get_all_titles()) > 2]
        pass
