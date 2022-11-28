import MaskExtract
import os
import numpy as np
import matplotlib.pyplot as plt
import Big_keck_load as BKL
import CreateSim
import math
from scipy.optimize import curve_fit

fit_invoke = 0;
def twoGauss(xdata, a, b, c, d, e, f, g):
    global fit_invoke;
    fit_invoke += 1;
    #print(fit_invoke, a, b, c, d, e, f, g);
    result_y = np.arange(xdata.size).astype(np.double);
    for x_idx in range(xdata.size):
        x = xdata[x_idx];
        result_y[x_idx] = a * math.exp(-0.5*((x-b)/c)**2) + d * math.exp(-0.5*((x-e)/f)**2) + g;
    #print(xdata, result_y)
    return result_y;

def threeGauss(xdata, a, b, c, d, e, f, g, j, k, l):
    global fit_invoke;
    fit_invoke += 1;
    #print(fit_invoke, a, b, c, d, e, f, g, j, k, l);
    result_y = np.arange(xdata.size).astype(np.double);
    for x_idx in range(xdata.size):
        x = xdata[x_idx];
        result_y[x_idx] = a * math.exp(-0.5*((x-b)/c)**2) + \
        d * math.exp(-0.5*((x-e)/f)**2) + \
            g * math.exp(-0.5*((x-j)/k)**2) + l;
    #print(xdata, result_y)
    return result_y;

def fourGauss(xdata, a, b, c, d, e, f, g, j, k, l, m, n, o):
    global fit_invoke;
    fit_invoke += 1;
    #print(fit_invoke, a, b, c, d, e, f, g, j, k, l);
    result_y = np.arange(xdata.size).astype(np.double);
    for x_idx in range(xdata.size):
        x = xdata[x_idx];
        result_y[x_idx] = a * math.exp(-0.5*((x-b)/c)**2) + \
        d * math.exp(-0.5*((x-e)/f)**2) + \
            g * math.exp(-0.5*((x-j)/k)**2) + \
                l * math.exp(-0.5*((x-m)/n)**2) + o;
    #print(xdata, result_y)
    return result_y;

def clip_hist(hist_data, clip_thresh):
    hist_data.sort();
    num_valid = len(hist_data);
    clipped_pixels = hist_data[int(num_valid*clip_thresh):int((num_valid*(1-clip_thresh))+1)];
    return clipped_pixels;


# Specify the number of caps
NUM_CAPS = 8

# Initialize the filenames
#bgFilename = '/mnt/raid/keckpad/set-phHist/run-4ms_back/frames/4ms_back_00000001' +'.raw'
bgFilename = '/mnt/raid/keckpad/set-HeadRework/run-ph_back_500us/frames/ph_back_500us_00000001' +'.raw';
#fgFilename = '/mnt/raid/keckpad/set-issbufPIX_40KV/run-scan_issbufPIX_f_1200/frames/scan_issbufPIX_f_1200_00000001.raw';
maskFilename = 'single_pix.csv';

pFolder = "vref_50kv"
dFolder = "vref"
backImageData = open(bgFilename,"rb")

backStack = np.zeros((NUM_CAPS,512,512),dtype=np.double)
numImages = int(os.path.getsize(bgFilename)/(1024+512*512*2))

#Calc cap backs
for fIdex in range(numImages):
   payload = BKL.keckFrame(backImageData)
   backStack[(payload[3]-1)%NUM_CAPS,:,:] += np.resize(payload[4],[512,512])
backStack = backStack/ (numImages/8)


# Initialize the extractor
pixelExtractor = MaskExtract.MaskExtractor();
pixelExtractor.load_mask(maskFilename);
#uncomment below for single pixel analysis 
#pixelExtractor.singlePixelMat = pixelExtractor.singlePixelMat[:,128:(128+128+1),256:(256+128+1)] # [caps, y1:y2, x1:x2]
pixelExtractor.singlePixelMat = pixelExtractor.singlePixelMat[:,:,:] # [caps, y1:y2, x1:x2]
# Load background image # Need to re-load and average instead.
#bgImage = np.fromfile(bgFilename, dtype=np.double).reshape((-1,512,512));

numFiles = 8

for num in range(numFiles):
    images = num * 1000 + 1
    fgFilename = '/mnt/raid/keckpad/set-HeadRework/run-ph_45KV_fore500us/frames/ph_45KV_fore500us_' + '{:08d}'.format(images) + '.raw'
    #fgFilename = '/mnt/raid/keckpad/set-HeadRework/run-ph_40KV_fore3ms/frames/ph_40KV_fore3ms_00000001.raw'
# Iterate over all foreground images
    fgImageFile = open(fgFilename, "rb");
    numFgImages = int(os.path.getsize(fgFilename)/(1024+512*512*2));


    for fIdx in range(numFgImages):
        payload = BKL.keckFrame(fgImageFile);
        curr_frame = payload[4].reshape([512,512]);
        fmbImg = curr_frame - backStack[(payload[3]-1)%NUM_CAPS,:,:];
        #fmbImg = fmbImg[128:(128+128+1),256:(256+128+1)] #uncomment for looking at individual pixels
        #-=-= XXX Comment this out for production
        #fmbImg = CreateSim.CreateSim();

        pixelExtractor.extract_frame(fmbImg, (payload[3]-1)%NUM_CAPS); # FIXME Assumes that all caps are being used in the foreground image
        
    # Close the file
    fgImageFile.close();

# Now get some valid pixels
valid_pixels = [];
for cap_idx in range(NUM_CAPS):
    valid_pixels.append(np.array(pixelExtractor.valid_values[cap_idx]).astype(np.double))

# valid_pixelsall= np.array(allpixels).reshape([1,-1])
clipPos = 250
clipNeg = -20
clip_thresh = 0.000;

# Clip the arrays
clipped_pixels = [];
for cap_idx in range(NUM_CAPS):
    clipped_pixels.append(clip_hist(valid_pixels[cap_idx], clip_thresh));

# Now histogram the arrays
hist_pixels = [];
# binRan = np.arange(-50,351);    # The bins for the histogram
binRan = np.arange(-20,80);


for cap_idx in range(NUM_CAPS):
    hist_pixels.append((np.histogram(clipped_pixels[cap_idx], bins=binRan))[0]);

# # Now do the curve fitting
# fit_pixels = [];
# for cap_idx in range(NUM_CAPS):
# #   # Two Gauss
#     guess_val = [ 1, 0, 10, 0.9, 30, 10, 0];
#     guess_val[0] = np.max(hist_pixels);
#     guess_val[3] = guess_val[0]*0.9;
    
#     # Three Gauss
#     # guess_val = [1, 0, 10, 0.9, 30, 10, 0.5, 60, 10, 0]
#     # guess_val[0] = np.max(hist_pixels)
#     # guess_val[3] = guess_val[0]*0.9
#     # guess_val[6] = guess_val[0]*0.2;

#     # Four Gauss
#     # guess_val = [1, 0, 10, 0.9, 30, 10, 0.5, 60, 10, 0.2, 90, 10, 0]
#     # guess_val[0] = np.max(hist_pixels)
#     # guess_val[3] = guess_val[0]*0.9
#     # guess_val[6] = guess_val[0]*0.2
#     # guess_val[9] = guess_val[0]*0.1;
    
#     # Two Gauss
#     fit_vals = curve_fit(twoGauss, binRan[:-1], hist_pixels[cap_idx], guess_val, method='dogbox');
#     fit_pixels.append(twoGauss(binRan[:-1], *fit_vals[0]));

#     # Three Gauss
#     # fit_vals = curve_fit(threeGauss, binRan[:-1], hist_pixels[cap_idx], guess_val, method='dogbox');
#     # fit_pixels.append(threeGauss(binRan[:-1], *fit_vals[0]));

#     # Four Gauss
#     # fit_vals = curve_fit(fourGauss, binRan[:-1], hist_pixels[cap_idx], guess_val, method='dogbox');
#     # fit_pixels.append(fourGauss(binRan[:-1], *fit_vals[0]));

#  #   print("Cap {} Fit Centers:".format(cap_idx))                   
#     #print(fit_vals[0])
#     # Two Gauss
#     print("{}, {}".format(fit_vals[0][1], fit_vals[0][4]))

#     # Three Gauss
#     # print("{}, {}, {}".format(fit_vals[0][1], fit_vals[0][4], fit_vals[0][7]))

#     # Four Gauss
#     # print("{}, {}, {}, {}".format(fit_vals[0][1], fit_vals[0][4], fit_vals[0][7], fit_vals[0][10]))

# Do the plotting
fig,axs = plt.subplots(NUM_CAPS,1)
# Special case if only one cap
if NUM_CAPS == 1:
    axs = [axs]                 # Turn into a list so it can be subscripted

for cap_idx in range(NUM_CAPS):
    axs[cap_idx].hist(clipped_pixels[cap_idx], bins=binRan);
    #axs[cap_idx].plot(binRan[:-1], fit_pixels[cap_idx], 'r--');


plt.show()
