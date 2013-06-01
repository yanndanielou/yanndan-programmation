#define VAR_GLOBALES_MODEM_SI2457
#include "modem_si2457.h"
#include "tempo.h"
#include "c2_pass.h"
#include "gestion_evenements.h"
#include "usart.h"

unsigned char TIMER_INIT_MODEM = 0;
unsigned char TIMER_RESET_MODEM = 0;	// pour g�n�rer le reset sur la broche RESET_SI2457
unsigned char TIMER_CONNEXION_MODEM = 0;



void modem_si2457_init (void)
{

}

void f_PAS_DE_CABLE_PC(void)
{
	FLAG_MODEM_SI2457Bits.Bits.f_MODEM_RESET = 1;	//Ce flag annonce que le modem effecue un RESET
	
	RESET_SI2457 = 0; //Etat bas 3b7
	
	TIMER_RESET_MODEM = 55;
}

void RESET_MODEM_HARD_int10ms(void)
{
	// Est-ce qu'on doit g�rer la broche RESET du modem ?
	if(FLAG_MODEM_SI2457Bits.Bits.f_MODEM_RESET == 1)
	{
		TIMER_RESET_MODEM--;
		
		//Attendre 50ms , RESET_SI2457 = 0
		if(TIMER_RESET_MODEM < 50)
		{
			//200ms �coul�,
			//On passe RESET_SI2457 � l'�tat haut, red�marrage du MODEM
			RESET_SI2457 = 1; //3b7
		
			//Attendre 500 ms restante, pour son init, la ligne est toujours d�croch� pour �viter les "RING"
			if(TIMER_RESET_MODEM == 0)
			{
				//Le modem � termin� son RESET
				FLAG_MODEM_SI2457Bits.Bits.f_MODEM_RESET = 0;
			}
		}
	}
}

void RESET_MODEM_HARD_noint(void)
{
	FLAG_MODEM_SI2457Bits.Bits.f_MODEM_RESET = 1;
	PRISE_DE_LIGNE = 1;	//d�crochage, pour eviter les "RING" sur le bus
	RESET_SI2457 = 0;	//3b7

	//Attendre environ 200 ms
	tempo_100ms();
	tempo_100ms();
	
	RESET_SI2457 = 1; //3B7
	
	//Attendre 500 ms
	tempo_100ms();
	tempo_100ms();
	tempo_100ms();
	tempo_100ms();
	tempo_100ms();
	
	FLAG_MODEM_SI2457Bits.Bits.f_MODEM_RESET = 0;
	PRISE_DE_LIGNE = 1;	//raccrochage. FIXME: devrait �tre 0 (bug dans asm)
}

void INIT_MODEM_int1s(void)
{
	//appeler toutes les secondes
	//INIT_MODEM_int1s
	if(FLAG_MODEM_SI2457Bits.Bits.f_MODEM_CONNECTE == 0)
	{
		//no_conect
		if(TIMER_INIT_MODEM > 0)
			TIMER_INIT_MODEM--;
			
		if(TIMER_INIT_MODEM == 0)
		{
			/* Est ce qu'on doit faire une INIT ?
			oui si :
			-  un modem � �t� detect�
				&& le cable PC n'est pas branch�
				&& le modem n'est pas connect�
				&& on n'est pas en train de recevoir un appel
				&& le modem n'est pas dans la phase de reinitialisation pour une communication avec un modem distant
				&& le modem n'est en train de se synchroniser
			*/
			
			if(	FLAG_MODEM_SI2457Bits.Bits.f_MODEM_DETECTE == 1			&&
			//	FLAG_MODEM_SI2457Bits.Bits.f_PAS_DE_CABLE_PC == 1 			&&
				FLAG_MODEM_SI2457Bits.Bits.f_MODEM_CONNECTE == 0			&&
				FLAG_MODEM_SI2457Bits.Bits.f_RING_EN_COURS == 0			&&
				FLAG_MODEM_SI2457Bits.Bits.f_MODEM_RESET_HARD_SYNC == 0	&&
				FLAG_MODEM_SI2457Bits.Bits.f_MODEM_ATA_ENCOURS == 0)
			{
				FLAG_MODEM_SI2457Bits.Bits.f_MODEM_INIT = 1;
				reset_modem_hard();				
			}
			
		}
			
	}
	else if(TIMER_CONNEXION_MODEM == 1)
	{
		//timeout
		//reset
	}
	else
	{
		//no_timeout
		if(TIMER_CONNEXION_MODEM > 0)
			TIMER_CONNEXION_MODEM--;
	}
}


void SHUTDOWN_MODEM(void)
{
	RESET_SI2457 = 0; //3B7
	
	// RESET 2 secondes apr�s avoir retirer le cable
	START_RESET_MODEM(2);
}

void START_RESET_MODEM(char seconds)
{
	TIMER_INIT_MODEM = seconds;
}

void reset_modem_hard(void)
{
	FLAG_MODEM_SI2457Bits.Bits.f_MODEM_RESET = 1;
	RESET_SI2457 = 0;
	TIMER_RESET_MODEM = 55;
}

void INIT_MODEM_IDCALLER(void)
{
//	FLAG_MODEM_SI2457Bits.Bits.f_SMS_FRM_ENVOYE = 0;
//	FLAG_MODEM_SI2457Bits.Bits.f_SMS_ATDT_EN_COURS = 0;	
	
	const char AT_INIT[]="ATE0V0S0=0X0\\V2+GCI=3D\r";
	const char AT_IDCALLER_ON[]="AT+VCDT=1\r";
	const char AT_IDCALLER_FORMAT[]="AT+VCID=1\r";
	const char AT_U67[]="AT:U67,0008\r";		//Parametre de la ligne
	const char AT_ATA[]="ATA\r"	; // D�crocher et synchroniser avec le modem distant
//	const char AT_INIT[]="ATE0V0S0=0X0\\V2+GCI=3D\r";
	
	ENTER_CRITICAL();	
	usart1_send_at(AT_INIT);
	EXIT_CRITICAL();
}

/****************************
;***  Detection du modem  ***
;****************************
Appeler seulement au demarrage de la platine
 M�thode :
 - Effectuer un RESET hard
 - Envoyer "\r"
 - Recevoir l'echo avec timeout de 200 ms (reponse mesur� � 54ms)
 - Si aucun echo re�u, il n'y a pas de modem */
void DETECT_MODEM(void)
{
	unsigned char vidage_buffer = 0;
	unsigned char i = 200;	//200 ms de timeout
	unsigned char caractere_recu = 0;
	unsigned char modem_detecte = 0;

	//RESET hard du modem
	ENTER_CRITICAL();	
	RESET_MODEM_HARD_noint();
	EXIT_CRITICAL();
	
	//Vider le bufer de r�ception
	vidage_buffer = RCREG1;
	
	//Envoyer le \r
	usart1_putc('\r');
	
	//loop
	while(	i-- > 0 && PIR1bits.RCIF == 0);
	
	if(PIR1bits.RCIF == 1)
	{
		//char_recu
		caractere_recu = RCREG1;
		if(caractere_recu == '\r')
		{
			//OK le modem est l�
			modem_detecte = 1;
		}
	}
	

	if(modem_detecte == 0)
	{
		// Pas de modem sur la carte
		FLAG_MODEM_SI2457Bits.Bits.f_MODEM_DETECTE = 0;
		RESET_SI2457 = 0; //3b7
	}
	else
	{
		FLAG_MODEM_SI2457Bits.Bits.f_MODEM_DETECTE = 1;

		//Eteindre le modem pour le moment (ne pas recevoir de "RING\r")
		RESET_SI2457 = 0; //3b7
			
		START_RESET_MODEM(2);	
	}
	
}

