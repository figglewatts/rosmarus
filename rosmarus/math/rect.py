from typing import Tuple

import glm


class Rect:
    def __init__(self,
                 x: float = 0,
                 y: float = 0,
                 w: float = 0,
                 h: float = 0) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x2 = x + w
        self.y2 = y + h

    def get_position(self) -> glm.vec2:
        return glm.vec2(self.x, self.y)

    def get_extent(self) -> glm.vec2:
        return glm.vec2(self.x2, self.y2)

    def get_size(self) -> glm.vec2:
        return glm.vec2(self.w, self.h)

    def get_tuple(self) -> Tuple[float, float, float, float]:
        return self.x, self.y, self.w, self.h

    def get_extent_tuple(self) -> Tuple[float, float, float, float]:
        return self.x, self.y, self.x2, self.y2