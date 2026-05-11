import pandas
from logger import logger_config


import connexion_param
from createchampfx import constants, create_champfx


def main() -> None:
    """Main function"""

    with logger_config.application_logger():

        application = create_champfx.CreateChampFXApplication(
            champfx_login=connexion_param.champfx_login,
            champfx_password=connexion_param.champfx_password,
        )
        application.init()

        main_data_frame: pandas.DataFrame = pandas.read_excel(r"D:\temp\resultats_tests_SSI_complet.xlsx", sheet_name="Sheet1")

        for index, (_, row) in enumerate(main_data_frame.iterrows()):
            test_name = row["Test"]
            step_name = int(row["Étape"])
            action = row["Action"]
            comment = row["Commentaire"]
            expected_result = row["Résultat attendu"]
            observed_result = row["Résultat observé"]
            requirements = row["Exigences SSI"]

            application.create_champfx(
                cfx_data=create_champfx.CreateChampFxData(
                    headline=f"STD SSI {test_name}/{step_name}:{comment}",
                    project_name="ATSP",
                    category=constants.Category.CONFIGURATION_DATA,
                    current_owner="Wasilewski Olivia (z003p11n)",
                    description=f"Test:\n{test_name}\n\nStep:\n{step_name}\n\nSTE STD SSI requirements:\n{requirements}\n\nAction:\n{action}\n\nRésultat attendu:\n{expected_result}\n\nRésultat observé:\n{observed_result}\n\nCommentaires (anomalie):\n{comment}",
                    request_type=constants.RequestType.DEFECT,
                    severity=constants.Severity.MINOR_IMPACT_ON_AVAILABILITY,
                    system_structure_part_1="S002_Subsystem",
                    system_structure_part_2="Réseau Sol ATS 1",
                    system_structure_part_3="STD pour COVASEC décembre 2025",
                    safety_relevant=constants.SafetyRelevant.NO,
                    security_relevant=constants.SecurityRelevant.YES,
                    detected_in_phase=constants.DetectedInPhase.VALIDATION,
                    environment_type=constants.EnvironmentType.TEST_SYSTEM,
                )
            )


if __name__ == "__main__":
    main()
