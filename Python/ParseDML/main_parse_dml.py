from logger import logger_config
from parsedml import parse_dml
import param

if __name__ == "__main__":

    with logger_config.application_logger("ParseDML"):
        dml_file_content2 = parse_dml.DmlFileContent.Builder.build_with_excel_file(dml_excel_file_full_path=param.DML_FILE_WITH_USELESS_RANGES)
