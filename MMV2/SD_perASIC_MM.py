#SD_perASIC.py created by BWM 11/17/22
#program to create average standard deviation on per ASIC basis

import numpy as np
import Big_MM_load as BML
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
foreFile = "/Volumes/BMARTIN/rn2_00000001.raw"
backFile = "/Volumes/BMARTIN/rn2_00000001.raw"
cwd = os.getcwd()
foreImage = open(foreFile,"rb")
backImage = open(backFile,"rb")
numImagesF = int(os.path.getsize(foreFile)/(2048+512*512*4))
numImagesB = int(os.path.getsize(backFile)/(2048+512*512*4))
foreStack = np.zeros((numImagesF,512,512),dtype="int64")
backStack = np.zeros((numImagesB,512,512),dtype="int64")
 

##################################
#Adjust for clipping
##################################
clipHigh = 1e8
clipLow = 0
#read all the image files
for fIdex in range(numImagesB):
   payloadB = BML.mmFrame(backImage)
   backStack[:,:] += np.resize(payloadB[4],[512,512])

avgBack = np.average (backStack, axis = 0)

for fIdex in range(numImagesF):
   payload = BML.mmFrame(foreImage)
   foreStack[payload[5]-1,:,:] += np.resize(payload[4],[512,512])

DiffStack = foreStack-avgBack

#how many pixels in from edge
margin = 3
asicSDs = []
PerCapImage = DiffStack[:,:,:]
standDev = np.std(PerCapImage, axis=0)
AsicCount = 0 
for pS in range (4):
   startPixX = pS * 128
   endPixX = startPixX + 127
   
   for pSY in range (4):
      startPixY = pSY * 128
      endPixY = startPixY + 127
      perAsicAvg = np.average(standDev[startPixX+margin:endPixX-margin,startPixY+margin:endPixY-margin])
      #print (perAsicAvg)
      asicSDs += [perAsicAvg]
      #print(asicSDs)

dataWrite = np.savetxt(fname='asicSDs.txt',X=asicSDs, delimiter=',' )

