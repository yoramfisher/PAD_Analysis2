#Bias_Anal.py created by BWM 8/31/22
#program to analyze keck data while varying DAC bias voltages

import numpy as np
import Big_keck_load as BKL
import os
import matplotlib.pyplot as plt
import sys


cwd = os.getcwd()
imageData = open(cwd +"\\KeckData\\fore.raw","rb")
numImages = int(os.path.getsize(cwd +"\\KeckData\\fore.raw")/(1024+512*512*2))
backStack = np.zeros((numImages,8,512,512),dtype=np.double)


#read all the image files
for fIdex in range(numImages):
   payload = BKL.keckFrame(imageData)
   backStack[(payload[5]-1),(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512])

# avgBack = backStack/(numImages/8.0)
capPlot = ()
capPlot2 = ()
listBias = ()
#values set for ISSB Change range for vRef scan
# for junk in range(8):
#    for val in range (10):      # number of daughter folders
#       BiasV = (val + 1) *100 + 900       # range of voltages you used 
#       listBias = np.append(listBias, BiasV)

#       foreImageData = open("/mnt/raid/keckpad/set-" + pFolder +"/run-scan_" + dFolder + "_"+ str(BiasV) + "/frames/scan_"+ dFolder + "_" + str(BiasV) +"_00000001.raw","rb")
#       foreStack = np.zeros((80,8,512,512),dtype = np.double)
#       numImagesFore = int(os.path.getsize("/mnt/raid/keckpad/set-" + pFolder +"/run-scan_" + dFolder + "_"+ str(BiasV) + "/frames/scan_"+ dFolder + "_" + str(BiasV) +"_00000001.raw")/(1024+512*512*2))

#       #Calc cap backs
#       for fIdex in range(numImages):
#          payloadFore = Big_keck_load.keckFrame(foreImageData)
#          foreStack[((payloadFore[5]-1),payloadFore[3]-1)%8,:,:] += np.resize(payloadFore[4],[512,512])

#       # avgFore = foreStack/(numImages/8.0)

#       #not background subtracting image
#       # fmb = foreStack

   
#       Cap = junk
#       capAvg = np.mean(fmb[Cap,,291:364,173:240])      # second module down on the right, L ASIC 
#       capAvg2 = np.mean(fmb[Cap,411:484,158:225])      # second module down on the right, R ASIC 
#       capPlot = np.append(capPlot, capAvg)
#       capPlot2 = np.append(capPlot2, capAvg2)

fNum = 65
plotData = backStack[:,:,:,:]
#plotData = np.average(plotData, axis=1)
plotData = np.average(plotData, axis=0)
# plotData = plotData[4,:,:]
# plt.imshow(plotData)
# plt.show()  
# plt.close()

fig,axs = plt.subplots(2,4)
axs[0,0].imshow(plotData[0,:,:])
axs[0,1].imshow(plotData[1,:,:])
axs[0,2].imshow(plotData[2,:,:])
axs[0,3].imshow(plotData[3,:,:])
axs[1,0].imshow(plotData[4,:,:])
axs[1,1].imshow(plotData[5,:,:])
axs[1,2].imshow(plotData[6,:,:])
axs[1,3].imshow(plotData[7,:,:])
#plt.imshow(fmb[3,:,:])
plt.show()