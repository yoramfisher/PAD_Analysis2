#!/usr/bin/env python3
# File: plotlineout.py
# Description - Read a raw KECK file from disk, and plot a hor. lineout.
#
# History
# v 0.1 6/13/23 YF - Inception
#
# Expected parameters
#    setname runname FrameNum zASICX zASICY nTap ROIW ROIH 
# where, 
#    zASICX and zASICY are zero index based 0-3 for the ASIC coordinate. 
#    ie 0 0 is top-left, 3 3 is bottom-right
#    nTap is 1-based tap (1-8)
#    ROIW, ROIH is width and height, typically will be 128 16
# typically will be called from shell script (see xpadScan.sh)

import numpy as np
import Big_keck_load as BKL
import os
import matplotlib.pyplot as plt
import sys
import tkinter.filedialog as fd
import subprocess

#
# Define some globals
#
foreStack = []
backStack = []
numImagesF=0
numImagesB=0
nFrames = 10
integrationTime = 50
interframeTime = 100


def run_cmd( cmd_string ):
    global nFrames
    res = 0

    # Run the shell command
    result = subprocess.run("mmcmd " + cmd_string, shell=True, capture_output=True, text=True)

    if len(result.stderr) >0:
        print("E! " + result.stderr)
        res = -1
    if len(result.stdout)>0:
        # Print the command output #DEBUG
        print("O: "+result.stdout)   
    return res # 0 = success, -1 = error
    

def go( params ):
    global foreImage, backImage, foreStack,backStack, numImagesF, numImagesB, nFrames

    if len(params) < 8:
        print(" Usage: ~ setname runname FrameNum nTap zASICX zASICY ROIW ROIH")
        exit(0)

    setname = params[0]
    ##
    res = True
    list_commands = [
        f"Image_Count {nFrames}",
        f"Interframe_Nsec {interframeTime}",
        f"Integration_Nsec {integrationTime}",
        f"Integration_Nsec {integrationTime}",
        f"SW_Trigger 1",
        f"startset {setname}"
        ]
 
    
    for c in list_commands:
        res = run_cmd( c  )   #Set number of frames
        if res:
            break
    for i in range(1, 3 + 1):        
        runname=f"run_{i}"        
        res = run_cmd( f"startrun {runname}"  )   
        if res:
            break
        run_cmd( f"status -wait" )


    exit() # debug

    setname = params[0]
    runname = params[1]
    foreFile = f'/mnt/raid/keckpad/set-{setname}/run-{runname}/frames/{runname}_00000001.raw' # check not sure...
    
    # todo - hardcode a back file - skip for now - #WIP#
    backFile = f'/mnt/raid/keckpad/set-{setname}/run-back/frames/run_1_00000001.raw' 
    foreImage = open(foreFile,"rb")
    backImage = open(backFile,"rb")
    numImagesF = int(os.path.getsize(foreFile)/(1024+512*512*2))
    numImagesB = int(os.path.getsize(backFile)/(1024+512*512*2))
    
    foreStack = np.zeros((numImagesF,8,512,512),dtype=np.double)
    backStack = np.zeros((numImagesB,8,512,512),dtype=np.double)

    cap = params[2] % 8
    zSX = params[3]
    zSY = params[4]
    nTap = params[5]
    W   = params[6]
    H   = params[7]

    
    plotROI( cap, zSX, zSY, nTap, W, H )
 
def plotROI(cap, zSX, zSY, nTap, W, H): 
    """ cap is cap 0-7
        zSX and zSY are 0-3 ASIC coordinate
        nTap is 1-8
        W,H are in pixels typ 128,16
    """
    global foreImage, backImage ,foreStack,backStack, numImagesF, numImagesB
    ##################################
    #Adjust for clipping
    ##################################
    clipHigh = 1e8
    clipLow = 0
    #read all the image files
    for fIdex in range(numImagesB):
        (mdB,dataB) = BKL.keckFrame(backImage)
        #  return frameParms, lengthParms, frameMeta, capNum, data, frameNum, integTime, interTime
        backStack[ mdB.frameNum-1,(mdB.capNum-1)%8,:,:] += np.resize(dataB,[512,512])

    avgBack = backStack/(numImagesB/8.0)

    for fIdex in range(numImagesF):
        (mdF,dataF) = BKL.keckFrame(foreImage)
        foreStack[mdF.frameNum-1,(mdF.capNum-1)%8,:,:] += np.resize(dataF,[512,512])

    #standDev = np.zeros((8,512,512),dtype=np.double)
    DiffStack = foreStack-backStack
    #asicSDs = np.zeros((8,16),dtype=np.double)

    
    PerCapImage = DiffStack[:,cap,:,:]
    
    startPixY = zSY * 128 + (nTap-1) * 16
    endPixY = startPixY + H
    startPixX = zSX * 128
    endPixX = startPixX + W
    # frame 0 hardcoded for now
    plt.imshow( PerCapImage[0, startPixY:endPixY, startPixX:endPixX]) # might be flipped?? #WIP#
    plt.show()
 
   

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
    # setname runname FrameNum zASICX zASICY   nTap  ROIW ROIH 
    parameters=['xpadscan','run_1', 1, 0, 0,   1,    128, 16]
    go( parameters )
    input("Press Enter to continue...")