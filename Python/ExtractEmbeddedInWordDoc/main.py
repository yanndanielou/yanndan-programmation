from logger import logger_config

import zipfile
import os
import sys


def extract_embedded_files(docx_path: str, output_dir: str) -> None:
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


if __name__ == "__main__":
    """if len(sys.argv) < 2:
    print("Usage: python extract_embedded.py <docx_file> [output_dir]")
    sys.exit(1)


    docx_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted_embedded_files"
    """

    with logger_config.application_logger("extract_embedded_from_word_documnts"):

        extract_embedded_files("TCR3_DDIP_S_ed7.7_RL3F2.1-a.docx", "output")
