clear

start_time = time();

image_width = 512;
image_height = 512;
asic_width = 128;
asic_height = 128;
num_caps = 8;
offset = 256;
gap = 1024;


##-=-= NOTE Dummy filename that points to simulated data
dark_image_filename = 'xpad_dark.raw';
##-=-= Filename pointing to actual data
dark_image_filename = '/media/iainm/7708b1ae-fb79-4039-914b-6f905445c611/iainm/ff_keck_test/run-back5ms/frames/back5ms_00000001.raw';

#dark_image_file = fopen(dark_image_filename, 'rb');
[dark_raw, num_dark_frames] = read_xpad_image(dark_image_filename, 16, offset, gap, image_width, image_height);
dark_image = avg_caps(dark_raw, num_caps);
clear dark_raw

##-=-= NOTE Dummy filename that points to simulated data
test_image_filename = 'xpad_test.raw';
##-=-= Filename pointing to actual data
test_image_filename = '/media/iainm/7708b1ae-fb79-4039-914b-6f905445c611/iainm/ff_keck_test/run-flat30KV5ms/frames/flat30KV5ms_00000001.raw';
#test_image_file = fopen(test_image_filename, 'rb');
[test_image, num_image_frames] = read_xpad_image(test_image_filename, 16, offset, gap, image_width, image_height);

bg_sub_image = test_image;
for frame_idx=1:num_image_frames
  cap_idx = mod(frame_idx-1, num_caps)+1;
  bg_sub_image(:,:,frame_idx) = test_image(:,:,frame_idx)-dark_image(:,:,cap_idx);
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
  corr_image(:,:,frame_idx) = bg_sub_image(:,:,frame_idx).*flat_raster(:,:,cap_idx);
endfor

end_time = time();

disp('Correction elapsed time')
end_time-start_time

## Now save the files to disc
bg_sub_file = fopen('bg_sub.raw', 'wb');
corr_file = fopen('corr_sub.raw', 'wb');

corr_image(find(isnan(corr_image))) = 0;

for frame_idx=1:num_image_frames
  fwrite(bg_sub_file, bg_sub_image(:,:,frame_idx)', "double", 0, "l");
  fwrite(corr_file, corr_image(:,:,frame_idx)', "double", 0, "l");
endfor

fclose(bg_sub_file);
fclose(corr_file);
