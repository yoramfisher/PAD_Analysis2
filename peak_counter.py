# Counts the peaks in each submodule of a peak-detected image

import numpy as np
import Big_keck_load as BKL
import scipy
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
from scipy.optimize import minimize
import imageio
import os
import matplotlib
import matplotlib.pyplot as plt
import sys
import tkinter.filedialog as fd
import findpeaks.findpeaks as fp   # https://erdogant.github.io/findpeaks/pages/html/index.html 
import tifffile
import math

ASIC_HEIGHT = 128
ASIC_WIDTH  = 128

PEAKS_EXPECTED = 81

def gen_grid(length, delta, scale, theta, offset=(0,0)):
    length = int(length)
    if length%2 == 0:
        print("Length must be odd.")
        return None

    mid_val = length/2+1;     # Get the value in the middle of the length

    grid_points = [];
    for row_idx in range(length):
        row_val = row_idx-mid_val+1 # Row number centered around mid_val for interval [-length/2, length/2]
        row_dist = row_val*delta*scale # Expand to a distance per row
        for col_idx in range(length):
            col_val = col_idx-mid_val+1 # Column number the same way as rows above
            col_dist = col_val*delta*scale # Distance as above

            rot_col = math.cos(theta)*col_dist - math.sin(theta)*row_dist+offset[1] 
            rot_row = math.sin(theta)*col_dist + math.cos(theta)*row_dist+offset[0] # Rotation matrix plus offset
            grid_points.append((rot_row, rot_col))

    return grid_points
                               
class Peak_Image:
    def __init__(self):
        self.ASIC_HEIGHT = 128
        self.ASIC_WIDTH = 128
        self.PEAKS_EXPECTED = 81
        self.LENGTH = 9
        self.NUM_COLS = 4
        self.NUM_ROWS = 4
        self.peak_img = None
        self.neighbor_mask = np.array([[1,1,1],[1,1,1],[1,1,1]]);
        self.labeled_img = None
        self.num_objects = 0
        self.CoM = None
        self.DELTA = 11
        self.asic_com = None    # A list of CoM in a specified ASIC
        return
    
    def set_image(self, newImage):
        self.peak_img = newImage + 0; # Try to enforce a deep copy

        return

    def label_peaks(self):
        if self.peak_img is None:
            return None

        labeled_img, num_objects = ndimage.label(self.peak_img, structure=self.neighbor_mask)
        self.labeled_img = labeled_img
        self.num_objects = num_objects

        return True

    def quadrant_peak_count(self):
        if self.peak_img is None:
            return None

        for row_idx in range(self.NUM_ROWS):
            for col_idx in range(self.NUM_COLS):
                start_row = self.ASIC_HEIGHT * row_idx
                start_col = self.ASIC_WIDTH * col_idx
                end_row = start_row + self.ASIC_HEIGHT
                end_col = start_col + self.ASIC_WIDTH
                curr_asic_pix = self.labeled_img[start_row:end_row,start_col:end_col]
                distinct_val = set(curr_asic_pix.flat)
                if not 0 in distinct_val:
                    print("ERROR: No background found in ASIC {},{}".format(row_idx, col_idx));
                    return False
                
                num_peaks = len(distinct_val - set([0]));
                print("ASIC {},{} has {} peaks.".format(row_idx, col_idx, num_peaks))
                if (num_peaks != self.PEAKS_EXPECTED):
                    print("Error: Incorrect number of peaks.  Wanted: {} Actual: {}".format(self.PEAKS_EXPECTED, num_peaks))
                    return False
        return True

    def calc_CoM(self):
        self.CoM = ndimage.center_of_mass(self.peak_img, labels=self.labeled_img, index=list(set(self.labeled_img.flat)-set([0]))) # Get every unique peak and subtract out the CoM for 0, where there is no peak
    
    def point_in_asic(self, test_point, asic_idx):
        start_row = self.ASIC_HEIGHT * asic_idx[0]
        start_col = self.ASIC_WIDTH * asic_idx[1]
        end_row = start_row + self.ASIC_HEIGHT
        end_col = start_col + self.ASIC_WIDTH

        if (test_point[0] >= start_row) and (test_point[0] < end_row):
            if (test_point[1] >= start_col) and (test_point[1] < end_col):
                return True

        return False

    def com_in_asic(self, asic_idx):
        CoM = [];
        
        for curr_peak in self.CoM:
            if self.point_in_asic(curr_peak, asic_idx):
                CoM.append(curr_peak)

        return CoM

    def point_dist_sq(self, point1, point2):
        delta_x = point1[0] - point2[0]
        delta_y = point1[1] - point2[1]
        
        return (delta_x*delta_x + delta_y*delta_y)
    
    def nearest_com(self, point, com_list):

        # Initialize with first point
        curr_point = com_list[0]
        curr_dist_sq = self.point_dist_sq(curr_point, point)
        min_dist_sq = curr_dist_sq
        min_idx = 0
        
        for point_idx in range(len(com_list)):
            curr_point = com_list[point_idx]
            curr_dist_sq = self.point_dist_sq(curr_point, point)
            if (curr_dist_sq < min_dist_sq):
                min_dist_sq = curr_dist_sq
                min_idx = point_idx

        return min_idx, min_dist_sq

    def nearest_com_point(self, point, com_list):
        min_idx, min_distsq = self.nearest_com(point, com_list)
        return com_list[min_idx]
    
    def set_asic(self, row, col):
        asic_com = self.com_in_asic((row, col)) # Create a list of centers of mass
        print("Raw ASIC COM")
        print(len(asic_com))
        print(asic_com)
        # Compute the center point of the grid to place the generated grid
        avg_row = 0
        avg_col = 0
        point_count = 0.0
        for curr_point in asic_com:
            avg_row += curr_point[0]
            avg_col += curr_point[1]
            point_count += 1.0
        avg_row = avg_row / point_count
        avg_col = avg_col / point_count

        print("Nominal center: {}, {}".format(avg_row, avg_col))
        # Find the actual starting position
        center_pos_a = self.nearest_com_point((avg_row, avg_col), asic_com)
        print("Actual center: {}, {}".format(center_pos_a[0], center_pos_a[1]))
        

        # Now walk our way to the left
        half_walk_limit = int(self.LENGTH/2)
        curr_found_point = center_pos_a; # Start from the center
        for col_idx in range(half_walk_limit):
            curr_test_point = (curr_found_point[0], curr_found_point[1]-self.DELTA); # Adjust self.DELTA to the left
            curr_found_point = self.nearest_com_point(curr_test_point, asic_com) # Update the point with the newest

        # Walk upwards
        for row_idx in range(half_walk_limit):
            curr_test_point = (curr_found_point[0]-self.DELTA, curr_found_point[1]); # Walk upwards
            curr_found_point = self.nearest_com_point(curr_test_point, asic_com)

        # We should now have the top-left point found
        print("Grid top-left is: {}".format(curr_found_point))

        # Prepare some bookkeeping variable
        self.asic_com = []      # Empty list
        row_start_point = curr_found_point # We need to refer to the start of the row after doing all columns
        curr_iter_point = curr_found_point # The point we use in iteration
        curr_com_point = curr_found_point  # The point we store the nearest in
    
        for row_idx in range(self.LENGTH):
            for col_idx in range(self.LENGTH):
                curr_com_point = self.nearest_com_point(curr_iter_point, asic_com); # Compute the nearest
                self.asic_com.append(curr_com_point) # Add to the list
                print(curr_com_point)
                curr_iter_point = (curr_com_point[0], curr_com_point[1]+self.DELTA); # Walk right one point
            # To prepare for the next row
            curr_iter_point = (row_start_point[0]+self.DELTA, row_start_point[1]) # Go to the start of the row, then walk down one point
            curr_com_point = self.nearest_com_point(curr_iter_point, asic_com) # Compute nearest
            row_start_point = curr_com_point # Update row value for next row
            curr_iter_point = curr_com_point # Store value for next iteration
                
                                 
        return True

    # Assume that the internal CoM list has been set with set_asic
    # Grid coeff is an array with scale, theta, offset_row, offset_col
    def calc_err(self, grid_coeff):
        # First generate the grid we are fitting
        curr_grid = gen_grid(self.LENGTH, self.DELTA, grid_coeff[0], grid_coeff[1], (grid_coeff[2], grid_coeff[3]))

        # Evaluate distance**2 for each point in generated grid to its match in the mask
        total_dist = 0.0
        print("##############")
        print(len(curr_grid))
        for curr_idx in range(len(curr_grid)):
            curr_point = curr_grid[curr_idx]
            curr_com = self.asic_com[curr_idx]
            print("{},{}".format(curr_point, curr_com))
            min_dist = self.point_dist_sq(curr_point, curr_com)
            total_dist += math.sqrt(min_dist)

        return total_dist

    # Assume that the internal CoM list has been set with set_asic
    # Grid coeff is an array with scale, theta, offset_row, offset_col
    def calc_err_unorder(self, grid_coeff):
        # First generate the grid we are fitting
        curr_grid = gen_grid(self.LENGTH, self.DELTA, grid_coeff[0], grid_coeff[1], (grid_coeff[2], grid_coeff[3]))

        # Evaluate distance**2 for each point in generated grid to its match in the mask
        total_dist = 0.0

        for curr_point in curr_grid:
            min_idx, min_dist = self.nearest_com(curr_point, self.asic_com)
            total_dist += math.sqrt(min_dist)

        return total_dist
        
    # Assume that the internal CoM list has been set with set_asic
    # Grid coeff is an array with theta, offset_row, offset_col
    def calc_err2(self, grid_coeff):
        # First generate the grid we are fitting
        curr_grid = gen_grid(self.LENGTH, self.DELTA, 1.0, grid_coeff[0], (grid_coeff[1], grid_coeff[2]))

        # Evaluate distance**2 for each point in generated grid
        total_dist = 0.0
        for curr_point in curr_grid:
            min_idx, min_dist = self.nearest_com(curr_point, self.asic_com)
            total_dist += math.sqrt(min_dist)

        return total_dist
    
maskPath = "F_forgeocal.tiff"

data = imageio.imread(maskPath)

print("Image Shape: {}".format(data.shape))
print("Image Type: {}".format(data.dtype))


geocal_img = Peak_Image()

geocal_img.set_image(data)

if not geocal_img.label_peaks():
    print("Error labeling peaks.")
    sys.exit(1)

peak_count_status = geocal_img.quadrant_peak_count()
if peak_count_status is None:
    print("No image for peak counting.")
    sys.exit(1)
elif peak_count_status is False:
    print("Error in peak count.")
    sys.exit(1)
else:
    pass

# With the image labeled, I can check the center of mass

geocal_img.calc_CoM();

for row_idx in range(4):
    for col_idx in range(4):
        com_list = geocal_img.com_in_asic((row_idx, col_idx))
        print("ASIC {},{} has {} CoM.".format(row_idx, col_idx, len(com_list)))


test_nearest = (403,134)
my_com_list = geocal_img.com_in_asic((3,1))
com_idx, com_dist_sq = geocal_img.nearest_com(test_nearest, my_com_list)
print("Nearest CoM to {},{} is {},{}.".format(test_nearest[0], test_nearest[1], my_com_list[com_idx][0], my_com_list[com_idx][1]));

# Plot rotated grid

my_grid = gen_grid(9, 11, 1, 10.0/180*3.141593, offset=(448,192))
my_grid = gen_grid(9, 11, 1, 0, offset=(448,192))
#for point in my_grid:
#    geocal_img.peak_img[int(point[0]),int(point[1])] = 200

#plt.imshow(geocal_img.peak_img)
#plt.show()

# Now try the minimization
geocal_img.set_asic(3,0)
res1 = minimize(geocal_img.calc_err, [1.0, 0, 448, 64], method='nelder-mead')
print(res1.x)
res1_x = res1.x
my_grid = gen_grid(9, 11, res1_x[0], res1_x[1], offset=(res1_x[2], res1_x[3]))

print("CoM points:")
print(geocal_img.asic_com)

# Try iterating over every asic
full_grid = []
for asic_row in range(4):
    for asic_col in range(4):
        geocal_img.set_asic(asic_row, asic_col)
        res1 = minimize(geocal_img.calc_err, [1.0, 0, 1.5*asic_row*128, 1.5*asic_col*128], method='nelder-mead')
        res1_x = res1.x
        my_grid = gen_grid(9, 11, res1_x[0], res1_x[1], offset=(res1_x[2], res1_x[3]))
        full_grid.extend(my_grid)
        
for point in full_grid:
    if (point[0] < 0) or (point[0] >= 512) or (point[1] < 0) or (point[1] >= 512):
        continue
    geocal_img.peak_img[int(point[0]),int(point[1])] = 200

plt.imshow(geocal_img.peak_img)
plt.show()


                               
sys.exit(0)
        
labeled_img, num_objects = ndimage.label(data, structure=neighbor_mask)


for row_idx in range(4):
    for col_idx in range(4):
        start_row = ASIC_HEIGHT * row_idx
        start_col = ASIC_WIDTH * col_idx
        end_row = start_row + ASIC_HEIGHT
        end_col = start_col + ASIC_WIDTH
        curr_asic = labeled_img[start_row:end_row,start_col:end_col]
        distinct_val = set(curr_asic.flat)
        if not 0 in distinct_val:
            print("ERROR: No background found in quadrant.");
        num_peaks = len(distinct_val - set([0]))
        print("ASIC ({},{}) has {} peaks.".format(row_idx, col_idx, num_peaks))
        if (num_peaks != PEAKS_EXPECTED):
            print("ERROR: Incorrect number of values.  Wanted: {} Actual: {}".format(PEAKS_EPECTED, num_peaks))

            
com_list = ndimage.center_of_mass(data, labels=labeled_img, index=list(set(labeled_img.flat)-set([0])))

for coords in com_list:
    data[int(coords[0]+0.5), int(coords[1]+0.5)] = 128;

plt.imshow(data)
plt.show()
