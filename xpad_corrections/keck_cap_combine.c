#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
  FILE *in_img[8];
  char *img_frame;
  int img_idx;
  size_t img_size = 512*512*2+1024;
  FILE *out_img;

  img_frame = malloc(img_size);
  out_img = fopen("flat_img.raw", "wb");

  for (img_idx = 0; img_idx < 8; img_idx++)
    {
      in_img[img_idx] = fopen(argv[img_idx], "rb");
      printf("%s\n", argv[img_idx+1]);
    }

  for (img_idx = 0; img_idx < 8; img_idx++)
    {
      while (1)
	{
	  fread(img_frame, 1, img_size, in_img[img_idx]);
	  
	  fwrite(img_frame, 1, img_size, out_img);
	  if (feof(in_img[img_idx]))
	    {
	      break;
	    }
	}
    }

  return 0;
}


	 
  
