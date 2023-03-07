clear

img_size = 512;

x_val = 0:(img_size-1);

x_array = ones(img_size, 1)*x_val/img_size;
y_array = x_array';

out_image = x_array.^.8+y_array.^2;

#out_image = floor(out_image * 10);

img_min = min(min(out_image));
img_max = max(max(out_image));

scaled_image = (out_image-img_min)/(img_max-img_min)*16000;

imagesc(out_image)
plot(out_image(510,:))

out_file = fopen('basic_pattern.raw', 'wb');

for cap_idx=1:8
  fwrite(out_file, scaled_image', 'uint16',0,'b');
endfor

fclose(out_file);
