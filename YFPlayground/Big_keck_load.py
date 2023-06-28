#!/usr/bin/env python3
#created by BWM to take Kecks big data load
#8/30/22 first creation

# YF 6/23/23 - Tweaks

import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import struct
import xpad_utils as xutil

class Metadata:
    __slots__ = ["frameParms", "lengthParms", "frameMeta", "capNum", "frameNum",
                 "integTime", "interTime", "sensorTemp"]
    def __init__(self, fp,  lp,  fm, cn, fn, integ, inter, st):
        self.frameParms = fp
        self.lengthParms = lp
        self.frameMeta = fm
        self.capNum = cn
        self.frameNum = fn
        self.integTime = integ
        self.interTime = inter
        self.sensorTemp = st




def keckFrame(dataFile):
    headerBites = dataFile.read(16)  
    frameParms = struct.unpack("<HHHHII",headerBites)
    headerBites = dataFile.read(16) 
    lengthParms = struct.unpack("<IHHBB6x",headerBites)
    headerBites = dataFile.read(16)   # The first 48 are <?> in the file header
    headerBites = dataFile.read(40)   # At 0x800000   to 0x800029
    frameMeta = struct.unpack("<QIIQIIII",headerBites) # Q = 8, I = 4
    # ADDR   Param                              Index
    #  0x800000  Host Ref Tag           Q_1      0
    #  0x800004  Host Ref Tag           Q_2      0  
    #  0x800008  Glopbal Frame Count     I       1
    #  0x80000C  GSeq Frame Count        I       2
    #  0x800010  Time Since Armed        Q_1     3
    #  0x800014  Time Since Armed        Q_2     3
    #  0x800018  IntegrationTime         I       4
    #  0x80001C  InterframeTime          I       5
    #  0x800020  various_metame          I       6
    #  0x800024  ReadoutDelay            I       7
    
    
    headerBites = dataFile.read(256-(16+16+16+40)) #read remainder of header bites
    # Actually these are all 0?
    s = 0
    SensorTemp = np.zeros( (8,1), dtype='int16')  # nope :-(
    for i in range(8):
        subModMetaData = headerBites[s:s+24]
        subModMetaDataB = struct.unpack("<HHHHHHHHHHHH",subModMetaData) # 
        SensorTemp[i] = subModMetaDataB[9]
        s += 8

    
    frameNum = frameMeta[1]
    capNum = int(frameMeta[6]>>24)&0xf
    integTime = frameMeta[4]
    interTime = frameMeta[5]
    #print(capNum)

    
    dt = np.dtype('int16')
    data = np.fromfile(dataFile, count = (lengthParms[1] * lengthParms[2]), dtype = dt)
    footer = dataFile.read(768) #read footer bites 
    footerB = struct.unpack("<384H",footer) #  read into list of uint16

    # DEBUG
    #print (tuple(hex(num) for num in footerB) )
    # SubMod<N> Semsor Temp<N>
    #print( footerB[8],  footerB[8 + 1*12],  footerB[8 + 2*12], 
    #      footerB[8 + 3*12], footerB[8 + 4*12],  footerB[8 + 5*12], footerB[8 + 6*12], 
    #      footerB[8 + 7*12]  ) 

    v_iss_buf_pix = [footerB[i * 12] for i in range(8)]
    v_iss_ab = [footerB[1 + i * 12] for i in range(8)]
    v_mon_out = [footerB[2 + i * 12] for i in range(8)]
    v_iss_buf = [footerB[3 + i * 12] for i in range(8)]
    vdda_current = [footerB[4 + i * 12] for i in range(8)]
    vdda_voltage = [footerB[5 + i * 12] for i in range(8)]
    sensor_temp = [footerB[8 + i * 12] for i in range(8)]   # Sensor Temp

    test = [ xutil.convertSensorVoltage( x ) for x in v_iss_buf_pix  ]
    test = [ xutil.convertSensorVoltage( x ) for x in vdda_voltage  ]
    st = [ xutil.convertSensorTemp( x ) for x in sensor_temp  ]
    #debug
    print(st) # Sensor Temperatures in Celcius

    metadata= Metadata(frameParms, lengthParms, frameMeta, capNum, 
                 frameNum, integTime, interTime, st )


    # return a Tuple of metadata structure and the Array Data             
    return (metadata, data)





# Entry point of the script
if __name__ == "__main__":

    # Code to be executed when the script is run directly
    print("Start.")

    #"C:\Sydor Technologies\temptst_00000001.raw"
    #"C:\Sydor Technologies\temptst2_T21_00000001.raw"
    #"C:\Sydor Technologies\temptst3_T28_00000001.raw"
    #"C:\Sydor Technologies\temptst40_00000001.raw"
    #"C:\Sydor Technologies\S08a_CeO2_06_00000001.raw"
    randomf = r"C:\Sydor Technologies\temptst_00000001.raw" # C:/mnt/raid/keckpad/set-yoram/run-2023-06-23-16-21-32/frames/2023-06-23-16-21-32_00000001.raw"
    randomb = r"C:\Sydor Technologies\S08a_CeO2_06_00000001.raw" # "/mnt/raid/keckpad/set-yoram/run-2023-06-23-16-23-00/frames/2023-06-23-16-23-00_00000001.raw"

    Fore = open(randomf,"rb")
    Back = open(randomb,"rb")

    (mdF, dataF) = keckFrame(Fore)
    (mdB, dataB) = keckFrame(Back)

    Fore.close()
    Back.close()


    print(mdF.frameNum, mdB.frameNum)

    data2dF = np.resize( dataF, [512,512])
    data2dB = np.resize( dataB, [512,512])

    fig,axs = plt.subplots(3,1)
    axs[0].imshow(data2dF)
    axs[1].imshow(data2dB)
    axs[2].imshow(data2dF-data2dB)
    plt.show()
