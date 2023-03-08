clear

num_caps = 8;
image_width = 512;
image_height = 512;
asic_width = 128;
asic_height = 128;

asic_x_count = image_width/asic_width;
asic_y_count = image_height/asic_height;

dark_filename = 'xpad_dark.raw'; # The image of dark current
bright_filename = 'xpad_bright.raw'; # The flat-field image

[dark_raw, num_dark_frames] = read_xpad_image(dark_filename, 16, 0, 0, image_width, image_height);
disp('Loaded dark image')

## With the dark current image loaded, we can average the values per-cap
dark_image = avg_caps(dark_raw, num_caps);
clear dark_raw
disp('Averaged dark image')

## Now repeat for the bright image
[bright_raw, num_bright_frames] = read_xpad_iamge(bright_filename, 16, 0, 0, image_width, image_height);
disp('Loaded bright image')

## With the bright image loaded, we can average the values per-cap
bright_image = avg_caps(dark_raw, num_caps);
clear bright_raw
disp('Averaged bright image')

## Now do the background subtraction
bgsub_image = bright_image-dark_image;
disp('Completed background subtraction')

## We now need to NaN out the bad pixels.  These are contained in two PGM files
bad_dark_pixels = imread("dark_pixels.pgm");
bad_hot_pixels = imread("hot_pixels.pgm");
disp('Loaded bad pixel maps')

## -=-= XXX Makes no accounting for overflow of the sum, so the masks should only have values of 1
bad_pixels = bad_dark_pixels+bad_hot_pixels; #Combine the two images
bad_pixel_loc = find(bad_pixels != 0);       #Get the locations
disp('Found bad pixels')

## Set all bad flat pixels to NaN
## Iterate over all caps
for cap_idx = 1:num_caps
  curr_slice = bg_sub_image(:,:,cap_idx);
  curr_slice(bad_pixel_loc) = NaN;
  bg_sub_image(:,:,cap_idx) = curr_slice;
  disp('Masked bad pixels for cap ')
  cap_idx
endfor
