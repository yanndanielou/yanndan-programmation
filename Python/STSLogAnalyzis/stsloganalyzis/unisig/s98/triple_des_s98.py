from __future__ import annotations

from collections.abc import Sequence

MAC_SIZE_IN_BYTES = 8

# ------------------------------------------------------------------------------------
# Arithmétique modulaire et classe Redond
# ------------------------------------------------------------------------------------


A1: int = 12970357
A2: int = 12239417


class Redond:
    """
    Représente un élément de redondance arithmétique sur le double anneau Z/A1 x Z/A2.
    """

    def __init__(self, c1: int = 0, c2: int = 0) -> None:
        self._c1: int = c1
        self._c2: int = c2
        self.recadrer()

    def recadrer(self) -> None:
        self._c1 = self._c1 % A1
        if self._c1 < 0:
            self._c1 += A1

        self._c2 = self._c2 % A2
        if self._c2 < 0:
            self._c2 += A2

    def C1(self) -> int:
        return self._c1

    def C2(self) -> int:
        return self._c2

    def afficher(self) -> None:
        print(f"({self._c1} , {self._c2} )", end="")

    def ajouter(self, r: Redond) -> None:
        self._c1 += r.C1()
        self._c2 += r.C2()
        self.recadrer()

    def multiplier(self, r: Redond) -> None:
        self._c1 *= r.C1()
        self._c2 *= r.C2()
        self.recadrer()

    def clone(self) -> Redond:
        return Redond(self._c1, self._c2)


Bx14_cnx1: Redond = Redond(1762325, 8853225)  # ligne 14 sec_gen_cst_es_tfh_fem_3des_res_connection_1.car
Bx14_cnx2: Redond = Redond(5980613, 5938493)  # ligne 14 sec_gen_cst_es_tfh_fem_3des_res_connection_2.car


class const_PSC:
    """
    Constantes et fonctions de redondance précalculées (Subset-098 / Euroradio).
    """

    def __init__(self) -> None:
        self._Fi_A1: list[int] = [8963117, 11615768, 8834825, 4229672, 5015549, 8741366, 4176911, 3182013, 8674420, 9502541, 4591249, 2936130, 10821750, 4640236, 11498060, 7126637]
        self._Fi_A2: list[int] = [9019133, 6729379, 1155050, 4779184, 7436604, 9339690, 1053442, 5442112, 9016832, 11911906, 9959282, 3503273, 8194484, 9060941, 8337535, 5940019]
        self.moinsRk: Redond = Redond(2726071, 6444477)
        self.tau0: Redond = Redond(4691298, 10686154)
        self.deux_p32: Redond = Redond(1779129, 11171346)  # 2**32
        self.deux_p196: Redond = Redond(280108, 10053949)  # 2**(32*8)

        self._unisig_98_hard: list[Redond] = [
            Redond(3035900, 8152819),  # indice : 0
            Redond(11284085, 7686153),  # indice : 1
            Redond(5454991, 51769),  # indice : 2
            Redond(3885828, 8486416),  # indice : 3
            Redond(7671359, 4549372),  # indice : 4
            Redond(8782678, 8649429),  # indice : 5
            Redond(6826558, 6742661),  # indice : 6
            Redond(2895994, 9987983),  # indice : 7
            Redond(10725748, 7033477),  # indice : 8
            Redond(730811, 5567194),  # indice : 9
            Redond(12151965, 1447932),  # indice : 10
            Redond(7339716, 6245186),  # indice : 11
            Redond(11290486, 6632403),  # indice : 12
            Redond(2398841, 2843654),  # indice : 13
            Redond(11929462, 2392309),  # indice : 14
            Redond(11285806, 8701977),  # indice : 15
            Redond(2023425, 5531246),  # indice : 16
            Redond(8664429, 1183804),  # indice : 17
            Redond(7739424, 8700726),  # indice : 18
            Redond(1050582, 459863),  # indice : 19
        ]

        self.Somme_Fi: list[Redond] = []
        self.Fi: list[Redond] = []
        sum_f: Redond = Redond(0, 0)
        for i in range(16):
            f_val: Redond = Redond(self._Fi_A1[i], self._Fi_A2[i])
            self.Fi.append(f_val)
            sum_f.ajouter(f_val)
            self.Somme_Fi.append(sum_f.clone())

    def tau_i(self, i: int) -> Redond:
        tau: Redond = self.tau0.clone()
        for _ in range(1, i + 1):
            tau.multiplier(self.deux_p32)
        return tau

    def Unisig_98_Hard(self, indice: int) -> Redond:
        assert 0 <= indice < 20
        return self._unisig_98_hard[indice].clone()

    def calculer_redond_tableau8(self, Tab: Sequence[int], Bx_Tab: Redond, reverse: bool = False) -> Redond:
        r: Redond = Bx_Tab.clone()
        for i in range(8):
            j: int = 7 - i if reverse else i
            r_temp: Redond = Redond(Tab[j], Tab[j])
            r_temp.multiplier(self.tau_i(i))
            r_temp.multiplier(self.moinsRk)
            r.ajouter(r_temp)
        return r


# ------------------------------------------------------------------------------------
# Tables S-BOX pour le chiffrement DES standard (FIPS PUB 46-3)
# ------------------------------------------------------------------------------------

SBOX_1: list[list[int]] = [
    [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
    [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
    [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
    [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
]
SBOX_2: list[list[int]] = [
    [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
    [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
    [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
    [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
]
SBOX_3: list[list[int]] = [
    [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
    [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
    [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
    [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
]
SBOX_4: list[list[int]] = [
    [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
    [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
    [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
    [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
]
SBOX_5: list[list[int]] = [
    [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
    [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
    [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
    [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
]
SBOX_6: list[list[int]] = [
    [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
    [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
    [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
    [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
]
SBOX_7: list[list[int]] = [
    [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
    [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
    [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
    [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
]
SBOX_8: list[list[int]] = [
    [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
    [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
    [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
    [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
]

SBOX_TABLES: list[list[list[int]]] = [[], SBOX_1, SBOX_2, SBOX_3, SBOX_4, SBOX_5, SBOX_6, SBOX_7, SBOX_8]  # Indexation 1 à 8


# ------------------------------------------------------------------------------------
# Primitives DES bit-level
# ------------------------------------------------------------------------------------


def des_permuted_choice_1(key_in: Sequence[int], permuted_choice_1: bytearray) -> None:
    permuted_choice_1[0] = (
        (key_in[7] & 0x80) | ((key_in[6] & 0x80) >> 1) | ((key_in[5] & 0x80) >> 2) | ((key_in[4] & 0x80) >> 3) | ((key_in[3] & 0x80) >> 4) | ((key_in[2] & 0x80) >> 5) | ((key_in[1] & 0x80) >> 6)
    )
    permuted_choice_1[1] = (
        (key_in[0] & 0x80) | (key_in[7] & 0x40) | ((key_in[6] & 0x40) >> 1) | ((key_in[5] & 0x40) >> 2) | ((key_in[4] & 0x40) >> 3) | ((key_in[3] & 0x40) >> 4) | ((key_in[2] & 0x40) >> 5)
    )
    permuted_choice_1[2] = (
        ((key_in[1] & 0x40) << 1) | (key_in[0] & 0x40) | (key_in[7] & 0x20) | ((key_in[6] & 0x20) >> 1) | ((key_in[5] & 0x20) >> 2) | ((key_in[4] & 0x20) >> 3) | ((key_in[3] & 0x20) >> 4)
    )
    permuted_choice_1[3] = (
        ((key_in[2] & 0x20) << 2) | ((key_in[1] & 0x20) << 1) | (key_in[0] & 0x20) | (key_in[7] & 0x10) | ((key_in[6] & 0x10) >> 1) | ((key_in[5] & 0x10) >> 2) | ((key_in[4] & 0x10) >> 3)
    )
    permuted_choice_1[4] = (
        ((key_in[7] & 0x02) << 6) | ((key_in[6] & 0x02) << 5) | ((key_in[5] & 0x02) << 4) | ((key_in[4] & 0x02) << 3) | ((key_in[3] & 0x02) << 2) | ((key_in[2] & 0x02) << 1) | (key_in[1] & 0x02)
    )
    permuted_choice_1[5] = (
        ((key_in[0] & 0x02) << 6) | ((key_in[7] & 0x04) << 4) | ((key_in[6] & 0x04) << 3) | ((key_in[5] & 0x04) << 2) | ((key_in[4] & 0x04) << 1) | (key_in[3] & 0x04) | ((key_in[2] & 0x04) >> 1)
    )
    permuted_choice_1[6] = (
        ((key_in[1] & 0x04) << 5) | ((key_in[0] & 0x04) << 4) | ((key_in[7] & 0x08) << 2) | ((key_in[6] & 0x08) << 1) | (key_in[5] & 0x08) | ((key_in[4] & 0x08) >> 1) | ((key_in[3] & 0x08) >> 2)
    )
    permuted_choice_1[7] = (
        ((key_in[2] & 0x08) << 4) | ((key_in[1] & 0x08) << 3) | ((key_in[0] & 0x08) << 2) | (key_in[3] & 0x10) | ((key_in[2] & 0x10) >> 1) | ((key_in[1] & 0x10) >> 2) | ((key_in[0] & 0x10) >> 3)
    )


def des_left_shift(des_shift_in: bytearray) -> None:
    # Shift C0
    shift_temp3: int = 0x02 if (des_shift_in[3] & 0x80) else 0x00
    shift_temp2: int = 0x02 if (des_shift_in[2] & 0x80) else 0x00
    shift_temp1: int = 0x02 if (des_shift_in[1] & 0x80) else 0x00
    shift_temp0: int = 0x02 if (des_shift_in[0] & 0x80) else 0x00

    des_shift_in[3] = (des_shift_in[3] << 1) & 0xFF
    des_shift_in[2] = (des_shift_in[2] << 1) & 0xFF
    des_shift_in[1] = (des_shift_in[1] << 1) & 0xFF
    des_shift_in[0] = (des_shift_in[0] << 1) & 0xFF

    des_shift_in[0] |= shift_temp1
    des_shift_in[1] |= shift_temp2
    des_shift_in[2] |= shift_temp3
    des_shift_in[3] |= shift_temp0

    # Shift L0
    shift_temp3 = 0x02 if (des_shift_in[7] & 0x80) else 0x00
    shift_temp2 = 0x02 if (des_shift_in[6] & 0x80) else 0x00
    shift_temp1 = 0x02 if (des_shift_in[5] & 0x80) else 0x00
    shift_temp0 = 0x02 if (des_shift_in[4] & 0x80) else 0x00

    des_shift_in[7] = (des_shift_in[7] << 1) & 0xFF
    des_shift_in[6] = (des_shift_in[6] << 1) & 0xFF
    des_shift_in[5] = (des_shift_in[5] << 1) & 0xFF
    des_shift_in[4] = (des_shift_in[4] << 1) & 0xFF

    des_shift_in[4] |= shift_temp1
    des_shift_in[5] |= shift_temp2
    des_shift_in[6] |= shift_temp3
    des_shift_in[7] |= shift_temp0


def DES_Permuted_Choice_2(Key_In: Sequence[int], Permuted_Choice_2: bytearray, offset: int = 0) -> None:
    Permuted_Choice_2[offset + 0] = (
        ((Key_In[1] & 0x02) << 6) | ((Key_In[2] & 0x20) << 1) | ((Key_In[1] & 0x10) << 1) | ((Key_In[3] & 0x20) >> 1) | ((Key_In[0] & 0x80) >> 4) | ((Key_In[0] & 0x08) >> 1)
    )
    Permuted_Choice_2[offset + 1] = (
        ((Key_In[0] & 0x20) << 2) | ((Key_In[3] & 0x03) << 5) | ((Key_In[2] & 0x80) >> 2) | ((Key_In[0] & 0x04) << 2) | ((Key_In[2] & 0x02) << 2) | ((Key_In[1] & 0x20) >> 3)
    )
    Permuted_Choice_2[offset + 2] = ((Key_In[3] & 0x40) << 1) | ((Key_In[2] & 0x08) << 3) | ((Key_In[1] & 0x08) << 2) | (Key_In[0] & 0x10) | (Key_In[3] & 0x08) | ((Key_In[1] & 0x80) >> 5)
    Permuted_Choice_2[offset + 3] = (
        ((Key_In[2] & 0x40) << 1) | ((Key_In[0] & 0x02) << 5) | ((Key_In[3] & 0x04) << 3) | ((Key_In[2] & 0x04) << 2) | ((Key_In[1] & 0x04) << 1) | ((Key_In[0] & 0x40) >> 4)
    )
    Permuted_Choice_2[offset + 4] = ((Key_In[5] & 0x04) << 5) | ((Key_In[7] & 0x20) << 1) | (Key_In[4] & 0x20) | ((Key_In[5] & 0x40) >> 2) | (Key_In[6] & 0x08) | (Key_In[7] & 0x04)
    Permuted_Choice_2[offset + 5] = ((Key_In[4] & 0x40) << 1) | ((Key_In[5] & 0x08) << 3) | ((Key_In[7] & 0x40) >> 1) | ((Key_In[6] & 0x20) >> 1) | (Key_In[4] & 0x08) | (Key_In[6] & 0x04)
    Permuted_Choice_2[offset + 6] = (
        ((Key_In[6] & 0x40) << 1) | ((Key_In[6] & 0x02) << 5) | ((Key_In[5] & 0x10) << 1) | ((Key_In[7] & 0x02) << 3) | ((Key_In[4] & 0x04) << 1) | ((Key_In[7] & 0x10) >> 2)
    )
    Permuted_Choice_2[offset + 7] = (
        ((Key_In[6] & 0x10) << 3) | ((Key_In[5] & 0x02) << 5) | ((Key_In[7] & 0x80) >> 2) | ((Key_In[5] & 0x80) >> 3) | ((Key_In[4] & 0x80) >> 4) | ((Key_In[4] & 0x10) >> 2)
    )


def des_initial_permutation(Input: Sequence[int], Output: bytearray) -> None:
    Output[0] = (
        ((Input[7] & 0x40) << 1)
        | (Input[6] & 0x40)
        | ((Input[5] & 0x40) >> 1)
        | ((Input[4] & 0x40) >> 2)
        | ((Input[3] & 0x40) >> 3)
        | ((Input[2] & 0x40) >> 4)
        | ((Input[1] & 0x40) >> 5)
        | ((Input[0] & 0x40) >> 6)
    )
    Output[1] = (
        ((Input[7] & 0x10) << 3)
        | ((Input[6] & 0x10) << 2)
        | ((Input[5] & 0x10) << 1)
        | (Input[4] & 0x10)
        | ((Input[3] & 0x10) >> 1)
        | ((Input[2] & 0x10) >> 2)
        | ((Input[1] & 0x10) >> 3)
        | ((Input[0] & 0x10) >> 4)
    )
    Output[2] = (
        ((Input[7] & 0x04) << 5)
        | ((Input[6] & 0x04) << 4)
        | ((Input[5] & 0x04) << 3)
        | ((Input[4] & 0x04) << 2)
        | ((Input[3] & 0x04) << 1)
        | (Input[2] & 0x04)
        | ((Input[1] & 0x04) >> 1)
        | ((Input[0] & 0x04) >> 2)
    )
    Output[3] = (
        ((Input[7] & 0x01) << 7)
        | ((Input[6] & 0x01) << 6)
        | ((Input[5] & 0x01) << 5)
        | ((Input[4] & 0x01) << 4)
        | ((Input[3] & 0x01) << 3)
        | ((Input[2] & 0x01) << 2)
        | ((Input[1] & 0x01) << 1)
        | (Input[0] & 0x01)
    )
    Output[4] = (
        (Input[7] & 0x80)
        | ((Input[6] & 0x80) >> 1)
        | ((Input[5] & 0x80) >> 2)
        | ((Input[4] & 0x80) >> 3)
        | ((Input[3] & 0x80) >> 4)
        | ((Input[2] & 0x80) >> 5)
        | ((Input[1] & 0x80) >> 6)
        | ((Input[0] & 0x80) >> 7)
    )
    Output[5] = (
        ((Input[7] & 0x20) << 2)
        | ((Input[6] & 0x20) << 1)
        | (Input[5] & 0x20)
        | ((Input[4] & 0x20) >> 1)
        | ((Input[3] & 0x20) >> 2)
        | ((Input[2] & 0x20) >> 3)
        | ((Input[1] & 0x20) >> 4)
        | ((Input[0] & 0x20) >> 5)
    )
    Output[6] = (
        ((Input[7] & 0x08) << 4)
        | ((Input[6] & 0x08) << 3)
        | ((Input[5] & 0x08) << 2)
        | ((Input[4] & 0x08) << 1)
        | (Input[3] & 0x08)
        | ((Input[2] & 0x08) >> 1)
        | ((Input[1] & 0x08) >> 2)
        | ((Input[0] & 0x08) >> 3)
    )
    Output[7] = (
        ((Input[7] & 0x02) << 6)
        | ((Input[6] & 0x02) << 5)
        | ((Input[5] & 0x02) << 4)
        | ((Input[4] & 0x02) << 3)
        | ((Input[3] & 0x02) << 2)
        | ((Input[2] & 0x02) << 1)
        | (Input[1] & 0x02)
        | ((Input[0] & 0x02) >> 1)
    )


def des_inverse_initial_permutation(Input: Sequence[int], Output: bytearray) -> None:
    Output[0] = (
        ((Input[4] & 0x01) << 7)
        | ((Input[0] & 0x01) << 6)
        | ((Input[5] & 0x01) << 5)
        | ((Input[1] & 0x01) << 4)
        | ((Input[6] & 0x01) << 3)
        | ((Input[2] & 0x01) << 2)
        | ((Input[7] & 0x01) << 1)
        | (Input[3] & 0x01)
    )
    Output[1] = (
        ((Input[4] & 0x02) << 6)
        | ((Input[0] & 0x02) << 5)
        | ((Input[5] & 0x02) << 4)
        | ((Input[1] & 0x02) << 3)
        | ((Input[6] & 0x02) << 2)
        | ((Input[2] & 0x02) << 1)
        | (Input[7] & 0x02)
        | ((Input[3] & 0x02) >> 1)
    )
    Output[2] = (
        ((Input[4] & 0x04) << 5)
        | ((Input[0] & 0x04) << 4)
        | ((Input[5] & 0x04) << 3)
        | ((Input[1] & 0x04) << 2)
        | ((Input[6] & 0x04) << 1)
        | (Input[2] & 0x04)
        | ((Input[7] & 0x04) >> 1)
        | ((Input[3] & 0x04) >> 2)
    )
    Output[3] = (
        ((Input[4] & 0x08) << 4)
        | ((Input[0] & 0x08) << 3)
        | ((Input[5] & 0x08) << 2)
        | ((Input[1] & 0x08) << 1)
        | (Input[6] & 0x08)
        | ((Input[2] & 0x08) >> 1)
        | ((Input[7] & 0x08) >> 2)
        | ((Input[3] & 0x08) >> 3)
    )
    Output[4] = (
        ((Input[4] & 0x10) << 3)
        | ((Input[0] & 0x10) << 2)
        | ((Input[5] & 0x10) << 1)
        | (Input[1] & 0x10)
        | ((Input[6] & 0x10) >> 1)
        | ((Input[2] & 0x10) >> 2)
        | ((Input[7] & 0x10) >> 3)
        | ((Input[3] & 0x10) >> 4)
    )
    Output[5] = (
        ((Input[4] & 0x20) << 2)
        | ((Input[0] & 0x20) << 1)
        | (Input[5] & 0x20)
        | ((Input[1] & 0x20) >> 1)
        | ((Input[6] & 0x20) >> 2)
        | ((Input[2] & 0x20) >> 3)
        | ((Input[7] & 0x20) >> 4)
        | ((Input[3] & 0x20) >> 5)
    )
    Output[6] = (
        ((Input[4] & 0x40) << 1)
        | (Input[0] & 0x40)
        | ((Input[5] & 0x40) >> 1)
        | ((Input[1] & 0x40) >> 2)
        | ((Input[6] & 0x40) >> 3)
        | ((Input[2] & 0x40) >> 4)
        | ((Input[7] & 0x40) >> 5)
        | ((Input[3] & 0x40) >> 6)
    )
    Output[7] = (
        (Input[4] & 0x80)
        | ((Input[0] & 0x80) >> 1)
        | ((Input[5] & 0x80) >> 2)
        | ((Input[1] & 0x80) >> 3)
        | ((Input[6] & 0x80) >> 4)
        | ((Input[2] & 0x80) >> 5)
        | ((Input[7] & 0x80) >> 6)
        | ((Input[3] & 0x80) >> 7)
    )


def DES_Function_P(Input: Sequence[int], Output: bytearray) -> None:
    Output[0] = ((Input[1] & 0x01) << 7) | ((Input[0] & 0x02) << 5) | ((Input[2] & 0x18) << 1) | (Input[3] & 0x08) | ((Input[1] & 0x10) >> 2) | ((Input[3] & 0x10) >> 3) | ((Input[2] & 0x80) >> 7)
    Output[1] = (
        (Input[0] & 0x80) | ((Input[1] & 0x02) << 5) | ((Input[2] & 0x02) << 4) | ((Input[3] & 0x40) >> 2) | (Input[0] & 0x08) | ((Input[2] & 0x40) >> 4) | (Input[3] & 0x02) | ((Input[1] & 0x40) >> 6)
    )
    Output[2] = (
        ((Input[0] & 0x40) << 1)
        | ((Input[0] & 0x01) << 6)
        | ((Input[2] & 0x01) << 5)
        | ((Input[1] & 0x04) << 2)
        | ((Input[3] & 0x01) << 3)
        | ((Input[3] & 0x20) >> 3)
        | ((Input[0] & 0x20) >> 4)
        | ((Input[1] & 0x80) >> 7)
    )
    Output[3] = (
        ((Input[2] & 0x20) << 2)
        | ((Input[1] & 0x08) << 3)
        | ((Input[3] & 0x04) << 3)
        | ((Input[0] & 0x04) << 2)
        | ((Input[2] & 0x04) << 1)
        | ((Input[1] & 0x20) >> 3)
        | ((Input[0] & 0x10) >> 3)
        | ((Input[3] & 0x80) >> 7)
    )


def DES_Function_E(Input: Sequence[int], Output: bytearray) -> None:
    Output[0] = ((Input[0] >> 1) & 0x7C) | ((Input[3] & 0x01) << 7)
    Output[1] = ((Input[0] << 3) & 0xF8) | ((Input[1] & 0x80) >> 5)
    Output[2] = ((Input[1] >> 1) & 0x7C) | ((Input[0] & 0x01) << 7)
    Output[3] = ((Input[1] << 3) & 0xF8) | ((Input[2] & 0x80) >> 5)
    Output[4] = ((Input[2] >> 1) & 0x7C) | ((Input[1] & 0x01) << 7)
    Output[5] = ((Input[2] << 3) & 0xF8) | ((Input[3] & 0x80) >> 5)
    Output[6] = ((Input[3] >> 1) & 0x7C) | ((Input[2] & 0x01) << 7)
    Output[7] = ((Input[3] << 3) & 0xF8) | ((Input[0] & 0x80) >> 5)


def DES_Function_XOR(XOR_1: bytearray, XOR_2: Sequence[int], offset1: int = 0, offset2: int = 0) -> None:
    for i in range(4):
        XOR_1[offset1 + i] ^= XOR_2[offset2 + i]


def DES_SBox(Raw: int, Column: int, Box_Number: int) -> int:
    return SBOX_TABLES[Box_Number][Raw][Column]


def DES_Function_F(DES_Buffer: bytearray, Key: Sequence[int]) -> None:
    F_Temp: bytearray = bytearray(8)
    DES_Function_E(DES_Buffer, F_Temp)
    DES_Function_XOR(F_Temp, Key, offset1=0, offset2=0)
    DES_Function_XOR(F_Temp, Key, offset1=4, offset2=4)

    for i in range(1, 9):
        raw: int = ((F_Temp[i - 1] & 0x04) >> 2) | ((F_Temp[i - 1] & 0x80) >> 6)
        column: int = (F_Temp[i - 1] & 0x78) >> 3
        F_Temp[i - 1] = DES_SBox(raw, column, i)

    # Convertit 8 x 1 quartet en 4 x 2 quartets
    for i in range(4):
        F_Temp[2 * i] = (F_Temp[2 * i] << 4) & 0xFF
        F_Temp[2 * i] |= F_Temp[(2 * i) + 1]

    F_Temp[1] = F_Temp[2]
    F_Temp[2] = F_Temp[4]
    F_Temp[3] = F_Temp[6]

    DES_Function_P(F_Temp, DES_Buffer)


def des_key_scheduling(Key: Sequence[int], Key_Schedule_1: bytearray, Key_Schedule_2: bytearray) -> None:
    permuted_choice_1: bytearray = bytearray(8)
    des_permuted_choice_1(Key, permuted_choice_1)

    key_index: int = 1
    offset_ks1: int = 0
    while True:
        des_left_shift(permuted_choice_1)
        if key_index != 1 and key_index != 2:
            des_left_shift(permuted_choice_1)
        DES_Permuted_Choice_2(permuted_choice_1, Key_Schedule_1, offset=offset_ks1)
        offset_ks1 += 8
        key_index += 1
        if key_index > 8:
            break

    offset_ks2: int = 0
    while True:
        des_left_shift(permuted_choice_1)
        if key_index != 9 and key_index != 16:
            des_left_shift(permuted_choice_1)
        DES_Permuted_Choice_2(permuted_choice_1, Key_Schedule_2, offset=offset_ks2)
        offset_ks2 += 8
        key_index += 1
        if key_index > 16:
            break


def des_round_enc(DES_Buffer: bytearray, Key_Schedule_1: bytearray, Key_Schedule_2: bytearray) -> None:
    DES_Buffer_Left: bytearray = bytearray(DES_Buffer[:4])
    DES_Buffer_Right: bytearray = bytearray(DES_Buffer[4:8])
    DES_Buffer_Temp1: bytearray = bytearray(4)
    DES_Buffer_Temp2: bytearray = bytearray(4)
    Round_Key: bytearray = bytearray(8)

    ks1_offset: int = 0
    for _ in range(1, 9):
        Round_Key[:] = Key_Schedule_1[ks1_offset : ks1_offset + 8]
        ks1_offset += 8
        DES_Buffer_Temp1[:] = DES_Buffer_Left
        DES_Buffer_Left[:] = DES_Buffer_Right
        DES_Buffer_Temp2[:] = DES_Buffer_Right
        DES_Function_F(DES_Buffer_Temp2, Round_Key)
        DES_Function_XOR(DES_Buffer_Temp1, DES_Buffer_Temp2)
        DES_Buffer_Right[:] = DES_Buffer_Temp1

    ks2_offset: int = 0
    for _ in range(1, 9):
        Round_Key[:] = Key_Schedule_2[ks2_offset : ks2_offset + 8]
        ks2_offset += 8
        DES_Buffer_Temp1[:] = DES_Buffer_Left
        DES_Buffer_Left[:] = DES_Buffer_Right
        DES_Buffer_Temp2[:] = DES_Buffer_Right
        DES_Function_F(DES_Buffer_Temp2, Round_Key)
        DES_Function_XOR(DES_Buffer_Temp1, DES_Buffer_Temp2)
        DES_Buffer_Right[:] = DES_Buffer_Temp1

    DES_Buffer[:4] = DES_Buffer_Left
    DES_Buffer[4:8] = DES_Buffer_Right


def des_round_dec(DES_Buffer: bytearray, Key_Schedule_1: bytearray, Key_Schedule_2: bytearray) -> None:
    DES_Buffer_Left: bytearray = bytearray(DES_Buffer[4:8])
    DES_Buffer_Right: bytearray = bytearray(DES_Buffer[:4])
    DES_Buffer_Temp1: bytearray = bytearray(4)
    DES_Buffer_Temp2: bytearray = bytearray(4)
    Round_Key: bytearray = bytearray(8)

    ks2_offset: int = 56
    ks1_offset: int = 56

    for _ in range(1, 9):
        Round_Key[:] = Key_Schedule_2[ks2_offset : ks2_offset + 8]
        ks2_offset -= 8
        DES_Buffer_Temp1[:] = DES_Buffer_Right
        DES_Buffer_Right[:] = DES_Buffer_Left
        DES_Buffer_Temp2[:] = DES_Buffer_Left
        DES_Function_F(DES_Buffer_Temp2, Round_Key)
        DES_Function_XOR(DES_Buffer_Temp1, DES_Buffer_Temp2)
        DES_Buffer_Left[:] = DES_Buffer_Temp1

    for _ in range(1, 9):
        Round_Key[:] = Key_Schedule_1[ks1_offset : ks1_offset + 8]
        ks1_offset -= 8
        DES_Buffer_Temp1[:] = DES_Buffer_Right
        DES_Buffer_Right[:] = DES_Buffer_Left
        DES_Buffer_Temp2[:] = DES_Buffer_Left
        DES_Function_F(DES_Buffer_Temp2, Round_Key)
        DES_Function_XOR(DES_Buffer_Temp1, DES_Buffer_Temp2)
        DES_Buffer_Left[:] = DES_Buffer_Temp1

    DES_Buffer[:4] = DES_Buffer_Left
    DES_Buffer[4:8] = DES_Buffer_Right


def XOR_Byte2Byte(Source: Sequence[int], Dest: bytearray, SzData: int) -> None:
    for i in range(SzData):
        Dest[i] ^= Source[i]


def des_dec(input_bytes: Sequence[int], output: bytearray, key: Sequence[int]) -> None:
    des_work_buffer: bytearray = bytearray(8)
    key_schedule_1: bytearray = bytearray(64)
    key_schedule_2: bytearray = bytearray(64)

    des_key_scheduling(key, key_schedule_1, key_schedule_2)
    des_initial_permutation(input_bytes, des_work_buffer)
    des_round_dec(des_work_buffer, key_schedule_1, key_schedule_2)
    des_inverse_initial_permutation(des_work_buffer, output)


def des_enc(Input: Sequence[int], Output: bytearray, Key: Sequence[int]) -> None:
    des_work_buffer: bytearray = bytearray(8)
    key_schedule_1: bytearray = bytearray(64)
    key_schedule_2: bytearray = bytearray(64)
    des_temp: bytearray = bytearray(4)

    des_initial_permutation(Input, des_work_buffer)
    des_key_scheduling(Key, key_schedule_1, key_schedule_2)
    des_round_enc(des_work_buffer, key_schedule_1, key_schedule_2)

    # Swap R16 and L16
    des_temp[:] = des_work_buffer[:4]
    des_work_buffer[:4] = des_work_buffer[4:8]
    des_work_buffer[4:8] = des_temp

    des_inverse_initial_permutation(des_work_buffer, Output)


# ------------------------------------------------------------------------------------
# Fonctions d'affichage et calcul CBC-MAC
# ------------------------------------------------------------------------------------


def convert_mac_to_string_of_hexas(mac: bytearray) -> str:
    return f"{mac[0]:x} {mac[1]:x} {mac[2]:x} {mac[3]:x} {mac[4]:x} {mac[5]:x} {mac[6]:x} {mac[7]:x}"


def afficher_64bits(s: str, bytes_array: Sequence[int]) -> None:
    print(s, end="")
    for i in range(8):
        print(f"{int(bytes_array[i])} ", end="")
    print()


def afficher_hexa(s: str, Tab: Sequence[int]) -> None:
    print(s, end="")
    print(f"16#{Tab[0]:x}_{Tab[1]:x}#, 16#{Tab[2]:x}_{Tab[3]:x}#, 16#{Tab[4]:x}_{Tab[5]:x}#, 16#{Tab[6]:x}_{Tab[7]:x}#")


def calcul_mac_n_Blocks(blocks: Sequence[int], k1: Sequence[int], k2: Sequence[int], k3: Sequence[int], verbose: bool = False) -> bytearray:

    nb_bloks = len(blocks) // 8
    output = bytearray(MAC_SIZE_IN_BYTES)
    current_block: bytearray = bytearray(8)
    byte_index: int = 0
    for i in range(nb_bloks):
        for j in range(8):
            current_block[j] = blocks[byte_index]
            byte_index += 1
        if verbose:
            afficher_64bits("current message block : ", current_block)
        if i > 0:
            XOR_Byte2Byte(current_block, output, 8)
            if verbose:
                afficher_64bits("Apres XOR avec le block precedent ==> ", output)
            des_enc(output, output, k1)
        else:
            des_enc(current_block, output, k1)
        if verbose:
            afficher_64bits("Apres cryptage par Ks1 ==> ", output)

    des_dec(output, output, k2)
    if verbose:
        afficher_64bits("Apres decryptage par Ks2 ==> ", output)
    des_enc(output, output, k3)
    if verbose:
        afficher_64bits("Apres cryptage par Ks3 ==> ", output)
        print(f"CBC-MAC         = {output[0]:x} {output[1]:x} {output[2]:x} {output[3]:x} {output[4]:x} {output[5]:x} {output[6]:x} {output[7]:x}")
    return output


# ------------------------------------------------------------------------------------
# Classe de session Connection_U98
# ------------------------------------------------------------------------------------


class ConnectionUnisig98:
    def __init__(
        self,
        authentication_key_kmac_1: Sequence[int],
        authentication_key_kmac_2: Sequence[int],
        authentication_key_kmac_3: Sequence[int],
        initiator_etcs_id: int,
        responder_etcs_id: int,
        resp_type: int = 192,
        is_cnx1: bool = True,
    ) -> None:
        self.cst_PSC: const_PSC = const_PSC()
        self.authentication_key_kmac_1: bytearray = bytearray(authentication_key_kmac_1[:8])
        self.authentication_key_kmac_2: bytearray = bytearray(authentication_key_kmac_2[:8])
        self.authentication_key_kmac_3: bytearray = bytearray(authentication_key_kmac_3[:8])

        self.session_key_1: bytearray = bytearray(8)
        self.session_key_2: bytearray = bytearray(8)
        self.session_key_3: bytearray = bytearray(8)

        self.initiator_etcs_id: int = initiator_etcs_id
        self.responder_etcs_id: int = responder_etcs_id
        self.responder_type: int = resp_type
        self.is_connnection1: bool = is_cnx1

        self.random_a: bytearray = bytearray(8)
        self.random_b: bytearray = bytearray(8)

    def compute_session_key(self, random_number: Sequence[int], session_key: bytearray, reverse: bool) -> None:
        if reverse:
            des_enc(random_number, session_key, self.authentication_key_kmac_3)
            des_dec(session_key, session_key, self.authentication_key_kmac_2)
            des_enc(session_key, session_key, self.authentication_key_kmac_1)
        else:
            des_enc(random_number, session_key, self.authentication_key_kmac_1)
            des_dec(session_key, session_key, self.authentication_key_kmac_2)
            des_enc(session_key, session_key, self.authentication_key_kmac_3)

    def start_session(self, random_number_a: Sequence[int], random_number_b: Sequence[int], verbose: bool = False) -> None:
        ral_l_rb_l: bytearray = bytearray(8)
        ra_r_rb_r: bytearray = bytearray(8)

        for i in range(4):
            self.random_a[i] = random_number_a[i]
            self.random_b[i] = random_number_b[i]
            ral_l_rb_l[i] = random_number_a[i]
            ral_l_rb_l[i + 4] = random_number_b[i]

            self.random_a[i + 4] = random_number_a[i + 4]
            self.random_b[i + 4] = random_number_b[i + 4]
            ra_r_rb_r[i] = random_number_a[i + 4]
            ra_r_rb_r[i + 4] = random_number_b[i + 4]

        self.compute_session_key(ral_l_rb_l, self.session_key_1, False)
        self.compute_session_key(ra_r_rb_r, self.session_key_2, False)
        self.compute_session_key(ral_l_rb_l, self.session_key_3, True)

        bx_r: Redond
        if self.is_connnection1:
            if verbose:
                print("Connection numero 1 :")
            bx_r = self.cst_PSC.Unisig_98_Hard(3)
        else:
            if verbose:
                print("Connection numero 2 :")
            bx_r = self.cst_PSC.Unisig_98_Hard(13)

        if verbose:
            print()
            afficher_64bits("Session Key1        : ", self.session_key_1)
            afficher_64bits("Session Key2        : ", self.session_key_2)
            afficher_64bits("Session Key3        : ", self.session_key_3)
            print()

        r1_redond: Redond = self.cst_PSC.calculer_redond_tableau8(ral_l_rb_l, bx_r, True)
        r2_redond: Redond = self.cst_PSC.calculer_redond_tableau8(ra_r_rb_r, bx_r, True)

        if verbose:
            afficher_hexa("Random number 1 :", ral_l_rb_l)
            print(" Redond Random1 = ", end="")
            r1_redond.afficher()
            print()
            afficher_hexa("Random number 2 :", ra_r_rb_r)
            print(" Redond Random2 = ", end="")
            r2_redond.afficher()
            print()
            afficher_hexa("Random number 3 :", ral_l_rb_l)  # r3 = r1
            print(" Redond Random3 = ", end="")
            r1_redond.afficher()
            print()
            print("\nconnection etablie ...\n")

    def compute_input_mac_au2(self, verbose: bool = False) -> bytearray:
        if verbose:
            print("computing G_INPUT_MAC_AU2 ", end="")
            if self.is_connnection1:
                print("for connection 1", end="")
            else:
                print("for connection 2", end="")
            print(" ...")

        AU2_bloc1: bytearray = bytearray(8)
        AU2_bloc2: bytearray = bytearray(8)
        AU2_bloc3: bytearray = bytearray(8)
        AU2_bloc4: bytearray = bytearray(8)

        Initiator_Etcs_Id: bytearray = bytearray(3)
        Responder_Etcs_Id: bytearray = bytearray(3)

        remaining_value1: int = self.initiator_etcs_id
        remaining_value2: int = self.responder_etcs_id
        for i in range(3):
            Initiator_Etcs_Id[2 - i] = remaining_value1 % 256
            remaining_value1 //= 256
            Responder_Etcs_Id[2 - i] = remaining_value2 % 256
            remaining_value2 //= 256

        # Creation de G_MAC_INPUT_AU2
        AU2_bloc1[0] = 0
        AU2_bloc1[1] = 27  # longueur
        for i in range(3):
            AU2_bloc1[i + 2] = Initiator_Etcs_Id[i]  # DA
        AU2_bloc1[5] = self.responder_type + 5  # ETY + MTI + DF
        for i in range(3):  # SA
            if i + 6 < 8:
                AU2_bloc1[i + 6] = Responder_Etcs_Id[i]
            else:
                AU2_bloc2[i - 2] = Responder_Etcs_Id[i]

        AU2_bloc2[1] = 1
        for i in range(8):  # RA
            if i + 2 < 8:
                AU2_bloc2[i + 2] = self.random_a[i]
            else:
                AU2_bloc3[i - 6] = self.random_a[i]

        for i in range(8):  # RB
            if i + 2 < 8:
                AU2_bloc3[i + 2] = self.random_b[i]
            else:
                AU2_bloc4[i - 6] = self.random_b[i]

        for i in range(3):
            AU2_bloc4[i + 2] = Initiator_Etcs_Id[i]  # DA (=B)
        for i in range(5, 8):
            AU2_bloc4[i] = 0  # padding

        if verbose:
            afficher_64bits("bloc1 (msg AU2) = ", AU2_bloc1)
            afficher_64bits("bloc2 (msg AU2) = ", AU2_bloc2)
            afficher_64bits("bloc3 (msg AU2) = ", AU2_bloc3)
            afficher_64bits("bloc4 (msg AU2) = ", AU2_bloc4)

        return calcul_mac_n_Blocks(AU2_bloc1 + AU2_bloc2 + AU2_bloc3 + AU2_bloc4, self.session_key_1, self.session_key_2, self.session_key_3)

    def compute_mac_n_blocks(self, blocks: Sequence[int], verbose: bool = False) -> bytearray:
        assert len(blocks) % 8 == 0
        nb_blocks = len(blocks) // 8
        if verbose:
            print(f"CALCUL de MAC à {nb_blocks} blocs avec N={nb_blocks}", end="")
        return calcul_mac_n_Blocks(blocks, self.session_key_1, self.session_key_2, self.session_key_3, verbose)
