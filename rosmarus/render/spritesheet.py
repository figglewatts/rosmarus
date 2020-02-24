from typing import Tuple

from ..graphics.texture import Texture2D
from .sprite import Sprite
from ..math.rect import Rect


class SpriteSheet:
    def __init__(self, texture: Texture2D, sprite_width: int,
                 sprite_height: int) -> None:
        self.texture = texture
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height

    def get_size_in_sprites(self) -> Tuple[int, int]:
        tex_w, tex_h = self.texture.get_size()
        return int(tex_w / self.sprite_width), int(tex_h / self.sprite_height)

    def get_sprite_count(self) -> int:
        num_x, num_y = self.get_size_in_sprites()
        return num_x * num_y

    def get_sprite(self, index: int, **kwargs) -> Sprite:
        tex_region = self._get_tex_region(index)
        return Sprite(self.texture, tex_region=tex_region, **kwargs)

    def _get_tex_region(self, index: int) -> Rect:
        tex_w, tex_h = self.texture.get_size()
        reg_y = int(index / (tex_w / self.sprite_width)) * self.sprite_height
        reg_x = int(index % (tex_w / self.sprite_width)) * self.sprite_width

        return Rect(reg_x, reg_y, self.sprite_width, self.sprite_height)
