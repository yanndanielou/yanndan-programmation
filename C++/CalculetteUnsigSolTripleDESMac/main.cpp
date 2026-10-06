#include "kmac_keys.h"
#include <stdio.h>
#include <iostream>
using namespace std;


//------------------------------------------------------------------------------------

long long Calculer_inverse_modulo(long long a, long long p) {
	long long U_prec, U, V_prec, V, X, X_Prec, Y, Y_prec, new_U, new_V;
	U_prec = 1;
	U = 0;
	V_prec = 0;
	V = 1;

	X = a;
	Y = p;

	while (Y != 0) {
		X_Prec = X;
		Y_prec = Y;

		X = Y_prec;
		Y = X_Prec %  Y_prec;
		new_U = U_prec - U * (X_Prec / Y_prec);
		new_V = V_prec - V * (X_Prec / Y_prec);

		U_prec = U;
		V_prec = V;
		U = new_U;
		V = new_V;
	}

	if (X == 1) {
		return U_prec;
	}
	else { return 0; }
}

const int A1 = 12970357;
const int A2 = 12239417;

class Redond {
private:
	long long _c1;
	long long _c2;

	void recadrer() {
		_c1 = _c1 % A1;
		if (_c1 < 0) _c1 += A1;

		_c2 = _c2 % A2;
		if (_c2 < 0) _c2 += A2;
	}

public:
	Redond() { _c1 = 0; _c2 = 0; }
	Redond(long long c1, long long c2)
	{
		_c1 = c1;
		_c2 = c2;
		this->recadrer();
	}

	long long C1() const { return (this->_c1); }
	long long C2() const { return (this->_c2); }

	void afficher() {
		cout << "(" << this->_c1 << " , " << this->_c2 << " )";
	}

	void ajouter(Redond r) {
		_c1 += r.C1();
		_c2 += r.C2();
		this->recadrer();
	}

	void multiplier(Redond r) {
		_c1 *= r.C1();
		_c2 *= r.C2();
		this->recadrer();
	}

	void inverser() {
		_c1 = Calculer_inverse_modulo(_c1, A1);
		_c2 = Calculer_inverse_modulo(_c2, A2);
		this->recadrer();
	}
};

const Redond Bx14_cnx1(1762325, 8853225); // lu à la ligne 14 de sec_gen_cst_es_tfh_fem_3des_res_connection_1.car
const Redond Bx14_cnx2(5980613, 5938493); // lu à la ligne 14 sec_gen_cst_es_tfh_fem_3des_res_connection_2.car


class const_PSC {

private:
	Redond Somme_Fi[16];
	Redond Fi[16];
	const long long Fi_A1[16]{ 8963117,11615768,8834825,4229672,5015549,8741366,4176911,3182013,8674420,9502541,4591249,2936130,10821750,4640236,11498060,7126637 };
	const long long Fi_A2[16]{ 9019133,6729379,1155050,4779184,7436604,9339690,1053442,5442112,9016832,11911906,9959282,3503273,8194484,9060941,8337535,5940019 };
	Redond moinsRk;//(2726071, 6444477);
	Redond tau0;//(4691298, 10686154);
	Redond deux_p32; // 2**32 = (1779129, 11171346);
	Redond deux_p196; // 2**(32*8) = (208108, 10053949)
	const Redond unisig_98_hard[20] = {
				Redond(3035900, 8152819),		// indice :  0
				Redond(11284085, 7686153),		// indice :  1
				  Redond(5454991, 51769),		// indice :  2
				  Redond(3885828, 8486416),		// indice :  3
				  Redond(7671359, 4549372),		// indice :  4
				  Redond(8782678, 8649429),		// indice :  5
				  Redond(6826558, 6742661),		// indice :  6
				  Redond(2895994, 9987983),		// indice :  7
				 Redond(10725748, 7033477),		// indice :  8
				   Redond(730811, 5567194),		// indice :  9
				 Redond(12151965, 1447932),		// indice :  10
				  Redond(7339716, 6245186),		// indice :  11
				 Redond(11290486, 6632403),		// indice :  12
				  Redond(2398841, 2843654),		// indice :  13
				 Redond(11929462, 2392309),		// indice :  14
				 Redond(11285806, 8701977),		// indice :  15
				  Redond(2023425, 5531246),		// indice :  16
				  Redond(8664429, 1183804),		// indice :  17
				  Redond(7739424, 8700726),		// indice :  18
				  Redond(1050582, 459863)		// indice :  19
	};

	const Redond calcul_Bx_N_non_brouille(int id_connection, short int N_value) {
		if (id_connection < 0 or id_connection>1) {
			cout << "Erreur : mauvais id_connection : " << id_connection << " (valeur attendue : 0 ou 1)" << endl;
			return Redond(0, 0);
		}
		if (N_value < 0 or N_value>16) {
			cout << "Erreur : mauvaise valeur pour N : " << N_value << " (valeurs possibles : 1 à 16)" << endl;
			return Redond(0, 0);
		}

		Redond Bxres = Unisig_98_Hard(7); // voir DSL de Sec_Gen_Cst_Es
		Redond BxK3 = Unisig_98_Hard(0 + 10 * id_connection); // id_connection=0 => connection 1, utiliser l'indice 0, sinon connection 1 => utiliser l'indice 10
		// Bx_in est un alias pour Bxd
		Redond Bxd = Unisig_98_Hard(6 + 10 * id_connection); // id_connection=0 => connection 1, utiliser l'indice 6, sinon connection 1 => utiliser l'indice 16

		Redond calcul1 = Redond(1, 1);
		for (int i = 1;i <= N_value + 2;i++) calcul1.multiplier(deux_p196); // 2**(32*8*(N+2))
		calcul1.inverser();// 1/ [ 2**(32*8*(N+2)) ]
		calcul1.multiplier(Bxd); // Bx_d / [ 2**(32*8*(N+2)) ]
		//cout << "Bx_in/[2^(32*8*(" << N_value << "+2))] = "; calcul1.afficher();cout << endl;

		Redond calcul2 = deux_p196; // 2**(32*8)
		//cout << "calcul2 = "; calcul2.afficher();cout << endl;
		calcul2.multiplier(Redond(4181, 4181)); // 2**(32*8) * 4181
		//cout << "calcul2 = "; calcul2.afficher();cout << endl;
		calcul2.inverser(); // 1 / [ 2**(32*8) * 4181 ]
		//cout << "calcul2 = "; calcul2.afficher();cout << endl;
		// NB : BxKs3 = BxK3  / [ 2**(32*8) * 4181 ]
		// On cherche à calculer BxKs3 / [ 2**(32*8) * 4181 ]
		calcul2.multiplier(calcul2); // 1 / [ 2**(32*8) * 4181 ] * [ 2**(32*8) * 4181 ]
		//cout << "calcul2 = "; calcul2.afficher();cout << endl;
		calcul2.multiplier(BxK3); // BxKs3 / [ 2**(32*8) * 4181 ]
		//cout << "calcul2 = "; calcul2.afficher();cout << endl;

		Redond result = Bxres;
		result.ajouter(calcul1);
		result.ajouter(calcul2);

		return result;
	}

public:
	const_PSC() {

		moinsRk = Redond(2726071, 6444477);
		tau0 = Redond (4691298, 10686154);
		deux_p32 = Redond(1779129, 11171346); // 2**32 (valeur précalculée)
		deux_p196 = Redond(280108, 10053949); // 2**(32*8) (valeur précalculée)

		Redond sum_F(0,0);
		for (int i = 0; i < 16; i++) {
			Fi[i] = Redond(Fi_A1[i], Fi_A2[i]);
			sum_F.ajouter(Fi[i]);
			Somme_Fi[i] = sum_F;
		}
	}

	Redond somme_Fi(int i) const {
		Redond sum(0, 0);
		if (i < 0 or i>15) return sum;
		return Somme_Fi[i];
	}

	Redond get_deux_p32() { return Redond(this->deux_p32); }
	Redond moins_rk() { return Redond(moinsRk); }

	Redond tau_i(int i) {
		Redond tau(tau0);
		for (int x = 1; x <= i; x++) {
			tau.multiplier(this->deux_p32);
		}
		return tau;
	}
	Redond Unisig_98_Hard(int indice) {
		if (0<= indice <20) return unisig_98_hard[indice];
		cout << endl << "erreur d'indice !!" << endl;
		return Redond(0, 0);
	}

	Redond calculer_redond_tableau8(unsigned char Tab[8], Redond Bx_Tab, bool reverse=false) {
		Redond r = Bx_Tab;
		int j;
		for (int i = 0; i < 8; i++) {
			if (reverse) { j = 7 - i; } else { j = i; }
			Redond r_temp(Tab[j], Tab[j]);
			r_temp.multiplier(tau_i(i)); // c'est bien i est pas j
			r_temp.multiplier(moinsRk);
			r.ajouter(r_temp);
		}
		return r;
	}

	/*
	Redond calculer_redond_MAC_N14(unsigned char MAC[8], int marker, bool is_connection1) {

		Redond r(0, 0);

		for (int i = 0; i < 8; i++) {
			Redond r_temp(MAC[7-i], MAC[7-i]);

			r_temp.multiplier(tau_i(i));
			r.ajouter(r_temp);
		}
		Redond r_temp(marker, marker);
		r_temp.multiplier(tau_i(8));
		r.ajouter(r_temp);
		r.multiplier(moinsRk);

		Redond compensation = this->Somme_Fi[15];
		compensation.multiplier(moinsRk);
		Redond Bx14_corr;
		if (is_connection1) { Bx14_corr = Redond(Bx14_cnx1); }
		else { Bx14_corr = Redond(Bx14_cnx2); }
		cout << "Bx_MAC_14 =";Bx14_corr.afficher();cout << endl;
		Bx14_corr.ajouter(compensation);
		cout << "Bx_MAC_14 compensé =";Bx14_corr.afficher();cout << endl;
		r.ajouter(Bx14_corr);

		return r;
	}
	*/

	Redond calculer_redond_MAC(unsigned char MAC[8], int marker, short int id_connection, short int N_Value) {
		Redond r(0, 0);

		for (int i = 0; i < 8; i++) {
			Redond r_temp(MAC[7 - i], MAC[7 - i]);

			r_temp.multiplier(tau_i(i));
			r.ajouter(r_temp);
		}
		Redond r_temp(marker, marker);
		r_temp.multiplier(tau_i(8));
		r.ajouter(r_temp);
		r.multiplier(moinsRk);

		Redond Bx_MAC = calcul_Bx_N_non_brouille(id_connection, N_Value);
		//cout << "Bx_MAC=";Bx_MAC.afficher();cout << endl;
		r.ajouter(Bx_MAC);

		return r;
	}
};

//------------------------------------------------------------------------------------









//------------------------------------------------------------------------------------
const unsigned char SBOX_1[4][16] = {
                                    {14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7},
                                    {0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8},
                                    {4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0},
                                    {15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13}
};
const unsigned char SBOX_2[4][16] = {
                                    {15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10},
                                    {3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5},
                                    {0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15},
                                    {13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9}
};
const unsigned char SBOX_3[4][16] = {
                                    {10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8},
                                    {13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1},
                                    {13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7},
                                    {1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12}
};
const unsigned char SBOX_4[4][16] = {
                                    {7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15},
                                    {13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9},
                                    {10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4},
                                    {3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14}
};
const unsigned char SBOX_5[4][16] = {
                                    {2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9},
                                    {14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6},
                                    {4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14},
                                    {11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3}
};
const unsigned char SBOX_6[4][16] = {
                                    {12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11},
                                    {10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8},
                                    {9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6},
                                    {4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13}
};
const unsigned char SBOX_7[4][16] = {
                                    {4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1},
                                    {13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6},
                                    {1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2},
                                    {6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12}
};
const unsigned char SBOX_8[4][16] = {
                                    {13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7},
                                    {1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2},
                                    {7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8},
                                    {2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11}
};


//------------------------------------------------------------------------------------
void MEMORY_Copy(unsigned char* Target, unsigned char* Source, unsigned short size)
{
    while (size-- != 0)
        *Target++ = *Source++;
}


//------------------------------------------------------------------------------------
void DES_Permuted_Choice_1(unsigned char* Key_In, unsigned char* Permuted_Choice_1)
{
    Permuted_Choice_1[0] = (Key_In[7] & 0x80) |
        ((Key_In[6] & 0x80) >> 1) |
        ((Key_In[5] & 0x80) >> 2) |
        ((Key_In[4] & 0x80) >> 3) |
        ((Key_In[3] & 0x80) >> 4) |
        ((Key_In[2] & 0x80) >> 5) |
        ((Key_In[1] & 0x80) >> 6);

    Permuted_Choice_1[1] = (Key_In[0] & 0x80) |
        (Key_In[7] & 0x40) |
        ((Key_In[6] & 0x40) >> 1) |
        ((Key_In[5] & 0x40) >> 2) |
        ((Key_In[4] & 0x40) >> 3) |
        ((Key_In[3] & 0x40) >> 4) |
        ((Key_In[2] & 0x40) >> 5);

    Permuted_Choice_1[2] = ((Key_In[1] & 0x40) << 1) |
        (Key_In[0] & 0x40) |
        (Key_In[7] & 0x20) |
        ((Key_In[6] & 0x20) >> 1) |
        ((Key_In[5] & 0x20) >> 2) |
        ((Key_In[4] & 0x20) >> 3) |
        ((Key_In[3] & 0x20) >> 4);

    Permuted_Choice_1[3] = ((Key_In[2] & 0x20) << 2) |
        ((Key_In[1] & 0x20) << 1) |
        (Key_In[0] & 0x20) |
        (Key_In[7] & 0x10) |
        ((Key_In[6] & 0x10) >> 1) |
        ((Key_In[5] & 0x10) >> 2) |
        ((Key_In[4] & 0x10) >> 3);

    Permuted_Choice_1[4] = ((Key_In[7] & 0x02) << 6) |
        ((Key_In[6] & 0x02) << 5) |
        ((Key_In[5] & 0x02) << 4) |
        ((Key_In[4] & 0x02) << 3) |
        ((Key_In[3] & 0x02) << 2) |
        ((Key_In[2] & 0x02) << 1) |
        (Key_In[1] & 0x02);

    Permuted_Choice_1[5] = ((Key_In[0] & 0x02) << 6) |
        ((Key_In[7] & 0x04) << 4) |
        ((Key_In[6] & 0x04) << 3) |
        ((Key_In[5] & 0x04) << 2) |
        ((Key_In[4] & 0x04) << 1) |
        (Key_In[3] & 0x04) |
        ((Key_In[2] & 0x04) >> 1);

    Permuted_Choice_1[6] = ((Key_In[1] & 0x04) << 5) |
        ((Key_In[0] & 0x04) << 4) |
        ((Key_In[7] & 0x08) << 2) |
        ((Key_In[6] & 0x08) << 1) |
        (Key_In[5] & 0x08) |
        ((Key_In[4] & 0x08) >> 1) |
        ((Key_In[3] & 0x08) >> 2);

    Permuted_Choice_1[7] = ((Key_In[2] & 0x08) << 4) |
        ((Key_In[1] & 0x08) << 3) |
        ((Key_In[0] & 0x08) << 2) |
        (Key_In[3] & 0x10) |
        ((Key_In[2] & 0x10) >> 1) |
        ((Key_In[1] & 0x10) >> 2) |
        ((Key_In[0] & 0x10) >> 3);
}


//------------------------------------------------------------------------------------
void DES_Left_Shift(unsigned char* DES_Shift_In)
{
    unsigned char Shift_Temp0, Shift_Temp1, Shift_Temp2, Shift_Temp3;
    // Shift C0
    if (DES_Shift_In[3] & 0x80) Shift_Temp3 = 0x02;
    else Shift_Temp3 = 0x00;
    if (DES_Shift_In[2] & 0x80) Shift_Temp2 = 0x02;
    else Shift_Temp2 = 0x00;
    if (DES_Shift_In[1] & 0x80) Shift_Temp1 = 0x02;
    else Shift_Temp1 = 0x00;
    if (DES_Shift_In[0] & 0x80) Shift_Temp0 = 0x02;
    else Shift_Temp0 = 0x00;

    DES_Shift_In[3] <<= 1;
    DES_Shift_In[2] <<= 1;
    DES_Shift_In[1] <<= 1;
    DES_Shift_In[0] <<= 1;

    DES_Shift_In[0] |= Shift_Temp1;
    DES_Shift_In[1] |= Shift_Temp2;
    DES_Shift_In[2] |= Shift_Temp3;
    DES_Shift_In[3] |= Shift_Temp0;

    // Shift L0
    if (DES_Shift_In[7] & 0x80) Shift_Temp3 = 0x02;
    else Shift_Temp3 = 0x00;
    if (DES_Shift_In[6] & 0x80) Shift_Temp2 = 0x02;
    else Shift_Temp2 = 0x00;
    if (DES_Shift_In[5] & 0x80) Shift_Temp1 = 0x02;
    else Shift_Temp1 = 0x00;
    if (DES_Shift_In[4] & 0x80) Shift_Temp0 = 0x02;
    else Shift_Temp0 = 0x00;

    DES_Shift_In[7] <<= 1;
    DES_Shift_In[6] <<= 1;
    DES_Shift_In[5] <<= 1;
    DES_Shift_In[4] <<= 1;

    DES_Shift_In[4] |= Shift_Temp1;
    DES_Shift_In[5] |= Shift_Temp2;
    DES_Shift_In[6] |= Shift_Temp3;
    DES_Shift_In[7] |= Shift_Temp0;
}

//------------------------------------------------------------------------------------
void DES_Permuted_Choice_2(unsigned char* Key_In, unsigned char* Permuted_Choice_2)
{
    Permuted_Choice_2[0] = ((Key_In[1] & 0x02) << 6) |
        ((Key_In[2] & 0x20) << 1) |
        ((Key_In[1] & 0x10) << 1) |
        ((Key_In[3] & 0x20) >> 1) |
        ((Key_In[0] & 0x80) >> 4) |
        ((Key_In[0] & 0x08) >> 1);

    Permuted_Choice_2[1] = ((Key_In[0] & 0x20) << 2) |
        ((Key_In[3] & 0x03) << 5) |
        ((Key_In[2] & 0x80) >> 2) |
        ((Key_In[0] & 0x04) << 2) |
        ((Key_In[2] & 0x02) << 2) |
        ((Key_In[1] & 0x20) >> 3);

    Permuted_Choice_2[2] = ((Key_In[3] & 0x40) << 1) |
        ((Key_In[2] & 0x08) << 3) |
        ((Key_In[1] & 0x08) << 2) |
        (Key_In[0] & 0x10) |
        (Key_In[3] & 0x08) |
        ((Key_In[1] & 0x80) >> 5);

    Permuted_Choice_2[3] = ((Key_In[2] & 0x40) << 1) |
        ((Key_In[0] & 0x02) << 5) |
        ((Key_In[3] & 0x04) << 3) |
        ((Key_In[2] & 0x04) << 2) |
        ((Key_In[1] & 0x04) << 1) |
        ((Key_In[0] & 0x40) >> 4);

    Permuted_Choice_2[4] = ((Key_In[5] & 0x04) << 5) |
        ((Key_In[7] & 0x20) << 1) |
        (Key_In[4] & 0x20) |
        ((Key_In[5] & 0x40) >> 2) |
        (Key_In[6] & 0x08) |
        (Key_In[7] & 0x04);

    Permuted_Choice_2[5] = ((Key_In[4] & 0x40) << 1) |
        ((Key_In[5] & 0x08) << 3) |
        ((Key_In[7] & 0x40) >> 1) |
        ((Key_In[6] & 0x20) >> 1) |
        (Key_In[4] & 0x08) |
        (Key_In[6] & 0x04);

    Permuted_Choice_2[6] = ((Key_In[6] & 0x40) << 1) |
        ((Key_In[6] & 0x02) << 5) |
        ((Key_In[5] & 0x10) << 1) |
        ((Key_In[7] & 0x02) << 3) |
        ((Key_In[4] & 0x04) << 1) |
        ((Key_In[7] & 0x10) >> 2);

    Permuted_Choice_2[7] = ((Key_In[6] & 0x10) << 3) |
        ((Key_In[5] & 0x02) << 5) |
        ((Key_In[7] & 0x80) >> 2) |
        ((Key_In[5] & 0x80) >> 3) |
        ((Key_In[4] & 0x80) >> 4) |
        ((Key_In[4] & 0x10) >> 2);
}

////------------------------------------------------------------------------------------
//void DES_Key_Schedule(unsigned char * Permuted_Choice_1, unsigned char * Key_Out, unsigned char Key_Index)
//  {
//  DES_Left_Shift((unsigned char *)&Permuted_Choice_1[0]);
//  if ((Key_Index != 1) && (Key_Index != 2) && (Key_Index != 9) && (Key_Index != 16))
//    DES_Left_Shift((unsigned char *)&Permuted_Choice_1[0]);
//  DES_Permuted_Choice_2((unsigned char *)&Permuted_Choice_1[0], Key_Out);
//  }

//------------------------------------------------------------------------------------
void DES_Initial_Permutation(unsigned char* Input, unsigned char* Output)
{
    Output[0] = ((Input[7] & 0x40) << 1) |
        (Input[6] & 0x40) |
        ((Input[5] & 0x40) >> 1) |
        ((Input[4] & 0x40) >> 2) |
        ((Input[3] & 0x40) >> 3) |
        ((Input[2] & 0x40) >> 4) |
        ((Input[1] & 0x40) >> 5) |
        ((Input[0] & 0x40) >> 6);

    Output[1] = ((Input[7] & 0x10) << 3) |
        ((Input[6] & 0x10) << 2) |
        ((Input[5] & 0x10) << 1) |
        (Input[4] & 0x10) |
        ((Input[3] & 0x10) >> 1) |
        ((Input[2] & 0x10) >> 2) |
        ((Input[1] & 0x10) >> 3) |
        ((Input[0] & 0x10) >> 4);

    Output[2] = ((Input[7] & 0x04) << 5) |
        ((Input[6] & 0x04) << 4) |
        ((Input[5] & 0x04) << 3) |
        ((Input[4] & 0x04) << 2) |
        ((Input[3] & 0x04) << 1) |
        (Input[2] & 0x04) |
        ((Input[1] & 0x04) >> 1) |
        ((Input[0] & 0x04) >> 2);

    Output[3] = ((Input[7] & 0x01) << 7) |
        ((Input[6] & 0x01) << 6) |
        ((Input[5] & 0x01) << 5) |
        ((Input[4] & 0x01) << 4) |
        ((Input[3] & 0x01) << 3) |
        ((Input[2] & 0x01) << 2) |
        ((Input[1] & 0x01) << 1) |
        (Input[0] & 0x01);

    Output[4] = (Input[7] & 0x80) |
        ((Input[6] & 0x80) >> 1) |
        ((Input[5] & 0x80) >> 2) |
        ((Input[4] & 0x80) >> 3) |
        ((Input[3] & 0x80) >> 4) |
        ((Input[2] & 0x80) >> 5) |
        ((Input[1] & 0x80) >> 6) |
        ((Input[0] & 0x80) >> 7);

    Output[5] = ((Input[7] & 0x20) << 2) |
        ((Input[6] & 0x20) << 1) |
        (Input[5] & 0x20) |
        ((Input[4] & 0x20) >> 1) |
        ((Input[3] & 0x20) >> 2) |
        ((Input[2] & 0x20) >> 3) |
        ((Input[1] & 0x20) >> 4) |
        ((Input[0] & 0x20) >> 5);

    Output[6] = ((Input[7] & 0x08) << 4) |
        ((Input[6] & 0x08) << 3) |
        ((Input[5] & 0x08) << 2) |
        ((Input[4] & 0x08) << 1) |
        (Input[3] & 0x08) |
        ((Input[2] & 0x08) >> 1) |
        ((Input[1] & 0x08) >> 2) |
        ((Input[0] & 0x08) >> 3);

    Output[7] = ((Input[7] & 0x02) << 6) |
        ((Input[6] & 0x02) << 5) |
        ((Input[5] & 0x02) << 4) |
        ((Input[4] & 0x02) << 3) |
        ((Input[3] & 0x02) << 2) |
        ((Input[2] & 0x02) << 1) |
        (Input[1] & 0x02) |
        ((Input[0] & 0x02) >> 1);
}

//------------------------------------------------------------------------------------
void DES_Inverse_Initial_Permutation(unsigned char* Input, unsigned char* Output)
{
    Output[0] = ((Input[4] & 0x01) << 7) |
        ((Input[0] & 0x01) << 6) |
        ((Input[5] & 0x01) << 5) |
        ((Input[1] & 0x01) << 4) |
        ((Input[6] & 0x01) << 3) |
        ((Input[2] & 0x01) << 2) |
        ((Input[7] & 0x01) << 1) |
        (Input[3] & 0x01);

    Output[1] = ((Input[4] & 0x02) << 6) |
        ((Input[0] & 0x02) << 5) |
        ((Input[5] & 0x02) << 4) |
        ((Input[1] & 0x02) << 3) |
        ((Input[6] & 0x02) << 2) |
        ((Input[2] & 0x02) << 1) |
        (Input[7] & 0x02) |
        ((Input[3] & 0x02) >> 1);

    Output[2] = ((Input[4] & 0x04) << 5) |
        ((Input[0] & 0x04) << 4) |
        ((Input[5] & 0x04) << 3) |
        ((Input[1] & 0x04) << 2) |
        ((Input[6] & 0x04) << 1) |
        (Input[2] & 0x04) |
        ((Input[7] & 0x04) >> 1) |
        ((Input[3] & 0x04) >> 2);

    Output[3] = ((Input[4] & 0x08) << 4) |
        ((Input[0] & 0x08) << 3) |
        ((Input[5] & 0x08) << 2) |
        ((Input[1] & 0x08) << 1) |
        (Input[6] & 0x08) |
        ((Input[2] & 0x08) >> 1) |
        ((Input[7] & 0x08) >> 2) |
        ((Input[3] & 0x08) >> 3);

    Output[4] = ((Input[4] & 0x10) << 3) |
        ((Input[0] & 0x10) << 2) |
        ((Input[5] & 0x10) << 1) |
        (Input[1] & 0x10) |
        ((Input[6] & 0x10) >> 1) |
        ((Input[2] & 0x10) >> 2) |
        ((Input[7] & 0x10) >> 3) |
        ((Input[3] & 0x10) >> 4);

    Output[5] = ((Input[4] & 0x20) << 2) |
        ((Input[0] & 0x20) << 1) |
        (Input[5] & 0x20) |
        ((Input[1] & 0x20) >> 1) |
        ((Input[6] & 0x20) >> 2) |
        ((Input[2] & 0x20) >> 3) |
        ((Input[7] & 0x20) >> 4) |
        ((Input[3] & 0x20) >> 5);

    Output[6] = ((Input[4] & 0x40) << 1) |
        (Input[0] & 0x40) |
        ((Input[5] & 0x40) >> 1) |
        ((Input[1] & 0x40) >> 2) |
        ((Input[6] & 0x40) >> 3) |
        ((Input[2] & 0x40) >> 4) |
        ((Input[7] & 0x40) >> 5) |
        ((Input[3] & 0x40) >> 6);

    Output[7] = (Input[4] & 0x80) |
        ((Input[0] & 0x80) >> 1) |
        ((Input[5] & 0x80) >> 2) |
        ((Input[1] & 0x80) >> 3) |
        ((Input[6] & 0x80) >> 4) |
        ((Input[2] & 0x80) >> 5) |
        ((Input[7] & 0x80) >> 6) |
        ((Input[3] & 0x80) >> 7);
}


//------------------------------------------------------------------------------------
void DES_Function_P(unsigned char* Input, unsigned char* Output)
{
    Output[0] = ((Input[1] & 0x01) << 7) |
        ((Input[0] & 0x02) << 5) |
        ((Input[2] & 0x18) << 1) |
        (Input[3] & 0x08) |
        ((Input[1] & 0x10) >> 2) |
        ((Input[3] & 0x10) >> 3) |
        ((Input[2] & 0x80) >> 7);

    Output[1] = (Input[0] & 0x80) |
        ((Input[1] & 0x02) << 5) |
        ((Input[2] & 0x02) << 4) |
        ((Input[3] & 0x40) >> 2) |
        (Input[0] & 0x08) |
        ((Input[2] & 0x40) >> 4) |
        (Input[3] & 0x02) |
        ((Input[1] & 0x40) >> 6);

    Output[2] = ((Input[0] & 0x40) << 1) |
        ((Input[0] & 0x01) << 6) |
        ((Input[2] & 0x01) << 5) |
        ((Input[1] & 0x04) << 2) |
        ((Input[3] & 0x01) << 3) |
        ((Input[3] & 0x20) >> 3) |
        ((Input[0] & 0x20) >> 4) |
        ((Input[1] & 0x80) >> 7);

    Output[3] = ((Input[2] & 0x20) << 2) |
        ((Input[1] & 0x08) << 3) |
        ((Input[3] & 0x04) << 3) |
        ((Input[0] & 0x04) << 2) |
        ((Input[2] & 0x04) << 1) |
        ((Input[1] & 0x20) >> 3) |
        ((Input[0] & 0x10) >> 3) |
        ((Input[3] & 0x80) >> 7);
}


//------------------------------------------------------------------------------------
void DES_Function_E(unsigned char* Input, unsigned char* Output)
{
    Output[0] = ((Input[0] >> 1) & 0x7C) | ((Input[3] & 0x01) << 7);
    Output[1] = ((Input[0] << 3) & 0xF8) | ((Input[1] & 0x80) >> 5);
    Output[2] = ((Input[1] >> 1) & 0x7C) | ((Input[0] & 0x01) << 7);
    Output[3] = ((Input[1] << 3) & 0xF8) | ((Input[2] & 0x80) >> 5);
    Output[4] = ((Input[2] >> 1) & 0x7C) | ((Input[1] & 0x01) << 7);
    Output[5] = ((Input[2] << 3) & 0xF8) | ((Input[3] & 0x80) >> 5);
    Output[6] = ((Input[3] >> 1) & 0x7C) | ((Input[2] & 0x01) << 7);
    Output[7] = ((Input[3] << 3) & 0xF8) | ((Input[0] & 0x80) >> 5);
}

//------------------------------------------------------------------------------------
void DES_Function_XOR(unsigned char* XOR_1, unsigned char* XOR_2)
{
    unsigned char I;

    for (I = 0; I < 4; I++)
        XOR_1[I] ^= XOR_2[I];
}

//------------------------------------------------------------------------------------
unsigned char DES_SBox(unsigned char Raw, unsigned char Column, unsigned char Box_Number)
{
    switch (Box_Number)
    {
    case 1:
        return SBOX_1[Raw][Column];
    case 2:
        return SBOX_2[Raw][Column];
    case 3:
        return SBOX_3[Raw][Column];
    case 4:
        return SBOX_4[Raw][Column];
    case 5:
        return SBOX_5[Raw][Column];
    case 6:
        return SBOX_6[Raw][Column];
    case 7:
        return SBOX_7[Raw][Column];
    case 8:
        return SBOX_8[Raw][Column];
    }

    return 0;
}

//------------------------------------------------------------------------------------
void DES_Function_F(unsigned char* DES_Buffer, unsigned char* Key)
{
    unsigned char F_Temp[8];
    unsigned char I;

    DES_Function_E(DES_Buffer, (unsigned char*)&F_Temp[0]);
    DES_Function_XOR((unsigned char*)&F_Temp[0], Key);
    DES_Function_XOR((unsigned char*)&F_Temp[4], Key + 4);
    unsigned char Raw, Column;

    for (I = 1; I <= 8; I++)
    {
        Raw = ((F_Temp[I - 1] & 0x04) >> 2) | ((F_Temp[I - 1] & 0x80) >> 6);
        Column = ((F_Temp[I - 1] & 0x78) >> 3);
        F_Temp[I - 1] = DES_SBox(Raw, Column, I);
    }

    // Convert 8 x 1 nIbble (ex. 0x010F0A050407010E)
    // Into 4 x 2 NIbble (ex. 1FA5471E)
    for (I = 0; I < 4; I++)
    {
        F_Temp[2 * I] <<= 4;
        F_Temp[2 * I] |= F_Temp[(2 * I) + 1];
    }

    F_Temp[1] = F_Temp[2];
    F_Temp[2] = F_Temp[4];
    F_Temp[3] = F_Temp[6];

    DES_Function_P((unsigned char*)&F_Temp[0], DES_Buffer);
}


//------------------------------------------------------------------------------------
void DES_Key_Scheduling(unsigned char* Key, unsigned char* Key_Schedule_1, unsigned char* Key_Schedule_2)
{
    unsigned char Permuted_Choice_1[8];
    unsigned char Key_Index = 1;

    DES_Permuted_Choice_1(Key, (unsigned char*)&Permuted_Choice_1[0]);

    do
    {
        DES_Left_Shift((unsigned char*)&Permuted_Choice_1[0]);
        if ((Key_Index != 1) && (Key_Index != 2)) DES_Left_Shift((unsigned char*)&Permuted_Choice_1[0]);
        DES_Permuted_Choice_2((unsigned char*)&Permuted_Choice_1[0], Key_Schedule_1);
        Key_Schedule_1 += 8;
    } while (++Key_Index <= 8);

    do
    {
        DES_Left_Shift((unsigned char*)&Permuted_Choice_1[0]);
        if ((Key_Index != 9) && (Key_Index != 16)) DES_Left_Shift((unsigned char*)&Permuted_Choice_1[0]);
        DES_Permuted_Choice_2((unsigned char*)&Permuted_Choice_1[0], Key_Schedule_2);
        Key_Schedule_2 += 8;
    } while (++Key_Index <= 16);
}


//------------------------------------------------------------------------------------
void DES_Round_ENC(unsigned char* DES_Buffer, unsigned char* Key_Schedule_1, unsigned char* Key_Schedule_2)
{
    unsigned char DES_Buffer_Left[4];
    unsigned char DES_Buffer_Right[4];
    unsigned char DES_Buffer_Temp1[4];
    unsigned char DES_Buffer_Temp2[4];
    unsigned char Round_Key[8];
    unsigned char I;

    // Split DES Input buffer into 2 x 4 bytes words L0 and R0 5including first swap)
    MEMORY_Copy((unsigned char*)&DES_Buffer_Left[0], DES_Buffer, 4);
    MEMORY_Copy((unsigned char*)&DES_Buffer_Right[0], DES_Buffer + 4, 4);

    for (I = 1; I <= 8; I++)
    {
        // For each of the 16 rounds:
        // Key Scheduling
        MEMORY_Copy((unsigned char*)&Round_Key[0], Key_Schedule_1, 8);
        Key_Schedule_1 += 8;
        MEMORY_Copy((unsigned char*)&DES_Buffer_Temp1[0], (unsigned char*)&DES_Buffer_Left[0], 4);
        // L_n+1 = R_n
        MEMORY_Copy((unsigned char*)&DES_Buffer_Left[0], (unsigned char*)&DES_Buffer_Right[0], 4);
        // R_n+1 = L_n + f(R_n, K_n+1)
        // F(R.K)
        MEMORY_Copy((unsigned char*)&DES_Buffer_Temp2[0], (unsigned char*)&DES_Buffer_Right[0], 4);
        DES_Function_F((unsigned char*)&DES_Buffer_Temp2[0], (unsigned char*)&Round_Key[0]);
        DES_Function_XOR((unsigned char*)&DES_Buffer_Temp1[0], (unsigned char*)&DES_Buffer_Temp2[0]);
        MEMORY_Copy((unsigned char*)&DES_Buffer_Right[0], (unsigned char*)&DES_Buffer_Temp1[0], 4);
    }

    for (I = 1; I <= 8; I++)
    {
        // For each of the 16 rounds:
        // Key Scheduling
        MEMORY_Copy((unsigned char*)&Round_Key[0], Key_Schedule_2, 8);
        Key_Schedule_2 += 8;
        MEMORY_Copy((unsigned char*)&DES_Buffer_Temp1[0], (unsigned char*)&DES_Buffer_Left[0], 4);
        // L_n+1 = R_n
        MEMORY_Copy((unsigned char*)&DES_Buffer_Left[0], (unsigned char*)&DES_Buffer_Right[0], 4);
        // R_n+1 = L_n + f(R_n, K_n+1)
        // F(R.K)
        MEMORY_Copy((unsigned char*)&DES_Buffer_Temp2[0], (unsigned char*)&DES_Buffer_Right[0], 4);
        DES_Function_F((unsigned char*)&DES_Buffer_Temp2[0], (unsigned char*)&Round_Key[0]);
        DES_Function_XOR((unsigned char*)&DES_Buffer_Temp1[0], (unsigned char*)&DES_Buffer_Temp2[0]);
        MEMORY_Copy((unsigned char*)&DES_Buffer_Right[0], (unsigned char*)&DES_Buffer_Temp1[0], 4);
    }

    MEMORY_Copy(DES_Buffer, (unsigned char*)&DES_Buffer_Left[0], 4);
    MEMORY_Copy(DES_Buffer + 4, (unsigned char*)&DES_Buffer_Right[0], 4);
}


//------------------------------------------------------------------------------------
void DES_Round_DEC(unsigned char* DES_Buffer, unsigned char* Key_Schedule_1, unsigned char* Key_Schedule_2)
{
    unsigned char DES_Buffer_Left[4];
    unsigned char DES_Buffer_Right[4];
    unsigned char DES_Buffer_Temp1[4];
    unsigned char DES_Buffer_Temp2[4];
    unsigned char Round_Key[8];
    unsigned char I;


    // Split DES Input buffer into 2 x 4 bytes words L0 and R0
    MEMORY_Copy((unsigned char*)&DES_Buffer_Left[0], DES_Buffer + 4, 4);
    MEMORY_Copy((unsigned char*)&DES_Buffer_Right[0], DES_Buffer, 4);

    Key_Schedule_2 += 56;
    Key_Schedule_1 += 56;

    for (I = 1; I <= 8; I++)
    {
        // For each of the 16 rounds:
        // Key Scheduling
        MEMORY_Copy((unsigned char*)&Round_Key[0], Key_Schedule_2, 8);
        Key_Schedule_2 -= 8;
        MEMORY_Copy((unsigned char*)&DES_Buffer_Temp1[0], (unsigned char*)&DES_Buffer_Right[0], 4);
        // R_n-1 = L_n
        MEMORY_Copy((unsigned char*)&DES_Buffer_Right[0], (unsigned char*)&DES_Buffer_Left[0], 4);
        // L_n-1 = R_n + f(L_n, K_n)
        // F(R.K)
        MEMORY_Copy((unsigned char*)&DES_Buffer_Temp2[0], (unsigned char*)&DES_Buffer_Left[0], 4);
        DES_Function_F((unsigned char*)&DES_Buffer_Temp2[0], (unsigned char*)&Round_Key[0]);
        DES_Function_XOR((unsigned char*)&DES_Buffer_Temp1[0], (unsigned char*)&DES_Buffer_Temp2[0]);
        MEMORY_Copy((unsigned char*)&DES_Buffer_Left[0], (unsigned char*)&DES_Buffer_Temp1[0], 4);
    }

    for (I = 1; I <= 8; I++)
    {
        // For each of the 16 rounds:
        // Key Scheduling
        MEMORY_Copy((unsigned char*)&Round_Key[0], Key_Schedule_1, 8);
        Key_Schedule_1 -= 8;
        MEMORY_Copy((unsigned char*)&DES_Buffer_Temp1[0], (unsigned char*)&DES_Buffer_Right[0], 4);
        // R_n-1 = L_n
        MEMORY_Copy((unsigned char*)&DES_Buffer_Right[0], (unsigned char*)&DES_Buffer_Left[0], 4);
        // L_n-1 = R_n + f(L_n, K_n)
        // F(R.K)
        MEMORY_Copy((unsigned char*)&DES_Buffer_Temp2[0], (unsigned char*)&DES_Buffer_Left[0], 4);
        DES_Function_F((unsigned char*)&DES_Buffer_Temp2[0], (unsigned char*)&Round_Key[0]);
        DES_Function_XOR((unsigned char*)&DES_Buffer_Temp1[0], (unsigned char*)&DES_Buffer_Temp2[0]);
        MEMORY_Copy((unsigned char*)&DES_Buffer_Left[0], (unsigned char*)&DES_Buffer_Temp1[0], 4);
    }

    MEMORY_Copy(DES_Buffer, (unsigned char*)&DES_Buffer_Left[0], 4);
    MEMORY_Copy(DES_Buffer + 4, (unsigned char*)&DES_Buffer_Right[0], 4);
}



//------------------------------------------------------------------------------------
void XOR_Byte2Byte(unsigned char* Source, unsigned char* Dest, unsigned char SzData)
{
    unsigned char I;

    for (I = 0; I < SzData; I++)
    {
        Dest[I] ^= Source[I];
    }
}

//------------------------------------------------------------------------------------
void DES_DEC(unsigned char* Input, unsigned char* Output, unsigned char* Key)
{
    unsigned char DES_Work_Buffer[8];
    unsigned char Key_Schedule_1[8][8];
    unsigned char Key_Schedule_2[8][8];

    //----- Key Scheduling -----
    DES_Key_Scheduling(Key, (unsigned char*)&Key_Schedule_1[0][0], (unsigned char*)&Key_Schedule_2[0][0]);

    DES_Initial_Permutation(Input, (unsigned char*)&DES_Work_Buffer[0]);
    DES_Round_DEC((unsigned char*)&DES_Work_Buffer[0], (unsigned char*)&Key_Schedule_1[0][0], (unsigned char*)&Key_Schedule_2[0][0]);
    DES_Inverse_Initial_Permutation((unsigned char*)&DES_Work_Buffer[0], Output);
}


//------------------------------------------------------------------------------------
void DES_ENC(unsigned char* Input, unsigned char* Output, unsigned char* Key)
{
    unsigned char DES_Work_Buffer[8];
    unsigned char Key_Schedule_1[8][8];
    unsigned char Key_Schedule_2[8][8];
    unsigned char DES_Temp[4];

    //----- Initial Permutation -----
    DES_Initial_Permutation(Input, (unsigned char*)&DES_Work_Buffer[0]);

    //----- Key Scheduling -----
    DES_Key_Scheduling(Key, (unsigned char*)&Key_Schedule_1[0][0], (unsigned char*)&Key_Schedule_2[0][0]);

    DES_Round_ENC((unsigned char*)&DES_Work_Buffer[0], (unsigned char*)&Key_Schedule_1[0][0], (unsigned char*)&Key_Schedule_2[0][0]);
    // Swap R16 and L16
    MEMORY_Copy((unsigned char*)&DES_Temp[0], (unsigned char*)&DES_Work_Buffer[0], 4);
    MEMORY_Copy((unsigned char*)&DES_Work_Buffer[0], (unsigned char*)&DES_Work_Buffer[4], 4);
    MEMORY_Copy((unsigned char*)&DES_Work_Buffer[4], (unsigned char*)&DES_Temp[0], 4);

    DES_Inverse_Initial_Permutation((unsigned char*)&DES_Work_Buffer[0], Output);
}

void afficher_64bits(string s, unsigned char Tab[8]) {
    cout << s;
    for (int i = 0; i < 8; i++) cout << (int)Tab[i] << " ";
    cout << endl;
}

void afficher_hexa(string s, unsigned char Tab[8]) {
    cout << s;
    printf("16#%x_%x#, 16#%x_%x#, 16#%x_%x#, 16#%x_%x#\n", Tab[0], Tab[1], Tab[2], Tab[3], Tab[4], Tab[5], Tab[6], Tab[7]);
}
void afficher_hexa_inverse(string s, unsigned char Tab[8]) {
    cout << s;
    printf("%x %x %x %x %x %x %x %x\n", Tab[7], Tab[6], Tab[5], Tab[4], Tab[3], Tab[2], Tab[1], Tab[0]);
}

void calcul_MAC_single_Block(unsigned char Block[8], unsigned char k1[8], unsigned char k2[8], unsigned char k3[8], unsigned char Output[8]) {
    //----- Step 1 -----
    //cout << endl << endl << "ETAPE_1" << endl << endl;
    DES_ENC(Block, Output, (unsigned char*)k1);
    afficher_64bits("message block 1 : ", Block);
    //afficher_64bits("Clef de session 1 (Ks1) = ", k1);
    //afficher_64bits("Apres cryptage par Ks1 ==> ", Output);
    //----- Step 2 -----
    //cout << endl << endl << "ETAPE_2" << endl << endl;
    DES_DEC(Output, Output, (unsigned char*)k2);
    //afficher_64bits("Apres decryptage par Ks2 ==> ", Output);
    //----- Step 3 -----
    //cout << endl << endl << "ETAPE_3" << endl << endl;
    DES_ENC(Output, Output, (unsigned char*)k3);
    //afficher_64bits("Apres cryptage par Ks3 ==> ", Output);
    printf("CBC-MAC         = %x %x %x %x %x %x %x %x\n", Output[0], Output[1], Output[2], Output[3], Output[4], Output[5], Output[6], Output[7]);
    int pause = 0;
}

void calcul_MAC_3Blocks(
    unsigned char Block1[8], unsigned char Block2[8], unsigned char Block3[8],
    unsigned char k1[8], unsigned char k2[8], unsigned char k3[8], unsigned char Output[8])
{

    //----- Step 1 -----
    cout << "CALCUL de MAC à 3 blocs";
    cout << endl << endl;
    DES_ENC(Block1, Output, (unsigned char*)k1);
    afficher_64bits("message block 1 : ", Block1);
    afficher_64bits("Clef de session 1 (Ks1) = ", k1);
    afficher_64bits("Apres cryptage par Ks1 ==> ", Output);

    //----- Step 2 -----
    cout << endl << endl;
    afficher_64bits("message block 2 : ", Block2);
    XOR_Byte2Byte(&Block2[0], &Output[0], 8);
    afficher_64bits("Apres XOR avec le block 2 ==> ", Output);

    //----- Step 3 -----
    cout << endl << endl;
    DES_ENC(Output, Output, (unsigned char*)k1);
    afficher_64bits("Apres cryptage par Ks1 ==> ", Output);

    //----- Step 4 -----
    cout << endl << endl;
    afficher_64bits("message block 3 : ", Block3);
    XOR_Byte2Byte(&Block3[0], &Output[0], 8);
    afficher_64bits("Apres XOR avec le block 3 ==> ", Output);

    //----- Step 5 -----
    cout << endl << endl;
    DES_ENC(Output, Output, (unsigned char*)k1);
    afficher_64bits("Apres cryptage par Ks1 ==> ", Output);

    //----- Step 6 -----
    cout << endl << endl;
    DES_DEC(Output, Output, (unsigned char*)k2);
    afficher_64bits("Apres decryptage par Ks2 ==> ", Output);

    //----- Step 7 -----
    cout << endl << endl;
    DES_ENC(Output, Output, (unsigned char*)k3);
    afficher_64bits("Apres cryptage par Ks3 ==> ", Output);
    printf("CBC-MAC         = %x %x %x %x %x %x %x %x\n", Output[0], Output[1], Output[2], Output[3], Output[4], Output[5], Output[6], Output[7]);
    int pause = 0;

}

void calcul_MAC_4Blocks(
            unsigned char Block1[8], unsigned char Block2[8], unsigned char Block3[8], unsigned char Block4[8],
            unsigned char k1[8], unsigned char k2[8], unsigned char k3[8], unsigned char Output[8])
{
    /*afficher_64bits("Clef de session 1 (Ks1) = ", k1);
    afficher_64bits("Clef de session 1 (Ks2) = ", k2);
    afficher_64bits("Clef de session 1 (Ks3) = ", k3);*/
    //----- Step 1 -----
    cout << "CALCUL de MAC à 4 blocs" << endl;
    //cout << endl << endl << "ETAPE_1" << endl << endl;
    DES_ENC(Block1, Output, (unsigned char*)k1);
    afficher_64bits("message block 1 : ", Block1);
    //afficher_64bits("Apres cryptage par Ks1 ==> ", Output);

    //----- Step 2 -----
    //cout << endl << endl << "ETAPE_2" << endl << endl;
    afficher_64bits("message block 2 : ", Block2);
    XOR_Byte2Byte(&Block2[0], &Output[0], 8);
    //afficher_64bits("Apres XOR avec le block 2 ==> ", Output);

    //----- Step 3 -----
    //cout << endl << endl << "ETAPE_3" << endl << endl;
    DES_ENC(Output, Output, (unsigned char*)k1);
    //afficher_64bits("Apres cryptage par Ks1 ==> ", Output);

    //----- Step 4 -----
    //cout << endl << endl << "ETAPE_4" << endl << endl;
    afficher_64bits("message block 3 : ", Block3);
    XOR_Byte2Byte(&Block3[0], &Output[0], 8);
    //afficher_64bits("Apres XOR avec le block 3 ==> ", Output);

    //----- Step 5 -----
    //cout << endl << endl << "ETAPE_5" << endl << endl;
    DES_ENC(Output, Output, (unsigned char*)k1);
    //afficher_64bits("Apres cryptage par Ks1 ==> ", Output);

    //----- Step 6 -----
    //cout << endl << endl << "ETAPE_6" << endl << endl;
    afficher_64bits("message block 4 : ", Block4);
    XOR_Byte2Byte(&Block4[0], &Output[0], 8);
    //afficher_64bits("Apres XOR avec le block 4 ==> ", Output);

    //----- Step 7 -----
    //cout << endl << endl << "ETAPE_7" << endl << endl;
    DES_ENC(Output, Output, (unsigned char*)k1);
    //afficher_64bits("Apres cryptage par Ks1 ==> ", Output);

    //----- Step 8 -----
    //cout << endl << endl << "ETAPE_8" << endl << endl;
    DES_DEC(Output, Output, (unsigned char*)k2);
    //afficher_64bits("Apres decryptage par Ks2 ==> ", Output);

    //----- Step 9 -----
    //cout << endl << endl << "ETAPE_9" << endl << endl;
    DES_ENC(Output, Output, (unsigned char*)k3);
    afficher_64bits("Apres cryptage par Ks3 ==> ", Output);
    printf("CBC-MAC         = %x %x %x %x %x %x %x %x\n", Output[0], Output[1], Output[2], Output[3], Output[4], Output[5], Output[6], Output[7]);
    int pause = 0;

}

void calcul_MAC_n_Blocks(int n, unsigned char Blocks[], unsigned char k1[8], unsigned char k2[8], unsigned char k3[8], unsigned char Output[8], bool verbose=false) {
    unsigned char current_block[8];
    int byte_index = 0;
    for (int i = 0; i < n;i++) {
        for (int j = 0; j < 8; j++) {
            current_block[j] = Blocks[byte_index++];
        }
        if (verbose) afficher_64bits("current message block : ", current_block);
        if (i > 0) {
            XOR_Byte2Byte(current_block, Output, 8);
            if (verbose) afficher_64bits("Apres XOR avec le block precedent ==> ", Output);
            DES_ENC(Output, Output, (unsigned char*)k1);
        }
        else { DES_ENC(current_block, Output, (unsigned char*)k1); }
        if (verbose) afficher_64bits("Apres cryptage par Ks1 ==> ", Output);
    }
    DES_DEC(Output, Output, (unsigned char*)k2);
    if (verbose) afficher_64bits("Apres decryptage par Ks2 ==> ", Output);
    DES_ENC(Output, Output, (unsigned char*)k3);
    if (verbose) afficher_64bits("Apres cryptage par Ks3 ==> ", Output);
    printf("CBC-MAC         = %x %x %x %x %x %x %x %x\n", Output[0], Output[1], Output[2], Output[3], Output[4], Output[5], Output[6], Output[7]);
    int pause = 0;
}

class Connection_U98 {
    private:
        const_PSC cst_PSC;
        unsigned char Key1[8];
        unsigned char Key2[8];
        unsigned char Key3[8];

        unsigned char Ks1[8] = { 0,0,0,0, 0,0,0,0 };
        unsigned char Ks2[8] = { 0,0,0,0, 0,0,0,0 };
        unsigned char Ks3[8] = { 0,0,0,0, 0,0,0,0 };

        int initiator_etcs_id=0;
        int responder_etcs_id=0;
        int responder_type = 192;

        bool is_connnection1;

        unsigned char RandomA[8] = { 0,0,0,0, 0,0,0,0 };
        unsigned char RandomB[8] = { 0,0,0,0, 0,0,0,0 };

        void compute_session_key(unsigned char random_number[8], unsigned char session_key[8], bool reverse)  {
            if (reverse) {
                DES_ENC(random_number, session_key, this->Key3);
                DES_DEC(session_key, session_key, this->Key2);
                DES_ENC(session_key, session_key, this->Key1);
            }
            else {
                DES_ENC(random_number, session_key, this->Key1);
                DES_DEC(session_key, session_key, this->Key2);
                DES_ENC(session_key, session_key, this->Key3);
            }
        }

    public:
        Connection_U98(unsigned char K1[8], unsigned char K2[8], unsigned char K3[8], int initiator, int responder, int resp_type = 192, bool is_cnx1=true) {
            for (int i = 0; i < 8; i++) {
                Key1[i] = K1[i];
                Key2[i] = K2[i];
                Key3[i] = K3[i];
            }
            initiator_etcs_id = initiator;
            responder_etcs_id = responder;
            responder_type = resp_type;
            is_connnection1 = is_cnx1;
        }

        void start_session(unsigned char RA[8], unsigned char RB[8]) {
            unsigned char RA_L_RB_L[8];
            unsigned char RA_R_RB_R[8];

            for (int i = 0;i < 4;i++) {
                this->RandomA[i] = RA[i];
                this->RandomB[i] = RB[i];
                RA_L_RB_L[i] = RA[i];
                RA_L_RB_L[i + 4] = RB[i];

                this->RandomA[i + 4] = RA[i + 4];
                this->RandomB[i + 4] = RB[i + 4];
                RA_R_RB_R[i] = RA[i + 4];
                RA_R_RB_R[i + 4] = RB[i + 4];
            }

            this->compute_session_key(RA_L_RB_L, this->Ks1, false);
            this->compute_session_key(RA_R_RB_R, this->Ks2, false);
            this->compute_session_key(RA_L_RB_L, this->Ks3, true);



            Redond Bx_r;
            if (is_connnection1) {
                cout << "Connection numero 1 :" << endl;
                Bx_r = cst_PSC.Unisig_98_Hard(3);
            } else {
                cout << "Connection numero 2 :" << endl;
                Bx_r = cst_PSC.Unisig_98_Hard(13);
            }
            cout << endl;
            afficher_64bits("Session Key1        : ", Ks1);
            afficher_64bits("Session Key2        : ", Ks2);
            afficher_64bits("Session Key3        : ", Ks3);
            cout << endl;

            Redond r1_redond = cst_PSC.calculer_redond_tableau8(RA_L_RB_L, Bx_r, true);
            Redond r2_redond = cst_PSC.calculer_redond_tableau8(RA_R_RB_R, Bx_r, true);

            afficher_hexa("Random number 1 :", RA_L_RB_L);
            cout << " Redond Random1 = "; r1_redond.afficher(); cout << endl;
            afficher_hexa("Random number 2 :", RA_R_RB_R);
            cout << " Redond Random2 = "; r2_redond.afficher(); cout << endl;
            afficher_hexa("Random number 3 :", RA_L_RB_L); // r3 = r1
            cout << " Redond Random3 = "; r1_redond.afficher(); cout << endl; // r3 = r1
            cout << endl << "connection etablie ..." << endl << endl;
        }

        void compute_input_MAC_AU2(unsigned char output[8]) {

            cout << "computing G_INPUT_MAC_AU2 ";
            if (is_connnection1) { cout << "for connection 1"; }
            else { cout << "for connection 2"; }
            cout << " ..." << endl;

            unsigned char AU2_bloc1[8] = { 0,0,0,0, 0,0,0,0 };
            unsigned char AU2_bloc2[8] = { 0,0,0,0, 0,0,0,0 };
            unsigned char AU2_bloc3[8] = { 0,0,0,0, 0,0,0,0 };
            unsigned char AU2_bloc4[8] = { 0,0,0,0, 0,0,0,0 };

            unsigned char Initiator_Etcs_Id[3];
            unsigned char Responder_Etcs_Id[3];

            int remaining_value1 = this->initiator_etcs_id;
            int remaining_value2 = this->responder_etcs_id;
            for (int i = 0; i < 3; i++) {
                Initiator_Etcs_Id[2-i] = remaining_value1 % 256;
                remaining_value1 = remaining_value1 / 256;
                Responder_Etcs_Id[2-i] = remaining_value2 % 256;
                remaining_value2 = remaining_value2 / 256;
            }

            // Creation de G_MAC_INPUT_AU2
            AU2_bloc1[0] = 0;
            AU2_bloc1[1] = 27; // longueur
            for (int i = 0; i < 3; i++) AU2_bloc1[i + 2] = Initiator_Etcs_Id[i]; // DA
            AU2_bloc1[5] = this->responder_type + 5; // ETY + MTI + DF // ETY = 1*(2^5) (TFH) ou 6*(2^5) (TE) , MTY=2*(2^1), DF=1
            for (int i = 0; i < 3; i++) { // SA
                if (i + 6 < 8) { AU2_bloc1[i + 6] = Responder_Etcs_Id[i]; }
                else { AU2_bloc2[i - 2] = Responder_Etcs_Id[i]; }
            }
            AU2_bloc2[1] = 1;
            for (int i = 0; i < 8; i++) { // RA
                if (i + 2 < 8) { AU2_bloc2[i + 2] = RandomA[i]; }
                else { AU2_bloc3[i - 6] = RandomA[i]; }
            }
            for (int i = 0; i < 8; i++) { // RB
                if (i + 2 < 8) { AU2_bloc3[i + 2] = RandomB[i]; }
                else { AU2_bloc4[i - 6] = RandomB[i]; }
            }
            for (int i = 0; i < 3; i++) AU2_bloc4[i + 2] = Initiator_Etcs_Id[i]; // DA (=B)
            for (int i = 5; i < 8; i++) AU2_bloc4[i] = 0; // padding
            // fin de la creation de G_MAC_INPUT_AU2

            afficher_64bits("bloc1 (msg AU2) = ", AU2_bloc1);
            afficher_64bits("bloc2 (msg AU2) = ", AU2_bloc2);
            afficher_64bits("bloc3 (msg AU2) = ", AU2_bloc3);
            afficher_64bits("bloc4 (msg AU2) = ", AU2_bloc4);

            calcul_MAC_4Blocks(AU2_bloc1, AU2_bloc2, AU2_bloc3, AU2_bloc4, this->Ks1, this->Ks2, this->Ks3, output);
            cout << endl;
        }

        void compute_Mac_n_Blocks(int nb_bloks, unsigned char Blocks[], unsigned char Output[8]) {
            cout << "CALCUL de MAC à N blocs avec N="<<nb_bloks;
            if (is_connnection1) { cout << " pour connection 1"; } else { cout << " pour connection 2"; }
            cout << endl;

            calcul_MAC_n_Blocks(nb_bloks, Blocks, this->Ks1, this->Ks2, this->Ks3, Output);
        }
};

//------------------------------------------------------------------------------------
int main(int argc, char* argv[]) {

    // AU2 message
    unsigned char Output[8];


    unsigned char Initiator_Etcs_Id[3] = { 32, 128, 45 }; // 44 = ZC_02[A] // 45 = ZC_02[B]
    unsigned char Responder_Etcs_Id[3] = { 32, 128, 43 }; // 42=PAI_75 // 43=PAI_81

    unsigned char RandomA_wshark[8] = { 0x41, 0xb2, 0xf3, 0xe2, 0x4b, 0xa9, 0x9c, 0x20 };          // RA_L | RA_R
    unsigned char RandomB_wshark[8] = { 0x37, 0x59, 0x47, 0xaa, 0xa4, 0xbf, 0x44, 0x97 };          // RB_L | RB_R


    cout << " Test de la classe connection_U98 : " << endl << endl;
    int etcsid_initiateur = 2130068; // 20 80 94
    int etcsid_repondeur = 2130066; // 20 80 92

    Connection_U98 connexion_ZcB_PAI75(Key1_TE, Key2_TE, Key3_TE, etcsid_initiateur, etcsid_repondeur, 192, true); // false => cnx2, true=cnx1
    connexion_ZcB_PAI75.start_session(RandomA_wshark, RandomB_wshark);
    unsigned char MAC_AU2_cnx1[8];
    cout << "Compute AU2. Expected MAC: 35 f7 fa 7a 7b 6a d3 75" << endl;
    connexion_ZcB_PAI75.compute_input_MAC_AU2(MAC_AU2_cnx1);
    afficher_64bits(" MAC AU2 cnx1 --> ", MAC_AU2_cnx1);

    cout << endl; // Calcul à 3 blocs
    cout << "++++ Compute Frame 116789, expected MAC 69 4c b0 e5 63 c6 d4 2c" << endl;
    unsigned char blocks_03[24] = {
        0x00, 0x13, 0x20, 0x80, 0x92, 0x0a, 0x03, 0x3d,
        0xc2, 0x00, 0x05, 0xca, 0xac, 0x00, 0x16, 0x02,
        0x42, 0x00, 0x05, 0xca, 0xac, 0x00, 0x00, 0x00, };

    connexion_ZcB_PAI75.compute_Mac_n_Blocks(3, blocks_03, Output);
    cout << "-----------------------------" << endl << endl;



    cout << endl; // Calcul à 4 blocs
    cout << "Compute Frame 116756, expected MAC: e2 4f 14 ea f4 65 99 54, calcul à 4 blocs" << endl;
    unsigned char blocks_04[32] = {
            0x00, 0x17, 0x20, 0x80, 0x94, 0x0b, 0x02, 0x00,
            0x00, 0x00, 0x16, 0x02, 0x42, 0x00, 0x05, 0xca,
            0x64, 0x00, 0x16, 0x02, 0x42, 0x00, 0x00, 0x00,
            0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };

    connexion_ZcB_PAI75.compute_Mac_n_Blocks(4, blocks_04, Output);
    cout << "-----------------------------" << endl << endl;

    return 0;
}