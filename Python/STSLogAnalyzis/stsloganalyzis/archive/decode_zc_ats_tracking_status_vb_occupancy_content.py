from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stsloganalyzis.archive.decode_message import DecodedMessage

from stsloganalyzis.zone_controllers import virtual_canton_zc

from stsloganalyzis.archive import decode_specific_message_content

PAS_ATS_TRACKING_STATUS_VB_OCCUPANCY_MESSAGE_ID = 173


@dataclass
class ZcAtsTrackingStatusVbOccDecoder:
    virtual_canton_zc_library: "virtual_canton_zc.VirtualCantonZcLibrary"

    def decode(self, decoded_message: "DecodedMessage", equipment_name: str) -> decode_specific_message_content.SpecificMessageContentDecoded:

        decoded_specific_message = decode_specific_message_content.SpecificMessageContentDecoded()
        all_tvd_op_data_fields_and_value = [(key, value) for (key, value) in decoded_message.decoded_fields_flat_directory.items() if key.startswith("VBOccupancy")]

        for initial_field_name, initial_field_value in all_tvd_op_data_fields_and_value:
            assert isinstance(initial_field_value, int)
            field_name_split = initial_field_name.split("_")
            cv_field_name_prefix = field_name_split[0]
            cv_number = int(field_name_split[1])

            cv_zc_relation = self.virtual_canton_zc_library.get_by_zc_name_and_cv_number(
                zc_identifier=equipment_name,
                num_cv_zc_starting_1=cv_number,
            )
            if cv_zc_relation:
                new_field_name = f"{cv_field_name_prefix}_{cv_number}_{cv_zc_relation.cv_identifier}"
                decoded_specific_message.fields_with_value[new_field_name] = virtual_canton_zc.VbOccupancyState(initial_field_value).name
                decoded_message.decoded_fields_flat_directory.pop(initial_field_name)
            else:
                decoded_message.decoded_fields_flat_directory[initial_field_name] = virtual_canton_zc.VbOccupancyState(initial_field_value).name

        assert decoded_specific_message
        return decoded_specific_message
