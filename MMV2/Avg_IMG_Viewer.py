#Avg_IMG_Viewer.py created by BWM 9/12/22
#program to create pretty averaged images plot and save them

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

FFImage = 0 # set to 0 if dont want to FF

backFile = file_select("Background File")
foreFile = file_select("Foreground File")

cwd = os.getcwd()
foreImage = open(foreFile,"rb")
backImage = open(backFile,"rb")
numImagesF = int(os.path.getsize(foreFile)/(2048+512*512*4))
numImagesB = int(os.path.getsize(backFile)/(1048+512*512*4))
foreStack = np.zeros((512,512),dtype=np.double)
backStack = np.zeros((512,512),dtype=np.double)
FFStat = "noFF"
if FFImage ==1 :
   fileObject = open(cwd + "/FF.pickle", 'rb')
   ffCorect = pkl.load(fileObject)
   fileObject.close()
   FFStat = "FF"
else: ffCorect = 1

##################################
#Adjust for clipping
##################################
clipHigh = 1e3
clipLow = 0
#read all the image files
for fIdex in range(numImagesB):
   payloadB = BML.mmFrame(backImage)
   backStack[:,:] += np.resize(payloadB[4],[512,512])

avgBack = backStack/(numImagesB/8.0)

for fIdex in range(numImagesF):
   payload = BML.mmFrame(foreImage)
   foreStack[:,:] += np.resize(payload[4],[512,512])

avgFore = foreStack/(numImagesB/8.0)
plotData = (avgFore-avgBack) * ffCorect
plotDataClip = np.clip(plotData, clipLow, clipHigh)
avgplotData = np.average(plotDataClip, axis=0)
avg,axs = plt.subplots(1)
imageAvg = axs.imshow(avgplotData, cmap = "viridis")
Acbar = avg.colorbar(imageAvg, aspect=10)
axs.set_title('MM Average')
axs.set_ylabel("Pixel")
axs.set_xlabel("Pixel")
Acbar.set_label ("Counts (ADU)")
# fig.set_size_inches(20, 10)    
# fig.subplots_adjust(wspace = 0.545)
avg.savefig(foreFile + FFStat +"_Avg.png")


plt.show()

