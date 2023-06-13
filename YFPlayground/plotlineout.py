#
# File: plotlineout.py
# Description - Read a raw KECK file from disk, and plot a hor. lineout.
#
# History
# v 0.1 6/13/23 YF - Inception
#
# Expected parameters
#    setname runname FrameNum zASICX zASICY ROIW ROIH 
# where, 
#    zASICX and zASICY are zero index based 0-3 for the ASIC coordinate. ie 0 0 is top-left, 3 3 is bottom-right
# typically will be called from shell script (see xpadScan.sh)

import numpy as np
import Big_keck_load as BKL
import os
import matplotlib.pyplot as plt
import sys
import tkinter.filedialog as fd

#
# Define some globals
#
foreStack = []
backStack = []
numImagesF=0
numImagesB=0


def go( params ):
    global foreImage, backimage, foreStack,backStack, numImagesF, numImagesB

    if len(params) < 7:
        print(" Usage: ~ setname runname FrameNum zASICX zASICY ROIW ROIH")
        exit(0)
        
    setname = params[0]
    runname = params[1]
    foreFile = f'/mnt/raid/keckpad/set-{setname}/run-{runname}/frames/{runname}_00000001.raw' # check not sure...
    
    # todo - hardcode a back file - skip for now - #WIP#
    backFile = '/mnt/raid/keckpad/set-HeadRework/run-dark50ns_1/frames/dark50ns_1_00000001.raw'
    foreImage = open(foreFile,"rb")
    backImage = open(backFile,"rb")
    numImagesF = int(os.path.getsize(foreFile)/(1024+512*512*2))
    numImagesB = int(os.path.getsize(backFile)/(1024+512*512*2))
    
    foreStack = np.zeros((numImagesF,8,512,512),dtype=np.double)
    backStack = np.zeros((numImagesB,8,512,512),dtype=np.double)

    cap = params[2] % 8
    zSX = params[3]
    zSY = params[4]
    W   = params[5]
    H   = params[6]

    
    plotROI( cap, zSX, zSY, W, H )
 
def plotROI(cap, zSX, zSY, W, H): 
    """ cap is cap 0-7
        zSX and zSY are 0-3 ASIC coordinate
    """
    global foreImage, backImage ,foreStack,backStack, numImagesF, numImagesB
    ##################################
    #Adjust for clipping
    ##################################
    clipHigh = 1e8
    clipLow = 0
    #read all the image files
    for fIdex in range(numImagesB):
        payloadB = BKL.keckFrame(backImage)
        #  return frameParms, lengthParms, frameMeta, capNum, data, frameNum, integTime, interTime
        backStack[payloadB[5]-1,(payloadB[3]-1)%8,:,:] += np.resize(payloadB[4],[512,512])

    avgBack = backStack/(numImagesB/8.0)

    for fIdex in range(numImagesF):
        payload = BKL.keckFrame(foreImage)
        foreStack[payload[5]-1,(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512])

    #standDev = np.zeros((8,512,512),dtype=np.double)
    DiffStack = foreStack-backStack
    #asicSDs = np.zeros((8,16),dtype=np.double)


    
    PerCapImage = DiffStack[:,cap,:,:]
    
    startPixY = zSY * 128
    endPixY = startPixY + H
    startPixX = zSX * 128
    endPixX = startPixX + W
    # frame 0 hardcoded for now
    plt.imshow( PerCapImage[0, startPixY:endPixY, startPixX:endPixX]) # might be flipped?? #WIP#
 
   

# Entry point of the script
if __name__ == "__main__":
    # Code to be executed when the script is run directly
    print("Start.")

    # Access the command-line arguments
    # sys.argv[0] contains the script name
    # sys.argv[1:] contains the parameters
    parameters = sys.argv[1:]
    # F! doesnt work
    # hardcode instead
    # setname runname FrameNum zASICX zASICY ROIW ROIH 
    parameters=['xpadscan','run_1', 0, 0, 0, 128, 16]
    go( parameters )