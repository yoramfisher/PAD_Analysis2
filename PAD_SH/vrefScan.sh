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
echo "setname = $ringwalker"



# Path to binary
#mmcmd="/home/sydor/projects/mm-pad-client-cmdline/bin/debug/mmcmd"
mmcmd="mmcmd"

# run mmclient in script mode if not already running
./LaunchIfNeeded.sh

# warn if deleting first
# todo: remove directories:
# loop:
#  rm -rf "/mnt/raid/set-$setname/"
  
#  rm "/home/sydor/Sydor/mmclient/out/default/Fore_$integration"
#  rm "/home/sydor/Sydor/mmclient/out/default/Back_$integration"

$mmcmd open 1

$mmcmd stop


sleep 1

nFrames=10
##integration=100; # in usec


#Set number of frames
$mmcmd "Image_Count $nFrames"
$mmcmd "SW_Trig"


#set integration time in microseconds ( note: actual time may now be correct)
##$mmcmd "integration_usec $integration"


#set set name - $1 is passed in parameter
$mmcmd "startset $setname"


#Turn on power
#$mmcmd "Power_Control 1"

#sleep 2

#
	#  Background image
	#
	# assumes a hardware trigger
	$mmcmd "startrun vref_Back"  
   $mmcmd "status -wait"
   # Retrieve run 
   #$mmcmd "getframe -$nFrames"
  
   $mmcmd "Shutter_Open 1"
   sleep 1
 
	#  Foreground image
	#

	#set integration time in microseconds ( note: actual time may now be correct)
	#$mmcmd "integration_usec $integration"

	#assumes a hardware trigger

   for i in {1..10}
   do
      let "bias = 900 + i * 100"


      #echo "DEBUG: About to StartRun" & read -n 1 -s
      $mmcmd "DFPGA_DAC_OUT_VREF_BUF $bias" 
       
      $mmcmd "DFPGA_DAC_OUT_VREF_BP $bias"  
      runname="scan_vref_$bias"
      $mmcmd "startrun $runname"  
             
      $mmcmd "status -wait"

   done
        
   $mmcmd "status -wait -verbose"
   $mmcmd "Shutter_Open 0"

