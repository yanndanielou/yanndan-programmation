def CBTC_Addr_Mcast(EQUI_ID: int, Subnet_Prefix: str) -> str:
    # Définition des parties Class_C et Class_D
    tmp = EQUI_ID

    # Classe C : Décalage des bits vers la droite
    Class_C_Part = tmp >> 8

    # Classe D : Utilisation d'un masque pour les 8 derniers bits
    Class_D_Part = tmp & 0xFF

    # Concaténation des parties pour former l'adresse multicast
    CBTC_Addr_Mcast = f"{Subnet_Prefix}.{Class_C_Part}.{Class_D_Part}"
    return CBTC_Addr_Mcast


def generate_ip_address(prefix: str, mask: str, number: int) -> str:
    """
    Génère une adresse IP valide en combinant un préfixe donné, un masque et un numéro.

    Arguments:
    prefix (str) -- Le préfixe de l'adresse IP (ex : "192.168.1").
    masque (str) -- Le masque réseau (ex : "255.255.255.0"). Ce masque définit les parties fixes de l'IP.
    numero (int) -- Numéro d'hôte (ex : 42).

    Retourne:
    str -- Adresses IP valide sous forme de chaîne (ex : "192.168.1.42").
    """
    # Validation des entrées (léger contrôle du préfix)
    if not prefix.count(".") == 2 or not all(0 <= int(octet) <= 255 for octet in prefix.split(".")):
        raise ValueError("Le préfixe n'est pas valide!")

    if not number >= 0 or number > 255:
        raise ValueError("Le numéro doit être compris entre 0 et 255!")

    ip_complete = f"{prefix}.{number}"
    return ip_complete


# Exemple d'appel
adresse_ip = generate_ip_address("192.168.1", "255.255.255.0", 42)
print(adresse_ip)  # Affiche : 192.168.1.42
