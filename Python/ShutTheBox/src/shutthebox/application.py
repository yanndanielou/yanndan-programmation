# -*-coding:Utf-8 -*
""" Main """

from dataclasses import dataclass, field
from typing import List, Optional  # , TYPE_CHECKING

from logger import logger_config
from common import json_encoders

from shutthebox.dices import Dices, Dice, DicesThrownCombinationsResults
from shutthebox.combinations_to_reach_sum import CombinationsToReachSum

# if TYPE_CHECKING:
#    from shutthebox.dices import DicesThrownCombinationsOfOneSum


import json
from json import JSONEncoder
from typing import Any


class SimulationResultEncoder(JSONEncoder):
    def default(self, o: Any) -> list | Any:
        if isinstance(o, set):
            return list(o)

        if hasattr(o, "__dict__"):
            obj_dict = o.__dict__.copy()

            # Break circular references by replacing objects with simple identifiers
            if "_previous_turn" in obj_dict and obj_dict["_previous_turn"] is not None:
                pass  # obj_dict["_previous_turn"] = f"OneTurn(previous_turn_id={id(obj_dict['_previous_turn'])})"

            if "_next_turns" in obj_dict and obj_dict["_next_turns"]:
                pass  # obj_dict["_next_turns"] = [f"OneTurn(next_turn_id={id(turn)})" for turn in obj_dict["_next_turns"] if turn]

            if "_turn" in obj_dict and obj_dict["_turn"] is not None:
                pass  # obj_dict["_turn"] = f"OneTurn(turn_id={id(obj_dict['_turn'])})"

            return obj_dict

        return super().default(o)


@dataclass
class CompleteSimulationResult:

    _all_flat_games: list["OneFlatGame"] = field(default_factory=list)

    @property
    def all_flat_games(self) -> list["OneFlatGame"]:
        return self._all_flat_games

    def add_flat_games(self, flat_games_to_add: list["OneFlatGame"]) -> None:
        self._all_flat_games = self._all_flat_games + flat_games_to_add

    def add_flat_game(self, flat_game_to_add: "OneFlatGame") -> None:
        self._all_flat_games.append(flat_game_to_add)

    def dump_in_json_file(self, json_file_full_path: str) -> None:

        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(self._all_flat_games, json_file_full_path, SimulationResultEncoder)


@dataclass
class CloseHatchesAction:
    _dices_result_step: "DicesResultStep"
    _opened_hatches_before_turn: list[int]
    _closed_hatches_during_turn: Optional[list[int]]
    # _previously_already_closed_hatches: list[int] = field(default_factory=list)
    _turn: Optional["OneTurn"] = None

    @property
    def turn(self) -> Optional["OneTurn"]:
        return self._turn

    @turn.setter
    def turn(self, turn: "OneTurn") -> None:
        self._turn = turn


@dataclass
class DicesResultStep:
    _dices_sum: int
    _dices_sum_odds: float
    _turns: list["OneTurn"] = field(default_factory=list)

    @property
    def turns(self) -> list["OneTurn"]:
        return self._turns

    @property
    def dices_sum(self) -> int:
        return self._dices_sum

    def __str__(self) -> str:
        return f"DicesResultAction thrown, sum:{self.dices_sum}, _dices_sum_odds:{self._dices_sum_odds}"


@dataclass
class OneTurn:
    _dices_result_action: DicesResultStep
    _close_hatches_action: CloseHatchesAction
    _previous_turn: Optional["OneTurn"] = None
    _next_turns: List[Optional["OneTurn"]] = field(default_factory=list)


@dataclass
class OneFlatGame:
    last_turn: OneTurn
    final_opened_hatches: list[int]


@dataclass
class SimulationRequest:
    _dices: list[Dice] = field(default_factory=lambda: [Dice(), Dice()])
    _initial_opened_hatches: list[int] = field(default_factory=lambda: list(range(1, 10)))

    @property
    def dices(self) -> list[Dice]:
        return self._dices

    @property
    def initial_opened_hatches(self) -> list[int]:
        return self._initial_opened_hatches


@dataclass
class Simulation:
    _simulation_request: SimulationRequest
    _complete_simulation_result: CompleteSimulationResult = field(default_factory=CompleteSimulationResult)

    @property
    def simulation_request(self) -> SimulationRequest:
        return self._simulation_request

    @property
    def complete_simulation_result(self) -> CompleteSimulationResult:
        return self._complete_simulation_result

    def start(self) -> None:
        self.throw_dices(self._simulation_request.initial_opened_hatches, None)

    def throw_dices(self, opened_hatches: list[int], previous_turn: Optional[OneTurn]) -> None:
        logger_config.print_and_log_info(f"throw_dices, opened_hatches:{opened_hatches}")

        dices_all_possible_thrown_combinations_results: DicesThrownCombinationsResults = Dices.get_dices_all_possible_thrown_combinations_results(self._simulation_request.dices)

        for combinations_grouped_by_sum in dices_all_possible_thrown_combinations_results.all_combinations_grouped_by_sum:
            dices_sum_odds = combinations_grouped_by_sum.get_odds()
            dices_result_step = DicesResultStep(_dices_sum=combinations_grouped_by_sum.sum, _dices_sum_odds=dices_sum_odds)

            self.play_dices_result_step(dices_result_step, opened_hatches, previous_turn)

    def play_dices_result_step(self, dices_result_step: DicesResultStep, opened_hatches_before_step: list[int], previous_turn: Optional[OneTurn]) -> None:

        logger_config.print_and_log_info(f"play_dices_result_step, dices_result_step:{dices_result_step}, opened_hatches:{opened_hatches_before_step}, previous_turn:{previous_turn}")

        all_hatches_combinations = CombinationsToReachSum.get_all_unique_combinations_to_reach_exactly_sum_using_element_no_more_than_once(
            elements=opened_hatches_before_step, sum_to_reach=dices_result_step.dices_sum
        )

        if not all_hatches_combinations:

            logger_config.print_and_log_info(f"Game is lost, no possible hatch combination to reach {dices_result_step.dices_sum} from {opened_hatches_before_step}")

            close_hatch_action = CloseHatchesAction(_dices_result_step=dices_result_step, _opened_hatches_before_turn=opened_hatches_before_step, _closed_hatches_during_turn=[])
            new_turn = OneTurn(dices_result_step, close_hatch_action, previous_turn)
            dices_result_step.turns.append(new_turn)
            close_hatch_action.turn = new_turn

            flat_game = OneFlatGame(new_turn, opened_hatches_before_step)
            self._complete_simulation_result.add_flat_game(flat_game)

        for hatches_combination in all_hatches_combinations:

            new_opened_hatches: list[int] = list(set(opened_hatches_before_step) - set(hatches_combination))
            logger_config.print_and_log_info(f"hatches_combination {hatches_combination}, new_opened_hatches:{new_opened_hatches}")

            close_hatch_action = CloseHatchesAction(_dices_result_step=dices_result_step, _opened_hatches_before_turn=opened_hatches_before_step, _closed_hatches_during_turn=hatches_combination)
            new_turn = OneTurn(dices_result_step, close_hatch_action, previous_turn)
            dices_result_step.turns.append(new_turn)
            close_hatch_action.turn = new_turn

            if not new_opened_hatches:
                logger_config.print_and_log_info("Game is won, all hatches closed")

                flat_game = OneFlatGame(new_turn, new_opened_hatches)
                self._complete_simulation_result.add_flat_game(flat_game)

            else:
                self.throw_dices(new_opened_hatches, new_turn)


@dataclass
class Application:
    """Close the box application"""

    def run(self, simulation_request: SimulationRequest = SimulationRequest()) -> Simulation:
        """Run"""
        simulation = Simulation(simulation_request)
        logger_config.print_and_log_info("Run")
        simulation.start()
        return simulation
