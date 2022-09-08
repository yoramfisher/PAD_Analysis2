import MaskExtract
import os
import numpy as np
import matplotlib.pyplot as plt
import Big_keck_load as BKL

def clip_hist(hist_data, clip_thresh):
    hist_data.sort();
    num_valid = len(hist_data);
    clipped_pixels = hist_data[int(num_valid*clip_thresh):int((num_valid*(1-clip_thresh))+1)];
    return clipped_pixels;



# Initialize the filenames
bgFilename = '/mnt/ra`id/keckpad/set-issbufPIX_40KV/'
fgFilename = '/mnt/raid/keckpad/set-issbufPIX_40KV/run-scan_issbufPIX_f_1200/frames/scan_issbufPIX_f_1200_00000001.raw';
maskFilename = 'single_pix.csv';

pFolder = "vref_50kv"
dFolder = "vref"
backImageData = open(bgFilename,"rb")

backStack = np.zeros((8,512,512),dtype=np.double)
numImages = int(os.path.getsize(bgFilename/(1024+512*512*2)))

#Calc cap backs
for fIdex in range(numImages):
   payload = BKL.keckFrame(backImageData)
   backStack[(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512])
backStack = backStack/ (numImages/8)


# Initialize the extractor
pixelExtractor = MaskExtract.MaskExtractor();
pixelExtractor.load_mask(maskFilename);

# Load background image # Need to re-load and average instead.
#bgImage = np.fromfile(bgFilename, dtype=np.double).reshape((-1,512,512));

# Iterate over all foreground images
fgImageFile = open(fgFilename, "rb");
numFgImages = int(os.path.getsize(fgFilename)/(1024+512*512*2));


for fIdx in range(numFgImages):
    payload = BKL.keckFrame(fgImageFile);
    curr_frame = payload[4].reshape([512,512]);
    fmbImg = curr_frame - backStack[(payload[3]-1)%8,:,:];
    pixelExtractor.extract_frame(fmbImg, (payload[3]-1)%8); # FIXME Assumes that all caps are being used in the foreground image
    
# Close the file
fgImageFile.close();

# Now get some valid pixels
valid_pixels0 = np.array(pixelExtractor.valid_values[0]);
valid_pixels1 = np.array(pixelExtractor.valid_values[4]);

# Clip the arrays
clipped0 = clip_hist(valid_pixels0, 0.005);
clipped1 = clip_hist(valid_pixels1, 0.005);


fig,axs = plt.subplots(2,1)
axs[0].hist(clipped0, bins=256);
axs[1].hist(clipped1, bins=256);

plt.show()