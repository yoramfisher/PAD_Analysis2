#!/bin/bash
# File: test_bash3.sh
# 1/14/20 - YF - Inception

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

nFrames=100

#Set number of frames
$mmcmd "frame $nFrames"

for n in {0..9}
do
   integration=$(( 1000 + n * 100 ))
   
   #set integration time in microseconds ( note: actual time is ~70% shorter)
   $mmcmd "integration_usec $integration"


   #
   #  Foreground image
   #
   $mmcmd "Shutter_Enabled 1"
   # ^^ will change to 'shutter_open'
   
   # assumes a hardware trigger
   $mmcmd "startrun -nt 1 Fore_$integration"
   # assumes above is a BLOCKING CALL
   
   sleep 5
   $mmcmd "Shutter_Enabled 0"  
   # ^^ will change to shutter_close
   $mmcmd "stop"  # unarm the system

   sleep 1
   
   # Retrieve run 
   $mmcmd "getframe -$nFrames"
 

   #
   #  Background image
   #
  
   # assumes a hardware trigger
   $mmcmd "startrun -nt 1 Back_$integration"  
   # assumes above is a BLOCKING CALL

   sleep 5
   $mmcmd "stop"  # unarm the system
   sleep 1

   # Retrieve run
   $mmcmd "getframe -$nFrames"


done
