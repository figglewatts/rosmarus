from ctypes import *
import glm

from .color import Color


class Vertex(Structure):
    _fields_ = [("position", c_float * 4), ("normal", c_float * 3),
                ("uv", c_float * 2), ("color", c_float * 4)]

    def __init__(
        self,
        position: glm.vec4,
        normal: glm.vec3 = (0, 0, 0),
        uv: glm.vec2 = (0, 0),
        color: glm.vec4 = (1, 1, 1, 1)
    ) -> None:
        super(Vertex, self).__init__(position, normal, uv, color)