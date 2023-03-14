#Avg_IMG_Viewer.py created by BWM 9/12/22
#program to create pretty averaged images plot and save them

import numpy as np
import Big_keck_load as BKL
import os
import matplotlib.pyplot as plt
import sys
import tkinter.filedialog as fd
import pickle as pkl
import Geo_Corr as gc
def file_select(Type):
  
   filename = fd.askopenfilename(
      title = "Open " + str(Type),
      initialdir = "/mnt/raid/keckpad/set-HeadRework",
  
   )
   return filename

FFImage = 0 # set to 0 if dont want to FF

# backFile = file_select("Background File")
# foreFile = file_select("Foreground File")
backFile = "/Volumes/BMARTIN/DCS_06222022/set-HLChopper/run-back/frames/back_00000001.raw"
foreFile = "/Volumes/BMARTIN/DCS_06222022/set-HLChopper/run-scan_TD_220/frames/scan_TD_220_00000001.raw"
cwd = os.getcwd()
foreImage = open(foreFile,"rb")
backImage = open(backFile,"rb")
numImagesF = int(os.path.getsize(foreFile)/(1024+512*512*2))
numImagesB = int(os.path.getsize(backFile)/(1024+512*512*2))
foreStack = np.zeros((8,512,512),dtype=np.double)
backStack = np.zeros((8,512,512),dtype=np.double)
FFStat = "noFF"
if FFImage ==1 :
   fileObject = open(cwd + "/pickleFF.pi", 'rb')
   ffCorect = pkl.load(fileObject)
   fileObject.close()
   FFStat = "FF"
else: ffCorect = 1

##################################
#Adjust for clipping
##################################
clipHigh = 5e2
clipLow = 0
#read all the image files
for fIdex in range(numImagesB):
   payloadB = BKL.keckFrame(backImage)
   backStack[(payloadB[3]-1)%8,:,:] += np.resize(payloadB[4],[512,512])

avgBack = backStack/(numImagesB/8.0)

for fIdex in range(numImagesF):
   payload = BKL.keckFrame(foreImage)
   foreStack[(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512])


avgFore = foreStack/(numImagesB/8.0)
plotData = (avgFore-avgBack) * ffCorect
plotDataClip = np.clip(plotData, clipLow, clipHigh)
avgplotData = gc.GeoCor(np.average(plotDataClip, axis=0))

avg,axs = plt.subplots(1)
imageAvg = axs.imshow(avgplotData, cmap = "viridis")
Acbar = avg.colorbar(imageAvg, aspect=10)
axs.set_title('Keck Cap Average')
axs.set_ylabel("Pixel")
axs.set_xlabel("Pixel")
Acbar.set_label ("Counts (ADU)")
# fig.set_size_inches(20, 10)    
# fig.subplots_adjust(wspace = 0.545)
avg.savefig(foreFile + FFStat +"_Avg.png")

# plt.imshow(plotData)


allplot = []
for val in range(8):
   allplot.append(gc.GeoCor(plotDataClip[val,:,:]))


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
fig.savefig(foreFile + FFStat + "_AvgAll.png")
plotData1 = plotData[0,:,:]

#average the data across all 8 caps
plotData = np.average(plotData, axis=0)
#clip data below to get rid of hot pixels and negative pixels
clipData = np.clip(plotData, clipLow, clipHigh)

########################
#code to plot all 8 caps individually
########################

# plt.imshow(plotData)
# # fig,axs = plt.subplots(2,4)
# # axs[0,0].imshow(plotData[0,:,:])
# # axs[0,1].imshow(plotData[1,:,:])
# # axs[0,2].imshow(plotData[2,:,:])
# # axs[0,3].imshow(plotData[3,:,:])
# # axs[1,0].imshow(plotData[4,:,:])
# # axs[1,1].imshow(plotData[5,:,:])
# # axs[1,2].imshow(plotData[6,:,:])
# # axs[1,3].imshow(plotData[7,:,:])
# #plt.imshow(fmb[3,:,:])
# plt.show()

###################
#Code to plot and save one image with labels and such
###################

# fig,ax = plt.subplots(1)
# image = ax.imshow(clipData, cmap = "viridis")
# cbar = fig.colorbar(image, aspect=10)
# ax.set_title('DCS Keck')
# ax.set_ylabel("Pixel")
# ax.set_xlabel("Pixel")
# cbar.set_label ("Counts (ADU)")
#fig.savefig(foreFile + "_Avg.png")
plt.show()

#################
#3d Projection plot code example
########################
# fig = plt.figure()
 
# # syntax for 3-D projection
# fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
 
# # defining all 3 axes
# z = clipData
# x = range(512)
# y = range(512)

# X, Y = np.meshgrid(x, y)

# # plotting


# surf = ax.plot_surface(X, Y, z,cmap ='viridis')
# fig.colorbar(surf, shrink=0.5, aspect=5)
# ax.set_title('DCSKeck')
# plt.show()
#############################