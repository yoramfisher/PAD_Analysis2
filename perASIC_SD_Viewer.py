#SD_perASIC.py created by BWM 11/17/22
#program to create average standard deviation on per ASIC basis

import numpy as np
import Big_keck_load as BKL
import os
import matplotlib.pyplot as plt
import sys
import tkinter.filedialog as fd

def file_select(Type):
  
   filename = fd.askopenfilename(
      title = "Open " + str(Type),
      initialdir = "/mnt/raid/keckpad/set-HeadRework",
  
   )
   return filename

foreFile = '/mnt/raid/keckpad/set-HeadRework/run-dark50ns/frames/dark50ns_00000001.raw'
backFile = '/mnt/raid/keckpad/set-HeadRework/run-dark50ns_1/frames/dark50ns_1_00000001.raw'
# backFile = file_select("Background File")
# foreFile = file_select("Foreground File")
# print(backFile)
# print(foreFile)
cwd = os.getcwd()
foreImage = open(foreFile,"rb")
backImage = open(backFile,"rb")
numImagesF = int(os.path.getsize(foreFile)/(1024+512*512*2))
numImagesB = int(os.path.getsize(backFile)/(1024+512*512*2))
foreStack = np.zeros((numImagesF,8,512,512),dtype=np.double)
backStack = np.zeros((numImagesB,8,512,512),dtype=np.double)
 

##################################
#Adjust for clipping
##################################
clipHigh = 1e8
clipLow = 0
#read all the image files
for fIdex in range(numImagesB):
   payloadB = BKL.keckFrame(backImage)
   backStack[payloadB[5]-1,(payloadB[3]-1)%8,:,:] += np.resize(payloadB[4],[512,512])

avgBack = backStack/(numImagesB/8.0)

for fIdex in range(numImagesF):
   payload = BKL.keckFrame(foreImage)
   foreStack[payload[5]-1,(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512])
standDev = np.zeros((8,512,512),dtype=np.double)
DiffStack = foreStack-backStack
asicSDs = np.zeros((8,16),dtype=np.double)

#how many pixels in from edge
margin = 3

for cap in range(8):
   PerCapImage = DiffStack[:,cap,:,:]
   standDev[cap,:,:] += np.std(PerCapImage, axis=0)
   AsicCount = 0 
   for pSY in range (4):
      startPixY = pSY * 128
      endPixY = startPixY + 127
      
      for pSX in range (4):
         startPixX = pSX * 128
         endPixX = startPixX + 127
         sX = startPixX+margin
         eX = endPixX-margin
         sY = startPixY+margin
         eY = endPixY-margin

         perAsicAvg = np.mean(standDev[cap,(sX):(eX),(sY):(eY)])
         print(perAsicAvg)
         #print (perAsicAvg)
         asicSDs[cap,AsicCount] += perAsicAvg
         AsicCount +=1


dataWrite = np.savetxt(fname='asicSDs.txt',X=asicSDs, delimiter=',' )


