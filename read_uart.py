import serial

ser = serial.Serial ("/dev/ttyS0")    #Open named port 
ser.baudrate = 76800                     #Set baud rate to 76800

while True:

    data = ser.read(6)                  #Read 6 characters from serial
	
	for raw in data:
		print(bin(raw))
	
	volt = data[1] << 8 + data[0]
    if volt > 2**15:
        volt -= 2**16
    print(volt)
    volt = volt/32767.0*600.0
	print(str(volt)+' V')

	curr = data[3] << 8 + data[2]
    if curr > 2**15:
        curr -= 2**16
    print(curr)
    curr = curr/32767.0*600.0
	print(str(curr)+' A')
    
	time = data[5] << 8 + data[4]
	print(str(time)+' us')

	
ser.close()



