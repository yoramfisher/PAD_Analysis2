#make_FlatField.py created by BWM 1/28/22
#program to create a flat field correction file and save per cap version of normalized correction

import numpy as np
import Big_keck_load as BKL
import os
import matplotlib.pyplot as plt
import sys
import tkinter.filedialog as fd
import pickle as pkl
def file_select(Type):
  
   filename = fd.askopenfilename(
      title = "Open " + str(Type),
      initialdir = "/mnt/raid/keckpad/set-HeadRework",
  
   )
   return filename

#backFile = file_select("Background File")
foreFile = file_select("Foreground File")
#foreFile = "/Volumes/BMARTIN/set-Geod/run-f3ms/frames/f3ms_00000001.raw"
#backFile = "/Volumes/BMARTIN/set-Geod/run-b3ms/frames/b3ms_00000001.raw"
cwd = os.getcwd()
foreImage = open(foreFile,"rb")
#backImage = open(backFile,"rb")
numImagesF = int(os.path.getsize(foreFile)/(1024+512*512*2))
#numImagesB = int(os.path.getsize(backFile)/(1024+512*512*2))
foreStack = np.zeros((8,512,512),dtype=np.double)
#backStack = np.zeros((8,512,512),dtype=np.double)
 

##################################
#Adjust for clipping
##################################
clipHigh = 5e2
clipLow = 0
#read all the image files
# for fIdex in range(numImagesB):
#    payloadB = BKL.keckFrame(backImage)
#    backStack[(payloadB[3]-1)%8,:,:] += np.resize(payloadB[4],[512,512])

# avgBack = backStack/(numImagesB/8.0)

for fIdex in range(numImagesF):
   payload = BKL.keckFrame(foreImage)
   foreStack[(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512])

avgFore = foreStack/(numImagesF/8.0)
normFore = np.zeros((8,512,512), dtype=np.double)
for cap in range(8):
   dataMax = np.max(1/avgFore[cap,:,:])

   normFore[cap,:,:] += 1/avgFore[cap,:,:]  * dataMax


fileName = cwd + '/FF.pickle'
fileObject = open(fileName, 'wb')
pkl.dump(normFore, fileObject)
fileObject.close()

#######################
#Code to unpickle, need pickle import 
# fileObject = open(fileName, 'rb')
# modelInput = pkl.load(fileObject2)
# fileObject2.close()

plotData = normFore
plotDataClip = np.clip(plotData, clipLow, clipHigh)
# avgplotData = np.average(plotDataClip, axis=0)
# avg,axs = plt.subplots(1)
# imageAvg = axs.imshow(avgplotData, cmap = "viridis")
# Acbar = avg.colorbar(imageAvg, aspect=10)
# axs.set_title('Keck Cap Average')
# axs.set_ylabel("Pixel")
# axs.set_xlabel("Pixel")
#Acbar.set_label ("Counts (ADU)")
# fig.set_size_inches(20, 10)    
# fig.subplots_adjust(wspace = 0.545)

#plt.imshow(plotData)


allplot = []
for val in range(8):
   allplot.append(plotDataClip[val,:,:])


indexVal =  (-1)
fig,ax = plt.subplots(2,4)
for pic in allplot:
   indexVal += 1 
   indexRow = int(indexVal/4) 
   indexCol = int(indexVal%4)
   #indexVal = allplot.index(pic)
   image = ax[indexRow,indexCol].imshow(pic, cmap = "viridis")
   # ax.imshow(pic)
# fig,ax = plt.subplots(1)
#needed to add more stuff
# image = ax.imshow(clipData, cmap = "viridis")
   cbar = fig.colorbar(image, aspect=10, ax = ax[indexRow,indexCol])
   ax[indexRow,indexCol].set_title('Keck Cap'+ str(indexVal))
   ax[indexRow,indexCol].set_ylabel("Pixel")
   ax[indexRow,indexCol].set_xlabel("Pixel")
   cbar.set_label ("Counts (ADU)")
fig.set_size_inches(20, 10)    
fig.subplots_adjust(wspace = 0.545)

plotData1 = plotData[0,:,:]

plt.show()

