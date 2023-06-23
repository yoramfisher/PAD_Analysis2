#!/usr/bin/env python3
#created by BWM to take Kecks big data load
#8/30/22 first creation

# YF 6/23/23 - Tweaks

import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import struct

class Metadata:
    __slots__ = ["frameParms", "lengthParms", "frameMeta", "capNum", "frameNum",
                 "integTime", "interTime"]
    def __init__(self, fp,  lp,  fm, cn, fn, integ, inter):
        self.frameParms = fp
        self.lengthParms = lp
        self.frameMeta = fm
        self.capNum = cn
        self.frameNum = fn
        self.integTime = integ
        self.interTime = inter




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

    metadata= Metadata(frameParms, lengthParms, frameMeta, capNum, 
                 frameNum, integTime, interTime )

    # return a Tuple of metadata structure and the Array Data             
    return (metadata, data)





# Entry point of the script
if __name__ == "__main__":

    # Code to be executed when the script is run directly
    print("Start.")

    randomf = "/mnt/raid/keckpad/set-yoram/run-2023-06-23-16-21-32/frames/2023-06-23-16-21-32_00000001.raw"
    randomb = "/mnt/raid/keckpad/set-yoram/run-2023-06-23-16-23-00/frames/2023-06-23-16-23-00_00000001.raw"

    imageDataF = open(randomf,"rb")
    imageDataB = open(randomb,"rb")


    (mdF, dataF) = keckFrame(imageDataF)
    (mdB, dataB) = keckFrame(imageDataB)

    imageDataF.close()
    imageDataB.close()


    print(mdF.frameNum, mdB.frameNum)

    data2dF = np.resize( dataF, [512,512])
    data2dB = np.resize( dataB, [512,512])

    fig,axs = plt.subplots(3,1)
    axs[0].imshow(data2dF)
    axs[1].imshow(data2dB)
    axs[2].imshow(data2dF-data2dB)
    plt.show()

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
