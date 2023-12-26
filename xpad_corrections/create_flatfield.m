clear

num_caps = 8;
image_width = 512;
image_height = 512;
asic_width = 128;
asic_height = 128;
offset = 256;
gap = 1024;
num_skip_image = 0;             # The number of images at the start to skip
num_skip_frames = num_caps * num_skip_image; # Total frames to skip
y_margin = 3;
x_margin = 3;

asic_x_count = image_width/asic_width;
asic_y_count = image_height/asic_height;

##-=-= NOTE Dummy filenames that point to simulated data
dark_filename = 'xpad_dark.raw'; # The image of dark current
bright_filename = 'xpad_bright.raw'; # The flat-field image

##-=-= NOTE These are for images taken in forward order
dark_filename = 'dark_combined.raw';
bright_filename = 'bright_combined.raw';

##-=-= XXX These are for images taken in backwards order
dark_filename = 'reverse_dark.raw';
bright_filename = 'reverse_bright.raw';

[dark_raw, num_dark_frames] = read_xpad_image(dark_filename, 16, offset, gap, image_width, image_height);
disp('Loaded dark image')
printf("Dark frames count: %i\n", num_dark_frames);

# Skip the first NUM_SKIP_IMAGE images
# Remember there are NUM_CAPS frames per image
if (num_skip_frames > 0)
  disp("Skipping dark frames: ")
  disp(num_skip_frames)
  dark_raw = dark_raw(:,:,(num_skip_frames+1):num_dark_frames);
  num_dark_frames = num_dark_frames-num_skip_frames;
endif

## With the dark current image loaded, we can average the values per-cap
dark_image = avg_caps(dark_raw, num_caps);
clear dark_raw
disp('Averaged dark image')

## Now repeat for the bright image
[bright_raw, num_bright_frames] = read_xpad_image(bright_filename, 16, offset, gap, image_width, image_height);
disp('Loaded bright image')
printf("Bright frames count: %i\n", num_bright_frames);

# Skip the first NUM_SKIP_IMAGE images
# Remember there are NUM_CAPS frames per image
if (num_skip_frames > 0)
  disp("Skipping frames: ")
  disp(num_skip_frames)
  bright_raw = bright_raw(:,:,(num_skip_frames+1):num_bright_frames);
  num_bright_frames = num_bright_frames-num_skip_frames;
endif

## With the bright image loaded, we can average the values per-cap
bright_image = avg_caps(bright_raw, num_caps);
clear bright_raw
disp('Averaged bright image')
printf("Frames per cap: %i\n", num_bright_frames/num_caps);

## Now do the background subtraction
bg_sub_image = bright_image-dark_image;
disp('Completed background subtraction')

## We now need to NaN out the bad pixels.  These are contained in two PGM files
## Change the filenames here to suit.
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

pix_std = zeros(16, 8);

for cap_idx = 1:num_caps
  curr_frame = bg_sub_image(:,:,cap_idx);
  # Second parameter below is the threshold of gain deemed too low.
  flat_raster(:,:,cap_idx) = calc_flat_asic(curr_frame, 0.001);

  asic_idx = 0;
  for row_idx=1:asic_y_count
    row_lower = (row_idx-1)*asic_height+1;
    row_upper = row_lower+asic_height - 1;
    row_lower = row_lower + y_margin;
    row_upper = row_upper - y_margin;
    
    for col_idx=1:asic_x_count
      col_lower = (col_idx-1)*asic_width+1;
      col_upper = col_lower+asic_width - 1;
      col_lower = col_lower + x_margin;
      col_upper = col_upper - x_margin;
      
      asic_idx = asic_idx + 1;
      
      curr_asic_pix = curr_frame(row_lower:row_upper, col_lower:col_upper);
      flat_pix = reshape(calc_flat_asic(curr_asic_pix, 0.001),1, []);
      flat_pix = flat_pix(find(isfinite(flat_pix)));
      if isempty(flat_pix)
        pix_std(asic_idx, cap_idx) = -1;
      else
        pix_std(asic_idx, cap_idx) = std(1./flat_pix);
      endif
    endfor
  endfor
endfor

ff_filename = 'flatfield.raw';
ff_file = fopen(ff_filename, 'wb');

for cap_idx = 1:num_caps
  curr_frame = flat_raster(:,:,cap_idx)';
  fwrite(ff_file, curr_frame, "double", 0, "l");
endfor

figure(1)
subplot(1,1,1)
plot(1:num_caps, pix_std(7,:), '-b*;ASIC 7;', 1:num_caps, pix_std(8,:), '-r^;ASIC8;')
title("ASIC Flatness")
xlabel("Cap Number")
ylabel("Std Dev of Flatfield Gain (normalized to 1)")
print asic_flatness.png

printf("ASIC Flatness\n")
disp([pix_std(7:8,:) mean(pix_std(7:8,:),2)])

fclose(ff_file);

