#Avg_IMG_Viewer.py created by BWM 9/12/22
#program to create pretty averaged images plot and save them

import numpy as np
import Big_MM_load as BML
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

# backFile = file_select("Background File")
# foreFile = file_select("Foreground File")
foreFile = "/Volumes/BMARTIN/rn2_00000001.raw"
cwd = os.getcwd()
foreImage = open(foreFile,"rb")
# backImage = open(backFile,"rb")
numImagesF = int(os.path.getsize(foreFile)/(2048+(512*512*4)))
# numImagesB = int(os.path.getsize(backFile)/(1024+512*512*2))
foreStack = np.zeros((512,512),dtype=("int32"))
# backStack = np.zeros((8,512,512),dtype=np.double)
 

##################################
#Adjust for clipping
##################################
clipHigh = 1e4
clipLow = 2e3
#read all the image files
# for fIdex in range(numImagesB):
#    payloadB = BKL.keckFrame(backImage)
#    backStack[(payloadB[3]-1)%8,:,:] += np.resize(payloadB[4],[512,512])

# avgBack = backStack/(numImagesB/8.0)

for fIdex in range(numImagesF):
   payload = BML.mmFrame(foreImage)
   foreStack[:,:] += np.resize(payload[4],[512,512])

avgFore = foreStack/(numImagesF)
plotData = avgFore #-avgBack
plotDataClip = np.clip(plotData, clipLow, clipHigh)
avg,axs = plt.subplots(1)
imageAvg = axs.imshow(plotDataClip, cmap = "viridis")
Acbar = avg.colorbar(imageAvg, aspect=10)
axs.set_title('MM Average')
axs.set_ylabel("Pixel")
axs.set_xlabel("Pixel")
Acbar.set_label ("Counts (ADU)")
# fig.set_size_inches(20, 10)    
# fig.subplots_adjust(wspace = 0.545)
# avg.savefig(foreFile + "_Avg.png")
plt.show()
# plt.imshow(plotData)





