import serial

ser = serial.Serial ("/dev/ttyS0")    #Open named port 
ser.baudrate = 76800                     #Set baud rate to 76800
volt=[0 for i in range(0,20)]
curr=[0 for i in range(0,20)]
time=[0 for i in range(0,20)]
numPoint=20
totalEnergy=0

while True:
	power=0
	energy=0
	period=0

	for i in range(0,numPoint):
		data = ser.read(6)                  #Read 6 characters from serial
		
		for raw in data:
			print(bin(raw))
		
		volt[i] = data[1] << 8 + data[0]
		if volt[i] > 2**15:
			volt[i] -= 2**16
		volt[i] = volt[i]/32767.0*600.0
		print('volt= '+str(volt[i])+' V')

		curr[i] = data[3] << 8 + data[2]
		if curr[i] > 2**15:
			curr[i] -= 2**16
		curr[i]= curr[i]/32767.0*600.0
		print('curr= '+str(curr)+' A')
		
		time[i] = data[5] << 8 + data[4]
		print('time= '+str(time[i])+' us')
		
		power += volt[i]*curr[i]
		period += time[i]

	#electricity calculation
	energy = energy/numPoint*(period/10**6)
	print('energy in the last period ='+str(energy)+' J')
	
	totalEnergy += energy
	print('totalEnergy= '+str(totalEnergy)+' J')
	
ser.close()



