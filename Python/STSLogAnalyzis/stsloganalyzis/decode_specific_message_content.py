import csv
import datetime
import os
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Dict, List, Optional, cast

from logger import logger_config

from stsloganalyzis import decode_action_set_content


@dataclass
class SpecificMessageContentDecoded:

    def __init__(self) -> None:
        # self.fields_with_value: Dict[str, bool | int | str | float] = dict()
        self.fields_with_value: Dict[str, float | int | bool | str | List[int] | List[str] | List[bool]] = dict()
