#!/bin/bash
# File: test_bash1.sh
#   call with init parameter to initialize hardware 
#   to a known state. Probably calls a script file called "init".
# 1/14/20 - YF - Inception

mmcmd="/home/sydor/projects/mm-pad-client-cmdline/bin/debug/mmcmd"

$mmcmd open

$mmcmd stop

sleep 1

nFrames=100
# List out instructions here for starting mmclient in 'pipe' mode.
####mmpad_client –init 

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
