from pylab import *
import time

X = np.linspace(-np.pi, np.pi, 256,endpoint=True)
C,S = np.cos(X), np.sin(X)

fig=figure()
plot(X,C)
show(block=False)
#hold(True)
close(fig)
plot(X,S)
show(block=False)

time.sleep(5)

