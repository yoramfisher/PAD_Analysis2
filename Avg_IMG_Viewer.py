#Avg_IMG_Viewer.py created by BWM 9/12/22
#program to create pretty averaged images plot and save them

import numpy as np
import Big_keck_load as BKL
import os
import matplotlib.pyplot as plt
import sys

foreFile = "/mnt/raid/keckpad/set-geocal_dcsKeck/run-geocal_f/frames/geocal_f_00000001.raw"
backFile = "/mnt/raid/keckpad/set-geocal_dcsKeck/run-geocal_b/frames/geocal_b_00000001.raw"
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
plotData1 = plotData[0,:,:]

#average the data across all 8 caps
plotData = np.average(plotData, axis=0)
#clip data below to get rid of hot pixels and negative pixels
clipData = np.clip(plotData, 0, 1250)

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

fig,ax = plt.subplots(1)
image = ax.imshow(clipData, cmap = "viridis")
cbar = fig.colorbar(image, aspect=10)
ax.set_title('DCS Keck')
ax.set_ylabel("Pixel")
ax.set_xlabel("Pixel")
cbar.set_label ("Counts (ADU)")
fig.savefig(foreFile + "_Avg.png")
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