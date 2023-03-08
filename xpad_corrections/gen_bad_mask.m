clear

asic_width = 128;
asic_height = 128;
img_width = 512;
img_height = 512;
num_caps = 8;                   # Camera Parameters
bad_asics = [0, 1, 0, 0; 0, 1, 1, 0; 0, 0, 0, 0; 0, 0, 0, 1]; # Set to 1 if the whole ASIC is bad

## Image raster with known bad pixels set non-zero
prelim_bad_pixel_filename = 'bad_pixels.raw';
prelim_bad_pixel_file = fopen(prelim_bad_pixel_filename, "rb");

prelim_bad_mask = fread(prelim_bad_pixel_file, [img_height, img_width], 'uint16', 0, 'b')';

## Note where preliminary bad pixels are set
prelim_bad_mask = prelim_bad_mask != 0;
fclose(prelim_bad_pixel_file);

dark_image = zeros(img_height, img_width, num_caps);
bright_image = zeros(img_height, img_width, num_caps);

% Load in the the dark image and threshold
dark_image_filename = 'basic_pattern.raw';

## Load in the whole stack
[raw_dark, num_frames] = read_xpad_image(dark_image_filename, 16, 0, 0, 512, 512);
## Then average over each cap
for cap_idx = 1:num_caps
  dark_image(:,:,cap_idx) = mean(raw_dark(:,:,cap_idx:num_caps:num_frames),3);
endfor

clear raw_dark

## NaN out all bad pixels identified in pixel map
for cap_idx = 1:num_caps
  curr_slice = dark_image(:,:,cap_idx);
  curr_slice(find(prelim_bad_mask)) = NaN;
  dark_image(:,:,cap_idx) = curr_slice;
endfor

## Now NaN out the bad asics
dark_image = apply_bad_asic(bad_asics, asic_height, asic_width, dark_image);

imagesc(dark_image(:,:,4))

## Threshold out the hot pixels
hot_img = thresh_image(dark_image, 0, 0.005, asic_width, asic_height);

## Now do similar to find the dark pixels

% Load in the the dark image and threshold
bright_image_filename = 'basic_pattern.raw';

## Load in the whole stack
[raw_bright, num_frames] = read_xpad_image(bright_image_filename, 16, 0, 0, 512, 512);
## Then average over each cap
for cap_idx = 1:num_caps
  bright_image(:,:,cap_idx) = mean(raw_bright(:,:,cap_idx:num_caps:num_frames),3);
endfor

clear raw_bright

## NaN out all bad pixels identified in pixel map
for cap_idx = 1:num_caps
  curr_slice = bright_image(:,:,cap_idx);
  curr_slice(find(prelim_bad_mask)) = NaN;
  bright_image(:,:,cap_idx) = curr_slice;
endfor

## Now NaN out the bad asics
bright_image = apply_bad_asic(bad_asics, asic_height, asic_width, bright_image);

## Threshold out the hot pixels
cold_img = thresh_image(bright_image, 1, 0.005, asic_width, asic_height);

## With the bad pixels calculated, we can collapse them to single layers for writing out
hot_total = sum(hot_img, 3);
cold_total = sum(cold_img, 3);

## We can now write the images out to PGM files
pgm_write(cold_total, "dark_pixels.pgm");
pgm_write(hot_total, "hot_pixels.pgm");
