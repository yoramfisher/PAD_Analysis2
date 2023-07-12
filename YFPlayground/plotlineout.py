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
import pickle
from dg645 import comObject
from dg645 import DG645

#
# Define some globals
#
VERBOSE = 1 # 0 = quiet, 1 = print some, 2 = print a lot

foreStack = []
backStack = []
fore = None
back = None

NRUNS = 1
RAIDPATH="/mnt/raid/keckpad"
dg = None
    
#
#
#
def takeData( params, list_commands, 
    overwrite = 1,
    runVaryCommand="", varRange = None,
    runFrameCommand = None ):
    """ 
        Run multiple Runs - issuing one command (one parameter) that changes
        at each run.
        params is a dictionary
        overWrite. Set to 1 to delete previous Runs
        list_commands = [list of string commands to send to HW ]
        runVaryCommand = string commmand
        varRange = numpy.arange( , ,) 
        
        runFrameCommand - pass in a function to call at each frame in a run
        Return dictionary of results
    """
    global  foreStack,backStack, fore, back
    

    # if len(params) < 8:
    #     print(" Usage: ~ setname runname FrameNum nTap zASICX zASICY ROIW ROIH")
    #     exit(0)


    setname = params["setname"]
    runname = params["runname"]
    nFrames = params["nFrames"]


    if overwrite:
        # delete old runs
        # rm -r "$RAIDPATH"/set-$setname/run-run_*
        for match in glob(f"{RAIDPATH}/set-{setname}/run-run_*"):
            shutil.rmtree(match)
            print(f"***DELETE RUN {match}")

    #
    # Create list of commands
    #  
    res = True
   
     
    
    #
    # Run through list of commands - and send them to HW
    #
    for c in list_commands:
        if VERBOSE:
            print(f"**RUN_CMD {c}")
        res = xd.run_cmd( c  )   
        if res:
            return None

    if varRange is not None:
        NRUNS = len(varRange)

    #
    # Start a series of Runs
    #
    runCount = 0
    for i in range(1, NRUNS + 1):     
        # scan a parameter here. Pass in runVaryCommand and varRange
        if runVaryCommand:
            var = varRange[0]
            varRange = varRange[1:] # remove first element
            c  = f"{runVaryCommand} {var}"
            res = xd.run_cmd(c)
            if res:
                break

        runname=f"run_{i}"        
        res = xd.run_cmd( f"startrun {runname}"  )   
        if res:
            break

        # Optionally set SRS options here and trigger SRS for each frame in the run
        # Loop <nFrames> times
        #  
        if runFrameCommand:
            for j in range(nFrames):
                runFrameCommand(j)

        xd.run_cmd( f"status -wait" )
        runCount += 1

    return {
        "parameters": params,
        "runCount":runCount,
        "runVaryCommand":runVaryCommand,
        "varRange":varRange
    }   

#
#
#
def analyzeData(aDict):
    """
    Load up the runs, and analyze
    aDict should contain "parameters", "runCount", "runVaryCommand", "varRange"
    """

    params = aDict["parameters"]
    setname = params[0]
    runname = params[1]

    foreFile = f'/mnt/raid/keckpad/set-{setname}/run-{runname}/frames/{runname}_00000001.raw' # check not sure...

    #DEBUG w local file on Windows
    foreFile = r"C:\Sydor Technologies\temptst_00000001.raw" 
    

    fore = BKL.KeckFrame( foreFile )

    backFile = f'/mnt/raid/keckpad/set-{setname}/run-back/frames/run_1_00000001.raw' 

    #DEBUG w local file on Windows
    backFile= r"C:\Sydor Technologies\temptst2_T21_00000001.raw" 

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
    global foreStack,backStack, fore, back 
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

    #  [ Frame, Cap, Y , X ] # TODO: check Y,X is correct
    PerCapImage = DiffStack[:,cap,:,:]
    
    startPixY = zSY * 128 + (nTap-1) * 16
    endPixY = startPixY + H
    startPixX = zSX * 128
    endPixX = startPixX + W
    # frame 0 hardcoded for now
    #                       frame  ,     Y,   X  
    plt.imshow( PerCapImage[0, startPixY:endPixY, startPixX:endPixX]) # might be flipped?? #WIP#
    plt.show()
 
   
#
# useFunction is called for each frame of a run ( assumes an external trigger )
#
def userFunction( nLoop ):
    """ nLoop is the frame number. 
    """
    global dg
    print(f"Called userFunction n={nLoop}")
    dg.counter  = nLoop + 1
    s = f"BURC {dg.counter}" # Set the burst Count
    dg.send(s);
    dg.doTrigger()
    

def Take_Data(constStringName):
    global dg

    if constStringName == "Sweep_SRS_BurstCount":


        # Setup is using 1 VCSEL inside the integrating sphere. With 
        # Width Switch; the three rightmost switches (towards power connector) are down:
        # 1 1 1 1 1 0 0 0,  and there is one piece of silver mylar IFO the VCSEL 
        # Set HW parameters
        setname = 'xpad-linscan'
        runname = 'varyVrefBuf'
        nFrames = 30  # frames Per Run
        # SRS is setup with PER of 100us, so 30 takes 3ms
        integrationTime = 5000000 # 5.0 millseconds
        interframeTime = 1000 # 1 usec

        # Create a dictionary of required parameters to define the run and later analysis
        parameters= {
            "setname": setname,
            "runname": runname, 
            "nFrames" : nFrames
        }



        # Using an SRS DG645 box:
        IP_ADDR = "192.168.11.225"  
        c = comObject( 1, IP_ADDR )
        r = c.tryConnect()
        dg = DG645( c )
        dg.counter = 0 # truly python hackery

        dg.send("*CLS") # Clear errors

        list_commands = [
            "stop",
            "Trigger_Mode 2",
            f"Image_Count {nFrames}",
            "Cap_Select 0xF",
            f"Interframe_Nsec {interframeTime}",
            f"Integration_Nsec {integrationTime}",
            f"startset {setname}"
        ]
        # Create new Runs
        # Returns number of runs saved
        takeDataRet = takeData( parameters, list_commands,
            overwrite = 1,
            runVaryCommand="DFPGA_DAC_OUT_VREF_BUF", 
            varRange = np.arange(1033,1533,100),
            runFrameCommand = userFunction )
        
        if (takeDataRet != None and takeDataRet["runCount"] > 0):
            # Pickle the results
            pickleFile = open('plo_dump.pickle', 'wb')
            pickle.dump(takeDataRet, pickleFile);
            pickleFile.close()
            return takeDataRet # return dictionary

        else:
            print(" Oh Oh. something went wrong.")
            return (0) # error    


    

# Entry point of the script
if __name__ == "__main__":
    # Code to be executed when the script is run directly
    print("Start.")
    TAKE_DATA = 1
    LOAD_DATA = 0

    
    if (TAKE_DATA):
        Take_Data("Sweep_SRS_BurstCount")

    if (LOAD_DATA):    
        ####
        pickleFile = open('plo_dump.pickle', 'rb')
        takeDataRet =  pickle.load(pickleFile)
        pickleFile.close()
        # Analyze the data
        analyzeData(takeDataRet)

    print("Done!")     
