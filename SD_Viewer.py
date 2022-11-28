#Avg_IMG_Viewer.py created by BWM 11/15/22
#program to create pretty plot of SDs

import numpy as np
import Big_keck_load as BKL
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
foreFile = '/mnt/raid/keckpad/set-HeadRework/run-dark50ns/frames/dark50ns_00000001.raw'
backFile = '/mnt/raid/keckpad/set-HeadRework/run-dark50ns_1/frames/dark50ns_1_00000001.raw'
cwd = os.getcwd()
foreImage = open(foreFile,"rb")
backImage = open(backFile,"rb")
numImagesF = int(os.path.getsize(foreFile)/(1024+512*512*2))
numImagesB = int(os.path.getsize(backFile)/(1024+512*512*2))
foreStack = np.zeros((numImagesF,8,512,512),dtype=np.double)
backStack = np.zeros((numImagesB,8,512,512),dtype=np.double)
 

##################################
#Adjust for clipping
##################################
clipHigh = 1e8
clipLow = -10000
#read all the image files
for fIdex in range(numImagesB):
   payloadB = BKL.keckFrame(backImage)
   backStack[payloadB[5]-1,(payloadB[3]-1)%8,:,:] += np.resize(payloadB[4],[512,512])

#avgBack = backStack/(numImagesB/8.0)

for fIdex in range(numImagesF):
   payload = BKL.keckFrame(foreImage)
   foreStack[payload[5]-1,(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512])
standDev = np.zeros((8,512,512),dtype=np.double)
DiffStack = foreStack-backStack
for cap in range(8):
   PerCapImage = DiffStack[:,cap,:,:]
   standDev[cap,:,:] += np.std(PerCapImage, axis=0)



plotData = standDev
plotDataClip = np.clip(plotData, clipLow, clipHigh)
avgplotData = np.average(plotDataClip, axis=0)
avg,axs = plt.subplots(1)
imageAvg = axs.imshow(avgplotData, cmap = "viridis")
Acbar = avg.colorbar(imageAvg, aspect=10)
axs.set_title('Keck Cap Average')
axs.set_ylabel("Pixel")
axs.set_xlabel("Pixel")
Acbar.set_label ("Counts (ADU)")

# fig.set_size_inches(20, 10)    
# fig.subplots_adjust(wspace = 0.545)
avg.savefig(foreFile + "_SD.png")

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
   ax[indexRow,indexCol].set_title('Keck Cap'+ str(indexVal))
   ax[indexRow,indexCol].set_ylabel("Pixel")
   ax[indexRow,indexCol].set_xlabel("Pixel")
   cbar.set_label ("Counts (ADU)")
fig.set_size_inches(20, 10)    
fig.subplots_adjust(wspace = 0.545)
fig.savefig(foreFile + "_SDAvgAll.png")
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