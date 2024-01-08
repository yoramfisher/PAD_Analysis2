clear

cfg_filename = 'flatfield_map.ini';
cfg_file = fopen(cfg_filename);
[cfg_list, file_status] = get_config_line(cfg_file);
fclose(cfg_file);

for cfg_idx = 1:size(cfg_list)(1)
  curr_name = strtrim(cfg_list{cfg_idx, 1}{1,1});
  curr_val = strtrim(cfg_list{cfg_idx, 2}{1,1});

  if strcmp(curr_name, "asic_width")
    asic_width = str2double(curr_val);
  elseif strcmp(curr_name, "asic_height")
    asic_height = str2double(curr_val);
  elseif strcmp(curr_name, "img_width")
    image_width = str2double(curr_val);
  elseif strcmp(curr_name, "img_height")
    image_height = str2double(curr_val);
  elseif strcmp(curr_name, "num_caps")
    num_caps = str2double(curr_val);
  elseif strcmp(curr_name, "file_offset")
    offset = str2double(curr_val);
  elseif strcmp(curr_name, "file_gap")
    gap = str2double(curr_val);
  elseif strcmp(curr_name, "num_skip_images")
    num_skip_images = str2double(curr_val);
  elseif strcmp(curr_name, "gain_threshold")
    gain_thresh = str2double(curr_val);
  elseif strcmp(curr_name, "dark_slope_thresh")
    bad_thresh = str2num(curr_val);
  elseif strcmp(curr_name, "x_margin")
    x_margin = str2double(curr_val);
  elseif strcmp(curr_name, "y_margin")
    y_margin = str2double(curr_val);
  elseif strcmp(curr_name, "dark_image_filename")
    dark_image_filename = curr_val;
  elseif strcmp(curr_name, "bright_image_filename")
    bright_image_filename = curr_val;
  elseif strcmp(curr_name, "dark_mask")
    dark_mask_filename = curr_val;
  elseif strcmp(curr_name, "hot_mask")
    hot_mask_filename = curr_val;
  elseif strcmp(curr_name, "bpp")
    sensor_bpp = str2double(curr_val);
  endif
endfor



#num_caps = 8;
#image_width = 512;
#image_height = 512;
#asic_width = 128;
#asic_height = 128;
#offset = 256;
#gap = 1024;
#num_skip_image = 0;             # The number of images at the start to skip
num_skip_frames = num_caps * num_skip_images; # Total frames to skip
#y_margin = 3;
#x_margin = 3;

asic_x_count = image_width/asic_width;
asic_y_count = image_height/asic_height;

asic_count = asic_x_count * asic_y_count;

[dark_raw, num_dark_frames] = read_xpad_image(dark_image_filename, sensor_bpp, offset, gap, image_width, image_height);
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
[bright_raw, num_bright_frames] = read_xpad_image(bright_image_filename, sensor_bpp, offset, gap, image_width, image_height);
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
bad_dark_pixels = imread(dark_mask_filename);
bad_hot_pixels = imread(hot_mask_filename);
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

pix_std = zeros(asic_count, num_caps);
pix_mean = zeros(asic_count, num_caps);         # -=-= TODO Make generic
for cap_idx = 1:num_caps
  curr_frame = bg_sub_image(:,:,cap_idx);
  # Second parameter below is the threshold of gain deemed too low.
  flat_raster(:,:,cap_idx) = calc_flat_asic(curr_frame, gain_thresh);

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
      flat_pix = reshape(calc_flat_asic(curr_asic_pix, gain_thresh),1, []);
      flat_pix = flat_pix(find(isfinite(flat_pix)));
      if isempty(flat_pix)
        pix_std(asic_idx, cap_idx) = -1;
        pix_mean(asic_idx, cap_idx) = -1;          # This should be an invalid value
      else
        pix_std(asic_idx, cap_idx) = std(10*log10(flat_pix));
        pix_mean(asic_idx, cap_idx) = mean(flat_pix);
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
plot(1:num_caps, pix_std(7,:), '-b*;ASIC 2;', 1:num_caps, pix_std(8,:), '-r^;ASIC3;')
title("ASIC Flatness")
xlabel("Cap Number")
ylabel("Std Dev of Flatfield Gain (dB)")
print asic_flatness.png

printf("ASIC Flatness\n")
disp([pix_std(7:8,:) mean(pix_std(7:8,:),2)])

h = bar(pix_mean(:,2)/pix_mean(3,2))
set(h, "basevalue", 1)

fclose(ff_file);

