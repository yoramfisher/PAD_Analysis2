clear

num_caps = 8
dark_val = 50;                  # Dark current Poisson mean
flat_val = 1000;                # Flat field current Poisson mean
num_frames = 100;               # How many frames to generate, per cap
image_width = 512;
image_height = 512;
asic_width = 128;
asic_height = 128;

asic_x_count = image_width/asic_width;
asic_y_count = image_height/asic_height;

rand("state", [42 17 69 105]);  # Seed to a known start
randn("state", [69 105 42 17]);
randp("state", [105 69 17 42]);

## First generate the random gains per asic
asic_deviation = rand(asic_y_count, asic_x_count, num_caps)*0.2-0.1; # 10% gain difference
asic_deviation = asic_deviation+1;                                   #Gains are offset from uniform gain of 1

## Now generate the random gains per pixel
pixel_gains = randn(image_height, image_width, num_caps)*(0.05/3); # 5% gain difference
pixel_gains = min(0.05, pixel_gains);
pixel_gains = max(-0.05, pixel_gains); # Clip to 5%
pixel_gains += 1;                      # Change to factor

for cap_idx = 1:num_caps
  for row_idx = 1:asic_y_count
    y_start = (row_idx-1)*asic_height+1;
    y_end = row_idx*asic_height;
    for col_idx = 1:asic_x_count
      x_start = (col_idx-1)*asic_width+1;
      x_end = col_idx*asic_width;

      pixel_gains(y_start:y_end, x_start:x_end, cap_idx) *= asic_deviation(row_idx, col_idx, cap_idx);
    endfor
  endfor
endfor

## Now set low-gain pixels
num_low_pixels = 0.1*(image_width*image_height);
for pixel_idx = 1:num_low_pixels
  rand_x = floor(rand(1,1)*image_width)+1;
  rand_y = floor(rand(1,1)*image_height)+1;
  pixel_gains(rand_y, rand_x, :) = pixel_gains(rand_y, rand_x, :)/800.0;
endfor

## With the gains generated, the dark and flat images can be generated

## First generate the base frames
dark_image = randp(dark_val, image_height, image_width, num_caps*num_frames);
## Then multiply by the per-cap gains
for frame_idx = 1:(num_caps*num_frames)
  cap_idx = mod(frame_idx-1, num_caps)+1; # Get the current cap
  dark_image(:,:,frame_idx) = dark_image(:,:,frame_idx).*pixel_gains(:,:,cap_idx);
endfor

subplot(2,1,1)
imagesc(dark_image(:,:,3))
subplot(2,1,2)
imagesc(dark_image(:,:,32)-dark_image(:,:,24))

## Now we have to save the dark image
dark_filename = 'xpad_dark.raw';
dark_file = fopen(dark_filename, "wb");

for frame_idx = 1:(num_frames*num_caps)
  curr_slice = dark_image(:,:,frame_idx)'; #Get the slice
  fwrite(dark_file, curr_slice, "uint16", 0, "b"); #-=-= XXX Write big-endian -- may need to switch later
endfor

fclose(dark_file);
clear dark_image

## Now generate the bright image
## First generate the base frames of dark plus flat
flat_image = randp(dark_val+flat_val, image_height, image_width, num_caps*num_frames);

## Then multiply by the per-cap gains
for frame_idx = 1:(num_caps*num_frames)
  cap_idx = mod(frame_idx-1, num_caps)+1; # Get the current cap
  flat_image(:,:,frame_idx) = flat_image(:,:,frame_idx).*pixel_gains(:,:,cap_idx);
endfor

## Then save to disk
bright_filename = 'xpad_bright.raw';
bright_file = fopen(bright_filename, "wb");

for frame_idx = 1:(num_frames*num_caps)
  curr_slice = flat_image(:,:,frame_idx)'; #Get the slice
  fwrite(bright_file, curr_slice, "uint16", 0, "b"); #-=-= XXX Write big-endian -- may need to switch later
endfor

fclose(bright_file);
clear bright_image


## Now create a flat file for testing the flat field correction
## First generate the base frames of dark plus new exposure
num_test_frames = 3;
test_image = randp(dark_val+2*flat_val, image_height, image_width, num_caps*num_test_frames);

## Then multiply by the per-cap gains
for frame_idx = 1:(num_caps*num_test_frames)
  cap_idx = mod(frame_idx-1, num_caps)+1; # Get the current cap
  test_image(:,:,frame_idx) = test_image(:,:,frame_idx).*pixel_gains(:,:,cap_idx);
endfor

## Then save to disk
test_filename = 'xpad_test.raw';
test_file = fopen(test_filename, "wb");

for frame_idx = 1:(num_test_frames*num_caps)
  curr_slice = test_image(:,:,frame_idx)'; #Get the slice
  fwrite(test_file, curr_slice, "uint16", 0, "b"); #-=-= XXX Write big-endian -- may need to switch later
endfor

fclose(test_file);
clear test_image
