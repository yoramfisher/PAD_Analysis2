function mod_img = pixel_rank(base_img, bLow, thresh)
  mod_img = base_img;
  curr_line = reshape(base_img, 1, []);
  curr_line = curr_line(find(isfinite(curr_line)));

  if (size(curr_line)(2) == 0)  #All pixels NaN
    return                      # Nothing to filter out
  endif

  line_len = size(curr_line)(2)
  
  sort_line = sort(curr_line);
    
  if bLow != 0                  # Filter out low pixels
    thresh_idx = floor(line_len*thresh)+1
    thresh_val = sort_line(thresh_idx)
    mod_img(find(mod_img <= thresh_val)) = NaN;
  else                        # Filter out high pixels
    thresh_idx = floor(line_len*(1-thresh))
    thresh_val = sort_line(thresh_idx)
    mod_img(find(mod_img >= thresh_val)) = NaN;
  endif

  return
endfunction


    
