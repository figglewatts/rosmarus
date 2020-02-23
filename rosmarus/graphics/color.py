import glm


class Color:
    def __init__(self,
                 r: float = 1,
                 g: float = 1,
                 b: float = 1,
                 a: float = 1) -> None:
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __repr__(self) -> str:
        return f"Color({self.r}, {self.g}, {self.b}, {self.a})"

    def to_vec4(self) -> glm.vec4:
        return glm.vec4(self.r, self.g, self.b, self.a)

    def to_tuple(self):
        return (self.r, self.g, self.b, self.a)


WHITE = Color()
BLACK = Color(0, 0, 0, 1)
TRANSPARENT = Color(1, 1, 1, 0)
RED = Color(1, 0, 0, 1)
GREEN = Color(0, 1, 0, 1)
BLUE = Color(0, 0, 1, 1)
