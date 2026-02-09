from dataclasses import dataclass
from polarionextractanalysis.constants import PolarionWorkItemType, PolarionAttributeType, PolarionSeverity
from datetime import datetime


class PolarionLibrary:
    def __init__(self) -> None:
        pass


@dataclass
class PolarionAttributes:
    type: PolarionAttributeType
    identifier: str
    title: str
    severity = PolarionSeverity
    created_timestamp: datetime
    updated_timestamp: datetime


@dataclass
class PolarionWorkItem:
    type: PolarionWorkItemType
    identifier: str
    attributes: PolarionAttributes
