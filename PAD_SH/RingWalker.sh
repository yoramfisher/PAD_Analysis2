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

setname=${1:-yoram}
echo "setname = $ringwalker"



# Path to binary
#mmcmd="/home/sydor/projects/mm-pad-client-cmdline/bin/debug/mmcmd"
mmcmd="mmcmd"

# run mmclient in script mode if not already running
./LaunchIfNeeded.sh

# warn if deleting first
# todo: remove directories:
# loop:
  rm -rf "/mnt/raid/set-$setname/"
  
#  rm "/home/sydor/Sydor/mmclient/out/default/Fore_$integration"
#  rm "/home/sydor/Sydor/mmclient/out/default/Back_$integration"

$mmcmd open 1

$mmcmd stop


sleep 1

nFrames=100
##integration=100; # in usec


#Set number of frames
$mmcmd "Image_Count $nFrames"
$mmcmd "Ext_Trig 1"


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
	#$mmcmd "startrun -t"  
   #$mmcmd "status -wait"
   # Retrieve run 
   #$mmcmd "getframe -$nFrames"
  

   #sleep 1
 
	#  Foreground image
	#

	#set integration time in microseconds ( note: actual time may now be correct)
	#$mmcmd "integration_usec $integration"

	#assumes a hardware trigger

   for i in {1..10}
   do
      let "td_ns = 100 + i * $deltaT"
      let "td_clk = td_ns / 10 "


      #echo "DEBUG: About to StartRun" & read -n 1 -s
      $mmcmd "Trigger_Delay $td_clk"  

      runname="scan_TD_${td_ns}"
      $mmcmd "startrun $runname"  
             
      $mmcmd "status -wait"

   done
        
   $mmcmd "status -wait -verbose"


