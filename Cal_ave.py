import sys
import os

f = open('data_PS.txt','r')
fr = open('ave_re.txt','w')
Vlist = []
Ilist = []
Tlist = []
f.readline()

for line in f.readlines():
    V, I, T = line.split()
    Vlist.append(float(V))
    Ilist.append(float(I))
    Tlist.append(float(T))

Vave = 0
for item in Vlist:
    Vave += item
Vave /= len(Vlist)

Iave = 0
for item in Ilist:
    Iave += item
Iave /= len(Ilist)

fr.write('{}\t{}'.format(Vave,Iave))
f.close()
fr.close()
