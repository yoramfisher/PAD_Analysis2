import numpy as np
import os

class MaskExtractor:
    def __init__(self):
        self.img_width = 512;
        self.img_height = 512;
        self.num_caps = 8;
        self.singlePixelMat = np.zeros((1, self.img_height, self.img_width)).astype(bool);
        self.broadcastCaps = False; # Whether to spread hits to all caps
        self.valid_values = [];
        self.valid_values.append([]);
        
    def clear_valid(self):
        self.valid_values = [];
        self.valid_values.append([]);
        
    def load_mask(self, maskFilename):
        maskFile = open(maskFilename, 'r');
        for curr_line in maskFile:
            line_split = curr_line.split(',');
            if self.broadcastCaps:
                self.singlePixelMat[:, int(line_split[0]), int(line_split[1])] = True; # Note as a valid pixel for all caps, as the mask won't move between caps
            else:
                self.singlePixelMat[int(line_split[2]), int(line_split[0]), int(line_split[1])] = True; # Note as a valid pixel for just one cap
        maskFile.close();
        return True;

    def extract_frame(self, curr_frame):
        if False and self.broadcastCaps:
            cap_num = 0;  # Only store in cap 0 if we are doing all pixels
        curr_mask = self.singlePixelMat[0, :, :]; # Extract the current mask
        valid_pixels = curr_frame[curr_mask];           # Get pixels where mask is True
        curr_valid = self.valid_values; # Presently a NOP
        self.valid_values[0].extend(valid_pixels.reshape((1,-1)).tolist()[0]);
        return;

