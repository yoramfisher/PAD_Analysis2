#created by BWM to take Kecks big data load
#8/30/22 first creation

import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import struct

#cwd = os.getcwd()
#imageData = open(cwd +"\\PAD_Anal\\KeckData\\back.raw","rb")

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

    capNum = int(frameMeta[6]>>24)&0xf
    print(capNum)
    dataFile.read(256-(16+16+16+41)) #read remainder of header bites
    dt = np.dtype('uint16')
    data = np.fromfile(dataFile, count = (lengthParms[1] * lengthParms[2]), dtype = dt)
    dataFile.read(768) #read footer bites 
    return frameParms, lengthParms, frameMeta, capNum, data


# Frame1 = keckFrame(imageData)
# Frame2 = keckFrame(imageData)
# data2d1 = np.resize(Frame1[4],[512,512])
# data2d2 = np.resize(Frame2[4],[512,512])
# fig,axs = plt.subplots(3,1)
# axs[0].imshow(data2d1)
# axs[1].imshow(data2d2)
# axs[2].imshow(data2d1-data2d2)
# plt.show()
