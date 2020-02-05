import os
from PIL import Image
import sys

from voussoirkit import imagetools
from voussoirkit import winglob

filenames = sys.argv[1]

filenames = winglob.glob(filenames)
for filename in filenames:
    i = Image.open(filename)
    if all(x.isdigit() for x in sys.argv[2:3]):
        new_x = int(sys.argv[2])
        new_y = int(sys.argv[3])
    else:
        try:
            ratio = float(sys.argv[2])
            new_x = int(i.size[0] * ratio)
            new_y = int(i.size[1] * ratio)
        except ValueError:
            print('you did it wrong')
            quit()

    (image_width, image_height) = i.size

    if new_x == 0:
        (new_x, new_y) = imagetools.fit_into_bounds(image_width, image_height, 10000000, new_y)
    if new_y == 0:
        (new_x, new_y) = imagetools.fit_into_bounds(image_width, image_height, new_x, 10000000)

    print(i.size, new_x, new_y)
    i = i.resize( (new_x, new_y), Image.ANTIALIAS)
    suffix = '_{width}x{height}'.format(width=new_x, height=new_y)
    (base, extension) = os.path.splitext(filename)
    newname = base + suffix + extension
    i.save(newname, quality=100)
