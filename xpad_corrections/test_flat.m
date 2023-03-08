clear

image_width = 512;
image_height = 512;
asic_width = 128;
asic_height = 128;
num_caps = 8;

dark_image_filename = 'xpad_dark.raw';
#dark_image_file = fopen(dark_image_filename, 'rb');
[dark_raw, num_dark_frames] = read_xpad_image(dark_image_filename, 16, 0, 0, image_width, image_height);
dark_image = avg_caps(dark_raw, num_caps);
clear dark_raw

test_image_filename = 'xpad_test.raw';
#test_image_file = fopen(test_image_filename, 'rb');
[test_image, num_image_frames] = read_xpad_image(test_image_filename, 16, 0, 0, image_width, image_height);

bg_sub_image = test_image;
for frame_idx=1:num_image_frames
  cap_idx = mod(frame_idx-1, num_caps)+1;
  bs_sub_image(:,:,frame_idx) = test_image(:,:,frame_idx)-dark_image(:,:,cap_idx);
endfor

subplot(2,1,1)
imagesc(bg_sub_image(:,:,3))
subplot(2,1,2)
imagesc(bg_sub_image(:,:,4))

## Now load the flatfield file
flat_filename = 'flatfield.raw';
flat_file = fopen(flat_filename, 'rb');
flat_raster = zeros(image_height, image_width, num_caps);

for cap_idx = 1:num_caps
  curr_frame = fread(flat_file, [image_height, image_width], "double", 0, "l");
  flat_raster(:,:,cap_idx) = curr_frame';
endfor

fclose(flat_file);

corr_image = test_image;
for frame_idx=1:num_image_frames
  cap_idx = mod(frame_idx-1, num_caps)+1;
  corr_image(:,:,frame_idx) = test_image(:,:,frame_idx).*flat_raster(:,:,cap_idx);
endfor
