def generate_16_mask_ip_address(number: int, subnet_prefix: str) -> str:
    # Définition des parties Class_C et Class_D
    tmp = number

    # Classe C : Décalage des bits vers la droite
    Class_C_Part = tmp >> 8

    # Classe D : Utilisation d'un masque pour les 8 derniers bits
    Class_D_Part = tmp & 0xFF

    # Concaténation des parties pour former l'adresse multicast
    result = f"{subnet_prefix}.{Class_C_Part}.{Class_D_Part}"
    return result


def generate_ip_address(prefix: str, mask: str, number: int) -> str:
    """
    Génère une adresse IP valide à partir d'un préfixe, d'un masque et d'un numéro.

    Arguments:
    prefix (str) -- Préfixe de l'adresse IP (ex : "192.168.1").
    masque (str) -- Masque réseau (ex : "255.255.255.0"). Définit les parties fixes de l'adresse.
    numero (int) -- Numéro d'hôte (ex : 42).

    Retourne:
    str -- Adresse IP valide sous forme de chaîne (ex : "192.168.1.42").
    """
    # Découper en octets
    prefix_octets = list(map(int, prefix.split(".")))
    masque_octets = list(map(int, mask.split(".")))

    if len(prefix_octets) != 3 or len(masque_octets) != 4:
        raise ValueError("Le préfixe doit contenir 3 octets et le masque 4 octets.")

    # Valider le numéro
    if number < 0 or number > 255:
        raise ValueError("Le numéro doit être compris entre 0 et 255.")

    # Appliquer le masque pour générer l'adresse IP
    adresse_ip_octets = prefix_octets + [0]  # On étend à 4 octets en ajoutant un 0 temporaire
    for i in range(len(masque_octets)):
        if masque_octets[i] == 255:
            adresse_ip_octets[i] = prefix_octets[i]  # Octet fixe
        elif masque_octets[i] == 0:
            if i == 3:
                adresse_ip_octets[i] = number  # Octet modifiable par le numéro
            else:
                adresse_ip_octets[i] = 0  # Octet modifiable avec une valeur par défaut
        else:
            raise ValueError("Le masque n'est pas supporté (utilisez uniquement 255 ou 0).")

    # Format et retour
    return ".".join(map(str, adresse_ip_octets))
