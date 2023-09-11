clear

asic_width = 128;
asic_height = 128;
img_width = 512;
img_height = 512;
num_caps = 8;                   # Camera Parameters
num_skip_images = 0;             # The number of images at the start to skip
num_skip_frames = num_caps * num_skip_images; # Total frames to skip
offset = 256;                   # Header size
gap=1024;                       # Gap between rasters
y_margin = 3;
x_margin = 3;                   #Pixels at each edge to ignore

asic_x_count = img_width/asic_width;
asic_y_count = img_height/asic_height;
asic_count = asic_x_count * asic_y_count;

bad_thresh = [1.5 1.806 1.955 2.2687 2.3881];

dark_image_filename = 'keck_test/dark_last2.raw'; # The image of all dark frames
dark_image_filename = 'keck_test/dark_combined.raw';
## Load in the whole stack
[raw_dark, num_frames] = read_xpad_image(dark_image_filename, 16, offset, gap, 512, 512);

printf("Total dark frames: %i\n", num_frames);

if mod(num_frames, num_caps) != 0
  error("Error: Frame count is not a multiple of number of caps.");
endif


## Subtract the stacks
stack_one_idx = 1:(num_frames/2);
stack_two_idx = (num_frames/2+1):(num_frames);
diff_stack = raw_dark(:,:,stack_two_idx) - raw_dark(:,:,stack_one_idx);

## We now need to NaN out the bad pixels.  These are contained in two PGM files
## Change the filenames here to suit.
bad_dark_pixels = imread("dark_pixels.pgm");
bad_hot_pixels = imread("hot_pixels.pgm");
disp('Loaded bad pixel maps')
bad_pixels = bad_dark_pixels+bad_hot_pixels;
bad_pixel_loc = find(bad_pixels != 0);

## Set all bad flat pixels to NaN
## Iterate over all caps
for slice_idx = 1:(num_frames/2)
  curr_slice = diff_stack(:,:,slice_idx);
  curr_slice(bad_pixel_loc) = NaN;
  diff_stack(:,:,slice_idx) = curr_slice;
endfor

diff_file = fopen("read_noise_diff.raw", "wb");
fwrite(diff_file, reshape(diff_stack,1,[]), "float64");
fclose(diff_file);


             # Compute a standard deviation for each ASIC for each cap
raw_cap_noise = zeros(asic_count, num_caps);
separate_cap_noise = zeros(asic_count, num_caps);
asic_idx = 0;

for cap_idx = 1:num_caps
  asic_idx = 0;
  cap_lower = cap_idx
  cap_range = cap_lower:num_caps:(num_frames/2);
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

      curr_asic = diff_stack(row_lower:row_upper, col_lower:col_upper, cap_range);
      
      raw_cap_noise(asic_idx, cap_idx) = calc_read_noise(curr_asic, 1);
      separate_cap_noise(asic_idx, cap_idx) = calc_read_noise(curr_asic, 0);
    endfor
  endfor
endfor

full_noise = mean(raw_cap_noise,2);

subplot(2,1,1)
plot(1:8,raw_cap_noise(7,:),'-b*;ASIC 7;', 1:8, raw_cap_noise(8,:),'-r^;ASIC 8;');
title("Total Noise")
subplot(2,1,2)
plot(1:8,separate_cap_noise(7,:),'-b*;ASIC 7;', 1:8, separate_cap_noise(8,:),'-r^;ASIC 8;');
title('Per-cap Noise')
