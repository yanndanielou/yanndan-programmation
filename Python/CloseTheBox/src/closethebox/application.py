# -*-coding:Utf-8 -*
""" Main """
from logger import logger_config

class Application:
    """ Close the box application """
    def __init__(self)->None:
        pass
    
    def run(self)->None:
        """ Run """
        pass
    
    def get_two_dices_all_combinaisons_with_occurences(self)->dict[int, int]:
        one_dices_combinaisons = range(1,7)
        
        all_combinaisons_with_occurences: dict[int, int] = {}
        
        for first_dice_result in one_dices_combinaisons:
            for second_dice_result in one_dices_combinaisons:
                sum_dices = first_dice_result + second_dice_result
                
                if sum_dices in all_combinaisons_with_occurences:
                    all_combinaisons_with_occurences[sum_dices] += 1
                                
                else:
                    all_combinaisons_with_occurences[sum_dices] = 1
        
        
        return all_combinaisons_with_occurences
        
        