#!/usr/bin/env python3
# File: plotlineout.py
# Description - Read a raw KECK file from disk, and plot a hor. lineout.
#
# History
# v 0.1 6/13/23 YF - Inception
# v 0.2 6/29/23 YF - Shift to not using any bash scripts. Instead commands run directly from Python.
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
import shutil
import matplotlib.pyplot as plt
import sys
import tkinter as tk
import xpad_utils as xd
from glob import glob
#
# Define some globals
#
foreStack = []
backStack = []
fore = None
back = None

nFrames = 10
integrationTime = 50
interframeTime = 100
NRUNS = 3
RAIDPATH="/mnt/raid/keckpad"

    
#
#
#
def takeData( params, overwrite = 1, runVaryCommand="", varRange = None ) -> int:
    """ 
        Run multiple Runs - issuing one command (one parameter) that changes
        at each run.
        runVaryCommand = string commmand
        varRange = numpy.arange( , ,) 
        overWrite. Set to 1 to delete previous Runs
        Return number of runs saved
    """
    global  foreStack,backStack, fore, back
    

    if len(params) < 8:
        print(" Usage: ~ setname runname FrameNum nTap zASICX zASICY ROIW ROIH")
        exit(0)


    setname = params[0]
    runname = params[1]


    if overwrite:
        # delete old runs
        # rm -r "$RAIDPATH"/set-$setname/run-run_*
        for match in glob(f"{RAIDPATH}/set-{setname}/run-run_*"):
            shutil.rmtree(match)

    #
    # Create list of commands
    #  
    res = True
    list_commands = [
        f"Image_Count {nFrames}",
        f"Interframe_Nsec {interframeTime}",
        f"Integration_Nsec {integrationTime}",
        f"Integration_Nsec {integrationTime}",
        f"SW_Trigger 1",
        f"startset {setname}"
        ]
     
    
    #
    # Run through list of commands - and send them to HW
    #
    for c in list_commands:
        res = xd.run_cmd( c  )   
        if res:
            break

    if varRange is not None:
        NRUNS = len(varRange)

    #
    # Start a series of Runs
    #
    for i in range(1, NRUNS + 1):     
        # scan a parameter here. Pass in runVaryCommand and varRange
        if runVaryCommand:
            var = varRange[0]
            varRange = varRange[1:] # remove first element
            c  = f"{runVaryCommand} {var}"
            xd.run_cmd(c)

        runname=f"run_{i}"        
        res = xd.run_cmd( f"startrun {runname}"  )   
        if res:
            break
        xd.run_cmd( f"status -wait" )

    return NRUNS   

#
#
#
def analyzeData(params):
    """
    Load up the runs, and analyze
    """

    setname = params[0]
    runname = params[1]

    foreFile = f'/mnt/raid/keckpad/set-{setname}/run-{runname}/frames/{runname}_00000001.raw' # check not sure...

    #DEBUG w local file on Windows
    foreFile = r"C:\Sydor Technologies\temptst_00000001.raw" # C:/mnt/raid/keckpad/set-yoram/run-2023-06-23-16-21-32/frames/2023-06-23-16-21-32_00000001.raw"
    

    fore = BKL.KeckFrame( foreFile )

    backFile = f'/mnt/raid/keckpad/set-{setname}/run-back/frames/run_1_00000001.raw' 

    #DEBUG w local file on Windows
    backFile= r"C:\Sydor Technologies\temptst2_T21_00000001.raw" # "/mnt/raid/keckpad/set-yoram/run-2023-06-23-16-23-00/frames/2023-06-23-16-23-00_00000001.raw"

    back = BKL.KeckFrame( backFile )
    
    numImagesF = fore.numImages 
    numImagesB = back.numImages
    
    # create global big arrays to hold images
    foreStack = np.zeros((numImagesF,8,512,512),dtype=np.double)
    backStack = np.zeros((numImagesB,8,512,512),dtype=np.double)

    cap = params[2] % 8
    zSX = params[3]
    zSY = params[4]
    nTap = params[5]
    W   = params[6]
    H   = params[7]
 
    plotROI( cap, zSX, zSY, nTap, W, H )
 

 #
 #
 #
def plotROI(cap, zSX, zSY, nTap, W, H): 
    """ cap is cap 0-7
        zSX and zSY are 0-3 ASIC coordinate
        nTap is 1-8
        W,H are in pixels typ 128,16
    """
    global foreStack,backStack , fore, back
    ##################################
    #Adjust for clipping
    ##################################
    clipHigh = 1e8
    clipLow = 0
    #read all the image files
    for fIdex in range( back.numImages ):
        (mdB,dataB) = back.getFrame()
        #  return frameParms, lengthParms, frameMeta, capNum, data, frameNum, integTime, interTime
        backStack[ mdB.frameNum-1,(mdB.capNum-1)%8,:,:] += np.resize(dataB,[512,512])

    avgBack = backStack/( back.numImages/8.0)

    for fIdex in range( fore.numImages):
        (mdF,dataF) = fore.getFrame()
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

    # Create new Runs
    takeData( parameters, overwrite = 1,
       runVaryCommand="DFPGA DAC_OUT_VREF_BUF", varRange = np.arange(0,3,0.5) )
    
    # Analyze the data
    analyzeData(parameters)
