from stsloganalyzis import decode_cck
import fnmatch
import os
import shutil
import tempfile
import time
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from typing import List, Tuple, cast

from logger import logger_config

from common import file_name_utils


cck_files: List[decode_cck.CckMproTraceFile] = []
with logger_config.stopwatch_with_label(f"Load MPRO traces"):
    for dirpath, dirnames, filenames in os.walk(r"D:\temp\2027-01-27 avec hitachi\2027-01-27\SIG3\Traces\Traces_MPRO1_1_20260127_15"):
        for file_name in filenames:
            cck_files.append(decode_cck.CckMproTraceFile(parent_folder_full_path=dirpath, file_name=file_name))


pass
