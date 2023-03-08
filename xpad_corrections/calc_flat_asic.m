function flat_raster = calc_flat_asic(asic_raster, gain_thresh)
  flat_raster = asic_raster;    #Populate the output, copying NaN

  curr_line = reshape(asic_raster, 1, []); # Reshape to line for averaging
  curr_line = curr_line(find(isfinite(curr_line))); # Filter out NaN

  if (size(curr_line)(2) == 0)  #All pixels NaN
    return;                     #No flat field to caluclate
  endif

  ## Compute the mean for the calculation of gain
  line_mean = mean(curr_line);

  flat_raster = line_mean ./ asic_raster; # Compute the per-pixel gains

  ## Now handle the pixels with too low of a gain, which corresponds to
  ## a big number in the flat_raster
  low_pixels = find(flat_raster > (1/gain_thresh));
  flat_raster(low_pixels) = 1.0; # No-op their gains

  return
endfunction


  
