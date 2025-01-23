# -*-coding:Utf-8 -*
""" Main """

from dataclasses import dataclass, field
from typing import List, Tuple

from dices import Dices

from logger import logger_config

from common import json_encoders




@dataclass
class OneTurn:
    dices_sum:int
    dices_results:Tuple[int, ...]
    opened_hatches_before_turn:list[int]
    closed_hatches_during_turn:list[int]
    previously_already_closed_hatches:list[int] = field(default_factory=list)

    def __str__(self) -> str:
        return f"Dices thrown:{self.dices_results}, opened_hatches_before_turn:{self.opened_hatches_before_turn}, closed_hatches_during_turns:{self.closed_hatches_during_turn}"

@dataclass
class OneGame:
    turns:list[OneTurn]
    final_opened_hatches:list[int]

    def __str__(self) -> str:
        return f"Final opened hatches: {self.final_opened_hatches} \n" + \
                "\tTurns: \n\t\t" + \
                "\n\t\t ".join([str(turn) for turn in self.turns])

class Application:
    """ Close the box application """
    def __init__(self) -> None:
        pass

    def run(self)->None:
        """ Run """
        pass

    def compute_all_possibilities_from_beginning(self) ->list[OneGame]:
        initial_opened_hatches = list(range(1,10))
        return self.compute_all_possibilities_with_hatches(initial_opened_hatches)
    
    
    def play_dices_with_all_combinaisons_with_same_sum(self, two_dices_sum:int, two_dices_results:list[Tuple[int, ...]], opened_hatches:list[int], previous_turns:list[OneTurn]|None = None)->list[OneGame]:
        if previous_turns is None: #to avoid https://pylint.pycqa.org/en/latest/user_guide/messages/warning/dangerous-default-value.html
            previous_turns = []

        all_possibilities_with_hatches:list[OneGame] = []
        
        for dices_results in two_dices_results:
                        
            all_hatches_combinaisons = self.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once(opened_hatches, two_dices_sum)
            
            if not all_hatches_combinaisons:
                
                
                current_turn_with_combinaison = OneTurn(dices_sum=two_dices_sum,
                                                        dices_results = dices_results,
                                                        closed_hatches_during_turn=None,
                                                        opened_hatches_before_turn=opened_hatches.copy()
                                                        )
                all_possibilities_with_hatches += [OneGame(final_opened_hatches=opened_hatches.copy(), turns=previous_turns.copy() + [current_turn_with_combinaison])]
            
            for hatches_combinaison in all_hatches_combinaisons:

                new_opened_hatches:list[int] = list(set(opened_hatches) - set(hatches_combinaison))
                current_turn_with_combinaison = OneTurn(dices_sum=two_dices_sum,
                                                        dices_results = dices_results,
                                                        closed_hatches_during_turn=hatches_combinaison,
                                                        opened_hatches_before_turn=opened_hatches.copy()
                                                        )
                
                
                all_possibilities_with_hatches += self.compute_all_possibilities_with_hatches(new_opened_hatches, previous_turns + [current_turn_with_combinaison])
    
        return all_possibilities_with_hatches

    def compute_all_possibilities_with_hatches(self, opened_hatches:list[int], previous_turns:list[OneTurn]|None = None)->list[OneGame]:
        
        if previous_turns is None: #to avoid https://pylint.pycqa.org/en/latest/user_guide/messages/warning/dangerous-default-value.html
            previous_turns = []

        all_possibilities_with_hatches:list[OneGame] = []

        two_dices_all_combinaisons_with_occurences:dict[int,list[Tuple[int, ...]]] = Dices.get_two_dices_all_combinaisons_by_sum()

        for two_dices_sum, two_dices_results in two_dices_all_combinaisons_with_occurences.items():
            all_possibilities_with_hatches += self.play_dices_with_all_combinaisons_with_same_sum(two_dices_sum, two_dices_results, opened_hatches, previous_turns)
            
                
        return all_possibilities_with_hatches + [OneGame(final_opened_hatches=opened_hatches.copy(), turns=previous_turns.copy())]
        

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

checker:Application = Application()
res_all_possibilities_with_hatches:list[OneGame] = checker.compute_all_possibilities_with_hatches([2])

json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(res_all_possibilities_with_hatches, "all_possibilities.json")

print(f"{len(res_all_possibilities_with_hatches)} possibilities found: \n\n" + "\n\n".join([str(game) for game in res_all_possibilities_with_hatches]))
#for game in all_possibilities_with_hatches:
#    print(f"Game :\n {str(game)}")

pause=1
