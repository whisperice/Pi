import serial
from pylab import *
import RPi.GPIO as GPIO

LED = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)

ser = serial.Serial ("/dev/ttyS0")    #Open named port 
ser.baudrate = 76800                     #Set baud rate to 76800
volt=[0 for i in range(0,20)]
curr=[0 for i in range(0,20)]
time=[0 for i in range(0,20)]
timeAxis=[]
voltAxis=[]
currAxis=[]
numPoint=20
RI=7.5
CTR=2500.0
RVL=1600.0
RVH=1200000.0
Mul=300.0
totalEnergy=0
groupIndex=0
#threshold and pulseTime need to be proper value to make blinds separated
threshold=100 #Led blind every 100J
pulseEneney=0 #record the energy make Led blink
pulseTime=100 #max time (per whlie loop,about 1ms) for Led pulse
cnt=0 #count for pulse time
f = open('data.txt','w')
fenergy = open('energy.txt','w')

f.write('volt/V\t\t\tcurr/A\t\t\ttotaltime/us\n')
fenergy.write('energy/J\t\ttotalEnergy/J\n')

while True:
	power=0
	energy=0
	period=0

	for i in range(0,numPoint):
		data = ser.read(6)                  #Read 6 characters from serial
		'''
		for raw in data:
			print(bin(raw))
		'''
		volt[i] = data[1]*2**8+ data[0]
		if volt[i] > 2**15:
			volt[i] -= 2**16
		#volt[i] = volt[i]/32767.0*600.0
		volt[i] = (volt[i]/32767.0*600.0)/RVL*(RVH+RVL)/1000
		#print('volt= '+str(volt[i])+' V')

		curr[i] = data[3]*2**8 + data[2]
		if curr[i] > 2**15:
			curr[i] -= 2**16
		#curr[i]= curr[i]/32767.0*600.0
		#curr[i]= (curr[i]/32767.0*600.0)/RI*CTR/1000
		curr[i]= (curr[i]/32767.0*600.0)/RI*CTR/1000*Mul
		#print('curr= '+str(curr[i])+' A')
		
		time[i] = data[5]*2**8 + data[4]
		#print('time= '+str(time[i])+' us')

		if len(timeAxis)==0:
			timeAxis.append(time[i])
		else:
                        timeAxis.append(timeAxis[-1]+time[i])                    
		#print('timeAxis= '+str(timeAxis[-1])+' us')
		
		#power += volt[i]*curr[i]
		power += volt[i]*curr[i]/Mul
		period += time[i]


        #volt and curr plots
	for i in range(0,numPoint):
                voltAxis.append(volt[i])
                currAxis.append(curr[i])
	if len(voltAxis)>100:
                del voltAxis[0:20]
                del currAxis[0:20]
                del timeAxis[0:20]
	plot(timeAxis,voltAxis)
	plot(timeAxis,currAxis)
	savefig('curve{}.png'.format(groupIndex))
	groupIndex += 1
	if groupIndex%20 == 0:
                close('all')
	#show(block=False)
	#electricity calculation
	energy = power/numPoint*(period/10**6)
	#print('energy in the last period ='+str(energy)+' J')
	
	totalEnergy += energy
	#print('totalEnergy= '+str(totalEnergy)+' J')

        #set Led
	pulseEnergy += energy
	cnt += 1
	if pulseEnergy > threshold:
                GPIO.output(LED, GPIO.HIGH)
                pulseEnergy -= threshold
                cnt=0
        if cnt == pulseTime:
                GPIO.output(LED, GPIO.LOW)                
	
	#record datas
	for i in range(0,numPoint):
		f.write(str(volt[i])+'\t'+str(curr[i])+'\t'+str(timeAxis[-(20-i)])+'\n')
	fenergy.write(str(energy)+'\t'+str(totalEnergy)+'\n')
	f.flush
	fenergy.flush

f.close()
fenergy.close()
ser.close()



