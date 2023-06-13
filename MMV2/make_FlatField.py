#make_FlatField.py created by BWM 1/28/22
#program to create a flat field correction file and save normalized correction

import numpy as np
import Big_MM_load as BML
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


foreFile = file_select("Foreground File")
cwd = os.getcwd()
foreImage = open(foreFile,"rb")
#backImage = open(backFile,"rb")
numImagesF = int(os.path.getsize(foreFile)/(2048+512*512*4))
#numImagesB = int(os.path.getsize(backFile)/(2048+512*512*4))
foreStack = np.zeros((512,512),dtype=np.double)
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
   payload = BML.mmFrame(foreImage)
   foreStack[:,:] += np.resize(payload[4],[512,512])

avgFore = foreStack/(numImagesF)
normFore = np.zeros((512,512), dtype=np.double)

dataMax = np.max(1/avgFore[:,:])
dataAvg = np.mean(avgFore[:,:])
normFore[:,:] += 1/avgFore[:,:]  * 1/dataAvg


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
avg,axs = plt.subplots(1)
imageAvg = axs.imshow(plotData, cmap = "viridis")
Acbar = avg.colorbar(imageAvg, aspect=10)

axs.set_title('MM FF')
axs.set_ylabel("Pixel")
axs.set_xlabel("Pixel")
Acbar.set_label ("Counts (ADU)")
plt.show()

