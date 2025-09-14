from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, cast

from common import excel_utils
from logger import logger_config


@dataclass
class Equipment:
    eqpt_type: str
    relative_name: str
    unique_name: str
    train_single_unit: Optional["TrainSingleUnit"] = None


@dataclass
class TrainSingleUnit:
    cc_id: int
    emu_id: int
    equipments: List[Equipment]
