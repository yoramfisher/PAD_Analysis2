import numpy as np
import Big_keck_load as BKL
import os
import matplotlib.pyplot as plt

# Initialize filenames
maskFilename = 'single_pix.csv';
imageFilename = 'fmb.raw'

# Create arrays
singlePixelMat = np.zeros((8,512,512)).astype(bool); # Initialize to false

# Load the pixel mask
maskFile = open(maskFilename, 'r');
for curr_line in maskFile:
    line_split = curr_line.split(',');
    bcCaps = False;              # Whether to get all caps
    if bcCaps:
        singlePixelMat[:, int(line_split[0]), int(line_split[1])] = True; # Note as a valid pixel for all caps, as the mask won't move between caps
    else:
        singlePixelMat[int(line_split[2]), int(line_split[0]), int(line_split[1])] = True; # Note as a valid pixel for all caps, as the mask won't move between caps
maskFile.close();

# Create the destination list
valid_pixel_values = [];

# Iterate over all frames in the file
numImages = int(os.path.getsize(imageFilename)/(1024+512*512*2));
imageFile = open(imageFilename, "rb");

fromKeck = False;               # Boolean if we are loading a Keck image
numImages = 8;
for fIdx in range(numImages):
    print("Processing frame {} of {}.".format(fIdx+1, numImages));
    curr_frame = np.array([512,512]);
    if fromKeck:                # Keck image
        payload = BKL.keckFrame(imageFile);
        curr_frame = np.resize(payload[4],[512,512]); # Load the current frame
        curr_cap = int((payload[3]-1)%8);                  # Compute the cap
    else:                                                  # Assume raw image
        payload = np.fromfile(imageFile, dtype=np.double, count=512*512)
        payload = payload.reshape((512,512));
        curr_frame = payload;
        #print(curr_frame)
        curr_cap = int(fIdx%8); # FIXME Assumes all caps in 
    
    valid_pixels = curr_frame[singlePixelMat[curr_cap,:,:]]; # Get pixels where singlePixelMat is True
    valid_pixel_values.extend(valid_pixels.reshape((1,-1)).tolist()[0]);

valid_val_array = np.array(valid_pixel_values)

fig,axs = plt.subplots(1,1);
axs.hist(valid_val_array,bins=256);
plt.show()
