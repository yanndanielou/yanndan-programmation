import ipaddress
from warnings import deprecated


def generate_ip_address(initial_ip_address: str, mask: str, number: int) -> str:
    """
    Incrémente l'adresse IP initiale de `number` tout en vérifiant que
    le masque reste applicable.

    Args:
        initial_ip_address (str): L'adresse IP initiale (ex: '192.168.0.1').
        mask (str): Le masque de sous-réseau (ex: '255.255.255.0').
        number (int): Le nombre d'incréments appliqués à l'adresse IP.

    Returns:
        str: La nouvelle adresse IP après incrémentation.

    Raises:
        ValueError: Si la nouvelle adresse IP dépasse le masque ou si
                    les arguments sont invalides.
    """

    try:
        # Crée les objets IP pour la vérification et l'incrémentation
        network = ipaddress.IPv4Network(f"{initial_ip_address}/{mask}", strict=False)
        current_ip = ipaddress.IPv4Address(initial_ip_address)

        # Incrémente l'adresse IP
        new_ip = current_ip + number

        # Vérifie si la nouvelle adresse IP appartient au réseau
        if new_ip not in network:
            raise ValueError(f"L'adresse IP {new_ip} dépasse le réseau défini par le masque {mask}.")

        return str(new_ip)

    except ipaddress.AddressValueError:
        raise ValueError("Les arguments spécifiés ne sont pas des adresses IP valides.")


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


@deprecated("Kept just in case")
def generate_ip_address_old_does_not_work(prefix: str, mask: str, number: int) -> str:
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
