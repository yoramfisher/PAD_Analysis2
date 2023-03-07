function mod_img = thresh_image(base_img, bLow, thresh, asic_width, asic_height)
  mod_img = base_img;

  num_caps = size(base_img)(3);

  num_x_asic = size(base_img)(2)/asic_width;
  num_y_asic = size(base_img)(1)/asic_height;

  for cap_idx = 1:num_caps
    for row_idx = 1:num_x_asic
      y_start = (row_idx-1)*asic_height+1;
      y_end = row_idx*asic_height;
      for col_idx = 1:num_x_asic
        x_start = (col_idx-1)*asic_width+1;
        x_end = col_idx*asic_width;
        
        curr_asic = mod_img(y_start:y_end, x_start:x_end, cap_idx);
        
        mod_img(y_start:y_end, x_start:x_end, cap_idx) = pixel_rank(curr_asic, bLow, thresh);

      endfor
    endfor
  endfor

  return
endfunction
