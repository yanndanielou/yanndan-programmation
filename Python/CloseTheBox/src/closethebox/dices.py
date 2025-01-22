# -*-coding:Utf-8 -*
""" Class that handles dices """

from typing import List, Tuple, cast, Dict
import itertools

from common import singleton

class Dices(metaclass=singleton.Singleton):
    """ Dices """

    @staticmethod
    def get_two_dices_all_combinaisons_by_sum() -> dict[int,list[Tuple[int, int]]]:
        return cast(Dict[int, List[Tuple[int, int]]], Dices.get_several_dices_all_combinaisons_by_sum(2))

    @staticmethod
    def get_several_dices_all_combinaisons_by_sum(number_of_dices:int) -> dict[int,list[Tuple[int, ...]]]:
        several_dices_all_combinaisons = Dices.get_several_dices_all_combinaisons(number_of_dices=number_of_dices)
        all_combinaisons_by_sum:dict[int,list[Tuple[int, ...]]] = dict()

        for combinaison in several_dices_all_combinaisons:
            sum_dices:int =  sum(combinaison)

            if sum_dices in all_combinaisons_by_sum:
                all_combinaisons_by_sum[sum_dices] += [combinaison]

            else:
                all_combinaisons_by_sum[sum_dices] = [combinaison]

        return all_combinaisons_by_sum


    @staticmethod
    def get_several_dices_all_combinaisons(number_of_dices:int) -> List[Tuple[int, ...]]:
        one_dice_combinaisons = list(range(1,7))

        #Le cast est une façon explicite de dire à MyPy : "je sais mieux que toi dans ce cas précis". Il informe MyPy que nous avons bien une List[Tuple[int, int]] # pylint: disable=line-too-long
        all_combinaisons: List[Tuple[int, ...]] = list(itertools.product(one_dice_combinaisons, repeat=number_of_dices))

        return all_combinaisons
