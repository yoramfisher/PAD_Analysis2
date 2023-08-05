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
# v 0.4 7/31/23 OOP the S out of it. You should be able to edit createObject() to generate
#  most data runs where one thing is varied per Run and another thing is varied per frame.
# v 0.5 8/5/23 tkinter graphics

import numpy as np
import Big_keck_load as BKL
import os
import shutil
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import sys
#import tkinter as tk
import xpad_utils as xd
from glob import glob
import pickle
from dg645 import comObject
from dg645 import DG645
import time
#from ipywidgets import *
#from IPython.display import display
import UI_utils


#
# Define some globals
#
VERBOSE = 1 # 0 = quiet, 1 = print some, 2 = print a lot
#
#
# User edit settings
RAIDPATH="/mnt/raid/keckpad"

#
# 
#   
 
# OOP the heck out of this
class dataObject:
    def __init__(self, strDescriptor, 
                 bTakeData=False, bAnalyzeData = False):
        self.strDescriptor = strDescriptor
        self.dg = None  # Optional Delay Generator
        self.createObject()
        self.overwrite = True  # Set to true to delete previous runs
        self.bTakeData = bTakeData
        self.bAnalyzeData = bAnalyzeData
        self.TEST_ON_MAC = False
        self.TakeBG = False



    #
    # userFunction is called for each frame of a run ( assumes an external trigger )
    #
    def userFunction( self,nLoop ):
        """ nLoop is the frame number. 
        """
        
        print(f"Called userFunction n={nLoop}")
        self.dg.counter  = nLoop + 1
        s = f"BURC {self.dg.counter}" # Set the burst Count
        self.dg.send(s);
        self.dg.doTrigger()
        
    #
    # userFunction is called for each frame of a run ( assumes an external trigger )
    #
    def userFunctionB( self, nLoop ):
        """ nLoop is the frame number. 
        """
        print(f"Called userFunctionB n={nLoop}")
        c  = f"{self.innerVarCommand} {self.innerVarRange[nLoop]}"  
        
        res = xd.run_cmd(c)
        self.dg.doTrigger()


    def createObject(self):
        # ****************************************************
        if self.strDescriptor == "Sweep_SRS_BurstCount":
            # Setup is using 1 VCSEL inside the integrating sphere. With 
            # Width Switch; the three rightmost switches (towards power connector) are down:
            # 1 1 1 1 1 0 0 0,  and there is one piece of silver mylar IFO the VCSEL 
            # Set HW parameters
            self.setname = 'xpad-linscan_B27'
            self.nFrames = 30  # frames Per Run
            # SRS is setup with PER of 100us, so 30 takes 3ms
            self.integrationTime = 5000000 # 5.0 millseconds
            self.interframeTime = 1000 # 1 usec

            # create a list of commands to send to hardware via mmcmd 
            unique_commands = [ 
                "Cap_Select 0xF"       
            ]

            
            self.runVaryCommand="DFPGA_DAC_OUT_VREF_BUF" 
            self.varRange = [1000, 1200, 1400, 1600, 1800, 2000] 
            self.runFrameCommand = self.userFunction 

            self.roi = [46, 92, 32, 20]
            self.NCAPS = 3 # can this be pulled from file?
            self.fcnToCall = plotLinearity
            self.roiSumNumDims = 3
            self.fcnPlot = prettyPlot
  
        # ****************************************************
        elif self.strDescriptor == "Sweep_Interframe1":
            # Setup is using 1 VCSEL inside the integrating sphere. With 
            # Width Switch; the three rightmost switches (towards power connector) are down:
            # 1 1 1 1 1 0 0 0,  and there is one piece of silver mylar IFO the VCSEL 
            # Set HW parameters
            self.setname = 'xpad-linscan_B100_IF1'
            self.nFrames = 20  # frames Per Run
            # SRS is setup with PER of 100us, so 20 takes 2ms
            self.integrationTime = 3000000 # 3.0 millseconds
            self.interframeTime = 100 # 100 nSec # gets swept #

            # create a list of commands to send to hardware via mmcmd 
            unique_commands = [ 
                "Cap_Select 0xF"       
            ]

            
            self.runVaryCommand="InterFrame_NSec" 
            self.varRange = [200, 500, 1000, 2000, 5000, 10000] 
            self.runFrameCommand = self.userFunction 

            self.roi = [46, 92, 32, 20]
            self.NCAPS = 3 # can this be pulled from file?
            self.fcnToCall = plotLinearity
            self.roiSumNumDims = 3
            self.fcnPlot = prettyPlot

        # ****************************************************
        elif self.strDescriptor == "Sweep_Inter1":               
            # How does the slope of dark frames change as we change the interframe1 time? 
            # Set HW parameters
            self.setname = 'xpad-scan_inter1_B27'
            self.nFrames = 10  # frames Per Run  
          
            # We ARE 'allowed' to change delay param in a run (!)
            
            self.integrationTime = 100 # 100ns
            self.interframeTime = 100  # 100 ns - initial same on all.
            
            # create a list of commands to send to hardware via mmcmd 
            unique_commands = [ 
                "Cap_Select 0x1FF",
            ]
           
            self.runVaryCommand="Readout_Delay" 
            self.varRange = [0,50,100,150]
            self.runFrameCommand = self.userFunctionB
            self.innerVarRange = [100,1100,2100,3100,4100,5100,6100,7100,8100,9100]
            self.innerVarCommand ="Interframe_nsec[1]" # [0] does not work correctly BUG!

            self.roi = [0, 7*16, 128, 16]
            self.NCAPS = 8 # can this be pulled from file?
            self.fcnToCall = plotEachCapLineout
            self.roiSumNumDims = 4
            self.fcnPlot = prettyAllCapsInALine

        # ****************************************************
        elif self.strDescriptor == "Sweep_w_Background":
            # Setup is using 1 VCSEL inside the integrating sphere. With 
            # Width Switch; the three rightmost switches (towards power connector) are down:
            # 1 1 1 1 1 0 0 0,  and there is one piece of silver mylar IFO the VCSEL 
            # Set HW parameters
            self.TakeBG = True
            self.setname = 'zzz'
            self.nFrames = 20  # frames Per Run
            # SRS is setup with PER of 100us, so 20 takes 2ms
            self.integrationTime = 3000000 # 3.0 millseconds
            self.interframeTime = 100 # 100 nSec # gets swept #

            # create a list of commands to send to hardware via mmcmd 
            unique_commands = [ 
                "Cap_Select 0x1FF"       
            ]

            
            self.runVaryCommand="InterFrame_NSec" 
            self.varRange = [500] 
            self.runFrameCommand = self.userFunction 

            self.roi = [0, 7*16, 128, 16]
            self.NCAPS = 8 # can this be pulled from file?
            self.fcnToCall = plotEachCapLineout
            self.roiSumNumDims = 4
            self.fcnPlot = prettyAllCapsInALine    

        # ****************************************************
        elif self.strDescriptor == "Sweep_Integ1":               
            # How does the slope of dark frames change as we change the interframe1 time? 
            # Set HW parameters
            self.setname = 'xpad-scan_integ1_B27'
            self.nFrames = 5  # frames Per Run  
          
            # We ARE 'allowed' to change delay param in a run (!)
            
            self.integrationTime = 100 # 100ns
            self.interframeTime = 100  # 100 ns - initial same on all.
            
            # create a list of commands to send to hardware via mmcmd 
            unique_commands = [ 
                "Cap_Select 0x1FF",
            ]
           
            self.runVaryCommand="Readout_Delay"
            self.varRange = [0,50,100,150]
            self.runFrameCommand = self.userFunctionB
            self.innerVarRange = [100,2100,6100,10100,20100]
            self.innerVarCommand ="Integration_nsec[1]" # [0] does not work correctly BUG!

            self.roi = [0, 7*16, 128, 16]
            self.NCAPS = 8 # can this be pulled from file?
            self.fcnToCall = plotEachCapLineout
            self.roiSumNumDims = 4
            self.fcnPlot = prettyAllCapsInALine    


        # ****************************************************
        # create a list of commands to send to hardware via mmcmd 
        self.list_commands = [
            "stop",
            "Trigger_Mode 2",
            f"Image_Count {self.nFrames}",
            f"Interframe_Nsec {self.interframeTime}",
            f"Integration_Nsec {self.integrationTime}",
        ]
        self.list_commands.extend( unique_commands )
        self.list_commands.append(  f"startset {self.setname}" )



    #
    #
    #
    def takeBackground(self):
        setname = self.setname
        nFrames = self.nFrames

        if self.overwrite:
            # delete old runs
            # rm -r "$RAIDPATH"/set-$setname/run-run_*
            for match in glob(f"{RAIDPATH}/set-{setname}/run-back"):
                shutil.rmtree(match)
                print(f"***DELETE RUN {match}")
      
        #
        # Run through list of commands - and send them to HW
        #
        for c in self.list_commands:
            res = xd.run_cmd( c  )    
            if res:
                raise Exception(" Error ")

        NRUNS = 1

        runname=f"-bg back"        
        res = xd.run_cmd( f"startrun {runname}"  )   
        if res:
            raise Exception(" Error ") 

        # Optionally set SRS options here and trigger SRS for each frame in the run
        # Loop <nFrames> times
        #  
        self.runCount = 0
        if self.runFrameCommand:
            for j in range(nFrames):
                self.runFrameCommand(j)
                time.sleep(.5)
                
        xd.run_cmd( f"status -wait" )
        self.runCount += 1

    #
    # 
    #     
    def takeData(self):
        """ 
        Run multiple Runs - issuing one command (one parameter) that changes
        at each run.
        overWrite. Set to 1 to delete previous Runs
        Return Number of runs completed.
        """

        setname = self.setname
        #runname = 
        nFrames = self.nFrames
        varRange = self.varRange

        if self.overwrite:
            # delete old runs
            # rm -r "$RAIDPATH"/set-$setname/run-run_*
            for match in glob(f"{RAIDPATH}/set-{setname}/run-run_*"):
                shutil.rmtree(match)
                print(f"***DELETE RUN {match}")
      
        res = True
      
 
        #
        # Run through list of commands - and send them to HW
        #
        for c in self.list_commands:
            if VERBOSE:
                print(f"**RUN_CMD {c}")
            res = xd.run_cmd( c  )    # there may be a bug in mmcmd  - returns previous string output.
            if res:
                raise Exception(" Error ")

        if varRange is not None:
            NRUNS = len(varRange)

        #
        # Start a series of Runs
        #
        self.runCount = 0
        for i in range(1, NRUNS + 1):     
            # scan a parameter here. Pass in runVaryCommand and varRange
            if self.runVaryCommand:
                var = varRange[0]
                varRange = varRange[1:] # remove first element
                c  = f"{self.runVaryCommand} {var}"
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
            if self.runFrameCommand:
                for j in range(nFrames):
                    self.runFrameCommand(j)
                    time.sleep(.5)
                    
            xd.run_cmd( f"status -wait" )
            self.runCount += 1

        return  self.runCount
    
    
    #
    #
    #
    def Take_Data(self):
        """
        Take Data        
        """        
        # Using an SRS DG645 box:
        IP_ADDR = "192.168.11.225"  
        c = comObject( 1, IP_ADDR )
        r = c.tryConnect()

        # Future me:  dg is used in userFunction to adjust SRS box at each run frame.

        self.dg = DG645( c )
        self.dg.counter = 0 # truly python hackery
        self.dg.send("*CLS") # Clear errors
         
  
        # Create new Runs
        # Returns a dictionary
        if self.takeBackground:
            self.takeBackground()

        takeDataRet = self.takeData( )
        return takeDataRet    
            
    def Analyze_Data(self):
        """
        Load up the runs, and analyze
        """

        setname = self.setname
        NRUNS = len(self.varRange) 
        NCAPS = self.NCAPS
       
        roiSum = None
        for runnum in range(NRUNS):
            runname = f"run_{runnum+1}"
            if self.TEST_ON_MAC: # Local Mac testing!
                foreFile = f'/Users/yoram/Sydor/keckpad/30KV_1.5mA_40ms_f_00015001.raw' # check not sure...
                
            else:
                foreFile = f'/mnt/raid/keckpad/set-{setname}/run-{runname}/frames/{runname}_00000001.raw' # check not sure...
            
            self.fore = BKL.KeckFrame( foreFile )

            numImagesF = self.fore.numImages 
            if roiSum is None:
                if self.roiSumNumDims == 3:
                    roiSum = np.zeros((NRUNS,numImagesF // NCAPS, NCAPS),dtype=np.double)
                elif self.roiSumNumDims == 4:
                    roiSum = np.zeros((NRUNS,numImagesF // NCAPS, NCAPS, self.roi[2]),dtype=np.double)


            # create global big arrays to hold images
            self.foreStack = np.zeros((numImagesF // NCAPS, NCAPS,512,512),dtype=np.double)


            # Each time called, builds up data in data var/ roiSum.
           
            roiSum = self.fcnToCall( self, data = roiSum, runnum = runnum)

            if self.runVaryCommand:
                title = f"{self.runVaryCommand} {self.varRange}"
        
        #
        #  fcnPlot is the function to generate plot. It is defined in the IF's above.
        #
        self.fcnPlot (roiSum, title)





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
    # TODO - we want to measure the amount of gradient, and average them over N Frames - toss out first image.
    # x axis is <varRange>  y axis is <entity> x 8 for each Cap. 
    ave_over_frames = DiffStack[ : , cap, startPixY:endPixX, startPixX:endPixX].mean(axis = 0) # Take average over rows
    data_array = ave_over_frames.mean(axis=0) # does this give me a 1-D over x?
    # Not sure ^ if thats right.

    xd.gradient_over_lineout(data_array)
    plt.show()
 
   
    

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

#
#   Data has <NCAPS> lineouts.  Line them all up into one lineout per image 
#
def prettyAllCapsInALine(data, title):
    """
    data should be [nRuns, nFrames, nCaps, Width_of_lineout]
    """
    nruns = len(data)

    fig, ax = plt.subplots()
    #plt.figure(1)
    nframes = len(data[0])
    ncaps = len(data[0,0] )
    dataWidth = len(data[0,0,0])

    
    for n in range(nruns):     
        for f in range(nframes):
            d = []    
            for c in range(ncaps):
                d.extend( data[n, f, c, :])
            
            x = .5 +.5*(f / (nframes-1))
            if n%3 == 0:
                clr = (x,0,0)
            elif n%3 == 1:    
                clr = (0,x,0)
            elif n%3 == 2:
                clr = (0,0,x)

            ax.plot( range(len(d)), d, color=clr,
            label=f"Run{n}" if f ==0 else "" )



    plt.legend()
    plt.xlabel('1Tap-lineout across ALL caps')
    plt.ylabel('Ave (ADU)')
    plt.title( title )
    ax.yaxis.set_minor_locator( MultipleLocator(1000))
    plt.show(block=True) 


def plotLinearity(dobj, data=None, runnum = 0):
    """
   
    title 
    data is [#run, #frame, #cap]
    runnum increments from 0 to #run-1
    NOTE - Data is NOT plotted, rather data is storted in array data.
    stores the average value over the ROI.
    """
   
    fore = dobj.fore
    roi = dobj.roi
    ncaps = dobj.NCAPS


    for fIdex in range( fore.numImages):
        (mdF,dataF) = fore.getFrame()
        frameNum = fIdex // ncaps  # not a typo "//" is integer division 
        dataArray = np.resize(dataF,[512,512])
        dobj.foreStack[frameNum,(mdF.capNum-1) % ncaps,:,:] = dataArray

    #  [ Frame, Cap, Y , X ] # TODO: check Y,X is correct
    
    # rio is [X,Y,W,H]
    startPixY = roi[1]
    endPixY = startPixY + roi[3]
    startPixX = roi[0]
    endPixX = startPixX + roi[2]
    nImages =  fore.numImages // ncaps  # not a typo "//" is integer division 
    

    for fn in range( nImages ): 
        for cn in range (ncaps):
            data[runnum, fn,cn] = np.average( dobj.foreStack[fn, cn, startPixY:endPixY, startPixX:endPixX] )
            #print( fn, cn, roiSum)

    return data


def plotEachCapLineout(dobj,  data=None, runnum = 0):
    """
    data is [#run, #frame, #cap]
    runnum increments from 0 to #run-1
    NOTE - Data is NOT plotted, rather data is storted in array data.
    stores the average value over the ROI.
    """
   
   
    fore = dobj.fore
    roi = dobj.roi

    ncaps = dobj.NCAPS

    for fIdex in range( fore.numImages):
        (mdF,dataF) = fore.getFrame()
        frameNum = fIdex // ncaps  # not a typo "//" is integer division 
        dataArray = np.resize(dataF,[512,512])
        dobj.foreStack[frameNum,(mdF.capNum-1) % ncaps,:,:] = dataArray

    #  [ Frame, Cap, Y , X ] # TODO: check Y,X is correct
    
    # rio is [X,Y,W,H]
    startPixY = roi[1]
    endPixY = startPixY + roi[3]
    startPixX = roi[0]
    endPixX = startPixX + roi[2]
    nImages =  fore.numImages // ncaps  # not a typo "//" is integer division 
    

    for fn in range( nImages ): 
        for cn in range (ncaps):
            # Hopefully - axis=0 averages over columns
            data[runnum, fn,cn] = np.mean( dobj.foreStack[fn, cn, startPixY:endPixY, startPixX:endPixX], axis=0 )
            #print(f"debug:{data[runnum, fn, cn]}")

    return data







def defineListOfTests():
    """
    Create a list of (string,string) that DEFINES the 
    Take or Analyze data routines, and give each a text description
    NOTE that the string MUST match those in createObject
    """

    lot = []
    lot.append( ("Sweep_SRS_BurstCount", "Using SRS box - adjust burst count to get linear intensity sweeps") )
    lot.append( ("Sweep_Inter1", "Adjust inteframe time [1] - see if the gradient shapes change with delay (they dont)") )
    lot.append( ("Sweep_Integ1", "Adjust integration time [1] - see if the gradient shapes change with delay (they dont)") )
    lot.append( ("Sweep_w_Background", "Sweep linearity with SRS - and also take a background") )
    
    return lot


               


# Entry point of the script
if __name__ == "__main__":
    # Code to be executed when the script is run directly
    print("Start.")
   
    # 
    # Create a list of possible actions - and displayu a modal
    #
    lot = defineListOfTests()
    ui = UI_utils.UIPage( lot )
    ui.show()
    strDescriptor = ui.selectedText
    bTakeData,bAnalyzeData = ui.selectedActions

    print(f"I will run {strDescriptor} and " + "Take Data" if bTakeData else "" + "  Analyze Data" if bAnalyzeData else "" )


    #
    # Do the thing
    #
    dobj = dataObject( strDescriptor, bTakeData=bTakeData, bAnalyzeData=bAnalyzeData)
    
    if dobj.bTakeData:
        ret = dobj.Take_Data()
        if ret == 0:
            exit(0)
        
    if dobj.bAnalyzeData:
        ret = dobj.Analyze_Data()
      
       

    print("Done!")     



