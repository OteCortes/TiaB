Text in a Bottle is a Steganography class to encode messages in a image.
Tested in python 2.6, 2.7 and 3.3 in Linux, Cygwin and Windows with the library Pillow also works with the old PIL library.
To get the Pillow library use:
 pip install pillow

Pillow only works with image formats ready at the moment of compilation in Linux

In windows download the binary package from http://www.lfd.uci.edu/~gohlke/pythonlibs/#pil


The class is also executable to encode a text in a image or to get the encoded text from a image. The destination image extension
must be equal to the base image extension to keep the format.

To encode a text use:
  Tiab <passphrase> <base_image_path> --out <destination_image_name> --msg <text_to_encode>

To decode a text from a image:
  tiab <passphrase> <base_image_path>


Hope you enjoy.