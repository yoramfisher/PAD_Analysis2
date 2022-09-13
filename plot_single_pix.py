import numpy as np
import matplotlib.pyplot as plt
import matplotlib

maskFilename = 'single_pix.csv';
maskFile = open(maskFilename, 'r')

hit_array = np.zeros((512,512));
for currLine in maskFile:
    split_line = currLine.split(',');
    hit_array[int(split_line[0]), int(split_line[1])] = float(split_line[3]);

maskFile.close()

fig,ax = plt.subplots(1,1)
scale_list = hit_array.reshape(1,-1).tolist()[0];
scale_list.sort();
num_points = len(scale_list);
vmin = scale_list[int(num_points*0.005)];
vmax = scale_list[int(num_points*(1-0.005))];
#ax.imshow(hit_array, norm=matplotlib.colors.Normalize(vmin=vmin, vmax=vmax));
ax.imshow(hit_array);

plt.show()