import numpy as np
import Big_keck_load as BKL
import os
import pickle
import CreateSim

class EventPixel:
    def __init__(self):
        self.x = -1;
        self.y = -1;
        self.cap = -1;
        self.value = -1;        # Initialize to invalid values
Low = 26
Hi = 50
# Set thresholds
low_thresh = [Low, Low, Low, Low, Low, Low, Low, Low]; # Threshold for neighbors being low
high_thresh = [Hi, Hi, Hi, Hi, Hi, Hi, Hi, Hi]; # Threshold for pixel under test being high

# Allocate arrays
backStack = np.zeros((8,512,512), dtype=np.double);
foreStack = np.zeros((8,512,512), dtype=np.double);

# Load background
backImageFilename = '/mnt/raid/keckpad/set-phHist_dcsKeck/run-30KV_1mA_40ms_b/frames/30KV_1mA_40ms_b_00000001' +'.raw';
numBackImages = int(os.path.getsize(backImageFilename)/(1024+512*512*2));
backImageFile = open(backImageFilename, "rb");

for fIdx in range(numBackImages): 
    payload = BKL.keckFrame(backImageFile);
    backStack[(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512]);
backStack = backStack/(numBackImages/8); # Average the background
backImageFile.close();

# Load the foreground images
foreImageFilename = '/mnt/raid/keckpad/set-phHist_dcsKeck/run-30KV_1mA_40ms_f/frames/30KV_1mA_40ms_f_00000001.raw';
numForeImages = int(os.path.getsize(foreImageFilename)/(1024+512*512*2));
foreImageFile = open(foreImageFilename, "rb");

for fIdx in range(numForeImages):
    payload = BKL.keckFrame(foreImageFile);
    foreStack[(payload[3]-1)%8,:,:] += np.resize(payload[4],[512,512]);
foreStack = foreStack/(numForeImages/8); # Average the background
foreImageFile.close();

# Compute the background subtracted image
fmbImage = foreStack - backStack;

# Save the computed images
# Uncomment below if wish to save images
foreStack.tofile('fore_avg.raw');
backStack.tofile('back_avg.raw');
fmbImage.tofile('fmb.raw');

if False:
    simData = CreateSim.CreateSim()
    for x in range(8):
        fmbImage[x,:,:] = simData;

singlePixelList = [];
noPixelList = [];
total_pixels = 0;
cold_neighborhoods = 0;
    
#Now iterate over the inner pixels to find single events
for cap_idx in range(8):
    curr_frame = fmbImage[cap_idx,:,:]; # Get just the current frame
    for row_idx in range(2,510):    # Ignore outer two pixels
        for col_idx in range(2,510): # Ibid
            total_pixels += 1;       # Increment pixel count
            test_mat = curr_frame[(row_idx-1):(row_idx+1+1),(col_idx-1):(col_idx+1+1)]; # Extract the 3x3 neighborhood
            # Compute the low threshold
            cold_test = (test_mat<low_thresh[cap_idx]).astype(int); # See if neighborhood below limi
            cold_test[1,1] = 0;              # Set inner to zero for sum
            cold_sum = np.sum(cold_test);
            #if (cold_sum > 0):
            #    print(cold_test);
            cold_neighbor = False;
            if cold_sum == 8:   # All pixels below threshold
                cold_neighbor = True;
                cold_neighborhoods += 1;
                test_pixel = EventPixel();
                test_pixel.x = col_idx;
                test_pixel.y = row_idx;
                test_pixel.cap = cap_idx;
                test_pixel.value = test_mat[1,1]; # Set the pixel parameters
                
                # Determine list to append to
                if test_pixel.value >= high_thresh[cap_idx]: # Pixel hot
                    singlePixelList.append(test_pixel);
                # uncomment below if you want to save no pixel list    
                # else:           # Pixel cold
                #     noPixelList.append(test_pixel);

print("Tested {} pixels.".format(total_pixels));
print("Cold neighborhoods: {}".format(cold_neighborhoods));
print("{} single pixels and {} no pixels.".format(len(singlePixelList),len(noPixelList)));
single_pixel_filename = 'single_pix.csv';
single_pixel_file = open(single_pixel_filename, 'w');
for curr_pixel in singlePixelList:
    single_pixel_file.write('{},{},{},{}\n'.format(curr_pixel.y, curr_pixel.x, curr_pixel.cap, curr_pixel.value));
    #if (curr_pixel.y < 128) and (curr_pixel.x < 128) and (curr_pixel.cap == 3):
        #single_pixel_file.write('{},{},{},{}\n'.format(curr_pixel.y, curr_pixel.x, curr_pixel.cap, curr_pixel.value));
single_pixel_file.close();

#uncomment below if you want to save no pixel list to file
# no_pixel_filename = 'no_pix.csv';
# no_pixel_file = open(no_pixel_filename, 'w');
# for curr_pixel in noPixelList:
#     no_pixel_file.write('{},{},{},{}\n'.format(curr_pixel.y, curr_pixel.x, curr_pixel.cap, curr_pixel.value));
# no_pixel_file.close();

# Pickle the results
pickleFile = open('pixels.pickle', 'wb')
pickle.dump(singlePixelList, pickleFile);
pickle.dump(noPixelList, pickleFile);
pickleFile.close();
