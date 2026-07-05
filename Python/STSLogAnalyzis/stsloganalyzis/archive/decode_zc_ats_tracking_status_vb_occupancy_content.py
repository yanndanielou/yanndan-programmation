from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
    cast,
)

from stsloganalyzis.topology import line_topology

if TYPE_CHECKING:
    from stsloganalyzis.archive.decode_message import DecodedMessage


import csv

from stsloganalyzis.archive import decode_specific_message_content

PAS_ATS_TRACKING_STATUS_VB_OCCUPANCY_MESSAGE_ID = 173


@dataclass
class VirtualCantonZcRelation:
    cv_identifier: str
    zc_identifier: str
    num_cv_zc_starting_1: int


@dataclass
class VirtualCantonZcLibrary:
    all_cv_zc_relations: List[VirtualCantonZcRelation]
    all_known_zc_id: set[str]

    def get_by_zc_name_and_cv_number(
        self,
        zc_identifier: str,
        num_cv_zc_starting_0: int,
    ) -> Optional[VirtualCantonZcRelation]:

        assert zc_identifier in self.all_known_zc_id

        matches = [relation for relation in self.all_cv_zc_relations if relation.zc_identifier == zc_identifier and relation.num_cv_zc_starting_1 == num_cv_zc_starting_0 - 1]
        if not matches:
            return None

        assert len(matches) == 1
        return matches[0]


@dataclass
class ZcAtsTrackingStatusVbOccDecoder:
    dc_cv_pas_csv_file_full_path: str

    def __post_init__(self) -> None:

        all_cv_zc_relations: List[VirtualCantonZcRelation] = []
        all_known_zc_id: set[str] = set()

        # Read the CSV file
        with open(self.dc_cv_pas_csv_file_full_path, mode="r", encoding="utf-8") as file:
            # 'CV_ID';'PAS_ID';'NUM_CV_PAS';'FIXE_MODIFIABLE'
            # 'CV_TTEO_V1';'PAS_05';1;'FIXE'

            csv_reader = csv.DictReader(file, delimiter=";")

            # Iterate through each row in the CSV
            for csv_row in csv_reader:

                cv_identifier = cast(str, csv_row["'CV_ID'"])
                zc_identifier = cast(str, csv_row["'PAS_ID'"])
                num_cv_pas = int(csv_row["'NUM_CV_PAS'"])

                cv_zc_relation = VirtualCantonZcRelation(
                    cv_identifier=cv_identifier,
                    zc_identifier=zc_identifier,
                    num_cv_zc_starting_1=num_cv_pas,
                )
                all_cv_zc_relations.append(cv_zc_relation)
                all_known_zc_id.add(zc_identifier)

        self.cv_zc_library = VirtualCantonZcLibrary(all_cv_zc_relations, all_known_zc_id)

    def decode(self, decoded_message: "DecodedMessage", equipment_name: str) -> decode_specific_message_content.SpecificMessageContentDecoded:

        if equipment_name not in self.cv_zc_library.all_known_zc_id:
            equipment_name = equipment_name.replace(" ", "_")
        decoded_specific_message = decode_specific_message_content.SpecificMessageContentDecoded()
        all_tvd_op_data_fields_and_value = [(key, value) for (key, value) in decoded_message.decoded_fields_flat_directory.items() if key.startswith("VBOccupancy")]

        for initial_field_name, initial_field_value in all_tvd_op_data_fields_and_value:
            field_name_split = initial_field_name.split("_")
            cv_field_name_prefix = field_name_split[0]
            cv_number = int(field_name_split[1])

            cv_zc_relation = self.cv_zc_library.get_by_zc_name_and_cv_number(
                zc_identifier=equipment_name,
                num_cv_zc_starting_0=cv_number,
            )
            if cv_zc_relation:
                new_field_name = f"{cv_field_name_prefix}_{cv_number}_{cv_zc_relation.cv_identifier}"
                decoded_specific_message.fields_with_value[new_field_name] = initial_field_value

        assert decoded_specific_message
        return decoded_specific_message
