import MaskExtract
import os
import numpy as np
import matplotlib.pyplot as plt
import Big_keck_load as BKL

# Initialize the filenames
bgFilename = 'back_avg.raw';
fgFilename = 'keck_single_pixel/run-scan_issbufPIX_f_800/frames/scan_issbufPIX_f_800_00000001.raw';
maskFilename = 'single_pix.csv';

# Initialize the extractor
pixelExtractor = MaskExtract.MaskExtractor();
pixelExtractor.load_mask(maskFilename);

# Load background image
bgImage = np.fromfile(bgFilename, dtype=np.double).reshape((-1,512,512));

# Iterate over all foreground images
fgImageFile = open(fgFilename, "rb");
numFgImages = int(os.path.getsize(fgFilename)/(1024+512*512*2));

for fIdx in range(numFgImages):
    payload = BKL.keckFrame(fgImageFile);
    curr_frame = payload[4].reshape([512,512]);
    fmbImg = curr_frame - bgImage[(payload[3]-1)%8,:,:];
    pixelExtractor.extract_frame(fmbImg); # There is an option here to use different caps, but by default we will not use separate caps

# Now get all the valid pixels
valid_pixels = np.array(pixelExtractor.valid_values);

# Sort to clip off some values
clip_thresh = 0.005;
valid_pixels.sort();
num_valid = len(valid_pixels);
clipped_pixels = valid_pixels[int(num_valid*clip_thresh):int((num_valid*(1-clip_thresh))+1)];


# Close the file
fgImageFile.close();

fig,axs = plt.subplots(1,1)
axs.hist(clipped_pixels, bins=256);
plt.show()
