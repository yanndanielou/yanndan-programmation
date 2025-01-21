from typing import List

def trouver_combinations(liste: List[int], somme: int) -> List[List[int]]:
    def backtrack(reste, index, chemin):
        # Si la somme restante est atteinte, ajouter la combinaison
        if reste == 0:
            resultats.append(list(chemin))
            return
        # Si la somme restante est négative, arrêter
        if reste < 0:
            return

        for i in range(index, len(liste)):
            # Ajouter le nombre actuel au chemin
            chemin.append(liste[i])
            # Appel récursif avec la somme restante mise à jour et index + 1 (pour éviter les répétitions)
            backtrack(reste - liste[i], i, chemin)  # Réutiliser l'élément actuel
            # Retirer l'élément ajouté (backtracking)
            chemin.pop()

    resultats = []
    backtrack(somme, 0, [])  # Appel initial avec un chemin vide
    return resultats

# Exemple d'utilisation
liste = [2, 3, 6, 7]
somme_a_atteindre = 7
combinations = trouver_combinations(liste, somme_a_atteindre)
print(combinations)


liste = [2, 3, 5, 7]
somme_a_atteindre = 7
combinations = trouver_combinations(liste, somme_a_atteindre)
print(combinations)

liste = [1]
somme_a_atteindre = 7
combinations = trouver_combinations(liste, somme_a_atteindre)
print(combinations)