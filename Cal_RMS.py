import sys
import os
import math

f = open('data_PS.txt','r')
fr = open('RMS_re.txt','w')
Vlist = []
Ilist = []
Tlist = []
f.readline()

n = 0
for line in f.readlines():
    V, I, T = line.split()
    Vlist.append(float(V))
    Ilist.append(float(I))
    Tlist.append(float(T))
    n += 1

Vave = 0
for item in Vlist:
    Vave += item**2
Vave = math.sqrt(Vave/n)

Iave = 0
for item in Ilist:
    Iave += item**2
Iave = math.sqrt(Iave/n)

fr.write('{}\t{}'.format(Vave,Iave))
f.close()
fr.close()
