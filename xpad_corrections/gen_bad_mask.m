clear

asic_width = 128;
asic_height = 128;
img_width = 512;
img_height = 512;
num_caps = 8;
bad_asics = [0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1];

#prelim_bad_pixel_filename = 'bad_pixels.raw';
#prelim_bad_pixel_file = fopen(prelim_bad_pixel_filename, "rb");

#prelim_bad_mask = fread(prelim_bad_pixel_file, [asic_height, asic_width], 'uint32');

#prelim_bad_mask = prelim_bad_mask != 0;
#fclose(prelim_bad_pixel_file);

dark_image = zeros(img_height, img_width, num_caps);
bright_image = zeros(img_height, img_width, num_caps);

                            % Load in the the dark image and threshold
#dark_image_filename = 'dark_image.raw';
#dark_image_file = fopen(dark_image_filename, 'rb');
#m_is
[basic_grad, num_frames] = read_xpad_image('basic_grad.raw', 16, 0, 0, 512, 512);
num_frames
imagesc(basic_grad(:,:,1))

dark_image = zeros(img_height, img_width, num_caps);
for cap_idx = 1:8
  dark_image(:,:,cap_idx) = mean(basic_grad(:,:,cap_idx:8:num_frames),3);
endfor

