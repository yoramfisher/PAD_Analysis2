#!/bin/bash
# File: bm.sh
# 3/6/20 - YF - Inception
#Long Description:
#  Turn on Sensor
#  do stuff
#  Turn off sensor
#  get frames
#
#  Usage bm -n NNN -e EEE
#      NNN is number of frames.
#      EEE is exposure time in usec
#  Example:
#     bm -n 100 -e 200  # takes 100 images, exp time = 200us


#
# set defaults
#
nFrames=100
integration=100; # in usec


#
#parse input parameters
#
while (( "$#" )); do
   case "$1" in
      -n) shift
          nFrames="$1"
          ;;
      -e) shift
          integration="$1"
          ;;
      
   esac
   shift
done


#
#
#
set -x # show commands as they run


# Path to binary
mmcmd="/home/sydor/projects/mm-pad-client-cmdline/bin/debug/mmcmd"

# run mmclient in script mode if not already running
./LaunchIfNeeded.sh

$mmcmd open

$mmcmd stop



sleep 1



$mmcmd "Trigger_Count 0"


#Set number of frames
$mmcmd "frame $nFrames"

#set integration time in microseconds ( note: actual time may now be correct)
$mmcmd "integration_usec $integration"

#set max_frames_count
$mmcmd "Max_Frame_Count 20"

#set set name
$mmcmd "startset yoram"


#Turn on power
$mmcmd "Power_Control 1"

sleep 2

#
	#  Background image
	#
	# assumes a hardware trigger
	$mmcmd "startrun -t"  
   for n in {1..20}
   do
      
      #$mmcmd "status -wait"
      echo "n:$n,  ********* MOVE Z motor. ************"
      sleep 4
      $mmcmd "trigger"
   done
   
  
   # Retrieve run 
   $mmcmd "getframe -20"
  

   sleep 1
#Turn off power
$mmcmd "Power_Control 0"

