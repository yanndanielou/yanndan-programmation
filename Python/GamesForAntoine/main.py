import random
from typing import Callable, List, cast

from logger import logger_config

from nombres_et_syllabes.ui import GameMainWindow
from nombres_et_syllabes.exercises_bank import (
    AdditionExercise,
    DoubleExercise,
    HeaderFrame,
    ListenAndTypeExercise,
    ModexFrame,
    RecognizeSyllabeInChoiceWithVoiceExercise,
    SoustractionExercise,
    TextAnswerInEntryExercise,
)

if __name__ == "__main__":
    with logger_config.application_logger("nombres_et_syllabes"):

        game_main_window = GameMainWindow()

        modes: List[ModexFrame] = [
            ListenAndTypeExercise(game_main_window, game_main_window.switch_mode, ListenAndTypeExercise.NumberToListenAndType(number=random.randint(0, 10))),
            ListenAndTypeExercise(game_main_window, game_main_window.switch_mode, ListenAndTypeExercise.NumberToListenAndType(number=random.randint(0, 20))),
            DoubleExercise(game_main_window, switch_mode_callback=game_main_window.switch_mode, number=random.randint(0, 5)),
            DoubleExercise(game_main_window, switch_mode_callback=game_main_window.switch_mode, number=random.randint(4, 8)),
            AdditionExercise(game_main_window, switch_mode_callback=game_main_window.switch_mode, first_number=random.randint(0, 20), second_number=random.randint(0, 10)),
            SoustractionExercise(game_main_window, switch_mode_callback=game_main_window.switch_mode, first_number=random.randint(3, 9), second_number=random.randint(0, 2)),
            SoustractionExercise(game_main_window, switch_mode_callback=game_main_window.switch_mode, first_number=random.randint(8, 15), second_number=random.randint(2, 5)),
            DoubleExercise(game_main_window, switch_mode_callback=game_main_window.switch_mode, number=random.randint(0, 6)),
            DoubleExercise(game_main_window, switch_mode_callback=game_main_window.switch_mode, number=random.randint(0, 8)),
            ListenAndTypeExercise(game_main_window, game_main_window.switch_mode, ListenAndTypeExercise.NumberToListenAndType(number=random.randint(0, 30))),
            AdditionExercise(game_main_window, switch_mode_callback=game_main_window.switch_mode, first_number=random.randint(0, 9), second_number=random.randint(0, 5)),
            AdditionExercise(game_main_window, switch_mode_callback=game_main_window.switch_mode, first_number=random.randint(0, 10), second_number=random.randint(0, 8)),
            SoustractionExercise(game_main_window, switch_mode_callback=game_main_window.switch_mode, first_number=random.randint(3, 9), second_number=random.randint(0, 2)),
            AdditionExercise(game_main_window, switch_mode_callback=game_main_window.switch_mode, first_number=random.randint(0, 20), second_number=random.randint(0, 10)),
            AdditionExercise(game_main_window, switch_mode_callback=game_main_window.switch_mode, first_number=random.randint(0, 20), second_number=random.randint(0, 10)),
            AdditionExercise(game_main_window, switch_mode_callback=game_main_window.switch_mode, first_number=random.randint(0, 20), second_number=random.randint(0, 10)),
            RecognizeSyllabeInChoiceWithVoiceExercise(game_main_window, game_main_window.switch_mode),
        ]

        game_main_window.modes = modes
        game_main_window.show_current_mode()

        game_main_window.mainloop()
