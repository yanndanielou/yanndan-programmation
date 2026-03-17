import random
from typing import List

from logger import logger_config

from nombres_et_syllabes.exercises_bank import (
    AdditionExercise,
    DoubleExercise,
    ListenAndTypeNumberExercise,
    ListenAndTypeWordExercise,
    ModexFrame,
    RecognizeSyllabeInChoiceWithVoiceExercise,
    SoustractionExercise,
    TextAnswerInEntryExercise,
)
from nombres_et_syllabes.ui import GameMainWindow

if __name__ == "__main__":
    with logger_config.application_logger("nombres_et_syllabes"):

        game_main_window = GameMainWindow()

        modes: List[ModexFrame] = [
            ListenAndTypeNumberExercise(game_main_window, number=random.randint(0, 10)),
            DoubleExercise(game_main_window, number=random.randint(0, 4)),
            SoustractionExercise(game_main_window, first_number=random.randint(3, 9), second_number=random.randint(0, 2)),
            ListenAndTypeNumberExercise(game_main_window, number=random.randint(10, 20)),
            SoustractionExercise(game_main_window, first_number=random.randint(3, 9), second_number=random.randint(1, 3)),
            DoubleExercise(game_main_window, number=random.randint(4, 8)),
            ListenAndTypeNumberExercise(game_main_window, number=random.randint(20, 39)),
            AdditionExercise(game_main_window, first_number=random.randint(0, 20), second_number=random.randint(2, 10)),
            SoustractionExercise(game_main_window, first_number=random.randint(8, 15), second_number=random.randint(2, 5)),
            DoubleExercise(game_main_window, number=random.randint(3, 7)),
            ListenAndTypeNumberExercise(game_main_window, number=random.randint(11, 16)),
            DoubleExercise(game_main_window, number=random.randint(5, 8)),
            ListenAndTypeNumberExercise(game_main_window, number=random.randint(11, 20)),
            AdditionExercise(game_main_window, first_number=random.randint(3, 9), second_number=random.randint(2, 5)),
            AdditionExercise(game_main_window, first_number=random.randint(3, 10), second_number=random.randint(2, 8)),
            SoustractionExercise(game_main_window, first_number=random.randint(3, 9), second_number=random.randint(2, 3)),
            AdditionExercise(game_main_window, first_number=random.randint(1, 20), second_number=random.randint(3, 10)),
            ListenAndTypeNumberExercise(game_main_window, number=random.randint(20, 30)),
            AdditionExercise(game_main_window, first_number=random.randint(4, 20), second_number=random.randint(3, 10)),
            ListenAndTypeNumberExercise(game_main_window, number=random.randint(30, 50)),
            AdditionExercise(game_main_window, first_number=random.randint(8, 20), second_number=random.randint(3, 10)),
            AdditionExercise(game_main_window, first_number=random.randint(2, 5), second_number=random.randint(18, 22)),
            # RecognizeSyllabeInChoiceWithVoiceExercise(game_main_window),
        ]

        game_main_window.modes = modes
        game_main_window.show_current_mode()

        game_main_window.mainloop()
