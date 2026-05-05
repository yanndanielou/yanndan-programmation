from logger import logger_config

import connexion_param
from champfx import create_champfx, constants


def main() -> None:
    """Main function"""

    with logger_config.application_logger():

        application = create_champfx.CreateChampFXApplication(
            champfx_login=connexion_param.champfx_login,
            champfx_password=connexion_param.champfx_password,
        )
        application.init()
        application.create_champfx(
            cfx_data=create_champfx.CreateChampFxData(
                headline="headline",
                project_name="FR_NEXTEO",
                category=constants.Category.CONFIGURATION_DATA,
                current_owner="Danielou Yann (fr232487)",
                description="Description",
                request_type=constants.RequestType.DEFECT,
                severity=constants.Severity.MINOR_IMPACT_ON_AVAILABILITY,
                system_structure_part_1="S002_Subsystem",
                system_structure_part_2="Réseau Sol ATS",
                system_structure_part_3="STD pour COVASEC décembre 2025",
                safety_relevant=constants.SafetyRelevant.NO,
                security_relevant=constants.SecurityRelevant.MITIGATED,
                detected_in_phase=constants.DetectedInPhase.VALIDATION,
                environment_type=constants.EnvironmentType.TEST_SYSTEM,
            )
        )


if __name__ == "__main__":
    main()
