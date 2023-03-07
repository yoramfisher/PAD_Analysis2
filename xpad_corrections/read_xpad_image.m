function [img_stack, num_frames] = read_xpad_image(filename, bpp, offset, gap, width, height)
  img_file = fopen(filename, 'rb');

  data_pending = 1;
             %-=-= XXX Assumes there is at least one frame in the file

  ## Skip the offset
  fseek(img_file, offset, SEEK_SET);

  ## Read in the first slice according to datatype
  if bpp == 16
    data_type = 'uint16';
  elseif bpp == 32            #XXX May have issues later with float, but could use -32 for BPP like FITS doese
    data_type = 'uint32';
  endif

  curr_array = fread(img_file, [height, width], data_type, 0, 'b')';
  num_frames = 1;
  
  fseek(img_file, gap, SEEK_CUR);

  img_stack = cat(3,curr_array);
  
  while(data_pending == 1)
    ## Read in the data
    [curr_array, nread] = fread(img_file, [height, width], data_type, 0, 'b');
    curr_array = curr_array';

    if nread != height*width    # Incomplete read -- assume finish
      data_pending = 0;
      return                    # I guess we're done; maybe break vs return?
    endif
      
    img_stack = cat(3, img_stack, curr_array); # Append the new slice
    num_frames++;                              # Increment the count

    fseek(img_file, gap, SEEK_CUR); # Skip the gap
  endwhile

  return
endfunction

