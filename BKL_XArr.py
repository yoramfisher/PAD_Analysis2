#created by BWM to take Kecks big data load
#8/30/22 first creation

import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import struct
import xarray as xr
import hvplot.xarray

cwd = os.getcwd()
imageData = open("/Users/benjaminmartin/Documents/GitHub/PAD_Analysis/f3ms_00000001.raw","rb")

def keckFrame(dataFile):
    headerBites = dataFile.read(16)
    frameParms = struct.unpack("<HHHHII",headerBites)
    headerBites = dataFile.read(16)
    lengthParms = struct.unpack("<IHHBB6x",headerBites)
    headerBites = dataFile.read(16)
    headerBites = dataFile.read(41)
    frameMeta = struct.unpack("<QIIQIIIIB",headerBites)
    # for val in frameMeta:
    #     print(hex(val))
    frameNum = frameMeta[1]
    capNum = int(frameMeta[6]>>24)&0xf
    integTime = frameMeta[4]
    interTime = frameMeta[5]
    #print(capNum)

    dataFile.read(256-(16+16+16+41)) #read remainder of header bites

    dt = np.dtype('int16')
    data = np.fromfile(dataFile, count = (lengthParms[1] * lengthParms[2]), dtype = dt)
    dataFile.read(768) #read footer bites 

    data= np.resize(data,[512,512])
    numImages = int(os.path.getsize(dataFile)/(1024+512*512*2))
    Stack = np.zeros((numImages,8,512,512),dtype=np.double)
    Stack[frameNum-1,(capNum-1)%8,:,:] += data
#     framedata = {'pixels':(["frameNum","capNum","x","y"], data, 
#                          {'units': 'ADU', 
#                           'long_name':'data from PAD uncorrected'})}
#     inum={"frame":(["number"], frameNum,)}
#     ds = xr.Dataset(

#     data_vars=dict(

#         framedata=(["x", "y"], data),


#     ),

#     coords=dict(

#         xleng=lengthParms[1],

#         yleng=lengthParms[2],

#         num=frameNum,

#         capNume=capNum,

#     ),

#     attrs=dict(description="a keck frame with meta data"),

# )

    df=xr.Dataset(data_vars=Stack)
    # return frameParms, lengthParms, frameMeta, capNum, data, frameNum, integTime, interTime
    return df


keckData = keckFrame(imageData)
print(keckData)
keckData+=(keckFrame(imageData))
print(keckData)

#Frame1.pixels.interactive.sel(time=pnw.DiscreteSlider).plot()

# dataset=Frame1
# dataset = xr.append(dataset,Frame2)
# avg,axs = hvplot.subplots(1)
# imageAvg = axs.imshow(Frame1["pixels"], cmap = "viridis")
# Acbar = avg.colorbar(imageAvg, aspect=10)
# axs.set_title('Keck Cap Average')
# axs.set_ylabel("Pixel")
# axs.set_xlabel("Pixel")
# Acbar.set_label ("Counts (ADU)")
# # print(Frame1[5])
# # data2d1 = np.resize(Frame1[4],[512,512])
# # data2d2 = np.resize(Frame2[4],[512,512])
# # fig,axs = plt.subplots(3,1)
# # axs[0].imshow(data2d1)
# # axs[1].imshow(data2d2)
# # axs[2].imshow(data2d1-data2d2)
# plt.show()

#Frame1 = keckFrame(imageData)
# # # Frame2 = keckFrame(imageData)
#data2d1 = np.resize(Frame1[4],[512,512])
# # capAvg = np.mean(data2d1[291:364,173:240]) 
# # print(capAvg)
 # # data2d2 = np.resize(Frame2[4],[512,512])
# #  #fig,axs = plt.subplots(3,1)
#plt.imshow(data2d1[137:270,139:270])
# #     #axs[1].imshow(data2d2)
# # # axs[2].imshow(data2d1-data2d2)
#plt.show()
# Frame1 = ()

