from typing import List, Tuple, Optional, TYPE_CHECKING


# class Dices(metaclass=singleton.Singleton):
class CombinationsToReachSum:
    """Dices"""

    @staticmethod
    def get_all_unique_combinations_to_reach_exactly_sum_using_element_no_more_than_once(elements: list[int], sum_to_attain: int) -> list[list[int]]:

        def backtrack(reste: int, index: int, chemin: list) -> None:
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
                backtrack(reste - elements[i], i + 1, chemin)  # Réutiliser l'élément actuel (index = i)
                # Retirer l'élément ajouté (backtracking)
                chemin.pop()

        results: list[list[int]] = list()

        backtrack(sum_to_attain, 0, [])

        return results
