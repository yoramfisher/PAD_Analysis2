#!/usr/bin/env python3
# File: plotlineout.py
# Description - Used to Take and Analyze data on KeckPAD
# Requires an SRS box connected via Ethernet.   Varies a parameter (such as VREF_BUF) while
# sweeping the light source intensity by varying the number of pulses in BURST mode. 
# Used to map out the linearity and perhaps find the most-linear on DC biases.
#
# History
# v 0.1 6/13/23 YF - Inception
# v 0.2 6/29/23 YF - Shift to not using any bash scripts. Instead commands run directly from Python.
#
# v 0.3 7/12/23 YF Take_Data works well.
#
import numpy as np
import Big_keck_load as BKL
import os
import shutil
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
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
P = []

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
    ####global  foreStack,backStack, fore, back
    

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
# not used
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
# userFunction is called for each frame of a run ( assumes an external trigger )
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
        # Returns a dictionary
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


def Analyze_Data(constStringName):
    """
    Load up the runs, and analyze
    """
    global foreStack,backStack, fore, back 
    if constStringName == "Sweep_SRS_BurstCount":
        setname = 'xpad-linscan'
        #runname = 'varyVrefBuf'
        cap = 1
        roi = [46, 92, 32, 20]
        NRUNS = 5
        NCAPS = 3 # can this be pulled from file?
        runVaryCommand="DFPGA_DAC_OUT_VREF_BUF", 
        varRange = np.arange(1033,1533,100),
 
    
    else:
        return # error out

    roiSum = None
    for runnum in range(NRUNS):
        runname = f"run_{runnum+1}"
        foreFile = f'/mnt/raid/keckpad/set-{setname}/run-{runname}/frames/{runname}_00000001.raw' # check not sure...
        fore = BKL.KeckFrame( foreFile )

        numImagesF = fore.numImages 
        if roiSum is None:
            roiSum = np.zeros((NRUNS,numImagesF // NCAPS, NCAPS),dtype=np.double)
        
        # create global big arrays to hold images
        foreStack = np.zeros((numImagesF // NCAPS, NCAPS,512,512),dtype=np.double)
        fore.NCAPS = NCAPS # Python tom-foolery



        roiSum = plotLinearity( fore, roi, data = roiSum, runnum = runnum)

    if runVaryCommand:
       title = f"{runVaryCommand} {varRange}"
 
    prettyPlot (roiSum, title)
    

#
#
#
def prettyPlot(data, title):
    nruns = len(data)

    fig, ax = plt.subplots()
    #plt.figure(1)
    nframes = len(data [0])
    for n in range(nruns):
        x = .5 +.5*(n / (nruns-1))
        ax.plot( range(nframes), data[n,:,0], 
            label="Cap1" if n==0 else "", color=( x,0,0) )

    for n in range(nruns):
        x = .5 +.5*(n / (nruns-1))
        ax.plot( range(nframes), data[n,:,1], 
            label="Cap2" if n==0 else "", color = (0,0,x) )

    for n in range(nruns):
        x = .5 +.5*(n / (nruns-1))
        ax.plot( range(nframes), data[n,:,2], 
            label="Cap3" if n==0 else "", color = (0,x,0)) 


    plt.legend()
    plt.xlabel('N')
    plt.ylabel('mean (ADU)')
    plt.title( title )
    ax.yaxis.set_minor_locator( MultipleLocator(1000))
    plt.show(block=True) 



def plotLinearity(fore, roi, data=None, runnum = 0):
    """
    fore is BKL.Keckframe
    roi is [x,y,W,H]
    title 
    data is [#run, #frame, #cap]
    runnum increments from 0 to #run-1
    """
    global foreStack,backStack
    global P
   
    ncaps = fore.NCAPS

    for fIdex in range( fore.numImages):
        (mdF,dataF) = fore.getFrame()
        frameNum = fIdex // ncaps  # not a typo "//" is integer division 
        dataArray = np.resize(dataF,[512,512])
        foreStack[frameNum,(mdF.capNum-1) % ncaps,:,:] = dataArray

    #  [ Frame, Cap, Y , X ] # TODO: check Y,X is correct
    
    # rio is [X,Y,W,H]
    startPixY = roi[1]
    endPixY = startPixY + roi[3]
    startPixX = roi[0]
    endPixX = startPixX + roi[2]
    nImages =  fore.numImages // ncaps  # not a typo "//" is integer division 
    

    for fn in range( nImages ): 
        for cn in range (ncaps):
            data[runnum, fn,cn] = np.average( foreStack[fn, cn, startPixY:endPixY, startPixX:endPixX] )
            #print( fn, cn, roiSum)

    return data

    #plt.figure(1)
    #plt.plot( range(nImages), roiSum[:,0], label="Cap1") 
    #plt.plot( range(nImages), roiSum[:,1], label="Cap2") 
    #plt.plot( range(nImages), roiSum[:,2], label="Cap3") 


    #plt.legend()
    #plt.xlabel('N')
    #plt.ylabel('mean (ADU)')
    #plt.title( title )
    #plt.show(block=True) 



# Entry point of the script
if __name__ == "__main__":
    # Code to be executed when the script is run directly
    print("Start.")
    TAKE_DATA = 0
    LOAD_DATA = 1

    
    if (TAKE_DATA):
        Take_Data("Sweep_SRS_BurstCount")

    if (LOAD_DATA):    

        Analyze_Data("Sweep_SRS_BurstCount")

        ####
        #pickleFile = open('plo_dump.pickle', 'rb')
        #takeDataRet =  pickle.load(pickleFile)
        #pickleFile.close()
        # Analyze the data
        #analyzeData(takeDataRet)

    print("Done!")     
