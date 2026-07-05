from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
    cast,
)

if TYPE_CHECKING:
    from stsloganalyzis.archive.decode_message import DecodedMessage


import csv

from stsloganalyzis.archive import decode_specific_message_content

PAS_ATS_TM_AO_SIG_MESSAGE_ID = 205


@dataclass
class TvdZcRelation:
    tvd_identifier: str
    zc_identifier: str
    num_tvd_zc_starting_1: int


@dataclass
class TvdZcLibrary:
    all_tvd_zc_relations: List[TvdZcRelation]
    all_known_zc_id: set[str]

    def get_by_zc_name_and_tvd_number(
        self,
        zc_identifier: str,
        num_tvd_zc_starting_0: int,
    ) -> Optional[TvdZcRelation]:

        assert zc_identifier in self.all_known_zc_id

        matches = [relation for relation in self.all_tvd_zc_relations if relation.zc_identifier == zc_identifier and relation.num_tvd_zc_starting_1 == num_tvd_zc_starting_0 - 1]
        if not matches:
            return None

        assert len(matches) == 1
        return matches[0]


@dataclass
class ZcAtsTmAoSigDecoder:
    ats_inv_tvd_pas_csv_file_full_path: str

    def __post_init__(self) -> None:

        all_tvd_zc_relations: List[TvdZcRelation] = []
        all_known_zc_id: set[str] = set()

        # Read the CSV file
        with open(self.ats_inv_tvd_pas_csv_file_full_path, mode="r", encoding="utf-8") as file:
            # TVD_ID;PAS_ID;NUM_TVD_PAS
            # TVD_z2410;PAS_05;12

            csv_reader = csv.DictReader(file, delimiter=";")

            # Iterate through each row in the CSV
            for csv_row in csv_reader:

                tvd_identifier = cast(str, csv_row["TVD_ID"])
                zc_identifier = cast(str, csv_row["PAS_ID"])
                num_tvd_pas = int(csv_row["NUM_TVD_PAS"])

                tvd_zc_relation = TvdZcRelation(
                    tvd_identifier=tvd_identifier,
                    zc_identifier=zc_identifier,
                    num_tvd_zc_starting_1=num_tvd_pas,
                )
                all_tvd_zc_relations.append(tvd_zc_relation)
                all_known_zc_id.add(zc_identifier)

        self.tvd_zc_library = TvdZcLibrary(all_tvd_zc_relations, all_known_zc_id)

    def decode(self, decoded_message: "DecodedMessage", equipment_name: str) -> decode_specific_message_content.SpecificMessageContentDecoded:

        if equipment_name not in self.tvd_zc_library.all_known_zc_id:
            equipment_name = equipment_name.replace(" ", "_")

        decoded_specific_message = decode_specific_message_content.SpecificMessageContentDecoded()
        all_tvd_op_data_fields_and_value = [(key, value) for (key, value) in decoded_message.decoded_fields_flat_directory.items() if key.startswith("TvdOpData")]

        for initial_field_name, initial_field_value in all_tvd_op_data_fields_and_value:
            field_name_split = initial_field_name.split("_")
            tvd_field_name_prefix = field_name_split[0]
            tvd_number = int(field_name_split[1])
            tvd_field_name_suffix = field_name_split[2]
            tvd_zc_relation = self.tvd_zc_library.get_by_zc_name_and_tvd_number(
                zc_identifier=equipment_name,
                num_tvd_zc_starting_0=tvd_number,
            )
            if tvd_zc_relation:
                new_field_name = f"{tvd_field_name_prefix}_{tvd_number}_{tvd_zc_relation.tvd_identifier}_{tvd_field_name_suffix}"
                decoded_specific_message.fields_with_value[new_field_name] = initial_field_value

        assert decoded_specific_message
        return decoded_specific_message
