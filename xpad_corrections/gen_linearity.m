clear

asic_width = 128;
asic_height = 128;
img_width = 512;
img_height = 512;
num_caps = 1;                   # Camera Parameters
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

dark_image_filename = 'keck_test/linearity/50KV_0C_2p5ms_linear_b_00000001.raw'

## Load in the whole stack
[raw_dark, num_frames] = read_xpad_image(dark_image_filename, 16, offset, gap, 512, 512);
raw_dark = double(raw_dark);
printf("Total dark frames: %i\n", num_frames);

if mod(num_frames, num_caps) != 0
  error("Error: Frame count is not a multiple of number of caps.");
endif

## Compute the background image
raw_dark = mean(raw_dark,3);

## We now need to NaN out the bad pixels.  These are contained in two PGM files
## Change the filenames here to suit.
bad_dark_pixels = imread("dark_pixels.pgm");
bad_hot_pixels = imread("hot_pixels.pgm");
disp('Loaded bad pixel maps')
bad_pixels = bad_dark_pixels+bad_hot_pixels;
bad_pixel_loc = find(bad_pixels != 0);


## Get the foreground files
bright_file_list = glob('keck_test/linearity/*f*.raw')
num_fg = size(bright_file_list)(1);

sigmasq_vals = zeros(asic_count, num_fg);
mu_vals = zeros(asic_count, num_fg);

for fg_idx=1:num_fg
  bright_filename = bright_file_list{fg_idx}
  [raw_bright, num_frames] = read_xpad_image(bright_filename, 16, offset, gap, 512, 512);

  raw_bright = double(raw_bright);
  printf("Loaded %i foreground frames.\n", num_frames);

  ## Set all bad flat pixels to NaN
  ## Iterate over all caps
  for slice_idx = 1:(num_frames)
    curr_slice = raw_bright(:,:,slice_idx);
                                #-=-= NOTE Also squeeze in BG sub
    curr_slice = curr_slice - raw_dark;
    curr_slice(bad_pixel_loc) = NaN;
    raw_bright(:,:,slice_idx) = curr_slice;
  endfor

  #-=-= DEBUGGING
  if (fg_idx == 0)
    imwrite(raw_bright(:,:,100), 'sub_bright.tiff');
  endif
  
  
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

      curr_asic = raw_bright(row_lower:row_upper, col_lower:col_upper, :);
      [curr_sigmasq, curr_mu] = calc_linearity_vals(curr_asic);
      sigmasq_vals(asic_idx, fg_idx) = curr_sigmasq;
      mu_vals(asic_idx, fg_idx) = curr_mu;
    endfor
  endfor
endfor

subplot(1,1,1)
plot(mu_vals(7,:), sigmasq_vals(7,:),'-b*;ASIC 7;', mu_vals(8,:), sigmasq_vals(8,:),'-r^;ASIC 8;');
title("Linearity - Cap 1")
xlabel('Frame Mean (ADU)')
ylabel('Frame Variance (ADU^2)')
print pad_linearity.png

printf("Linearity Data ASIC 7\n")
disp([mu_vals(7,num_fg:-1:1); sigmasq_vals(7,num_fg:-1:1)]')

printf("Linearity Data ASIC 8\n")
disp([mu_vals(8,num_fg:-1:1); sigmasq_vals(8,num_fg:-1:1)]')


#subplot(2,1,2)
#plot(1:8,separate_cap_noise(7,:),'-b*;ASIC 7;', 1:8, separate_cap_noise(8,:),'-r^;ASIC 8;');
#title('Per-cap Noise')
