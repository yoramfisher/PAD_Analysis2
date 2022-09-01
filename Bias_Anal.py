#Bias_Anal.py created by BWM 8/31/22
#program to analyze keck data while varying DAC bias voltages

import numpy as np
import Big_keck_load 
import os
import matplotlib.pyplot as plt
import sys


cwd = os.getcwd()
pFolder = "vref1"
dFolder = "vref"
backImageData = open("/mnt/raid/keckpad/set-" + pFolder +"/run-" + dFolder + "_Back/frames/"+ dFolder + "_Back_00000001.raw","rb")

backStack = np.zeros((8,512,512),dtype=np.double)
numImages = int(os.path.getsize("/mnt/raid/keckpad/set-" + pFolder +"/run-" + dFolder + "_Back/frames/"+ dFolder + "_Back_00000001.raw")/(1024+512*512*2))

#Calc cap backs
for fIdex in range(numImages):
   payload = Big_keck_load.keckFrame(backImageData)
   backStack[(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512])

avgBack = backStack/(numImages/8.0)
capPlot = ()
capPlot2 = ()
listBias = ()
#values set for ISSB Change range for vRef scan
for junk in range(8):
   for val in range (10):      # number of daughter folders
      BiasV = (val + 1) *100 + 900       # range of voltages you used 
      listBias = np.append(listBias, BiasV)

      foreImageData = open("/mnt/raid/keckpad/set-" + pFolder +"/run-scan_" + dFolder + "_"+ str(BiasV) + "/frames/scan_"+ dFolder + "_" + str(BiasV) +"_00000001.raw","rb")
      foreStack = np.zeros((8,512,512),dtype = np.double)
      numImagesFore = int(os.path.getsize("/mnt/raid/keckpad/set-" + pFolder +"/run-scan_" + dFolder + "_"+ str(BiasV) + "/frames/scan_"+ dFolder + "_" + str(BiasV) +"_00000001.raw")/(1024+512*512*2))

      #Calc cap backs
      for fIdex in range(numImages):
         payloadFore = Big_keck_load.keckFrame(foreImageData)
         foreStack[(payloadFore[3]-1)%8,:,:] += np.resize(payloadFore[4],[512,512])

      avgFore = foreStack/(numImages/8.0)

      #not background subtracting image
      fmb = foreStack

   
      Cap = junk
      capAvg = np.mean(fmb[Cap,291:364,173:240])      # second module down on the right, L ASIC 
      capAvg2 = np.mean(fmb[Cap,411:484,158:225])      # second module down on the right, R ASIC 
      capPlot = np.append(capPlot, capAvg)
      capPlot2 = np.append(capPlot2, capAvg2)


   y = listBias
   plt.scatter(y,capPlot, label='left ASIC')
   plt.scatter(y,capPlot2, label='right ASIC')
   plt.legend();
   plt.xlabel('DAC voltage (mV)');
   plt.ylabel('mean (ADU)');
   plt.title('DAC voltage vs. mean signal for ROIs in Cap' + str(Cap))
   plt.savefig('/mnt/raid/keckpad/set-' + pFolder +'/Cap_' + str(Cap)+ '.png')
   #plt.show()  
   plt.close()

   # fig,axs = plt.subplots(1)
   # # axs[0].imshow(avgBack[1,:,:])
   # plt.imshow(fmb[3,:,:])
   # plt.show()