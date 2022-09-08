#!/bin/bash
# File: RingWalker.sh
# 6/16/22 - YF - Inception
# BWM EDITS
#Long Description:
#  Assume  Sensor is on
#  Scan delay time  for each run
#
# Usage
#   RingWalker.sh <setname>

set -x # show commands as they run
# Define deltaT
deltaT=10 # in ns

setname=${1:-bias}
echo "setname = $bias"



# Path to binary
#mmcmd="/home/sydor/projects/mm-pad-client-cmdline/bin/debug/mmcmd"
mmcmd="mmcmd"

# run mmclient in script mode if not already running
./LaunchIfNeeded.sh



$mmcmd open 1

$mmcmd stop


sleep 1

nFrames=10
integ=20 # in ms


#Set number of frames
#$mmcmd "Image_Count $nFrames"
$mmcmd "SW_Trig"
#$mcmd "Integration_MSec $integ"




#set set name - $1 is passed in parameter
$mmcmd "startset $setname"


   for i in {1..10}
   do
      let "bias = 800 + i * 100"

      $mmcmd "DFPGA_DAC_OUT_V_ISS_BUF $bias" 
      sleep 5

      bname="scan_issbuf_b_$bias"
	  $mmcmd "startrun $bname" 

      $mmcmd "status -wait"
      

      $mmcmd "Shutter_Open 1"
      sleep 5
      runname="scan_issbuf_f_$bias"
      $mmcmd "startrun $runname"  
             
      $mmcmd "status -wait"
      $mmcmd "Shutter_Open 0"
      
   done
        
   $mmcmd "status -wait -verbose"
   $mmcmd "Shutter_Open 0"

