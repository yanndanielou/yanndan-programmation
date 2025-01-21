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
       
    def get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once(self,
                                                                                           elements:list[int],
                                                                                           sum_to_attain:int)->list[list[int]]:
               
        def backtrack(reste:int, index:int, chemin:list)->None:
            # Si la somme restante est atteinte, ajouter la combinaison
            if reste == 0:
                results.append(list(chemin))
                return
            # Si la somme restante est négative ou plus d'éléments, arrêter
            if reste < 0:
                return

            for i in range(index, len(elements)):
                # Ajouter le nombre actuel au chemin
                chemin.append(elements[i])
                # Appel récursif avec la somme restante mise à jour et index + 1 (pour éviter les répétitions)
                backtrack(reste - elements[i], i+1, chemin)  # Réutiliser l'élément actuel (index = i)
                # Retirer l'élément ajouté (backtracking)
                chemin.pop()


        results:list[list[int]] = list()

        backtrack(sum_to_attain, 0, [])    
        
        return results
    
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
        
        