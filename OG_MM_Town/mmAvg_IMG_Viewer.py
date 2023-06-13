#Avg_IMG_Viewer.py created by BWM 9/12/22
#program to create pretty averaged images plot and save them
#modded by BWM 10/7/22 for OG MM PAD frames

import numpy as np
import OGBig_MM_load as BKL
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
# foreImage = open(foreFile,"rb")
# backImage = open(backFile,"rb")

cwd = os.getcwd()
foreFile = "/Users/benjaminmartin/Downloads/OGMM_40kV_1ms.raw"
# backFile = "/Users/benjaminmartin/Downloads/OGMM_1msb.raw"
cwd = os.getcwd()
foreImage = open(foreFile,"rb")
# backImage = open(backFile,"rb")
numImagesF = int(os.path.getsize(foreFile)/(2048+512*512*4))
# numImagesB = int(os.path.getsize(backFile)/(2048+512*512*4))
foreStack = np.zeros((512,512),dtype=np.double)
backStack = np.zeros((512,512),dtype=np.double)

# #read all the image files
# for fIdex in range(numImagesB):
#    payloadB = BKL.mmFrame(backImage)
#    backStack += np.resize(payloadB,[512,512])

# avgBack = backStack/(numImagesB)

for fIdex in range(numImagesF):
   payload = BKL.mmFrame(foreImage)
   foreStack += np.resize(payload,[512,512])

avgFore = foreStack/(numImagesF)
plotData = avgFore

#clip data below to get rid of hot pixels and negative pixels
clipData = np.clip(plotData, 0, 1e7)

###################
#Code to plot and save one image with labels and such
###################

fig,ax = plt.subplots(1)
image = ax.imshow(clipData, cmap = "viridis")
cbar = fig.colorbar(image, aspect=10)
ax.set_title('MM PAD')
ax.set_ylabel("Pixel")
ax.set_xlabel("Pixel")
cbar.set_label ("Counts (ADU)")
# fig.savefig(foreFile + "_Avg.png")
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