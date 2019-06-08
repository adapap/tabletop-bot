import io
import os
from typing import List
from PIL import Image
class ImageUtil:
    """Handles operations on images including merging and conversions."""
    @staticmethod
    def from_file(filename: str):
        """Converts an image file to image bytes."""
        imgbytes = io.BytesIO()
        im = Image.open(filename).convert('RGBA')
        im.save(imgbytes, format='PNG')
        imgbytes.seek(0)
        return imgbytes

    @staticmethod
    def scale(image: Image, w=None, h=None):
        width, height = image.size
        ratio = (w or width) / (h or height)
        size = (int(width * ratio), int(height * ratio))
        image.thumbnail(size, Image.ANTIALIAS)

    @staticmethod
    def merge(*images_: List[bytes], axis: int=0, pad: bool=False):
        """
        Combines a set of images along an axis and returns the bytes of the image.
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

class AssetManager:
    """Handles asset retrieval by checking for `assets/` folder in the game directory."""
    def __init__(self, filepath):
        root = os.path.dirname(os.path.realpath(filepath))
        assets = os.path.join(root, 'assets')
        basename = os.path.basename(os.path.normpath(root))
        if not os.path.isdir(assets):
            raise FileNotFoundError(basename + ' has no /assets folder.')
        self.root = assets

    def get_asset(self, filename: str):
        """Retrieves an asset matching the given filename."""
        path = os.path.join(self.root, filename)
        if not os.path.exists(path):
            raise FileNotFoundError('No file ' + filename + ' found in assets folder.')
        return path