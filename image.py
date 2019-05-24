import io
from typing import List
from PIL import Image
class ImageUtil:
    """Handles operations on images including merging and conversions."""
    @staticmethod
    def from_file(filename):
        """Converts an image file to image bytes."""
        imgbytes = io.BytesIO()
        im = Image.open(filename).convert('RGBA')
        im.save(imgbytes, format='PNG')
        imgbytes.seek(0)
        return imgbytes

    @staticmethod
    def merge(*images_: List[bytes], axis=0, pad=False):
        """Combines a set of images along an axis and returns the bytes of the image.
        0: horizontal
        1: vertical
        """
        images = ()
        for image in images_:
            if type(image) == bytes:
                image = io.BytesIO(image)
            image.seek(0)
            images += (Image.open(image).convert('RGBA'),)
        dims = list(zip(*(i.size for i in images)))
        if pad:
            dims[axis] = [15 + x for x in dims[axis]]
        total_axis = sum(dims[axis])
        max_cross = max(dims[axis - 1])

        if axis == 0:
            new_im = Image.new('RGBA', (total_axis, max_cross))
        else:
            new_im = Image.new('RGBA', (max_cross, total_axis))

        offset = 0
        for i, img in enumerate(images):
            if axis == 0:
                new_im.paste(img, (offset, 0))
            else:
                new_im.paste(img, (0, offset))
            offset += dims[axis][i]

        imgbytes = io.BytesIO()
        new_im.save(imgbytes, format='PNG')
        imgbytes.seek(0)
        return imgbytes