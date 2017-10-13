#import
import RPi.GPIO as GPIO
import time
import serial

ser = serial.Serial ("/dev/ttyS0")    #Open named port 
ser.baudrate = 76800                     #Set baud rate to 76800
volt=[0 for i in range(0,20)]
curr=[0 for i in range(0,20)]
time=[0 for i in range(0,20)]
numPoint=20
RI=7.5
CTR=2500.0
RVL=1600.0
RVH=1200000.0
Mul=300.0
totalEnergy=0
lastTime=0
LCDPower=0
LCDEnergy=0

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18


# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

def main():
  # Main program block
  
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7


  # Initialise display
  lcd_init()
  lcd_string("Rasbperry Pi",LCD_LINE_1)
  lcd_string("16x2 LCD",LCD_LINE_2)
   
  while True:
  
    # Send some test
	power=0
	energy=0
	period=0

	for i in range(0,numPoint):
		data = ser.read(6)                  #Read 6 characters from serial
		volt[i] = data[1]*2**8+ data[0]
		if volt[i] > 2**15:
			volt[i] -= 2**16
		volt[i] = (volt[i]/32767.0*600.0)/RVL*(RVH+RVL)/1000
		#print('volt= '+str(volt[i])+' V')

		curr[i] = data[3]*2**8 + data[2]
		if curr[i] > 2**15:
			curr[i] -= 2**16
		curr[i]= (curr[i]/32767.0*600.0)/RI*CTR/1000
		#print('curr= '+str(curr[i])+' A')
		
		time[i] = data[5]*2**8 + data[4]
		#print('time= '+str(time[i])+' us')
		
		power += volt[i]*curr[i]
		period += time[i]

	#electricity calculation
	energy = power/numPoint*(period/10**6)
	#print('energy in the last period ='+str(energy)+' J')
	
	totalEnergy += energy
	#print('totalEnergy= '+str(totalEnergy)+' J')
	
	if time[19]-lastTime>=3000000:
		lastTime=time[19]
		LCDPower=round(power,3)
		LCDEnergy=round(totalEnergy,3)
		lcd_string('Power:{}W'.format(LCDPower),LCD_LINE_1)
		lcd_string('Energy:{}J'.format(LCDEnergy),LCD_LINE_2)


		
def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display
  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
	GPIO.cleanup()
    #pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()