import os
import sys
import xml.etree.ElementTree as ET
import zipfile

from common import file_utils, file_name_utils


from logger import logger_config

OUTPUT_PARENT_DIRECTORY = "output"


def simply_unzip_embedded_files(docx_path: str, output_dir: str) -> None:
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Open the docx file as a zip archive
    with zipfile.ZipFile(docx_path, "r") as docx_zip:
        # List all files in the archive
        for file_info in docx_zip.infolist():
            # Embedded files are usually in the word/embeddings/ directory
            if file_info.filename.startswith("word/embeddings/"):
                # Extract the embedded file
                embedded_filename = os.path.basename(file_info.filename)
                output_path = os.path.join(output_dir, embedded_filename)
                with open(output_path, "wb") as f_out:
                    f_out.write(docx_zip.read(file_info.filename))
                print(f"Extracted: {embedded_filename}")


def extract_embedded_files(docx_path: str, output_dir: str) -> None:
    logger_config.print_and_log_info(f"Creating output directory: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    logger_config.print_and_log_info(f"Opening docx file: {docx_path}")
    with zipfile.ZipFile(docx_path, "r") as docx_zip:
        logger_config.print_and_log_info("Parsing word/document.xml for embedded objects...")
        try:
            document_xml = docx_zip.read("word/document.xml")
        except KeyError:
            logger_config.print_and_log_error("word/document.xml not found in docx.")
            return
        tree = ET.fromstring(document_xml)
        ns = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            "o": "urn:schemas-microsoft-com:office:office",
            "v": "urn:schemas-microsoft-com:vml",
            "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        }

        rid_to_displayname = {}
        for oleobj in tree.findall(".//w:object", ns):
            shape = oleobj.find(".//v:shape", ns)
            if shape is not None:
                alt = shape.attrib.get("{http://www.w3.org/XML/1998/namespace}alt")
                if not alt:
                    texts = shape.findall(".//w:t", ns)
                    alt = "".join([t.text for t in texts if t.text])
            else:
                alt = None
            ole = oleobj.find(".//o:OLEObject", ns)
            if ole is not None:
                rid = ole.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                if rid:
                    logger_config.print_and_log_info(f"Found OLE object: r:id={rid}, display_name={alt}")
                    rid_to_displayname[rid] = alt or f"embedded_{rid}"

        logger_config.print_and_log_info("Parsing word/_rels/document.xml.rels for relationships...")
        try:
            rels_xml = docx_zip.read("word/_rels/document.xml.rels")
        except KeyError:
            logger_config.print_and_log_error("word/_rels/document.xml.rels not found in docx.")
            return
        rels_tree = ET.fromstring(rels_xml)
        rid_to_target = {}
        for rel in rels_tree.findall("Relationship"):
            rid = rel.attrib.get("Id")
            target = rel.attrib.get("Target")
            if rid and target and target.startswith("embeddings/"):
                logger_config.print_and_log_info(f"Found relationship: r:id={rid}, target={target}")
                rid_to_target[rid] = "word/" + target.replace("\\", "/")

        logger_config.print_and_log_info(f"Extracting {len(rid_to_target)} embedded files...")
        for rid, target in rid_to_target.items():
            if target in docx_zip.namelist():
                display_name = rid_to_displayname.get(rid)
                ext = os.path.splitext(target)[1]
                if display_name:
                    safe_name = "".join(c for c in display_name if c not in '\\/:*?"<>|').strip()
                    if not safe_name.lower().endswith(ext.lower()):
                        safe_name += ext
                else:
                    safe_name = os.path.basename(target)
                output_path = os.path.join(output_dir, safe_name)
                logger_config.print_and_log_info(f"Extracting {target} as {safe_name}")
                with open(output_path, "wb") as f_out:
                    f_out.write(docx_zip.read(target))
                logger_config.print_and_log_info(f"Extracted: {safe_name}")
            else:
                logger_config.print_and_log_warning(f"Target {target} not found in docx archive.")


if __name__ == "__main__":
    with logger_config.application_logger("extract_embedded_from_word_documnts"):

        os.makedirs(OUTPUT_PARENT_DIRECTORY, exist_ok=True)

        input_files_paths = file_utils.get_files_by_directory_and_file_name_mask(directory_path="Input", filename_pattern="*.doc*") + file_utils.get_files_by_directory_and_file_name_mask(
            directory_path="Input_for_tests", filename_pattern="*.doc*"
        )
        for input_file_path in input_files_paths:
            input_file_name_without_extension = file_name_utils.get_file_name_without_extension_from_full_path(input_file_path)
            with logger_config.stopwatch_with_label(label=f"Handling input file {input_file_path}", inform_beginning=True):
                output_dir = f"{OUTPUT_PARENT_DIRECTORY}/{input_file_name_without_extension}"
                os.makedirs(output_dir, exist_ok=True)
                simply_unzip_embedded_files(input_file_path, output_dir)
                extract_embedded_files(input_file_path, output_dir)
