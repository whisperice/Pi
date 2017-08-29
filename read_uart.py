import serial

ser = serial.Serial ("/dev/ttyS0")    #Open named port 
ser.baudrate = 76800                     #Set baud rate to 9600

while True:

    data = ser.read(2)                  #Read 2 characters from serial
	
	print(data[0])
	print(data[1])
	
	volt = data[1]*2**8 + data[0]
	if volt > 2**15
		volt -= 2**16
	print(volt)


ser.close()
