clear

asic_width = 128;
asic_height = 128;
img_width = 512;
img_height = 512;
num_caps = 8;
bad_asics = [0, 1, 0, 0; 0, 1, 1, 0; 0, 0, 0, 0; 0, 0, 0, 1];

prelim_bad_pixel_filename = 'bad_pixels.raw';
prelim_bad_pixel_file = fopen(prelim_bad_pixel_filename, "rb");

prelim_bad_mask = fread(prelim_bad_pixel_file, [img_height, img_width], 'uint16', 0, 'b')';

prelim_bad_mask = prelim_bad_mask != 0;
fclose(prelim_bad_pixel_file);

dark_image = zeros(img_height, img_width, num_caps);
bright_image = zeros(img_height, img_width, num_caps);

% Load in the the dark image and threshold
dark_image_filename = 'basic_pattern.raw';

[raw_dark, num_frames] = read_xpad_image(dark_image_filename, 16, 0, 0, 512, 512);
for cap_idx = 1:8
  dark_image(:,:,cap_idx) = mean(raw_dark(:,:,cap_idx:8:num_frames),3);
endfor

#m_is
[basic_grad, num_frames] = read_xpad_image('basic_pattern.raw', 16, 0, 0, 512, 512);
num_frames
imagesc(basic_grad(:,:,5))

%dark_image = zeros(img_height, img_width, num_caps);
%for cap_idx = 1:8
%  dark_image(:,:,cap_idx) = mean(basic_grad(:,:,cap_idx:8:num_frames),3);
%endfor

for cap_idx = 1:8
  curr_slice = dark_image(:,:,cap_idx);
  curr_slice(find(prelim_bad_mask)) = NaN;
  dark_image(:,:,cap_idx) = curr_slice;
endfor

dark_image = apply_bad_asic(bad_asics, asic_height, asic_width, dark_image);

imagesc(dark_image(:,:,4))

bad_img = thresh_image(dark_image, 0, 0.005, asic_width, asic_height);

#imagesc(bad_img(:,:,1))
