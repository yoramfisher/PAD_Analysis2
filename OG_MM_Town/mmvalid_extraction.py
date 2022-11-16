#Modded by BWM for OG MM Pad 
#10/07/22


import mmMaskExtract
import os
import numpy as np
import matplotlib.pyplot as plt
import Big_MM_load as BKL
import math
from scipy.optimize import curve_fit
import glob

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
NUM_CAPS = 1

# Initialize the filenames
#bgFilename = '/mnt/raid/keckpad/set-phHist/run-4ms_back/frames/4ms_back_00000001' +'.raw'
bgFilename = '/mnt/raid/set-pinhole/run-ph_0C_30KV_5ms_b2/mm-pad-512x512-2022-10-07-16-18-16-0002' +'.raw';
#fgFilename = '/mnt/raid/keckpad/set-issbufPIX_40KV/run-scan_issbufPIX_f_1200/frames/scan_issbufPIX_f_1200_00000001.raw';
maskFilename = 'single_pix.csv';

pFolder = "vref_50kv"
dFolder = "vref"
backImageData = open(bgFilename,"rb")

backStack = np.zeros((512,512),dtype=np.double)
numImages = int(os.path.getsize(bgFilename)/(2048+512*512*4))

#Calc cap backs
for fIdex in range(numImages):
   payload = BKL.keckFrame(backImageData)
   backStack[:,:] += np.resize(payload,[512,512])
backStack = backStack/ (numImages)


# Initialize the extractor
pixelExtractor = mmMaskExtract.MaskExtractor();
pixelExtractor.load_mask(maskFilename);
#uncomment below for single pixel analysis 
#pixelExtractor.singlePixelMat = pixelExtractor.singlePixelMat[:,128:(128+128+1),256:(256+128+1)] # [caps, y1:y2, x1:x2]
pixelExtractor.singlePixelMat = pixelExtractor.singlePixelMat[:,:] # [caps, y1:y2, x1:x2]
# Load background image # Need to re-load and average instead.
#bgImage = np.fromfile(bgFilename, dtype=np.double).reshape((-1,512,512));

fg_filename_list = glob.glob('/mnt/raid/set-pinhole/run-ph_0C_30KV_5ms_f2/mm*.raw');
numFiles = len(fg_filename_list)

for num in range(numFiles):
    #images = num * 1000 + 1
    #fgFilename = '/mnt/raid/keckpad/set-phHist/run-30kv_3ms_pinholes2/frames/30kv_3ms_pinholes2_' + '{:08d}'.format(images) + '.raw'
    #fgFilename = '/mnt/raid/set-pinhole/run-ph_0C_30KV_2ms_f/30KV_1.5mA_40ms_f_' + '{:08d}'.format(images) + '.raw'
    fgFilename = fg_filename_list[num];
# Iterate over all foreground images
    fgImageFile = open(fgFilename, "rb");
    numFgImages = int(os.path.getsize(fgFilename)/(2048+512*512*4));


    for fIdx in range(numFgImages):
        payload = BKL.mmFrame(fgImageFile);
        curr_frame = payload.reshape([512,512]);
        fmbImg = curr_frame - backStack
        #fmbImg = fmbImg[128:(128+128+1),256:(256+128+1)] #uncomment for looking at individual pixels
        #-=-= XXX Comment this out for production
        #fmbImg = CreateSim.CreateSim();

        pixelExtractor.extract_frame(fmbImg); # FIXME Assumes that all caps are being used in the foreground image
        
    # Close the file
    fgImageFile.close();

# Now get some valid pixels
valid_pixels = [];
valid_pixels.append(np.array(pixelExtractor.valid_values).astype(np.double))

# valid_pixelsall= np.array(allpixels).reshape([1,-1])
clipPos = 500
clipNeg = -50
clip_thresh = 0.000;

# Clip the arrays
clipped_pixels = [];
clipped_pixels.append(clip_hist(valid_pixels[0], clip_thresh));

# Now histogram the arrays
hist_pixels = [];
binRan = np.arange(-50,351);    # The bins for the histogram
binRan = np.arange(-50,500);

hist_pixels.append((np.histogram(clipped_pixels[0], bins=binRan))[0]);

# Now do the curve fitting
# fit_pixels = [];
# for cap_idx in range(1):
# #     # Two Gauss
#     guess_val = [ 1, 0, 10, 0.9, 30, 10, 0];
#     guess_val[0] = np.max(hist_pixels);
#     guess_val[3] = guess_val[0]*0.9;
    
    # Three Gauss
    # guess_val = [1, 0, 10, 0.9, 30, 10, 0.5, 60, 10, 0]
    # guess_val[0] = np.max(hist_pixels)
    # guess_val[3] = guess_val[0]*0.9
    # guess_val[6] = guess_val[0]*0.2;

    # Four Gauss
    # guess_val = [1, 0, 10, 0.9, 30, 10, 0.5, 60, 10, 0.2, 90, 10, 0]
    # guess_val[0] = np.max(hist_pixels)
    # guess_val[3] = guess_val[0]*0.9
    # guess_val[6] = guess_val[0]*0.2
    # guess_val[9] = guess_val[0]*0.1;
    
    # Two Gauss
    # fit_vals = curve_fit(twoGauss, binRan[:-1], hist_pixels[cap_idx], guess_val, method='dogbox');
    # fit_pixels.append(twoGauss(binRan[:-1], *fit_vals[0]));

    # Three Gauss
    # fit_vals = curve_fit(threeGauss, binRan[:-1], hist_pixels[cap_idx], guess_val, method='dogbox');
    # fit_pixels.append(threeGauss(binRan[:-1], *fit_vals[0]));

    # Four Gauss
    # fit_vals = curve_fit(fourGauss, binRan[:-1], hist_pixels[cap_idx], guess_val, method='dogbox');
    # fit_pixels.append(fourGauss(binRan[:-1], *fit_vals[0]));

 #   print("Cap {} Fit Centers:".format(cap_idx))                   
    #print(fit_vals[0])
    # Two Gauss
    # print("{}, {}".format(fit_vals[0][1], fit_vals[0][4]))

    # Three Gauss
    # print("{}, {}, {}".format(fit_vals[0][1], fit_vals[0][4], fit_vals[0][7]))

    # Four Gauss
    # print("{}, {}, {}, {}".format(fit_vals[0][1], fit_vals[0][4], fit_vals[0][7], fit_vals[0][10]))

# Do the plotting
fig,axs = plt.subplots(1)
# Special case if only one cap
                # Turn into a list so it can be subscripted

clipped_pixels[0] = clipped_pixels[0]
cl_pixels = clipped_pixels[0].reshape((-1,));
print(cl_pixels.shape)
axs.hist(cl_pixels, bins=binRan);
    #axs[cap_idx].plot(binRan[:-1], fit_pixels[cap_idx], 'r--');


plt.show()
plt.savefig('clipped_plot.jpg');