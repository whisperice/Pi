/*
 * main_c.h
 *
 *  Created on: 2017Äê7ÔÂ31ÈÕ
 *      Author: Ziwei Lan; Yitao Deng
 */

#ifndef MAIN_C_H_
#define MAIN_C_H_

#include "msp430.h"
#include <math.h>
#include <stdint.h>

//#define THRESHOLD 100000            		// Energy Threshold value for LED blink
#define DC_OFFSET_CURRENT 0				// Offset for current calculation
#define DC_OFFSET_VOLTAGE 0				// Offset for the voltage calculation
#define Num_of_Results 32
//#define LED 0

void uartInit();
void transmitByte(int8_t data);

#endif /* MAIN_C_H_ */
