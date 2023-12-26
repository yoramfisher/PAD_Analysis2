clear

asic_width = 128;
asic_height = 128;
img_width = 512;
img_height = 512;
num_caps = 8;                   # Camera Parameters
num_skip_images = 0;             # The number of images at the start to skip
num_skip_frames = num_caps * num_skip_images; # Total frames to skip
bad_asics = [1, 1, 1, 1; 1, 1, 0, 0; 1, 1, 1, 1; 1, 1, 1, 1]; # Set to 1 if the whole ASIC is bad
offset = 256;                   # Header size
gap=1024;                       # Gap between rasters

bad_thresh = [0.9 0.8 0.75 0.5];

##-=-= NOTE A good file
#prelim_bad_pixel_filename = 'blank_bad.raw';

#prelim_bad_pixel_file = fopen(prelim_bad_pixel_filename, "rb");

#prelim_bad_mask = fread(prelim_bad_pixel_file, [img_height, img_width], 'uint16', 0, 'b')';

## Note where preliminary bad pixels are set
#prelim_bad_mask = prelim_bad_mask != 0;
#fclose(prelim_bad_pixel_file);

prelim_bad_mask = zeros(512,512);
prelim_bad_mask(129:256, 128*3+1) = 1;
prelim_bad_mask = prelim_bad_mask != 0;
                                    
dark_image = zeros(img_height, img_width, num_caps);
bright_image = zeros(img_height, img_width, num_caps);

# Load in the the dark image and threshold
## Good filename
dark_image_filename = 'dark_combined.raw';

## Load in the whole stack
[raw_dark, num_frames] = read_xpad_image(dark_image_filename, 16, offset, gap, 512, 512);
disp("Loaded dark frames.")

## Skip the first NUM_SKIP_IMAGE background images
## Remember there are NUM_CAPS frames per image
if num_skip_frames > 0
  raw_dark = raw_dark(:,:,(num_skip_frames+1):num_frames);
  num_frames = num_frames-num_skip_frames;
endif

disp("Skipped bad dark frames.")

## Then average over each cap
for cap_idx = 1:num_caps
  dark_image(:,:,cap_idx) = mean(raw_dark(:,:,cap_idx:num_caps:num_frames),3);
endfor

disp("Averaged dark frames.")

clear raw_dark

## NaN out all bad pixels identified in pixel map
#for cap_idx = 1:num_caps
#  curr_slice = dark_image(:,:,cap_idx);
#  curr_slice(find(prelim_bad_mask)) = NaN;
#  dark_image(:,:,cap_idx) = curr_slice;
#endfor

## Now NaN out the bad asics
#dark_image = apply_bad_asic(bad_asics, asic_height, asic_width, dark_image);



## Threshold out the hot pixels
## The threshold is the third argument in thresh_image(), below.
#hot_filt = [];
#for curr_thresh=bad_thresh
#  [hot_img, pix_thresh] = thresh_image(dark_image, 0, curr_thresh, asic_width, asic_height);
#  hot_filt = [hot_filt pix_thresh];
#endfor

## Now do similar to find the dark pixels

## Load in the the dark image and threshold
## Filename of a test pattern
bright_image_filename = 'basic_pattern.raw';
## Good filename
bright_image_filename = 'bright_combined.raw';

## Load in the whole stack
[raw_bright, num_frames] = read_xpad_image(bright_image_filename, 16, offset, gap, 512, 512);
disp("Loaded bright frames.")


## Skip the first NUM_SKIP_IMAGE flatfiled images
## Remember there are NUM_CAPS frames per image
if num_skip_frames > 0
  raw_bright = raw_bright(:,:,(num_skip_frames+1):num_frames);
  num_frames = num_frames-num_skip_frames;
endif
disp("Skipped bad bright frames.")

                                # Background subtract
for frame_idx = 1:num_frames
  dark_frame_idx = mod(frame_idx, num_caps);
  if dark_frame_idx < 1
    dark_frame_idx = 8;
  endif
  
  curr_dark = dark_image(:,:,dark_frame_idx);
  
  raw_bright(:,:,frame_idx) = raw_bright(:,:,frame_idx) - curr_dark;
  if mod(frame_idx, num_caps) < 1
    disp("Background subtracted frame:")
    disp(frame_idx)
  endif
endfor

## Then average over each cap
for cap_idx = 1:num_caps
  bright_image(:,:,cap_idx) = mean(raw_bright(:,:,cap_idx:num_caps:num_frames),3);
endfor

disp("Averaged bright images.")

clear raw_bright

## NaN out all bad pixels identified in pixel map
for cap_idx = 1:num_caps
  curr_slice = bright_image(:,:,cap_idx);
  curr_slice(find(prelim_bad_mask)) = NaN;
  bright_image(:,:,cap_idx) = curr_slice;
endfor

disp("Masked bad pixels.")

## Now NaN out the bad asics
bright_image = apply_bad_asic(bad_asics, asic_height, asic_width, bright_image);

## Threshold out the hot pixels
## The threshold is the third argument in thresh_image(), below.
cold_filt = [];
for curr_thresh=bad_thresh
  [cold_img, curr_filt] = thresh_gain(bright_image, curr_thresh, asic_width, asic_height);
  cold_filt = [cold_filt curr_filt];
  disp("Thresholded gain level:")
  disp(curr_thresh)

  ## Record a mask at each threshold
  cold_total = sum(cold_img, 3);
  out_name = sprintf("dark_pixels_%.3f.pgm", curr_thresh);
  pgm_write(cold_total, out_name);
endfor

## With the bad pixels calculated, we can collapse them to single layers for writing out
## This works by adding NaNs so that a NaN in any cap propagates to the total
#hot_total = sum(hot_img, 3);
cold_total = sum(cold_img, 3);

## We can now write the images out to PGM files
## The pgm_write function is needed to convert NaNs and format the output properly
pgm_write(cold_total, "dark_pixels.pgm");
#pgm_write(hot_total, "hot_pixels.pgm");
