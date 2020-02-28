import array
from ctypes import c_ubyte
from os import path

from PIL import Image

from .. import resources
from ..graphics.texture import Texture2D


def load_texture(file_path: str, **kwargs) -> Texture2D:
    ext = path.splitext(file_path)[1][1:].lower()
    if ext != "png":
        raise RuntimeError("Only PNG files are supported")

    with open(file_path, "rb") as image_file:
        img = Image.open(image_file).transpose(
            Image.FLIP_TOP_BOTTOM).convert("RGBA")
        w, h = img.size
        img_data = array.array("B")
        for v in img.getdata():
            img_data.extend(v)
        raw_img_data = (c_ubyte * len(img_data)).from_buffer(img_data)
        return Texture2D(w, h, raw_img_data, **kwargs)


def cleanup_texture(tex: Texture2D) -> None:
    tex.cleanup()


resources.register_type_handler("texture", load_texture, cleanup_texture)