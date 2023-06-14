clear

asic_width = 128;
asic_height = 128;
img_width = 512;
img_height = 512;
num_caps = 8;                   # Camera Parameters
num_skip_image = 9;             # The number of images at the start to skip
num_skip_frames = num_caps * num_skip_images; # Total frames to skip
bad_asics = [0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0]; # Set to 1 if the whole ASIC is bad
offset = 256;                   # Header size
gap=1024;                       # Gap between rasters

##-=-= NOTE A good file
prelim_bad_pixel_filename = 'blank_bad.raw';

prelim_bad_pixel_file = fopen(prelim_bad_pixel_filename, "rb");

prelim_bad_mask = fread(prelim_bad_pixel_file, [img_height, img_width], 'uint16', 0, 'b')';

## Note where preliminary bad pixels are set
prelim_bad_mask = prelim_bad_mask != 0;
fclose(prelim_bad_pixel_file);

dark_image = zeros(img_height, img_width, num_caps);
bright_image = zeros(img_height, img_width, num_caps);

# Load in the the dark image and threshold
## Good filename
dark_image_filename = 'C:/rtsup/raid/keckpad/set-rework/run-back5ms/frames/back5ms_00000001.raw';

## Load in the whole stack
[raw_dark, num_frames] = read_xpad_image(dark_image_filename, 16, offset, gap, 512, 512);

## Skip the first NUM_SKIP_IMAGE background images
## Remember there are NUM_CAPS frames per image
raw_dark = raw_dark(:,:,(num_skip_frames+1):num_frames);
num_frames = num_frames-num_skip_frames;

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

## Threshold out the hot pixels
## The threshold is the third argument in thresh_image(), below.
hot_img = thresh_image(dark_image, 0, 1.7, asic_width, asic_height);

## Now do similar to find the dark pixels

## Load in the the dark image and threshold
## Filename of a test pattern
bright_image_filename = 'basic_pattern.raw';
## Good filename
bright_image_filename = 'C:/rtsup/raid/keckpad/set-rework/run-flat30KV5ms/frames/flat30KV5ms_00000001.raw';

## Load in the whole stack
[raw_bright, num_frames] = read_xpad_image(bright_image_filename, 16, offset, gap, 512, 512);

## Skip the first NUM_SKIP_IMAGE flatfiled images
## Remember there are NUM_CAPS frames per image
raw_bright = raw_bright(:,:,(num_skip_frames+1):num_frames);
num_frames = num_frames-num_skip_frames;


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
## The threshold is the third argument in thresh_image(), below.
cold_img = thresh_image(bright_image, 1, 1.5, asic_width, asic_height);

## With the bad pixels calculated, we can collapse them to single layers for writing out
## This works by adding NaNs so that a NaN in any cap propagates to the total
hot_total = sum(hot_img, 3);
cold_total = sum(cold_img, 3);

## We can now write the images out to PGM files
## The pgm_write function is needed to convert NaNs and format the output properly
pgm_write(cold_total, "dark_pixels.pgm");
pgm_write(hot_total, "hot_pixels.pgm");
