#Filename: TBD
# Description: Generate Data for Final Report SMK 020 (LANL)
#
#
# Keywords:
#  FlatField


#
# Define some globals
#
VERBOSE = 1 # 0 = quiet, 1 = print some, 2 = print a lot



import numpy as np
import Big_keck_load as BKL
import os
import matplotlib.pyplot as plt
import sys
import tkinter.filedialog as fd
import pickle as pkl
##import Geo_Corr as gc
import UI_utils



def file_select(Type):
   filename = fd.askopenfilename(
      title = "Open " + str(Type),
      initialdir = "/mnt/raid/keckpad/set-HeadRework",
  
   )
   return filename


#
# 
# 
class dataObject:
   def __init__(self, strDescriptor):
      self.TEST_ON_MAC = True

      self.strDescriptor = strDescriptor
      self.rootPath = r"Z:\Project#_1300_1499\#1415 SM HE Keck CdTe LANL\set-SMK020FTR"
      self.createObject()
      

   def makeData(self):
      self.FFImage = 0 # set to 0 if dont want to FF
      self.baseFileName = "50KV_0C_1ms_cap"
      W = self.roi[2]
      H = self.roi[3]
      self.data = np.zeros((8, H, W),dtype=np.double)
      
      for cap in range(0,8):
         aveData = self.openRunAndCreateData( cap )
         self.data[cap,:,:] = aveData 


   def  openRunAndCreateData( self,cap ):
      """
      Returns 2-D array, defined by ROI. Averaged over N images. F-B
      """
      backFile = self.rootPath +  \
         f"\\run-{self.baseFileName}{cap}_b" +  r"\frames" + f"\\{self.baseFileName}{cap}_b_00000001.raw"
      foreFile = self.rootPath + \
           f"\\run-{self.baseFileName}{cap}_f" +  r"\frames" + f"\\{self.baseFileName}{cap}_f_00000001.raw"
      

      if self.TEST_ON_MAC: # Local Mac testing!
         foreFile = f'/Users/yoram/Sydor/keckpad/30KV_1.5mA_40ms_f_00015001.raw' 
         backFile = f'/Users/yoram/Sydor/keckpad/30KV_1.5mA_40ms_f_00015001.raw' 
         

      cwd = os.getcwd()
      back = BKL.KeckFrame(backFile)
      fore = BKL.KeckFrame(foreFile)

      numImagesF = fore.numImages
      numImagesB = back.numImages


      foreStack = np.zeros((8,512,512),dtype=np.double)
      backStack = np.zeros((8,512,512),dtype=np.double)
      FFStat = "noFF"
      if self.FFImage ==1 :
         fileObject = open(cwd + "/pickleFF.pi", 'rb')  # not at all tested will break 4 sure
         ffCorect = pkl.load(fileObject)
         fileObject.close()
         FFStat = "FF"
      else: 
         ffCorect = 1


      ##################################
      #Adjust for clipping
      ##################################
      clipHigh = 5e2
      clipLow = 0
      #read all the image files
      for fIdex in range(numImagesB):
         (mdB,dataB) = back.getFrame()
         backStack[cap,:,:] += np.resize(dataB,[512,512])
            
      avgBack = backStack/numImagesB
      
      for fIdex in range(numImagesF):
         (mdF,dataF) = fore.getFrame()
      
         foreStack[cap,:,:] += np.resize(dataF,[512,512])

      avgFore = foreStack/numImagesB

      if self.TEST_ON_MAC:
         plotData = (avgFore) * ffCorect

      else:
         plotData = (avgFore-avgBack) * ffCorect


      plotData = np.clip(plotData, clipLow, clipHigh)
      #tavgplotData = gc.GeoCor(np.average(plotData, axis=0))
      
      tavgplotData = np.average(plotData, axis=0)
      
      # rio is [X,Y,W,H]
      startPixY = self.roi[1]
      endPixY = startPixY + self.roi[3]
      startPixX = self.roi[0]
      endPixX = startPixX + self.roi[2]
      result =  tavgplotData[  startPixY:endPixY, startPixX:endPixX ]
      return result


   def makePlot(self):
      allplot = []
      dim0 = self.data.shape[0] 
      for val in range(dim0):
         #allplot.append(gc.GeoCor(self.data[val,:,:]))
         allplot.append(self.data[val,:,:])


      indexVal =  (-1)
      fig,ax = plt.subplots(2,4,sharex='col', sharey='row')

      for pic in allplot:
         indexVal += 1 
         indexRow = int(indexVal/4) 
         indexCol = int(indexVal%4)
         #indexVal = allplot.index(pic)
         image = ax[indexRow,indexCol].imshow(pic, cmap = "viridis")
         # ax.imshow(pic)
         # fig,ax = plt.subplots(1)
         #needed to add more stuff
         # image = ax.imshow(clipData, cmap = "viridis")
         cbar = fig.colorbar(image, aspect=4, ax = ax[indexRow,indexCol])
         ax[indexRow,indexCol].set_title('Keck Cap'+ str(indexVal))
         if indexCol == 0:
            ax[indexRow,indexCol].set_ylabel("Pixel")
         if indexRow == 1:   
            ax[indexRow,indexCol].set_xlabel("Pixel")
         cbar.set_label ("Counts (ADU)")
         


      fig.set_size_inches(12, 4)    
      fig.subplots_adjust(wspace = 0.645, hspace = -0.2) # space is padding height
      




      ##fig.savefig(foreFile + FFStat + "_AvgAll.png")
      ##plotData1 = plotData[0,:,:]


   def createObject(self):
      # ****************************************************
      if self.strDescriptor == "Flatfield":            
         # with geo self.roi = [262, 144, 256+1, 128]
         self.roi = [256, 128, 256, 128]
         self.NCAPS_per_file = 1 
         self.fcnToCall = self.makeData
         self.fcnPlot   =  self.makePlot
         
      else:
         raise Exception(" !Unknown string! ")    
      

  
   #
   # 
   #         
   def Analyze_Data(self):
      """
      Load up the runs, and analyze
      """
      self.fcnToCall()
      self.fcnPlot()






if 0:
   
   
   
   avg,axs = plt.subplots(1)
   imageAvg = axs.imshow(avgplotData, cmap = "viridis")
   Acbar = avg.colorbar(imageAvg, aspect=10)
   axs.set_title('Keck Cap Average')
   axs.set_ylabel("Pixel")
   axs.set_xlabel("Pixel")
   Acbar.set_label ("Counts (ADU)")
   # fig.set_size_inches(20, 10)    
   # fig.subplots_adjust(wspace = 0.545)
   avg.savefig(foreFile + FFStat +"_Avg.png")

   # plt.imshow(plotData)


   
   #average the data across all 8 caps
   plotData = np.average(plotData, axis=0)
   #clip data below to get rid of hot pixels and negative pixels
   clipData = np.clip(plotData, clipLow, clipHigh)

   ########################
   #code to plot all 8 caps individually
   ########################

   # plt.imshow(plotData)
   # # fig,axs = plt.subplots(2,4)
   # # axs[0,0].imshow(plotData[0,:,:])
   # # axs[0,1].imshow(plotData[1,:,:])
   # # axs[0,2].imshow(plotData[2,:,:])
   # # axs[0,3].imshow(plotData[3,:,:])
   # # axs[1,0].imshow(plotData[4,:,:])
   # # axs[1,1].imshow(plotData[5,:,:])
   # # axs[1,2].imshow(plotData[6,:,:])
   # # axs[1,3].imshow(plotData[7,:,:])
   # #plt.imshow(fmb[3,:,:])
   # plt.show()

   ###################
   #Code to plot and save one image with labels and such
   ###################

   # fig,ax = plt.subplots(1)
   # image = ax.imshow(clipData, cmap = "viridis")
   # cbar = fig.colorbar(image, aspect=10)
   # ax.set_title('DCS Keck')
   # ax.set_ylabel("Pixel")
   # ax.set_xlabel("Pixel")
   # cbar.set_label ("Counts (ADU)")
   #fig.savefig(foreFile + "_Avg.png")
   plt.show()

   #################
   #3d Projection plot code example
   ########################
   # fig = plt.figure()
   
   # # syntax for 3-D projection
   # fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
   
   # # defining all 3 axes
   # z = clipData
   # x = range(512)
   # y = range(512)

   # X, Y = np.meshgrid(x, y)

   # # plotting


   # surf = ax.plot_surface(X, Y, z,cmap ='viridis')
   # fig.colorbar(surf, shrink=0.5, aspect=5)
   # ax.set_title('DCSKeck')
   # plt.show()
   #############################


   plt.show()





def defineListOfTests():
    """
    Create a list of (string,string) that DEFINES the 
    Analyze data routines, and give each a text description
    NOTE that the string MUST match those in createObject
    """

    lot = []
    lot.append( ("Flatfield","Analyze the 8 FF files. ") )
    # TODO - add more here
    return lot




# Entry point of the script
if __name__ == "__main__":
   # Code to be executed when the script is run directly
   print("Start.")

   # 
   # Create a list of possible actions - and display a modal
   #
   lot = defineListOfTests()
   ui = UI_utils.UIPage( lot )
   ui.show()
   if ui.cancelled:
      exit(0)

      
   strDescriptor = ui.selectedText
   bTakeData,bAnalyzeData = ui.selectedActions

   print(f"I will run {strDescriptor} and " + "Take Data" if bTakeData else "" + "  Analyze Data" if bAnalyzeData else "" )


   #
   # Do the things
   #
   dobj = dataObject( strDescriptor)

   ret = dobj.Analyze_Data()
   plt.show()
