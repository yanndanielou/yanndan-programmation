import csv
from dataclasses import dataclass
from enum import IntEnum, auto
from typing import (
    List,
    Optional,
    Self,
    cast,
)


class VbOccupancyState(IntEnum):
    CV_LIBRE = 0
    CV_TE_MOINS = 1
    CV_TE_PLUS = 2
    CV_TE_ARRIERE = 3
    CV_TNI = 4
    UNUSED_5 = auto()
    UNUSED_6 = auto()
    UNUSED_7 = auto()


@dataclass
class VirtualCantonZcRelation:
    cv_identifier: str
    zc_identifier: str
    num_cv_zc_starting_1: int


@dataclass
class VirtualCantonZcLibrary:
    all_cv_zc_relations: List[VirtualCantonZcRelation]
    all_known_zc_id: set[str]

    dc_cv_pas_csv_file_full_path: str

    @classmethod
    def from_csv_file(cls, dc_cv_pas_csv_file_full_path: str) -> Self:

        all_cv_zc_relations: List[VirtualCantonZcRelation] = []
        all_known_zc_id: set[str] = set()

        # Read the CSV file
        with open(dc_cv_pas_csv_file_full_path, mode="r", encoding="utf-8") as file:
            # 'CV_ID';'PAS_ID';'NUM_CV_PAS';'FIXE_MODIFIABLE'
            # 'CV_TTEO_V1';'PAS_05';1;'FIXE'

            csv_reader = csv.DictReader(file, delimiter=";")

            # Iterate through each row in the CSV
            for csv_row in csv_reader:

                cv_identifier = cast(str, csv_row["'CV_ID'"]).replace("'", "")
                zc_identifier = cast(str, csv_row["'PAS_ID'"]).replace("'", "")
                num_cv_pas = int(csv_row["'NUM_CV_PAS'"])

                cv_zc_relation = VirtualCantonZcRelation(
                    cv_identifier=cv_identifier,
                    zc_identifier=zc_identifier,
                    num_cv_zc_starting_1=num_cv_pas,
                )
                all_cv_zc_relations.append(cv_zc_relation)
                all_known_zc_id.add(zc_identifier)

        return cls(all_cv_zc_relations, all_known_zc_id, dc_cv_pas_csv_file_full_path)

    def get_by_zc_name_and_cv_number(
        self,
        zc_identifier: str,
        num_cv_zc_starting_1: int,
    ) -> Optional[VirtualCantonZcRelation]:

        if zc_identifier not in self.all_known_zc_id:
            zc_identifier = zc_identifier.replace(" ", "_")

        assert zc_identifier in self.all_known_zc_id

        matches = [relation for relation in self.all_cv_zc_relations if relation.zc_identifier == zc_identifier and relation.num_cv_zc_starting_1 == num_cv_zc_starting_1]
        if not matches:
            return None

        assert len(matches) == 1
        return matches[0]
