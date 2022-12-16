#Avg_IMG_Viewer.py created by BWM 9/12/22
#program to create pretty averaged images plot and save them

import numpy as np
import Big_keck_load as BKL
import scipy
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import imageio
import os
import matplotlib.pyplot as plt
import sys
import tkinter.filedialog as fd
import findpeaks.findpeaks as fp   # https://erdogant.github.io/findpeaks/pages/html/index.html 
import tifffile
# img = tifffile.imread(tif_name)


plt.clf()

# Data location of complete geocal mask image
maskPath = "C:/Users/valerief/Desktop/KeckPAD_headdata/F_forgeocal.png"

# Requirements for finding a local maximum 
neighborhood_size = 3
threshold = 250

data = imageio.imread(maskPath) 

# Look at how big the image is to make sure it imported correctly
# Code expects a single image with a 'perfect' geocal mask, thresholded at 0/255
print(data.shape)
print(data.dtype)

# Find the local max and local min
data_max = filters.maximum_filter(data, neighborhood_size)
maxima = (data == data_max)
data_min = filters.minimum_filter(data, neighborhood_size)
diff = ((data_max - data_min) > threshold)
maxima[diff == 0] = 0

labeled, num_objects = ndimage.label(maxima)
slices = ndimage.find_objects(labeled)
x, y = [], []
for dy,dx in slices:
    x_center = (dx.start + dx.stop - 1)/2
    x.append(x_center)
    y_center = (dy.start + dy.stop - 1)/2    
    y.append(y_center)

# append the x and y lists together to make coordinates
peaks = np.vstack((x, y)).T



# plt.imshow(data)
# plt.savefig('C:/Users/valerief/Desktop/KeckPAD_headdata/data.png', bbox_inches = 'tight')

plt.autoscale(False)
plt.plot(peaks[:,0], peaks[:,1], 'ro')
plt.savefig('C:/Users/valerief/Desktop/KeckPAD_headdata/result.png', bbox_inches = 'tight')
plt.show()





# Find the geocal mask points on each ASIC
# # mask method
# finderP = fp(method="mask")
# finderP.fit(geo)
# finderP.plot_preprocessing()
# finderP.plot()

# # scale method
# finderP = fp(method="mask", scale=True)
# finderP.fit(geo)
# finderP.plot_preprocessing()
# finderP.plot()


# # finderP = fp(method="topology", interpolate=None, limit=1, verbose=5)
# geoCalPeaks = finderP.fit(geo)
# x= geoCalPeaks['Xdetect']
# print (str(geoCalPeaks.keys()))
# #print(geoCalPeaks['persistance'])
# #print(geoCalPeaks)
# plotData = np.resize(x, [512,512])
# plt.imshow(plotData)
# plt.show()
