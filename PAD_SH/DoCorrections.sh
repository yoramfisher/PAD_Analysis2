#!/bin/bash
# File: DoCorrections.sh
# 6/17/22 - YF - Inception
#
# Usage
#   DoCorrections <setname> <runName> <backrunName>
#   DoCorrections <setname> all    -- Enter astericks to correct all runs in the set.
#  

set -x # show commands as they run

# **** Configuration ****
setname=$1
backrunname=$2
runname=""
allmode=0
# ***********************


showUsage() { 
   set +x # turn off debug
   echo "Usage:"
   echo "$0 <setname> <backRunName> <runname> -- "
   echo "   convert the given set / run. Uses background specified."
   echo "$0 <setname> <backRunName> all --"
   echo "   convert all runs in the set."
   
}


if [ -z "$setname" ] || [ -z "$backrunname" ]
then
      showUsage
      exit 0
fi


if [ "$3" = "all" ]
then
   allmode=1
   echo "all mode"
else
   runname="$3" 
fi   




# Path to binary
#mmcmd="/home/sydor/projects/mm-pad-client-cmdline/bin/debug/mmcmd"
mmcmd="mmcmd"

# run mmclient in script mode if not already running
./LaunchIfNeeded.sh


res=$($mmcmd "open 1")

#echo "res = $res"
# TODO - how check failure

$mmcmd "bg_subtract_enable 1"

$mmcmd "debounce_correction_enable 0"   # KECK no debounce
$mmcmd "geometric_correction_enable 1"  # GEO YES
$mmcmd "flatfield_correction_enable 0"  # FF NO
$mmcmd "bad_pixel_map_enable 0" # this should be 1 probably

# Enable corrections
$mmcmd "correction_global_enable 1"

# no no no$mmcmd "calcbg $setname $runname"
# no no no $mmcmd "calcflatfield $default foo_flatfield

$mmcmd "calcbg $setname $backrunname"
# Sleep is required
sleep 2

if [ "$allmode" = 1 ]
then
   
   echo "All mode"
   echo "The Following runs will be converted:"
   
   SET_PATH="/mnt/raid/keckpad/set-$setname/*"
   for f in $SET_PATH
   do 
      fil="$(basename $f)"
      # Remove the "run-"  prefix
      fil=${fil:4}
      echo "Processing $fil"
      $mmcmd "batchcorrect $setname $fil"
   done
   exit 0
   
fi

$mmcmd "batchcorrect $setname $runname"
