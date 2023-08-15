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
import xarray as xr
import hvplot.xarray
import panel.widgets as pnw
def file_select(Type):
  
   filename = fd.askopenfilename(
      title = "Open " + str(Type),
      initialdir = "/mnt/raid/keckpad/set-HeadRework",
  
   )
   return filename

FFImage = 0 # set to 0 if dont want to FF

# backFile = file_select("Background File")
# foreFile = file_select("Foreground File")
# backFile = "/Volumes/BMARTIN/DCS_06222022/set-HLChopper/run-back/frames/back_00000001.raw"
foreFile = ("/Users/benjaminmartin/Desktop/S01_CompB_04_00000001.raw")
cwd = os.getcwd()
foreImage = open(foreFile,"rb")
# backImage = open(backFile,"rb")
numImagesF = int(os.path.getsize(foreFile)/(1024+512*512*2))
# numImagesB = int(os.path.getsize(backFile)/(1024+512*512*2))
foreStack =np.zeros(((numImagesF),8,512,512),dtype=np.double)
# backStack = np.zeros((8,512,512),dtype=np.double)
# Stack ={'pixels':(["frameNum","capNum","x","y"], foreStack, 
#                          {'units': 'ADU', 
#                           'long_name':'data from PAD uncorrected'})}



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
   payload = BKL.keckFrame(foreImage)
   foreStack[(payload[5]-1),(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512])

Stack =xr.Dataset({'stack1':(["frameNum","capNum","y","x"], foreStack, 
                        {'units': 'ADU', 
                        'long_name':'data from PAD uncorrected'})})

print(Stack.stack1.sel(frameNum=5,capNum=5))
Stack.stack1.interactive.sel(frameNum=5,capNum=5).hvplot()


# plotStack = Stack["Stack1"("frameNum","x","y")]
# plotStack.hvplot(groupby='frameNum', width=600, widget_type='scrubber', widget_location='bottom')
#Stack.Stack1["x","y"].interactive.sel(frameNum=pnw.DiscreteSlider).plot()