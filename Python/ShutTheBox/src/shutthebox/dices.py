# -*-coding:Utf-8 -*
""" Class that handles dices """

from typing import List, Tuple, cast, Dict
import itertools

#from common import singleton

#class Dices(metaclass=singleton.Singleton):
class Dices:

    """ Dices """

    @staticmethod
    def get_two_dices_all_combinations_by_sum() -> dict[int,list[Tuple[int, int]]]:
        return cast(Dict[int, List[Tuple[int, int]]], Dices.get_several_dices_all_combinations_by_sum(2))

    @staticmethod
    def get_several_dices_all_combinations_by_sum(number_of_dices:int) -> dict[int,list[Tuple[int, ...]]]:
        several_dices_all_combinations = Dices.get_several_dices_all_combinations(number_of_dices=number_of_dices)
        all_combinations_by_sum:dict[int,list[Tuple[int, ...]]] = dict()

        for combination in several_dices_all_combinations:
            sum_dices:int =  sum(combination)

            if sum_dices in all_combinations_by_sum:
                all_combinations_by_sum[sum_dices] += [combination]

            else:
                all_combinations_by_sum[sum_dices] = [combination]

        return all_combinations_by_sum


    @staticmethod
    def get_several_dices_all_combinations(number_of_dices:int) -> List[Tuple[int, ...]]:
        one_dice_combinations = list(range(1,7))

        #Le cast est une façon explicite de dire à MyPy : "je sais mieux que toi dans ce cas précis". Il informe MyPy que nous avons bien une List[Tuple[int, int]] # pylint: disable=line-too-long
        all_combinations: List[Tuple[int, ...]] = list(itertools.product(one_dice_combinations, repeat=number_of_dices))

        return all_combinations
