#Created BWM 7/29/22
#Program to load in TXC files and do some analysis to them 

from datetime import datetime
from pytz import timezone
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import os

dt = np.dtype('int32')
data = np.fromfile("/Users/benm/Documents/GitHub/ScratchPad/LongScan1.raw", dtype = dt)
dSize = np.size(data)
imageTotal = int(dSize / 1024)
print ('Total # images')
print(imageTotal)
print ("the total average of all data")
totalframeAvg = np.average(data)
print (totalframeAvg)
frameAvg = np.array(0)
print(range(imageTotal))
for i in range(imageTotal):
    imStart = (i-1)*1024
    imEnd = i * 1024
    image = data[imStart:imEnd]
    #data2d = image.reshape(32,32)
    iAvg = (np.average(image))
    #print(np.average(image))
    frameAvg = np.append(frameAvg,iAvg) 
#print (data2d)

plt.plot(frameAvg)
plt.show()
#print(frameAvg)