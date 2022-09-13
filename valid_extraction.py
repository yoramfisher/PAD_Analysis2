import MaskExtract
import os
import numpy as np
import matplotlib.pyplot as plt
import Big_keck_load as BKL
import CreateSim

def clip_hist(hist_data, clip_thresh):
    hist_data.sort();
    num_valid = len(hist_data);
    clipped_pixels = hist_data[int(num_valid*clip_thresh):int((num_valid*(1-clip_thresh))+1)];
    return clipped_pixels;



# Initialize the filenames
#bgFilename = '/mnt/raid/keckpad/set-phHist/run-4ms_back/frames/4ms_back_00000001' +'.raw'
bgFilename = '/mnt/raid/keckpad/set-phHist/run-3ms_backs/frames/3ms_backs_00000001' +'.raw';
#fgFilename = '/mnt/raid/keckpad/set-issbufPIX_40KV/run-scan_issbufPIX_f_1200/frames/scan_issbufPIX_f_1200_00000001.raw';
maskFilename = 'single_pix.csv';

pFolder = "vref_50kv"
dFolder = "vref"
backImageData = open(bgFilename,"rb")

backStack = np.zeros((8,512,512),dtype=np.double)
numImages = int(os.path.getsize(bgFilename)/(1024+512*512*2))

#Calc cap backs
for fIdex in range(numImages):
   payload = BKL.keckFrame(backImageData)
   backStack[(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512])
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
    #fgFilename = '/mnt/raid/keckpad/set-phHist/run-30kv_3ms_pinholes2/frames/30kv_3ms_pinholes2_' + '{:08d}'.format(images) + '.raw'
    fgFilename = '/mnt/raid/keckpad/set-phHist/run-30kv_3ms_pinholes/frames/30kv_3ms_pinholes_' + '{:08d}'.format(images) + '.raw'
# Iterate over all foreground images
    fgImageFile = open(fgFilename, "rb");
    numFgImages = int(os.path.getsize(fgFilename)/(1024+512*512*2));


    for fIdx in range(numFgImages):
        payload = BKL.keckFrame(fgImageFile);
        curr_frame = payload[4].reshape([512,512]);
        fmbImg = curr_frame - backStack[(payload[3]-1)%8,:,:];
        #fmbImg = fmbImg[128:(128+128+1),256:(256+128+1)] #uncomment for looking at individual pixels
        #-=-= XXX Comment this out for production
        #fmbImg = CreateSim.CreateSim();

        pixelExtractor.extract_frame(fmbImg, (payload[3]-1)%8); # FIXME Assumes that all caps are being used in the foreground image
        
    # Close the file
    fgImageFile.close();

# Now get some valid pixels
valid_pixels0 = np.array(pixelExtractor.valid_values[0])
valid_pixels1 = np.array(pixelExtractor.valid_values[1])
valid_pixels2 = np.array(pixelExtractor.valid_values[2])
valid_pixels3 = np.array(pixelExtractor.valid_values[3])
valid_pixels4 = np.array(pixelExtractor.valid_values[4])
valid_pixels5 = np.array(pixelExtractor.valid_values[5])
valid_pixels6 = np.array(pixelExtractor.valid_values[6])
valid_pixels7 = np.array(pixelExtractor.valid_values[7])
# allpixels = []
# for val in range(8):
#     print('{} {}'.format(val, len(pixelExtractor.valid_values[val])))
#     print(pixelExtractor.valid_values[val][0:10])
#     allpixels.extend(pixelExtractor.valid_values[val])

# valid_pixelsall= np.array(allpixels).reshape([1,-1])
clipPos = 250
clipNeg = -50
# Clip the arrays
clipped0 = clip_hist(valid_pixels0, 0.00);
clipped1 = clip_hist(valid_pixels1, 0.00);
clipped2 = clip_hist(valid_pixels2, 0.00);
clipped3 = clip_hist(valid_pixels3, 0.00);
clipped4 = clip_hist(valid_pixels4, 0.00);
clipped5 = clip_hist(valid_pixels5, 0.00);
clipped6 = clip_hist(valid_pixels6, 0.00);
clipped7 = clip_hist(valid_pixels7, 0.00);
# clipped0 = clipped0[clipped0>clipNeg]
# clipped0 = clipped0[clipped0<clipPos]
# clipped1 = clipped1[clipped1<clipPos]
# clipped1 = clipped1[clipped1>clipNeg]
# clipped2 = clipped2[clipped2>clipNeg]
# clipped2 = clipped2[clipped2<clipPos]
# clipped3 = clipped3[clipped3>clipNeg]
# clipped3 = clipped3[clipped3<clipPos]
# clipped4 = clipped4[clipped4>clipNeg]
# clipped5 = clipped5[clipped5>clipNeg]
# clipped6 = clipped6[clipped6>clipNeg]
# clipped7 = clipped7[clipped7>clipNeg]
# clipped4 = clipped4[clipped4<clipPos]
# clipped5 = clipped5[clipped5<clipPos]
# clipped6 = clipped6[clipped6<clipPos]
# clipped7 = clipped7[clipped7<clipPos]


fig,axs = plt.subplots(8,1)


# axs[0].set_yscale('log')
# axs[1].set_yscale('log')
# axs[2].set_yscale('log')
# axs[3].set_yscale('log')
# axs[4].set_yscale('log')
# axs[5].set_yscale('log')
# axs[6].set_yscale('log')
# axs[7].set_yscale('log')

binRan = np.arange(-50,351)

axs[0].hist(clipped0, bins=binRan);
axs[1].hist(clipped1, bins=binRan);
axs[2].hist(clipped2, bins=binRan);
axs[3].hist(clipped3, bins=binRan);
axs[4].hist(clipped4, bins=binRan);
axs[5].hist(clipped5, bins=binRan);
axs[6].hist(clipped6, bins=binRan);
axs[7].hist(clipped7, bins=binRan);


#nphist, bins = np.histogram(clipped7, bins=400, range=(-6,71))
#axs[7].plot(bins[:-1], nphist);
# axs[2].hist(valid_pixelsall, bins=400);

#fig,axs = plt.subplots(1,1)
#axs.hist(clipped3, bins=binRan);

plt.show()