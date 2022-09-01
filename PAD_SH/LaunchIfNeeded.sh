#!/bin/bash
# File: LaunchIfNeeded.sh
#  Will start mmclient in  scripting mode if not already running
# 1/14/20 - YF - Inception

# Path to binary
mmcmd="/usr/local/bin/mmcmd"
mmclient="/usr/local/bin/mmclient"
found=0

p=$(ps -ef |  awk '/mmclient/ {print}' | awk '/-s/ {print $2}')
echo $p



# special care taken not to launch a subprocess - or cant set variables inside
# the while loop!
while IFS= read -r line  
do 
   #echo "line:$line"; 
   isNumber=$(echo "$line" | grep -E ^[0-9]+$)
   #echo "isNumber: $isNumber"

   # if not empty we have a match!
   if [ ! -z "$isNumber" ]
   then
      found=1
      break
   fi
done < <(printf '%s\n' $p)


if [[ "$found" == 1 ]]
then
   exit 0
else
   # otherwise launch  it now
   echo "Launching mmclient in script mode"
   $mmclient -s -t &
fi







