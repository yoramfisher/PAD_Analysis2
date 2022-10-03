#Bias_Anal.py created by BWM 8/31/22
#program to analyze keck data while varying DAC bias voltages

import numpy as np
import Big_keck_load as BKL
import os
import matplotlib.pyplot as plt
import sys

foreFile = "/mnt/raid/keckpad/set-junk123/run-1ms_flat_fore/frames/1ms_flat_fore_00000001.raw"
backFile = "/mnt/raid/keckpad/set-junk123/run-1ms_flat_back/frames/1ms_flat_back_00000001.raw"
cwd = os.getcwd()
foreImage = open(foreFile,"rb")
backImage = open(backFile,"rb")
numImagesF = int(os.path.getsize(foreFile)/(1024+512*512*2))
numImagesB = int(os.path.getsize(backFile)/(1024+512*512*2))
foreStack = np.zeros((8,512,512),dtype=np.double)
backStack = np.zeros((8,512,512),dtype=np.double)

#read all the image files
for fIdex in range(numImagesB):
   payloadB = BKL.keckFrame(backImage)
   backStack[(payloadB[3]-1)%8,:,:] += np.resize(payloadB[4],[512,512])

avgBack = backStack/(numImagesB/8.0)

for fIdex in range(numImagesF):
   payload = BKL.keckFrame(foreImage)
   foreStack[(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512])

avgFore = foreStack/(numImagesB/8.0)
plotData = avgFore-avgBack
plotDataClip = np.clip(plotData, 0, 1000)
avgplotData = np.average(plotDataClip, axis=0)
avg,axs = plt.subplots(1)
imageAvg = axs.imshow(avgplotData, cmap = "viridis")
Acbar = avg.colorbar(imageAvg, aspect=10)
axs.set_title('DCS Keck Cap Average')
axs.set_ylabel("Pixel")
axs.set_xlabel("Pixel")
Acbar.set_label ("Counts (ADU)")
# fig.set_size_inches(20, 10)    
# fig.subplots_adjust(wspace = 0.545)
avg.savefig(foreFile + "_Avg.png")

# plt.imshow(plotData)


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
   ax[indexRow,indexCol].set_title('DCS Keck Cap'+ str(indexVal))
   ax[indexRow,indexCol].set_ylabel("Pixel")
   ax[indexRow,indexCol].set_xlabel("Pixel")
   cbar.set_label ("Counts (ADU)")
fig.set_size_inches(20, 10)    
fig.subplots_adjust(wspace = 0.545)
fig.savefig(foreFile + "_AvgAll.png")
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