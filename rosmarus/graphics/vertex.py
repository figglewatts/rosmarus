from ctypes import *
import glm

from .color import Color


class Vertex(Structure):
    _fields_ = [("position", c_float * 4), ("normal", c_float * 3),
                ("uv", c_float * 2), ("color", c_float * 4)]

    def __init__(
        self,
        position: glm.vec4,
        normal: glm.vec3 = glm.vec3(0, 0, 0),
        uv: glm.vec2 = glm.vec2(0, 0),
        color: glm.vec4 = glm.vec4(1, 1, 1, 1)
    ) -> None:
        position = (c_float * 4).from_buffer(position)
        normal = (c_float * 3).from_buffer(normal)
        uv = (c_float * 2).from_buffer(uv)
        color = (c_float * 4).from_buffer(color)
        super(Vertex, self).__init__(position, normal, uv, color)

    def set_position(self, pos: glm.vec4) -> None:
        self.position = (c_float * 4).from_buffer(pos)

    def set_uv(self, uv: glm.vec2) -> None:
        self.uv = (c_float * 4).from_buffer(uv)

    def set_color(self, color: Color) -> None:
        self.color = (c_float * 4).from_buffer(color.to_vec4())

    def set_normal(self, normal: glm.vec3) -> None:
        self.normal = (c_float * 3).from_buffer(normal)