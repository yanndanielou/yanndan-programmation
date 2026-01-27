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

with logger_config.application_logger("main_pai_analyzis"):
    cck_libary = decode_cck.CckMproTraceLibrary().load_folder(r"D:\temp\2027-01-27 avec hitachi\2027-01-27\SIG3\Traces\Traces_MPRO1_1_20260127_15")

    enchainement_protocolaire_lines = [line for line in cck_libary.all_processed_lines if "le msg a un problème de 'enchainement numero protocolaire'" in line.full_raw_line]
    pass

pass
