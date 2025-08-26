import os
import sys
import xml.etree.ElementTree as ET
import zipfile

from logger import logger_config


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
    os.makedirs(output_dir, exist_ok=True)
    with zipfile.ZipFile(docx_path, "r") as docx_zip:
        # 1. Parse document.xml to find embedded object display names and r:id
        document_xml = docx_zip.read("word/document.xml")
        tree = ET.fromstring(document_xml)
        ns = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            "o": "urn:schemas-microsoft-com:office:office",
            "v": "urn:schemas-microsoft-com:vml",
            "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        }

        # Map r:id to display name (as shown in Word)
        rid_to_displayname = {}
        for oleobj in tree.findall(".//w:object", ns):
            # Find the shape containing the display name
            shape = oleobj.find(".//v:shape", ns)
            if shape is not None:
                alt = shape.attrib.get("{http://www.w3.org/XML/1998/namespace}alt")
                if not alt:
                    # Sometimes the display name is in v:textbox/v:txbxContent/w:p/w:r/w:t
                    texts = shape.findall(".//w:t", ns)
                    alt = "".join([t.text for t in texts if t.text])
            else:
                alt = None
            # Find the OLE object (o:OLEObject) with r:id
            ole = oleobj.find(".//o:OLEObject", ns)
            if ole is not None:
                rid = ole.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                if rid:
                    rid_to_displayname[rid] = alt or f"embedded_{rid}"

        # 2. Parse document.xml.rels to map r:id to target (embedded file)
        rels_xml = docx_zip.read("word/_rels/document.xml.rels")
        rels_tree = ET.fromstring(rels_xml)
        rid_to_target = {}
        for rel in rels_tree.findall("Relationship"):
            rid = rel.attrib.get("Id")
            target = rel.attrib.get("Target")
            if rid and target and target.startswith("embeddings/"):
                rid_to_target[rid] = "word/" + target.replace("\\", "/")

        # 3. Extract embedded files with display names
        for rid, target in rid_to_target.items():
            if target in docx_zip.namelist():
                display_name = rid_to_displayname.get(rid)
                # Try to get extension from the embedded file name
                ext = os.path.splitext(target)[1]
                if display_name:
                    # Clean display name for filesystem
                    safe_name = "".join(c for c in display_name if c not in '\\/:*?"<>|').strip()
                    if not safe_name.lower().endswith(ext.lower()):
                        safe_name += ext
                else:
                    safe_name = os.path.basename(target)
                output_path = os.path.join(output_dir, safe_name)
                with open(output_path, "wb") as f_out:
                    f_out.write(docx_zip.read(target))
                print(f"Extracted: {safe_name}")


if __name__ == "__main__":
    """if len(sys.argv) < 2:
    print("Usage: python extract_embedded.py <docx_file> [output_dir]")
    sys.exit(1)


    docx_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted_embedded_files"
    """

    with logger_config.application_logger("extract_embedded_from_word_documnts"):

        extract_embedded_files("TCR3_DDIP_S_ed7.7_RL3F2.1-a.docx", "output")
