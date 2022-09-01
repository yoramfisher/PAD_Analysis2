#!/bin/bash
# File: ScanExpTime.sh
# 3/5/20 - YF - Inception
#Long Description:
#  Turn on Sensor
#  Take a scan with exp time sweeping
#  Turn off sensor
#  get frames

set -x # show commands as they run

# Path to binary
mmcmd="/home/sydor/projects/mm-pad-client-cmdline/bin/debug/mmcmd"

# run mmclient in script mode if not already running
./LaunchIfNeeded.sh

# warn if deleting first
# todo: remove directories:
# loop:
#  rm "/mnt/raid/set-default/run-Back_$integration"
#  rm "/mnt/raid/set-default/run-Fore_$integration"
#  rm "/home/sydor/Sydor/mmclient/out/default/Fore_$integration"
#  rm "/home/sydor/Sydor/mmclient/out/default/Back_$integration"

$mmcmd open

$mmcmd stop


sleep 1

nFrames=1
integration=100; # in usec
nTriggers=200

#Set number of frames
$mmcmd "frame $nFrames"

#Set number of triggers
$mmcmd "Trigger_Count $nTriggers"

#set integration time in microseconds ( note: actual time may now be correct)
$mmcmd "integration_usec $integration"

#set max_frames_count
mfc=$(expr $nFrames \* $nTriggers)  # ugh bash ...
echo "mfc: $mfc"  # debug

$mmcmd "Max_Frame_Count $mfc"

#set set name
$mmcmd "startset yoram"


#Turn on power
$mmcmd "Power_Control 1"

sleep 2

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
	$mmcmd "integration_usec $integration"

	$mmcmd "startrun -nt $nTriggers -di 500 "  
   $mmcmd "status -wait -verbose"
   # Retrieve run 
   $mmcmd "getframe -$mfc"

   sleep 1
#Turn off power
$mmcmd "Power_Control 0"

