import numpy as np
import matplotlib.pyplot as plt


t1 = [ 0, 0.2,  0.4,  0.6,  0.8,  1,   1.2,  1.4,  1.6,  1.8,  2,   2.2,  2.4 , 2.6 , 2.8,  3,   3.2,  3.4,  3.6,  3.8 , 4,   4.2,  4.4,  4.6,  4.8]
t2=[]
for t in t1:
    t2.append(t+2)
plt.plot(t1,'.')
plt.plot(t2)
plt.show()