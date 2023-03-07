import numpy as np
import scipy
import scipy.ndimage as ndimage
import imageio
import math

BOX_BOUNDS = [-1, 0, 1]
NUM_POINTS = 81
GRID_LENGTH = 9
GRID_DELTA = 11

ASIC_WIDTH = 128
ASIC_HEIGHT = 128

# Center in (y,x)
def place_box(full_image, center, bounds):
    ctr_x = int(center[1])
    ctr_y = int(center[0])
    for x_diff in BOX_BOUNDS:
        for y_diff in BOX_BOUNDS:
            full_image[ctr_y + y_diff][ctr_x + x_diff] = 255

    return

test_image = np.zeros((ASIC_HEIGHT * 4, ASIC_WIDTH * 4), np.uint16)

MAG_FACTOR = 1.037
MAG_FACTOR = 0.9
for asic_row in range(4):
    asic_ctr_y = int(asic_row * ASIC_HEIGHT + ASIC_HEIGHT/2)
    for asic_col in range(4):
        asic_ctr_x = 0;
        CHANGE_MAG = 1;
        if (CHANGE_MAG == 0):
            asic_ctr_x = int(asic_col * ASIC_WIDTH + ASIC_WIDTH/2)
        else:
            sm_ctr = 128;               # 128 pixels is half across an submodule
            if ((asic_col%2) == 0):     # We are on the left side
                asic_ctr_x = sm_ctr - (ASIC_WIDTH/2*MAG_FACTOR) # Magnified distance from center on left
            else:
                asic_ctr_x = sm_ctr + (ASIC_WIDTH/2*MAG_FACTOR); # Ibid, but on right
            sm_col = int(asic_col / 2); # What submodule we are in
            asic_ctr_x = int(asic_ctr_x)+sm_col*ASIC_WIDTH*2
            
        for row_idx in range(GRID_LENGTH):
            hole_row = int(row_idx - math.ceil(GRID_LENGTH/2))
            hole_ctr_y = asic_ctr_y + int((hole_row * GRID_DELTA * MAG_FACTOR)+0.5)
            for col_idx in range(GRID_LENGTH):
                hole_col = int(col_idx - math.ceil(GRID_LENGTH/2))
                hole_ctr_x = asic_ctr_x + int((hole_col * GRID_DELTA * MAG_FACTOR+0.5))
                place_box(test_image, (hole_ctr_y, hole_ctr_x), BOX_BOUNDS);

DO_SPACING = False
if DO_SPACING:
    test_image = np.zeros((512,512), np.uint16)
    for asic_row in range(4):
        asic_ctr_y = int(asic_row * ASIC_HEIGHT + ASIC_HEIGHT/2)
        for asic_col in range(0,4,2):
            asic_ctr_x = int(asic_col * ASIC_WIDTH + ASIC_WIDTH/2)
            for row_idx in range(GRID_LENGTH):
                hole_row = int(row_idx - math.ceil(GRID_LENGTH/2))
                hole_ctr_y = asic_ctr_y + int((hole_row * GRID_DELTA * MAG_FACTOR)+0.5)
                for col_idx in range(GRID_LENGTH):
                    hole_col = int(col_idx - math.ceil(GRID_LENGTH/2))
                    hole_ctr_x = asic_ctr_x + int((hole_col * GRID_DELTA * MAG_FACTOR+0.5))
                    place_box(test_image, (hole_ctr_y, hole_ctr_x), BOX_BOUNDS);
                    place_box(test_image, (hole_ctr_y, hole_ctr_x+131), BOX_BOUNDS);
                
imageio.imwrite("grid_pattern.png", test_image);
