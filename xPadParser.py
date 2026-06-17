#created by BWM
#8/30/22 first creation

import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import struct


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
    return frameParms, lengthParms, frameMeta, capNum, data, frameNum, integTime, interTime

def mmpadFrame(dataFile):
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

    dt = np.dtype('uint32')
    data = np.fromfile(dataFile, count = (lengthParms[1] * lengthParms[2]), dtype = dt)
    dataFile.read(2048-256) #read footer bites 
    return frameParms, lengthParms, frameMeta, capNum, data, frameNum, integTime, interTime

