# -*-coding:Utf-8 -*
# import pytest

from shutthebox import application
from shutthebox.dices import Dice
from logger import logger_config


class TestSimpleSimulations:

    class TestOne1SidesDiceAnd1Hatches:

        def test_x(self) -> None:
            dices: list[Dice] = [Dice(list(range(1, 2)))]
            initial_opened_hatches: list[int] = list(range(1, 2))

            logger_config.configure_logger_with_random_log_file_suffix("shutthebox")
            logger_config.print_and_log_info("application start")
            simulation_request = application.SimulationRequest(dices, initial_opened_hatches)
            simulation: application.Simulation = application.Application().run(simulation_request)
            all_flat_games = simulation.complete_simulation_result.all_flat_games
            # simulation.complete_simulation_result.dump_in_json_file("TestOne1SidesDiceAnd1Hatches.json")

            assert len(all_flat_games) == 1

    class TestOne2SidesDiceAnd2Hatches:

        def test_x(self) -> None:
            dices: list[Dice] = [Dice(list(range(1, 3)))]
            initial_opened_hatches: list[int] = list(range(1, 3))

            logger_config.configure_logger_with_random_log_file_suffix("shutthebox")
            logger_config.print_and_log_info("application start")
            simulation_request = application.SimulationRequest(dices, initial_opened_hatches)
            simulation: application.Simulation = application.Application().run(simulation_request)
            all_flat_games = simulation.complete_simulation_result.all_flat_games
            # simulation.complete_simulation_result.dump_in_json_file("TestOne2SidesDiceAnd2Hatches.json")

            assert len(all_flat_games) == 5

    class TestOne3SidesDiceAnd3Hatches:

        def test_x(self) -> None:
            dices: list[Dice] = [Dice(list(range(1, 4)))]
            initial_opened_hatches: list[int] = list(range(1, 4))

            logger_config.configure_logger_with_random_log_file_suffix("shutthebox")
            logger_config.print_and_log_info("application start")
            simulation_request = application.SimulationRequest(dices, initial_opened_hatches)
            simulation: application.Simulation = application.Application().run(simulation_request)
            all_flat_games = simulation.complete_simulation_result.all_flat_games
            # simulation.complete_simulation_result.dump_in_json_file("TestOne3SidesDiceAnd3Hatches.json")

            assert len(all_flat_games) == 27

    class TestOne6SidesDiceAnd6Hatches:

        def test_x(self) -> None:
            dices: list[Dice] = [Dice()]
            initial_opened_hatches: list[int] = list(range(1, 7))

            logger_config.configure_logger_with_random_log_file_suffix("shutthebox")
            logger_config.print_and_log_info("application start")
            simulation_request = application.SimulationRequest(dices, initial_opened_hatches)
            simulation: application.Simulation = application.Application().run(simulation_request)
            all_flat_games = simulation.complete_simulation_result.all_flat_games
            # simulation.complete_simulation_result.dump_in_json_file("TestOne6SidesDiceAnd6Hatches.json")

            assert len(all_flat_games) == 15
