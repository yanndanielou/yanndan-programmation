import inspect
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

import pandas
from common import file_utils, json_encoders
from logger import logger_config

from networkflowmatrix import constants

if TYPE_CHECKING:
    from networkflowmatrix import (
        equipments,
        network_matrix_data_model,
    )


def create_reports_after_matching_network_conf_files_and_flow_matrix(
    network_flow_matrix: "network_matrix_data_model.NetworkFlowMatrix", equipments_library: "equipments.NetworkConfFilesEquipmentsLibrary"
) -> None:

    with logger_config.stopwatch_with_label(f"{inspect.stack(0)[0].function}", inform_beginning=True):
        file_utils.create_folder_if_not_exist(constants.OUTPUT_PARENT_DIRECTORY_NAME)

        create_reports_wrong_ip(network_flow_matrix, equipments_library)
        create_report_flows_synthesis(network_flow_matrix, equipments_library)
        create_report_equipments_on_multiple_subsystems(network_flow_matrix, equipments_library)
        create_report_equipments_on_multiple_types(network_flow_matrix, equipments_library)
        create_report_equipments_synthesis(network_flow_matrix, equipments_library)
        create_report_flows_synthesis(network_flow_matrix, equipments_library)
        create_report_subsystems_synthesis(network_flow_matrix, equipments_library)
        create_report_types_synthesis(network_flow_matrix, equipments_library)
        create_report_network_conf_files_groups(equipments_library)
        create_report_unknown_equipment(equipments_library)

        create_dump_network_conf_files_library(equipments_library, "all_equipments_in_conf_files_after_matching_network_matrix")

        pass


def create_report_network_conf_files_groups(equipments_library: "equipments.NetworkConfFilesEquipmentsLibrary") -> None:

    save_rows_to_output_files(
        rows_as_list_dict=[
            {
                "Group definition": group.definition,
                "Number of equipments": len(group.equipments),
                "Equipments": ",".join([equipment.name for equipment in group.equipments]),
            }
            for group in equipments_library.all_groups
        ],
        file_base_name="network_conf_files_groups",
    )


def create_dump_network_conf_files_library(equipments_library: "equipments.NetworkConfFilesEquipmentsLibrary", output_json_file_base_name: str) -> None:

    data_to_dump_equipment = [
        {
            "name": f"{equipment.name}",
            "Source": f"{equipment.source_label}",
            "Types": f"{', '.join(list(equipment.equipment_types))}",
            "Seclab": f"{equipment.seclab_side}",
            "Alternative ids": f"{', '.join([str(alter) for alter in equipment.alternative_identifiers])}",
            "Ip": f"{', '.join([ip.ip_raw for ip in equipment.ip_addresses])}",
            "Groups": f"{', '.join([group.definition.name + ' ' + group.definition.subnet_and_mask for  group in equipment.groups])}",
        }
        for equipment in equipments_library.all_network_conf_files_defined_equipments
    ]
    save_rows_to_output_files(data_to_dump_equipment, f"{output_json_file_base_name}_equipments")

    data_to_dump_groups = [
        {
            "group definition": group.definition,
            "Equipments": ",".join(
                [equipment.name for equipment in group.equipments],
            ),
        }
        for group in equipments_library.all_groups
    ]
    save_rows_to_output_files(data_to_dump_groups, f"{output_json_file_base_name}_groups")
    data_to_dump = data_to_dump_equipment + data_to_dump_groups

    output_json_file_full_path = f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/{output_json_file_base_name}.json"
    json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(data_to_dump, output_json_file_full_path)


def create_reports_wrong_ip(network_flow_matrix: "network_matrix_data_model.NetworkFlowMatrix", equipments_library: "equipments.NetworkConfFilesEquipmentsLibrary") -> None:

    save_rows_to_output_files(
        rows_as_list_dict=[
            {
                "Wrong IP": wrong_ip.wrong_equipment_name_allocated_to_this_ip_by_mistake,
                "detected on sncf network": wrong_ip.raw_ip_address,
                "source providers": ",".join(wrong_ip.equipments_names_having_genuinely_this_ip_address),
                "destination providers": ",".join([str(matrix_line) for matrix_line in wrong_ip.matrix_line_ids_referencing]),
            }
            for wrong_ip in sorted(equipments_library.wrong_equipment_name_allocated_to_this_ip_by_mistake, key=lambda x: x.wrong_equipment_name_allocated_to_this_ip_by_mistake)
        ],
        file_base_name="matrix_wrong_ip",
    )


def create_report_flows_synthesis(network_flow_matrix: "network_matrix_data_model.NetworkFlowMatrix", equipments_library: "equipments.NetworkConfFilesEquipmentsLibrary") -> None:

    save_rows_to_output_files(
        rows_as_list_dict=[
            {
                "identifier": matrix_line.identifier_int,
                "detected on sncf network": "" if matrix_line.is_deleted else "X" if matrix_line.is_sncf_network_detected() else "",
                "source providers": [provider.name for provider in matrix_line.source.get_all_network_entity_providers()],
                "destination providers": [provider.name for provider in matrix_line.destination.get_all_network_entity_providers()],
            }
            for matrix_line in network_flow_matrix.network_flow_matrix_lines
        ],
        file_base_name="flow_on_sncf_network_detection",
    )


def create_report_subsystems_synthesis(network_flow_matrix: "network_matrix_data_model.NetworkFlowMatrix", equipments_library: "equipments.NetworkConfFilesEquipmentsLibrary") -> None:

    save_rows_to_output_files(
        rows_as_list_dict=[
            {
                "Type name": subsystem.name,
                "Number of matrix flow equipments": len(subsystem.all_equipments_detected_in_flow_matrix),
                "matrix flow equipments": ",".join([equipment.name for equipment in subsystem.all_equipments_detected_in_flow_matrix]),
            }
            for subsystem in network_flow_matrix.all_matrix_flow_subsystems_definitions_instances
        ],
        file_base_name="matrix_all_subsystems",
    )


def create_report_types_synthesis(network_flow_matrix: "network_matrix_data_model.NetworkFlowMatrix", equipments_library: "equipments.NetworkConfFilesEquipmentsLibrary") -> None:

    save_rows_to_output_files(
        rows_as_list_dict=[
            {
                "Type name": type_it.name,
                "Number of network conf files equipments": len(type_it.network_conf_files_equipments_detected),
                "Network conf files equipments": ",".join([equipment.name for equipment in type_it.network_conf_files_equipments_detected]),
                "Number of matrix flow equipments": len(type_it.network_flow_matrix_equipments_detected),
                "matrix flow equipments": ",".join([equipment.name for equipment in type_it.network_flow_matrix_equipments_detected]),
            }
            for type_it in network_flow_matrix.all_types_defined
        ],
        file_base_name="matrix_all_types",
    )


def create_report_equipments_synthesis(network_flow_matrix: "network_matrix_data_model.NetworkFlowMatrix", equipments_library: "equipments.NetworkConfFilesEquipmentsLibrary") -> None:
    rows = []
    for equipment in network_flow_matrix.all_matrix_flow_equipments_definitions_instances:
        row = {
            "Name": equipment.name,
            "Number of subsystems": len(equipment.all_subsystems_detected_in_flow_matrix),
            "Subsystems": ",".join([subsystem.name for subsystem in equipment.all_subsystems_detected_in_flow_matrix]),
            "Subsystems with associated lines": ",".join(
                [
                    subsystem.name + ":" + "-".join([str(line_identifier_int) for line_identifier_int in line_identifiers])
                    for subsystem, line_identifiers in equipment.all_subsystems_detected_in_flow_matrix_with_lines_identifiers.items()
                ]
            ),
            "Number of types": [subsystem.name for subsystem in equipment.all_subsystems_detected_in_flow_matrix],
            "Types": ",".join(equipment.all_types_names_detected_in_flow_matrix),
        }
        for subsystem, lines_identifiers in equipment.all_subsystems_detected_in_flow_matrix_with_lines_identifiers.items():
            row["Subsystem " + subsystem.name + " number of lines"] = len(lines_identifiers)
            row["Subsystem " + subsystem.name + " lines"] = ",".join(str(line_identifier_str) for line_identifier_str in lines_identifiers)

        for type_it, lines_identifiers in equipment.all_types_detected_in_flow_matrix_with_lines_identifiers.items():
            row["Type " + type_it.name + " number of lines"] = len(lines_identifiers)
            row["Type " + type_it.name + " lines"] = ",".join(str(line_identifier_str) for line_identifier_str in lines_identifiers)

        rows.append(row)

    save_rows_to_output_files(rows, "matrix_all_equipments_in_flow_matrix")


def create_report_unknown_equipment(equipments_library: "equipments.NetworkConfFilesEquipmentsLibrary") -> None:

    save_rows_to_output_files(
        rows_as_list_dict=[
            {
                "Not found equipment name": not_found_eqpt.name,
                "IP Address": not_found_eqpt.raw_ip_address,
                "Other equipments matching": ",".join(not_found_eqpt.alternative_names_matching_ip),
                "Matrix lines ids": ",".join([str(matrix_line_id) for matrix_line_id in not_found_eqpt.matrix_line_ids_referencing]),
            }
            for not_found_eqpt in sorted(equipments_library.not_found_equipments_but_defined_in_flow_matrix, key=lambda x: x.name)
        ],
        file_base_name="matrix_all_unknown_equipments",
    )


def create_report_equipments_on_multiple_subsystems(network_flow_matrix: "network_matrix_data_model.NetworkFlowMatrix", equipments_library: "equipments.NetworkConfFilesEquipmentsLibrary") -> None:

    save_rows_to_output_files(
        rows_as_list_dict=[
            {
                "Equipment name": equipment.name,
                "Number of subsystems": len(equipment.all_subsystems_detected_in_flow_matrix),
                "subsystems": ",".join(type_it.name for type_it in equipment.all_subsystems_detected_in_flow_matrix),
                "subsystems with number of occurences": "-".join(
                    [subsystem.name + ":" + str(len(line_identifiers)) for subsystem, line_identifiers in equipment.all_subsystems_detected_in_flow_matrix_with_lines_identifiers.items()]
                ),
                "subsystems with line ids": "-".join(
                    [
                        subsystem.name + ":" + ",".join([str(line_identifier_int) for line_identifier_int in line_identifiers])
                        for subsystem, line_identifiers in equipment.all_subsystems_detected_in_flow_matrix_with_lines_identifiers.items()
                    ]
                ),
            }
            for equipment in sorted(
                [equipment for equipment in network_flow_matrix.all_matrix_flow_equipments_definitions_instances if len(equipment.all_subsystems_detected_in_flow_matrix) > 1], key=lambda x: x.name
            )
        ],
        file_base_name="matrix_all_equipments_on_multiple_subsystems",
    )


def create_report_equipments_on_multiple_types(network_flow_matrix: "network_matrix_data_model.NetworkFlowMatrix", equipments_library: "equipments.NetworkConfFilesEquipmentsLibrary") -> None:

    save_rows_to_output_files(
        rows_as_list_dict=[
            {
                "Equipment name": equipment.name,
                "Number of types": len(equipment.all_types_detected_in_flow_matrix_with_lines_identifiers),
                "Types": ",".join(type_it.name for type_it in equipment.all_types_detected_in_flow_matrix_with_lines_identifiers),
                "Types with number of occurences": "-".join(
                    [type_it.name + ":" + str(len(line_identifiers)) for type_it, line_identifiers in equipment.all_types_detected_in_flow_matrix_with_lines_identifiers.items()]
                ),
                "Types with line ids": "-".join(
                    [
                        type_it.name + ":" + ",".join([str(line_identifier_int) for line_identifier_int in line_identifiers])
                        for type_it, line_identifiers in equipment.all_types_detected_in_flow_matrix_with_lines_identifiers.items()
                    ]
                ),
            }
            for equipment in sorted(
                [equipment for equipment in network_flow_matrix.all_matrix_flow_equipments_definitions_instances if len(equipment.all_types_names_detected_in_flow_matrix) > 1], key=lambda x: x.name
            )
        ],
        file_base_name="matrix_all_equipments_with_multiple_types",
    )


def save_rows_to_output_files(rows_as_list_dict: List[Dict[str, Any]], file_base_name: str) -> None:
    with logger_config.stopwatch_with_label(f"{inspect.stack(0)[0].function} for {len(rows_as_list_dict)} lines to {file_base_name}", inform_beginning=True):
        file_path_without_suffix = f"{constants.OUTPUT_PARENT_DIRECTORY_NAME}/{file_base_name}"
        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(rows_as_list_dict, f"{file_path_without_suffix}.json")
        pandas.DataFrame(rows_as_list_dict).to_excel(f"{file_path_without_suffix}.xlsx", index=False)
        pandas.DataFrame(rows_as_list_dict).to_csv(f"{file_path_without_suffix}.csv", index=False)
