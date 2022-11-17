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
      initialdir = "/mnt/raid/keckpad",
  
   )
   return filename

# backFile = file_select("Background File")
# foreFile = file_select("Foreground File")
foreFile = "/Volumes/BMARTIN/set-Geod/run-f3ms/frames/f3ms_00000001.raw"
backFile = "/Volumes/BMARTIN/set-Geod/run-b3ms/frames/b3ms_00000001.raw"
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

#avgBack = backStack/(numImagesB/8.0)

for fIdex in range(numImagesF):
   payload = BKL.keckFrame(foreImage)
   foreStack[payload[5]-1,(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512])
standDev = np.zeros((8,512,512),dtype=np.double)
DiffStack = foreStack-backStack

asicSDs = np.zeros((8,16),dtype=np.int16)
#how many pixels in from edge
margin = 3
for cap in range(8):
   PerCapImage = DiffStack[:,cap,:,:]
   standDev[cap,:,:] += np.std(PerCapImage, axis=0)
   AsicCount = 0 
   for pS in range (4):
      startPixX = pS * 128
      endPixX = startPixX + 127
      
      for pSY in range (4):
         startPixY = pSY * 128
         endPixY = startPixY + 127
         perAsicAvg = np.average(PerCapImage[startPixX+margin:endPixX-margin,startPixY+margin:endPixY-margin])
         #print (perAsicAvg)
         asicSDs[cap,AsicCount] += perAsicAvg
         AsicCount +=1

dataWrite = np.savetxt(fname='asicSDs.txt',X=asicSDs, delimiter=',' )

