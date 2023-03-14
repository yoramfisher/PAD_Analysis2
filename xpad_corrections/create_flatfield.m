clear

num_caps = 8;
image_width = 512;
image_height = 512;
asic_width = 128;
asic_height = 128;
offset = 256;
gap = 1024;

asic_x_count = image_width/asic_width;
asic_y_count = image_height/asic_height;

##-=-= NOTE Dummy filenames that point to simulated data
dark_filename = 'xpad_dark.raw'; # The image of dark current
bright_filename = 'xpad_bright.raw'; # The flat-field image

dark_filename = '/media/iainm/7708b1ae-fb79-4039-914b-6f905445c611/iainm/ff_keck_test/run-back5ms/frames/back5ms_00000001.raw';
bright_filename = '/media/iainm/7708b1ae-fb79-4039-914b-6f905445c611/iainm/ff_keck_test/run-flat30KV5ms/frames/flat30KV5ms_00000001.raw';

[dark_raw, num_dark_frames] = read_xpad_image(dark_filename, 16, offset, gap, image_width, image_height);
disp('Loaded dark image')

# Skip the first 9 frames
dark_raw = dark_raw(:,:,73:num_dark_frames);
num_dark_frames = num_dark_frames-72;

## With the dark current image loaded, we can average the values per-cap
dark_image = avg_caps(dark_raw, num_caps);
clear dark_raw
disp('Averaged dark image')

## Now repeat for the bright image
[bright_raw, num_bright_frames] = read_xpad_image(bright_filename, 16, offset, gap, image_width, image_height);
disp('Loaded bright image')

## With the bright image loaded, we can average the values per-cap
bright_image = avg_caps(bright_raw, num_caps);
clear bright_raw
disp('Averaged bright image')

## Now do the background subtraction
bg_sub_image = bright_image-dark_image;
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

## Now compute the flatfield corrections
flat_raster = zeros(image_height, image_width, num_caps);

for cap_idx = 1:num_caps
  curr_frame = bg_sub_image(:,:,cap_idx);
  flat_raster(:,:,cap_idx) = calc_flat_asic(curr_frame, 0.001);
endfor

ff_filename = 'flatfield.raw';
ff_file = fopen(ff_filename, 'wb');

for cap_idx = 1:num_caps
  curr_frame = flat_raster(:,:,cap_idx)';
  fwrite(ff_file, curr_frame, "double", 0, "l");
endfor

fclose(ff_file);

