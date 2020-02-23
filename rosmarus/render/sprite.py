from ..graphics.texture import Texture2D
from ..render.spritebatch import SpriteBatch
from ..math.transform import Transform2D


class Sprite:
    def __init__(self, texture: Texture2D, transform: Transform2D) -> None:
        self.texture = texture
        self.transform = transform

    def draw(self, spritebatch: SpriteBatch, *args, **kwargs) -> None:
        spritebatch.draw(self.texture,
                         transform=self.transform,
                         *args,
                         **kwargs)
