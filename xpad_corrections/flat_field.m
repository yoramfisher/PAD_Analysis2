clear

input_filename = 'avg_image_bgsub_8caps.raw';
input_file = fopen(input_filename, 'rb');

num_frames = 8;
asic_size = 128;

raster = zeros(512, 512, num_frames);
for frame_idx = 1:num_frames
  raster(:,:,frame_idx) = fread(input_file, [512 512], 'float', 'b')';
endfor

imagesc(raster(:,:,2))

fclose(input_file);

out_raster = raster;
for frame_idx = 1:num_frames
  for asic_row_idx=0:3
    start_row = asic_row_idx*asic_size+1;
    end_row = (asic_row_idx+1)*asic_size;
    for asic_col_idx=0:3
      start_col = asic_col_idx*asic_size+1;
      end_col = (asic_col_idx+1)*asic_size;
      curr_asic_img = raster(start_row:end_row,start_col:end_col,frame_idx);

      asic_mean = mean(reshape(curr_asic_img, 1, []));

      curr_asic_img = asic_mean*1./curr_asic_img;

      out_raster(start_row:end_row,start_col:end_col, frame_idx) = curr_asic_img;
    endfor
  endfor
endfor

output_filename = 'dcs2_flatfield.raw';
output_file = fopen(output_filename, 'wb');

for frame_idx = 1:num_frames
  final_raster = out_raster(:,:,frame_idx)'; % transpose for writing out to file
  final_raster = reshape(final_raster, 1, []);
  fwrite(output_file, final_raster, 'double', 0, 'l');
endfor

