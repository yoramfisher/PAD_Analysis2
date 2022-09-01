#!/bin/bash
# File: scopeTesting.sh
# 3/6/20 - YF - Inception
#Long Description:
#  Turn on Sensor
#  Turn off sensor


set -x # show commands as they run

# Path to binary
mmcmd="/home/sydor/projects/mm-pad-client-cmdline/bin/debug/mmcmd"

# run mmclient in script mode if not already running
./LaunchIfNeeded.sh

$mmcmd open
$mmcmd stop

nFrames=100
integration=100; # in usec

#Set Trigger Count
$mmcmd "Trigger_Count 1"

#Set number of frames
$mmcmd "frame $nFrames"

#set integration time in microseconds ( note: actual time may now be correct)
$mmcmd "integration_usec $integration"

#set max_frames_count
$mmcmd "Max_Frame_Count $nFrames"

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
   $mmcmd "status -wait"
   # Retrieve run 
   #$mmcmd "getframe -$nFrames"
  

sleep 1
#Turn off power
$mmcmd "Power_Control 0"




