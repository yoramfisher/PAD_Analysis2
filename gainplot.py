# name: gainpercap.py
# description: plots the mean of a select ASIC per cap, intended for gain measurements

import numpy as np
import Big_keck_load as BKL
import os
import matplotlib.pyplot as plt
import sys
import tkinter.filedialog as fd



backFile = '/mnt/raid/keckpad/set-HeadRework/run-dark50ns/frames/dark50ns_00000001.raw'
foreFile = '/mnt/raid/keckpad/set-HeadRework/run-dark10ms/frames/dark10ms_00000001.raw'

# set up blank arrays
cwd = os.getcwd()
foreImage = open(foreFile,"rb")
backImage = open(backFile,"rb")
numImagesF = int(os.path.getsize(foreFile)/(1024+512*512*2))
numImagesB = int(os.path.getsize(backFile)/(1024+512*512*2))
foreStack = np.zeros((numImagesF,8,512,512),dtype=np.double)
backStack = np.zeros((numImagesB,8,512,512),dtype=np.double)
 

# ##################################
# #Adjust for clipping
# ##################################
# clipHigh = 1e8
# clipLow = 0


# read all the image files
for fIdex in range(numImagesB):
   payloadB = BKL.keckFrame(backImage)
   backStack[payloadB[5]-1,(payloadB[3]-1)%8,:,:] += np.resize(payloadB[4],[512,512])

# background subtract the data
avgBack = backStack/(numImagesB/8.0)

# process to make an array of means for each cap
for fIdex in range(numImagesF):
   payload = BKL.keckFrame(foreImage)
   foreStack[payload[5]-1,(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512])
stackMean = np.zeros((8,512,512),dtype=np.double)
DiffStack = foreStack-backStack

CAPmeans = np.zeros((8,16),dtype=np.double) # blank array to store mean of each asic for each cap


# how many pixels in from edge do you want your ROI?
margin = 20

# if you want to do things on a single image basis, averaging each ASIC, use this
# average of each ASIC in each average cap image 
for cap in range(8):
   PerCapImage = DiffStack[:,cap,:,:]
   stackMean[cap,:,:] += np.mean(PerCapImage, axis=0)
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

         perAsicMean = np.mean(stackMean[cap,(sX):(eX),(sY):(eY)])
         print(perAsicMean)
         #print (perAsicMean)
         CAPmeans[cap,AsicCount] += perAsicMean
         AsicCount +=1


dataWrite = np.savetxt(fname='perASICmean.txt',X=CAPmeans, delimiter=',' )

# if you want to do things for one ROI for a series of images, use this... 
# this will plot gain for each cap over the 15 gain options...
 

