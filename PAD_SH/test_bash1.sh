#!/bin/bash
# File: test_bash1.sh
#   call with init parameter to initialize hardware 
#   to a known state. Probably calls a script file called "init".
# 1/14/20 - YF - Inception

nFrames=100
# List out instructions here for starting mmclient in 'pipe' mode.
#mmclient -s & 

# open connection
mmcmd "open 1"

#Set number of frames
mmcmd "frames $nFrames"

for n in range(10)
do
   integration = $(( 1000 + n * 100 ))
   
   #set integration time in microseconds ( note: actual time is ~70% shorter)
   mmcmd "integration_usec $integration"


   #
   #  Foreground image
   #
   mmcmd "Shutter_Enabled 1"
   # ^^ will change to 'shutter_open'
   
   sleep .5

   # assumes a hardware trigger
   #  debug -- software -- 
   mmcmd "startrun -nt 1 Fore_$integration"   
   # assumes above is a BLOCKING CALL
   
   mmcmd "Shutter_Enabled 0"  
   # ^^ will change to shutter_close
   mmcmd "stop"  # unarm the system
   
   # Retrieve run 
   mmcmd "getframe -$nFrames"
 

   #
   #  Background image
   #
  
   # assumes a hardware trigger
   mmcmd "startrun -nt 1 Back_$integration"  
   # assumes above is a BLOCKING CALL

   mmcmd "stop"  # unarm the system
   
   # Retrieve run
   mmcmd "getframe -$nFrames"


done


# close connection
mmcmd "close"

