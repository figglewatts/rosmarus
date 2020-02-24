from ..graphics.texture import Texture2D
from ..render.spritebatch import SpriteBatch
from ..math.transform import Transform2D
from ..math.rect import Rect


class Sprite:
    def __init__(self,
                 texture: Texture2D,
                 transform: Transform2D = Transform2D(),
                 tex_region: Rect = None,
                 x_pos: int = 0,
                 y_pos: int = 0) -> None:
        self.texture = texture
        self.transform = transform
        self.tex_region = tex_region
        self.transform.set_position((x_pos, y_pos))

    def draw(self, spritebatch: SpriteBatch, *args, **kwargs) -> None:
        spritebatch.draw(self.texture,
                         transform=self.transform,
                         tex_region=self.tex_region,
                         *args,
                         **kwargs)
