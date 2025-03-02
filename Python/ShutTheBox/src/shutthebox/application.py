# -*-coding:Utf-8 -*
""" Main """

from dataclasses import dataclass, field
from typing import List, Optional, Any  # , TYPE_CHECKING


from json import JSONEncoder

from logger import logger_config
from common import json_encoders

from shutthebox.dices import Dices, Dice, DicesThrownCombinationsResults
from shutthebox.combinations_to_reach_sum import CombinationsToReachSum
from shutthebox import param

# if TYPE_CHECKING:
#    from shutthebox.dices import DicesThrownCombinationsOfOneSum


class CompleteSimulationResult:

    def __init__(self, initial_situation: "InitialSituation") -> None:
        self._all_flat_games: list["OneFlatGame"] = []
        self._initial_situation = initial_situation

    @property
    def all_flat_games(self) -> list["OneFlatGame"]:
        return self._all_flat_games

    @property
    def initial_situation(self) -> "InitialSituation":
        return self._initial_situation

    def add_flat_game(self, flat_game_to_add: "OneFlatGame") -> None:
        self._all_flat_games.append(flat_game_to_add)
        if len(self._all_flat_games) % 1000 == 0:
            logger_config.print_and_log_info(f"Games computed so far:{len(self._all_flat_games)}")

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
    _previous_turn: Optional["OneTurn|InitialSituation"] = None
    _next_turns: List["OneTurn"] = field(default_factory=list)
    _games_using_turn: list["OneFlatGame"] = field(default_factory=list)

    @property
    def next_turns(self) -> List["OneTurn"]:
        return self._next_turns


@dataclass
class InitialSituation:
    _initial_opened_hatches: list[int]
    _next_turns: List["OneTurn"] = field(default_factory=list)

    @property
    def next_turns(self) -> List["OneTurn"]:
        return self._next_turns


@dataclass
class OneFlatGame:
    last_turn: OneTurn
    final_opened_hatches: list[int]


@dataclass
class SimulationRequest:
    _dices: list[Dice] = field(default_factory=lambda: [Dice(), Dice()])
    _initial_opened_hatches: list[int] = field(default_factory=lambda: param.DEFAULT_INITIAL_OPENED_HATCHES)

    @property
    def dices(self) -> list[Dice]:
        return self._dices

    @property
    def initial_opened_hatches(self) -> list[int]:
        return self._initial_opened_hatches


class Simulation:

    def __init__(self, simulation_request: SimulationRequest) -> None:
        self._simulation_request: SimulationRequest = simulation_request
        self._initial_situation = InitialSituation(simulation_request.initial_opened_hatches)
        self._complete_simulation_result: CompleteSimulationResult = CompleteSimulationResult(self._initial_situation)

    def _create_new_turn(
        self,
        dices_result_step: DicesResultStep,
        previous_turn: OneTurn | InitialSituation,
        closed_hatches_during_turn: list[int],
        opened_hatches_before_step: list[int],
    ) -> OneTurn:
        close_hatch_action = CloseHatchesAction(_dices_result_step=dices_result_step, _opened_hatches_before_turn=opened_hatches_before_step, _closed_hatches_during_turn=closed_hatches_during_turn)

        new_turn = OneTurn(dices_result_step, close_hatch_action, previous_turn)
        previous_turn.next_turns.append(new_turn)
        dices_result_step.turns.append(new_turn)
        close_hatch_action.turn = new_turn
        return new_turn

    def _create_new_game(self, new_turn: OneTurn, opened_hatches_before_step: list[int]) -> OneFlatGame:
        new_game = OneFlatGame(new_turn, opened_hatches_before_step)
        self._complete_simulation_result.add_flat_game(new_game)
        return new_game

    @property
    def simulation_request(self) -> SimulationRequest:
        return self._simulation_request

    @property
    def complete_simulation_result(self) -> CompleteSimulationResult:
        return self._complete_simulation_result

    def start(self) -> None:
        self.throw_dices(self._simulation_request.initial_opened_hatches, self._initial_situation)

    def throw_dices(self, opened_hatches: list[int], previous_turn: OneTurn | InitialSituation) -> None:
        # logger_config.print_and_log_info(f"throw_dices, opened_hatches:{opened_hatches}")

        dices_all_possible_thrown_combinations_results: DicesThrownCombinationsResults = Dices.get_dices_all_possible_thrown_combinations_results(self._simulation_request.dices)

        for combinations_grouped_by_sum in dices_all_possible_thrown_combinations_results.all_combinations_grouped_by_sum:
            dices_sum_odds = combinations_grouped_by_sum.get_odds()
            dices_result_step = DicesResultStep(_dices_sum=combinations_grouped_by_sum.sum, _dices_sum_odds=dices_sum_odds)

            self.play_dices_result_step(dices_result_step, opened_hatches, previous_turn)

    def play_dices_result_step(self, dices_result_step: DicesResultStep, opened_hatches_before_step: list[int], previous_turn: OneTurn | InitialSituation) -> None:

        # logger_config.print_and_log_info(f"play_dices_result_step, dices_result_step:{dices_result_step}, opened_hatches:{opened_hatches_before_step}, previous_turn:{previous_turn}")

        all_hatches_combinations = CombinationsToReachSum.get_all_unique_combinations_to_reach_exactly_sum_using_element_no_more_than_once(
            elements=opened_hatches_before_step, sum_to_reach=dices_result_step.dices_sum
        )

        if not all_hatches_combinations:

            # logger_config.print_and_log_info(f"Game is lost, no possible hatch combination to reach {dices_result_step.dices_sum} from {opened_hatches_before_step}")
            new_turn = self._create_new_turn(dices_result_step, previous_turn, [], opened_hatches_before_step)
            self._create_new_game(new_turn, opened_hatches_before_step)

        for hatches_combination in all_hatches_combinations:

            new_opened_hatches: list[int] = list(set(opened_hatches_before_step) - set(hatches_combination))
            # logger_config.print_and_log_info(f"hatches_combination {hatches_combination}, new_opened_hatches:{new_opened_hatches}")

            new_turn = self._create_new_turn(dices_result_step, previous_turn, hatches_combination, opened_hatches_before_step)

            if not new_opened_hatches:
                # logger_config.print_and_log_info("Game is won, all hatches closed")
                self._create_new_game(new_turn, new_opened_hatches)

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
        logger_config.print_and_log_info(f"Simulation ended. Games computer {len(simulation.complete_simulation_result.all_flat_games)}")

        return simulation
