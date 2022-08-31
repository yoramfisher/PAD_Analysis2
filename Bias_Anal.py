#Bias_Anal.py created by BWM 8/31/22
#program to analyze keck data while varying DAC bias voltages

import numpy as np
import Big_keck_load 
import os
import matplotlib.pyplot as plt
import sys


cwd = os.getcwd()

backImageData = open(cwd +"\\PAD_Anal\\KeckData\\back.raw","rb")

backStack = np.zeros((8,512,512),dtype=np.double)
numImages = int(os.path.getsize(cwd +"\\PAD_Anal\\KeckData\\back.raw")/(1024+512*512*2))

#Calc cap backs
for fIdex in range(numImages):
   payload = Big_keck_load.keckFrame(backImageData)
   backStack[(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512])

avgBack = backStack/(numImages/8.0)

foreImageData = open(cwd +"\\PAD_Anal\\KeckData\\fore.raw","rb")
foreStack = np.zeros((8,512,512),dtype = np.double)
numImagesFore = int(os.path.getsize(cwd +"\\PAD_Anal\\KeckData\\fore.raw")/(1024+512*512*2))

#Calc cap backs
for fIdex in range(numImages):
   payloadFore = Big_keck_load.keckFrame(foreImageData)
   foreStack[(payloadFore[3]-1)%8,:,:] += np.resize(payloadFore[4],[512,512])

avgFore = foreStack/(numImages/8.0)
capPlot = ()
capPlot2 = ()
fmb = foreStack - backStack
for caps in range (8):
  capAvg = np.mean(fmb[caps%8,0:127,256:384])
  capAvg2 = np.mean(fmb[caps%8,128:256,384:512])
  capPlot = np.append(capPlot, capAvg)
  capPlot2 = np.append(capPlot2, capAvg)
y = range(8)

plt.scatter(y,capPlot)
plt.scatter(y,capPlot2+100)
plt.show()  

fig,axs = plt.subplots(1)
# axs[0].imshow(avgBack[1,:,:])
plt.imshow(fmb[3,:,:])
plt.show()