#Avg_IMG_Viewer.py created by BWM 9/12/22
#program to create pretty averaged images plot and save them

import numpy as np
import Big_MM_load as BML
import os
import matplotlib.pyplot as plt
import sys
import tkinter.filedialog as fd
import pickle as pkl
import Geo_Corr as GC

def file_select(Type):
  
   filename = fd.askopenfilename(
      title = "Open " + str(Type),
      ##########
      #Change location so you dont need to click so much
      ##########
      initialdir = "/mnt/raid/keckpad/set-HeadRework",
  
   )
   return filename

FFImage = 1 # set to 0 if dont want to FF

# backFile = file_select("Background File")
# foreFile = file_select("Foreground File")
# backFile = "/Users/benjaminmartin/Downloads/germanate_stills_dark_100us_run29_00000.raw"
# foreFile = "/Users/benjaminmartin/Downloads/germanate_stills_100pct_100us_run17_00000.raw"
foreFile = "/Users/benjaminmartin/Downloads/germanate_stills_100pct_run5_00000.raw"
backFile = "/Users/benjaminmartin/Downloads/germanate_stills_dark_run16_00000.raw"
cwd = os.getcwd()
foreImage = open(foreFile,"rb")
backImage = open(backFile,"rb")
numImagesF = int(os.path.getsize(foreFile)/(2048+512*512*4))
numImagesB = int(os.path.getsize(backFile)/(2048+512*512*4))
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
clipHigh = 1e7
clipLow = 0
PhConv = 1
#read all the image files
for fIdex in range(numImagesB):
   payloadB = BML.mmFrame(backImage)
   backStack[:,:] += np.resize(payloadB[4],[512,512])

avgBack = backStack/(numImagesB)

for fIdex in range(numImagesF):
   payload = BML.mmFrame(foreImage)
   foreStack[:,:] += np.resize(payload[4],[512,512])

avgFore = foreStack/(numImagesF)
plotData = GC.GeoCor((avgFore-avgBack) * ffCorect * PhConv)
plotDataClip = np.clip(plotData, clipLow, clipHigh)

#################
#Code for normal plotting 
#################

avg,axs = plt.subplots(1)
imageAvg = axs.imshow(plotDataClip, cmap = "viridis")
Acbar = avg.colorbar(imageAvg, aspect=10)

axs.set_title('MM Average')
axs.set_ylabel("Pixel")
axs.set_xlabel("Pixel")
Acbar.set_label ("Counts (ADU)")
# fig.set_size_inches(20, 10)    
# fig.subplots_adjust(wspace = 0.545)
plt.show()
avg.savefig(foreFile + FFStat +"_Avg.png")


# # #################
# #3d Projection plot code example
# ########################

 
# # syntax for 3-D projection
# fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
 
# # defining all 3 axes
# z = plotDataClip
# x = range(532)
# y = range(612)

# X, Y = np.meshgrid(x, y)

# # plotting


# surf = ax.plot_surface(X, Y, z,cmap ='viridis')
# fig.colorbar(surf, shrink=0.5, aspect=5)
# ax.set_title('data')

# #############################
# plt.show()

