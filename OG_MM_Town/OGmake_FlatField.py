#make_FlatField.py created by BWM 1/28/22
#program to create a flat field correction file and save normalized correction

import numpy as np
import OGBig_MM_load as BML
import os
import matplotlib.pyplot as plt
import sys
import tkinter.filedialog as fd
import pickle as pkl

cwd = os.getcwd()

# def file_select(Type):
  
#    filename = fd.askopenfilename(
#       title = "Open " + str(Type),
#       initialdir = "/mnt/raid/keckpad/set-HeadRework",
  
#    )
#    return filename

foreFile = "/Users/benjaminmartin/Downloads/OGMM_40kV_1ms.raw"
foreImage = open(foreFile,"rb")
numImagesF = int(os.path.getsize(foreFile)/(2048+512*512*4))
# numImagesB = int(os.path.getsize(backFile)/(2048+512*512*4))
foreStack = np.zeros((512,512),dtype=np.double)
normFore = np.zeros((512,512), dtype=np.double)

for fIdex in range(numImagesF):
   payload = BML.mmFrame(foreImage)
   foreStack += np.resize(payload,[512,512])

avgFore = foreStack/(numImagesF)


dataAvg = np.mean(avgFore[:,:])
normFore[:,:] += 1/(avgFore[:,:] / dataAvg)
dataMax = np.max(normFore)
normFore = normFore/dataMax

fileName = cwd + '/FF.pickle'
fileObject = open(fileName, 'wb')
pkl.dump(normFore, fileObject)
fileObject.close()

# #######################
# #Code to unpickle, need pickle import 
# # fileObject = open(fileName, 'rb')
# # modelInput = pkl.load(fileObject2)
# # fileObject2.close()

###################
#Code to plot and save one image with labels and such
###################
plotData = normFore
#clip data below to get rid of hot pixels and negative pixels
clipData = np.clip(plotData, 0, 1e7)
fig,ax = plt.subplots(1)
image = ax.imshow(clipData, cmap = "viridis")
cbar = fig.colorbar(image, aspect=10)
ax.set_title('MM PAD')
ax.set_ylabel("Pixel")
ax.set_xlabel("Pixel")
cbar.set_label ("Counts (ADU)")
# fig.savefig(foreFile + "_Avg.png")
plt.show()
