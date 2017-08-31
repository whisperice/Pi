#include <msp430.h> 
#include <main_c.h>
#include <math.h>
#include <stdint.h>

//-------------------Global Variables--------------------//
int16_t vadc;                     	 						// Used for storing SD24 conversion results
int16_t iadc;
uint8_t vh, vl, ih, il, th, tl;
uint16_t timerCount;
uint8_t data;
uint32_t ledcounter = 0;                    				// Used for blinking LED
double results[Num_of_Results];
volatile unsigned int i;
int index=0;
//--------------------- main.c--------------------------//
int main(void) {
    WDTCTL = WDTPW | WDTHOLD;	                         // Stop watchdog timer
	
    //clock setting---------------------------------------
    //ACLK - Auxiliary clock, sourced from the VLO
    //MCLK - Main clock, system clock used by cpu
    //SMCLK - Sub-Main clock, the sub-system clock used by the peripheral modules
    if (CALBC1_8MHZ == 0xFF || CALDCO_8MHZ == 0xFF) {    // Traps the CPU if the callibration data has been erased
    		while(1);
    	}

    BCSCTL1 = CALBC1_8MHZ;								 // Calibrates BCSCTL1 for a DCO of 8MHz,ACLK /1 selected
    DCOCTL = CALDCO_8MHZ;								 // Set DCO to 8MHz

    BCSCTL3 |= LFXT1S_2;		                         //VLOCK enable
    /*Note here that SMCLK is sourced directly from the DCO. A
    division in MCLK will not affect the SMCLK frequency. */

    BCSCTL2 |= DIVS_1;                                   //Set MCLK=DCO=8MHz and SMCLK=DCO/2=4MHz


	// Oscillator fault handling------------------------m----
    P1SEL |= BIT3 + BIT4;             				     // Set Pin 1.3,4 to be USART0 TXD/RXD
    do {
		IFG1 &= ~OFIFG;                       			 // Clear OSCFault flag
		for (i = 0x47F; i > 0; i--)
			;          									 // Time for flag to set
	} while (IFG1 & OFIFG);								 // While OSCFault flag still set

	uartInit();      								     // Initialize USART state machine


	// LED (P1.0)--------------------------------------------
	SETBIT(P1DIR,LED);				  		     // Set the direction of P1.0 as an output for LED
	CLEARBIT(P1OUT,LED);						 // Set output of P1.0 to 0


	// Configure ADC----------------------------------------
	SD24CCTL0 &= ~SD24SC;                                //No conversion before ADC initialization
	SD24CCTL1 &= ~SD24SC;
	SD24CTL = SD24REFON + SD24SSEL0 + SD24DIV_2;         // Set internal reference on and ADC Clock=SMCLK/4=1MHz
	// ADC Channel 0 (Current)
	//SD24CCTL0 |= SD24OSR_1024 + SD24GRP;
	SD24CCTL0 |= SD24OSR_1024 + SD24GRP + SD24DF;        // OSR = 1024 (around 977Hz) , output data format to be continuous bipolar 2's compliment
	// ADC Channel 1 (Voltage)
	//SD24CCTL1 |= SD24OSR_1024 + SD24IE;
	SD24CCTL1 |= SD24OSR_1024 + SD24IE + SD24DF; 	     // Set as master, OSR = 1024 (around 977Hz), enable interrupt Enable, 2s complement and
	for (i = 0; i < 0x3600; i++);                        // Delay for 1.2V ref startup

	TACTL = TASSEL_2 | ID_2; 							 // Set timer clock=SMCLK/4=1MHz
	
	SD24CCTL1 |= SD24SC;                                 // Set bit to start conversion


	//  Enable Global Interrupts--------------------------------
	__bis_SR_register(GIE);


	//  Wait for interrupts
	while (1) {
		_nop();                                          // Loop forever and wait for interrupts
	}
}


//---------------------- Sigma-Delta ADC interrupt routine--------------------------//
#pragma vector=SD24_VECTOR
__interrupt void SD24AISR(void) {
	switch (SD24IV) {
		case 2: // SD24MEM Overflow
			break;
		case 4: // SD24MEM0 IFG
			break ;
		case 6:
			TACTL |= MC_0;                          //Stop mode: the timer is halted.

			vadc = SD24MEM1 + DC_OFFSET_VOLTAGE;	// Get voltage sample from SD24MEM1
			iadc = SD24MEM0 + DC_OFFSET_CURRENT;	// Get current sample from SD24MEM0
			timerCount = TAR;                       // Get time from TAR
			TACTL |= TACLR;                         //Resets TAR, the clock divider, and the count direction.
			TACTL |= MC_2;                          //Continuous mode: the timer counts from zero to 0FFFFh.
			
 			vl = vadc & 0xFF;
			vh = vadc >> 8;
			il = iadc & 0xFF;
			ih = iadc >> 8;
			tl = timerCount & 0xFF;
			th = timerCount >> 8;
			
			// Transmit data
			transmitByte(vl);
			transmitByte(vh);
			transmitByte(il);
			transmitByte(ih);
			transmitByte(tl);
			transmitByte(th);
           
			/*            
			results[index]=(vadc/32767.0)*600.0;
            index++;
            if(index==Num_of_Results)
                index=0;
			
			//MPYS = vadc;          								// Signed 16-bit Hardware Multiplier
			//OP2 = iadc;
			//result = RESHI;
			//result = (result << 16) | RESLO;
			//ledcounter += result;

			if (ledcounter > THRESHOLD) {
				TOGGLEBIT(P1OUT, LED);			 			    // Blink LED when threshold is crossed
				ledcounter = 0;									// Reset blink counter
			

			// Transmit data
			transmitByte(vh);
			transmitByte(vl);
			transmitByte(ih);
			transmitByte(il);
			transmitByte(th);
			transmitByte(tl);*/
	//		transmitByte(crc);
	}
}

//----------------------Configure UART--------------------------//
void uartInit(void)
{
	U0CTL |= SWRST;                             // USART Software Reset
	U0CTL |= CHAR;	             			    // Set 8-bit character, no parity bit, one stop bit
	ME1 = UTXE0 | URXE0;						// Module Enable Register, Enable USART0 TXD/RXD
	U0TCTL |= SSEL1;                            // BRCLK = SMCLK = 4MHz
	U0BR0 = 0x34;                             	// Set Baud rate = 76800 bits/sec
	U0BR1 = 0x00;								//http://mspgcc.sourceforge.net/cgi-bin/msp-uart.pl?clock=4000000&baud=76800&submit=calculate
	U0MCTL = 0x40;    	                    	// Modulation control to minimize data errors; Divider=52.1
	U0CTL &= ~SWRST;                            // Initialize USART state machine
	IE1 |= URXIE0;								// Enable UART RX interrupt
}


//-----------------UART Transmission Functions-------------------//
void transmitByte(int8_t data) {
	while (IFG1 & UTXIFG0);                  	// USART0 TX buffer ready?
	U0TXBUF = data;
}



