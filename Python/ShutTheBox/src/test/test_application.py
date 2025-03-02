# -*-coding:Utf-8 -*
import pytest

from shutthebox import application
from shutthebox.dices import Dice
from logger import logger_config

# fmt: off
small_examples_test_data = [([Dice(list(range(1, 2)))], list(range(1, 2)), 1),
                            ([Dice(list(range(1, 3)))], list(range(1, 3)), 4), 
                            ([Dice(list(range(1, 4)))], list(range(1, 4)), 24), 
                            ([Dice(list(range(1, 5)))], list(range(1, 5)), 158), 
                            ([Dice(list(range(1, 6)))], list(range(1, 6)), 1256), 
                            ([Dice(list(range(1, 7)))], list(range(1, 7)), 10951)]
# fmt: on


class TestBugTurnsInDouble20250302:
    def test_bug_turns_in_double(self) -> None:
        logger_config.configure_logger_with_random_log_file_suffix("shutthebox")
        simulation_request = application.SimulationRequest([Dice(list(range(1, 5)))], list(range(1, 4)))
        simulation = application.Application().run(simulation_request)
        simulation_result = simulation.complete_simulation_result
        initial_situation = simulation_result.initial_situation
        first_level_turns = initial_situation.next_turns
        first_level_turns_size = len(first_level_turns)

        # Extract dices_sum from each OneTurn's dices_result_action
        dices_sums = {turn.dices_result_action.dices_sum for turn in first_level_turns}

        # Assert that all sums are unique
        assert len(dices_sums) == len(first_level_turns), "Duplicate dices_sum values found in first_level_turns"

        last_first_level_turn = first_level_turns[first_level_turns_size - 1].dices_result_action.dices_sum
        before_last_first_level_turn = first_level_turns[first_level_turns_size - 2]
        pause = 1


class TestSimpleSimulations:

    @pytest.mark.parametrize("dices, initial_opened_hatches, expected_number_of_plays", small_examples_test_data)
    def test_small_examples(self, dices: list[Dice], initial_opened_hatches: list[int], expected_number_of_plays: int) -> None:
        logger_config.configure_logger_with_random_log_file_suffix("shutthebox")
        logger_config.print_and_log_info("application start")
        simulation_request = application.SimulationRequest(dices, initial_opened_hatches)
        simulation: application.Simulation = application.Application().run(simulation_request)
        simulation_result = simulation.complete_simulation_result
        all_flat_games = simulation_result.all_flat_games
        # simulation.complete_simulation_result.dump_in_json_file("TestOne1SidesDiceAnd1Hatches.json")
        assert len(simulation_result.initial_situation.next_turns) == expected_number_of_plays
        assert len(all_flat_games) == expected_number_of_plays

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
